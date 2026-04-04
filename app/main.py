import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.clarifier import build_clarified_query, should_clarify
from agent.light_answer import generate_light_answer
from agent.planner import plan_subquestions
from agent.reflector import reflect
from agent.reporter import generate_report
from agent.rewriter import rewrite_query
from agent.router import route_task
from agent.scratchpad import (
    build_scratchpad_entry,
    render_central_report,
    render_report_citation_appendix,
)
from agent.search import search
from agent.selector import select_top_results
from agent.state import ResearchState
from agent.summarizer import summarize
from agent.tasks import create_task, sync_task_from_state, update_task


MAX_ROUNDS = 3
TOP_K_RESULTS = 3
LOG_DIR = Path("outputs/logs")


class TeeStream:
    """Write stdout to both terminal and log file."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, data: str) -> None:
        for stream in self.streams:
            try:
                stream.write(data)
            except UnicodeEncodeError:
                safe_data = data.encode("gbk", errors="replace").decode("gbk", errors="replace")
                stream.write(safe_data)
            stream.flush()

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()


def get_run_log_path(task_id: str) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR / f"{task_id}.log.txt"


def get_central_report_path(state: ResearchState) -> Path | None:
    if not state.task_dir:
        return None
    return Path(state.task_dir) / "central_report.md"


def extract_directional_judgment(summary: str) -> str:
    lines = [line.strip() for line in summary.splitlines() if line.strip()]
    if not lines:
        return "现有材料暂时只能支持一个较初步的方向性判断。"

    first_line = lines[0]
    prefixes = [
        "当前更可靠的判断是：",
        "当前更值得关注的不是单点突破，而是未来几年可能出现的几条方向性变化：",
        "当前材料提示主要限制并不只来自技术能力本身，还集中体现在",
    ]

    for prefix in prefixes:
        if first_line.startswith(prefix):
            first_line = first_line[len(prefix) :].strip()
            break

    if not first_line:
        return "现有材料暂时只能支持一个较初步的方向性判断。"

    return f"现有材料暂时提示：{first_line.rstrip('。?')}。"


def build_final_summary(sub_question: str, summary: str, reflection: dict) -> str:
    if reflection.get("status") == "enough":
        return summary

    reason = reflection.get("reason", "").strip() or "当前证据仍然不足。"
    suggestion = reflection.get("suggestion", "").strip()
    support_section = summary.split("支撑点：", 1)[1].strip() if "支撑点：" in summary else summary.strip()
    direction_line = extract_directional_judgment(summary)

    lines = [
        f"关于“{sub_question}”，当前结论仍然只能视为初步判断，证据还不够扎实。",
        "",
        "目前不足主要在于：",
        reason,
        "",
        "在现有材料下，可以暂时保留的方向性判断是：",
        direction_line,
        "",
        "支撑点：",
        support_section,
        "",
        "需要注意的是：当前结果更适合作为方向性信号，而不是已经完全坐实的结论。"
        + (f" 如果继续迭代，建议优先补充：{suggestion}" if suggestion else ""),
    ]
    return "\n".join(lines)


def write_report(state: ResearchState, report: str) -> None:
    if not state.report_path:
        return
    report_path = Path(state.report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")


def write_central_report(state: ResearchState) -> None:
    path = get_central_report_path(state)
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_central_report(state), encoding="utf-8")


def build_final_report(state: ResearchState) -> str:
    report = generate_report(state.query, state.summaries)
    appendix = render_report_citation_appendix(state)
    return f"{report}\n\n{appendix}".strip()


def build_light_report(state: ResearchState, results: list[dict], answer: str) -> str:
    lines = [
        f"问题：{state.query}",
        "",
        f"【工作流】{state.task_type}",
        f"【路由原因】{state.routing_reason}",
        "",
        answer.strip(),
    ]
    if results:
        lines.extend(["", "## 参考来源"])
        for index, item in enumerate(results, 1):
            lines.append(f"{index}. {item.get('title', '').strip()} | {item.get('source', '').strip()}")
    return "\n".join(lines).strip()


def write_light_central_report(state: ResearchState, results: list[dict], answer: str) -> None:
    path = get_central_report_path(state)
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Central Report",
        "",
        f"- task_type: {state.task_type}",
        f"- router_source: {state.router_source}",
        f"- routing_reason: {state.routing_reason}",
        "",
        "## Query",
        state.query,
        "",
        "## Draft Answer",
        answer.strip(),
    ]
    if results:
        lines.extend(["", "## Retrieved Sources"])
        for index, item in enumerate(results, 1):
            lines.append(f"{index}. {item.get('title', '').strip()} | {item.get('source', '').strip()}")
    path.write_text("\n".join(lines).strip(), encoding="utf-8")


class Runtime:
    """Own task bootstrap and workflow dispatch so main() stays thin."""

    def build_state(self, task, bootstrap_query: str, log_path: Path) -> ResearchState:
        return ResearchState(
            query=bootstrap_query,
            task_id=task.task_id,
            task_status="created",
            task_dir=task.task_dir,
            log_path=str(log_path),
            report_path=task.report_path,
        )

    def _maybe_clarify(self, state: ResearchState) -> ResearchState:
        clarification = should_clarify(state.query)
        if clarification.source == "rule_fallback" and clarification.note:
            print(f"\n[Clarifier 回退] LLM 判定不可用，已回退到规则模式：{clarification.note}")

        if not clarification.should_clarify or not clarification.questions:
            return state

        state.clarification_questions = clarification.questions
        print(f"\n[需求澄清][{clarification.source}] 这个问题还可以先补一点约束，这样后面的处理会更贴题。")

        for index, question in enumerate(clarification.questions, 1):
            answer = input(f"{index}. {question}\n>>> ").strip()
            state.clarification_answers.append(answer)

        state.clarified_query = build_clarified_query(
            state.original_query,
            state.clarification_questions,
            state.clarification_answers,
        )
        state.query = state.clarified_query

        print("\n[澄清后的问题]")
        print(state.query)
        return state

    def _apply_route(self, state: ResearchState) -> ResearchState:
        route = route_task(state.query)
        state.task_type = route.task_type
        state.router_source = route.source
        state.routing_reason = route.routing_reason
        state.routing_confidence = route.confidence_score
        state.routing_note = route.note

        print(f"\n[任务路由][{route.source}] {route.task_type} | confidence={route.confidence_score:.2f}")
        print(f"[路由原因] {route.routing_reason}")
        if route.note:
            print(f"[路由回退] {route.note}")

        return state

    def _checkpoint(self, task, state: ResearchState, note: str = "") -> None:
        sync_task_from_state(task, state, note=note)
        write_central_report(state)

    def _emit_search_trace(
        self,
        sub_question: str,
        current_query: str,
        round_num: int,
        results: list[dict],
        selected_results: list[dict],
        reflection: dict,
    ) -> None:
        print(f"\n原始问题：{sub_question}")
        print(f"当前搜索 query：{current_query}")
        print(f"第 {round_num} 轮搜索结果：")
        for index, item in enumerate(results, 1):
            print(f"  {index}. 标题：{item['title']}")
            print(f"     摘要：{item['snippet']}")
            print(f"     来源：{item['source']}")

        print("\n筛选后保留的结果：")
        for index, item in enumerate(selected_results, 1):
            print(f"  {index}. 标题：{item['title']}")
            print(f"     摘要：{item['snippet']}")
            print(f"     来源：{item['source']}")

        print(f"判断状态：{reflection['status']}")
        print(f"原因：{reflection['reason']}")

    def _run_light_workflow(self, task, state: ResearchState, log_path: Path) -> None:
        if state.task_type == "ADVICE":
            state.task_status = "clarifying"
            update_task(task, status="clarifying", log_path=str(log_path))
            state = self._maybe_clarify(state)
            sync_task_from_state(task, state, note="clarifier completed")

        state.task_status = "researching"
        update_task(task, status="researching")
        if state.task_type == "QUICK_ANSWER":
            results = search(state.query, 1)
        else:
            results = []
        answer = generate_light_answer(state.query, state.task_type, results)
        report = build_light_report(state, results, answer)
        write_report(state, report)
        write_light_central_report(state, results, answer)
        sync_task_from_state(task, state, note=f"{state.task_type.lower()} workflow completed")
        update_task(task, status="completed")

        print("\n[轻量工作流结果]")
        print(report)
        print(f"\n[报告已保存] {state.report_path}")
        central_report_path = get_central_report_path(state)
        if central_report_path is not None:
            print(f"[中央草稿] {central_report_path}")
        print(f"[日志已保存] {log_path}")
        print("[流程结束]")

    def _research_loop(self, sub_question: str) -> tuple[list[dict], dict]:
        round_num = 1
        current_query = sub_question
        all_results: list[dict] = []
        reflection = {
            "status": "insufficient",
            "reason": "尚未完成搜索。",
            "suggestion": "",
        }

        while round_num <= MAX_ROUNDS:
            results = search(current_query, round_num)
            all_results.extend(results)
            selected_results = select_top_results(sub_question, all_results, top_k=TOP_K_RESULTS)
            reflection = reflect(sub_question, selected_results)

            self._emit_search_trace(sub_question, current_query, round_num, results, selected_results, reflection)

            if reflection["status"] == "enough":
                break

            print(f"改写建议：{reflection['suggestion']}")
            current_query = rewrite_query(sub_question, reflection, round_num)
            print("信息不足，准备使用新 query 进行下一轮搜索...\n")
            round_num += 1

        if round_num > MAX_ROUNDS and reflection["status"] != "enough":
            print(f"\n[提示] 子问题《{sub_question}》已达到最大搜索轮数，停止继续搜索。")

        final_selected_results = select_top_results(sub_question, all_results, top_k=TOP_K_RESULTS)
        return final_selected_results, reflection

    def _run_research_workflow(self, task, state: ResearchState, log_path: Path) -> None:
        state.task_status = "clarifying"
        update_task(task, status="clarifying", log_path=str(log_path))
        state = self._maybe_clarify(state)
        sync_task_from_state(task, state, note="clarifier completed")

        state.task_status = "planned"
        update_task(task, status="planned")
        state = plan_subquestions(state)
        self._checkpoint(task, state, note="planner completed")
        planner_source = getattr(state, "planner_source", "") or "unknown"
        planner_type = getattr(state, "planner_type", "") or "general"
        planner_reason = getattr(state, "planner_reason", "").strip()
        planner_note = getattr(state, "planner_note", "").strip()
        print(f"\n[规划器][{planner_source}] {planner_type}")
        if planner_reason:
            print(f"[规划原因] {planner_reason}")
        if planner_note:
            print(f"[规划回退] {planner_note}")

        print("\n[拆解出的子问题]")
        for index, sub_question in enumerate(state.sub_questions, 1):
            print(f"{index}. {sub_question}")

        print("\n[开始搜索、筛选、反思、改写与总结]")
        state.task_status = "researching"
        update_task(task, status="researching")

        for sub_question in state.sub_questions:
            final_selected_results, reflection = self._research_loop(sub_question)
            state.search_results[sub_question] = final_selected_results

            raw_summary = summarize(sub_question, final_selected_results)
            summary = build_final_summary(sub_question, raw_summary, reflection)
            state.summaries[sub_question] = summary

            scratchpad_entry = build_scratchpad_entry(
                state,
                sub_question,
                final_selected_results,
                summary,
                reflection,
            )
            state.scratchpad_entries.append(scratchpad_entry)
            self._checkpoint(task, state, note=f"completed sub-question: {sub_question}")

            print(f"总结：\n{summary}")
            if scratchpad_entry["source_ids"]:
                print(f"[Scratchpad] Sources: {', '.join(scratchpad_entry['source_ids'])}")

        report = build_final_report(state)
        write_report(state, report)
        self._checkpoint(task, state, note="report generated")
        update_task(task, status="completed")

        print("\n[最终研究报告]")
        print(report)
        print(f"\n[报告已保存] {state.report_path}")
        central_report_path = get_central_report_path(state)
        if central_report_path is not None:
            print(f"[中央草稿] {central_report_path}")
        print(f"[日志已保存] {log_path}")
        print("[流程结束]")

    def resolve_workflow(self, state: ResearchState):
        if state.task_type == "RESEARCH":
            return self._run_research_workflow
        return self._run_light_workflow

    def run_task(self, task, bootstrap_query: str, log_path: Path) -> None:
        try:
            state = self.build_state(task, bootstrap_query, log_path)

            print("\n[任务已创建] {}".format(task.task_id))
            print("[任务记录] {}".format(Path(task.task_dir) / "task.json"))

            state.task_status = "routing"
            update_task(task, status="routing", log_path=str(log_path))
            state = self._apply_route(state)
            sync_task_from_state(task, state, note="router completed")

            workflow = self.resolve_workflow(state)
            workflow(task, state, log_path)
        except Exception as exc:
            update_task(task, status="failed")
            print("\n[错误] 任务执行失败: {}".format(exc))
            raise


def main() -> None:
    query = input("\n>>> 请输入你的问题：").strip()
    task = create_task(query)
    log_path = get_run_log_path(task.task_id)
    runtime = Runtime()

    original_stdout = sys.stdout
    with log_path.open("w", encoding="utf-8") as log_file:
        sys.stdout = TeeStream(original_stdout, log_file)
        try:
            runtime.run_task(task, query, log_path)
        finally:
            sys.stdout = original_stdout


if __name__ == "__main__":
    main()

