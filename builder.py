import data_types as dt
import networkx as nx
import random

MIN_SPACING = 4

def _build_flow_graph(films: list[dt.Film], category_rules: list[dt.CategoryRule], capacities: dict[str, int], film_to_col: dict | None = None, spacing: int = 0) -> nx.DiGraph:
    if film_to_col is None:
        film_to_col = {}
        
    total_films = len(films)
    G = nx.DiGraph()
    G.add_node("S", demand=-total_films) #přidá uzel, S = source, záporný demand označuje "zdroj" a číslo určí počet dodaných jednotek
    G.add_node("T", demand=total_films) #přidá uzel, T = terminal (spotřebitel), kladný demand označuje "spotřebitele" a číslo určí počet požadovaných jednotek
    G.add_edge("S", "T", capacity=total_films, weight=0) #přímo spojuje uzly S a T pro případ, že všechny tituly nepůjdou přiřadit, jinak by graf spadl; takový bypass
    
    for rule in category_rules:
        cat_node = f"C_{rule.name}"
        G.add_node(cat_node)
        G.add_edge(cat_node, "T", capacity=capacities.get(rule.name, 0), weight=0) #propojení uzlu dané kategorie > s uzlem spotřebitele; kapacita = kolik max filmů může z kategorie ke spotřebiteli odtéct - kapacita je max 10 popř míň; váha znamená, kolik stojí poslat jednu jednotku, 0 = neutrální
        
    for film in films: #smyčka stavící graf
        if not film.categories:
            continue
            
        movie_node = f"M_{film.id}" #string M_ a unikátní id filmu
        G.add_node(movie_node)
        
        match film.priority: #čím menší váha, tím raději algoritmus film použije
            case 1: weight = -100000 
            case 2: weight = -10000
            case 3: weight = -1000
            case _: weight = -100
            
        G.add_edge("S", movie_node, capacity=1, weight=weight) #propojení uzlu zdroje > s uzlem filmu; kapacita = ze zdroje do uzlu film může jít logicky jen 1 film
        original_columns = film_to_col.get(film.id, []) # ve kterých sloupcích (čísla) už tento konkrétní film leží (pro Fázi 2)
        
        for cat_name in film.categories: #prochází všechny kategorie do kterých film patří
            try:
                col_idx = next(i for i, r in enumerate(category_rules) if r.name == cat_name) # číslo sloupce dané kategorie
            except StopIteration:
                continue # pokud kategorie není v pravidlech, přeskočí se
                
            if any(abs(col_idx - c) < spacing for c in original_columns):
                continue # pokud už film je v tabulce a nový sloupec je blízko, tak se tohle spojení vůbec nevytvoří
                
            cat_node = f"C_{cat_name}"
            
            match cat_name:
                case "Plná velikost 1" | "Plná velikost 2" | "Plná velikost 3": edge_weight = -90
                case "Náš výběr": edge_weight = -80
                case "Originální produkce": edge_weight = -70
                case "Seriály": edge_weight = -60
                case "Obsah zdarma": edge_weight = -50
                case "Pro děti": edge_weight = -40
                case "Rodinné filmy": edge_weight = -30
                case _: edge_weight = 0
                
            G.add_edge(movie_node, cat_node, capacity=1, weight=edge_weight) #propojení uzlu filmu > s uzlem kategorie; kapacita = film může být přiřazen jen do jedné kategorie, váha = jak moc je pro danou kategorii vhodný, nižší váha = lepší
    return G

def _extract_flow_results(flow_dict, films, category_rules, table, id_table, cat_counts, used_films, film_to_col):
    cat_to_col = {rule.name: idx for idx, rule in enumerate(category_rules)} # rychlé zjištění čísla sloupce dle názvu kategorie
    
    for film in films:
        movie_node = f"M_{film.id}"
        for target_node, flow_value in flow_dict.get(movie_node, {}).items(): # flow_dict.get vrátí cíle a objem (např. {'C_Drama': 1, 'C_Náš výběr': 0})
            if flow_value > 0 and target_node.startswith("C_"): # pokud film protekl do daného uzlu, je to to co hledáme
                cat_name = target_node.removeprefix("C_")
                col_idx = cat_to_col[cat_name] #zjistí index kategorie v tabulce
                row_idx = cat_counts.get(cat_name, 0) #dle počítadla vložených filmů v kategorii zjistí řádek kam vložit nový film
                
                if row_idx < category_rules[col_idx].capacity:
                    table[row_idx][col_idx] = film.title
                    id_table[row_idx][col_idx] = film.id
                    cat_counts[cat_name] += 1
                    used_films.add(film.id)
                    film_to_col.setdefault(film.id, []).append(col_idx) #pokud film v tomto sledovacím dictu neexistuje, vytvoří nový klíč a k němu list. pak vloží do listu číslo kategorie; číslo sloupce pro rozestupy

def generate_layout(films: list[dt.Film], category_rules: list[dt.CategoryRule]) -> dt.LayoutResult:
    table = [["" for _ in range(len(category_rules))] for _ in range(10)]
    id_table: list[list[int | None]] = [[None for _ in range(len(category_rules))] for _ in range(10)]
    cat_counts = {rule.name: 0 for rule in category_rules}
    capacities = {rule.name: rule.capacity for rule in category_rules} # Na začátku je kapacita rovna pravidlům
    used_films = set()
    film_to_col = {}
    unassigned_films = []
    shuffled_films = list(films)
    random.shuffle(shuffled_films)
    sorted_films = sorted(shuffled_films, key=lambda f: f.priority)
    G = _build_flow_graph(sorted_films, category_rules, capacities, film_to_col, spacing=0)
    
    try:
        flow_dict = nx.min_cost_flow(G)
    except Exception as e:
        raise RuntimeError(f"Chyba v NetworkX (Fáze 1): {e}")

    _extract_flow_results(flow_dict, sorted_films, category_rules, table, id_table, cat_counts, used_films, film_to_col)
    
    for f in sorted_films:
        if f.id not in used_films:
            if not f.categories:
                unassigned_films.append((f, "Film nemá v Excelu přiřazenou žádnou kategorii"))
            else:
                unassigned_films.append((f, "Kapacita vhodných kategorií je plná"))
    
    message = f"Úspěšně přiřazeno {len(used_films)} unikátních filmů do {sum(cat_counts.values())} okýnek."
    return dt.LayoutResult(table, id_table, cat_counts, used_films, unassigned_films, message)

def refill_empty_slots(layout: dt.LayoutResult, films: list[dt.Film], category_rules: list[dt.CategoryRule]) -> dt.LayoutResult:
    total_capacity = sum(rule.capacity for rule in category_rules)
    film_to_col = {}
    
    if (total_capacity - layout.total_placed) <= 0:
        layout.message = "Není co doplňovat, všechna místa jsou plná."
        return layout
    
    for row in layout.id_table: # Z ID tabulky získáme aktuální informace o tom, ve kterých sloupcích už filmy leží
        for c_idx, film_id in enumerate(row):
            if film_id is not None:
                film_to_col.setdefault(film_id, []).append(c_idx)
    
    if any(len(cols) > 2 for cols in film_to_col.values()):
        raise ValueError("Kritická chyba: Vstupní rozvržení porušuje pravidlo maximálně 2 výskytů na film.")
    
    eligible_films = [f for f in films if len(film_to_col.get(f.id, [])) < 2] # Vyfiltruje z databáze POUZE ty filmy, které jsou v tabulce méně než dvakrát, tedy 1x
    shuffled_films = list(eligible_films)
    random.shuffle(shuffled_films)
    remaining_caps = {rule.name: rule.capacity - layout.category_counts.get(rule.name, 0) for rule in category_rules}
    G = _build_flow_graph(shuffled_films, category_rules, remaining_caps, film_to_col, spacing=MIN_SPACING)
    
    try:
        flow_dict = nx.min_cost_flow(G)
    except Exception as e:
        raise RuntimeError(f"Chyba v NetworkX (Fáze 2): {e}")

    films_before = layout.total_placed
    _extract_flow_results(flow_dict, shuffled_films, category_rules, layout.result_table, layout.id_table, layout.category_counts, layout.used_films, film_to_col)
    films_after = layout.total_placed
    layout.message = f"Úspěšně doplněno {films_after - films_before} filmů z rebufferu."
    return layout