def normalize_text(text: str) -> str:
    """
    基础文本清洗。
    """
    return " ".join(str(text or "").split())


def deduplicate_points(points: list[str]) -> list[str]:
    """
    对证据点去重，避免总结里来回说同一句话。
    """
    unique_points = []
    seen = set()

    for point in points:
        normalized = normalize_text(point).lower()[:140]
        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        unique_points.append(point.strip())

    return unique_points


def build_support_points(search_results: list[dict]) -> list[str]:
    """
    从搜索结果里抽出可作为“支撑点”的句子。

    这里不是把整段网页摘要原封不动贴上来，
    而是尽量只摘出一小段能支撑判断的信息。
    """
    support_points = []

    for item in search_results:
        title = normalize_text(item.get("title", ""))
        snippet = normalize_text(item.get("snippet", ""))

        if title == "SEARCH_ERROR":
            continue

        if snippet:
            support_points.append(snippet[:120])
        elif title:
            support_points.append(title[:120])

    return deduplicate_points(support_points)


def build_lead_sentence(sub_question: str, support_points: list[str]) -> str:
    """
    先生成一句“自己的判断”。

    现在这个版本仍然是规则法，不是高级抽象推理，
    但目标至少是：
    不要看起来像直接把网页摘要贴回来。
    """
    if not support_points:
        return f'关于“{sub_question}”，当前还没有足够信息形成结论。'

    first_point = support_points[0].rstrip("。；;,. ")

    if "趋势" in sub_question or "未来" in sub_question:
        return f'关于“{sub_question}”，当前材料显示它的主线正在逐步变清晰：{first_point}。'

    if "风险" in sub_question or "限制" in sub_question:
        return f'关于“{sub_question}”，综合当前结果可以先判断：相关风险和限制已经开始集中暴露，尤其体现在{first_point}。'

    if "驱动" in sub_question or "因素" in sub_question:
        return f'关于“{sub_question}”，综合当前结果可以先判断：它背后最值得关注的推动力量主要体现在{first_point}。'

    return f'关于“{sub_question}”，综合当前结果可以先得出一个初步判断：{first_point}。'


def build_uncertainty_sentence(support_points: list[str]) -> str:
    """
    如果支撑点里已经出现明显的不确定性信号，
    就额外补一句“别把这件事看得过于绝对”。
    """
    combined = " ".join(support_points)
    uncertainty_keywords = ["可能", "仍然", "差异", "风险", "限制", "争议", "尚未", "but", "however"]

    if any(keyword in combined for keyword in uncertainty_keywords):
        return "不过，现有信息也提示这个判断并不是绝对结论，仍然要结合具体场景和样本差异来理解。"

    return ""


def summarize(sub_question: str, search_results: list[dict]) -> str:
    """
    将筛选后的结果压缩成：
    - 一句话结论
    - 2~3 条支撑点
    - 必要时补一句不确定性

    这一步的目标不是“写得长”，而是“提炼得像样”。
    """
    if not search_results:
        return f'关于“{sub_question}”，当前没有找到可用信息。'

    support_points = build_support_points(search_results)

    if not support_points:
        return f'关于“{sub_question}”，当前结果里没有足够清晰的有效信息。'

    support_points = support_points[:3]
    lead_sentence = build_lead_sentence(sub_question, support_points)
    uncertainty_sentence = build_uncertainty_sentence(support_points)

    formatted_support = []
    for index, point in enumerate(support_points, 1):
        formatted_support.append(f"{index}. {point}")

    summary_parts = [lead_sentence, "\n".join(formatted_support)]
    if uncertainty_sentence:
        summary_parts.append(uncertainty_sentence)

    return "\n".join(summary_parts)
