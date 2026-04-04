RESEARCH_SIGNAL_HINTS = [
    "\u62a5\u544a",
    "\u8c03\u7814",
    "\u7814\u7a76",
    "\u6570\u636e",
    "\u5206\u6790",
    "framework",
    "report",
    "study",
    "survey",
    "benchmark",
]

DRIVER_SIGNAL_HINTS = [
    "\u9a71\u52a8",
    "\u63a8\u52a8",
    "\u539f\u56e0",
    "\u56e0\u7d20",
    "\u56e0\u4e3a",
    "\u5bfc\u81f4",
    "\u673a\u5236",
    "\u9700\u6c42",
    "\u7ea6\u675f",
    "\u8f6c\u6298\u70b9",
    "factor",
    "driver",
    "cause",
    "because",
    "reason",
    "mechanism",
]

RISK_SIGNAL_HINTS = [
    "\u98ce\u9669",
    "\u9650\u5236",
    "\u6311\u6218",
    "\u4e0d\u8db3",
    "\u6cbb\u7406",
    "\u5b89\u5168",
    "\u5408\u89c4",
    "\u8d23\u4efb",
    "risk",
    "limitation",
    "challenge",
]

CHANGE_SIGNAL_HINTS = [
    "\u672a\u6765",
    "\u53d8\u5316",
    "\u6f14\u8fdb",
    "\u65b9\u5411",
    "\u8f6c\u5411",
    "\u8d8b\u52bf",
    "shift",
    "future",
    "trend",
    "next",
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
    "business model",
    "workflow integration",
    "market demand",
    "enterprise software",
    "infrastructure",
    "deployment",
    "productivity",
    "roi",
    "adoption",
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
    "driven by",
    "depends on",
    "led to",
    "enabled by",
    "mechanism",
    "tradeoff",
]

BATTERY_SIGNAL_HINTS = [
    "\u56fa\u6001\u7535\u6c60",
    "\u5168\u56fa\u6001",
    "\u7535\u89e3\u8d28",
    "\u4e2d\u8bd5\u7ebf",
    "\u91cf\u4ea7",
    "\u5546\u4e1a\u5316",
    "solid-state battery",
]

BATTERY_DRIVER_HINTS = [
    "\u826f\u7387",
    "\u6210\u672c",
    "\u6210\u672c\u66f2\u7ebf",
    "\u754c\u9762",
    "\u754c\u9762\u7a33\u5b9a",
    "\u6574\u8f66\u5382",
    "\u8f66\u4f01",
    "\u4f9b\u5e94\u94fe",
    "\u5236\u9020",
    "\u53ef\u5236\u9020\u6027",
    "\u653f\u7b56",
    "\u6cd5\u89c4",
    "\u786b\u5316\u7269",
    "\u6c27\u5316\u7269",
    "yield",
    "cost curve",
    "interface",
    "manufacturing",
    "oem",
    "automaker",
    "policy",
    "regulation",
]

DEFINITION_SIGNAL_HINTS = [
    "\u5b9a\u4e49",
    "\u542b\u4e49",
    "\u57fa\u672c\u542b\u4e49",
    "\u5de5\u4f5c\u539f\u7406",
    "\u7ec4\u6210",
    "\u673a\u5236",
    "\u533a\u522b",
]

RECOMMENDATION_SIGNAL_HINTS = [
    "\u4e3b\u6d41\u53ef\u9009\u9879",
    "\u8bc4\u4ef7\u7ef4\u5ea6",
    "\u9009\u62e9\u6807\u51c6",
    "\u4f18\u7f3a\u70b9",
    "\u9002\u7528\u4eba\u7fa4",
    "\u4f7f\u7528\u573a\u666f",
    "\u7efc\u5408\u5efa\u8bae",
    "\u9884\u7b97",
    "review",
    "comparison",
]

GENERIC_TREND_SIGNAL_HINTS = [
    "\u6b63\u5728\u53d1\u5c55",
    "\u8d8a\u6765\u8d8a",
    "\u6301\u7eed\u589e\u957f",
    "\u8d8b\u52bf\u660e\u663e",
    "\u5feb\u901f\u53d1\u5c55",
    "\u52a0\u901f\u843d\u5730",
    "\u91cd\u5851",
    "\u53d8\u9769",
    "growing rapidly",
    "hot",
    "accelerating",
    "more companies",
    "trying it",
]


def normalize_text(text: str) -> str:
    return " ".join(str(text or "").split())


def contains_any(text: str, keywords: list[str]) -> bool:
    normalized_text = normalize_text(text).lower()
    return any(keyword in normalized_text for keyword in keywords)


def count_hits(text: str, keywords: list[str]) -> int:
    normalized_text = normalize_text(text).lower()
    return sum(1 for keyword in keywords if keyword in normalized_text)


def extract_focus_text(sub_question: str) -> str:
    text = normalize_text(sub_question)
    for separator in ["\uFF1F", "?", "\u3002", "."]:
        if separator in text:
            parts = [part.strip() for part in text.split(separator) if part.strip()]
            if len(parts) >= 2:
                return parts[-1]
    return text


def infer_query_focus(sub_question: str) -> str:
    normalized_question = extract_focus_text(sub_question).lower()

    if contains_any(normalized_question, RECOMMENDATION_SIGNAL_HINTS):
        return "recommendation"
    if contains_any(normalized_question, DEFINITION_SIGNAL_HINTS):
        return "definition"
    if contains_any(normalized_question, DRIVER_SIGNAL_HINTS):
        return "driver"
    if contains_any(normalized_question, RISK_SIGNAL_HINTS):
        return "risk"
    if contains_any(normalized_question, CHANGE_SIGNAL_HINTS):
        return "change"
    if "\u8d8b\u52bf" in normalized_question or "\u4e3b\u7ebf" in normalized_question or "\u73b0\u72b6" in normalized_question:
        return "trend"
    return "general"


def has_battery_signals(text: str) -> bool:
    return contains_any(text, BATTERY_SIGNAL_HINTS)


def get_valid_results(search_results: list[dict]) -> list[dict]:
    valid_results = []
    for item in search_results:
        title = item.get("title", "").strip()
        snippet = item.get("snippet", "").strip()
        if title == "SEARCH_ERROR":
            continue
        if not title and not snippet:
            continue
        valid_results.append(item)
    return valid_results


def get_domains(results: list[dict]) -> list[str]:
    domains = []
    for item in results:
        source = item.get("source", "").strip()
        if source and "://" in source:
            parts = source.split("/")
            if len(parts) > 2:
                domains.append(parts[2])
        elif source:
            domains.append(source)
    return domains


def count_focus_matches(results: list[dict], keywords: list[str]) -> tuple[int, int]:
    matched_result_count = 0
    total_hits = 0
    for item in results:
        combined_text = normalize_text(f"{item.get('title', '')} {item.get('snippet', '')}")
        hits = count_hits(combined_text, keywords)
        if hits > 0:
            matched_result_count += 1
            total_hits += hits
    return matched_result_count, total_hits


def is_too_generic(results: list[dict]) -> bool:
    if not results:
        return True

    generic_like_count = 0
    for item in results:
        combined_text = normalize_text(f"{item.get('title', '')} {item.get('snippet', '')}")
        if count_hits(combined_text, GENERIC_TREND_SIGNAL_HINTS) >= 2:
            generic_like_count += 1

    return generic_like_count >= max(2, len(results) - 1)

def get_source_scores(results: list[dict]) -> list[int]:
    return [int(item.get("source_score", 0) or 0) for item in results]


def has_strong_evidence_pool(results: list[dict], avg_snippet_len: float, unique_domain_count: int) -> bool:
    scores = get_source_scores(results)
    high_quality_count = sum(1 for score in scores if score >= 70)
    medium_quality_count = sum(1 for score in scores if score >= 55)
    max_score = max(scores, default=0)

    if high_quality_count >= 2 and avg_snippet_len >= 55 and unique_domain_count >= 2:
        return True
    if max_score >= 85 and medium_quality_count >= 2 and avg_snippet_len >= 60 and unique_domain_count >= 2:
        return True
    return False


def has_stage_judgment_support(
    query_focus: str,
    matched_results: int,
    total_hits: int,
    context_hits: int = 0,
    mechanism_hits: int = 0,
    research_hits: int = 0,
    strong_pool: bool = False,
    battery_mechanism_support: bool = False,
) -> bool:
    if query_focus == "driver":
        return strong_pool and (
            matched_results >= 1
            or total_hits >= 2
            or (context_hits + mechanism_hits) >= 2
            or research_hits > 0
            or battery_mechanism_support
        )

    if query_focus == "risk":
        return strong_pool and (matched_results >= 1 or total_hits >= 2 or mechanism_hits >= 1)

    if query_focus == "change":
        return strong_pool and (matched_results >= 1 or total_hits >= 2 or research_hits > 0)

    return False



def build_response(status: str, reason: str, suggestion: str) -> dict:
    return {
        "status": status,
        "reason": reason,
        "suggestion": suggestion,
    }


def reflect(sub_question: str, search_results: list[dict]) -> dict:
    if not search_results:
        return build_response(
            "insufficient",
            "\u5f53\u524d\u6ca1\u6709\u53ef\u7528\u7ed3\u679c\uff0c\u65e0\u6cd5\u652f\u6491\u56de\u7b54\u3002",
            f"\u8bf7\u8865\u5145\u641c\u7d22\u4e0e\u201c{sub_question}\u201d\u76f4\u63a5\u76f8\u5173\u7684\u57fa\u7840\u8d44\u6599\u3001\u6848\u4f8b\u6216\u8c03\u7814\u5185\u5bb9\u3002",
        )

    valid_results = get_valid_results(search_results)
    if not valid_results:
        return build_response(
            "insufficient",
            "\u5f53\u524d\u7ed3\u679c\u5927\u591a\u65e0\u6548\u6216\u4e0d\u53ef\u7528\u3002",
            f"\u8bf7\u91cd\u65b0\u641c\u7d22\u201c{sub_question}\u201d\u7684\u89e3\u91ca\u3001\u8bc1\u636e\u3001\u6848\u4f8b\u6216\u7814\u7a76\u5185\u5bb9\u3002",
        )

    if len(valid_results) < 2:
        return build_response(
            "insufficient",
            "\u5f53\u524d\u6709\u6548\u7ed3\u679c\u592a\u5c11\uff0c\u4fe1\u606f\u8986\u76d6\u9762\u8fd8\u4e0d\u591f\u3002",
            f"\u8bf7\u8865\u5145\u201c{sub_question}\u201d\u7684\u4e0d\u540c\u89d2\u5ea6\u6750\u6599\uff0c\u6bd4\u5982\u62a5\u544a\u3001\u6848\u4f8b\u3001\u5bf9\u6bd4\u5206\u6790\u6216\u8c03\u67e5\u3002",
        )

    avg_snippet_len = sum(len(item.get("snippet", "").strip()) for item in valid_results) / len(valid_results)
    domains = get_domains(valid_results)
    unique_domain_count = len(set(domains))
    strong_pool = has_strong_evidence_pool(valid_results, avg_snippet_len, unique_domain_count)
    combined_text = " ".join(
        f"{item.get('title', '')} {item.get('snippet', '')}"
        for item in valid_results
    )
    research_hits = count_hits(combined_text, RESEARCH_SIGNAL_HINTS)
    query_focus = infer_query_focus(sub_question)

    if avg_snippet_len < 35:
        return build_response(
            "insufficient",
            "\u867d\u7136\u6709\u7ed3\u679c\uff0c\u4f46\u6458\u8981\u666e\u904d\u504f\u77ed\uff0c\u4fe1\u606f\u5bc6\u5ea6\u4e0d\u591f\u3002",
            f"\u8bf7\u8865\u5145\u201c{sub_question}\u201d\u7684\u8be6\u7ec6\u89e3\u91ca\u3001\u62a5\u544a\u6458\u8981\u6216\u66f4\u5b8c\u6574\u7684\u6848\u4f8b\u63cf\u8ff0\u3002",
        )

    if query_focus in {"driver", "risk", "change"} and unique_domain_count < 2:
        return build_response(
            "insufficient",
            "\u5f53\u524d\u6765\u6e90\u592a\u5355\u4e00\uff0c\u5bb9\u6613\u53ea\u542c\u5230\u4e00\u4e2a\u58f0\u97f3\u3002",
            f"\u8bf7\u8865\u5145\u201c{sub_question}\u201d\u6765\u81ea\u4e0d\u540c\u6765\u6e90\u7684\u6750\u6599\uff0c\u5c24\u5176\u662f\u62a5\u544a\u3001\u7814\u7a76\u6216\u6848\u4f8b\u578b\u5185\u5bb9\u3002",
        )

    if query_focus == "definition":
        matched_results, _ = count_focus_matches(valid_results, DEFINITION_SIGNAL_HINTS)
        if matched_results >= 1 and avg_snippet_len >= 45:
            return build_response(
                "enough",
                "\u5f53\u524d\u7ed3\u679c\u4e0d\u53ea\u662f\u76f8\u5173\uff0c\u800c\u4e14\u5df2\u7ecf\u8f83\u660e\u786e\u5730\u56de\u7b54\u4e86\u8fd9\u9053\u5b50\u95ee\u9898\uff0c\u53ef\u4ee5\u8fdb\u5165\u603b\u7ed3\u9636\u6bb5\u3002",
                "",
            )

    if query_focus == "recommendation":
        matched_results, _ = count_focus_matches(valid_results, RECOMMENDATION_SIGNAL_HINTS)
        if matched_results >= 1 and avg_snippet_len >= 45:
            return build_response(
                "enough",
                "\u5f53\u524d\u7ed3\u679c\u4e0d\u53ea\u662f\u76f8\u5173\uff0c\u800c\u4e14\u5df2\u7ecf\u8f83\u660e\u786e\u5730\u56de\u7b54\u4e86\u8fd9\u9053\u5b50\u95ee\u9898\uff0c\u53ef\u4ee5\u8fdb\u5165\u603b\u7ed3\u9636\u6bb5\u3002",
                "",
            )

    if query_focus == "driver":
        matched_results, total_hits = count_focus_matches(valid_results, DRIVER_SIGNAL_HINTS)
        _, context_hits = count_focus_matches(valid_results, DRIVER_CONTEXT_HINTS)
        _, mechanism_hits = count_focus_matches(valid_results, MECHANISM_SIGNAL_HINTS)
        _, battery_driver_hits = count_focus_matches(valid_results, BATTERY_DRIVER_HINTS)
        battery_query = has_battery_signals(sub_question)
        battery_mechanism_support = battery_query and (
            battery_driver_hits >= 2 or (battery_driver_hits + mechanism_hits + context_hits) >= 3
        )
        strong_driver_support = (
            (context_hits + mechanism_hits) >= 2
            or research_hits > 0
            or battery_mechanism_support
        )
        if has_stage_judgment_support(
            "driver",
            matched_results,
            total_hits,
            context_hits=context_hits,
            mechanism_hits=mechanism_hits,
            research_hits=research_hits,
            strong_pool=strong_pool,
            battery_mechanism_support=battery_mechanism_support,
        ):
            return build_response(
                "enough",
                "当前结果虽然不算完美，但已经具备阶段性判断所需的主要证据，可以进入总结阶段。",
                "",
            )
        if (
            (not battery_mechanism_support and matched_results < 1)
            or (not battery_mechanism_support and total_hits < 2)
            or not strong_driver_support
        ):
            return build_response(
                "insufficient",
                "\u5f53\u524d\u6750\u6599\u66f4\u591a\u662f\u5728\u63cf\u8ff0\u8d8b\u52bf\u73b0\u8c61\uff0c\u8fd8\u6ca1\u6709\u5145\u5206\u89e3\u91ca\u80cc\u540e\u7684\u9a71\u52a8\u56e0\u7d20\u6216\u4f5c\u7528\u673a\u5236\u3002",
                f"\u8bf7\u66f4\u805a\u7126\u5730\u641c\u7d22\u201c{sub_question}\u201d\u80cc\u540e\u7684\u539f\u56e0\u3001\u63a8\u52a8\u56e0\u7d20\u3001\u9700\u6c42\u53d8\u5316\u6216\u6280\u672f\u673a\u5236\u3002",
            )

    if query_focus == "risk":
        matched_results, total_hits = count_focus_matches(valid_results, RISK_SIGNAL_HINTS)
        _, mechanism_hits = count_focus_matches(valid_results, MECHANISM_SIGNAL_HINTS)
        if has_stage_judgment_support(
            "risk",
            matched_results,
            total_hits,
            mechanism_hits=mechanism_hits,
            strong_pool=strong_pool,
        ):
            return build_response(
                "enough",
                "当前结果虽然不算完美，但已经覆盖了主要风险或限制线索，可以进入阶段性总结。",
                "",
            )
        if matched_results < 1 or total_hits < 2:
            return build_response(
                "insufficient",
                "\u5f53\u524d\u6750\u6599\u4e0e\u4e3b\u9898\u76f8\u5173\uff0c\u4f46\u8fd8\u6ca1\u6709\u771f\u6b63\u628a\u4e3b\u8981\u98ce\u9669\u3001\u9650\u5236\u6216\u6cbb\u7406\u95ee\u9898\u8bb2\u6e05\u695a\u3002",
                f"\u8bf7\u8865\u5145\u201c{sub_question}\u201d\u76f8\u5173\u7684\u98ce\u9669\u7c7b\u578b\u3001\u6cbb\u7406\u96be\u70b9\u3001\u5b89\u5168\u95ee\u9898\u3001\u9650\u5236\u6761\u4ef6\u6216\u5931\u8d25\u6848\u4f8b\u3002",
            )

    if query_focus == "change":
        matched_results, total_hits = count_focus_matches(valid_results, CHANGE_SIGNAL_HINTS)
        if has_stage_judgment_support(
            "change",
            matched_results,
            total_hits,
            research_hits=research_hits,
            strong_pool=strong_pool,
        ):
            return build_response(
                "enough",
                "当前结果虽然不算完美，但已经能支持对变化方向的阶段性判断，可以进入总结阶段。",
                "",
            )
        if matched_results < 1 or total_hits < 2:
            return build_response(
                "insufficient",
                "\u5f53\u524d\u6750\u6599\u4e3b\u8981\u5728\u8bb2\u73b0\u5728\u600e\u4e48\u6837\uff0c\u8fd8\u6ca1\u6709\u628a\u672a\u6765\u51e0\u5e74\u53ef\u80fd\u51fa\u73b0\u7684\u53d8\u5316\u8bb2\u6e05\u695a\u3002",
                f"\u8bf7\u8865\u5145\u201c{sub_question}\u201d\u76f8\u5173\u7684\u672a\u6765\u6f14\u8fdb\u65b9\u5411\u3001\u9636\u6bb5\u53d8\u5316\u3001\u7ed3\u6784\u8f6c\u5411\u6216\u957f\u671f\u8d8b\u52bf\u5224\u65ad\u3002",
            )

    if query_focus in {"general", "trend", "definition", "recommendation"}:
        if avg_snippet_len >= 45 and len(valid_results) >= 2:
            return build_response(
                "enough",
                "\u5f53\u524d\u7ed3\u679c\u4e0d\u53ea\u662f\u76f8\u5173\uff0c\u800c\u4e14\u5df2\u7ecf\u8f83\u660e\u786e\u5730\u56de\u7b54\u4e86\u8fd9\u9053\u5b50\u95ee\u9898\uff0c\u53ef\u4ee5\u8fdb\u5165\u603b\u7ed3\u9636\u6bb5\u3002",
                "",
            )

    if query_focus in {"driver", "risk", "change"} and research_hits == 0 and is_too_generic(valid_results):
        return build_response(
            "insufficient",
            "\u5f53\u524d\u7ed3\u679c\u5927\u591a\u66f4\u50cf\u6cdb\u8d8b\u52bf\u8868\u8ff0\uff0c\u76f8\u5173\u4f46\u8fd8\u4e0d\u591f\u5177\u4f53\uff0c\u5bb9\u6613\u770b\u8d77\u6765\u50cf\u56de\u7b54\u4e86\uff0c\u5b9e\u9645\u4e0a\u6ca1\u6709\u771f\u6b63\u7b54\u9898\u3002",
            f"\u8bf7\u8865\u5145\u201c{sub_question}\u201d\u66f4\u5177\u4f53\u7684\u8bc1\u636e\u3001\u6848\u4f8b\u3001\u673a\u5236\u89e3\u91ca\u6216\u5206\u7c7b\u578b\u5206\u6790\u3002",
        )

    return build_response(
        "enough",
        "\u5f53\u524d\u7ed3\u679c\u4e0d\u53ea\u662f\u76f8\u5173\uff0c\u800c\u4e14\u5df2\u7ecf\u8f83\u660e\u786e\u5730\u56de\u7b54\u4e86\u8fd9\u9053\u5b50\u95ee\u9898\uff0c\u53ef\u4ee5\u8fdb\u5165\u603b\u7ed3\u9636\u6bb5\u3002",
        "",
    )
