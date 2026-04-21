import aux_functions as af
import random
import networkx as nx


def get_carousel_data_unique(): #funkce s logikou plnění tabulky unikátními filmy
    df = af.load_films()
    categories = af.get_categories(df) #vytvoří list s kategoriemi
    result_table = [["" for _ in range(len(categories))] for _ in range(10)] #vytvoří se finální tabulka, počet řádků 10, počet sloupců = počtu kategorií
    G, rebuffer = af.build_flow_graph(df, categories) #vytvoří graf a naplní rebuffer
            
    try: #spustí proces toku dat grafem tak, aby to bylo podle pravidel a stálo to co nejmíň
        flow_dict = nx.min_cost_flow(G)
    except Exception as e: #asi když se to nepovede, tak nastala chyba v networkx a konzole vypíše error toto bych rád přesunul do frontendu, aby vyjelo okýnko
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
    filled_films = 0
    
    while rebuffer and sum(free_space.values()) > 0: #běží dokud je něco v rebufferu a zároveň jsou v tabulce volná místa
        priority, film, film_cat = rebuffer.pop(0)
        random.shuffle(film_cat)
        
        for cat in film_cat:
            if free_space.get(cat, 0) > 0: #pokud má kategorie víc než 0 volných míst, jinak defaultně 0
                col_index = categories.index(cat) #vytvoří proměnnou s číslem sloupce podle toho kolikátá je ta kategorie
                capacity = max_rows.get(cat, 10)
                original_columns = film_to_col.get(film, []) #kategorie, do kterých už film byl zařazen
                
                if any(abs(col_index - c) < 3 for c in original_columns): #kontrola vzdálenosti sloupce kam chce film umístit od ostatních sloupců, kde už je
                    continue #pokud je rozestup menší než 3 sloupce tak zkusí jinou kategorii
                
                for row in range(capacity): #hledá volný řádek v dané kategorii
                    if result_table[row][col_index] == "":
                        result_table[row][col_index] = film
                        film_to_col.setdefault(film, []).append(col_index) #pro účely sledování připíše k tomu filmu tuto kategorii
                        free_space[cat] -= 1 #snižuje počet volných míst u dané kategorie, aby while loop nejel donekonečna
                        filled_films += 1
                        break
                break
    
    message = f"Úspěšně doplněno {filled_films} filmů z rebufferu."
        
    return result_table, message