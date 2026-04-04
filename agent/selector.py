import re
from difflib import SequenceMatcher
from typing import List
from urllib.parse import urlparse


LOW_QUALITY_DOMAINS = {
    "",
    "system_error",
    "localhost",
    "127.0.0.1",
    "bing.com",
    "archiveofourown.org",
    "smallcolor.art",
    "cloudfront.net",
}

LOW_QUALITY_DOMAIN_HINTS = [
    "login",
    "signup",
    "register",
    "advert",
    "promo",
    "tracker",
    "redirect",
]

MARKETING_TEXT_HINTS = [
    "\u7acb\u5373",
    "\u9a6c\u4e0a",
    "\u62a2\u8d2d",
    "\u4f18\u60e0",
    "\u7206\u6b3e",
    "\u9650\u65f6",
    "\u70b9\u51fb",
    "\u54a8\u8be2",
    "\u8d2d\u4e70",
    "\u63a8\u8350\u7ed9\u4f60",
    "best deal",
    "buy now",
    "limited time",
    "sponsored",
]

RECOMMENDATION_SIGNAL_HINTS = [
    "\u8bc4\u6d4b",
    "\u6d4b\u8bc4",
    "\u6a2a\u8bc4",
    "\u5bf9\u6bd4",
    "\u6392\u884c",
    "\u4f18\u7f3a\u70b9",
    "\u9002\u7528\u4eba\u7fa4",
    "\u4f7f\u7528\u573a\u666f",
    "review",
    "comparison",
    "rank",
    "best",
]

RESEARCH_SIGNAL_HINTS = [
    "\u62a5\u544a",
    "\u8c03\u7814",
    "\u7814\u7a76",
    "\u6570\u636e",
    "\u7edf\u8ba1",
    "\u5206\u6790",
    "\u767d\u76ae\u4e66",
    "framework",
    "report",
    "survey",
    "study",
    "research",
    "white paper",
    "whitepaper",
    "benchmark",
]

REPOST_TEXT_HINTS = [
    "\u4e00\u6587\u5e26\u4f60",
    "\u5e26\u4f60\u89e3\u8bfb",
    "\u6df1\u5165\u89e3\u8bfb",
    "\u89e3\u8bfb",
    "\u8f6c\u8f7d",
    "\u8f6c\u81ea",
    "\u6574\u7406\u81ea",
    "\u5feb\u8bc4",
    "\u76d8\u70b9",
    "\u535a\u5ba2",
    "blog",
    "\u4e13\u680f",
]

AGGREGATOR_DOMAIN_HINTS = [
    "zhihu.com",
    "csdn.net",
    "sina.com",
    "sohu.com",
    "toutiao.com",
    "163.com",
    "xueqiu.com",
]

PRIMARY_DOMAIN_HINTS = [
    ".gov",
    ".edu",
    ".org",
    "mckinsey.com",
    "gartner.com",
    "forrester.com",
    "deloitte.com",
    "bcg.com",
    "ibm.com",
    "google.com",
    "openai.com",
    "anthropic.com",
    "news.cn",
]

OFF_TOPIC_HINTS = [
    "vpn",
    "\u89c6\u9891",
    "\u5f71\u89c6",
    "\u540c\u4eba",
    "\u5c0f\u8bf4",
    "fanfic",
    "genshin",
    "\u539f\u795e",
    "\u6218\u8230",
    "\u6b66\u5668",
    "\u6e38\u620f",
]

DRIVER_SIGNAL_HINTS = [
    "\u9a71\u52a8",
    "\u63a8\u52a8",
    "\u539f\u56e0",
    "\u56e0\u7d20",
    "\u56e0\u4e3a",
    "\u5bfc\u81f4",
    "\u673a\u5236",
    "\u5173\u952e\u53d8\u91cf",
    "\u7ea6\u675f",
    "\u8f6c\u6298\u70b9",
    "factor",
    "driver",
    "cause",
    "because",
    "why",
    "reason",
    "trigger",
    "constraint",
    "bottleneck",
    "adoption",
    "roi",
    "return on investment",
    "penetration",
    "integration",
    "governance",
]

RISK_SIGNAL_HINTS = [
    "\u98ce\u9669",
    "\u9650\u5236",
    "\u6311\u6218",
    "\u95ee\u9898",
    "\u4e0d\u8db3",
    "\u6cbb\u7406",
    "\u5b89\u5168",
    "\u5408\u89c4",
    "risk",
    "limitation",
    "challenge",
]

CHANGE_SIGNAL_HINTS = [
    "\u672a\u6765",
    "\u53d8\u5316",
    "\u8d8b\u52bf",
    "\u6f14\u8fdb",
    "\u65b9\u5411",
    "\u8f6c\u5411",
    "next",
    "future",
    "trend",
    "shift",
]

COMPARISON_SIGNAL_HINTS = [
    "\u5dee\u5f02",
    "\u6bd4\u8f83",
    "\u5bf9\u6bd4",
    "\u7ef4\u5ea6",
    "\u4e2d\u7f8e",
    "\u5206\u522b",
]


COMPARISON_CONTEXT_HINTS = [
    "就业市场",
    "岗位需求",
    "技能门槛",
    "招聘趋势",
    "劳动力市场",
    "职业路径",
    "中国",
    "美国",
    "中美",
    "cross-country",
    "labor market",
    "job demand",
    "skill requirement",
    "career path",
    "hiring trend",
    "china",
    "us",
    "u.s.",
]

EDUCATION_ADMISSIONS_HINTS = [
    "招生",
    "专业介绍",
    "学位",
    "课程",
    "雅思",
    "ielts",
    "admission",
    "degree",
    "curriculum",
]

DRIVER_CONTEXT_HINTS = [
    "\u9700\u6c42\u53d8\u5316",
    "\u4f01\u4e1a\u91c7\u7528",
    "\u89c4\u6a21\u5316",
    "\u5546\u4e1a\u4ef7\u503c",
    "\u5e02\u573a\u589e\u957f",
    "\u6280\u672f\u6210\u719f",
    "\u6210\u672c\u4e0b\u964d",
    "\u6548\u7387\u63d0\u5347",
    "\u751f\u4ea7\u529b",
    "\u5de5\u4f5c\u6d41",
    "\u90e8\u7f72",
    "\u96c6\u6210",
    "\u7ba1\u7406",
    "business model",
    "workflow integration",
    "customer support",
    "market demand",
    "enterprise software",
    "infrastructure",
    "deployment",
    "compliance pressure",
    "labor cost",
    "productivity",
    "case study",
]

MECHANISM_SIGNAL_HINTS = [
    "\u4f5c\u7528\u673a\u5236",
    "\u901a\u8fc7",
    "\u4ece\u800c",
    "\u4fc3\u4f7f",
    "\u51b3\u5b9a",
    "\u53d6\u51b3\u4e8e",
    "\u6760\u6746",
    "\u5173\u952e\u53d8\u91cf",
    "\u7ea6\u675f",
    "\u74f6\u9888",
    "\u4e2d\u8bd5",
    "\u91cf\u4ea7",
    "\u5546\u4e1a\u5316",
    "\u4f9b\u5e94\u94fe",
    "\u6210\u672c\u66f2\u7ebf",
    "driven by",
    "depends on",
    "led to",
    "enabled by",
    "mechanism",
    "tradeoff",
    "pilot line",
    "commercialization",
    "supply chain",
]

PURE_TREND_SIGNAL_HINTS = [
    "\u5f7b\u5e95\u706b\u4e86",
    "\u70ed\u5ea6",
    "\u8d8b\u52bf",
    "\u5230\u5e95\u4f1a\u8d70\u5411\u54ea",
    "\u6700\u65b0\u8c03\u7814",
    "\u4e09\u5927\u8d8b\u52bf",
    "\u516d\u5927\u8d8b\u52bf",
    "\u5168\u666f\u56fe",
    "landscape",
    "trend",
]

AI_AGENT_HINTS = [
    "ai agent",
    "agent",
    "\u667a\u80fd\u4f53",
    "\u4ee3\u7406",
]

ENTERPRISE_HINTS = [
    "\u4f01\u4e1a",
    "\u90e8\u7f72",
    "\u4e1a\u52a1\u6d41\u7a0b",
    "\u5de5\u4f5c\u6d41",
    "\u96c6\u6210",
    "\u91c7\u7528",
    "\u7ec4\u7ec7",
    "enterprise",
    "deployment",
    "workflow",
    "integration",
    "adoption",
]

BATTERY_HINTS = [
    "\u56fa\u6001\u7535\u6c60",
    "\u7535\u6c60",
    "\u91cf\u4ea7",
    "\u5546\u4e1a\u5316",
    "\u4e2d\u8bd5",
    "\u8f66\u4f01",
    "\u4f9b\u5e94\u94fe",
    "solid-state",
    "battery",
    "pilot line",
]

BATTERY_DRIVER_HINTS = [
    "\u4e2d\u8bd5\u7ebf",
    "\u826f\u7387",
    "\u6210\u672c",
    "\u6210\u672c\u66f2\u7ebf",
    "\u754c\u9762",
    "\u754c\u9762\u7a33\u5b9a",
    "\u8f66\u4f01",
    "\u6574\u8f66\u5382",
    "\u4f9b\u5e94\u94fe",
    "\u653f\u7b56",
    "\u6cd5\u89c4",
    "\u5236\u9020",
    "\u53ef\u5236\u9020\u6027",
    "\u786b\u5316\u7269",
    "\u6c27\u5316\u7269",
    "yield",
    "cost curve",
    "interface",
    "manufacturing",
    "scaling",
    "oem",
    "automaker",
    "policy",
    "regulation",
]

EMPLOYMENT_HINTS = [
    "\u5c31\u4e1a",
    "\u7a0b\u5e8f\u5458",
    "\u5f00\u53d1\u8005",
    "\u521d\u7ea7",
    "\u5c97\u4f4d",
    "\u62db\u8058",
    "\u85aa\u8d44",
    "\u52b3\u52a8\u529b",
    "\u52b3\u52a8\u529b\u5e02\u573a",
    "\u4e2d\u56fd",
    "\u7f8e\u56fd",
    "\u4e2d\u7f8e",
    "entry-level",
    "developer",
    "software engineer",
    "labor market",
]

TERM_PATTERN = re.compile(r"[a-z0-9][a-z0-9\-\+\.]{1,}|[\u4e00-\u9fff]{2,}")
ASCII_TERM_PATTERN = re.compile(r"[a-z0-9][a-z0-9\-\+\.]{3,}")
GENERIC_TERMS = {
    "\u5f53\u524d",
    "\u4e3b\u8981",
    "\u54ea\u4e9b",
    "\u4ec0\u4e48",
    "\u4e3a\u4ec0\u4e48",
    "\u76f8\u5173",
    "\u95ee\u9898",
    "\u5206\u6790",
    "\u6848\u4f8b",
    "\u80cc\u666f",
    "\u60c5\u51b5",
    "\u8868\u73b0",
    "\u5efa\u8bae",
}

ANCHOR_STOPWORDS = {
    "\u4f01\u4e1a",
    "\u4e2d\u56fd",
    "\u7f8e\u56fd",
    "\u4e2d\u7f8e",
    "\u5dee\u5f02",
    "\u4e0d\u540c",
    "\u539f\u56e0",
    "\u56e0\u7d20",
    "\u673a\u5236",
    "\u8d8b\u52bf",
    "\u672a\u6765",
    "\u5173\u952e",
    "\u5206\u6790",
    "\u6848\u4f8b",
    "\u95ee\u9898",
    "\u5efa\u8bae",
    "\u80cc\u540e",
    "\u5c31\u4e1a",
    "\u5c97\u4f4d",
    "\u9700\u6c42",
    "\u7ea6\u675f",
    "china",
    "us",
    "u.s.",
    "comparison",
    "difference",
    "driver",
    "trend",
    "future",
    "reason",
    "report",
    "study",
}


def normalize_text(text: str) -> str:
    return " ".join(str(text or "").lower().split())


def extract_domain(source: str) -> str:
    source = (source or "").strip()
    if not source:
        return ""
    parsed = urlparse(source if "://" in source else f"https://{source}")
    return parsed.netloc.lower().replace("www.", "")


def contains_any(text: str, hints: list[str]) -> bool:
    normalized_text = normalize_text(text)
    return any(hint in normalized_text for hint in hints)


def count_hits(text: str, hints: list[str]) -> int:
    normalized_text = normalize_text(text)
    return sum(1 for hint in hints if hint in normalized_text)


def extract_terms(text: str) -> set[str]:
    normalized = normalize_text(text)
    terms = set()
    for token in TERM_PATTERN.findall(normalized):
        token = token.strip()
        if len(token) < 2:
            continue
        if token in GENERIC_TERMS:
            continue
        terms.add(token)
    return terms


def extract_ascii_core_terms(text: str) -> set[str]:
    normalized = normalize_text(text)
    terms = set()
    for token in ASCII_TERM_PATTERN.findall(normalized):
        token = token.strip(".-+ ")
        if len(token) < 5:
            continue
        if token in {"report", "study", "whitepaper", "survey"}:
            continue
        terms.add(token)
    return terms


def extract_anchor_terms(text: str) -> set[str]:
    anchors = set()
    for term in extract_terms(text):
        if term in ANCHOR_STOPWORDS:
            continue
        if term.isascii():
            if len(term) >= 5:
                anchors.add(term)
        else:
            if len(term) >= 3:
                anchors.add(term)
    return anchors


def count_exact_ascii_hits(text: str, terms: set[str]) -> int:
    normalized = normalize_text(text)
    hits = 0
    for term in terms:
        if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", normalized):
            hits += 1
    return hits


def infer_query_focus(query: str) -> set[str]:
    normalized_query = normalize_text(query)
    focus = set()
    if contains_any(normalized_query, COMPARISON_SIGNAL_HINTS):
        focus.add("comparison")
    if contains_any(normalized_query, DRIVER_SIGNAL_HINTS):
        focus.add("driver")
    if contains_any(normalized_query, RISK_SIGNAL_HINTS):
        focus.add("risk")
    if contains_any(normalized_query, CHANGE_SIGNAL_HINTS):
        focus.add("change")
    return focus


def has_employment_signals(text: str) -> bool:
    return contains_any(text, EMPLOYMENT_HINTS)


def is_low_quality_source(source: str) -> bool:
    domain = extract_domain(source)
    if domain in LOW_QUALITY_DOMAINS:
        return True
    return any(hint in domain for hint in LOW_QUALITY_DOMAIN_HINTS)


def is_marketing_like(result: dict) -> bool:
    combined = f"{result.get('title', '')} {result.get('snippet', '')}"
    return contains_any(combined, MARKETING_TEXT_HINTS)


def is_pdf_source(result: dict) -> bool:
    source = normalize_text(result.get("source", ""))
    title = normalize_text(result.get("title", ""))
    return source.endswith(".pdf") or ".pdf" in source or title.endswith(".pdf")


def is_primary_source_like(result: dict) -> bool:
    source = normalize_text(result.get("source", ""))
    domain = extract_domain(source)
    if any(hint in domain for hint in PRIMARY_DOMAIN_HINTS):
        return True
    if is_pdf_source(result):
        return True
    combined = f"{result.get('title', '')} {result.get('snippet', '')}"
    return count_hits(combined, RESEARCH_SIGNAL_HINTS) >= 2


def is_repost_like(result: dict) -> bool:
    combined = f"{result.get('title', '')} {result.get('snippet', '')}"
    return contains_any(combined, REPOST_TEXT_HINTS)


def is_off_topic(result: dict) -> bool:
    combined = f"{result.get('title', '')} {result.get('snippet', '')} {result.get('source', '')}"
    return contains_any(combined, OFF_TOPIC_HINTS)


def result_similarity(a: dict, b: dict) -> float:
    a_text = normalize_text(f"{a.get('title', '')} {a.get('snippet', '')}")
    b_text = normalize_text(f"{b.get('title', '')} {b.get('snippet', '')}")
    return SequenceMatcher(None, a_text, b_text).ratio()


def deduplicate_results(results: List[dict]) -> List[dict]:
    unique_results = []
    for item in results:
        title = normalize_text(item.get("title", ""))
        source = normalize_text(item.get("source", ""))
        is_duplicate = False
        for existing_item in unique_results:
            existing_title = normalize_text(existing_item.get("title", ""))
            existing_source = normalize_text(existing_item.get("source", ""))
            if title and title == existing_title and source == existing_source:
                is_duplicate = True
                break
            if result_similarity(item, existing_item) >= 0.86:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_results.append(item)
    return unique_results


def score_result(query: str, result: dict) -> int:
    query_focus = infer_query_focus(query)
    query_terms = extract_terms(query)
    ascii_core_terms = extract_ascii_core_terms(query)
    anchor_terms = extract_anchor_terms(query)
    employment_query = has_employment_signals(query)

    title = normalize_text(result.get("title", ""))
    snippet = normalize_text(result.get("snippet", ""))
    source = normalize_text(result.get("source", ""))
    domain = extract_domain(source)
    combined = f"{title} {snippet}"
    combined_terms = extract_terms(combined)

    if not title and not snippet:
        return -999
    if is_off_topic(result):
        return -999

    query_term_hits = len(query_terms & combined_terms)
    anchor_hits = len(anchor_terms & combined_terms)
    exact_ascii_hits = count_exact_ascii_hits(combined, ascii_core_terms)
    research_hits = count_hits(combined, RESEARCH_SIGNAL_HINTS)
    driver_hits = count_hits(combined, DRIVER_SIGNAL_HINTS)
    driver_context_hits = count_hits(combined, DRIVER_CONTEXT_HINTS)
    mechanism_hits = count_hits(combined, MECHANISM_SIGNAL_HINTS)
    risk_hits = count_hits(combined, RISK_SIGNAL_HINTS)
    change_hits = count_hits(combined, CHANGE_SIGNAL_HINTS)
    comparison_hits = count_hits(combined, COMPARISON_SIGNAL_HINTS)
    comparison_context_hits = count_hits(combined, COMPARISON_CONTEXT_HINTS)
    recommendation_hits = count_hits(combined, RECOMMENDATION_SIGNAL_HINTS)
    pure_trend_hits = count_hits(combined, PURE_TREND_SIGNAL_HINTS)
    employment_hits = count_hits(combined, EMPLOYMENT_HINTS)
    education_hits = count_hits(combined, EDUCATION_ADMISSIONS_HINTS)
    battery_driver_hits = count_hits(combined, BATTERY_DRIVER_HINTS)

    score = 0

    if is_low_quality_source(source):
        score -= 10
    if is_marketing_like(result):
        score -= 10
    if is_repost_like(result):
        score -= 6
    if any(hint in domain for hint in AGGREGATOR_DOMAIN_HINTS):
        score -= 2

    if len(snippet) >= 180:
        score += 4
    elif len(snippet) >= 120:
        score += 3
    elif len(snippet) >= 70:
        score += 2
    elif len(snippet) >= 40:
        score += 1
    else:
        score -= 2

    score += query_term_hits * 3
    score += anchor_hits * 4
    score += exact_ascii_hits * 5

    if ascii_core_terms and exact_ascii_hits == 0:
        score -= 6

    if query_focus:
        if query_term_hits == 0:
            score -= 4
        elif query_term_hits == 1:
            score -= 1
        if anchor_terms and anchor_hits == 0:
            score -= 4

    if title:
        score += 1
    score += research_hits * 2

    if is_primary_source_like(result):
        score += 7
    if is_pdf_source(result):
        score += 4

    if "driver" in query_focus:
        score += driver_hits * 2
        score += driver_context_hits * 3
        score += mechanism_hits * 4
        if driver_hits == 0 and mechanism_hits == 0 and driver_context_hits == 0:
            score -= 4
        if pure_trend_hits > 0 and mechanism_hits == 0 and driver_context_hits == 0:
            score -= pure_trend_hits * 4
        if query_term_hits == 0 and not is_primary_source_like(result):
            score -= 4
        if is_primary_source_like(result) and (driver_context_hits > 0 or mechanism_hits > 0):
            score += 5
        if contains_any(query, AI_AGENT_HINTS) and not contains_any(combined, AI_AGENT_HINTS):
            score -= 10
        if contains_any(query, ENTERPRISE_HINTS) and not contains_any(combined, ENTERPRISE_HINTS):
            score -= 6

    if "risk" in query_focus:
        score += risk_hits * 2
        if risk_hits == 0:
            score -= 4

    if "change" in query_focus:
        score += change_hits * 3
        if contains_any(query, BATTERY_HINTS):
            score += battery_driver_hits * 3
            score += mechanism_hits * 2
            if change_hits == 0 and battery_driver_hits == 0 and mechanism_hits == 0:
                score -= 6
        elif change_hits == 0:
            score -= 4
        if pure_trend_hits > 0 and change_hits == 0 and battery_driver_hits == 0:
            score -= 4

    if "comparison" in query_focus:
        score += comparison_hits * 2
        score += comparison_context_hits * 3
        if comparison_hits == 0 and comparison_context_hits == 0 and query_term_hits == 0:
            score -= 3
        if contains_any(query, AI_AGENT_HINTS) and not contains_any(combined, AI_AGENT_HINTS):
            score -= 10
        if employment_query and not contains_any(combined, ["中国", "美国", "中美", "china", "us", "u.s."]):
            score -= 5
        if education_hits > 0 and employment_hits == 0:
            score -= 8

    if "recommendation" in query_focus:
        score += recommendation_hits * 3
        if recommendation_hits == 0 and query_term_hits == 0:
            score -= 3

    if employment_query:
        score += employment_hits * 3
        if employment_hits == 0:
            score -= 5
        if contains_any(combined, ["\u4e2d\u56fd", "\u7f8e\u56fd", "\u4e2d\u7f8e", "china", "us", "u.s."]):
            score += 4
        if not contains_any(combined, AI_AGENT_HINTS):
            score -= 6

    if contains_any(query, BATTERY_HINTS):
        if contains_any(combined, BATTERY_HINTS):
            score += 4
        else:
            score -= 6
        if "driver" in query_focus:
            score += battery_driver_hits * 4
            if battery_driver_hits == 0 and mechanism_hits == 0 and driver_context_hits == 0:
                score -= 6
            if any(hint in domain for hint in AGGREGATOR_DOMAIN_HINTS) and battery_driver_hits == 0:
                score -= 4

    return score


def select_top_results(query: str, results: List[dict], top_k: int = 3) -> List[dict]:
    clean_candidates = []
    for item in results:
        source = item.get("source", "")
        if is_low_quality_source(source):
            continue
        if is_marketing_like(item):
            continue
        if is_off_topic(item):
            continue
        clean_candidates.append(item)

    deduped_results = deduplicate_results(clean_candidates)
    query_focus = infer_query_focus(query)
    query_terms = extract_terms(query)
    ascii_core_terms = extract_ascii_core_terms(query)
    anchor_terms = extract_anchor_terms(query)

    scored_results = []
    for item in deduped_results:
        combined = f"{item.get('title', '')} {item.get('snippet', '')}"
        combined_terms = extract_terms(combined)
        query_term_hits = len(query_terms & combined_terms)
        anchor_hits = len(anchor_terms & combined_terms)
        exact_ascii_hits = count_exact_ascii_hits(combined, ascii_core_terms)
        score = score_result(query, item)
        if score < 0:
            continue

        enriched_item = dict(item)
        enriched_item["_score"] = score
        enriched_item["_query_term_hits"] = query_term_hits
        enriched_item["_anchor_hits"] = anchor_hits
        enriched_item["_exact_ascii_hits"] = exact_ascii_hits
        enriched_item["_is_primary"] = is_primary_source_like(item)
        enriched_item["_is_pdf"] = is_pdf_source(item)
        enriched_item["_is_repost"] = is_repost_like(item)
        enriched_item["_driver_hits"] = count_hits(combined, DRIVER_SIGNAL_HINTS)
        enriched_item["_driver_context_hits"] = count_hits(combined, DRIVER_CONTEXT_HINTS)
        enriched_item["_mechanism_hits"] = count_hits(combined, MECHANISM_SIGNAL_HINTS)
        enriched_item["_risk_hits"] = count_hits(combined, RISK_SIGNAL_HINTS)
        enriched_item["_change_hits"] = count_hits(combined, CHANGE_SIGNAL_HINTS)
        enriched_item["_comparison_hits"] = count_hits(combined, COMPARISON_SIGNAL_HINTS)
        enriched_item["_comparison_context_hits"] = count_hits(combined, COMPARISON_CONTEXT_HINTS)
        enriched_item["_recommendation_hits"] = count_hits(combined, RECOMMENDATION_SIGNAL_HINTS)
        enriched_item["_employment_hits"] = count_hits(combined, EMPLOYMENT_HINTS)
        enriched_item["_education_hits"] = count_hits(combined, EDUCATION_ADMISSIONS_HINTS)
        enriched_item["_battery_driver_hits"] = count_hits(combined, BATTERY_DRIVER_HINTS)
        scored_results.append(enriched_item)

    base_scored_results = list(scored_results)

    if "driver" in query_focus and contains_any(query, AI_AGENT_HINTS):
        ai_agent_results = [
            item
            for item in scored_results
            if contains_any(f"{item.get('title', '')} {item.get('snippet', '')}", AI_AGENT_HINTS)
        ]
        if len(ai_agent_results) >= 2 or len(scored_results) <= 1:
            scored_results = ai_agent_results

    if "driver" in query_focus and contains_any(query, ENTERPRISE_HINTS):
        enterprise_results = [
            item
            for item in scored_results
            if contains_any(f"{item.get('title', '')} {item.get('snippet', '')}", ENTERPRISE_HINTS)
        ]
        if len(enterprise_results) >= 2 or len(scored_results) <= 1:
            scored_results = enterprise_results

    if contains_any(query, BATTERY_HINTS):
        battery_results = [
            item
            for item in scored_results
            if contains_any(f"{item.get('title', '')} {item.get('snippet', '')}", BATTERY_HINTS)
        ]
        if len(battery_results) >= 2 or len(scored_results) <= 1:
            scored_results = battery_results

    if "driver" in query_focus and contains_any(query, BATTERY_HINTS):
        battery_driver_results = [
            item
            for item in scored_results
            if (
                item.get("_battery_driver_hits", 0) > 0
                or item.get("_mechanism_hits", 0) > 0
                or item.get("_driver_context_hits", 0) > 0
                or (
                    item.get("_is_primary", False)
                    and item.get("_query_term_hits", 0) > 0
                )
            )
        ]
        if len(battery_driver_results) >= 2 or len(scored_results) <= 1:
            scored_results = battery_driver_results

    if "driver" in query_focus:
        driver_specific_results = [
            item
            for item in scored_results
            if (
                item.get("_mechanism_hits", 0) > 0
                or item.get("_driver_context_hits", 0) > 0
                or (
                    item.get("_is_primary", False)
                    and (
                        item.get("_driver_hits", 0) > 0
                        or item.get("_query_term_hits", 0) > 0
                    )
                )
            )
        ]
        if len(driver_specific_results) >= 2 or len(scored_results) <= 1:
            scored_results = driver_specific_results

    if "risk" in query_focus:
        risk_specific_results = [
            item
            for item in scored_results
            if item.get("_risk_hits", 0) > 0
            or (item.get("_is_primary", False) and item.get("_query_term_hits", 0) > 0)
        ]
        if len(risk_specific_results) >= 2 or len(scored_results) <= 1:
            scored_results = risk_specific_results

    if "change" in query_focus:
        change_specific_results = [
            item
            for item in scored_results
            if item.get("_change_hits", 0) > 0
            or (item.get("_is_primary", False) and item.get("_query_term_hits", 0) > 0)
        ]
        if contains_any(query, BATTERY_HINTS):
            battery_change_results = [
                item
                for item in scored_results
                if item.get("_battery_driver_hits", 0) > 0
                or item.get("_mechanism_hits", 0) > 0
                or (
                    item.get("_is_primary", False)
                    and item.get("_query_term_hits", 0) > 0
                    and contains_any(f"{item.get('title', '')} {item.get('snippet', '')}", BATTERY_HINTS)
                )
            ]
            if len(battery_change_results) >= 2 or len(scored_results) <= 1:
                change_specific_results = battery_change_results
        if len(change_specific_results) >= 2 or len(scored_results) <= 1:
            scored_results = change_specific_results

    if "comparison" in query_focus and has_employment_signals(query):
        employment_specific_results = [
            item
            for item in scored_results
            if (
                item.get("_employment_hits", 0) > 0
                or item.get("_comparison_context_hits", 0) > 0
            )
            and (
                contains_any(f"{item.get('title', '')} {item.get('snippet', '')}", ["中国", "美国", "中美", "china", "us", "u.s."])
                or item.get("_comparison_hits", 0) > 0
            )
            and item.get("_education_hits", 0) == 0
        ]
        if len(employment_specific_results) >= 2 or len(scored_results) <= 1:
            ai_employment_results = [
                item
                for item in employment_specific_results
                if contains_any(f"{item.get('title', '')} {item.get('snippet', '')}", AI_AGENT_HINTS)
            ]
            if len(ai_employment_results) >= 2 or len(employment_specific_results) <= 1:
                scored_results = ai_employment_results or employment_specific_results
            else:
                scored_results = employment_specific_results

    if "recommendation" in query_focus and len(scored_results) < 2:
        recommendation_results = [
            item
            for item in base_scored_results
            if item.get("_recommendation_hits", 0) > 0
            or item.get("_query_term_hits", 0) > 0
        ]
        if recommendation_results:
            scored_results = recommendation_results

    if len(scored_results) < 2 and len(base_scored_results) > len(scored_results):
        scored_results = base_scored_results

    scored_results.sort(
        key=lambda item: (
            item.get("_score", 0),
            item.get("_anchor_hits", 0),
            item.get("_employment_hits", 0),
            item.get("_battery_driver_hits", 0),
            item.get("_exact_ascii_hits", 0),
            item.get("_query_term_hits", 0),
            item.get("_comparison_context_hits", 0),
            item.get("_comparison_hits", 0),
            item.get("_mechanism_hits", 0),
            item.get("_driver_context_hits", 0),
            item.get("_change_hits", 0),
            item.get("_is_primary", False),
            item.get("_is_pdf", False),
            not item.get("_is_repost", False),
            len(item.get("snippet", "")),
            len(item.get("title", "")),
        ),
        reverse=True,
    )

    selected = []
    for item in scored_results[:top_k]:
        clean_item = dict(item)
        for key in [
            "_score",
            "_query_term_hits",
            "_anchor_hits",
            "_exact_ascii_hits",
            "_is_primary",
            "_is_pdf",
            "_is_repost",
            "_driver_hits",
            "_driver_context_hits",
            "_mechanism_hits",
            "_risk_hits",
            "_change_hits",
            "_comparison_hits",
            "_comparison_context_hits",
            "_recommendation_hits",
            "_employment_hits",
            "_education_hits",
            "_battery_driver_hits",
        ]:
            clean_item.pop(key, None)
        selected.append(clean_item)

    return selected
