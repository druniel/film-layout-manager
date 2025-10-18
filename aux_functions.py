import pandas as pd
import numpy as np

prioritni_kategorie = [
    "Plné velikosti", "Náš výběr", "Náš výběr z internetu",
    "Obsah zdarma", "Pro děti", "Biblické filmy",
    "Originální produkce", "Seriály", "Rodinné filmy"
]

max_pocet_radku = {"Plné velikosti": 3, "Náš výběr": 5, "Náš výběr z internetu": 10}

# Aux functions
def get_volna_mista(tabulka, kategorie, max_pocet_radku):
    volna_mista = {}
    for i, kat in enumerate(kategorie):
        max_radku = max_pocet_radku.get(kat, 10)
        volna_mista[kat] = sum(1 for r in range(max_radku) if tabulka[r][i] is None)
    return volna_mista


def nacti_filmy(soubor="databaze_filmu.xlsx"):
    return pd.read_excel(soubor, header=0)


def ziskej_kategorie(df):
    return df.columns[2:].tolist()


def kategorie_filmu(row, kategorie):
    bool_hodnoty = row.iloc[2:].astype(str).str.lower().tolist()
    return [kat for kat, val in zip(kategorie, bool_hodnoty) if val == "true"]


def vloz_prioritni_film(tabulka, film, kategorie_filmu, kategorie, film_to_col, priorita):
    for kat in prioritni_kategorie:
        if kat in kategorie_filmu and priorita <= 2:
            col_index = kategorie.index(kat)
            for radek in range(10):
                if tabulka[radek][col_index] is None:
                    tabulka[radek][col_index] = film
                    film_to_col.setdefault(film, []).append(col_index)
                    return True
    return False


def dopln_buffer(tabulka, buffer, film_to_col, kategorie, max_pocet_radku, rebuffer=None):
    if rebuffer is None:
        rebuffer = []

    np.random.shuffle(buffer)
    buffer.sort(key=lambda x: len(x[2]), reverse=True)

    for index in range(len(buffer) - 1, -1, -1):
        priorita, film, kat_filmu = buffer[index]
        vlozeno = False
        
        if kat_filmu == ["Dokumenty"]:
            if priorita <= 2:
                col_index = kategorie.index("Dokumenty")
                max_radku = max_pocet_radku.get("Dokumenty", 10)
                for radek in range(max_radku):
                    if tabulka[radek][col_index] is None:
                        tabulka[radek][col_index] = film
                        film_to_col.setdefault(film, []).append(col_index)
                        vlozeno = True
                        break
                if not vlozeno:
                    rebuffer.append((priorita, film, kat_filmu))
            else:
                rebuffer.append((priorita, film, kat_filmu))
        
        else:
            # Only remove "Dokumenty" if film is already in table
            if "Dokumenty" in kat_filmu and film in film_to_col:
                kat_filmu = [kat for kat in kat_filmu if kat != "Dokumenty"]
                
            np.random.shuffle(kat_filmu)
            for kat in kat_filmu:
                col_index = kategorie.index(kat)
                max_radku = max_pocet_radku.get(kat, 10)
                for radek in range(max_radku):
                    if tabulka[radek][col_index] is None:
                        tabulka[radek][col_index] = film
                        film_to_col.setdefault(film, []).append(col_index)
                        dalsi_kategorie = [k for k in kat_filmu if k != kat]
                        if dalsi_kategorie:
                            rebuffer.append((priorita, film, dalsi_kategorie))
                        vlozeno = True
                        break
                if vlozeno:
                    break
            
            if not vlozeno:
                rebuffer.append((priorita, film, kat_filmu))

        del buffer[index]

    return rebuffer


def dopln_rebuffer(tabulka, rebuffer, film_to_col, kategorie, max_pocet_radku):
    np.random.shuffle(rebuffer)
    rebuffer.sort(key=lambda x: x[0], reverse = True)
    while rebuffer and any(v > 0 for v in get_volna_mista(tabulka, kategorie, max_pocet_radku).values()):
        priorita, film, kategorie_filmu = rebuffer.pop()
        np.random.shuffle(kategorie_filmu)

        for kat in kategorie_filmu:
            col_index = kategorie.index(kat)
            max_radku = max_pocet_radku.get(kat, 10)
            puvodni_sloupce = film_to_col.get(film, [])

            for radek in range(max_radku):
                if tabulka[radek][col_index] is None:
                    if any(abs(col_index - c) < 3 for c in puvodni_sloupce):
                        continue
                    tabulka[radek][col_index] = film
                    film_to_col.setdefault(film, []).append(col_index)
                    break