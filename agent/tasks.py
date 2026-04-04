import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List
from uuid import uuid4

from agent.state import ResearchState


TASKS_DIR = Path("outputs/tasks")
REPORTS_DIR = Path("outputs/reports")


def utc_now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def build_task_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"task_{timestamp}_{uuid4().hex[:6]}"


@dataclass
class ResearchTask:
    task_id: str
    created_at: str
    updated_at: str
    status: str
    original_query: str
    task_type: str = "RESEARCH"
    router_source: str = ""
    routing_reason: str = ""
    routing_confidence: float = 0.0
    planner_type: str = ""
    planner_source: str = ""
    planner_reason: str = ""
    clarified_query: str = ""
    task_dir: str = ""
    log_path: str = ""
    report_path: str = ""
    clarification_questions: List[str] = field(default_factory=list)
    clarification_answers: List[str] = field(default_factory=list)
    sub_questions: List[str] = field(default_factory=list)
    completed_sub_questions: List[str] = field(default_factory=list)
    scratchpad_entries: List[dict] = field(default_factory=list)
    citation_index: dict = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    @property
    def state_path(self) -> Path:
        return Path(self.task_dir) / "task.json"

    def to_dict(self) -> dict:
        return asdict(self)


def ensure_task_dirs() -> None:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def create_task(query: str) -> ResearchTask:
    ensure_task_dirs()
    now = utc_now_iso()
    task_id = build_task_id()
    task_dir = TASKS_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    task = ResearchTask(
        task_id=task_id,
        created_at=now,
        updated_at=now,
        status="created",
        original_query=query,
        clarified_query=query,
        task_dir=str(task_dir),
        report_path=str(REPORTS_DIR / f"{task_id}_report.md"),
    )
    save_task(task)
    return task


def save_task(task: ResearchTask) -> None:
    task.updated_at = utc_now_iso()
    task.state_path.write_text(
        json.dumps(task.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def update_task(task: ResearchTask, **fields: object) -> ResearchTask:
    for key, value in fields.items():
        setattr(task, key, value)
    save_task(task)
    return task


def sync_task_from_state(task: ResearchTask, state: ResearchState, note: str = "") -> ResearchTask:
    completed = [
        sub_question
        for sub_question in state.sub_questions
        if sub_question in state.summaries
    ]
    notes = list(task.notes)
    if note:
        notes.append(note)

    return update_task(
        task,
        clarified_query=state.query,
        task_type=state.task_type,
        router_source=state.router_source,
        routing_reason=state.routing_reason,
        routing_confidence=state.routing_confidence,
        planner_type=state.planner_type,
        planner_source=state.planner_source,
        planner_reason=state.planner_reason,
        clarification_questions=list(state.clarification_questions),
        clarification_answers=list(state.clarification_answers),
        sub_questions=list(state.sub_questions),
        completed_sub_questions=completed,
        scratchpad_entries=list(state.scratchpad_entries),
        citation_index=dict(state.citation_index),
        notes=notes[-20:],
    )
