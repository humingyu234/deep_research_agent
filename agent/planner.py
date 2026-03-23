from typing import List

from agent.state import ResearchState


# 这几组关键词像“问题分类提示卡”。
# classify_query 会先看 query 里有没有这些词，
# 再决定这个问题更像哪一类研究任务。
DEFINITION_KEYWORDS = [
    "是什么",
    "什么意思",
    "定义",
    "概念",
    "介绍一下",
]

TREND_KEYWORDS = [
    "趋势",
    "前景",
    "发展方向",
    "未来",
    "变化",
    "走向",
]

PREFERENCE_KEYWORDS = [
    "喜欢什么样",
    "偏好",
    "更喜欢",
    "倾向于",
    "受欢迎",
    "审美",
]

HOWTO_KEYWORDS = [
    "怎么",
    "如何",
    "怎样",
    "步骤",
    "方法",
    "教程",
]


def classify_query(query: str) -> str:
    """
    先判断用户的问题属于哪一类。

    你可以把这个函数理解成“分诊台”：
    用户把问题递过来，我们先判断它更像定义题、趋势题、偏好题、
    操作题，还是普通泛化问题。
    """
    # 先把输入清洗一下，避免空格和大小写干扰判断。
    normalized_query = " ".join(query.strip().lower().split())

    if not normalized_query:
        return "general"

    # 判断顺序也有讲究：
    # 比如“喜欢什么样”这类偏好问题，如果不优先判断，
    # 很容易被更泛的规则误吞掉。
    if any(keyword in normalized_query for keyword in PREFERENCE_KEYWORDS):
        return "preference"

    if any(keyword in normalized_query for keyword in HOWTO_KEYWORDS):
        return "howto"

    if any(keyword in normalized_query for keyword in TREND_KEYWORDS):
        return "trend"

    if any(keyword in normalized_query for keyword in DEFINITION_KEYWORDS):
        return "definition"

    return "general"


def build_subquestions(query: str, query_type: str) -> List[str]:
    """
    按问题类型生成一组适合直接搜索的子问题。

    直观理解：
    classify_query 负责“贴标签”，
    build_subquestions 负责“按标签出题”。
    """
    cleaned_query = query.strip()

    if not cleaned_query:
        return []

    if query_type == "definition":
        return [
            f"{cleaned_query} 的定义是什么？",
            f"{cleaned_query} 的核心特征有哪些？",
            f"{cleaned_query} 通常适用于哪些场景？",
            f"{cleaned_query} 容易和哪些概念混淆？",
        ]

    if query_type == "trend":
        return [
            f"{cleaned_query} 目前的发展趋势是什么？",
            f"{cleaned_query} 背后的主要驱动因素有哪些？",
            f"{cleaned_query} 未来几年可能出现哪些变化？",
            f"{cleaned_query} 当前面临的主要限制或风险是什么？",
        ]

    if query_type == "preference":
        return [
            f"{cleaned_query} 的常见偏好结论是什么？",
            f"{cleaned_query} 这种偏好背后的主要影响因素有哪些？",
            f"{cleaned_query} 在不同人群或情境下是否存在差异？",
            f"{cleaned_query} 有没有相关调查、研究或案例支持？",
        ]

    if query_type == "howto":
        return [
            f"{cleaned_query} 的具体步骤是什么？",
            f"{cleaned_query} 需要满足哪些前提条件或准备工作？",
            f"{cleaned_query} 过程中常见的问题和解决方法有哪些？",
            f"{cleaned_query} 有没有可参考的实践建议或案例？",
        ]

    # general 是兜底类型。
    # 当系统看不清用户到底想问哪一类时，
    # 就先从背景、关键点、案例、争议这几个通用角度切进去。
    return [
        f"{cleaned_query} 的背景和基本情况是什么？",
        f"{cleaned_query} 涉及哪些关键要点？",
        f"{cleaned_query} 常见的应用、表现或案例有哪些？",
        f"{cleaned_query} 当前有哪些主要争议、限制或注意事项？",
    ]


def plan_subquestions(state: ResearchState) -> ResearchState:
    """
    Planner 对外的主入口。

    这个函数像一个小调度员：
    1. 从 state 里取出原始问题
    2. 先分类
    3. 再生成子问题
    4. 把结果写回 state
    """
    query = state.query
    query_type = classify_query(query)

    state.sub_questions = build_subquestions(query, query_type)
    return state
