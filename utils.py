import sys
from pathlib import Path

def get_resource_path(relative_path: str) -> str: 
    if hasattr(sys, '_MEIPASS'): # ptá se, jestli běží jako sbalené exe, pokud jo ta v sys._mespass leží cesta např. ke složce img kterou si vytvořil windows při spuštění; pokud ne tak ji hledá v normální složce img
        base_path = Path(getattr(sys, '_MEIPASS'))
    else:
        base_path = Path(__file__).resolve().parent
    return (base_path / relative_path).as_posix()