from typing import Dict, List

from agent.state import ResearchState


def normalize_text(text: str) -> str:
    return " ".join(str(text or "").split())


def infer_focus(sub_question: str) -> str:
    text = normalize_text(sub_question).lower()
    if any(
        token in text
        for token in ["主流可选项", "评价维度", "选择标准", "优缺点", "适用人群", "综合建议", "recommendation"]
    ):
        return "recommendation"
    if any(token in text for token in ["驱动", "推动", "原因", "因素", "机制", "关键变量", "driver"]):
        return "driver"
    if any(token in text for token in ["风险", "限制", "挑战", "治理", "合规", "risk"]):
        return "risk"
    if any(token in text for token in ["未来", "变化", "演进", "方向", "change"]):
        return "change"
    if any(token in text for token in ["定义", "含义", "是什么", "原理", "组成", "definition"]):
        return "definition"
    return "general"


def make_result_key(result: dict) -> str:
    return "||".join(
        [
            normalize_text(result.get("source", "")),
            normalize_text(result.get("title", "")),
            normalize_text(result.get("snippet", ""))[:160],
        ]
    )


def ensure_source_id(state: ResearchState, result: dict) -> str:
    key = make_result_key(result)
    for source_id, payload in state.citation_index.items():
        if payload.get("key") == key:
            return source_id

    source_id = f"S{len(state.citation_index) + 1:03d}"
    state.citation_index[source_id] = {
        "key": key,
        "title": result.get("title", ""),
        "source": result.get("source", ""),
        "snippet": result.get("snippet", ""),
        "url": result.get("source", ""),
    }
    return source_id


def extract_summary_judgment(summary: str) -> str:
    for raw_line in summary.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line == "支撑点：":
            continue
        if line[0:2] in {"1.", "2.", "3."}:
            continue
        return line
    return normalize_text(summary)


def build_scratchpad_entry(
    state: ResearchState,
    sub_question: str,
    selected_results: List[dict],
    summary: str,
    reflection: dict,
) -> dict:
    source_ids = []
    evidence_notes = []

    for result in selected_results[:3]:
        source_id = ensure_source_id(state, result)
        source_ids.append(source_id)
        snippet = normalize_text(result.get("snippet", ""))
        if snippet:
            evidence_notes.append(snippet[:180])

    return {
        "sub_question": sub_question,
        "focus": infer_focus(sub_question),
        "status": reflection.get("status", "unknown"),
        "judgment": extract_summary_judgment(summary),
        "reason": reflection.get("reason", ""),
        "source_ids": source_ids,
        "evidence_notes": evidence_notes[:2],
    }


def render_central_report(state: ResearchState) -> str:
    lines = [
        "# Central Report",
        "",
        f"- Original Query: {state.original_query}",
        f"- Working Query: {state.query}",
        f"- Sub-questions: {len(state.sub_questions)}",
        f"- Scratchpad Entries: {len(state.scratchpad_entries)}",
        "",
        "## Scratchpad",
    ]

    if not state.scratchpad_entries:
        lines.append("- No scratchpad entries yet.")
    else:
        for index, entry in enumerate(state.scratchpad_entries, 1):
            lines.extend(
                [
                    f"### {index}. {entry['sub_question']}",
                    f"- focus: {entry['focus']}",
                    f"- status: {entry['status']}",
                    f"- judgment: {entry['judgment']}",
                    f"- reason: {entry['reason']}",
                    f"- source_ids: {', '.join(entry['source_ids']) if entry['source_ids'] else 'none'}",
                ]
            )
            if entry["evidence_notes"]:
                lines.append("- evidence_notes:")
                for note in entry["evidence_notes"]:
                    lines.append(f"  - {note}")
            lines.append("")

    lines.extend(["## Citation Index"])
    if not state.citation_index:
        lines.append("- No citations yet.")
    else:
        for source_id, payload in state.citation_index.items():
            lines.append(f"- {source_id}: {payload.get('title', '')} | {payload.get('source', '')}")

    return "\n".join(lines)


def render_report_citation_appendix(state: ResearchState) -> str:
    lines = ["## 引用附录", ""]

    if not state.scratchpad_entries:
        lines.append("- 当前没有可展示的引用记录。")
        return "\n".join(lines)

    lines.extend(["### 子问题对应来源", ""])
    for index, entry in enumerate(state.scratchpad_entries, 1):
        source_ids = ", ".join(entry.get("source_ids", [])) or "none"
        lines.append(f"{index}. {entry.get('sub_question', '')}")
        lines.append(f"   - Source_ID: {source_ids}")

    lines.extend(["", "### Source Index", ""])
    if not state.citation_index:
        lines.append("- 当前没有来源索引。")
        return "\n".join(lines)

    for source_id, payload in state.citation_index.items():
        title = payload.get("title", "").strip() or "Untitled"
        source = payload.get("source", "").strip() or "Unknown source"
        lines.append(f"- {source_id}: {title} | {source}")

    return "\n".join(lines)
