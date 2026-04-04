import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.planner import plan_subquestions
from agent.reflector import reflect
from agent.reporter import generate_report
from agent.rewriter import rewrite_query
from agent.search import search
from agent.selector import select_top_results
from agent.state import ResearchState
from agent.summarizer import summarize
from app.main import MAX_ROUNDS, TOP_K_RESULTS, build_final_summary


TEST_CASES_PATH = ROOT / "test_cases.json"
EVAL_SUMMARIES_DIR = ROOT / "eval_summaries"
EVAL_RUNS_DIR = ROOT / "eval_runs"
BASELINES_DIR = ROOT / "baselines"
RETAIN_RECENT_EVALS = 3


def load_test_cases() -> list[dict]:
    with TEST_CASES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_focus_from_sub_question(sub_question: str) -> str:
    lower = (sub_question or "").lower()
    if any(token in lower for token in ["影响因素", "关键变量", "驱动", "推动", "原因", "why", "driver"]):
        return "driver"
    if any(token in lower for token in ["风险", "限制", "挑战", "治理", "安全", "合规", "risk"]):
        return "risk"
    if any(token in lower for token in ["未来", "变化", "演进", "方向", "future", "change"]):
        return "change"
    if any(token in lower for token in ["定义", "是什么", "区别", "definition"]):
        return "definition"
    return "general"


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def has_planner_drift(case_type: str, sub_questions: list[dict]) -> bool:
    """
    只在子问题结构明显跑偏时标记 planner_drift。
    不再因为问号个数或下游 insufficient 就误报。
    """
    texts = [item.get("sub_question", "") for item in sub_questions]
    if not texts:
        return True

    expected_groups_by_case_type = {
        "definition": [
            ["定义", "含义", "是什么"],
            ["组成", "机制", "原理", "架构"],
            ["区别", "混淆"],
            ["应用", "场景", "值得关注"],
        ],
        "driver": [
            ["核心问题", "值得关注"],
            ["影响因素", "关键变量", "驱动", "原因"],
            ["表现", "案例", "实际情况"],
            ["争议", "限制", "风险"],
        ],
        "high-noise-preference": [
            ["主流可选项", "可选项", "选项"],
            ["评价维度", "选择标准", "评价标准"],
            ["优缺点", "适用人群", "使用场景"],
            ["综合建议", "建议", "预算", "约束"],
        ],
        "timeline-trend": [
            ["时间节点", "里程碑", "过去几年", "阶段"],
            ["技术突破", "事件", "代表案例"],
            ["推动力量", "转折点", "驱动"],
            ["演进方向", "接下来", "未来"],
        ],
        "complex-comparison": [
            ["比较对象", "分别", "表现"],
            ["差异", "维度", "比较"],
            ["原因", "约束"],
            ["判断", "建议", "应对策略", "策略"],
        ],
    }

    expected_groups = expected_groups_by_case_type.get(case_type)
    if not expected_groups:
        return False

    matched_group_count = 0
    for keyword_group in expected_groups:
        if any(_contains_any(text, keyword_group) for text in texts):
            matched_group_count += 1

    # 只有缺失两组及以上关键槽位，才算明显拆歪。
    return matched_group_count <= len(expected_groups) - 2


def detect_failure_tags(case_result: dict) -> list[str]:
    tags = set()

    case = case_result.get("case", {})
    case_type = case.get("type", "")
    sub_questions = case_result.get("sub_questions", [])
    summaries = [item.get("summary", "") for item in sub_questions]
    report = case_result.get("report", "")

    if any(item.get("final_status") == "insufficient" for item in sub_questions):
        tags.add("reflect_false_insufficient")
        tags.add("insufficient_but_sounds_final")

    if any(
        any(keyword in item.get("summary", "") for keyword in ["点赞", "收藏", "浏览阅读", "评论"])
        for item in sub_questions
    ):
        tags.add("summary_noise")

    if any(
        extract_focus_from_sub_question(item.get("sub_question", "")) == "risk"
        and "未来几年可能出现的变化" in item.get("final_reason", "")
        for item in sub_questions
    ):
        tags.add("reflect_focus_mixup")

    if any(
        extract_focus_from_sub_question(item.get("sub_question", "")) == "driver"
        and item.get("final_status") == "enough"
        and "驱动" not in item.get("summary", "")
        and "原因" not in item.get("summary", "")
        and "因素" not in item.get("summary", "")
        for item in sub_questions
    ):
        tags.add("reflect_false_enough")

    if len(summaries) >= 2 and len(set(summary[:60] for summary in summaries if summary)) <= max(1, len(summaries) - 2):
        tags.add("summary_repetition")

    if report:
        repeated_fragments = 0
        for item in sub_questions:
            summary = item.get("summary", "")
            if summary and summary[:40] in report:
                repeated_fragments += 1
        if repeated_fragments >= max(2, len(sub_questions) - 1):
            tags.add("report_over_repetition")

    if any(
        "当前更可靠的判断是" not in summary
        and "当前结论仍然只能视为初步判断" not in summary
        for summary in summaries
        if summary
    ):
        tags.add("summary_not_answering")

    if has_planner_drift(case_type, sub_questions):
        tags.add("planner_drift")

    if not tags:
        tags.add("no_obvious_failure")

    return sorted(tags)


def build_scoreboard(results: list[dict]) -> dict:
    scoreboard = {
        "summary_repetition": 0,
        "insufficient_handling_error": 0,
        "planner_drift": 0,
        "selector_noise": 0,
        "report_over_repetition": 0,
        "reflect_focus_mixup": 0,
        "reflect_false_enough": 0,
        "reflect_false_insufficient": 0,
        "summary_noise": 0,
        "summary_not_answering": 0,
        "total_cases": len(results),
        "cases_with_insufficient": 0,
    }

    for result in results:
        tags = set(result.get("failure_tags", []))
        if any(item["final_status"] != "enough" for item in result.get("sub_questions", [])):
            scoreboard["cases_with_insufficient"] += 1

        for key in list(scoreboard.keys()):
            if key in tags:
                scoreboard[key] += 1

    return scoreboard


def run_single_case(case: dict) -> dict:
    query = case["question"]
    state = ResearchState(query=query)
    state = plan_subquestions(state)

    sub_question_runs = []

    for sub_question in state.sub_questions:
        round_num = 1
        current_query = sub_question
        all_results = []
        reflection = {
            "status": "insufficient",
            "reason": "尚未完成搜索。",
            "suggestion": "",
        }
        rounds = []

        while round_num <= MAX_ROUNDS:
            results = search(current_query, round_num)
            all_results.extend(results)
            selected_results = select_top_results(sub_question, all_results, top_k=TOP_K_RESULTS)
            reflection = reflect(sub_question, selected_results)

            rounds.append(
                {
                    "round": round_num,
                    "query": current_query,
                    "raw_results": results,
                    "selected_results": selected_results,
                    "reflection": reflection,
                }
            )

            if reflection["status"] == "enough":
                break

            current_query = rewrite_query(sub_question, reflection, round_num)
            round_num += 1

        final_selected_results = select_top_results(sub_question, all_results, top_k=TOP_K_RESULTS)
        state.search_results[sub_question] = final_selected_results

        raw_summary = summarize(sub_question, final_selected_results)
        summary = build_final_summary(sub_question, raw_summary, reflection)
        state.summaries[sub_question] = summary

        sub_question_runs.append(
            {
                "sub_question": sub_question,
                "focus": extract_focus_from_sub_question(sub_question),
                "rounds": rounds,
                "final_status": reflection["status"],
                "final_reason": reflection["reason"],
                "final_suggestion": reflection["suggestion"],
                "summary": summary,
            }
        )

    report = generate_report(state.query, state.summaries)
    case_result = {
        "case": case,
        "sub_questions": sub_question_runs,
        "report": report,
    }
    case_result["failure_tags"] = detect_failure_tags(case_result)
    return case_result


def write_case_run(case_result: dict, timestamp: str) -> Path:
    case_id = case_result["case"]["id"]
    run_path = EVAL_RUNS_DIR / f"{timestamp}_{case_id}.json"
    with run_path.open("w", encoding="utf-8") as f:
        json.dump(case_result, f, ensure_ascii=False, indent=2)
    return run_path


def build_case_summary_block(case_result: dict, run_path: Path) -> str:
    case = case_result["case"]
    insufficient_count = sum(1 for item in case_result["sub_questions"] if item["final_status"] != "enough")
    total_count = len(case_result["sub_questions"])

    lines = [
        f"## {case['id']}",
        f"- 题目：{case['question']}",
        f"- 类型：{case['type']}",
        f"- 难度：{case['difficulty']}",
        f"- 主要目标模块：{case['main_target_module']}",
        f"- 设计意图：{case['intent']}",
        f"- 子问题统计：{total_count}",
        f"- `insufficient` 数量：{insufficient_count}",
        f"- 失败标签：{', '.join(case_result['failure_tags'])}",
        f"- 详细运行记录：`{run_path.relative_to(ROOT.parent)}`",
        "",
        "### 子问题状态",
    ]

    for item in case_result["sub_questions"]:
        lines.extend(
            [
                f"- `{item['focus']}` | `{item['final_status']}` | {item['sub_question']}",
                f"  原因：{item['final_reason']}",
            ]
        )

    lines.extend(
        [
            "",
            "### 快速观察",
            f"- 总报告是否生成：{'是' if case_result['report'].strip() else '否'}",
            f"- 总报告长度：{len(case_result['report'])} 字符",
            "",
        ]
    )

    return "\n".join(lines)


def write_eval_summary(results: list[dict], timestamp: str) -> Path:
    EVAL_SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = EVAL_SUMMARIES_DIR / f"eval_summary_{timestamp}.md"

    insufficient_cases = [item for item in results if any(sq["final_status"] != "enough" for sq in item["sub_questions"])]
    scoreboard = build_scoreboard(results)

    lines = [
        f"# Eval Summary {timestamp}",
        "",
        f"- 测试题数量：{len(results)}",
        f"- 出现 `insufficient` 的题目数量：{len(insufficient_cases)}",
        "",
        "## 评分层（计数视角）",
        "",
        "```json",
        json.dumps(scoreboard, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 总览",
    ]

    for result in results:
        case = result["case"]
        insufficient_count = sum(1 for item in result["sub_questions"] if item["final_status"] != "enough")
        lines.append(
            f"- `{case['id']}` | `{case['type']}` | insufficient={insufficient_count} | tags={', '.join(result['failure_tags'])}"
        )

    lines.append("")
    lines.append("## 逐题摘要")
    lines.append("")

    for result in results:
        run_path = EVAL_RUNS_DIR / f"{timestamp}_{result['case']['id']}.json"
        lines.append(build_case_summary_block(result, run_path))
        lines.append("")

    with summary_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return summary_path


def write_latest_summary_alias(summary_path: Path) -> Path:
    latest_path = EVAL_SUMMARIES_DIR / "latest_summary.md"
    latest_path.write_text(summary_path.read_text(encoding="utf-8"), encoding="utf-8")
    return latest_path


def write_latest_runs_alias(results: list[dict], timestamp: str) -> Path:
    latest_dir = EVAL_RUNS_DIR / "latest"
    if latest_dir.exists():
        shutil.rmtree(latest_dir)
    latest_dir.mkdir(parents=True, exist_ok=True)

    for result in results:
        case_id = result["case"]["id"]
        source_path = EVAL_RUNS_DIR / f"{timestamp}_{case_id}.json"
        target_path = latest_dir / f"{case_id}.json"
        shutil.copy2(source_path, target_path)

    return latest_dir


def extract_summary_timestamp(path: Path) -> str | None:
    name = path.name
    prefix = "eval_summary_"
    if not name.startswith(prefix) or not name.endswith(".md"):
        return None
    return name[len(prefix):-3]


def extract_run_timestamp(path: Path) -> str | None:
    name = path.name
    if not name.endswith(".json") or "_" not in name:
        return None
    return name.split("_", 1)[0]


def cleanup_old_evals() -> None:
    summary_files = [
        path for path in EVAL_SUMMARIES_DIR.glob("eval_summary_*.md")
        if extract_summary_timestamp(path)
    ]
    timestamps = sorted(
        {extract_summary_timestamp(path) for path in summary_files if extract_summary_timestamp(path)},
        reverse=True,
    )
    keep_timestamps = set(timestamps[:RETAIN_RECENT_EVALS])

    for path in summary_files:
        timestamp = extract_summary_timestamp(path)
        if timestamp and timestamp not in keep_timestamps:
            path.unlink(missing_ok=True)

    run_files = [
        path for path in EVAL_RUNS_DIR.glob("*.json")
        if extract_run_timestamp(path)
    ]
    for path in run_files:
        timestamp = extract_run_timestamp(path)
        if timestamp and timestamp not in keep_timestamps:
            path.unlink(missing_ok=True)


def save_baseline_snapshot(results: list[dict], summary_path: Path, timestamp: str, baseline_label: str) -> Path:
    safe_label = baseline_label.strip().replace(" ", "-")
    baseline_dir = BASELINES_DIR / safe_label
    baseline_dir.mkdir(parents=True, exist_ok=True)

    target_summary = baseline_dir / f"eval_summary_{timestamp}.md"
    shutil.copy2(summary_path, target_summary)

    runs_dir = baseline_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    for result in results:
        case_id = result["case"]["id"]
        source_path = EVAL_RUNS_DIR / f"{timestamp}_{case_id}.json"
        target_path = runs_dir / f"{case_id}.json"
        shutil.copy2(source_path, target_path)

    return baseline_dir


def filter_cases(cases: list[dict], only_case_ids: list[str] | None) -> list[dict]:
    if not only_case_ids:
        return cases
    keep = set(only_case_ids)
    return [case for case in cases if case["id"] in keep]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run fixed evaluation set for deep_research_agent.")
    parser.add_argument("--case", action="append", help="Only run specific case id. Can be used multiple times.")
    parser.add_argument("--baseline-label", help="Save this run as a permanent baseline snapshot.")
    args = parser.parse_args()

    EVAL_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    EVAL_SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    BASELINES_DIR.mkdir(parents=True, exist_ok=True)

    cases = load_test_cases()
    selected_cases = filter_cases(cases, args.case)

    if not selected_cases:
        raise SystemExit("没有匹配到可运行的测试题。")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = []

    print(f"[eval] 开始运行 {len(selected_cases)} 道测试题")
    for case in selected_cases:
        print(f"[eval] 运行：{case['id']} -> {case['question']}")
        result = run_single_case(case)
        results.append(result)
        write_case_run(result, timestamp)

    summary_path = write_eval_summary(results, timestamp)
    latest_summary_path = write_latest_summary_alias(summary_path)
    latest_runs_dir = write_latest_runs_alias(results, timestamp)

    if args.baseline_label:
        baseline_dir = save_baseline_snapshot(results, summary_path, timestamp, args.baseline_label)
        print(f"[eval] baseline 已保存：{baseline_dir}")

    cleanup_old_evals()

    print(f"[eval] 汇总已生成：{summary_path}")
    print(f"[eval] 最新摘要：{latest_summary_path}")
    print(f"[eval] 最新详细结果目录：{latest_runs_dir}")


if __name__ == "__main__":
    main()
