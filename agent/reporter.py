USE_LLM = False


def generate_report(query: str, summaries: dict) -> str:
    """
    Reporter 最终简化版：
    - 不再逐条复述子 summary
    - 先做子问题状态概览
    - 再输出整体综合判断
    """
    items = [(sub_question, summary) for sub_question, summary in summaries.items() if summary]

    if not items:
        return f"研究问题：{query}\n\n【整体结论】\n当前还没有足够信息形成整体报告。"

    report = f"研究问题：{query}\n\n"
    report += build_subquestion_overview(items)
    report += "\n\n"
    report += generate_overall_by_rules(query, items)
    return report


def classify_summary_focus(sub_question: str) -> str:
    normalized = (sub_question or "").lower()
    if any(token in normalized for token in ["主流可选项", "评价维度", "选择标准", "优缺点", "适用人群", "综合建议"]):
        return "recommendation"
    if "驱动" in normalized or "因素" in normalized or "为什么" in normalized or "原因" in normalized:
        return "driver"
    if "风险" in normalized or "限制" in normalized or "挑战" in normalized:
        return "risk"
    if "未来" in normalized or "变化" in normalized or "演进" in normalized:
        return "change"
    if "趋势" in normalized or "主线" in normalized or "目前" in normalized:
        return "trend"
    if "定义" in normalized or "含义" in normalized or "是什么" in normalized:
        return "definition"
    return "general"


def is_insufficient_summary(summary: str) -> bool:
    markers = [
        "当前结论仍然只能视为初步判断",
        "证据还不够扎实",
        "证据不足",
        "方向性信号",
        "仍需结合更具体的案例和研究材料继续验证",
    ]
    return any(marker in summary for marker in markers)


def extract_conclusion(summary: str) -> str:
    for raw_line in summary.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line == "支撑点：":
            continue
        if line.startswith(("1.", "2.", "3.")):
            continue
        if line.startswith("需要注意的是："):
            continue
        if line.startswith("目前不足主要在于："):
            continue
        if line.startswith("在现有材料下，可以暂时保留的方向性判断是："):
            continue
        if line.startswith("后续建议：") or line.startswith("原因："):
            continue
        return line
    return summary.strip()


def strip_question_prefix(text: str) -> str:
    stripped = (text or "").strip()
    if "当前更可靠的判断是：" in stripped:
        stripped = stripped.split("当前更可靠的判断是：", 1)[1].strip()
    elif "当前更高层的判断是：" in stripped:
        stripped = stripped.split("当前更高层的判断是：", 1)[1].strip()
    elif "当前更值得关注的不是" in stripped:
        return stripped
    elif "当前材料提示" in stripped:
        return stripped
    elif "当前结论仍然只能视为初步判断" in stripped:
        return stripped
    return stripped


def bucketize_items(items: list[tuple[str, str]]) -> dict[str, list[str]]:
    buckets = {
        "trend": [],
        "driver": [],
        "change": [],
        "risk": [],
        "definition": [],
        "recommendation": [],
        "general": [],
        "insufficient": [],
    }

    for sub_question, summary in items:
        claim = strip_question_prefix(extract_conclusion(summary))
        if is_insufficient_summary(summary):
            buckets["insufficient"].append(claim)
            continue

        focus = classify_summary_focus(sub_question)
        buckets[focus].append(claim)

    return buckets


def count_focuses(items: list[tuple[str, str]]) -> dict[str, int]:
    counts = {
        "trend": 0,
        "driver": 0,
        "change": 0,
        "risk": 0,
        "definition": 0,
        "recommendation": 0,
        "general": 0,
        "insufficient": 0,
    }
    for sub_question, summary in items:
        if is_insufficient_summary(summary):
            counts["insufficient"] += 1
        else:
            counts[classify_summary_focus(sub_question)] += 1
    return counts


def build_subquestion_overview(items: list[tuple[str, str]]) -> str:
    counts = count_focuses(items)
    total = len(items)
    lines = [
        "【子问题状态概览】",
        f"- 子问题总数：{total}",
        f"- 已形成较稳定结论：{total - counts['insufficient']}",
        f"- 仍需谨慎看待：{counts['insufficient']}",
    ]

    active_focuses = []
    for focus in ["definition", "recommendation", "trend", "driver", "change", "risk", "general"]:
        if counts[focus]:
            active_focuses.append(f"{focus}={counts[focus]}")
    if active_focuses:
        lines.append(f"- 题型分布：{', '.join(active_focuses)}")

    return "\n".join(lines)


def collect_main_lines(buckets: dict[str, list[str]]) -> list[str]:
    lines = []

    combined = " ".join(
        buckets["trend"] + buckets["change"] + buckets["driver"] + buckets["risk"] + buckets["general"]
    )

    if any(token in combined for token in ["概念验证", "企业级", "规模化", "落地", "工程化"]):
        lines.append("从概念验证走向企业级落地和规模化应用。")
    if any(token in combined for token in ["自主执行", "自动执行", "任务执行", "工作流", "协同"]):
        lines.append("从辅助工具走向更强的自主执行与工作流整合。")
    if any(token in combined for token in ["治理", "安全", "合规", "可靠性", "责任边界", "集成成本"]):
        lines.append("治理、安全、合规与可靠性正在从配角变成核心约束。")
    if any(token in combined for token in ["模型能力", "多模态", "执行力", "推理", "自主决策"]):
        lines.append("能力提升的重点正从单点演示转向更稳定的理解、推理与执行。")
    if buckets["insufficient"]:
        lines.append("驱动因素或机制解释层面的证据仍偏弱，需要继续补充一手研究材料。")

    deduped = []
    for line in lines:
        if line not in deduped:
            deduped.append(line)
    return deduped[:4]


def build_overall_judgment(query: str, buckets: dict[str, list[str]]) -> str:
    main_lines = collect_main_lines(buckets)

    if buckets["insufficient"]:
        if main_lines:
            lead = "；".join(main_lines[:2])
            return (
                f"围绕“{query}”，当前更高层的判断是：现有材料已经能支持一个方向性的研究结论，"
                f"即 {lead}；但在驱动因素或机制解释等层面，证据仍然偏弱，因此这份报告更适合作为阶段性判断，而不是已经完全坐实的定论。"
            )
        return (
            f"围绕“{query}”，当前更高层的判断是：现有材料已经能支持一个方向性的研究结论，"
            "但在关键机制解释层面，证据仍然偏弱，因此这份报告更适合作为阶段性判断，而不是已经完全坐实的定论。"
        )

    if buckets["risk"]:
        return (
            f"围绕“{query}”，当前更高层的判断是：这个主题的关键主线不是单纯“看涨”或“看强”，"
            "而是正在从概念热度转向更可落地的结构变化；与此同时，真正决定它能否进一步扩张的，不只是能力提升本身，还包括治理、可靠性、集成与成本等现实约束。"
        )

    return (
        f"围绕“{query}”，当前更高层的判断是：这个主题的发展重点已经不只是“有没有”，"
        "而是“能不能稳定落地并形成真实价值”，这意味着工程化与可持续应用会比单点能力展示更重要。"
    )


def build_trend_section(buckets: dict[str, list[str]]) -> str:
    if buckets["trend"] or buckets["change"] or buckets["general"]:
        return "从趋势层面看，研究对象正在从概念热度走向更可落地的结构变化，这说明它的发展重点已经不只是“有没有”，而是“能不能稳定落地”。"
    return "从趋势层面看，当前材料对整体方向的覆盖仍有限，但结构化落地的迹象已经开始出现。"


def build_driver_change_section(buckets: dict[str, list[str]]) -> str:
    if buckets["driver"] and buckets["change"]:
        return "从驱动与变化层面看，这一轮演进既受到技术能力提升推动，也受到业务效率与组织集成需求驱动，因此接下来更可能出现的是工作流整合和规模化部署，而不是单点能力的孤立升级。"
    if buckets["driver"]:
        return "从驱动与变化层面看，当前材料已经支持一个初步判断：这轮变化并不只是技术热度推动，还与效率需求、业务落地压力和基础设施成熟有关。"
    if buckets["change"]:
        return "从驱动与变化层面看，未来几年更值得关注的不是单点技术突破，而是从辅助工具走向更强自主执行、从试验性部署走向规模化落地这样的方向性演进。"
    return "从驱动与变化层面看，当前更像是现象层描述，真正的因果解释和机制链条还需要继续补强。"


def build_risk_section(buckets: dict[str, list[str]]) -> str:
    if buckets["risk"]:
        return "从限制与风险层面看，真正的卡点不会只来自模型本身，还会集中出现在治理、合规、可靠性、责任边界和集成成本这些现实问题上。"
    return "从限制与风险层面看，当前风险信息还不算充分，但治理、可靠性与落地成本已经开始成为不可回避的话题。"


def build_caution_text(buckets: dict[str, list[str]]) -> str:
    if buckets["insufficient"]:
        return "需要注意的是，部分子问题当前证据仍然偏弱，尤其是驱动因素、机制解释或未来演进层面的结论，还需要结合更具体的案例和一手研究材料继续验证。"
    if buckets["risk"]:
        return "需要注意的是，现有材料虽然已经能支撑总体方向判断，但不同来源仍有一定媒体转述色彩，细节结论最好继续结合一手资料验证。"
    return "需要注意的是，当前结果更适合作为相对稳定的阶段性研究判断，而不是无需再验证的绝对结论。"


def build_conclusion_nature(buckets: dict[str, list[str]]) -> tuple[str, str]:
    if buckets["insufficient"]:
        return "方向性研究判断", "已经完全坐实的最终结论"
    if buckets["risk"] and (buckets["driver"] or buckets["change"]):
        return "初步研究结论", "已经完全坐实的最终结论"
    return "相对稳定的阶段性结论", "不需要继续验证的绝对判断"


def generate_overall_by_rules(query: str, items: list[tuple[str, str]]) -> str:
    buckets = bucketize_items(items)
    overall_judgment = build_overall_judgment(query, buckets)
    caution_text = build_caution_text(buckets)
    conclusion_nature, not_nature = build_conclusion_nature(buckets)
    main_lines = collect_main_lines(buckets)

    lines = [
        "【整体结论】",
        overall_judgment,
        "",
        "具体来看：",
        f"1. {build_trend_section(buckets)}",
        f"2. {build_driver_change_section(buckets)}",
        f"3. {build_risk_section(buckets)}",
        "",
        "【当前最值得保留的主线】",
    ]

    if main_lines:
        for line in main_lines:
            lines.append(f"- {line}")
    else:
        lines.append("- 当前材料支持保留方向性判断，但主线还需要更多高质量证据来压实。")

    lines.extend(
        [
            "",
            "【需要保留的谨慎点】",
            caution_text,
            "",
            "【结论性质】",
            "这份结果当前更适合作为：",
            conclusion_nature,
            "而不是：",
            not_nature,
        ]
    )

    return "\n".join(lines)


def generate_overall_by_llm(query: str, combined_summary: str) -> str:
    try:
        import os
        from openai import OpenAI

        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )

        prompt = f"""
请基于以下研究信息，对问题进行综合分析并给出结论。
研究问题：{query}

子问题总结信息：{combined_summary}

要求：
1. 先给一个总判断。
2. 再给趋势、驱动/变化、风险三层总括。
3. 如果局部证据不足，要明确提示。
4. 不要机械复述子结论。
"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content.strip()
    except Exception as exc:
        return f"LLM 推理失败：{exc}"
