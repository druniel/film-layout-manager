import aux_functions as af
import random
import networkx as nx
from collections import deque

class FilmProcessor:
    def __init__(self):
        self.df = None
        self.categories = []
        self.max_rows = None
        self.result_table = []
        self.G = None
        self.rebuffer = []
        self.film_to_col = {}
        self.cat_counts = {}
        self.used_films = set()
        self.state = "EMPTY"
        
    def load_data(self, file_path):
        new_df, ignored_films = af.load_films(file_path)
        new_categories = af.get_categories(new_df)
        new_max_rows = af.max_rows_per_category
        self.df = new_df
        self.categories = new_categories
        self.max_rows = new_max_rows
        self.reset()
        return ignored_films
        
    def reset(self):
        if self.df is None:
            self.__init__()
            return
        
        self.result_table = [["" for _ in range(len(self.categories))] for _ in range(10)]
        self.df = self.df.sample(frac=1).reset_index(drop=True)
        self.G, self.rebuffer = af.build_flow_graph(self.df, self.categories)
        self.film_to_col = {}
        self.cat_counts = {}
        self.used_films = set()
        self.state = "LOADED"

    def get_carousel_data_unique(self): #funkce s logikou plnění tabulky unikátními filmy
        if self.state != "LOADED":
            raise RuntimeError("Unikátní rozvrh lze vytvořit pouze z čisté tabulky po načtení dat nebo po resetu.")
        if self.G is None:
            raise RuntimeError("Graf nebyl vytvořen. Nejdříve načtěte data z Excelu.")
        try: #spustí proces toku dat grafem tak, aby to bylo podle pravidel a stálo to co nejmíň
            flow_dict = nx.min_cost_flow(self.G)
        except Exception as e: #když se to nepovede, tak nastala chyba v networkx a konzole vypíše error
            raise RuntimeError(f"Chyba v NetworkX: {e}")
    
        self.result_table, self.film_to_col, self.cat_counts, self.used_films = af.extract_flow_results(self.df, flow_dict, self.categories, self.result_table) #z výsledků průtoku grafem vytvoří tabulku a další potřebné datové struktury
    
        random.shuffle(self.rebuffer)
        
        self.state = "GENERATED"
    
        return self.result_table, f"Úspěšně přiřazeno {len(self.used_films)} unikátních filmů do {sum(self.cat_counts.values())} okýnek."    


    def get_carousel_data_additional(self): #funkce která řeší doplnění tabulky opakujícími se filmy
        if self.state not in ["GENERATED", "REFILLED"]:
            raise RuntimeError("Doplňování z rebufferu lze spustit až po vytvoření unikátního rozvrhu.")
        
        free_space, total_free_space = af.calculate_free_space(self.result_table, self.categories, self.max_rows) #výpočet volných míst
    
        if not self.rebuffer or total_free_space == 0: #pokud není nic v rebufferu nebo nejsou volná místa tak vrátí původní tabulku
            return self.result_table, "Není co doplňovat, rebuffer je prázdný nebo nejsou žádná volná místa."
    
        self.rebuffer.sort(key=lambda x: x[0]) #seřadí rebuffer podle priority filmů
        rebuffer_deque = deque(self.rebuffer)
        filled_films = af.add_films_from_rebuffer(rebuffer_deque, free_space, self.categories, self.max_rows, self.result_table, self.film_to_col)
        self.rebuffer = list(rebuffer_deque)
        self.state = "REFILLED"
        
        return self.result_table, f"Úspěšně doplněno {filled_films} filmů z rebufferu."