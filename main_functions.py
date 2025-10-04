import pandas as pd
import aux_functions as af

# Hlavní funkce
def get_carousel_data_unique():
    df = af.nacti_filmy()
    df = df[df.iloc[:, 0].notna()]
    df = df[df.iloc[:, 0] < 5]  
    df = df.sample(frac=1).reset_index(drop=True)
    kategorie = af.ziskej_kategorie(df)
    tabulka = [[None for _ in range(len(kategorie))] for _ in range(10)]
    buffer = []
    rebuffer = []
    film_to_col = {}

    for _, row in df.iterrows():
        film = row.iloc[1]
        priorita = int(row.iloc[0])
        if pd.isna(film) or str(film).strip() == "":
            break

        kat_filmu = af.kategorie_filmu(row, kategorie)
        if not kat_filmu:
            continue

        if not af.vloz_prioritni_film(tabulka, film, kat_filmu, kategorie, film_to_col, priorita):
            buffer.append((priorita,film, kat_filmu))

    # Druhé kolo
    rebuffer = af.dopln_buffer(tabulka, buffer, film_to_col, kategorie, af.max_pocet_radku, rebuffer)

    return tabulka, rebuffer, film_to_col, kategorie, af.max_pocet_radku

def get_carousel_data_additional(tabulka, rebuffer, film_to_col, kategorie, max_pocet_radku):
        # Třetí kolo
    af.dopln_rebuffer(tabulka, rebuffer, film_to_col, kategorie, max_pocet_radku)
    
    return tabulka