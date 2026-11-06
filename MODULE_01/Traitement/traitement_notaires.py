# -*- coding: utf-8 -*-
"""
Traitement de la source notaires.csv — ImmoAnalyse.

Ce module reprend la fonction traiter_notaires() du notebook 01_notaires."""

from pathlib import Path
import sys
import pandas as pd

# Ajouter la racine du projet au chemin de recherche de Python
RACINE_PROJET = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE_PROJET))

import outils as o


def charger_referentiels(dossier_donnees: Path):
    """Charge les référentiels et construit les index utilisés par le traitement."""
    chemin_geo = dossier_donnees / "referentiels" / "referentiel_geographique.csv"
    chemin_cat = dossier_donnees / "referentiels" / "referentiel_categories.csv"

    if not chemin_geo.exists():
        raise FileNotFoundError(f"Référentiel géographique introuvable : {chemin_geo}")
    if not chemin_cat.exists():
        raise FileNotFoundError(f"Référentiel catégories introuvable : {chemin_cat}")

    ref_geo = pd.read_csv(chemin_geo)
    ref_cat = pd.read_csv(chemin_cat)

    idx_regions = o.construire_index(ref_geo["region"].unique())
    idx_villes = o.construire_index(
        ref_geo["ville"].unique(),
        alias={"Dkr": "Dakar"}
    )
    idx_types = o.construire_index_categories(
        zip(ref_cat["categorie"], ref_cat["synonymes"])
    )
    ref_cat_dict = o.construire_ref_categories(
        ref_cat[
            [
                "categorie",
                "prix_min_indicatif",
                "prix_max_indicatif",
                "surface_min_typique",
                "surface_max_typique",
            ]
        ].itertuples(index=False, name=None)
    )
    paires_region_ville = set(zip(ref_geo["region"], ref_geo["ville"]))

    return idx_regions, idx_villes, idx_types, ref_cat_dict, paires_region_ville


_suivre = o.suivre   # fonction partagée (outils.py)


def traiter_notaires(
    brut: pd.DataFrame,
    idx_regions,
    idx_villes,
    idx_types,
    ref_cat_dict,
    paires_region_ville,
    aujourdhui=None,
) -> pd.DataFrame:
    """Nettoie les annonces notaires et retourne toutes les lignes avec leur motif de quarantaine."""
    lignes = []

    for _, r in brut.iterrows():
        corr, avis, quar = [], [], []

        # Identifiant (bloquant)
        id_local = o.normaliser_texte(r["id_acte"])
        if id_local is None:
            quar.append("identifiant absent")

        # Date (bloquante) + date future (bloquante)
        d, e = o.parse_date(r["date_acte"])
        _suivre("date", r["date_acte"], d, e, corr, avis, quar, bloquant=True)
        if d and o.est_future(d, aujourdhui):
            quar.append(f"date future : {d}")

        # Géographie (signalée, jamais corrigée sans preuve)
        region, e_reg = o.canoniser(r["region"], idx_regions)
        _suivre("région", r["region"], region, e_reg, corr, avis, quar, bloquant=False)
        ville, e_ville = o.canoniser(r["ville"], idx_villes)
        _suivre("ville", r["ville"], ville, e_ville, corr, avis, quar, bloquant=False)
        deux_connues = e_reg in ("ok", "corrige") and e_ville in ("ok", "corrige")
        if deux_connues and (region, ville) not in paires_region_ville:
            avis.append(f"ville/région incohérentes : {ville} / {region}")

        # Type de bien (bloquant)
        type_bien, e = o.canoniser(r["type_bien"], idx_types)
        _suivre("type_bien", r["type_bien"], type_bien, e, corr, avis, quar,
                bloquant=o.TYPE_BIEN_INCONNU_BLOQUANT)

        # Montant (bloquant) et surface (bloquante)
        prix, e = o.parse_prix(r["montant_fcfa"])
        _suivre("prix", r["montant_fcfa"], prix, e, corr, avis, quar, bloquant=True)
        surface, e = o.parse_surface(r["superficie"])
        _suivre("surface", r["superficie"], surface, e, corr, avis, quar, bloquant=True)

        # Chambres (signalé)
        #chambres = pd.to_numeric(r["nb_chambres"], errors="coerce")
        #chambres = None if pd.isna(chambres) else int(chambres)

        chambres, etat_chambres = o.en_entier(r["nb_chambres"])

        _suivre("chambres",r["nb_chambres"], chambres,etat_chambres,corr,avis,quar, bloquant=False,)

        # Statut (signalé)
        statut, e = o.normaliser_statut(r["statut"])
        _suivre("statut", r["statut"], statut, e, corr, avis, quar, bloquant=False)

        # Plausibilité (uniquement si les valeurs sont exploitables)
        avis += o.avertissements_plausibilite(
            prix=prix,
            surface=surface,
            type_bien=type_bien,
            type_transaction="vente",
            chambres=chambres,
            ref_cat=ref_cat_dict,
        )

        lignes.append({
            "source": "notaires",
            "id_local": id_local,
            "date": d,
            "type_transaction": "vente",
            "type_bien": type_bien,
            "region": region,
            "ville": ville,
            "prix": prix,
            "surface": surface,
            "chambres": chambres,
            "sdb": None,
            "statut": statut,
            "avertissements": "; ".join(avis),
            "corrections": "; ".join(corr),
            "motif_quarantaine": "; ".join(quar),
        })

    return pd.DataFrame(lignes, index=brut.index)


def executer_traitement(dossier_projet: str | Path):
    """Charge notaires.csv, applique le traitement et retourne (conservees, quarantaine)."""
    dossier_projet = Path(dossier_projet)
    dossier_donnees = dossier_projet / "dossier" / "donnees_extraites" / "immoanalyse_dataset"
    fichier_source = dossier_donnees / "sources" / "notaires.csv"

    if not fichier_source.exists():
        raise FileNotFoundError(f"Fichier source introuvable : {fichier_source}")

    brut = pd.read_csv(fichier_source)
    refs = charger_referentiels(dossier_donnees)
    resultat = traiter_notaires(brut, *refs)

    masque_quarantaine = resultat["motif_quarantaine"].fillna("").str.strip().ne("")
    conservees = resultat.loc[~masque_quarantaine].copy()
    quarantaine = resultat.loc[masque_quarantaine].copy()


    if len(conservees) + len(quarantaine) != len(brut):
        raise AssertionError("Le bilan des lignes notaires est incohérent.")

    # Création du rapport de qualité
    rapport = pd.DataFrame([
        {"indicateur": "lignes_recues", "valeur": len(brut)},
        {"indicateur": "lignes_conservees", "valeur": len(conservees)},
        {"indicateur": "lignes_quarantaine", "valeur": len(quarantaine)},
        {
            "indicateur": "lignes_corrigees_conservees",
            "valeur": conservees["corrections"].fillna("").str.strip().ne("").sum()
        },
        {
            "indicateur": "lignes_conservees_avec_avertissements",
            "valeur": conservees["avertissements"].fillna("").str.strip().ne("").sum()
        },
        {
            "indicateur": "lignes_sans_correction_ni_avertissement",
            "valeur": (
                conservees["corrections"].fillna("").str.strip().eq("")
                & conservees["avertissements"].fillna("").str.strip().eq("")
            ).sum()
        },
    ])

    # Création du dossier de sortie
    dossier_sortie = dossier_projet / "Sortie" / "notaires"
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    # Export des données
    conservees.to_csv(
        dossier_sortie / "notaires_conservees.csv",
        index=False,
        encoding="utf-8-sig"
    )

    quarantaine.to_csv(
        dossier_sortie / "notaires_quarantaine.csv",
        index=False,
        encoding="utf-8-sig"
    )

    rapport.to_csv(
        dossier_sortie / "rapport_notaires.csv",
        index=False,
        encoding="utf-8-sig"
    )

    return conservees, quarantaine, rapport


if __name__ == "__main__":
    RACINE_PROJET = Path(__file__).resolve().parent.parent

    conservees, quarantaine, rapport = executer_traitement(RACINE_PROJET)

    print("Lignes conservées :", len(conservees))
    print("Lignes en quarantaine :", len(quarantaine))
    print("Total :", len(conservees) + len(quarantaine))

    print("\nRapport qualité :")
    print(rapport.to_string(index=False))
