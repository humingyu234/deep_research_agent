def rewrite_query(sub_question: str, reflection: dict, round_num: int) -> str:
    """
    根据 Reflect 的反馈，把原子问题改写成更适合搜索引擎的 query。
    """

    # 如果已经够了，就不改
    if reflection.get("status") == "enough":
        return sub_question

    suggestion = reflection.get("suggestion", "").strip()

    # 兜底：没建议时，直接补一个通用搜索方向
    if not suggestion:
        return f"{sub_question} 背景 定义 核心概念"

    # 根据子问题类型做针对性改写
    if "定义" in sub_question:
        return f"{sub_question} 定义 概念解释 基础介绍"

    if "关键概念" in sub_question:
        return f"{sub_question} 核心概念 关键术语 底层能力"

    if "应用场景" in sub_question:
        return f"{sub_question} 应用场景 行业落地 实际案例"

    if "优势" in sub_question or "局限" in sub_question:
        return f"{sub_question} 优势 局限 风险 挑战 对比分析"

    # 如果 round_num 已经大于 1，说明前面搜过了，这里再加一些更细的方向
    if round_num >= 2:
        return f"{sub_question} 详细分析 案例 解释"

    # 默认策略：从 suggestion 里提炼一些通用搜索方向
    keywords = []

    if "定义" in suggestion or "概念" in suggestion:
        keywords.extend(["定义", "概念解释"])

    if "背景" in suggestion:
        keywords.append("背景")

    if "核心" in suggestion:
        keywords.append("核心概念")

    if "案例" in suggestion or "场景" in suggestion:
        keywords.extend(["案例", "应用场景"])

    if "分析" in suggestion:
        keywords.append("分析")

    # 如果没提炼出关键词，就给个通用补充
    if not keywords:
        keywords = ["背景", "定义", "分析"]

    return f"{sub_question} {' '.join(keywords)}"