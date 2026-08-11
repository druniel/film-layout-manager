import pandas as pd
import networkx as nx
import random

priority_categories = ["Originální produkce", "Seriály", "Plná velikost 1", "Plná velikost 2", "Plná velikost 3", "Náš výběr"]
max_rows_per_category = {"Plná velikost 1": 1, "Plná velikost 2": 1, "Plná velikost 3": 1, "Náš výběr": 5, "Obsah zdarma": 10}
mix_category_spacing = 3

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

def build_flow_graph(df, categories): #Sestaví NetworkX graf a rovnou naplní rebuffer
    rebuffer = [] #list pro filmy, které se můžou použít znovu
    total_films = len(df) #celkový počet načtených filmů
    
    G = nx.DiGraph()
    G.add_node("S", demand=-total_films) #přidá uzel, S = source, záporný demand označuje "zdroj" a číslo určí počet dodaných jednotek
    G.add_node("T", demand=total_films)  #přidá uzel, T = terminal (spotřebitel), kladný demand označuje "spotřebitele" a číslo určí počet požadovaných jednotek
    G.add_edge("S", "T", capacity=total_films, weight=0) #přímo spojuje uzly S a T pro případ, že všechny tituly nepůjdou přiřadit, jinak by graf spadl; takový bypass
    
    for cat in categories:
        cat_node = f"C_{cat}"
        G.add_node(cat_node)
        capacity = max_rows_per_category.get(cat, 10) #pokud kategorie není v dictu definovaná, get jí automaticky přiřadí kapacitu 10
        G.add_edge(cat_node, "T", capacity=capacity, weight=0) #propojení uzlu dané kategorie > s uzlem spotřebitele; kapacita = kolik max filmů může z kategorie ke spotřebiteli odtéct; váha znamená, kolik stojí poslat jednu jednotku, 0 = neutrální

    for index, row in df.iterrows(): #smyčka stavící graf
        film_id = row["ID"]
        film = row["Film"] #vytáhne název filmu ze sloupce č. 1 
        priority = row["Priorita"] #vytáhne prioritu ze sloupce č. 3
        movie_node = f"M_{film_id}" #string M_ a unikátní id filmu
        G.add_node(movie_node)
        
        match priority: #čím menší váha, tím raději algoritmus film použije
            case 1: weight = -100000 
            case 2: weight = -10000
            case 3: weight = -1000
            case _: weight = -100
            
        G.add_edge("S", movie_node, capacity=1, weight=weight) #propojení uzlu zdroje > s uzlem filmu; kapacita = film může jít jen do jedné z připojených kategorií
        film_categories = get_movie_categories(row, categories) #vrátí list s kategoriemi, do kterých daný film patří
        
        if film_categories: #pokud existují u filmu kategorie tak ho přidá do rebufferu i s dalšími údaji
            rebuffer.append((priority, film_id, film, film_categories))
        
        for cat in film_categories:
            cat_node = f"C_{cat}"
            
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

def extract_flow_results(df, flow_dict, categories, result_table):
    used_films = set() #sleduje, které filmy se použily
    film_to_col = {} #dict sledující, do kterých kategorií už byl film přiřazen
    category_to_column = {cat: i for i, cat in enumerate(categories)}
    cat_assignments = {cat: [] for cat in categories}
    cat_counts = {cat: 0 for cat in categories} #dict sledující, kolik filmů už bylo přiřazeno do každé kategorie
    
    for index, row in df.iterrows(): #smyčka čte výsledky po průtoku grafem a staví výslednou tabulku
        film_id = row["ID"]
        film = row["Film"]  
        priority = row["Priorita"]
        movie_node = f"M_{film_id}"
        
        if movie_node in flow_dict: #je film v grafu?
            for cat_node, flow in flow_dict[movie_node].items(): #u daného id filmu je vždy kategorie kam odešel a množství, buď 1 nebo 0
                if flow > 0 and cat_node.startswith("C_"): #protekl film do dané kategorie? a protekl vůbec do některé kategorie, nebo prošel přes bypass?
                    cat_name = cat_node.removeprefix("C_") #odstraní prefix, aby kategorie byla shodná s názvem v tabulce
                    cat_assignments[cat_name].append((priority, film_id, film))
                    
    for cat_name, assigned_films in cat_assignments.items():
        assigned_films.sort(key=lambda x: x[0])
        col_index = category_to_column[cat_name] #zjistí index kategorie v tabulce
        
        for priority, film_id, film in assigned_films:
            row_index = cat_counts[cat_name] #dle počítadla vložených filmů v kategorii zjistí řádek kam vložit nový film
                    
            if row_index < len(result_table):
                result_table[row_index][col_index] = film 
                film_to_col.setdefault(film_id, []).append(col_index) #pokud film v tomto sledovacím dictu neexistuje, vytvoří nový klíč a k němu list. pak vloží do listu číslo kategorie
                cat_counts[cat_name] += 1
                used_films.add(film_id)
                        
    return result_table, film_to_col, cat_counts, used_films

def calculate_free_space(result_table, categories, max_rows): #najde volná místa pro účely dodatečného doplňování
    free_space = {} #dict pro počty chybějících míst v tabulce, která je potřeba zaplnit
    max_table_rows = len(result_table)
    
    for col, cat in enumerate(categories): #hledá prázdná místa v tabulce
        capacity = max_rows.get(cat, 10)
        free_space[cat] = sum(1 for row in range(min(capacity, max_table_rows)) if result_table[row][col] == "") #projde tabulku a pro každé volné místo v dané kategorii připočítá 1
        
    total_free_space = sum(free_space.values()) #celkový počet prázdných míst v tabulce
    return free_space, total_free_space

def add_films_from_rebuffer(rebuffer, free_space, categories, max_rows, result_table, film_to_col):
    category_to_column = {cat: i for i, cat in enumerate(categories)}
    filled_films = 0
    total_free = sum(free_space.values())
    
    while rebuffer and total_free > 0: #běží dokud je něco v rebufferu a zároveň jsou v tabulce volná místa
        priority, film_id, film, film_cat = rebuffer.popleft()
        random.shuffle(film_cat)
        
        for cat in film_cat:
            if free_space.get(cat, 0) > 0: #pokud má kategorie víc než 0 volných míst, jinak defaultně 0
                col_index = category_to_column[cat] #vytvoří proměnnou s číslem sloupce podle toho kolikátá je ta kategorie
                capacity = max_rows.get(cat, 10)
                original_columns = film_to_col.get(film_id, []) #kategorie, do kterých už film byl zařazen
                
                if any(abs(col_index - c) < mix_category_spacing for c in original_columns): #kontrola vzdálenosti sloupce kam chce film umístit od ostatních sloupců, kde už je
                    continue #pokud je rozestup menší než 3 sloupce tak zkusí jinou kategorii
                
                for row in range(min(capacity, len(result_table))): #hledá volný řádek v dané kategorii
                    if result_table[row][col_index] == "":
                        result_table[row][col_index] = film
                        film_to_col.setdefault(film_id, []).append(col_index) #pro účely sledování připíše k tomu filmu tuto kategorii
                        free_space[cat] -= 1 #snižuje počet volných míst u dané kategorie, aby while loop nejel donekonečna
                        total_free -= 1
                        filled_films += 1
                        break
                break
    return filled_films