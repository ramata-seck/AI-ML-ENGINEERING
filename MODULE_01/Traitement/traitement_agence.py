# -*- coding: utf-8 -*-
"""Traitement de la source agence_teranga.xlsx — ImmoAnalyse.


"""

from pathlib import Path
import numpy as np
import pandas as pd
from traitement_notaires import charger_referentiels
import sys

# Ajouter la racine du projet au chemin de recherche de Python
RACINE_PROJET = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE_PROJET))
import outils as o


COLONNES_REQUISES = [
    "Code", "Date", "Region", "Ville", "Type", "Prix_FCFA",
    "Surface_m2", "Chambres", "SDB", "Statut", "Commercial",
]


def traiter_agence_teranga(
    df: pd.DataFrame,
    idx_regions,
    idx_villes,
    idx_types,
    ref_cat_dict,
    paires_region_ville,
):
    """Nettoie les données de l'agence sans modifier le DataFrame original.

    Retourne (donnees_conservees, quarantaine, rapport).
    Les lignes avec erreurs bloquantes sont mises en quarantaine.
    Les valeurs atypiques non bloquantes restent conservées avec avertissement.
    """
    manquantes = [c for c in COLONNES_REQUISES if c not in df.columns]
    if manquantes:
        raise ValueError(f"Colonnes absentes dans agence_teranga.xlsx : {manquantes}")

    donnees = df.copy(deep=True)
    conservees, quarantaine = [], []
    date_du_jour = pd.Timestamp.today().normalize()

    for _, ligne in donnees.iterrows():
        resultat = ligne.to_dict()
        corrections, avertissements, motifs = [], [], []

        # 1. Code : champ bloquant
        code = ligne["Code"]
        if o.est_vide(code):
            motifs.append("Code du bien manquant")
        else:
            code_normalise = str(code).strip()
            resultat["Code"] = code_normalise
            if str(code) != code_normalise:
                corrections.append("Code normalisé")

        # 2. Date : champ bloquant
        date_brute = ligne["Date"]
        date_convertie, statut_date = o.parse_date(date_brute)

        if statut_date in ("absent", "invalide", "inconnu") or date_convertie is None:
            motifs.append(f"Date absente ou invalide : {date_brute}")
        else:
            date_convertie = pd.to_datetime(date_convertie, errors="coerce")
            if pd.isna(date_convertie):
                motifs.append(f"Date impossible à interpréter : {date_brute}")
            elif date_convertie.normalize() > date_du_jour:
                motifs.append(f"Date future : {date_brute}")
            else:
                resultat["Date"] = date_convertie.strftime("%Y-%m-%d")
                # Correction seulement si le format a vraiment changé (pas pour une date déjà propre)
                if statut_date in ("corrige", "ambigu"):
                    corrections.append("Date normalisée")
                if statut_date == "ambigu":
                    avertissements.append(f"Date interprétée selon la convention JJ/MM/AAAA : {date_brute}")

        # 3. Région et ville : ramenées au référentiel, avertissements seulement
        region, statut_region = o.canoniser(ligne["Region"], idx_regions)
        if statut_region == "absent":
            avertissements.append("Region manquante")
        else:
            resultat["Region"] = region
            if statut_region == "corrige":
                corrections.append(f"Region : '{ligne['Region']}' -> '{region}'")
            elif statut_region == "inconnu":
                avertissements.append(f"Region hors référentiel : {ligne['Region']}")

        ville, statut_ville = o.canoniser(ligne["Ville"], idx_villes)
        if statut_ville == "absent":
            avertissements.append("Ville manquante")
        else:
            resultat["Ville"] = ville
            if statut_ville == "corrige":
                corrections.append(f"Ville : '{ligne['Ville']}' -> '{ville}'")
            elif statut_ville == "inconnu":
                avertissements.append(f"Ville hors référentiel : {ligne['Ville']}")

        # Cohérence ville/région : signalée, jamais corrigée sans preuve
        deux_connues = statut_region in ("ok", "corrige") and statut_ville in ("ok", "corrige")
        if deux_connues and (region, ville) not in paires_region_ville:
            avertissements.append(f"ville/région incohérentes : {ville} / {region}")

        # 4. Type de bien : normalisation via le référentiel, catégorie inconnue signalée
        type_brut = ligne["Type"]
        type_final, statut_type = o.canoniser(type_brut, idx_types)
        if statut_type == "absent":
            avertissements.append("Type de bien manquant")
        else:
            resultat["Type"] = type_final
            if statut_type == "corrige":
                corrections.append("Type de bien normalisé")
            elif statut_type == "inconnu":
                message = f"Type de bien absent du référentiel : {type_brut}"
                # Règle commune à toutes les sources : voir o.TYPE_BIEN_INCONNU_BLOQUANT
                (motifs if o.TYPE_BIEN_INCONNU_BLOQUANT else avertissements).append(message)

        # 5. Prix : absence, valeur invalide ou <= 0 bloquante
        #    (les seuils min/max sont vérifiés plus bas dans avertissements_plausibilite)
        prix_brut = ligne["Prix_FCFA"]
        prix_converti, statut_prix = o.parse_prix(prix_brut)
        if statut_prix in ("absent", "invalide", "inconnu") or prix_converti is None:
            motifs.append(f"Prix absent ou invalide : {prix_brut}")
        elif prix_converti <= 0:
            motifs.append(f"Prix nul ou négatif : {prix_brut}")
        else:
            resultat["Prix_FCFA"] = prix_converti
            if statut_prix == "corrige":
                corrections.append("Prix corrigé")

        # 6. Surface : absence, valeur invalide ou <= 0 bloquante
        surface_brute = ligne["Surface_m2"]
        surface_convertie, statut_surface = o.parse_surface(surface_brute)
        if statut_surface in ("absent", "invalide", "inconnu") or surface_convertie is None:
            motifs.append(f"Surface absente ou invalide : {surface_brute}")
        elif surface_convertie <= 0:
            motifs.append(f"Surface nulle ou négative : {surface_brute}")
        else:
            resultat["Surface_m2"] = surface_convertie
            if statut_surface == "corrige":
                corrections.append("Surface corrigée")
            elif statut_surface == "ambigu":
                avertissements.append(f"Surface ambiguë : {surface_brute}")

        # 7. Chambres et salles de bain : anomalies signalées, non bloquantes
        for colonne in ("Chambres", "SDB"):
            valeur = ligne[colonne]
            if o.est_vide(valeur):
                avertissements.append(f"{colonne} manquant")
                continue
            try:
                nombre = float(valeur)
                if not np.isfinite(nombre) or not nombre.is_integer():
                    avertissements.append(f"{colonne} non entier : {valeur}")
                elif nombre < 0:
                    avertissements.append(f"{colonne} négatif : {valeur}")
                else:
                    resultat[colonne] = int(nombre)
            except (ValueError, TypeError):
                avertissements.append(f"{colonne} invalide : {valeur}")

        # 8. Statut : même règle que notaires (Vente conclue, Acte signé -> Vendu)
        statut_brut = ligne["Statut"]
        statut_final, etat_statut = o.normaliser_statut(statut_brut)
        if etat_statut == "absent":
            avertissements.append("Statut manquant")
        else:
            resultat["Statut"] = statut_final
            if etat_statut == "corrige":
                corrections.append("Statut normalisé")
            elif etat_statut == "inconnu":
                avertissements.append(f"Statut inconnu : {statut_brut}")

        # 9. Commercial : champ informatif
        commercial = ligne["Commercial"]
        if o.est_vide(commercial):
            avertissements.append("Commercial manquant")
        else:
            resultat["Commercial"] = str(commercial).strip()

        # 10. Avertissements métier communs (seuils + fourchettes du référentiel)
        chambres = resultat.get("Chambres")
        sdb = resultat.get("SDB")
        try:
            chambres = int(chambres) if not o.est_vide(chambres) else None
        except (ValueError, TypeError):
            chambres = None
        try:
            sdb = int(sdb) if not o.est_vide(sdb) else None
        except (ValueError, TypeError):
            sdb = None

        avertissements.extend(
            o.avertissements_plausibilite(
                prix=prix_converti,
                surface=surface_convertie,
                type_bien=resultat.get("Type"),
                type_transaction="vente",
                chambres=chambres,
                sdb=sdb,
                ref_cat=ref_cat_dict,
            )
        )

        resultat["corrections"] = " ; ".join(corrections)
        resultat["avertissements"] = " ; ".join(dict.fromkeys(avertissements))
        resultat["motif_quarantaine"] = " ; ".join(motifs)

        if motifs:
            quarantaine.append(resultat)
        else:
            conservees.append(resultat)

    df_conservees = pd.DataFrame(conservees, columns=list(donnees.columns) + [
        c for c in ("corrections", "avertissements", "motif_quarantaine")
        if c not in donnees.columns
    ])
    df_quarantaine = pd.DataFrame(quarantaine, columns=df_conservees.columns)

    rapport = pd.DataFrame([
        {"indicateur": "lignes_recues", "valeur": len(donnees)},
        {"indicateur": "lignes_conservees", "valeur": len(df_conservees)},
        {"indicateur": "lignes_quarantaine", "valeur": len(df_quarantaine)},
        {"indicateur": "lignes_corrigees_conservees",
         "valeur": int(df_conservees["corrections"].ne("").sum()) if len(df_conservees) else 0},
        {"indicateur": "lignes_conservees_avec_avertissements",
         "valeur": int(df_conservees["avertissements"].ne("").sum()) if len(df_conservees) else 0},
        {"indicateur": "lignes_sans_correction_ni_avertissement",
         "valeur": int((df_conservees["corrections"].eq("") &
                        df_conservees["avertissements"].eq("")).sum()) if len(df_conservees) else 0},
    ])

    assert len(df_conservees) + len(df_quarantaine) == len(donnees)
    return df_conservees, df_quarantaine, rapport


def harmoniser_agence(df: pd.DataFrame) -> pd.DataFrame:
    """Convertit les noms de colonnes agence vers le schéma canonique global."""
    correspondance = {
        "Code": "id_local",
        "Date": "date",
        "Region": "region",
        "Ville": "ville",
        "Type": "type_bien",
        "Prix_FCFA": "prix",
        "Surface_m2": "surface",
        "Chambres": "chambres",
        "SDB": "sdb",
        "Statut": "statut",
    }
    resultat = df.rename(columns=correspondance).copy()
    resultat["source"] = "agence_teranga"
    resultat["type_transaction"] = "vente"
    colonnes = [
        "source", "id_local", "date", "type_transaction", "type_bien",
        "region", "ville", "prix", "surface", "chambres", "sdb", "statut",
        "avertissements", "corrections", "motif_quarantaine",
    ]
    for colonne in colonnes:
        if colonne not in resultat.columns:
            resultat[colonne] = None
    return resultat[colonnes]


def executer_traitement(dossier_projet: str | Path):
    """Charge, traite et sépare agence_teranga.xlsx."""
    dossier_projet = Path(dossier_projet)
    dossier_donnees = dossier_projet / "dossier" / "donnees_extraites" / "immoanalyse_dataset"
    fichier_source = dossier_donnees / "sources" / "agence_teranga.xlsx"
    if not fichier_source.exists():
        raise FileNotFoundError(f"Fichier source introuvable : {fichier_source}")

    # TODO : le fichier a 2 feuilles. Ici seule la 1re est lue ; à compléter
    # une fois le contenu de la 2e feuille examiné (pd.ExcelFile(...).sheet_names).
    brut = pd.read_excel(fichier_source)
    refs = charger_referentiels(dossier_donnees)
    conservees, quarantaine, rapport = traiter_agence_teranga(brut, *refs)

    
    # Création du dossier de sortie
    dossier_sortie = dossier_projet / "Sortie" / "agence_teranga"
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    # Export des données conservées
    conservees.to_csv(
        dossier_sortie / "agence_teranga_conservees.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Export des données en quarantaine
    quarantaine.to_csv(
        dossier_sortie / "agence_teranga_quarantaine.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Export du rapport de qualité
    rapport.to_csv(
        dossier_sortie / "rapport_agence_teranga.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nFichiers générés dans : {dossier_sortie}")

    #return conservees, quarantaine,rapport
    #Harmonisation destinée à la consolidation multi-sources.
    return ( harmoniser_agence(conservees), harmoniser_agence(quarantaine), rapport, )


if __name__ == "__main__":
    racine = Path(__file__).resolve().parents[1]
    conservees, quarantaine, rapport = executer_traitement(racine)
    print("Lignes conservées :", len(conservees))
    print("Lignes en quarantaine :", len(quarantaine))
    print("Total :", len(conservees) + len(quarantaine))
    print(rapport.to_string(index=False))
