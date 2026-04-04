import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.clarifier import build_clarified_query, should_clarify
from agent.light_answer import generate_light_answer
from agent.router import route_task


TEST_CASES_PATH = ROOT / "advice_eval_cases.json"
EVAL_SUMMARIES_DIR = ROOT / "advice_eval_summaries"
EVAL_RUNS_DIR = ROOT / "advice_eval_runs"
RETAIN_RECENT_EVALS = 5

RESEARCH_LEAK_MARKERS = [
    "驱动因素",
    "关键变量",
    "治理",
    "落地成本",
    "一手研究材料",
    "研究报告",
    "阶段性判断",
    "证据仍然偏弱",
    "趋势层面",
    "机制解释",
]

BOUNDARY_MARKERS = [
    "边界提醒",
    "类型仅供参考",
    "不要为了",
    "不等于",
    "不是婚恋配对公式",
    "关键看个体",
]

STRONG_OVERCLAIM_MARKERS = [
    "一定会",
    "绝对适合",
    "唯一适合",
    "最适合你的就是",
]

WEAK_CONSTRAINT_ANSWERS = {
    "都行",
    "无所谓",
    "看情况",
    "都可以",
    "差不多",
}


def load_cases() -> list[dict]:
    with TEST_CASES_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def normalize(text: str) -> str:
    return " ".join((text or "").strip().split())


def contains_any(text: str, keywords: list[str]) -> bool:
    normalized = normalize(text)
    return any(keyword in normalized for keyword in keywords)


def count_constraint_hits(answer: str, keywords: list[str]) -> int:
    return sum(1 for keyword in keywords if keyword in answer)


def mbti_type_count(answer: str) -> int:
    return len(set(re.findall(r"\b[A-Z]{4}\b", answer or "")))


def detect_failure_tags(case: dict, router, clarification, answer: str) -> list[str]:
    tags = set()

    if router.task_type != "ADVICE":
        tags.add("router_misroute")

    if not clarification.should_clarify:
        tags.add("clarifier_miss")

    if contains_any(answer, RESEARCH_LEAK_MARKERS):
        tags.add("research_leak")

    if "参考来源" in answer or "http://" in answer or "https://" in answer:
        tags.add("source_pollution")

    hits = count_constraint_hits(answer, case["expected_constraint_keywords"])
    if hits < max(1, len(case["expected_constraint_keywords"]) - 1):
        tags.add("constraint_usage_weak")

    if not contains_any(answer, BOUNDARY_MARKERS):
        tags.add("boundary_missing")

    if contains_any(answer, STRONG_OVERCLAIM_MARKERS):
        tags.add("overclaim")

    if mbti_type_count(answer) > 3:
        tags.add("template_mbti_overreach")

    if not tags:
        tags.add("no_obvious_failure")

    return sorted(tags)


def build_scoreboard(results: list[dict]) -> dict:
    scoreboard = {
        "router_misroute": 0,
        "clarifier_miss": 0,
        "research_leak": 0,
        "source_pollution": 0,
        "constraint_usage_weak": 0,
        "boundary_missing": 0,
        "overclaim": 0,
        "template_mbti_overreach": 0,
        "total_cases": len(results),
        "clean_cases": 0,
    }

    for result in results:
        tags = set(result["failure_tags"])
        if tags == {"no_obvious_failure"}:
            scoreboard["clean_cases"] += 1
        for key in list(scoreboard.keys()):
            if key in tags:
                scoreboard[key] += 1
    return scoreboard


def run_single_case(case: dict) -> dict:
    router = route_task(case["question"])
    clarification = should_clarify(case["question"])
    clarified_query = case["question"]
    if clarification.should_clarify and clarification.questions:
        clarified_query = build_clarified_query(
            case["question"],
            clarification.questions,
            case["sample_answers"],
        )

    answer = generate_light_answer(clarified_query, "ADVICE", [])
    failure_tags = detect_failure_tags(case, router, clarification, answer)

    return {
        "case": case,
        "router": {
            "task_type": router.task_type,
            "confidence_score": router.confidence_score,
            "needs_clarification": router.needs_clarification,
            "routing_reason": router.routing_reason,
            "source": router.source,
            "note": router.note,
        },
        "clarifier": {
            "should_clarify": clarification.should_clarify,
            "reason": clarification.reason,
            "questions": clarification.questions,
            "source": clarification.source,
            "note": clarification.note,
        },
        "clarified_query": clarified_query,
        "answer": answer,
        "failure_tags": failure_tags,
    }


def write_case_run(case_result: dict, timestamp: str) -> Path:
    case_id = case_result["case"]["id"]
    run_path = EVAL_RUNS_DIR / f"{timestamp}_{case_id}.json"
    with run_path.open("w", encoding="utf-8") as fh:
        json.dump(case_result, fh, ensure_ascii=False, indent=2)
    return run_path


def build_case_summary_block(case_result: dict, run_path: Path) -> str:
    case = case_result["case"]
    router = case_result["router"]
    clarifier = case_result["clarifier"]
    tags = case_result["failure_tags"]
    answer = case_result["answer"]

    lines = [
        f"## {case['id']}",
        f"- 题目：{case['question']}",
        f"- 类型：{case['type']}",
        f"- 路由结果：`{router['task_type']}` | clarify={router['needs_clarification']} | source={router['source']}",
        f"- Clarifier：`{clarifier['should_clarify']}` | reason=`{clarifier['reason']}` | source={clarifier['source']}",
        f"- 失败标签：{', '.join(tags)}",
        f"- 详细运行记录：`{run_path.relative_to(PROJECT_ROOT)}`",
        "",
        "### 快速观察",
        f"- 约束命中数：{count_constraint_hits(answer, case['expected_constraint_keywords'])}/{len(case['expected_constraint_keywords'])}",
        f"- MBTI 类型名数量：{mbti_type_count(answer)}",
        f"- 是否出现 research 串味：{'是' if 'research_leak' in tags else '否'}",
        f"- 是否出现来源污染：{'是' if 'source_pollution' in tags else '否'}",
        "",
        "### 回答预览",
        answer[:800],
        "",
    ]
    return "\n".join(lines)


def write_eval_summary(results: list[dict], timestamp: str) -> Path:
    EVAL_SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = EVAL_SUMMARIES_DIR / f"eval_summary_{timestamp}.md"
    scoreboard = build_scoreboard(results)

    lines = [
        f"# Advice Eval Summary {timestamp}",
        "",
        f"- 测试题数量：{len(results)}",
        f"- 无明显失败的题目数量：{scoreboard['clean_cases']}",
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
        lines.append(
            f"- `{case['id']}` | route=`{result['router']['task_type']}` | tags={', '.join(result['failure_tags'])}"
        )

    lines.extend(["", "## 逐题摘要", ""])
    for result in results:
        run_path = EVAL_RUNS_DIR / f"{timestamp}_{result['case']['id']}.json"
        lines.append(build_case_summary_block(result, run_path))

    with summary_path.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
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


def main() -> None:
    EVAL_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    EVAL_SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)

    cases = load_cases()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = []

    print(f"[advice_eval] 开始运行 {len(cases)} 道 advice 题")
    for case in cases:
        print(f"[advice_eval] 运行：{case['id']} -> {case['question']}")
        result = run_single_case(case)
        results.append(result)
        write_case_run(result, timestamp)

    summary_path = write_eval_summary(results, timestamp)
    latest_summary_path = write_latest_summary_alias(summary_path)
    latest_runs_dir = write_latest_runs_alias(results, timestamp)
    cleanup_old_evals()

    print(f"[advice_eval] 汇总已生成：{summary_path}")
    print(f"[advice_eval] 最新摘要：{latest_summary_path}")
    print(f"[advice_eval] 最新详细结果目录：{latest_runs_dir}")


if __name__ == "__main__":
    main()
