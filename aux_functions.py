import pandas as pd
import numpy as np

prioritni_kategorie = ["Plné velikosti", "Náš výběr", "Náš výběr z internetu","Obsah zdarma", "Pro děti", "Rodinné filmy","Originální produkce", "Seriály"]

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