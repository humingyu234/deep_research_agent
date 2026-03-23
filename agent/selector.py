from difflib import SequenceMatcher
from typing import List
from urllib.parse import urlparse


# 这些域名默认直接视为低质量来源。
# 它们要么是系统错误占位符，要么不是正经可引用来源。
LOW_QUALITY_DOMAINS = {
    "",
    "system_error",
    "localhost",
    "127.0.0.1",
}

# 这些关键词更像“营销页 / 登录页 / 跳转页”的气味。
# 只要域名里带这些词，就先天然不信任。
LOW_QUALITY_DOMAIN_HINTS = [
    "login",
    "signup",
    "register",
    "advert",
    "promo",
    "tracker",
    "redirect",
]

# 这些词更像“营销稿、软文、导流稿”的正文信号。
# 如果标题或摘要里出现太多这类词，说明这条结果不太像研究资料。
MARKETING_TEXT_HINTS = [
    "立即",
    "马上",
    "抢购",
    "优惠",
    "爆款",
    "限时",
    "点击",
    "咨询",
    "购买",
    "推荐给你",
    "best deal",
    "buy now",
    "limited time",
    "sponsored",
]

# 这些词更像“报告 / 调研 / 方法论 / 框架”的味道。
# selector 会优先保留这类更适合后续总结的结果。
RESEARCH_SIGNAL_HINTS = [
    "报告",
    "调研",
    "研究",
    "数据",
    "统计",
    "分析",
    "framework",
    "report",
    "survey",
    "study",
    "research",
    "white paper",
    "whitepaper",
    "benchmark",
]

# 媒体类内容不是不能用，但如果全是泛新闻，
# 对“驱动因素 / 风险 / 证据”这类研究子问题帮助有限。
MEDIA_SIGNAL_HINTS = [
    "news",
    "新闻网",
    "快讯",
    "资讯",
    "headline",
    "breaking",
]


def normalize_text(text: str) -> str:
    """
    统一文本格式，方便后面做比较、去重和打分。
    """
    return " ".join(str(text or "").lower().split())


def extract_domain(source: str) -> str:
    """
    从 source 中抽出域名。
    """
    source = (source or "").strip()
    if not source:
        return ""

    parsed = urlparse(source if "://" in source else f"https://{source}")
    return parsed.netloc.lower().replace("www.", "")


def contains_any(text: str, hints: list[str]) -> bool:
    """
    小工具函数：判断文本里是否包含某组提示词。
    """
    normalized_text = normalize_text(text)
    return any(hint in normalized_text for hint in hints)


def is_low_quality_source(source: str) -> bool:
    """
    判断来源本身靠不靠谱。

    你可以把它理解成第一道门卫：
    来源本身就不对劲的，尽量别让它进厨房。
    """
    domain = extract_domain(source)

    if domain in LOW_QUALITY_DOMAINS:
        return True

    return any(hint in domain for hint in LOW_QUALITY_DOMAIN_HINTS)


def is_marketing_like(result: dict) -> bool:
    """
    判断这一条结果像不像营销稿。

    这里不是追求 100% 准确，而是做“明显软文先拦下来”的粗筛。
    """
    title = normalize_text(result.get("title", ""))
    snippet = normalize_text(result.get("snippet", ""))
    combined = f"{title} {snippet}"

    marketing_hits = sum(1 for hint in MARKETING_TEXT_HINTS if hint in combined)
    return marketing_hits >= 2


def result_similarity(left: dict, right: dict) -> float:
    """
    粗略计算两条结果有多像。

    这里用的是标准库里的 SequenceMatcher，
    不是最强方案，但足够拿来压掉“换个说法重复讲同一件事”的结果。
    """
    left_text = normalize_text(
        f"{left.get('title', '')} {left.get('snippet', '')}"
    )
    right_text = normalize_text(
        f"{right.get('title', '')} {right.get('snippet', '')}"
    )

    if not left_text or not right_text:
        return 0.0

    return SequenceMatcher(None, left_text[:400], right_text[:400]).ratio()


def deduplicate_results(results: List[dict]) -> List[dict]:
    """
    给搜索结果去重，并压掉重复转述。

    直观理解：
    如果两条结果只是换了个包装说同一件事，
    就没必要两盘都端给 Summarizer。
    """
    unique_results = []

    for item in results:
        title = normalize_text(item.get("title", ""))
        snippet = normalize_text(item.get("snippet", ""))
        source = normalize_text(item.get("source", ""))

        if not title and not snippet:
            continue

        is_duplicate = False
        for existing_item in unique_results:
            existing_title = normalize_text(existing_item.get("title", ""))
            existing_source = normalize_text(existing_item.get("source", ""))

            # 同标题同来源，基本可以视为同一条。
            if title and title == existing_title and source == existing_source:
                is_duplicate = True
                break

            # 标题不同但正文高度相似，也视为重复转述。
            if result_similarity(item, existing_item) >= 0.88:
                is_duplicate = True
                break

        if not is_duplicate:
            unique_results.append(item)

    return unique_results


def score_result(query: str, result: dict) -> int:
    """
    给单条结果打分。

    核心思路：
    - 更贴题，加分
    - 更像报告/调研/框架内容，加分
    - 更像营销稿，扣分
    - 摘要更充实，加分
    - 纯新闻味太重，轻微扣分
    """
    query_tokens = [token for token in normalize_text(query).split() if len(token) > 1]
    title = normalize_text(result.get("title", ""))
    snippet = normalize_text(result.get("snippet", ""))
    source = normalize_text(result.get("source", ""))
    combined = f"{title} {snippet}"

    score = 0

    if not title and not snippet:
        return -999

    if is_low_quality_source(source):
        score -= 6

    if is_marketing_like(result):
        score -= 8

    # 摘要太短，通常说明这条结果给不了太多有效信息。
    if len(snippet) >= 120:
        score += 3
    elif len(snippet) >= 70:
        score += 2
    elif len(snippet) >= 40:
        score += 1
    else:
        score -= 2

    unique_query_hits = {token for token in query_tokens if token in combined}
    score += len(unique_query_hits) * 2

    if title:
        score += 1

    # 更像“报告/调研/框架”的结果，额外加分。
    if contains_any(combined, RESEARCH_SIGNAL_HINTS):
        score += 4

    # 偏新闻稿气质的结果，不是一票否决，但优先级往后放一点。
    if contains_any(combined, MEDIA_SIGNAL_HINTS):
        score -= 1

    return score


def select_top_results(query: str, results: List[dict], top_k: int = 3) -> List[dict]:
    """
    Selector 对外主入口。

    它像一个“资料编辑台”：
    1. 先去掉脏结果
    2. 再压掉重复转述
    3. 再给剩下的内容打分
    4. 最后只留最值得喂给 Summarizer 的前几条
    """
    clean_candidates = []
    for item in results:
        if is_low_quality_source(item.get("source", "")):
            continue
        if is_marketing_like(item):
            continue
        clean_candidates.append(item)

    deduped_results = deduplicate_results(clean_candidates)

    scored_results = []
    for item in deduped_results:
        score = score_result(query, item)
        if score < 0:
            continue

        enriched_item = dict(item)
        enriched_item["_score"] = score
        scored_results.append(enriched_item)

    scored_results.sort(
        key=lambda item: (
            item.get("_score", 0),
            contains_any(
                f"{item.get('title', '')} {item.get('snippet', '')}",
                RESEARCH_SIGNAL_HINTS,
            ),
            len(item.get("snippet", "")),
            len(item.get("title", "")),
        ),
        reverse=True,
    )

    selected = []
    for item in scored_results[:top_k]:
        clean_item = dict(item)
        clean_item.pop("_score", None)
        selected.append(clean_item)

    return selected
