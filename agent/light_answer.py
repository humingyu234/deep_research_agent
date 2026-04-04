import os


WEAK_CONSTRAINT_MARKERS = (
    "都行",
    "都可以",
    "无所谓",
    "看情况",
    "随缘",
    "不确定",
    "差不多",
)


def _format_evidence(results: list[dict], limit: int = 4) -> str:
    lines = []
    for item in results[:limit]:
        title = (item.get("title") or "").strip()
        snippet = (item.get("snippet") or "").strip()
        source = (item.get("source") or "").strip()
        if not title and not snippet:
            continue
        lines.append(f"- 标题: {title}\n  摘要: {snippet}\n  来源: {source}")
    return "\n".join(lines).strip()


def _extract_constraints(query: str) -> list[str]:
    marker = "补充约束："
    if marker not in query:
        return []

    tail = query.split(marker, 1)[1]
    constraints: list[str] = []
    for raw_line in tail.splitlines():
        line = raw_line.strip()
        if line.startswith("-"):
            value = line[1:].strip()
            if value:
                constraints.append(value)
    return constraints


def _split_constraints(constraints: list[str]) -> tuple[list[str], list[str]]:
    strong: list[str] = []
    weak: list[str] = []
    for item in constraints:
        if any(marker in item for marker in WEAK_CONSTRAINT_MARKERS):
            weak.append(item)
        else:
            strong.append(item)
    return strong, weak


def _basic_fallback_answer(query: str, task_type: str, results: list[dict]) -> str:
    evidence = _format_evidence(results, limit=3)
    constraints = _extract_constraints(query)
    strong_constraints, weak_constraints = _split_constraints(constraints)

    if task_type == "ADVICE":
        lines = [
            "## 我的直接判断",
            "这是个人建议题，不适合被包装成有强证据闭环的研究报告。",
            "我可以给你一个方向性判断，但你最终还是要结合自己的真实感受做决定。",
        ]
        if strong_constraints:
            lines.extend(["", "## 为什么这么看", *[f"- {item}" for item in strong_constraints]])
        if weak_constraints:
            lines.extend(["", "## 边界提醒", *[f"- `{item}` 暂时不作为强偏好处理。" for item in weak_constraints]])
        else:
            lines.extend(["", "## 边界提醒", "- 这类问题更依赖偏好、目标和真实相处体验。"])
        lines.extend(["", "## 可执行建议", "- 先把真正重要的两到三个标准守住，再通过真实互动验证。"])
        if evidence:
            lines.extend(["", "## 可参考线索", evidence])
        return "\n".join(lines)

    lines = [
        "## 快速回答",
        f"问题：{query}",
        "当前已走轻量回答链，这类问题通常不需要完整 research pipeline。",
    ]
    if evidence:
        lines.extend(["", "## 参考线索", evidence])
    return "\n".join(lines)


def generate_light_answer(query: str, task_type: str, results: list[dict]) -> str:
    try:
        from openai import OpenAI

        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return _basic_fallback_answer(query, task_type, results)

        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        evidence = _format_evidence(results, limit=4)
        constraints = _extract_constraints(query)
        strong_constraints, weak_constraints = _split_constraints(constraints)
        strong_constraint_text = (
            "\n".join(f"- {item}" for item in strong_constraints) if strong_constraints else "无"
        )
        weak_constraint_text = (
            "\n".join(f"- {item}" for item in weak_constraints) if weak_constraints else "无"
        )

        if task_type == "ADVICE":
            prompt = f"""
你是一个克制、诚实、有判断力的 advice assistant。

用户问题：
{query}

强约束（必须优先回应）：
{strong_constraint_text}

弱约束（只表示用户暂时没有强偏好，不要当成重点展开）：
{weak_constraint_text}

可参考材料：
{evidence or "无外部材料"}

要求：
1. 这是个人建议题，不要写成研究报告。
2. 必须严格使用下面四个标题，且只输出这四个标题：
   - `## 我的直接判断`
   - `## 为什么这么看`
   - `## 边界提醒`
   - `## 可执行建议`
3. 必须优先使用强约束，回答要像是在回应这个具体的人，而不是在写通用模板文。
4. 对“都行 / 看情况 / 无所谓 / 都可以”这类表达，视为弱约束，不要把它们扩写成偏好。
5. 不要堆 MBTI 配对表，不要大量罗列人格类型名。除非真的必要，最多提 1 个类型作为例子，而且必须明确写出“仅供参考，不是公式”。
6. 不要用“驱动因素 / 关键变量 / 治理 / 落地成本 / 一手研究材料”等 research 口吻。
7. 如果没有外部证据，就坦诚保持在建议层，不要装成有强证据结论。
8. 语言要具体、克制、贴题，避免鸡汤和空话。
"""
        else:
            prompt = f"""
你是一个快速解释 assistant。

用户问题：
{query}

可参考材料：
{evidence or "无外部材料"}

要求：
1. 给一个直接、简洁、贴题的回答。
2. 不要写成研究报告。
3. 如果外部材料不足，就坦诚说明。
4. 输出中文 Markdown。
"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        content = (response.choices[0].message.content or "").strip()
        return content or _basic_fallback_answer(query, task_type, results)
    except Exception:
        return _basic_fallback_answer(query, task_type, results)
