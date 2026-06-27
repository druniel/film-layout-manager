import aux_functions as af
import random
import networkx as nx
from collections import deque

class FilmProcessor:
    def __init__(self):
        self.df = af.load_films()
        self.categories = af.get_categories(self.df)
        self.max_rows = af.max_rows_per_category
        self.reset()
        
    def reset(self):
        self.result_table = [["" for _ in range(len(self.categories))] for _ in range(10)]
        self.G, self.rebuffer = af.build_flow_graph(self.df, self.categories)
        self.film_to_col = {}
        self.cat_counts = {}
        self.used_films = set()

    def get_carousel_data_unique(self): #funkce s logikou plnění tabulky unikátními filmy
        try: #spustí proces toku dat grafem tak, aby to bylo podle pravidel a stálo to co nejmíň
            flow_dict = nx.min_cost_flow(self.G)
        except Exception as e: #když se to nepovede, tak nastala chyba v networkx a konzole vypíše error
            raise RuntimeError(f"Chyba v NetworkX: {e}")
    
        self.result_table, self.film_to_col, self.cat_counts, self.used_films = af.extract_flow_results(self.df, flow_dict, self.categories, self.result_table) #z výsledků průtoku grafem vytvoří tabulku a další potřebné datové struktury
    
        random.shuffle(self.rebuffer)
    
        return self.result_table, f"Úspěšně přiřazeno {len(self.used_films)} unikátních filmů do {sum(self.cat_counts.values())} okýnek."    


    def get_carousel_data_additional(self): #funkce která řeší doplnění tabulky opakujícími se filmy
        free_space, total_free_space = af.calculate_free_space(self.result_table, self.categories, self.max_rows) #výpočet volných míst
    
        if not self.rebuffer or total_free_space == 0: #pokud není nic v rebufferu nebo nejsou volná místa tak vrátí původní tabulku
            return self.result_table, "Není co doplňovat, rebuffer je prázdný nebo nejsou žádná volná místa."
    
        self.rebuffer.sort(key=lambda x: x[0]) #seřadí rebuffer podle priority filmů
        rebuffer_deque = deque(self.rebuffer)
        filled_films = af.add_films_from_rebuffer(rebuffer_deque, free_space, self.categories, self.max_rows, self.result_table, self.film_to_col)
        self.rebuffer = list(rebuffer_deque)
        
        return self.result_table, f"Úspěšně doplněno {filled_films} filmů z rebufferu."