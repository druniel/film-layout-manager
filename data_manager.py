from main_functions import get_carousel_data_unique, get_carousel_data_additional

class DataManager:
    def __init__(self):
        self.tabulka = None
        self.rebuffer = None
        self.film_to_col = None
        self.kategorie = None
        self.max_pocet_radku = None
        
    def reset(self):
        self.tabulka = None
        self.rebuffer = None
        self.film_to_col = None
        self.kategorie = None
        self.max_pocet_radku = None

    def inicializuj(self):
        (
            self.tabulka,
            self.rebuffer,
            self.film_to_col,
            self.kategorie,
            self.max_pocet_radku
        ) = get_carousel_data_unique()
        return self.tabulka

    def dopln(self):
        if self.tabulka is None or self.rebuffer is None:
            raise ValueError("Tabulka ještě nebyla vytvořena.")
        self.tabulka = get_carousel_data_additional(
            self.tabulka,
            self.rebuffer,
            self.film_to_col,
            self.kategorie,
            self.max_pocet_radku
        )
        return self.tabulka