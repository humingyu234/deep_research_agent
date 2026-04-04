import re


TREND_SIGNAL_HINTS = [
    "趋势",
    "主线",
    "发展",
    "现状",
    "目前",
    "表现",
    "实际情况",
]

DRIVER_SIGNAL_HINTS = [
    "驱动",
    "推动",
    "原因",
    "因素",
    "机制",
    "关键变量",
    "约束",
]

RISK_SIGNAL_HINTS = [
    "风险",
    "限制",
    "挑战",
    "安全",
    "合规",
    "治理",
    "争议",
]

CHANGE_SIGNAL_HINTS = [
    "未来",
    "变化",
    "演进",
    "方向",
    "接下来",
    "演化",
]

DEFINITION_SIGNAL_HINTS = [
    "定义",
    "含义",
    "基本含义",
    "组成",
    "工作原理",
    "核心机制",
    "区别",
    "混淆",
]

RECOMMENDATION_SIGNAL_HINTS = [
    "主流可选项",
    "评价维度",
    "选择标准",
    "优缺点",
    "适用人群",
    "使用场景",
    "综合建议",
    "预算",
]

NOISE_MARKERS = [
    "浏览阅读",
    "点赞",
    "收藏",
    "评论",
    ":label:",
    ":numref:",
    "width:",
    "fig_",
    "colab",
    "ipynb",
]

BOILERPLATE_PATTERNS = [
    r"^\s*摘要[:：]\s*",
    r"^\s*结语[:：]\s*",
    r"^\s*本文正文内容如下[:：]?\s*",
    r"浏览阅读\s*\d+(?:\.\d+)?[kK]?\s*次",
    r"点赞\s*\d+(?:\.\d+)?[kK]?\s*次",
    r"收藏\s*\d+(?:\.\d+)?[kK]?\s*次",
    r"评论\s*\d+(?:\.\d+)?[kK]?\s*次",
    r"显示全部.*$",
]


def normalize_text(text: str) -> str:
    return " ".join(str(text or "").split())


def contains_any(text: str, hints: list[str]) -> bool:
    normalized = normalize_text(text)
    return any(hint in normalized for hint in hints)


def extract_focus_text(sub_question: str) -> str:
    text = normalize_text(sub_question)
    for separator in ["？", "?", "。", "."]:
        if separator in text:
            parts = [part.strip() for part in text.split(separator) if part.strip()]
            if len(parts) >= 2:
                return parts[-1]
    return text


def extract_subject(sub_question: str) -> str:
    text = normalize_text(sub_question)
    for separator in ["？", "?", "。", "."]:
        if separator in text:
            parts = [part.strip() for part in text.split(separator) if part.strip()]
            if parts:
                return parts[0]
    return text


def infer_query_focus(sub_question: str) -> str:
    focus_text = extract_focus_text(sub_question)

    if contains_any(focus_text, RECOMMENDATION_SIGNAL_HINTS):
        return "recommendation"
    if contains_any(focus_text, CHANGE_SIGNAL_HINTS):
        return "change"
    if contains_any(focus_text, RISK_SIGNAL_HINTS):
        return "risk"
    if contains_any(focus_text, DRIVER_SIGNAL_HINTS):
        return "driver"
    if contains_any(focus_text, DEFINITION_SIGNAL_HINTS):
        return "definition"
    if contains_any(focus_text, TREND_SIGNAL_HINTS):
        return "trend"
    return "general"


def looks_noisy(text: str) -> bool:
    lowered = normalize_text(text).lower()
    return any(marker in lowered for marker in NOISE_MARKERS)


def clean_support_point(text: str) -> str:
    cleaned = normalize_text(text)
    if not cleaned:
        return ""

    for pattern in BOILERPLATE_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    cleaned = cleaned.strip("，。、；：: ")
    cleaned = re.sub(r"\s+", " ", cleaned)

    if not cleaned:
        return ""

    lowered = cleaned.lower()
    if any(token in lowered for token in ["colab", "ipynb", ":label", ":numref", "width:", "fig_"]):
        return ""

    if len(cleaned) < 16:
        return ""

    # 扔掉明显像残缺句子的支持点。
    if cleaned.count("?") >= 2 or cleaned.count("？") >= 2:
        return ""

    if len(cleaned) > 100:
        cleaned = cleaned[:100].rstrip("，。、；：: ") + "。"

    return cleaned


def should_skip_result(title: str, snippet: str, source: str) -> bool:
    title_text = normalize_text(title)
    snippet_text = normalize_text(snippet)
    source_text = normalize_text(source).lower()

    if not title_text and not snippet_text:
        return True

    if title_text == "SEARCH_ERROR":
        return True

    if "csdn" in source_text and looks_noisy(snippet_text):
        return True

    if looks_noisy(f"{title_text} {snippet_text} {source_text}"):
        return True

    # 过滤明显只剩下页面结构或短促标题的材料。
    if len(snippet_text) < 20 and len(title_text) < 20:
        return True

    return False


def deduplicate_points(points: list[str]) -> list[str]:
    unique_points = []
    seen = set()

    for point in points:
        cleaned = clean_support_point(point)
        if not cleaned:
            continue

        key = cleaned.lower()[:80]
        if key in seen:
            continue

        seen.add(key)
        unique_points.append(cleaned)

    return unique_points


def build_support_points(search_results: list[dict], limit: int = 3) -> list[str]:
    points = []

    for item in search_results:
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        source = item.get("source", "")

        if should_skip_result(title, snippet, source):
            continue

        if snippet:
            points.append(snippet)
        elif title:
            points.append(title)

    return deduplicate_points(points)[:limit]


def join_support_points(points: list[str], limit: int = 2) -> str:
    selected = [point for point in points[:limit] if point]
    return "；".join(selected)


def build_definition_conclusion(sub_question: str, support_points: list[str]) -> str:
    subject = extract_subject(sub_question)
    focus_text = extract_focus_text(sub_question)
    evidence = join_support_points(support_points)

    if "关键时间节点" in focus_text or "里程碑" in focus_text:
        return f"{subject}过去几年的关键时间节点和里程碑已经比较清楚。" if not evidence else f"{subject}过去几年的关键时间节点和里程碑，主要可以从 {evidence} 这些线索来梳理。"
    if "每个阶段" in focus_text or "代表案例" in focus_text or "事件" in focus_text:
        return f"{subject}各阶段最重要的突破和代表案例已经能形成阶段性梳理。" if not evidence else f"{subject}各阶段最重要的技术突破、事件或代表案例，主要可以从 {evidence} 这些材料里归纳。"
    if "组成" in focus_text or "工作原理" in focus_text or "核心机制" in focus_text:
        return f"{subject}的核心组成和工作原理已经有较清晰的基础判断。" if not evidence else f"{subject}的核心组成、关键机制和工作原理，主要可以从 {evidence} 这些线索来理解。"
    if "区别" in focus_text or "混淆" in focus_text:
        return f"{subject}与相关概念之间的区别已经比较清楚。" if not evidence else f"{subject}与相关概念容易混淆的地方及其区别，主要可以从 {evidence} 这些方面来分开。"
    return f"{subject}的基本含义已经比较清楚。" if not evidence else f"{subject}的基本含义和关键特征，主要可以从 {evidence} 这些线索来把握。"


def build_driver_conclusion(sub_question: str, support_points: list[str]) -> str:
    subject = extract_subject(sub_question)
    evidence = join_support_points(support_points)
    if not evidence:
        return f"{subject}背后的主要原因和驱动因素，当前主要指向技术能力、需求变化和落地条件这几个方向。"
    return f"{subject}背后的主要原因、驱动因素或关键变量，当前材料主要指向 {evidence} 这些方面。"


def build_change_conclusion(sub_question: str, support_points: list[str]) -> str:
    subject = extract_subject(sub_question)
    evidence = join_support_points(support_points)
    if not evidence:
        return f"从当前材料看，{subject}接下来更可能朝着规模化、结构调整或应用扩展这些方向演进。"
    return f"从当前材料看，{subject}接下来更可能围绕 {evidence} 这些方向继续演进。"


def build_risk_conclusion(sub_question: str, support_points: list[str]) -> str:
    subject = extract_subject(sub_question)
    evidence = join_support_points(support_points)
    if not evidence:
        return f"{subject}当前仍存在的主要限制，多集中在治理、可靠性、落地成本或合规约束之中。"
    return f"{subject}当前仍存在的争议、限制或待研究点，主要集中在 {evidence} 这些方面。"


def build_recommendation_conclusion(sub_question: str, support_points: list[str]) -> str:
    subject = extract_subject(sub_question)
    focus_text = extract_focus_text(sub_question)
    evidence = join_support_points(support_points)

    if "评价维度" in focus_text or "选择标准" in focus_text:
        return f"{subject}的评价维度和选择标准已经比较清楚。" if not evidence else f"{subject}最值得参考的评价维度或选择标准，主要可以从 {evidence} 这些方面来展开。"
    if "优缺点" in focus_text or "适用人群" in focus_text or "使用场景" in focus_text:
        return f"{subject}各主要选项的优缺点和适用场景已经能形成基础对比。" if not evidence else f"{subject}各主要选项的优缺点、适用人群和使用场景，主要可以从 {evidence} 这些方面来归纳。"
    if "综合建议" in focus_text:
        return f"{subject}的综合建议已经可以形成较清晰的判断。" if not evidence else f"{subject}在不同目标、预算或约束下的综合建议，主要可以结合 {evidence} 这些线索来给出。"
    return f"{subject}当前更值得关注的主流选项已经比较清楚。" if not evidence else f"{subject}当前更值得关注的选项和判断依据，主要可以从 {evidence} 这些线索来把握。"


def build_general_conclusion(sub_question: str, support_points: list[str]) -> str:
    subject = extract_subject(sub_question)
    focus_text = extract_focus_text(sub_question)
    evidence = join_support_points(support_points)

    if "核心问题" in focus_text or "值得关注" in focus_text:
        return f"{subject}当前最值得关注的核心问题已经比较清楚。" if not evidence else f"{subject}当前最值得关注的核心问题，主要可以从 {evidence} 这些方面来把握。"
    if "主流可选项" in focus_text:
        return f"{subject}当前的主流可选项已经比较清楚。" if not evidence else f"{subject}当前的主流可选项，主要可以从 {evidence} 这些线索来概括。"
    if "差异" in focus_text or "维度" in focus_text or "比较" in focus_text:
        return f"{subject}之间最关键的差异已经能形成比较清晰的框架。" if not evidence else f"{subject}之间最关键的差异，主要可以从 {evidence} 这些方面来比较。"
    if "判断" in focus_text or "建议" in focus_text or "策略" in focus_text:
        return f"基于当前材料，关于 {subject} 已经能形成相对清晰的判断或建议。" if not evidence else f"基于当前材料，关于 {subject} 的判断、选择建议或应对策略，主要可以从 {evidence} 这些线索来收束。"
    return f"关于 {subject}，当前材料已经能形成相对清晰的阶段性判断。" if not evidence else f"关于 {subject}，当前材料主要可以从 {evidence} 这些方面来把握。"


def build_conclusion(sub_question: str, support_points: list[str]) -> str:
    focus = infer_query_focus(sub_question)

    if focus == "definition":
        body = build_definition_conclusion(sub_question, support_points)
    elif focus == "driver":
        body = build_driver_conclusion(sub_question, support_points)
    elif focus == "change":
        body = build_change_conclusion(sub_question, support_points)
    elif focus == "risk":
        body = build_risk_conclusion(sub_question, support_points)
    elif focus == "recommendation":
        body = build_recommendation_conclusion(sub_question, support_points)
    else:
        body = build_general_conclusion(sub_question, support_points)

    return f"关于“{sub_question}”，当前更可靠的判断是：{body}"


def build_boundary_note(search_results: list[dict]) -> str:
    domains = " ".join(normalize_text(item.get("source", "")).lower() for item in search_results)

    if any(token in domains for token in ["36kr", "csdn", "xueqiu", "zhihu", "toutiao", "163.com", "sohu.com"]):
        return "需要注意的是，当前材料仍有一定媒体转述色彩，结论更适合作为方向性判断，而不是已经完全坐实的定论。"
    return ""


def summarize(sub_question: str, search_results: list[dict]) -> str:
    support_points = build_support_points(search_results)
    conclusion = build_conclusion(sub_question, support_points)

    lines = [conclusion]

    if support_points:
        lines.append("")
        lines.append("支撑点：")
        for idx, point in enumerate(support_points, 1):
            lines.append(f"{idx}. {point}")

    boundary_note = build_boundary_note(search_results)
    if boundary_note:
        lines.append("")
        lines.append(boundary_note)

    return "\n".join(lines)
