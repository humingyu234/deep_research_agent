from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ResearchState:
    query: str
    sub_questions: List[str] = field(default_factory=list)
    search_results: Dict[str, List[dict]] = field(default_factory=dict)
    summaries: Dict[str, str] = field(default_factory=dict)