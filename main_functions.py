import pandas as pd
import aux_functions as af
import random
import networkx as nx

def get_carousel_data_unique():
    print("\n--- SPOUŠTÍM FÁZI 1: UNIKÁTNÍ FILMY ---")
    df = af.nacti_filmy()
    df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0], errors='coerce')
    df = df[df.iloc[:, 0].notna()]
    df = df[df.iloc[:, 0] < 5]  
    
    kategorie = af.ziskej_kategorie(df)
    tabulka = [["" for _ in range(len(kategorie))] for _ in range(10)]
    film_to_col = {}
    
    celkem_filmu = len(df)
    
    G = nx.DiGraph()
    G.add_node("S", demand=-celkem_filmu) 
    G.add_node("T", demand=celkem_filmu)  
    
    G.add_edge("S", "T", capacity=celkem_filmu, weight=0)
    
    for kat in kategorie:
        kat_node = f"K_{kat}"
        G.add_node(kat_node)
        capacity = af.max_pocet_radku.get(kat, 10)
        G.add_edge(kat_node, "T", capacity=capacity, weight=0)

    for index, row in df.iterrows():
        film = str(row.iloc[1]).strip()
        if pd.isna(film) or film.lower() == "nan" or film == "":
            continue
        
        movie_node = f"M_{index}"
        G.add_node(movie_node)
        priorita = int(row.iloc[0])
        
        if priorita == 1: weight = -100000
        elif priorita == 2: weight = -10000
        elif priorita == 3: weight = -1000
        else: weight = -100
            
        G.add_edge("S", movie_node, capacity=1, weight=weight)
        
        bool_hodnoty = row.iloc[2:].astype(str).str.lower().tolist()
        kat_filmu = [kat for kat, val in zip(kategorie, bool_hodnoty) if val in ["true", "1", "1.0", "ano"]]
        
        for kat in kat_filmu:
            kat_node = f"K_{kat}"
            if kat == "Obsah zdarma": edge_weight = -90
            elif kat == "Pro děti": edge_weight = -80
            elif kat == "Rodinné filmy": edge_weight = -70
            elif kat in af.prioritni_kategorie: edge_weight = -50
            else: edge_weight = 0
                
            G.add_edge(movie_node, kat_node, capacity=1, weight=edge_weight)
            
    try:            
        flow_dict = nx.min_cost_flow(G)
    except Exception as e:
        print(f"CRITICAL ERROR v NetworkX: {e}")
        flow_dict = {}
        
    kat_counts = {kat: 0 for kat in kategorie}
    pouzite_filmy = set()
    
    for index, row in df.iterrows():
        movie_node = f"M_{index}"
        film = str(row.iloc[1]).strip()
        if movie_node in flow_dict:
            for kat_node, flow in flow_dict[movie_node].items():
                if flow > 0 and kat_node.startswith("K_"):
                    kat_name = kat_node.replace("K_", "")
                    col_index = kategorie.index(kat_name)
                    
                    radek_index = kat_counts[kat_name]
                    if radek_index < 10:
                        tabulka[radek_index][col_index] = film
                        film_to_col.setdefault(film, []).append(col_index)
                        kat_counts[kat_name] += 1
                        pouzite_filmy.add(film)
                        
    print(f"Úspěšně přiřazeno {len(pouzite_filmy)} unikátních filmů do {sum(kat_counts.values())} okýnek.")
    
    # OPRAVENÁ ČÁST: Do rebufferu jdou VŠECHNY dostupné filmy, filtr `in pouzite_filmy` byl odstraněn
    rebuffer = []
    for index, row in df.iterrows():
        film = str(row.iloc[1]).strip()
        priorita = int(row.iloc[0])
        
        if pd.isna(film) or film.lower() == "nan" or film == "":
            continue
        
        bool_hodnoty = row.iloc[2:].astype(str).str.lower().tolist()
        kat_filmu = [kat for kat, val in zip(kategorie, bool_hodnoty) if val in ["true", "1", "1.0", "ano"]]
        
        if kat_filmu:
            rebuffer.append((priorita, film, kat_filmu))
    
    random.shuffle(rebuffer)
    print(f"Rebuffer obsahuje {len(rebuffer)} položek (zde jsou všechny filmy pro opakování).")
    
    return tabulka, rebuffer, film_to_col, kategorie, af.max_pocet_radku


def get_carousel_data_additional(tabulka, rebuffer, film_to_col, kategorie, max_pocet_radku):
    print("\n--- SPOUŠTÍM FÁZI 2: DOPLŇOVÁNÍ DĚR ---")
    volna_mista = {}
    for i, kat in enumerate(kategorie):
        max_radku = max_pocet_radku.get(kat, 10)
        volna_mista[kat] = sum(1 for r in range(max_radku) if tabulka[r][i] == "")
        
    celkem_prazdnych = sum(volna_mista.values())
    print(f"Na platformě je {celkem_prazdnych} prázdných míst.")
    
    if not rebuffer or celkem_prazdnych == 0:
        print("Není co doplňovat, rebuffer je prázdný nebo nejsou žádná volná místa.")
        return tabulka
    
    rebuffer.sort(key=lambda x: x[0])
    doplneno_filmu = 0
    
    while rebuffer and sum(volna_mista.values()) > 0:
        priorita, film, kat_filmu = rebuffer.pop(0)
        random.shuffle(kat_filmu)
        
        for kat in kat_filmu:
            if volna_mista.get(kat, 0) > 0:
                col_index = kategorie.index(kat)
                max_radku = max_pocet_radku.get(kat, 10)
                puvodni_sloupce = film_to_col.get(film, [])
                
                # Tvoje podmínka rozestupu - nedovolí vložit film, pokud už je moc blízko
                if any(abs(col_index - c) < 3 for c in puvodni_sloupce):
                    continue
                
                for radek in range(max_radku):
                    if tabulka[radek][col_index] == "":
                        tabulka[radek][col_index] = film
                        film_to_col.setdefault(film, []).append(col_index)
                        volna_mista[kat] -= 1
                        doplneno_filmu += 1
                        break
                break
            
    print(f"Úspěšně doplněno {doplneno_filmu} filmů z rebufferu.")
    return tabulka