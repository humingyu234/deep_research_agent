import hashlib
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from ddgs import DDGS

from agent.env_loader import load_local_env


load_local_env()


SEARCH_MODE = "real"
SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "auto").strip().lower()
DDGS_TIMEOUT_SECONDS = 8
TAVILY_TIMEOUT_SECONDS = 12
TAVILY_SEARCH_DEPTH = os.getenv("TAVILY_SEARCH_DEPTH", "advanced").strip().lower() or "advanced"
TAVILY_TOPIC = os.getenv("TAVILY_TOPIC", "general").strip().lower() or "general"
SEARCH_RETRIES = 2
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SEARCH_CACHE_DIR = PROJECT_ROOT / ".cache" / "search"
SEARCH_CACHE_VERSION = "v3"
SEARCH_CACHE_ENABLED = os.getenv("SEARCH_CACHE_ENABLED", "1") != "0"
SEARCH_CACHE_REFRESH = os.getenv("SEARCH_CACHE_REFRESH", "0") == "1"
SIMILAR_CACHE_SCAN_LIMIT = 200
SEARCH_STALE_MIN_OVERLAP = 0.8
SIMILAR_CACHE_MIN_TOKEN_OVERLAP = 0.75

EXPANSION_HINT_TOKENS = {
    "原因",
    "驱动因素",
    "作用机制",
    "约束",
    "机制",
    "激励",
    "案例",
    "调查",
    "调研",
    "对比",
    "比较",
    "推荐",
    "评测",
    "优缺点",
    "适用人群",
    "预算",
    "使用场景",
    "选择标准",
    "时间线",
    "里程碑",
    "关键节点",
    "阶段",
    "转折点",
    "未来演进",
    "变化方向",
    "长期趋势",
    "结构转向",
    "商业化",
    "产业化",
    "benchmark",
    "case",
    "study",
    "adoption",
    "roi",
    "workflow",
    "integration",
    "governance",
    "cost",
    "review",
    "rank",
    "comparison",
    "report",
}

HIGH_TRUST_DOMAIN_PATTERNS = (
    ".gov",
    ".edu",
    ".ac.",
    "gov.cn",
    "moe.gov.cn",
    "miit.gov.cn",
    "ndrc.gov.cn",
    "stats.gov.cn",
    "nsfc.gov.cn",
    "cctv.com",
    "news.cn",
    "xinhuanet.com",
    "people.com.cn",
    "paper.people.com.cn",
    "thepaper.cn",
    "infoq.cn",
    "ccf.org.cn",
    "csia.org.cn",
    "oecd.org",
    "weforum.org",
    "mckinsey.com",
    "deloitte.com",
    "pwc.com",
    "kpmg.com",
    "accenture.com",
    "gartner.com",
    "cbinsights.com",
    "stanford.edu",
    "mit.edu",
    "harvard.edu",
    "nature.com",
    "science.org",
    "arxiv.org",
    "reuters.com",
    "bloomberg.com",
    "ft.com",
    "wsj.com",
    "economist.com",
    "wired.com",
    "bbc.com",
    "nytimes.com",
    "huawei.com",
    "e.huawei.com",
)

MEDIUM_TRUST_DOMAIN_PATTERNS = (
    "36kr.com",
    "163.com",
    "sohu.com",
    "qq.com",
    "news.qq.com",
    "sina.com.cn",
    "aliyun.com",
    "cloud.tencent.com",
    "tencent.com",
    "baidu.com",
    "baike.baidu.com",
    "chinadaily.com.cn",
    "qstheory.cn",
    "ifc.org",
    "stcn.com",
    "pdf.dfcfw.com",
)

LOW_TRUST_DOMAIN_PATTERNS = (
    "wikipedia.org",
    "zhihu.com",
    "csdn.net",
    "segmentfault.com",
    "53ai.com",
    "aibook.ren",
    "nowcoder.com",
    "xueqiu.com",
    "blog.",
    "wordpress.org",
)

BLOCKED_DOMAIN_PATTERNS = (
    "kimi.com",
    "gemini.google.com",
    "ttdm",
    "bbj75.com",
    "hrefgo.com",
)

TITLE_BAD_PATTERNS = (
    "广告",
    "下载",
    "安装",
    "在线看",
    "教程",
    "源码",
    "GitHub",
)

SNIPPET_BAD_PATTERNS = (
    "open-source model for visual coding",
    "download",
    "install",
    "试看",
    "H动画",
)


def clean_text(text: str, max_len: int = 300) -> str:
    if not text:
        return ""
    return " ".join(str(text).split())[:max_len]


def normalize_query_text(query: str) -> str:
    normalized = " ".join(str(query).split())
    return normalized.strip()


def normalize_query_for_match(query: str) -> str:
    normalized = normalize_query_text(query).lower()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def tokenize_for_overlap(text: str) -> set[str]:
    normalized = normalize_query_for_match(text)
    if not normalized:
        return set()
    return {token for token in re.split(r"[^a-z0-9\u4e00-\u9fff]+", normalized) if len(token) >= 2}


def token_overlap_ratio(left: str, right: str) -> float:
    left_tokens = tokenize_for_overlap(left)
    right_tokens = tokenize_for_overlap(right)
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = left_tokens & right_tokens
    smaller = min(len(left_tokens), len(right_tokens))
    if smaller == 0:
        return 0.0
    return len(intersection) / smaller


def extract_domain(source: str) -> str:
    if not source:
        return ""
    try:
        parsed = urlparse(source)
        domain = parsed.netloc.lower().strip()
    except Exception:
        return ""
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def classify_domain(domain: str) -> str:
    if not domain:
        return "unknown"
    if any(pattern in domain for pattern in BLOCKED_DOMAIN_PATTERNS):
        return "blocked"
    if any(pattern in domain for pattern in HIGH_TRUST_DOMAIN_PATTERNS):
        return "high"
    if any(pattern in domain for pattern in MEDIUM_TRUST_DOMAIN_PATTERNS):
        return "medium"
    if any(pattern in domain for pattern in LOW_TRUST_DOMAIN_PATTERNS):
        return "low"
    return "unknown"


def score_result(item: dict) -> int:
    title = (item.get("title") or "").lower()
    snippet = (item.get("snippet") or "").lower()
    domain = extract_domain(item.get("source", ""))
    trust = classify_domain(domain)

    base_scores = {
        "high": 100,
        "medium": 65,
        "unknown": 40,
        "low": 10,
        "blocked": -100,
    }
    score = base_scores.get(trust, 0)

    if any(pattern.lower() in title for pattern in TITLE_BAD_PATTERNS):
        score -= 30
    if any(pattern.lower() in snippet for pattern in SNIPPET_BAD_PATTERNS):
        score -= 30

    if title and snippet:
        score += 5
    if any(keyword in title for keyword in ("报告", "研究", "白皮书", "forecast", "outlook", "survey")):
        score += 10
    if any(keyword in snippet for keyword in ("报告", "调研", "研究", "survey", "outlook", "benchmark")):
        score += 8

    return score


def enrich_result(item: dict) -> dict:
    enriched = dict(item)
    domain = extract_domain(item.get("source", ""))
    enriched["domain"] = domain
    enriched["domain_trust"] = classify_domain(domain)
    enriched["source_score"] = score_result(item)
    return enriched


def filter_and_rank_results(results: list[dict]) -> list[dict]:
    ranked: list[dict] = []
    seen_domains: dict[str, int] = {}
    seen_titles: set[str] = set()

    for raw in results:
        enriched = enrich_result(raw)
        if enriched["source_score"] < 0:
            continue

        title_key = normalize_query_for_match(enriched.get("title", ""))
        if title_key and title_key in seen_titles:
            continue

        domain = enriched.get("domain") or ""
        if domain:
            seen_domains[domain] = seen_domains.get(domain, 0) + 1
            if seen_domains[domain] > 2 and enriched["domain_trust"] in {"low", "unknown"}:
                continue

        if title_key:
            seen_titles.add(title_key)
        ranked.append(enriched)

    ranked.sort(key=lambda item: item.get("source_score", 0), reverse=True)
    return ranked


def titles_overlap_ratio(left_results: list[dict], right_results: list[dict]) -> float:
    left_titles = {normalize_query_for_match(item.get("title", "")) for item in left_results if item.get("title")}
    right_titles = {normalize_query_for_match(item.get("title", "")) for item in right_results if item.get("title")}
    left_titles.discard("")
    right_titles.discard("")
    if not left_titles or not right_titles:
        return 0.0
    overlap = left_titles & right_titles
    return len(overlap) / min(len(left_titles), len(right_titles))


def build_search_cache_key(query: str, max_results: int) -> str:
    normalized_query = normalize_query_text(query)
    payload = f"{SEARCH_CACHE_VERSION}|{max_results}|{normalized_query}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def get_search_cache_path(query: str, max_results: int) -> Path:
    return SEARCH_CACHE_DIR / f"{build_search_cache_key(query, max_results)}.json"


def load_cache_payload(cache_path: Path) -> dict | None:
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def normalize_cached_results(results: list[dict]) -> list[dict]:
    if not isinstance(results, list) or not results:
        return []
    normalized = []
    for item in results:
        if not isinstance(item, dict):
            continue
        normalized.append({
            "title": clean_text(item.get("title", ""), max_len=120),
            "snippet": clean_text(item.get("snippet", ""), max_len=300),
            "source": item.get("source") or item.get("url", ""),
        })
    return filter_and_rank_results(normalized)


def load_cached_search_results(query: str, max_results: int) -> list[dict] | None:
    if not SEARCH_CACHE_ENABLED or SEARCH_CACHE_REFRESH:
        return None

    cache_path = get_search_cache_path(query, max_results)
    if not cache_path.exists():
        return None

    payload = load_cache_payload(cache_path)
    if not payload:
        return None

    results = normalize_cached_results(payload.get("results"))
    if not results:
        return None
    return results


def load_similar_cached_results(candidates: list[str], max_results: int, round_num: int = 1) -> list[dict] | None:
    if not SEARCH_CACHE_ENABLED or SEARCH_CACHE_REFRESH or not SEARCH_CACHE_DIR.exists():
        return None
    if round_num > 1:
        return None

    normalized_candidates = [normalize_query_for_match(candidate) for candidate in candidates if candidate]
    normalized_candidates = [candidate for candidate in normalized_candidates if candidate]
    if not normalized_candidates:
        return None

    scanned = 0
    best_match: list[dict] | None = None
    best_overlap = 0.0

    for cache_path in SEARCH_CACHE_DIR.glob("*.json"):
        scanned += 1
        if scanned > SIMILAR_CACHE_SCAN_LIMIT:
            break

        payload = load_cache_payload(cache_path)
        if not payload:
            continue

        if payload.get("max_results") != max_results:
            continue

        cached_query = payload.get("normalized_query") or payload.get("query")
        normalized_cached_query = normalize_query_for_match(cached_query or "")
        if not normalized_cached_query:
            continue

        candidate_overlap = max(
            token_overlap_ratio(candidate, normalized_cached_query)
            for candidate in normalized_candidates
        )
        if candidate_overlap < SIMILAR_CACHE_MIN_TOKEN_OVERLAP:
            continue

        results = normalize_cached_results(payload.get("results"))
        if not results:
            continue

        if candidate_overlap > best_overlap:
            best_overlap = candidate_overlap
            best_match = results

    return best_match


def save_search_cache(query: str, max_results: int, results: list[dict]) -> None:
    if not SEARCH_CACHE_ENABLED or not results:
        return

    normalized_query = normalize_query_text(query)
    SEARCH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = get_search_cache_path(normalized_query, max_results)
    payload = {
        "version": SEARCH_CACHE_VERSION,
        "query": normalized_query,
        "normalized_query": normalize_query_for_match(normalized_query),
        "max_results": max_results,
        "cached_at": int(time.time()),
        "results": results,
    }
    cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def mock_search(query: str, round_num: int = 1) -> list[dict]:
    suffix = "初步结果" if round_num == 1 else "补充结果"
    return [
        {
            "title": f"{query} - {suffix}",
            "snippet": f"这是关于“{query}”的模拟搜索结果，用于本地快速验证。",
            "source": f"mock_source_round_{round_num}",
            "domain": f"mock_source_round_{round_num}",
            "domain_trust": "high",
            "source_score": 999,
        }
    ]


def _provider_order() -> list[str]:
    if SEARCH_PROVIDER == "tavily":
        return ["tavily", "ddgs"]
    if SEARCH_PROVIDER == "ddgs":
        return ["ddgs"]
    return ["tavily", "ddgs"] if TAVILY_API_KEY else ["ddgs"]


def _search_once_ddgs(query: str, max_results: int) -> list[dict]:
    results = []

    with DDGS(timeout=DDGS_TIMEOUT_SECONDS) as ddgs:
        for item in ddgs.text(query, max_results=max_results):
            title = clean_text(item.get("title", ""), max_len=120)
            snippet = clean_text(item.get("body", ""), max_len=300)
            source = item.get("href", "")

            if not title and not snippet:
                continue

            results.append(
                {
                    "title": title,
                    "snippet": snippet,
                    "source": source,
                }
            )

    return filter_and_rank_results(results)


def _search_once_tavily(query: str, max_results: int) -> list[dict]:
    if not TAVILY_API_KEY:
        raise RuntimeError("Tavily API key is not configured")

    payload = json.dumps(
        {
            "query": query,
            "max_results": max_results,
            "search_depth": TAVILY_SEARCH_DEPTH,
            "topic": TAVILY_TOPIC,
            "include_raw_content": False,
            "include_answer": False,
        }
    ).encode("utf-8")

    request = Request(
        "https://api.tavily.com/search",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TAVILY_API_KEY}",
        },
        method="POST",
    )

    with urlopen(request, timeout=TAVILY_TIMEOUT_SECONDS) as response:
        data = json.loads(response.read().decode("utf-8"))

    results = []
    for item in data.get("results", []):
        title = clean_text(item.get("title", ""), max_len=120)
        snippet = clean_text(item.get("content", "") or item.get("raw_content", ""), max_len=300)
        source = item.get("url", "")

        if not title and not snippet:
            continue

        results.append(
            {
                "title": title,
                "snippet": snippet,
                "source": source,
            }
        )

    return filter_and_rank_results(results)


def _search_once(query: str, max_results: int) -> list[dict]:
    last_error = None

    for provider in _provider_order():
        try:
            if provider == "tavily":
                return _search_once_tavily(query, max_results=max_results)
            if provider == "ddgs":
                return _search_once_ddgs(query, max_results=max_results)
        except Exception as exc:
            last_error = exc
            continue

    raise RuntimeError(f"All search providers failed: {last_error}")


def dedupe_keep_order(items: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def strip_trailing_hint_tokens(query: str) -> str:
    tokens = normalize_query_text(query).split()
    if len(tokens) <= 8:
        return query

    trimmed = list(tokens)
    removed = False
    while len(trimmed) > 8:
        token = trimmed[-1].strip().lower()
        if token in EXPANSION_HINT_TOKENS or len(trimmed) > 12:
            trimmed.pop()
            removed = True
            continue
        break

    if not removed:
        return query
    return " ".join(trimmed)


def first_sentence_prefix(query: str) -> str:
    normalized = normalize_query_text(query)
    if not normalized:
        return normalized

    parts = re.split(r"(?<=[。！？?!])\s*", normalized)
    if not parts:
        return normalized

    first = parts[0].strip()
    return first or normalized


def build_prefix_variants(query: str) -> list[str]:
    tokens = normalize_query_text(query).split()
    if len(tokens) <= 8:
        return []

    variants = []
    for target_len in (12, 10, 8):
        if len(tokens) > target_len:
            variants.append(" ".join(tokens[:target_len]))
    return variants


def build_search_candidates(query: str) -> list[str]:
    normalized = normalize_query_text(query)
    candidates = [normalized]

    stripped = strip_trailing_hint_tokens(normalized)
    candidates.append(stripped)
    candidates.append(first_sentence_prefix(stripped))
    candidates.extend(build_prefix_variants(stripped))
    candidates.append(first_sentence_prefix(normalized))

    return [candidate for candidate in dedupe_keep_order(candidates) if len(candidate) >= 6]


def weak_result_pool(results: list[dict]) -> bool:
    if not results:
        return True
    top_scores = [item.get("source_score", 0) for item in results[:3]]
    return max(top_scores, default=0) < 55


def real_search(
    query: str,
    round_num: int = 1,
    max_results: int = 5,
    retries: int = SEARCH_RETRIES,
) -> list[dict]:
    candidates = build_search_candidates(query)
    if not candidates:
        candidates = [normalize_query_text(query)]

    for candidate in candidates:
        cached_results = load_cached_search_results(candidate, max_results)
        if cached_results is not None:
            if candidate != normalize_query_text(query):
                save_search_cache(query, max_results, cached_results)
            return cached_results

    fallback_cached = load_similar_cached_results(candidates, max_results, round_num=round_num)
    if fallback_cached is not None:
        save_search_cache(query, max_results, fallback_cached)
        return fallback_cached

    last_error = None
    previous_results = load_cached_search_results(query, max_results) if round_num > 1 else None

    for candidate in candidates:
        for attempt in range(1, retries + 1):
            try:
                results = _search_once(candidate, max_results=max_results)
                if results:
                    if previous_results and titles_overlap_ratio(previous_results, results) >= SEARCH_STALE_MIN_OVERLAP and weak_result_pool(results):
                        return [
                            {
                                "title": "SEARCH_STALE_RESULTS",
                                "snippet": "搜索结果连续两轮高度相似，且候选池质量偏弱，已停止继续空转。",
                                "source": "system_notice",
                                "domain": "system_notice",
                                "domain_trust": "high",
                                "source_score": 999,
                            }
                        ]

                    save_search_cache(candidate, max_results, results)
                    if candidate != normalize_query_text(query):
                        save_search_cache(query, max_results, results)
                    return results
                last_error = RuntimeError("搜索返回为空")
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                last_error = exc

            if attempt < retries:
                time.sleep(1)

    if round_num == 1:
        fallback_cached = load_similar_cached_results(candidates, max_results, round_num=round_num)
        if fallback_cached is not None:
            save_search_cache(query, max_results, fallback_cached)
            return fallback_cached

    return [
        {
            "title": "SEARCH_ERROR",
            "snippet": f"真实搜索失败：{last_error}",
            "source": "system_error",
            "domain": "system_error",
            "domain_trust": "high",
            "source_score": 999,
        }
    ]


def search(query: str, round_num: int = 1) -> list[dict]:
    if SEARCH_MODE == "mock":
        return mock_search(query, round_num)

    if SEARCH_MODE == "real":
        return real_search(query, round_num)

    raise ValueError(f"不支持的 SEARCH_MODE: {SEARCH_MODE}")


if __name__ == "__main__":
    test_query = "AI teacher definition"
    results = search(test_query)

    print(f"SEARCH_MODE: {SEARCH_MODE}")
    print(f"查询词: {test_query}")
    print(f"结果数量: {len(results)}")
    print("-" * 60)

    for index, item in enumerate(results, 1):
        print(f"结果 {index}")
        print("标题:", item["title"])
        print("摘要:", item["snippet"])
        print("来源:", item["source"])
        print("域名:", item.get("domain", ""))
        print("信任等级:", item.get("domain_trust", ""))
        print("得分:", item.get("source_score", ""))
        print("-" * 60)
