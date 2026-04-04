import json
import os
from dataclasses import dataclass

from agent.env_loader import load_local_env
from agent.state import ResearchState


load_local_env()


QUERY_TYPES = {
    "definition",
    "timeline",
    "comparison",
    "driver",
    "preference",
    "trend",
    "howto",
    "general",
}


DEFINITION_KEYWORDS = [
    "什么是",
    "什么意思",
    "定义",
    "概念",
    "介绍一下",
]

DRIVER_KEYWORDS = [
    "为什么",
    "原因",
    "驱动",
    "驱动因素",
    "背后",
    "机制",
]

COMPARISON_KEYWORDS = [
    "对比",
    "比较",
    "差异",
    "不同",
    "区别",
    "分别",
]

TREND_KEYWORDS = [
    "趋势",
    "前景",
    "发展方向",
    "未来",
    "变化",
    "走向",
]

TIMELINE_KEYWORDS = [
    "时间线",
    "时间轴",
    "里程碑",
    "过去几年",
    "近几年",
    "近五年",
    "何时",
    "演进",
    "阶段",
]

PREFERENCE_KEYWORDS = [
    "喜欢什么样",
    "偏好",
    "更喜欢",
    "倾向于",
    "受欢迎",
    "审美",
    "哪款更值得",
    "哪个更值得",
    "最值得",
    "优先尝试",
    "优先选",
    "推荐",
    "选哪个",
    "怎么选",
    "哪款",
    "哪个好",
    "最好",
]

HOWTO_KEYWORDS = [
    "怎么",
    "如何",
    "怎样",
    "步骤",
    "方法",
    "教程",
]


@dataclass
class PlannerDecision:
    query_type: str
    sub_questions: list[str]
    source: str = "llm"
    reason: str = ""
    note: str = ""


_LAST_PLANNER_ERROR = ""


def _llm_enabled() -> bool:
    if os.getenv("PLANNER_USE_LLM", "1") == "0":
        return False
    return bool(os.getenv("DEEPSEEK_API_KEY"))


def _extract_json_block(text: str) -> dict | None:
    raw = (text or "").strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(raw[start : end + 1])
            except json.JSONDecodeError:
                return None
    return None


def _light_validate_plan(decision: PlannerDecision) -> bool:
    if decision.query_type not in QUERY_TYPES:
        return False
    if not isinstance(decision.sub_questions, list):
        return False
    if len(decision.sub_questions) < 2 or len(decision.sub_questions) > 6:
        return False
    for sq in decision.sub_questions:
        if not isinstance(sq, str) or len(sq.strip()) < 5:
            return False
    return True


def llm_plan_subquestions(query: str) -> PlannerDecision | None:
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
        prompt = f"""
You are a research planner for an advanced AI system.
Your job is to analyze the user's research question and break it down into 3-5 focused sub-questions.

Classify the query into one of these types:
- definition: asks for definition, core concepts, or key distinctions
- timeline: asks for historical progression, milestones, or stages
- comparison: asks for differences, contrasts, or cross-region comparisons
- driver: asks for causes, mechanisms, factors, or why something happens
- preference: asks for recommendations, choices, or best options
- trend: asks for future directions, outlooks, or changes
- howto: asks for steps, methods, or practical guides
- general: broad or mixed questions that don't fit the above

Return valid JSON only with this exact schema:
{{
  "query_type": "trend",
  "sub_questions": [
    "First sub-question?",
    "Second sub-question?",
    "Third sub-question?"
  ]
}}

User query:
{query}
"""
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        payload = _extract_json_block(response.choices[0].message.content or "")
        if not payload:
            return None

        decision = PlannerDecision(
            query_type=str(payload.get("query_type", "")).strip().lower() or "general",
            sub_questions=[str(sq).strip() for sq in payload.get("sub_questions", []) if str(sq).strip()],
            source="llm",
            reason="LLM structured planning generated the sub-questions.",
            note="",
        )
        if _light_validate_plan(decision):
            return decision
        return None
    except Exception as exc:
        global _LAST_PLANNER_ERROR
        _LAST_PLANNER_ERROR = str(exc)
        return None


def is_definition_like_query(normalized_query: str) -> bool:
    """识别"解释概念/说明重要性/讲清核心区别"这类定义型问法。"""
    if any(keyword in normalized_query for keyword in DEFINITION_KEYWORDS):
        return True

    definition_patterns = [
        "为什么重要",
        "核心区别",
        "区别是什么",
        "有什么区别",
        "指的是什么",
    ]
    return any(pattern in normalized_query for pattern in definition_patterns)


def is_timeline_like_query(normalized_query: str) -> bool:
    """识别带时间推进、阶段演进、里程碑脉络的问题。"""
    if any(keyword in normalized_query for keyword in TIMELINE_KEYWORDS):
        return True

    timeline_patterns = [
        "从实验室到量产",
        "从实验室走向量产",
        "从概念走向落地",
        "发展历程",
        "关键节点",
        "关键阶段",
    ]
    return any(pattern in normalized_query for pattern in timeline_patterns)


def classify_query(query: str) -> str:
    """
    先判断用户的问题属于哪一类。

    你可以把这个函数理解成"分诊台"：
    用户把问题递过来，我们先判断它更像定义题、驱动题、比较题、趋势题、偏好题、
    操作题，还是普通泛化问题。
    """
    normalized_query = " ".join(query.strip().lower().split())

    if not normalized_query:
        return "general"

    if any(keyword in normalized_query for keyword in PREFERENCE_KEYWORDS):
        return "preference"

    # 某些定义题会同时带"为什么重要""核心区别"等词，
    # 这类问题本质上仍然是在解释概念和关键差异，不应该被误打成 comparison/driver。
    if is_definition_like_query(normalized_query):
        return "definition"

    if any(keyword in normalized_query for keyword in COMPARISON_KEYWORDS):
        return "comparison"

    if any(keyword in normalized_query for keyword in DRIVER_KEYWORDS):
        return "driver"

    if any(keyword in normalized_query for keyword in HOWTO_KEYWORDS):
        return "howto"

    if is_timeline_like_query(normalized_query):
        return "timeline"

    if any(keyword in normalized_query for keyword in TREND_KEYWORDS):
        return "trend"

    return "general"


def build_subquestions(query: str, query_type: str) -> list[str]:
    """
    按问题类型生成一组适合直接搜索的子问题。

    直观理解：
    classify_query 负责"贴标签"，
    build_subquestions 负责"按标签出题"。
    """
    cleaned_query = query.strip()

    if not cleaned_query:
        return []

    if query_type == "definition":
        return [
            f"{cleaned_query} 的定义是什么？",
            f"{cleaned_query} 的工作原理或核心特征有哪些？",
            f"{cleaned_query} 通常适用于哪些应用场景？",
            f"{cleaned_query} 容易和哪些概念混淆，核心区别是什么？",
        ]

    if query_type == "driver":
        return [
            f"推动 {cleaned_query} 的主要驱动因素有哪些？",
            f"这些驱动因素分别通过什么机制或因果链条起作用？",
            f"哪些现实案例、行业变化或组织动作已经体现出这些驱动因素？",
            f"{cleaned_query} 当前仍面临哪些约束、阻力或反向因素？",
        ]

    if query_type == "comparison":
        return [
            f"{cleaned_query} 的比较对象分别是谁，最核心的差异主要体现在哪些维度？",
            f"{cleaned_query} 在不同对象上分别有哪些具体表现或数据差异？",
            f"造成这些差异的主要结构性原因或驱动因素有哪些？",
            f"面对这些差异，不同对象应采取哪些对应的应对路径或策略？",
        ]

    if query_type == "trend":
        return [
            f"{cleaned_query} 目前的发展趋势是什么？",
            f"{cleaned_query} 背后的主要驱动因素有哪些？",
            f"{cleaned_query} 未来几年可能出现哪些变化？",
            f"{cleaned_query} 当前面临的主要限制或风险是什么？",
        ]

    if query_type == "timeline":
        return [
            f"{cleaned_query} 过去几年经历了哪些关键时间节点、阶段或里程碑？",
            f"{cleaned_query} 每个关键阶段分别出现了哪些代表性技术突破、产业动作或事件？",
            f"{cleaned_query} 哪些转折点最重要，它们背后的驱动因素或瓶颈变化是什么？",
            f"{cleaned_query} 按当前节奏，接下来最值得关注的演进方向、下一阶段门槛或落地条件是什么？",
        ]

    if query_type == "preference":
        return [
            f"{cleaned_query} 当前有哪些主流可选项，分别最适合什么目标或使用场景？",
            f"判断 {cleaned_query} 时，最关键的评价维度或选择标准有哪些？",
            f"{cleaned_query} 里几类代表性选项各自的优缺点、限制和适用人群有什么不同？",
            f"如果目标明确且时间有限，{cleaned_query} 最值得优先尝试的综合建议是什么？",
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
    2. 先尝试 LLM 结构化规划
    3. LLM 失败时回退到规则模板
    4. 把结果写回 state
    """
    query = state.query

    if _llm_enabled():
        llm_decision = llm_plan_subquestions(query)
        if llm_decision is not None:
            state.planner_type = llm_decision.query_type
            state.planner_source = llm_decision.source
            state.planner_reason = llm_decision.reason
            state.planner_note = llm_decision.note
            state.sub_questions = llm_decision.sub_questions
            return state

    query_type = classify_query(query)
    state.planner_type = query_type
    state.planner_source = "rule"
    state.planner_reason = f"Rule-based planner classified the query as {query_type}."
    if _LAST_PLANNER_ERROR:
        state.planner_note = f"LLM fallback: {_LAST_PLANNER_ERROR}"
    else:
        state.planner_note = ""
    state.sub_questions = build_subquestions(query, query_type)
    return state
