import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.clarifier import build_clarified_query, should_clarify  # noqa: E402
from agent.planner import build_subquestions, classify_query  # noqa: E402
from agent.router import route_task  # noqa: E402
from agent.rewriter import rewrite_query  # noqa: E402


QUICK_CHECKS_DIR = Path(__file__).resolve().parent
PLANNER_CASES_PATH = QUICK_CHECKS_DIR / "planner_cases.json"
CLARIFIER_CASES_PATH = QUICK_CHECKS_DIR / "clarifier_cases.json"
CLARIFIER_INTEGRATION_CASES_PATH = QUICK_CHECKS_DIR / "clarifier_integration_cases.json"
ROUTER_CASES_PATH = QUICK_CHECKS_DIR / "router_cases.json"
REWRITER_CASES_PATH = QUICK_CHECKS_DIR / "rewriter_cases.json"


def load_cases(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def filter_cases(cases: list[dict], case_filter: str | None) -> list[dict]:
    if not case_filter:
        return cases
    return [case for case in cases if case["id"] == case_filter]


def build_planner_case_summary(
    expected_type: str,
    actual_type: str,
    expected_keywords: list[str],
    joined_subquestions: str,
) -> dict:
    matched_keywords = [
        keyword for keyword in expected_keywords if keyword in joined_subquestions
    ]
    missing_keywords = [
        keyword for keyword in expected_keywords if keyword not in joined_subquestions
    ]

    return {
        "type_ok": actual_type == expected_type,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "keywords_ok": not missing_keywords,
    }


def print_planner_case_result(
    case: dict,
    actual_type: str,
    subquestions: list[str],
    summary: dict,
) -> None:
    case_ok = summary["type_ok"] and summary["keywords_ok"]
    print(f"[{'PASS' if case_ok else 'FAIL'}] {case['id']}")
    print(f"  query: {case['query']}")
    print(f"  expected_type: {case['expected_type']}")
    print(f"  actual_type:   {actual_type}")
    print(f"  type_check:    {'PASS' if summary['type_ok'] else 'FAIL'}")
    print(
        f"  template_check:{' PASS' if summary['keywords_ok'] else ' FAIL'}"
        f" | matched={len(summary['matched_keywords'])}/{len(case['expected_keywords'])}"
    )

    if summary["matched_keywords"]:
        print(f"  matched_keywords: {', '.join(summary['matched_keywords'])}")
    if summary["missing_keywords"]:
        print(f"  missing_keywords: {', '.join(summary['missing_keywords'])}")

    if case_ok:
        print("  why_pass: 题型识别正确，且子问题模板覆盖了预期方向。")
    else:
        reasons = []
        if not summary["type_ok"]:
            reasons.append("题型识别和预期不一致")
        if not summary["keywords_ok"]:
            reasons.append("子问题模板没有覆盖预期关键词")
        print(f"  why_fail: {'；'.join(reasons)}。")

    print("  subquestions:")
    for index, subquestion in enumerate(subquestions, 1):
        print(f"    {index}. {subquestion}")
    print()


def run_planner_checks(case_filter: str | None = None) -> int:
    cases = filter_cases(load_cases(PLANNER_CASES_PATH), case_filter)
    if not cases:
        print("No matching planner quick-check case found.")
        return 1

    failures = 0
    total_type_failures = 0
    total_template_failures = 0

    print("Quick Check: planner")
    print("检查项：题型识别 + 子问题模板方向")
    print()

    for case in cases:
        query = case["query"]
        actual_type = classify_query(query)
        subquestions = build_subquestions(query, actual_type)
        joined_subquestions = " ".join(subquestions)
        summary = build_planner_case_summary(
            expected_type=case["expected_type"],
            actual_type=actual_type,
            expected_keywords=case["expected_keywords"],
            joined_subquestions=joined_subquestions,
        )
        case_ok = summary["type_ok"] and summary["keywords_ok"]
        if not case_ok:
            failures += 1
        if not summary["type_ok"]:
            total_type_failures += 1
        if not summary["keywords_ok"]:
            total_template_failures += 1
        print_planner_case_result(case, actual_type, subquestions, summary)

    passed = len(cases) - failures
    print(f"planner quick checks: {passed}/{len(cases)} passed")
    print(
        "summary:"
        f" type_failures={total_type_failures},"
        f" template_failures={total_template_failures},"
        f" total_failures={failures}"
    )
    if failures:
        print("next_step: 先修 planner 的局部逻辑，再跑 mini_eval 或 full eval。")
    else:
        print("next_step: planner 快验证通过，可以进入更高层回归。")
    print()
    return failures


def build_clarifier_case_summary(case: dict, result) -> dict:
    joined_questions = " ".join(result.questions)
    expected_question_keywords = case.get("expected_question_keywords", [])
    matched_question_keywords = [
        keyword for keyword in expected_question_keywords if keyword in joined_questions
    ]
    missing_question_keywords = [
        keyword for keyword in expected_question_keywords if keyword not in joined_questions
    ]

    sample_answers = case.get("sample_answers", [])
    clarified_query = build_clarified_query(case["query"], result.questions, sample_answers)
    expected_clarified_keywords = case.get("expected_clarified_keywords", [])
    missing_clarified_keywords = [
        keyword for keyword in expected_clarified_keywords if keyword not in clarified_query
    ]

    return {
        "actual_should_clarify": result.should_clarify,
        "actual_reason": result.reason,
        "actual_questions": result.questions,
        "trigger_ok": result.should_clarify == case["expected_should_clarify"],
        "reason_ok": result.reason == case["expected_reason"],
        "question_keywords_ok": not missing_question_keywords,
        "matched_question_keywords": matched_question_keywords,
        "missing_question_keywords": missing_question_keywords,
        "clarified_query": clarified_query,
        "clarified_query_ok": not missing_clarified_keywords,
        "missing_clarified_keywords": missing_clarified_keywords,
    }


def print_clarifier_case_result(case: dict, summary: dict) -> None:
    case_ok = (
        summary["trigger_ok"]
        and summary["reason_ok"]
        and summary["question_keywords_ok"]
        and summary["clarified_query_ok"]
    )
    print(f"[{'PASS' if case_ok else 'FAIL'}] {case['id']}")
    print(f"  query: {case['query']}")
    print(f"  expected_should_clarify: {case['expected_should_clarify']}")
    print(f"  actual_should_clarify:   {summary['actual_should_clarify']}")
    print(f"  expected_reason:         {case['expected_reason']}")
    print(f"  actual_reason:           {summary['actual_reason']}")
    print(f"  trigger_check:           {'PASS' if summary['trigger_ok'] else 'FAIL'}")
    print(f"  reason_check:            {'PASS' if summary['reason_ok'] else 'FAIL'}")
    print(
        "  question_check:          "
        f"{'PASS' if summary['question_keywords_ok'] else 'FAIL'}"
    )
    print(
        "  clarified_query_check:   "
        f"{'PASS' if summary['clarified_query_ok'] else 'FAIL'}"
    )

    if summary["matched_question_keywords"]:
        print(
            "  matched_question_keywords: "
            + ", ".join(summary["matched_question_keywords"])
        )
    if summary["missing_question_keywords"]:
        print(
            "  missing_question_keywords: "
            + ", ".join(summary["missing_question_keywords"])
        )
    if summary["missing_clarified_keywords"]:
        print(
            "  missing_clarified_keywords: "
            + ", ".join(summary["missing_clarified_keywords"])
        )

    if case_ok:
        print("  why_pass: Clarifier 触发、分类和补充约束拼接都符合预期。")
    else:
        reasons = []
        if not summary["trigger_ok"]:
            reasons.append("是否触发澄清和预期不一致")
        if not summary["reason_ok"]:
            reasons.append("澄清原因分类不对")
        if not summary["question_keywords_ok"]:
            reasons.append("澄清问题没有覆盖预期方向")
        if not summary["clarified_query_ok"]:
            reasons.append("补充约束没有正确拼进澄清后 query")
        print(f"  why_fail: {'；'.join(reasons)}。")

    if summary["actual_questions"]:
        print("  clarification_questions:")
        for index, question in enumerate(summary["actual_questions"], 1):
            print(f"    {index}. {question}")
    else:
        print("  clarification_questions: <none>")
    print("  clarified_query_preview:")
    print(f"    {summary['clarified_query']}")
    print()


def run_clarifier_checks(case_filter: str | None = None) -> int:
    cases = filter_cases(load_cases(CLARIFIER_CASES_PATH), case_filter)
    if not cases:
        print("No matching clarifier quick-check case found.")
        return 1

    failures = 0
    trigger_failures = 0
    reason_failures = 0
    question_failures = 0
    clarified_query_failures = 0

    print("Quick Check: clarifier")
    print("检查项：是否触发澄清 + 澄清原因 + 澄清问题方向 + 补充约束拼接")
    print()

    for case in cases:
        result = should_clarify(case["query"])
        summary = build_clarifier_case_summary(case, result)
        case_ok = (
            summary["trigger_ok"]
            and summary["reason_ok"]
            and summary["question_keywords_ok"]
            and summary["clarified_query_ok"]
        )

        if not case_ok:
            failures += 1
        if not summary["trigger_ok"]:
            trigger_failures += 1
        if not summary["reason_ok"]:
            reason_failures += 1
        if not summary["question_keywords_ok"]:
            question_failures += 1
        if not summary["clarified_query_ok"]:
            clarified_query_failures += 1

        print_clarifier_case_result(case, summary)

    passed = len(cases) - failures
    print(f"clarifier quick checks: {passed}/{len(cases)} passed")
    print(
        "summary:"
        f" trigger_failures={trigger_failures},"
        f" reason_failures={reason_failures},"
        f" question_failures={question_failures},"
        f" clarified_query_failures={clarified_query_failures},"
        f" total_failures={failures}"
    )
    if failures:
        print("next_step: 先修 Clarifier 触发或拼接逻辑，再回到交互链路试跑。")
    else:
        print("next_step: Clarifier 快验证通过，可以继续做更高层集成验证。")
    print()
    return failures


def build_clarifier_integration_summary(case: dict) -> dict:
    clarification = should_clarify(case["query"])
    clarified_query = build_clarified_query(
        case["query"],
        clarification.questions,
        case["sample_answers"],
    )
    planner_type = classify_query(clarified_query)
    subquestions = build_subquestions(clarified_query, planner_type)
    joined_subquestions = " ".join(subquestions)

    expected_subquestion_keywords = case["expected_subquestion_keywords"]
    expected_constraint_keywords = case["expected_constraint_keywords"]

    missing_subquestion_keywords = [
        keyword for keyword in expected_subquestion_keywords if keyword not in joined_subquestions
    ]
    missing_constraint_keywords = [
        keyword for keyword in expected_constraint_keywords if keyword not in joined_subquestions
    ]

    return {
        "clarifier_reason_ok": clarification.reason == case["expected_clarifier_reason"],
        "planner_type_ok": planner_type == case["expected_planner_type"],
        "subquestion_keywords_ok": not missing_subquestion_keywords,
        "constraint_keywords_ok": not missing_constraint_keywords,
        "clarification": clarification,
        "clarified_query": clarified_query,
        "planner_type": planner_type,
        "subquestions": subquestions,
        "missing_subquestion_keywords": missing_subquestion_keywords,
        "missing_constraint_keywords": missing_constraint_keywords,
    }


def print_clarifier_integration_result(case: dict, summary: dict) -> None:
    case_ok = (
        summary["clarifier_reason_ok"]
        and summary["planner_type_ok"]
        and summary["subquestion_keywords_ok"]
        and summary["constraint_keywords_ok"]
    )
    print(f"[{'PASS' if case_ok else 'FAIL'}] {case['id']}")
    print(f"  query: {case['query']}")
    print(f"  expected_clarifier_reason: {case['expected_clarifier_reason']}")
    print(f"  actual_clarifier_reason:   {summary['clarification'].reason}")
    print(f"  expected_planner_type:     {case['expected_planner_type']}")
    print(f"  actual_planner_type:       {summary['planner_type']}")
    print(
        f"  clarifier_reason_check:    {'PASS' if summary['clarifier_reason_ok'] else 'FAIL'}"
    )
    print(
        f"  planner_type_check:        {'PASS' if summary['planner_type_ok'] else 'FAIL'}"
    )
    print(
        f"  subquestion_check:         {'PASS' if summary['subquestion_keywords_ok'] else 'FAIL'}"
    )
    print(
        f"  constraint_flow_check:     {'PASS' if summary['constraint_keywords_ok'] else 'FAIL'}"
    )

    if summary["missing_subquestion_keywords"]:
        print(
            "  missing_subquestion_keywords: "
            + ", ".join(summary["missing_subquestion_keywords"])
        )
    if summary["missing_constraint_keywords"]:
        print(
            "  missing_constraint_keywords: "
            + ", ".join(summary["missing_constraint_keywords"])
        )

    if case_ok:
        print("  why_pass: Clarifier 的补充约束已经真正流入了 Planner。")
    else:
        reasons = []
        if not summary["clarifier_reason_ok"]:
            reasons.append("Clarifier 分类不对")
        if not summary["planner_type_ok"]:
            reasons.append("澄清后 Planner 题型不对")
        if not summary["subquestion_keywords_ok"]:
            reasons.append("澄清后子问题模板方向不对")
        if not summary["constraint_keywords_ok"]:
            reasons.append("补充约束没有流进子问题")
        print(f"  why_fail: {'；'.join(reasons)}。")

    print("  clarified_query:")
    print(f"    {summary['clarified_query']}")
    print("  subquestions:")
    for index, subquestion in enumerate(summary["subquestions"], 1):
        print(f"    {index}. {subquestion}")
    print()


def run_clarifier_integration_checks(case_filter: str | None = None) -> int:
    cases = filter_cases(load_cases(CLARIFIER_INTEGRATION_CASES_PATH), case_filter)
    if not cases:
        print("No matching clarifier integration case found.")
        return 1

    failures = 0
    reason_failures = 0
    planner_type_failures = 0
    subquestion_failures = 0
    constraint_flow_failures = 0

    print("Quick Check: clarifier_integration")
    print("检查项：Clarifier 补充约束是否真正影响后续 Planner")
    print()

    for case in cases:
        summary = build_clarifier_integration_summary(case)
        case_ok = (
            summary["clarifier_reason_ok"]
            and summary["planner_type_ok"]
            and summary["subquestion_keywords_ok"]
            and summary["constraint_keywords_ok"]
        )
        if not case_ok:
            failures += 1
        if not summary["clarifier_reason_ok"]:
            reason_failures += 1
        if not summary["planner_type_ok"]:
            planner_type_failures += 1
        if not summary["subquestion_keywords_ok"]:
            subquestion_failures += 1
        if not summary["constraint_keywords_ok"]:
            constraint_flow_failures += 1
        print_clarifier_integration_result(case, summary)

    passed = len(cases) - failures
    print(f"clarifier integration checks: {passed}/{len(cases)} passed")
    print(
        "summary:"
        f" reason_failures={reason_failures},"
        f" planner_type_failures={planner_type_failures},"
        f" subquestion_failures={subquestion_failures},"
        f" constraint_flow_failures={constraint_flow_failures},"
        f" total_failures={failures}"
    )
    if failures:
        print("next_step: 先修 Clarifier 到 Planner 的衔接，再做交互试跑。")
    else:
        print("next_step: Clarifier 已经进入集成快验证阶段，可以考虑扩样本。")
    print()
    return failures


def print_router_case_result(case: dict, decision) -> None:
    type_ok = decision.task_type == case["expected_task_type"]
    clarify_ok = decision.needs_clarification == case["expected_needs_clarification"]
    case_ok = type_ok and clarify_ok

    print(f"[{'PASS' if case_ok else 'FAIL'}] {case['id']}")
    print(f"  query: {case['query']}")
    print(f"  expected_task_type:        {case['expected_task_type']}")
    print(f"  actual_task_type:          {decision.task_type}")
    print(f"  expected_needs_clarify:    {case['expected_needs_clarification']}")
    print(f"  actual_needs_clarify:      {decision.needs_clarification}")
    print(f"  routing_source:            {decision.source}")
    print(f"  confidence_score:          {decision.confidence_score:.2f}")
    print(f"  type_check:                {'PASS' if type_ok else 'FAIL'}")
    print(f"  clarification_check:       {'PASS' if clarify_ok else 'FAIL'}")
    print(f"  routing_reason:            {decision.routing_reason}")
    if decision.note:
        print(f"  routing_note:              {decision.note}")
    print()


def run_router_checks(case_filter: str | None = None) -> int:
    cases = filter_cases(load_cases(ROUTER_CASES_PATH), case_filter)
    if not cases:
        print("No matching router quick-check case found.")
        return 1

    failures = 0
    type_failures = 0
    clarification_failures = 0

    print("Quick Check: router")
    print("检查项：任务类型路由 + 是否需要前置澄清")
    print()

    for case in cases:
        decision = route_task(case["query"])
        type_ok = decision.task_type == case["expected_task_type"]
        clarify_ok = decision.needs_clarification == case["expected_needs_clarification"]
        if not (type_ok and clarify_ok):
            failures += 1
        if not type_ok:
            type_failures += 1
        if not clarify_ok:
            clarification_failures += 1
        print_router_case_result(case, decision)

    passed = len(cases) - failures
    print(f"router quick checks: {passed}/{len(cases)} passed")
    print(
        "summary:"
        f" type_failures={type_failures},"
        f" clarification_failures={clarification_failures},"
        f" total_failures={failures}"
    )
    print()
    return failures


def build_rewriter_case_summary(case: dict) -> dict:
    actual_query = rewrite_query(
        case["sub_question"],
        case["reflection"],
        case["round_num"],
    )
    matched_includes = [
        keyword for keyword in case.get("must_include", []) if keyword in actual_query
    ]
    missing_includes = [
        keyword for keyword in case.get("must_include", []) if keyword not in actual_query
    ]
    leaked_excludes = [
        keyword for keyword in case.get("must_exclude", []) if keyword in actual_query
    ]
    return {
        "actual_query": actual_query,
        "includes_ok": not missing_includes,
        "excludes_ok": not leaked_excludes,
        "matched_includes": matched_includes,
        "missing_includes": missing_includes,
        "leaked_excludes": leaked_excludes,
    }


def print_rewriter_case_result(case: dict, summary: dict) -> None:
    case_ok = summary["includes_ok"] and summary["excludes_ok"]
    print(f"[{'PASS' if case_ok else 'FAIL'}] {case['id']}")
    print(f"  sub_question: {case['sub_question']}")
    print(f"  round_num:    {case['round_num']}")
    print(f"  include_check:{' PASS' if summary['includes_ok'] else ' FAIL'}")
    print(f"  exclude_check:{' PASS' if summary['excludes_ok'] else ' FAIL'}")
    if summary["matched_includes"]:
        print(f"  matched_includes: {', '.join(summary['matched_includes'])}")
    if summary["missing_includes"]:
        print(f"  missing_includes: {', '.join(summary['missing_includes'])}")
    if summary["leaked_excludes"]:
        print(f"  leaked_excludes: {', '.join(summary['leaked_excludes'])}")
    if case_ok:
        print("  why_pass: query 重写方向符合当前题型预期。")
    else:
        reasons = []
        if not summary["includes_ok"]:
            reasons.append("缺少预期方向关键词")
        if not summary["excludes_ok"]:
            reasons.append("混入了不该出现的串题词")
        print(f"  why_fail: {'；'.join(reasons)}。")
    print("  rewritten_query:")
    print(f"    {summary['actual_query']}")
    print()


def run_rewriter_checks(case_filter: str | None = None) -> int:
    cases = filter_cases(load_cases(REWRITER_CASES_PATH), case_filter)
    if not cases:
        print("No matching rewriter quick-check case found.")
        return 1

    failures = 0
    include_failures = 0
    exclude_failures = 0

    print("Quick Check: rewriter")
    print("检查项：query 重写方向是否贴题，是否出现串题词泄漏")
    print()

    for case in cases:
        summary = build_rewriter_case_summary(case)
        case_ok = summary["includes_ok"] and summary["excludes_ok"]
        if not case_ok:
            failures += 1
        if not summary["includes_ok"]:
            include_failures += 1
        if not summary["excludes_ok"]:
            exclude_failures += 1
        print_rewriter_case_result(case, summary)

    passed = len(cases) - failures
    print(f"rewriter quick checks: {passed}/{len(cases)} passed")
    print(
        "summary:"
        f" include_failures={include_failures},"
        f" exclude_failures={exclude_failures},"
        f" total_failures={failures}"
    )
    if failures:
        print("next_step: 先修 rewriter 的题型化重写逻辑，再回到 research 手测。")
    else:
        print("next_step: rewriter 快验证通过，可以继续做 research 小样本回归。")
    print()
    return failures



def main() -> int:
    parser = argparse.ArgumentParser(description="Run fast local quick checks.")
    parser.add_argument(
        "--suite",
        choices=["planner", "clarifier", "clarifier_integration", "router", "rewriter", "all"],
        default="all",
        help="Choose which quick-check suite to run.",
    )
    parser.add_argument(
        "--case",
        help="Run only one quick-check case by id.",
    )
    args = parser.parse_args()

    total_failures = 0
    if args.suite in {"router", "all"}:
        total_failures += run_router_checks(args.case)
    if args.suite in {"planner", "all"}:
        total_failures += run_planner_checks(args.case)
    if args.suite in {"clarifier", "all"}:
        total_failures += run_clarifier_checks(args.case)
    if args.suite in {"clarifier_integration", "all"}:
        total_failures += run_clarifier_integration_checks(args.case)
    if args.suite in {"rewriter", "all"}:
        total_failures += run_rewriter_checks(args.case)

    return 1 if total_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())



