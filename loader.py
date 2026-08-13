import pandas as pd
import models as md

def get_movie_categories(row, categories) -> tuple[str, ...]:
    bool_values = row[categories].astype(str).str.lower().tolist() #vezme bool hodnoty u daného filmu a vloží do listu
    return tuple(cat for cat, val in zip(categories, bool_values) if val == "true") #list s kategoriemi, do kterých daný film patří

def get_all_category_names(df): #vrátí hlavičku od 2. sloupce, tedy kategorie
    return [col for col in df.columns if col not in {"ID", "Film", "Priorita"}]

def load_database(file_path: str) -> tuple[list[md.Film], list[str]]:
    ignored_films = []
    valid_films = []
    
    try:
        df = pd.read_excel(file_path, header=0)
    except Exception as e:
        raise ValueError("Vybraný soubor nelze načíst. Ujistěte se, že jde o platnou databázi filmů ve formátu Excel.")
        
    if not {'ID', 'Film', 'Priorita'}.issubset(df.columns):
        raise ValueError("Vyberte prosím správnou databázi.")
    
    categories = get_all_category_names(df)
    df["_excel_row"] = df.index + 2 # Uloží původní čísla řádků z Excelu pro chybové hlášky, hlavička = +1 a pandas začíná na 0 takže další +1; vytváří nový pomocný sloupec
    df = df.dropna(how='all', subset=['ID', 'Film', 'Priorita']) # vyhodí řádky kde není žádné povinné pole
    df["ID_num"] = pd.to_numeric(df["ID"], errors='coerce') #převádí první sloupec s prioritami na čísla a nečíselné hodnoty na NaN; vytváří nový pomocný sloupec
    df["Priorita_num"] = pd.to_numeric(df["Priorita"], errors='coerce'); #vytváří nový pomocný sloupec
    
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
    
    for _, row in df.iterrows():
        film_cats = get_movie_categories(row, categories)
        new_film = md.Film(id = int(row["ID_num"]), title = str(row["Film"]), priority = int(row["Priorita_num"]), categories = film_cats)
        valid_films.append(new_film)
        
    return valid_films, ignored_films