"""Pipeline global de nettoyage des données — ImmoAnalyse."""

from pathlib import Path
import pandas as pd

import traitement_commun as tc
from traitement_plateforme import executer_traitement as traiter_plateforme
from traitement_historique import executer_traitement as traiter_historique
from traitement_particuliers import executer_traitement as traiter_particuliers
from traitement_notaires import executer_traitement as traiter_notaires
from traitement_agence import executer_traitement as traiter_agence


def executer_pipeline(dossier_projet):
    """Exécute les cinq traitements et regroupe leurs résultats."""

    dossier_projet = Path(dossier_projet)

    traitements = {
        "plateforme": traiter_plateforme,
        "historique": traiter_historique,
        "particuliers": traiter_particuliers,
        "notaires": traiter_notaires,
        "agence": traiter_agence,
    }

    donnees_conservees = []
    donnees_quarantaine = []
    rapports = []

    for nom, fonction in traitements.items():
        print(f"\n--- Traitement : {nom} ---")

        conservees, quarantaine, rapport = fonction(dossier_projet)

        donnees_conservees.append(conservees)
        donnees_quarantaine.append(quarantaine)
        rapports.append(rapport)

        print("Conservées :", len(conservees))
        print("Quarantaine :", len(quarantaine))

    # Regroupement des résultats
    global_conservees = pd.concat(donnees_conservees, ignore_index=True)
    global_quarantaine = pd.concat(donnees_quarantaine, ignore_index=True)
    global_rapport = pd.concat(rapports, ignore_index=True)

    # Vérification du bilan global
    total_recu = len(global_conservees) + len(global_quarantaine)

    if total_recu != sum(
        int(rapport.loc[rapport["indicateur"] == "lignes_recues", "valeur"].iloc[0])
        for rapport in rapports
    ):
        raise AssertionError("Le bilan global des lignes est incohérent.")


    # Création du dossier de sortie global
    dossier_sortie = dossier_projet / "Sortie"
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    # Export des données propres
    global_conservees.to_csv(
        dossier_sortie / "donnees_propres.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Export de la quarantaine
    global_quarantaine.to_csv(
        dossier_sortie / "quarantaine.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Export du rapport qualité
    global_rapport.to_csv(
        dossier_sortie / "rapport_qualite.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nFichiers globaux générés dans : {dossier_sortie}")


    return global_conservees, global_quarantaine, global_rapport


if __name__ == "__main__":
    RACINE_PROJET = Path(__file__).resolve().parent.parent

    conservees, quarantaine, rapport = executer_pipeline(RACINE_PROJET)

    print("\n========== BILAN GLOBAL ==========")
    print("Lignes conservées :", len(conservees))
    print("Lignes en quarantaine :", len(quarantaine))
    print("Total :", len(conservees) + len(quarantaine))

