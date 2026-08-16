from dataclasses import dataclass, field

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
    result_table: list[list[str]]
    id_table: list[list[int | None]]
    category_counts: dict[str, int]
    used_films: set[int]
    unassigned_films: list[tuple[Film, str]] = field(default_factory=list)
    message: str = ""
    
    @property
    def total_placed(self) -> int:
        return sum(self.category_counts.values())