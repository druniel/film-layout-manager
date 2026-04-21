import pandas as pd
import numpy as np
import networkx as nx

priority_categories = ["Náš výběr z internetu", "Originální produkce", "Seriály"]

max_rows_per_category = {"Plné velikosti": 3, "Náš výběr": 5, "Náš výběr z internetu": 10}

# Aux functions
def get_movie_categories(row, categories):
    bool_values = row.iloc[2:].astype(str).str.lower().tolist() #vezme bool hodnoty u daného filmu a vloží do listu
    return [cat for cat, val in zip(categories, bool_values) if val == "true"] #list s kategoriemi, do kterých daný film patří

def load_films(file_name="databaze_filmu.xlsx"): #načte excel soubor se vstupními daty, vyčístí ho a vrátí jako pandas dataframe a první řádek určí jako hlavičku
    df = pd.read_excel(file_name, header=0)
    df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0], errors='coerce') #převádí první sloupec s prioritami na čísla a nečístelné hodnoty na NaN
    df = df[df.iloc[:, 0].notna()] #vyhodí pryč všechny NaN řádky
    df.iloc[:, 0] = df.iloc[:, 0].astype(int) #převede první sloupec s prioritami na integer
    df.iloc[:, 1] = df.iloc[:, 1].astype(str).str.strip() #sloupec s názvy filmů převede na stringy, očistí mezery
    df = df[~df.iloc[:, 1].str.lower().isin(['', 'nan'])] #označí řádky, kde není název filmu, nebo je tam "nan" jako True, znak ~ je vlastně not, otáčí operaci do záporu, aby zůstaly správné řádky
    return df

def get_categories(df): #vrátí hlavičku od 2. sloupce, tedy kategorie
    return df.columns[2:].tolist()

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
        G.add_edge(cat_node, "T", capacity=capacity, weight=0) #propojení uzlu dané kategorie > s uzlem spotřebitele; kapacita = kolik max filmů může z kategorie ke spotřebiteli odtéct; váha znamená, kolik stojí poslat jednu jednotu, 0 = neutrální

    for index, row in df.iterrows(): #smyčka stasvící graf
        film = row.iloc[1] #vytáhne název filmu ze sloupce č. 1 
        priority = row.iloc[0] #vytáhne prioritu ze sloupce č. 0
        movie_node = f"M_{index}" #string M_ a unikátní index filmu podle čísla řádku
        G.add_node(movie_node)
        
        match priority: #čím menší váha, tím raději algoritmus film použije
            case 1: weight = -100000 
            case 2: weight = -10000
            case 3: weight = -1000
            case _: weight = -100
            
        G.add_edge("S", movie_node, capacity=1, weight=weight) #propojení uzlu zdroje > s uzlem filmu; kapacita = film může jít jen do jedné z připojených kategorií
        film_categories = get_movie_categories(row, categories) #vrátí list s kategoriemi, do kterých daný film patří
        
        if film_categories: #pokud existují u filmu kategorie tak ho přidá do rebufferu i s dalšími údaji
            rebuffer.append((priority, film, film_categories))
        
        for cat in film_categories:
            cat_node = f"C_{cat}"
            
            match cat: #čím menší váha, tím spíš do ní algoritmus film přiřadí
                case "Plné velikosti": edge_weight = -90
                case "Náš výběr": edge_weight = -80
                case "Obsah zdarma": edge_weight = -70
                case "Pro děti": edge_weight = -60
                case "Rodinné filmy": edge_weight = -50
                case _ if cat in priority_categories: edge_weight = -40
                case _: edge_weight = 0
                
            G.add_edge(movie_node, cat_node, capacity=1, weight=edge_weight) #propojení uzlu filmu > s uzlem kategorie; kapacita = film může být přiřazen jen do jedné kategorie, váha = jak moc je pro danou kategorii vhodný, nižší váha = lepší
            
    return G, rebuffer

def extract_flow_results(df, flow_dict, categories, result_table):
    cat_counts = {cat: 0 for cat in categories} #dict sledující, kolik filmů je už bylo přiřazeno do každé kategorie
    used_films = set() #sleduje, které filmy se použily
    film_to_col = {} #dict sledující, do kterých kategorií už byl film přiřazen
    
    for index, row in df.iterrows(): #smyčka čte výsledky z po průtoku grafem a staví výslednou tabulku
        movie_node = f"M_{index}"
        film = row.iloc[1]
        
        if movie_node in flow_dict: #je film v grafu?
            for cat_node, flow in flow_dict[movie_node].items(): #u daného id filmu je vždy kategorie kam odešel a množství, buď 1 nebo 0
                if flow > 0 and cat_node.startswith("C_"): #protekl film do dané kategorie? a protekl vůbec do některé kategorie, nebo prošel přes bypass?
                    cat_name = cat_node.replace("C_", "") #odstraní prefix, aby kategorie byla shodná s názvem v tabulce
                    col_index = categories.index(cat_name) #zjistí index kategorie v tabulce
                    row_index = cat_counts[cat_name] #dle počítadla vložených filmů v kategorii zjistí řádek kam vložit nový film
                    
                    if row_index < 10:
                        result_table[row_index][col_index] = film 
                        film_to_col.setdefault(film, []).append(col_index) #pokud film v tomto sledovacím dictu neexistuje, vytvoří nový klíč a k němu list. pak vloží do listu číslo kategorie
                        cat_counts[cat_name] += 1
                        used_films.add(film)
                        
    return result_table, film_to_col, cat_counts, used_films

def calculate_free_space(result_table, categories, max_rows): #najde volná místa pro účely dodatečného doplňování
    free_space = {} #dict pro počty chybějících míst v tabulce, která je potřeba zaplnit
    for col, cat in enumerate(categories): #hledá prázdná místa v tabulce
        capacity = max_rows.get(cat, 10)
        free_space[cat] = sum(1 for row in range(capacity) if result_table[row][col] == "") #projde tabulku a pro každé volné místo v dané kategorii připočítá 1
        
    total_free_space = sum(free_space.values()) #celkový počet prázdných míst v tabulce
    
    return free_space, total_free_space