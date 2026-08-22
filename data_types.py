from dataclasses import dataclass, field

@dataclass(frozen=True) #díky dekorátoru není třeba psát __init__ protože si to python vytvoří sám na pozadí, frozen zaručuje, že objekt po vytvoří nelze nijak měnit
class Film:
    id: int
    title: str
    priority: int
    categories: tuple[str, ...] #kvůli zmrazení tuple a je to seznam kategorií, do kterých daný film patří
    
@dataclass(frozen=True)
class CategoryRule:
    name: str #vždy název jedné kategorie
    capacity: int #kolik místa v ní je; toto číslo zůstává stejné celou dobu, protože nejde o údaj aktuálního naplnění, ale prostě jen celkové kapacity kategorie
    
@dataclass
class LayoutResult:
    result_table: list[list[str]] #výsledná tabulka pro zobrazení v gui
    id_table: list[list[int | None]] #v podstatě stejná tabulka, ale jen pro vnitřní logiku a obsahuje pouze id filmů
    category_counts: dict[str, int] #kolik filmů je v jaké kategorii
    used_films: set[int] #použité id filmů, tzn. jestli už film byl zařazen
    unassigned_films: list[tuple[Film, str]] = field(default_factory=list) #nepřiřazené filmy a důvod proč; fiedl se stará o to, aby se při každém vytvoření nového objektu vytvořil nový prázdný seznam s novou adresou v paměti
    message: str = ""
    
    @property #navenek se chová jako proměnná která ukazuje kolik filmů je aktuálně zařazeno
    def total_placed(self) -> int:
        return sum(self.category_counts.values())