from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ResearchState:
    query: str
    task_type: str = "RESEARCH"
    router_source: str = ""
    routing_reason: str = ""
    routing_confidence: float = 0.0
    routing_note: str = ""
    planner_type: str = ""
    planner_source: str = ""
    planner_reason: str = ""
    planner_note: str = ""
    original_query: str = ""
    clarified_query: str = ""
    task_id: str = ""
    task_status: str = "created"
    task_dir: str = ""
    log_path: str = ""
    report_path: str = ""
    clarification_questions: List[str] = field(default_factory=list)
    clarification_answers: List[str] = field(default_factory=list)
    sub_questions: List[str] = field(default_factory=list)
    search_results: Dict[str, List[dict]] = field(default_factory=dict)
    summaries: Dict[str, str] = field(default_factory=dict)
    scratchpad_entries: List[dict] = field(default_factory=list)
    citation_index: Dict[str, dict] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.original_query:
            self.original_query = self.query
        if not self.clarified_query:
            self.clarified_query = self.query
