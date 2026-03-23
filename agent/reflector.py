def contains_any(text: str, keywords: list[str]) -> bool:
    """
    小工具函数：判断文本里是否出现某些关键提示词。
    """
    normalized_text = " ".join(str(text or "").lower().split())
    return any(keyword in normalized_text for keyword in keywords)


def reflect(sub_question: str, search_results: list[dict]) -> dict:
    """
    判断当前筛选后的结果，够不够支撑回答这个子问题。

    新版 Reflect 会更“严格一点”：
    不再只是看有没有结果，而是开始看这些结果像不像研究材料。
    """
    if not search_results:
        return {
            "status": "insufficient",
            "reason": "当前没有可用结果，无法支撑回答。",
            "suggestion": f'请补充搜索与“{sub_question}”直接相关的基础资料、案例或调研内容。',
        }

    valid_results = []
    for item in search_results:
        title = item.get("title", "").strip()
        snippet = item.get("snippet", "").strip()

        if title == "SEARCH_ERROR":
            continue

        if not title and not snippet:
            continue

        valid_results.append(item)

    if not valid_results:
        return {
            "status": "insufficient",
            "reason": "当前结果大多无效或不可用。",
            "suggestion": f'请重新搜索“{sub_question}”的解释、证据、案例或研究内容。',
        }

    if len(valid_results) < 2:
        return {
            "status": "insufficient",
            "reason": "当前有效结果太少，信息覆盖面还不够。",
            "suggestion": f'请补充“{sub_question}”的不同角度材料，例如报告、案例、对比分析或调查。',
        }

    avg_snippet_len = sum(len(item.get("snippet", "").strip()) for item in valid_results) / len(valid_results)
    if avg_snippet_len < 45:
        return {
            "status": "insufficient",
            "reason": "虽然有结果，但摘要普遍偏短，信息密度不够。",
            "suggestion": f'请补充“{sub_question}”的详细解释、报告摘要或更完整的案例描述。',
        }

    domains = []
    for item in valid_results:
        source = item.get("source", "").strip()
        if source:
            domains.append(source.split("/")[2] if "://" in source and len(source.split("/")) > 2 else source)

    # 来源过于单一，说明虽然看起来有几条，
    # 但可能只是同一类声音在重复说话。
    if len(set(domains)) < 2:
        return {
            "status": "insufficient",
            "reason": "当前来源多样性不足，容易只听到单一视角。",
            "suggestion": f'请补充“{sub_question}”来自不同来源的材料，尤其是报告、研究或案例型内容。',
        }

    combined_text = " ".join(
        (item.get("title", "") + " " + item.get("snippet", ""))
        for item in valid_results
    )

    # 如果看上去全是媒体稿，没有研究/报告/数据气质，
    # 对 deeper research 的帮助通常不够。
    research_signals = ["报告", "调研", "研究", "数据", "分析", "framework", "report", "study", "survey"]
    if not contains_any(combined_text, research_signals):
        return {
            "status": "insufficient",
            "reason": "当前结果更像泛媒体内容，缺少报告、研究或框架型材料。",
            "suggestion": f'请补充“{sub_question}”相关的研究报告、调研数据、方法框架或系统分析。',
        }

    # 针对子问题意图做更严格的检查。
    if "驱动" in sub_question or "因素" in sub_question:
        causal_signals = ["因为", "导致", "驱动", "推动", "原因", "factor", "driver"]
        if not contains_any(combined_text, causal_signals):
            return {
                "status": "insufficient",
                "reason": "当前结果提到了现象，但没有明显解释背后的驱动或原因。",
                "suggestion": f'请更聚焦地搜索“{sub_question}”背后的原因、驱动因素或影响机制。',
            }

    if "风险" in sub_question or "限制" in sub_question or "挑战" in sub_question:
        risk_signals = ["风险", "限制", "挑战", "问题", "不足", "risk", "limitation", "challenge"]
        if not contains_any(combined_text, risk_signals):
            return {
                "status": "insufficient",
                "reason": "当前结果还没有真正覆盖风险、限制或挑战层面的信息。",
                "suggestion": f'请补充“{sub_question}”相关的风险、问题、限制条件或失败案例。',
            }

    # 如果所有结果都只是泛泛趋势语句重复，也不该轻易 enough。
    generic_trend_signals = ["正在发展", "越来越", "持续增长", "趋势明显", "快速发展", "growing rapidly"]
    generic_signal_hits = sum(1 for keyword in generic_trend_signals if keyword in combined_text)
    if generic_signal_hits >= 3 and len(valid_results) <= 3:
        return {
            "status": "insufficient",
            "reason": "当前结果更像泛泛而谈的趋势重复，缺少更具体的支撑。",
            "suggestion": f'请补充“{sub_question}”的案例、数据、机制解释或更具体的研究材料。',
        }

    return {
        "status": "enough",
        "reason": "当前筛选后的结果已经具备基本质量、来源多样性和研究性，可以进入总结阶段。",
        "suggestion": "",
    }
