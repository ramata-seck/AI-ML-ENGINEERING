# -*- coding: utf-8 -*-
"""Traitement de la source import_historique.csv — ImmoAnalyse.

Points propres à cette source :
  - CSV séparé par ';', en latin-1 (le lecteur essaie UTF-8 puis latin-1) ;
  - tout est lu en texte : prix « 26 620 000 », surfaces « 1,250 », IDs courts ;
  - dates par o.parse_date (comme les autres sources) : les dates JJ/MM/AAAA dont le jour
    et le mois sont ≤ 12 sont converties mais SIGNALÉES « ambigu » ;
  - c'est un historique de ventes : type_transaction = vente, statut = Vendu (hypothèse
    notée dans DECISIONS.md).
"""

from pathlib import Path
import pandas as pd
import traitement_commun as tc
from traitement_notaires import charger_referentiels

import sys

# Ajouter la racine du projet au chemin de recherche de Python
RACINE_PROJET = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE_PROJET))
import outils as o

COLONNES_REQUISES = [
    "ID", "DateVente", "Region", "Ville", "TypeBien", "Prix", "Surface", "Chambres", "SallesBain",
]


def traiter_import_historique(
    brut: pd.DataFrame,
    idx_regions,
    idx_villes,
    idx_types,
    ref_cat_dict,
    paires_region_ville,
    aujourdhui=None,
) -> pd.DataFrame:
    """Nettoie l'historique et retourne toutes les lignes (schéma commun)."""
    lignes = []

    for _, r in brut.iterrows():
        corr, avis, quar = [], [], []

        # 1. Identifiant (bloquant)
        id_local = o.normaliser_texte(r["ID"])
        if id_local is None:
            quar.append("identifiant absent")

        # 2. Date de vente (bloquante) + date future (bloquante)
        date, e = o.parse_date(r["DateVente"])
        o.suivre("date", r["DateVente"], date, e, corr, avis, quar, bloquant=True)
        if date and o.est_future(date, aujourdhui):
            quar.append(f"date future : {date}")

        # 3. Géographie (signalée, jamais corrigée sans preuve)
        region, e_reg = o.canoniser(r["Region"], idx_regions)
        o.suivre("région", r["Region"], region, e_reg, corr, avis, quar)
        ville, e_ville = o.canoniser(r["Ville"], idx_villes)
        o.suivre("ville", r["Ville"], ville, e_ville, corr, avis, quar)
        deux_connues = e_reg in ("ok", "corrige") and e_ville in ("ok", "corrige")
        if deux_connues and (region, ville) not in paires_region_ville:
            avis.append(f"ville/région incohérentes : {ville} / {region}")

        # 4. Type de bien (voir o.TYPE_BIEN_INCONNU_BLOQUANT)
        type_bien, e = o.canoniser(r["TypeBien"], idx_types)
        o.suivre("type_bien", r["TypeBien"], type_bien, e, corr, avis, quar,
                 bloquant=o.TYPE_BIEN_INCONNU_BLOQUANT)

        # 5. Prix (bloquant) et surface (bloquante)
        prix, e = o.parse_prix(r["Prix"])
        o.suivre("prix", r["Prix"], prix, e, corr, avis, quar, bloquant=True)
        surface, e = o.parse_surface(r["Surface"])
        o.suivre("surface", r["Surface"], surface, e, corr, avis, quar, bloquant=True)

        # 6. Chambres et salles de bain (signalées, absence non signalée)
        chambres, e = o.en_entier(r["Chambres"])
        if e != "absent":
            o.suivre("chambres", r["Chambres"], chambres, e, corr, avis, quar)
        sdb, e = o.en_entier(r["SallesBain"])
        if e != "absent":
            o.suivre("sdb", r["SallesBain"], sdb, e, corr, avis, quar)

        # 7. Plausibilité (seuils + fourchettes du référentiel)
        avis += o.avertissements_plausibilite(
            prix=prix, surface=surface, type_bien=type_bien,
            type_transaction="vente", chambres=chambres, sdb=sdb, ref_cat=ref_cat_dict,
        )

        lignes.append({
            "source": "import_historique",
            "id_local": id_local,
            "date": date,
            "type_transaction": "vente",
            "type_bien": type_bien,
            "region": region,
            "ville": ville,
            "prix": prix,
            "surface": surface,
            "chambres": chambres,
            "sdb": sdb,
            "statut": "Vendu",
            "periodicite": None,
            "avertissements": "; ".join(dict.fromkeys(avis)),
            "corrections": "; ".join(dict.fromkeys(corr)),
            "motif_quarantaine": "; ".join(dict.fromkeys(quar)),
            "doublon": "",
        })

    return pd.DataFrame(lignes, index=brut.index, columns=tc.COLONNES_SCHEMA)


def executer_traitement(dossier_projet: str | Path, aujourdhui=None):
    """Charge import_historique.csv et retourne (conservees, quarantaine, rapport)."""
    dossier_projet = Path(dossier_projet)
    dossier_donnees = dossier_projet / "dossier" / "donnees_extraites" / "immoanalyse_dataset"
    fichier_source = dossier_donnees / "sources" / "import_historique.csv"
    if not fichier_source.exists():
        raise FileNotFoundError(f"Fichier source introuvable : {fichier_source}")

    brut, _ = tc.lire_csv(fichier_source, sep=";")
    manquantes = [c for c in COLONNES_REQUISES if c not in brut.columns]
    if manquantes:
        raise ValueError(f"Colonnes absentes dans import_historique.csv : {manquantes}")

    refs = charger_referentiels(dossier_donnees)
    resultat = traiter_import_historique(brut, *refs, aujourdhui=aujourdhui)

    conservees, quarantaine = tc.scinder(resultat)
    conservees = tc.marquer_doublons(conservees)
    rapport = tc.construire_rapport("import_historique", brut, conservees, quarantaine)

    if len(conservees) + len(quarantaine) != len(brut):
        raise AssertionError("Le bilan des lignes historique est incohérent.")
    return conservees, quarantaine, rapport


if __name__ == "__main__":
    racine = Path(__file__).resolve().parent.parent
    conservees, quarantaine, rapport = executer_traitement(racine)
    print("Lignes conservées :", len(conservees))
    print("Lignes en quarantaine :", len(quarantaine))
    print("Total :", len(conservees) + len(quarantaine))
    print(rapport.to_string(index=False))
