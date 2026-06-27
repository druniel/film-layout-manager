import aux_functions as af
import random
import networkx as nx
from collections import deque


def get_carousel_data_unique(): #funkce s logikou plnění tabulky unikátními filmy
    df = af.load_films()
    categories = af.get_categories(df) #vytvoří list s kategoriemi
    result_table = [["" for _ in range(len(categories))] for _ in range(10)] #vytvoří se finální tabulka, počet řádků 10, počet sloupců = počtu kategorií
    G, rebuffer = af.build_flow_graph(df, categories) #vytvoří graf a naplní rebuffer
            
    try: #spustí proces toku dat grafem tak, aby to bylo podle pravidel a stálo to co nejmíň
        flow_dict = nx.min_cost_flow(G)
    except Exception as e: #když se to nepovede, tak nastala chyba v networkx a konzole vypíše error
        raise RuntimeError(f"Chyba v NetworkX: {e}")
    
    result_table, film_to_col, cat_counts, used_films = af.extract_flow_results(df, flow_dict, categories, result_table) #z výsledků průtoku grafem vytvoří tabulku a další potřebné datové struktury              
    
    random.shuffle(rebuffer)
    
    stats_message = f"Úspěšně přiřazeno {len(used_films)} unikátních filmů do {sum(cat_counts.values())} okýnek."
    
    return result_table, rebuffer, film_to_col, categories, af.max_rows_per_category, stats_message


def get_carousel_data_additional(result_table, rebuffer, film_to_col, categories, max_rows): #funkce která řeší doplnění tabulky opakujícími se filmy
    free_space, total_free_space = af.calculate_free_space(result_table, categories, max_rows) #výpočet volných míst
    
    if not rebuffer or total_free_space == 0: #pokud není nic v rebufferu nebo nejsou volná místa tak vrátí původní tabulku
        return result_table, "Není co doplňovat, rebuffer je prázdný nebo nejsou žádná volná místa."
    
    rebuffer.sort(key=lambda x: x[0]) #seřadí rebuffer podle priority filmů
    rebuffer = deque(rebuffer)
    filled_films = af.add_films_from_rebuffer(rebuffer, free_space, categories, max_rows, result_table, film_to_col)
    message = f"Úspěšně doplněno {filled_films} filmů z rebufferu."
        
    return result_table, message