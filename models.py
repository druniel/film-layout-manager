from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional

@dataclass(frozen=True)
class Film:
    id: int
    title: str
    priority: int
    categories: tuple[str, ...]
    
@dataclass(frozen=True)
class CategoryRule:
    name: str
    capacity: int = 10
    
@dataclass
class LayoutResult:
    result_table: List[List[str]]
    cat_counts: Dict[str, int]
    used_films: Set[int]
    unassigned_films: List[tuple[Film, str]] = field(default_factory=list)
    message: str = ""
    
    @property
    def total_placed(self) -> int:
        return sum(self.cat_counts.values())