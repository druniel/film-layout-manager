from main_functions import get_carousel_data_unique, get_carousel_data_additional

class DataManager: #třída spravující data
    def __init__(self):
        self.result_table = None
        self.rebuffer = None
        self.film_to_col = None
        self.categories = None
        self.max_rows_per_category = None
        
    def reset(self):
        self.result_table = None
        self.rebuffer = None
        self.film_to_col = None
        self.categories = None
        self.max_rows_per_category = None

    def initialize(self): 
        (
            self.result_table,
            self.rebuffer,
            self.film_to_col,
            self.categories,
            self.max_rows_per_category,
            message
        ) = get_carousel_data_unique()
        return self.result_table, message

    def fill_free_spaces(self):
        if self.result_table is None or self.rebuffer is None:
            raise ValueError("Tabulka ještě nebyla vytvořena.")
        self.result_table, message = get_carousel_data_additional(
            self.result_table,
            self.rebuffer,
            self.film_to_col,
            self.categories,
            self.max_rows_per_category
        )
        return self.result_table, message