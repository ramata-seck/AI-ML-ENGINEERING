# -*- coding: utf-8 -*-
"""Traitement de la source particuliers.json — ImmoAnalyse.

Même format que traitement_notaires.py.


Points propres à cette source :
  - JSON imbriqué {annonce: {id, date, localisation: {...}, details: {...}, statut}},
    aplati par aplatir_particuliers() (une valeur null à la place d'un bloc ne plante pas) ;
  - beaucoup de manquants : type_transaction absent ou illisible => quarantaine ;
  - prix et surfaces parfois en texte (« 58.29 millions », « quatre-vingt ») : traités par outils.py ;
  - périodicité des loyers : lue dans le prix (« 250 000 par mois ») ou dans un champ
    `periodicite` s'il existe. Jamais devinée : absente => avertissement.
"""

import json
from pathlib import Path
import pandas as pd
import traitement_commun as tc
from traitement_notaires import charger_referentiels
import sys

# Ajouter la racine du projet au chemin de recherche de Python
RACINE_PROJET = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE_PROJET))
import outils as o

# {colonne après aplatissement : colonne de travail}
CHAMPS_JSON = {
    "annonce_id": "id",
    "annonce_date": "date",
    "annonce_localisation_region": "region",
    "annonce_localisation_ville": "ville",
    "annonce_details_type": "type_bien",
    "annonce_details_transaction": "type_transaction",
    "annonce_details_prix": "prix",
    "annonce_details_surface": "surface",
    "annonce_details_chambres": "chambres",
    "annonce_details_sdb": "sdb",
    "annonce_statut": "statut",
    "annonce_details_periodicite": "periodicite",   # facultatif
}
COLONNES_REQUISES = [c for c in CHAMPS_JSON.values() if c != "periodicite"]


def aplatir_particuliers(donnees_json) -> pd.DataFrame:
    """Aplatit le JSON : une ligne par annonce, les champs absents deviennent vides."""
    plat = pd.json_normalize(donnees_json, sep="_")
    for source, cible in CHAMPS_JSON.items():
        plat[cible] = plat[source] if source in plat.columns else None
    return plat[list(CHAMPS_JSON.values())].copy()


def traiter_particuliers(
    brut: pd.DataFrame,
    idx_regions,
    idx_villes,
    idx_types,
    ref_cat_dict,
    paires_region_ville,
    aujourdhui=None,
) -> pd.DataFrame:
    """Nettoie les annonces de particuliers et retourne toutes les lignes (schéma commun)."""
    lignes = []

    for _, r in brut.iterrows():
        corr, avis, quar = [], [], []

        # 1. Identifiant (bloquant)
        id_local = o.normaliser_texte(r["id"])
        if id_local is None:
            quar.append("identifiant absent")

        # 2. Date (bloquante) + date future (bloquante)
        date, e = o.parse_date(r["date"])
        o.suivre("date", r["date"], date, e, corr, avis, quar, bloquant=True)
        if date and o.est_future(date, aujourdhui):
            quar.append(f"date future : {date}")

        # 3. Type de transaction (bloquant) : vente ou location, avant tout traitement du prix
        transaction, e = o.normaliser_transaction(r["type_transaction"])
        o.suivre("type_transaction", r["type_transaction"], transaction, e,
                 corr, avis, quar, bloquant=True)
        if e not in ("ok", "corrige"):
            transaction = None

        # 4. Géographie (signalée, jamais corrigée sans preuve)
        region, e_reg = o.canoniser(r["region"], idx_regions)
        o.suivre("région", r["region"], region, e_reg, corr, avis, quar)
        ville, e_ville = o.canoniser(r["ville"], idx_villes)
        o.suivre("ville", r["ville"], ville, e_ville, corr, avis, quar)
        deux_connues = e_reg in ("ok", "corrige") and e_ville in ("ok", "corrige")
        if deux_connues and (region, ville) not in paires_region_ville:
            avis.append(f"ville/région incohérentes : {ville} / {region}")

        # 5. Type de bien (voir o.TYPE_BIEN_INCONNU_BLOQUANT)
        type_bien, e = o.canoniser(r["type_bien"], idx_types)
        o.suivre("type_bien", r["type_bien"], type_bien, e, corr, avis, quar,
                 bloquant=o.TYPE_BIEN_INCONNU_BLOQUANT)

        # 6. Prix ou loyer (bloquant), avec périodicité éventuelle dans le texte
        per_prix, _, prix_nettoye = o.extraire_periodicite(r["prix"])
        prix, e = o.parse_prix(prix_nettoye)
        o.suivre("prix", r["prix"], prix, e, corr, avis, quar, bloquant=True)

        # 7. Périodicité des loyers : signalée, jamais devinée
        periodicite = None
        if transaction == "location":
            candidats = set()
            colonne = r.get("periodicite")
            if not o.est_vide(colonne):
                p, _ = o.normaliser_periodicite(colonne)
                if p:
                    candidats.add(p)
            if per_prix:
                candidats.add(per_prix)
            if len(candidats) == 1:
                periodicite = next(iter(candidats))
            elif len(candidats) > 1:
                avis.append("périodicités contradictoires : loyer non évalué")

        # 8. Surface (bloquante) : '1,250' ambigu, 'quatre-vingt' => 80 (correction tracée)
        surface, e = o.parse_surface(r["surface"])
        o.suivre("surface", r["surface"], surface, e, corr, avis, quar, bloquant=True)

        # 9. Chambres et salles de bain (signalées, absence non signalée)
        chambres, e = o.en_entier(r["chambres"])
        if e != "absent":
            o.suivre("chambres", r["chambres"], chambres, e, corr, avis, quar)
        sdb, e = o.en_entier(r["sdb"])
        if e != "absent":
            o.suivre("sdb", r["sdb"], sdb, e, corr, avis, quar)

        # 10. Statut (signalé)
        statut, e = o.normaliser_statut(r["statut"])
        o.suivre("statut", r["statut"], statut, e, corr, avis, quar)

        # 11. Plausibilité (seuils, fourchettes du référentiel, loyer selon la périodicité)
        avis += o.avertissements_plausibilite(
            prix=prix, surface=surface, type_bien=type_bien,
            type_transaction=transaction or "vente", periodicite=periodicite,
            chambres=chambres, sdb=sdb, ref_cat=ref_cat_dict,
        )

        lignes.append({
            "source": "particuliers",
            "id_local": id_local,
            "date": date,
            "type_transaction": transaction,
            "type_bien": type_bien,
            "region": region,
            "ville": ville,
            "prix": prix,
            "surface": surface,
            "chambres": chambres,
            "sdb": sdb,
            "statut": statut,
            "periodicite": periodicite,
            "avertissements": "; ".join(dict.fromkeys(avis)),
            "corrections": "; ".join(dict.fromkeys(corr)),
            "motif_quarantaine": "; ".join(dict.fromkeys(quar)),
            "doublon": "",
        })

    return pd.DataFrame(lignes, index=brut.index, columns=tc.COLONNES_SCHEMA)


def executer_traitement(dossier_projet: str | Path, aujourdhui=None):
    """Charge particuliers.json et retourne (conservees, quarantaine, rapport)."""
    dossier_projet = Path(dossier_projet)
    dossier_donnees = dossier_projet / "dossier" / "donnees_extraites" / "immoanalyse_dataset"
    fichier_source = dossier_donnees / "sources" / "particuliers.json"
    if not fichier_source.exists():
        raise FileNotFoundError(f"Fichier source introuvable : {fichier_source}")

    with open(fichier_source, "r", encoding="utf-8") as fichier:
        donnees_json = json.load(fichier)
    brut = aplatir_particuliers(donnees_json)

    refs = charger_referentiels(dossier_donnees)
    resultat = traiter_particuliers(brut, *refs, aujourdhui=aujourdhui)

    conservees, quarantaine = tc.scinder(resultat)
    conservees = tc.marquer_doublons(conservees)
    rapport = tc.construire_rapport("particuliers", brut, conservees, quarantaine)

    if len(conservees) + len(quarantaine) != len(brut):
        raise AssertionError("Le bilan des lignes particuliers est incohérent.")
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
    dossier_sortie = dossier_projet / "Sortie" / "particuliers"
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    # Export des données
    conservees.to_csv(
        dossier_sortie / "particuliers_conservees.csv",
        index=False,
        encoding="utf-8-sig"
    )

    quarantaine.to_csv(
        dossier_sortie / "particuliers_quarantaine.csv",
        index=False,
        encoding="utf-8-sig"
    )

    rapport.to_csv(
        dossier_sortie / "rapport_particuliers.csv",
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

