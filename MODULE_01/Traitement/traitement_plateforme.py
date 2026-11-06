# -*- coding: utf-8 -*-
"""Traitement de la source plateforme_immo_sn.csv — ImmoAnalyse.

Même format que traitement_notaires.py : charger les référentiels, traiter ligne par
ligne, séparer, puis rapport

Points propres à cette source :
  - ventes ET locations : le type de transaction est normalisé avant le prix ;
  - périodicité des loyers lue dans une mention EXPLICITE (colonne, prix, devise, puis
    description en dernier recours). Jamais devinée : absente => avertissement ;
  - devise autre que FCFA => quarantaine (aucune conversion de change possible) ;
  - date future => quarantaine (comme notaires et agence) ;
  - `pieces` est utilisé comme `chambres` (hypothèse notée dans DECISIONS.md).
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
    "ref_plateforme", "date_mise_en_ligne", "type_transaction", "categorie",
    "region", "commune", "prix", "devise", "surface", "pieces", "sdb", "statut",
]
# Colonnes facultatives lues si elles existent : quartier, description, date_expiration, periodicite


def _chercher_periodicite(ligne, per_prix, per_devise):
    """Renvoie (periodicite, origine, contradiction).

    Ordre de recherche : colonne `periodicite`, prix, devise, puis description (dernier recours).
    """
    candidats = []
    colonne = ligne.get("periodicite")
    if not o.est_vide(colonne):
        p, _ = o.normaliser_periodicite(colonne)
        if p:
            candidats.append((p, "colonne periodicite"))
    if per_prix:
        candidats.append((per_prix, "prix"))
    if per_devise:
        candidats.append((per_devise, "devise"))
    if not candidats:
        p, _, _ = o.extraire_periodicite(ligne.get("description"))
        if p:
            candidats.append((p, "description"))

    valeurs = {p for p, _ in candidats}
    if len(valeurs) == 1:
        return candidats[0][0], candidats[0][1], False
    return None, None, len(valeurs) > 1


def traiter_plateforme_immo_sn(
    brut: pd.DataFrame,
    idx_regions,
    idx_villes,
    idx_types,
    ref_cat_dict,
    paires_region_ville,
    aujourdhui=None,
) -> pd.DataFrame:
    """Nettoie les annonces de la plateforme et retourne toutes les lignes (schéma commun)."""
    lignes = []

    for _, r in brut.iterrows():
        corr, avis, quar = [], [], []

        # 1. Identifiant (bloquant)
        id_local = o.normaliser_texte(r["ref_plateforme"])
        if id_local is None:
            quar.append("identifiant absent")

        # 2. Date de mise en ligne (bloquante) + date future (bloquante)
        date, e = o.parse_date(r["date_mise_en_ligne"])
        o.suivre("date", r["date_mise_en_ligne"], date, e, corr, avis, quar, bloquant=True)
        if date and o.est_future(date, aujourdhui):
            quar.append(f"date future : {date}")

        # 3. Date d'expiration (facultative, signalée seulement)
        brute_exp = r.get("date_expiration")
        expiration, e_exp = o.parse_date(brute_exp)
        if e_exp == "invalide":
            avis.append(f"date_expiration invalide : '{brute_exp}'")
        elif expiration and date and expiration < date:
            avis.append("date_expiration antérieure à la mise en ligne")

        # 4. Type de transaction (bloquant) : vente ou location, avant tout traitement du prix
        transaction, e = o.normaliser_transaction(r["type_transaction"])
        o.suivre("type_transaction", r["type_transaction"], transaction, e,
                 corr, avis, quar, bloquant=True)
        if e not in ("ok", "corrige"):
            transaction = None

        # 5. Géographie (signalée, jamais corrigée sans preuve)
        region, e_reg = o.canoniser(r["region"], idx_regions)
        o.suivre("région", r["region"], region, e_reg, corr, avis, quar)
        ville, e_ville = o.canoniser(r["commune"], idx_villes)
        o.suivre("ville", r["commune"], ville, e_ville, corr, avis, quar)
        deux_connues = e_reg in ("ok", "corrige") and e_ville in ("ok", "corrige")
        if deux_connues and (region, ville) not in paires_region_ville:
            avis.append(f"ville/région incohérentes : {ville} / {region}")

        # 6. Catégorie (voir o.TYPE_BIEN_INCONNU_BLOQUANT)
        type_bien, e = o.canoniser(r["categorie"], idx_types)
        o.suivre("type_bien", r["categorie"], type_bien, e, corr, avis, quar,
                 bloquant=o.TYPE_BIEN_INCONNU_BLOQUANT)

        # 7. Périodicité : mention explicite dans le prix et la devise
        per_prix, _, prix_nettoye = o.extraire_periodicite(r["prix"])
        per_devise, _, devise_nettoyee = o.extraire_periodicite(r["devise"])

        # 8. Devise : FCFA seulement, aucune conversion
        devise, e = o.normaliser_devise(devise_nettoyee)
        if e == "absent":
            avis.append("devise absente : FCFA supposé")
        elif e == "inconnu":
            quar.append(f"devise non FCFA : '{r['devise']}'")

        # 9. Prix ou loyer (bloquant)
        prix, e = o.parse_prix(prix_nettoye)
        o.suivre("prix", r["prix"], prix, e, corr, avis, quar, bloquant=True)

        # 10. Périodicité des loyers : signalée, jamais devinée
        periodicite = None
        if transaction == "location":
            periodicite, origine, contradiction = _chercher_periodicite(r, per_prix, per_devise)
            if contradiction:
                avis.append("périodicités contradictoires : loyer non évalué")
            elif periodicite and origine in ("description", "colonne periodicite"):
                corr.append(f"périodicité '{periodicite}' lue dans {origine}")

        # 11. Surface (bloquante). Une lecture ambiguë résolue reste signalée.
        surface, e = o.parse_surface(r["surface"])
        o.suivre("surface", r["surface"], surface, e, corr, avis, quar, bloquant=True)

        # 12. Chambres (colonne `pieces`) et salles de bain : signalées, absence non signalée
        chambres, e = o.en_entier(r["pieces"])
        if e != "absent":
            o.suivre("chambres", r["pieces"], chambres, e, corr, avis, quar)
        sdb, e = o.en_entier(r["sdb"])
        if e != "absent":
            o.suivre("sdb", r["sdb"], sdb, e, corr, avis, quar)

        # 13. Statut (signalé)
        statut, e = o.normaliser_statut(r["statut"])
        o.suivre("statut", r["statut"], statut, e, corr, avis, quar)

        # 14. Plausibilité (seuils, fourchettes du référentiel, loyer selon la périodicité)
        avis += o.avertissements_plausibilite(
            prix=prix, surface=surface, type_bien=type_bien,
            type_transaction=transaction or "vente", periodicite=periodicite,
            chambres=chambres, sdb=sdb, ref_cat=ref_cat_dict,
        )

        lignes.append({
            "source": "plateforme_immo_sn",
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
    """Charge plateforme_immo_sn.csv et retourne (conservees, quarantaine, rapport)."""
    dossier_projet = Path(dossier_projet)
    dossier_donnees = dossier_projet / "dossier" / "donnees_extraites" / "immoanalyse_dataset"
    fichier_source = dossier_donnees / "sources" / "plateforme_immo_sn.csv"
    if not fichier_source.exists():
        raise FileNotFoundError(f"Fichier source introuvable : {fichier_source}")

    brut, _ = tc.lire_csv(fichier_source, sep=";")
    manquantes = [c for c in COLONNES_REQUISES if c not in brut.columns]
    if manquantes:
        raise ValueError(f"Colonnes absentes dans plateforme_immo_sn.csv : {manquantes}")

    refs = charger_referentiels(dossier_donnees)
    resultat = traiter_plateforme_immo_sn(brut, *refs, aujourdhui=aujourdhui)

    conservees, quarantaine = tc.scinder(resultat)
    conservees = tc.marquer_doublons(conservees)
    rapport = tc.construire_rapport("plateforme_immo_sn", brut, conservees, quarantaine)

    if len(conservees) + len(quarantaine) != len(brut):
        raise AssertionError("Le bilan des lignes plateforme est incohérent.")
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
    dossier_sortie = dossier_projet / "Sortie" / "plateforme"
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    # Export des données
    conservees.to_csv(
        dossier_sortie / "plateforme_conservees.csv",
        index=False,
        encoding="utf-8-sig"
    )

    quarantaine.to_csv(
        dossier_sortie / "plateforme_quarantaine.csv",
        index=False,
        encoding="utf-8-sig"
    )

    rapport.to_csv(
        dossier_sortie / "rapport_plateforme.csv",
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
