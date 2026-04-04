import json
import os
from dataclasses import dataclass

from agent.env_loader import load_local_env


load_local_env()


MAX_QUESTIONS = 3

PREFERENCE_HINTS = [
    "最好的",
    "推荐",
    "哪个好",
    "哪个更好",
    "哪个最适合",
    "软件",
    "app",
    "工具",
]

COMPARISON_HINTS = [
    "分别",
    "对比",
    "比较",
    "差异",
    "中美",
    "美国",
    "中国",
    "vs",
]

OPEN_ENDED_HINTS = [
    "怎么",
    "怎么样",
    "怎么做",
    "怎么办",
    "如何",
    "影响",
    "趋势",
    "策略",
]

PERSONAL_STRATEGY_HINTS = [
    "财富自由",
    "财务独立",
    "财务自由",
    "赚钱",
    "失败",
    "人生",
    "职业",
    "成长",
    "阶段",
    "选择",
    "方向",
    "该不该",
    "要不要",
    "应该",
    "在意什么",
    "面对失败",
]


@dataclass
class ClarificationResult:
    should_clarify: bool
    reason: str
    questions: list[str]
    source: str = "rule"
    note: str = ""


def _contains_any(text: str, keywords: list[str]) -> bool:
    normalized = (text or "").lower()
    return any(keyword.lower() in normalized for keyword in keywords)


def _normalize_questions(questions: list[str]) -> list[str]:
    normalized = []
    for question in questions:
        cleaned = (question or "").strip()
        if cleaned and cleaned not in normalized:
            normalized.append(cleaned)
    return normalized[:MAX_QUESTIONS]


def _rule_based_should_clarify(query: str) -> ClarificationResult:
    normalized = (query or "").strip()
    if not normalized:
        return ClarificationResult(False, "empty_query", [], "rule", "")

    if _contains_any(normalized, PREFERENCE_HINTS):
        return ClarificationResult(
            True,
            "preference_query",
            [
                "你更看重哪类目标：效果、效率、价格，还是长期可持续使用？",
                "你希望优先考虑免费方案、低预算方案，还是愿意为更强效果付费？",
                "你更想要大众通用推荐，还是更贴合你自己场景的建议？",
            ][:MAX_QUESTIONS],
            "rule",
            "",
        )

    if _contains_any(normalized, COMPARISON_HINTS) and _contains_any(normalized, OPEN_ENDED_HINTS):
        return ClarificationResult(
            True,
            "complex_comparison",
            [
                "你更关心哪类差异：岗位需求、技能门槛、薪资变化，还是政策与行业结构？",
                "你更想看短期影响，还是未来 2 到 3 年的趋势？",
                "最终你更需要比较结论，还是更可执行的应对建议？",
            ][:MAX_QUESTIONS],
            "rule",
            "",
        )

    if _contains_any(normalized, PERSONAL_STRATEGY_HINTS):
        return ClarificationResult(
            True,
            "broad_open_ended",
            [
                "你这次更想要哪类输出：行动建议、阶段重点，还是心态与风险提醒？",
                "你更关心职业发展、赚钱路径、资产积累，还是长期生活方式选择？",
                "你希望答案更偏普遍原则，还是更贴近你当下个人阶段的建议？",
            ][:MAX_QUESTIONS],
            "rule",
            "",
        )

    if _contains_any(normalized, OPEN_ENDED_HINTS) and len(normalized) <= 30:
        return ClarificationResult(
            True,
            "broad_open_ended",
            [
                "你这次更想要哪类输出：行动建议、阶段重点，还是心态与风险提醒？",
                "你更关心职业发展、赚钱路径、资产积累，还是长期生活方式选择？",
                "你希望答案更偏普遍原则，还是更贴近你当下个人阶段的建议？",
            ][:MAX_QUESTIONS],
            "rule",
            "",
        )

    return ClarificationResult(False, "specific_enough", [], "rule", "")


def _llm_enabled() -> bool:
    if os.getenv("CLARIFIER_USE_LLM", "1") == "0":
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


def _llm_should_clarify(query: str) -> ClarificationResult | None:
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )

        prompt = f"""
你是一个研究型 assistant 的前置 Clarifier。
请判断下面这个用户问题在正式进入研究链路前，是否需要先澄清边界。

用户问题：
{query}

请只输出 JSON，对应字段如下：
{{
  "should_clarify": true or false,
  "reason": "one_of: preference_query | complex_comparison | broad_open_ended | specific_enough",
  "questions": ["question1", "question2", "question3"]
}}

要求：
1. 只有在问题确实宽泛、目标不清、范围不清、偏好不清时才返回 should_clarify=true。
2. questions 最多 3 个，且必须是最关键的追问。
3. 如果问题已经足够具体，questions 返回空数组。
4. 不要输出 JSON 以外的任何内容。
5. 如果问题是情感/伴侣/人生选择/个人策略/职业发展这类主题，不要套用固定模板，要贴着原问题问。
"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = response.choices[0].message.content.strip()
        payload = _extract_json_block(content)
        if not payload:
            return None

        should = bool(payload.get("should_clarify"))
        reason = str(payload.get("reason", "llm_judgment")).strip() or "llm_judgment"
        questions = _normalize_questions(payload.get("questions", []))
        return ClarificationResult(should, reason, questions if should else [], "llm", "")
    except Exception as exc:
        global _LAST_LLM_ERROR
        _LAST_LLM_ERROR = str(exc)
        return None


_LAST_LLM_ERROR = ""


def should_clarify(query: str) -> ClarificationResult:
    normalized = (query or "").strip()
    if not normalized:
        return ClarificationResult(False, "empty_query", [], "rule", "")

    if _llm_enabled():
        llm_result = _llm_should_clarify(query)
        if llm_result is not None:
            return llm_result
        rule_result = _rule_based_should_clarify(query)
        return ClarificationResult(
            rule_result.should_clarify,
            rule_result.reason,
            rule_result.questions,
            "rule_fallback",
            _LAST_LLM_ERROR,
        )

    return _rule_based_should_clarify(query)


def build_clarified_query(query: str, questions: list[str], answers: list[str]) -> str:
    constraints = []
    for _question, answer in zip(questions, answers):
        cleaned = (answer or "").strip()
        if cleaned:
            constraints.append(cleaned)

    if not constraints:
        return query

    return f"{query}\n\n补充约束：\n- " + "\n- ".join(constraints)
