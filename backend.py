import aux_functions as af
import networkx as nx

class FilmProcessor:
    def __init__(self):
        self.df = None
        self.categories = []
        self.result_table = []
        self.G = None
        self.rebuffer = []
        self.film_to_col = {}
        self.cat_counts = {}
        self.used_films = set()
        self.capacity_exceptions = {"Plná velikost 1": 1, "Plná velikost 2": 1, "Plná velikost 3": 1, "Náš výběr": 5}
        self.min_category_spacing = 3
        self.film_data = {}
        self.state = "EMPTY"
        
    def load_data(self, file_path):
        new_df, ignored_films = af.load_films(file_path)
        new_categories = af.get_categories(new_df)
        self.df = new_df
        self.categories = new_categories
        self.reset()
        return ignored_films
        
    def reset(self):
        if self.df is None:
            self.__init__()
            return
        
        self.result_table = [["" for _ in range(len(self.categories))] for _ in range(10)]
        max_rows = {cat: self.capacity_exceptions.get(cat, 10) for cat in self.categories}
        self.df = self.df.sample(frac=1).reset_index(drop=True)
        self.film_to_col = {}
        self.cat_counts = {}
        self.used_films = set()
        film_list = []
        
        for _, row in self.df.iterrows():
            priority = int(row["Priorita"])
            film_id = int(row["ID"])
            film_name = str(row["Film"])
            film_categories = af.get_movie_categories(row, self.categories)
            if film_categories:
                film_list.append((priority, film_id, film_name, film_categories))
                self.film_data[film_id] = (priority, film_name)
                
        self.G, self.rebuffer = af.build_flow_graph(film_list, self.categories, max_rows)
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
     
        self.result_table, self.film_to_col, self.cat_counts, self.used_films = af.extract_flow_results(self.film_data, flow_dict, self.categories, self.result_table, self.film_to_col, self.cat_counts, self.used_films) #z výsledků průtoku grafem vytvoří tabulku a další potřebné datové struktury
        self.state = "GENERATED"
    
        return self.result_table, f"Úspěšně přiřazeno {len(self.used_films)} unikátních filmů do {sum(self.cat_counts.values())} okýnek."    


    def get_carousel_data_additional(self): #funkce která řeší doplnění tabulky opakujícími se filmy
        if self.state not in ["GENERATED", "REFILLED"]:
            raise RuntimeError("Doplňování z rebufferu lze spustit až po vytvoření unikátního rozvrhu.")
        
        remaining_capacity = {cat: self.capacity_exceptions.get(cat, 10) - self.cat_counts.get(cat, 0) for cat in self.categories}
        total_free_space = sum(remaining_capacity.values()) #výpočet volných míst
        film_count_before_p2 = sum(self.cat_counts.values())
    
        if not self.rebuffer or total_free_space <= 0: #pokud není nic v rebufferu nebo nejsou volná místa tak vrátí původní tabulku
            return self.result_table, "Není co doplňovat, rebuffer je prázdný nebo nejsou žádná volná místa."
        
        G_phase_2, _ = af.build_flow_graph(self.rebuffer, self.categories, remaining_capacity, self.film_to_col, self.min_category_spacing)
        
        try:
            flow_dict_2 = nx.min_cost_flow(G_phase_2)
        except Exception as e:
            raise RuntimeError(f"Chyba v NetworkX (Fáze 2): {e}")
        
        self.result_table, self.film_to_col, self.cat_counts, self.used_films = af.extract_flow_results(self.film_data, flow_dict_2, self.categories, self.result_table, self.film_to_col, self.cat_counts, self.used_films)
        film_count_after_p2 = sum(self.cat_counts.values())
        self.state = "REFILLED"
        
        return self.result_table, f"Úspěšně doplněno {film_count_after_p2 - film_count_before_p2} filmů z rebufferu."