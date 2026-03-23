USE_LLM = False


def generate_report(query: str, summaries: dict) -> str:
    """
    生成最终研究报告。

    Reporter 的角色像“总编”：
    它不负责查资料，也不负责拆题，
    它负责把各个子问题的小结论收束成一个更高层的总判断。
    """
    report = f"研究问题：{query}\n\n"
    report += "【子问题分析】\n\n"

    valid_summaries = []

    for index, (sub_question, summary) in enumerate(summaries.items(), 1):
        if not summary:
            continue

        report += f"{index}. 子问题：{sub_question}\n"
        report += f"   结论：{summary}\n\n"
        valid_summaries.append(summary)

    combined_summary = " ".join(valid_summaries)

    if USE_LLM:
        overall = generate_overall_by_llm(query, combined_summary)
    else:
        overall = generate_overall_by_rules(query, valid_summaries)

    report += "【整体结论】\n"
    report += overall + "\n"
    return report


def extract_core_claim(summary: str) -> str:
    """
    从 summary 里抽第一句主结论，作为 Reporter 的原材料。
    """
    first_line = summary.splitlines()[0].strip()
    if "：" in first_line:
        return first_line.split("：", 1)[1].strip()
    return first_line


def generate_overall_by_rules(query: str, summaries: list[str]) -> str:
    """
    根据各子问题摘要，生成更高层的总体判断。

    这一层的目标不是简单拼接四个子结论，
    而是像写“研究总述”一样，说一句更上位的话。
    """
    if not summaries:
        return "当前信息还不足以形成整体结论。"

    core_claims = [extract_core_claim(summary) for summary in summaries if summary.strip()]
    if not core_claims:
        return "当前信息还不足以形成整体结论。"

    first_claim = core_claims[0].rstrip("。；;,. ")
    supporting_claims = [claim.rstrip("。；;,. ") for claim in core_claims[1:3]]
    combined = " ".join(summaries)

    report = f'综合各子问题结果，围绕“{query}”可以先形成一个更高层的判断：{first_claim}。'

    if supporting_claims:
        report += " 从支撑信息看，" + "；".join(supporting_claims) + "。"

    risk_keywords = ["限制", "风险", "争议", "差异", "挑战", "不足"]
    if any(keyword in combined for keyword in risk_keywords):
        report += " 这也说明，这个主题的关键主线并不是单纯“看涨”或“看好”，而是机会与约束正在同时变得更明显。"
    else:
        report += " 当前材料的方向相对一致，说明这个主题的主线已经开始清晰，但如果要形成更强判断，仍适合继续补充案例和数据。"

    return report


def generate_overall_by_llm(query: str, combined_summary: str) -> str:
    """
    预留的 LLM 版整体结论生成器。
    """
    try:
        import os
        from openai import OpenAI

        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )

        prompt = f"""
请基于以下研究信息，对问题进行综合分析并给出结论。

研究问题：
{query}

子问题总结信息：
{combined_summary}

要求：
1. 给出一个更高层的整体判断
2. 不要机械拼接子结论
3. 语言简洁清晰
4. 明确指出当前主题的主线、价值与限制
"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content.strip()

    except Exception as exc:
        return f"LLM 推理失败：{exc}"
