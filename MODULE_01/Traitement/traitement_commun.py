# -*- coding: utf-8 -*-
"""Fonctions communes aux modules de traitement des sources — ImmoAnalyse.

Contient seulement ce qui ne dépend pas d'une source : lecture d'un CSV, séparation
conservées / quarantaine, marquage des doublons et rapport chiffré.
"""

from pathlib import Path
import pandas as pd
import sys

# Ajouter la racine du projet au chemin de recherche de Python
RACINE_PROJET = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE_PROJET))
import outils as o

# Schéma commun produit par chaque source
COLONNES_SCHEMA = [
    "source", "id_local", "date", "type_transaction", "type_bien",
    "region", "ville", "prix", "surface", "chambres", "sdb", "statut",
    "periodicite", "avertissements", "corrections", "motif_quarantaine", "doublon",
]

# Colonnes comparées pour décider qu'une ligne est un doublon exact (id compris)
COLONNES_COMPARAISON = [
    "source", "id_local", "date", "type_transaction", "type_bien",
    "region", "ville", "prix", "surface", "chambres", "sdb", "statut", "periodicite",
]


def lire_csv(fichier, sep):
    """Lit un CSV entièrement en texte (aucune conversion automatique).

    Essaie UTF-8 puis latin-1. Renvoie (DataFrame, encodage utilisé).
    """
    for encodage in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(fichier, sep=sep, encoding=encodage, dtype=str), encodage
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Encodage illisible : {fichier}")


def scinder(resultat):
    """Sépare les lignes sans motif de quarantaine (conservées) de celles avec motif."""
    masque = resultat["motif_quarantaine"].fillna("").str.strip().ne("")
    return resultat.loc[~masque].copy(), resultat.loc[masque].copy()


def marquer_doublons(conservees):
    """Marque (sans supprimer) les doublons à l'intérieur d'une source.

    - doublon_exact : toutes les colonnes de COLONNES_COMPARAISON identiques à une ligne précédente
    - conflit_id    : même id_local mais valeurs différentes (à arbitrer, jamais supprimé seul)
    La suppression éventuelle se décide à l'étape de fusion, avec la même stratégie pour toutes les sources.
    """
    df = conservees.copy()
    df["doublon"] = ""
    if df.empty:
        return df

    cles = [c for c in COLONNES_COMPARAISON if c in df.columns]
    exact = df.duplicated(subset=cles, keep="first")
    versions = (
        df.drop_duplicates(subset=cles)
        .dropna(subset=["id_local"])
        .groupby("id_local")
        .size()
    )
    conflit = df["id_local"].isin(versions[versions > 1].index) & ~exact

    df.loc[exact, "doublon"] = "doublon_exact"
    df.loc[conflit, "doublon"] = "conflit_id"

    messages = {
        "doublon_exact": "doublon exact d'une ligne précédente de la même source",
        "conflit_id": "même identifiant avec des valeurs différentes (conflit)",
    }
    for etiquette, message in messages.items():
        masque = df["doublon"] == etiquette
        df.loc[masque, "avertissements"] = (
            df.loc[masque, "avertissements"].fillna("").astype(str)
            .map(lambda a: f"{a}; {message}" if a else message)
        )
    return df


def construire_rapport(nom, brut, conservees, quarantaine):
    """Rapport chiffré d'une source (DataFrame indicateur / valeur).

    Taux de conformité : lignes sans correction ni avertissement / lignes REÇUES.
    Les lignes en quarantaine ne sont donc jamais comptées comme conformes.
    """
    recues = len(brut)
    a_corr = conservees["corrections"].fillna("").ne("")
    a_avis = conservees["avertissements"].fillna("").ne("")
    conformes = int((~a_corr & ~a_avis).sum())
    doublon = conservees["doublon"] if "doublon" in conservees.columns else pd.Series(dtype=str)

    lignes = [
        ("source", nom),
        ("lignes_recues", recues),
        ("lignes_conservees", len(conservees)),
        ("lignes_quarantaine", len(quarantaine)),
        ("lignes_corrigees_conservees", int(a_corr.sum())),
        ("lignes_conservees_avec_avertissement", int(a_avis.sum())),
        ("lignes_entierement_conformes", conformes),
        ("taux_conformes_pct (denominateur : lignes recues)",
         round(100 * conformes / recues, 1) if recues else None),
        ("doublons_exacts_dans_le_fichier_brut", int(brut.duplicated().sum())),
        ("doublons_exacts_apres_normalisation", int((doublon == "doublon_exact").sum())),
        ("conflits_meme_identifiant", int((doublon == "conflit_id").sum())),
    ]
    for colonne in brut.columns:
        lignes.append((f"manquantes__{colonne}", int(brut[colonne].map(o.est_vide).sum())))
    return pd.DataFrame(lignes, columns=["indicateur", "valeur"])
