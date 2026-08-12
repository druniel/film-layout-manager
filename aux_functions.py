import pandas as pd
import networkx as nx

priority_categories = ["Originální produkce", "Seriály", "Plná velikost 1", "Plná velikost 2", "Plná velikost 3", "Náš výběr"]

# Aux functions
def get_movie_categories(row, categories):
    bool_values = row[categories].astype(str).str.lower().tolist() #vezme bool hodnoty u daného filmu a vloží do listu
    return [cat for cat, val in zip(categories, bool_values) if val == "true"] #list s kategoriemi, do kterých daný film patří

def load_films(file_name="databaze_filmu.xlsx"): #načte excel soubor se vstupními daty, vyčístí ho a vrátí jako pandas dataframe a první řádek určí jako hlavičku
    try:
        df = pd.read_excel(file_name, header=0)
    except Exception as e:
        raise ValueError("Vybraný soubor nelze načíst. Ujistěte se, že jde o platnou databázi filmů ve formátu Excel.")
    
    if not {'ID', 'Film', 'Priorita'}.issubset(df.columns):
        raise ValueError("Vyberte prosím správnou databázi.")
    
    df["_excel_row"] = df.index + 2 # Uloží původní čísla řádků z Excelu pro chybové hlášky, hlavička = +1 a pandas začíná na 0 takže další +1
    df = df.dropna(how='all', subset=['ID', 'Film', 'Priorita']) # vyhodí řádky kde není žádné povinné pole
    df["ID_num"] = pd.to_numeric(df["ID"], errors='coerce') #převádí první sloupec s prioritami na čísla a nečíselné hodnoty na NaN
    df["Priorita_num"] = pd.to_numeric(df["Priorita"], errors='coerce')
    ignored_films = []
    
    invalid_ids = df[df["ID_num"].isna()] # Záchyt filmů s neplatným nebo chybějícím ID
    for _, row in invalid_ids.iterrows():
        title = row["Film"] if pd.notna(row["Film"]) and str(row["Film"]).strip() != "" else "Neznámý název"
        ignored_films.append(f"Řádek {row['_excel_row']}: '{title}' - neplatné nebo chybějící ID")
        
    invalid_priorities = df[df["Priorita_num"].isna() & df["ID_num"].notna()] # Záchyt filmů s neplatnou nebo chybějící prioritou
    for _, row in invalid_priorities.iterrows():
        ignored_films.append(f"Řádek {row['_excel_row']}: '{row['Film']}' - neplatná priorita")
        
    df["Film"] = df["Film"].astype(str).str.strip()
    invalid_titles = df[df["Film"].str.lower().isin(['', 'nan']) & df["ID_num"].notna() & df["Priorita_num"].notna()] # Záchyt filmů s chybějícím názvem
    for _, row in invalid_titles.iterrows():
        ignored_films.append(f"Řádek {row['_excel_row']}: ID {int(row['ID_num'])} - chybí název filmu")
        
    df = df[df["ID_num"].notna() & df["Priorita_num"].notna() & ~df["Film"].str.lower().isin(['', 'nan'])].copy() # Filtrace pouze platných řádků (zůstane to, co nemá nikde NaN a má název)
    
    df["ID"] = df["ID_num"].astype(int) # Zápis čistých dat a úklid pomocných sloupců
    df["Priorita"] = df["Priorita_num"].astype(int)
    df = df.drop(columns=["ID_num", "Priorita_num", "_excel_row"])
    
    return df, ignored_films

def get_categories(df): #vrátí hlavičku od 2. sloupce, tedy kategorie
    return [col for col in df.columns if col not in {"ID", "Film", "Priorita"}]

def build_flow_graph(film_list, categories, capacities, film_to_col = None, spacing = 0): #Sestaví NetworkX graf a rovnou naplní rebuffer
    if film_to_col is None:
        film_to_col = {}
    rebuffer = [] #list pro filmy, které se můžou použít znovu
    total_films = len(film_list) #celkový počet načtených filmů
    
    G = nx.DiGraph()
    G.add_node("S", demand=-total_films) #přidá uzel, S = source, záporný demand označuje "zdroj" a číslo určí počet dodaných jednotek
    G.add_node("T", demand=total_films)  #přidá uzel, T = terminal (spotřebitel), kladný demand označuje "spotřebitele" a číslo určí počet požadovaných jednotek
    G.add_edge("S", "T", capacity=total_films, weight=0) #přímo spojuje uzly S a T pro případ, že všechny tituly nepůjdou přiřadit, jinak by graf spadl; takový bypass
    
    for cat in categories:
        cat_node = f"C_{cat}"
        G.add_node(cat_node)
        capacity = capacities.get(cat, 0)
        G.add_edge(cat_node, "T", capacity=capacity, weight=0) #propojení uzlu dané kategorie > s uzlem spotřebitele; kapacita = kolik max filmů může z kategorie ke spotřebiteli odtéct; váha znamená, kolik stojí poslat jednu jednotku, 0 = neutrální

    for priority, film_id, film, film_categories in film_list: #smyčka stavící graf
        movie_node = f"M_{film_id}" #string M_ a unikátní id filmu
        G.add_node(movie_node)
        
        match priority: #čím menší váha, tím raději algoritmus film použije
            case 1: weight = -100000 
            case 2: weight = -10000
            case 3: weight = -1000
            case _: weight = -100
            
        G.add_edge("S", movie_node, capacity=1, weight=weight) #propojení uzlu zdroje > s uzlem filmu; kapacita = film může jít jen do jedné z připojených kategorií
        
        if film_categories: #pokud existují u filmu kategorie tak ho přidá do rebufferu i s dalšími údaji
            rebuffer.append((priority, film_id, film, film_categories))
        
        for cat in film_categories:
            cat_node = f"C_{cat}"
            col_index = categories.index(cat)
            original_columns = film_to_col.get(film_id, [])
            if any(abs(col_index - c) < spacing for c in original_columns): continue
            
            match cat: #čím menší váha, tím spíš do ní algoritmus film přiřadí
                case "Plná velikost 1" | "Plná velikost 2" | "Plná velikost 3": edge_weight = -90
                case "Náš výběr": edge_weight = -80
                case "Obsah zdarma": edge_weight = -70
                case "Pro děti": edge_weight = -60
                case "Rodinné filmy": edge_weight = -50
                case _ if cat in priority_categories: edge_weight = -40
                case _: edge_weight = 0
                
            G.add_edge(movie_node, cat_node, capacity=1, weight=edge_weight) #propojení uzlu filmu > s uzlem kategorie; kapacita = film může být přiřazen jen do jedné kategorie, váha = jak moc je pro danou kategorii vhodný, nižší váha = lepší
 
    return G, rebuffer

def extract_flow_results(film_data, flow_dict, categories, result_table, film_to_col, cat_counts, used_films):
    category_to_column = {cat: i for i, cat in enumerate(categories)}
    cat_assignments = {cat: [] for cat in categories}
    
    for node, edges in flow_dict.items():
        if str(node).startswith("M_"):
            film_id = int(node.removeprefix("M_"))
            
            for target_node, flow in edges.items():
                if flow > 0 and str(target_node).startswith("C_"):
                    cat_name = target_node.removeprefix("C_")
                    priority, film_name = film_data[film_id]
                    cat_assignments[cat_name].append((priority, film_id, film_name))
                    
    for cat_name, assigned_films in cat_assignments.items():
        assigned_films.sort(key=lambda x: x[0])
        col_index = category_to_column[cat_name] #zjistí index kategorie v tabulce
        
        for priority, film_id, film in assigned_films:
            row_index = cat_counts.get(cat_name, 0) #dle počítadla vložených filmů v kategorii zjistí řádek kam vložit nový film
                    
            if row_index < len(result_table):
                result_table[row_index][col_index] = film 
                film_to_col.setdefault(film_id, []).append(col_index) #pokud film v tomto sledovacím dictu neexistuje, vytvoří nový klíč a k němu list. pak vloží do listu číslo kategorie
                cat_counts[cat_name] = row_index + 1
                used_films.add(film_id)
                        
    return result_table, film_to_col, cat_counts, used_films