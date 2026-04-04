import json
import os
from dataclasses import dataclass

from agent.env_loader import load_local_env
from agent.planner import classify_query


load_local_env()


TASK_TYPES = {"RESEARCH", "ADVICE", "QUICK_ANSWER", "UNSUPPORTED"}


@dataclass
class RouteDecision:
    task_type: str
    confidence_score: float
    needs_clarification: bool
    routing_reason: str
    source: str = "llm"
    note: str = ""


_LAST_ROUTER_ERROR = ""


def _router_llm_enabled() -> bool:
    if os.getenv("TASK_ROUTER_USE_LLM", "1") == "0":
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


def _clamp_confidence(value: object) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, numeric))


def _normalize_task_type(value: object) -> str:
    task_type = str(value or "").strip().upper()
    if task_type not in TASK_TYPES:
        return "UNSUPPORTED"
    return task_type


def _llm_route(query: str) -> RouteDecision | None:
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
        prompt = f"""
You are the Master Task Router for an advanced AI system.
Your only job is to classify the user's query into the correct workflow.

Classify into one of these task types:
- RESEARCH: objective, evidence-heavy, needs deep search / comparison / synthesis
- ADVICE: personal, subjective, relationship / career / lifestyle / life-decision guidance
- QUICK_ANSWER: simple factual lookup, definition, syntax, or lightweight explanation
- UNSUPPORTED: unclear, chaotic, or not suitable for the current system

Also decide whether the system should clarify before answering.
Set needs_clarification=true when the query is personal but still lacks important preferences, scope, goals, or constraints.
For partner / relationship / career-choice / life-choice questions, prefer needs_clarification=true unless the user has already given unusually clear constraints.

Return valid JSON only with this exact schema:
{{
  "task_type": "RESEARCH" | "ADVICE" | "QUICK_ANSWER" | "UNSUPPORTED",
  "confidence_score": 0.0,
  "needs_clarification": true,
  "routing_reason": "One short sentence."
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
        return RouteDecision(
            task_type=_normalize_task_type(payload.get("task_type")),
            confidence_score=_clamp_confidence(payload.get("confidence_score")),
            needs_clarification=bool(payload.get("needs_clarification")),
            routing_reason=str(payload.get("routing_reason", "")).strip() or "LLM classified the query into this workflow.",
            source="llm",
            note="",
        )
    except Exception as exc:
        global _LAST_ROUTER_ERROR
        _LAST_ROUTER_ERROR = str(exc)
        return None


def _fallback_route(query: str) -> RouteDecision:
    query_type = classify_query(query)
    normalized = (query or "").strip().lower()

    if query_type in {"timeline", "comparison", "driver", "trend", "recommendation"}:
        task_type = "RESEARCH"
        reason = "Fallback routing classified the query as evidence-heavy research."
        clarify = True
    elif query_type in {"definition", "howto"} and len(normalized) <= 40:
        task_type = "QUICK_ANSWER"
        reason = "Fallback routing classified the query as a lightweight factual or explanatory request."
        clarify = False
    elif any(token in normalized for token in ["适合什么样", "伴侣", "女朋友", "男朋友", "该不该", "怎么选", "适合我吗"]):
        task_type = "ADVICE"
        reason = "Fallback routing classified the query as personal advice."
        clarify = True
    elif normalized:
        task_type = "RESEARCH"
        reason = "Fallback routing defaulted to the research workflow."
        clarify = False
    else:
        task_type = "UNSUPPORTED"
        reason = "Fallback routing could not classify the query."
        clarify = False

    return RouteDecision(
        task_type=task_type,
        confidence_score=0.35,
        needs_clarification=clarify,
        routing_reason=reason,
        source="fallback",
        note=_LAST_ROUTER_ERROR,
    )


def route_task(query: str) -> RouteDecision:
    normalized = (query or "").strip()
    if not normalized:
        return RouteDecision(
            task_type="UNSUPPORTED",
            confidence_score=1.0,
            needs_clarification=False,
            routing_reason="The query is empty.",
            source="rule",
            note="",
        )

    if _router_llm_enabled():
        llm_result = _llm_route(normalized)
        if llm_result is not None:
            return llm_result

    return _fallback_route(normalized)
