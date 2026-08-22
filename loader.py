import pandas as pd
import data_types as dt
import random
import math

def get_movie_categories(row, categories, excel_row, display_title, ignored_films) -> tuple[str, ...] | None:
    valid_cats = []
    truthy = {"true", "1", "ano", "yes", "x", "y"}
    falsy = {"false", "0", "ne", "no", "nan", "", "none", "n"}
    
    for cat in categories:
        val = str(row[cat]).strip().lower() #pandas row vidí kromě samotného řádku i hlavičky, takže se dá použít jméno kategorie
        
        if val in truthy:
            valid_cats.append(cat)
        elif val not in falsy:
            ignored_films.append(f"Řádek {excel_row}: '{display_title}' - Neplatná hodnota '{row[cat]}' v kategorii '{cat}'.")
            return None
    return tuple(valid_cats) #list s kategoriemi, do kterých daný film patří

def get_all_category_names(df) -> list[str]: #vrátí hlavičku pokud není označení jako id film nebo priorita, tedy vrátí kategorie
    return [col for col in df.columns if col not in {"ID", "Film", "Priorita"}]

def load_database(file_path: str) -> tuple[list[dt.Film], list[dt.CategoryRule], list[str]]:
    ignored_films = []
    valid_films = []
    seen_ids = set()
    seen_titles = set()
    required_cols = {'ID', 'Film', 'Priorita'}
    capacity_exceptions = {"Plná velikost 1": 1, "Plná velikost 2": 1, "Plná velikost 3": 1, "Náš výběr": 5}
    
    try:
        df = pd.read_excel(file_path, header=0)
    except Exception as e:
        raise ValueError("Vybraný soubor nelze načíst. Ujistěte se, že jde o platnou databázi filmů ve formátu Excel.")
        
    if not required_cols.issubset(df.columns):
        missing_cols = required_cols - set(df.columns)
        missing_str = ", ".join(missing_cols)
        raise ValueError(f"Vybraná databáze neobsahuje povinné sloupce. Chybí: {missing_str}")
    
    categories = get_all_category_names(df)
    df["_excel_row"] = df.index + 2 # Uloží původní čísla řádků z Excelu pro chybové hlášky, hlavička = +1 a pandas začíná na 0 takže další +1; vytváří nový pomocný sloupec
    df = df.dropna(how='all', subset=['ID', 'Film', 'Priorita']) # vyhodí prázdné řádky, resp ty, které nemají vyplněné žádné udaje u id film a priorita
    df["ID_num"] = pd.to_numeric(df["ID"], errors='coerce') #převádí první sloupec s prioritami na čísla a nečíselné hodnoty na NaN; vytváří nový pomocný sloupec
    df["Priorita_num"] = pd.to_numeric(df["Priorita"], errors='coerce'); #vytváří nový pomocný sloupec
    
    for _, row in df.iterrows():
        excel_row = row["_excel_row"]
        
        raw_title_val = row["Film"]
        if pd.isna(raw_title_val) or not str(raw_title_val).strip() or str(raw_title_val).strip().lower() == "nan":
            ignored_films.append(f"Řádek {excel_row}: Chybí název filmu.")
            continue
        
        raw_title = str(raw_title_val).strip()
        title_cf = raw_title.casefold() #casefold je agresivnější varianta lower(), prostě převede znaky na lowercase
        if title_cf in seen_titles:
            ignored_films.append(f"Řádek {excel_row}: '{raw_title}' - Duplicitní název filmu.")
            continue
        
        raw_id = row["ID_num"]
        if pd.isna(raw_id) or math.isinf(raw_id) or not float(raw_id).is_integer() or raw_id <= 0:
            ignored_films.append(f"Řádek {excel_row}: '{raw_title}' - ID musí být platné kladné celé číslo.")
            continue
        
        film_id = int(raw_id)
        if film_id in seen_ids:
            ignored_films.append(f"Řádek {excel_row}: '{raw_title}' - Duplicitní ID ({film_id}).")
            continue
        
        raw_priority = row["Priorita_num"]
        if pd.isna(raw_priority) or math.isinf(raw_priority) or not float(raw_priority).is_integer() or not (1 <= raw_priority <= 4):
            ignored_films.append(f"Řádek {excel_row}: '{raw_title}' - Priorita musí být celé číslo v rozsahu 1-4.")
            continue
        
        priority = int(raw_priority)
        film_cats = get_movie_categories(row, categories, excel_row, raw_title, ignored_films)
        if film_cats is None:
            continue
        
        seen_ids.add(film_id)
        seen_titles.add(title_cf)
        new_film = dt.Film(id = film_id, title = raw_title, priority = priority, categories = film_cats)
        valid_films.append(new_film)
        
    if not valid_films:
        raise ValueError("Databáze neobsahuje žádný platný film k zařazení.")
    
    if not categories:
        raise ValueError("Databáze neobsahuje žádné sloupce s kategoriemi.")
    
    random.shuffle(valid_films)
    category_rules = [dt.CategoryRule(name = cat, capacity = capacity_exceptions.get(cat, 10)) for cat in categories]
    
    for rule in category_rules:
        if not 0 <= rule.capacity <= 10:
            raise ValueError(f"Kapacita kategorie '{rule.name}' je nastavena na {rule.capacity}, ale systémový limit je 0 až 10 okýnek.")
        
    return valid_films, category_rules, ignored_films