"""Tests des modules de traitement (plateforme, historique, particuliers, doublons).

Cas conformes, invalides et limites. Lancer : pytest -v
Les référentiels sont reconstruits ici en petit, pour que les tests ne dépendent d'aucun fichier.
"""
from datetime import date

import pandas as pd
import pytest

import outils as o

from pathlib import Path
import sys

RACINE_PROJET = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(RACINE_PROJET))
sys.path.insert(0, str(RACINE_PROJET / "Traitement"))

import traitement_commun as tc
import traitement_historique as th
import traitement_particuliers as tpa
import traitement_plateforme as tp

AUJOURDHUI = date(2026, 10, 30)

GEO = [("Dakar", "Dakar"), ("Dakar", "Pikine"), ("Thiès", "Thiès"), ("Thiès", "Mbour"),
       ("Ziguinchor", "Ziguinchor")]
CATEGORIES = [
    ("Appartement", "appart|appartement|appt", 25e6, 120e6, 45, 180),
    ("Studio", "studio", 12e6, 45e6, 20, 60),
    ("Chambre", "chambre|chambre simple", 5e6, 18e6, 10, 30),
    ("Villa", "villa", 80e6, 450e6, 120, 450),
    ("Maison", "maison", 35e6, 180e6, 60, 250),
    ("Terrain", "terrain|terrains", 8e6, 90e6, 80, 1500),
    ("Local commercial", "local|local commercial|bureau|magasin", 30e6, 200e6, 40, 300),
]


@pytest.fixture(scope="module")
def refs():
    return (
        o.construire_index({r for r, _ in GEO}),
        o.construire_index({v for _, v in GEO}, alias={"Dkr": "Dakar"}),
        o.construire_index_categories([(c, s) for c, s, *_ in CATEGORIES]),
        o.construire_ref_categories([(c, *rest) for c, _, *rest in CATEGORIES]),
        set(GEO),
    )


def ligne(resultat, id_local):
    sel = resultat[resultat["id_local"] == id_local]
    assert len(sel) == 1, f"ligne {id_local} introuvable ou en double"
    return sel.iloc[0]


# ===========================================================================
# PLATEFORME
# ===========================================================================
BASE_PF = dict(
    date_mise_en_ligne="2022-05-01", type_transaction="vente", categorie="Villa",
    region="Dakar", commune="Pikine", quartier="x", prix="200000000", devise="FCFA",
    surface="300", pieces="4", sdb="2", description="", statut="Vendu", date_expiration=None,
)


def pf(refs, *lignes):
    df = pd.DataFrame([dict(BASE_PF, ref_plateforme=i, **kw) for i, kw in lignes])
    return tp.traiter_plateforme_immo_sn(df, *refs, aujourdhui=AUJOURDHUI)


def test_plateforme_vente_propre(refs):
    res = pf(refs, ("P1", {}))
    r = ligne(res, "P1")
    assert r["motif_quarantaine"] == "" and r["avertissements"] == "" and r["corrections"] == ""
    assert r["type_transaction"] == "vente" and r["prix"] == 200e6 and r["periodicite"] is None


@pytest.mark.parametrize("kw,motif", [
    (dict(prix=None), "prix absent"),
    (dict(prix="0"), "prix invalide"),
    (dict(prix="gratuit"), "prix invalide"),
    (dict(surface=None), "surface absent"),
    (dict(date_mise_en_ligne="32/13/2024"), "date invalide"),
    (dict(date_mise_en_ligne="2030-01-01"), "date future"),
    (dict(type_transaction="echange"), "type_transaction inconnu"),
    (dict(type_transaction=None), "type_transaction absent"),
    (dict(categorie="Château"), "type_bien inconnu"),
    (dict(devise="EUR"), "devise non FCFA"),
])
def test_plateforme_cas_bloquants(refs, kw, motif):
    r = ligne(pf(refs, ("X", kw)), "X")
    assert motif in r["motif_quarantaine"]


def test_plateforme_identifiant_absent(refs):
    df = pd.DataFrame([dict(BASE_PF, ref_plateforme=None)])
    res = tp.traiter_plateforme_immo_sn(df, *refs, aujourdhui=AUJOURDHUI)
    assert "identifiant absent" in res.iloc[0]["motif_quarantaine"]


def test_plateforme_transaction_normalisee(refs):
    r = ligne(pf(refs, ("X", dict(type_transaction="Vente"))), "X")
    assert r["motif_quarantaine"] == "" and r["type_transaction"] == "vente"
    assert "type_transaction" in r["corrections"]


def test_plateforme_location_periodicite_dans_le_prix(refs):
    r = ligne(pf(refs, ("L", dict(type_transaction="location", categorie="Appartement",
                                  surface="80", prix="250 000 /mois"))), "L")
    assert r["motif_quarantaine"] == "" and r["periodicite"] == "mensuel" and r["prix"] == 250000
    assert "périodicité" not in r["avertissements"]


def test_plateforme_location_periodicite_dans_la_devise(refs):
    r = ligne(pf(refs, ("L", dict(type_transaction="location", categorie="Appartement",
                                  surface="80", prix="250000", devise="FCFA/mois"))), "L")
    assert r["motif_quarantaine"] == "" and r["periodicite"] == "mensuel"


def test_plateforme_location_periodicite_dans_la_description_est_tracee(refs):
    r = ligne(pf(refs, ("L", dict(type_transaction="location", categorie="Appartement", surface="80",
                                  prix="250000", description="Beau F3, loyer mensuel"))), "L")
    assert r["periodicite"] == "mensuel" and "lue dans description" in r["corrections"]


def test_plateforme_location_sans_periodicite_signalee_pas_rejetee(refs):
    r = ligne(pf(refs, ("L", dict(type_transaction="location", categorie="Appartement",
                                  surface="80", prix="250000"))), "L")
    assert r["motif_quarantaine"] == "" and r["periodicite"] is None
    assert "périodicité" in r["avertissements"]


def test_plateforme_loyer_annuel_evalue_par_mois(refs):
    # 600 000 par an = 50 000 par mois : pas d'avertissement de loyer
    r = ligne(pf(refs, ("L", dict(type_transaction="location", categorie="Appartement",
                                  surface="80", prix="600000 par an"))), "L")
    assert r["periodicite"] == "annuel" and "loyer atypique" not in r["avertissements"]


def test_plateforme_millions_et_surface_ambigue(refs):
    r = ligne(pf(refs, ("X", dict(prix="58.29 millions", categorie="Maison", surface="1,250"))), "X")
    assert r["prix"] == 58290000 and r["surface"] == 1250
    assert "surface ambigu" in r["avertissements"] and r["motif_quarantaine"] == ""


def test_plateforme_surface_ambigue_sans_lecture_plausible_en_quarantaine(refs):
    r = ligne(pf(refs, ("X", dict(surface="2,500"))), "X")
    assert "surface ambigu" in r["motif_quarantaine"]


def test_plateforme_expiration_avant_mise_en_ligne(refs):
    r = ligne(pf(refs, ("X", dict(date_expiration="2021-01-01"))), "X")
    assert "date_expiration antérieure" in r["avertissements"] and r["motif_quarantaine"] == ""


def test_plateforme_incoherence_ville_region_signalee(refs):
    r = ligne(pf(refs, ("X", dict(region="Thiès", commune="Dakar"))), "X")
    assert "incohérentes" in r["avertissements"] and r["region"] == "Thiès" and r["ville"] == "Dakar"


def test_plateforme_pieces_vide_non_signale(refs):
    r = ligne(pf(refs, ("X", dict(pieces=None, sdb=None))), "X")
    assert "chambres" not in r["avertissements"] and r["chambres"] is None


# ===========================================================================
# HISTORIQUE
# ===========================================================================
def hist(refs, *lignes):
    base = dict(DateVente="2019-01-02", Region="Dakar", Ville="Dakar", TypeBien="Villa",
                Prix="200 000 000", Surface="300", Chambres="4", SallesBain="2")
    df = pd.DataFrame([dict(base, ID=i, **kw) for i, kw in lignes])
    return th.traiter_import_historique(df, *refs, aujourdhui=AUJOURDHUI)


def test_historique_ligne_propre_et_normalisations(refs):
    r = ligne(hist(refs, ("H1", dict(Region="DAKAR", Ville="dkr", TypeBien="VILLA"))), "H1")
    assert (r["region"], r["ville"], r["type_bien"]) == ("Dakar", "Dakar", "Villa")
    assert r["prix"] == 200e6 and r["statut"] == "Vendu" and r["type_transaction"] == "vente"
    assert r["motif_quarantaine"] == "" and r["avertissements"] == ""


def test_historique_date_texte_iso_et_ambigue_signalee(refs):
    r = ligne(hist(refs, ("H1", dict(DateVente="05/06/2018"))), "H1")
    assert r["date"] == "2018-06-05" and isinstance(r["date"], str)
    assert "date ambigu" in r["avertissements"]
    r2 = ligne(hist(refs, ("H2", dict(DateVente="13/06/2018"))), "H2")
    assert r2["date"] == "2018-06-13" and "ambigu" not in r2["avertissements"]


@pytest.mark.parametrize("kw,motif", [
    (dict(DateVente="32/13/2024"), "date invalide"),
    (dict(DateVente="hier"), "date invalide"),
    (dict(DateVente="2031-01-01"), "date future"),
    (dict(Prix=None), "prix absent"),
    (dict(Prix="-5000"), "prix invalide"),
    (dict(Surface="0"), "surface invalide"),
    (dict(TypeBien="Château"), "type_bien inconnu"),
])
def test_historique_cas_bloquants(refs, kw, motif):
    assert motif in ligne(hist(refs, ("X", kw)), "X")["motif_quarantaine"]


def test_historique_surface_1_250_gardee_avec_avertissement_pas_en_quarantaine(refs):
    r = ligne(hist(refs, ("X", dict(Surface="1,250", TypeBien="Terrain", Prix="50 000 000"))), "X")
    assert r["surface"] == 1250 and r["motif_quarantaine"] == ""
    assert "surface ambigu" in r["avertissements"]


def test_historique_chambres_texte_converties(refs):
    r = ligne(hist(refs, ("X", dict(Chambres="3", SallesBain="2,0"))), "X")
    assert r["chambres"] == 3 and r["sdb"] == 2 and "sdb" in r["corrections"]


def test_historique_fourchette_referentiel_signalee(refs):
    r = ligne(hist(refs, ("X", dict(Prix="521 000 000"))), "X")
    assert "hors fourchette" in r["avertissements"] and r["motif_quarantaine"] == ""


# ===========================================================================
# PARTICULIERS
# ===========================================================================
def part(refs, *lignes):
    base = dict(date="2022-05-11", region="Dakar", ville="Dakar", type_bien="Villa",
                type_transaction="vente", prix=150000000, surface=200, chambres=3, sdb=2,
                statut="Vendu", periodicite=None)
    df = pd.DataFrame([dict(base, id=i, **kw) for i, kw in lignes])
    return tpa.traiter_particuliers(df, *refs, aujourdhui=AUJOURDHUI)


def test_particuliers_normalisations(refs):
    r = ligne(part(refs, ("Q1", dict(type_bien="appart", statut="VENDU", region="Thies",
                                      ville="Thies", type_transaction="Vente", surface=100))), "Q1")
    assert (r["type_bien"], r["statut"], r["region"], r["ville"]) == ("Appartement", "Vendu", "Thiès", "Thiès")
    assert r["type_transaction"] == "vente" and r["motif_quarantaine"] == ""


@pytest.mark.parametrize("kw,motif", [
    (dict(date="2031-01-01"), "date future"),
    (dict(date="32/13/2024"), "date invalide"),
    (dict(date=None), "date absent"),
    (dict(prix=None), "prix absent"),
    (dict(surface=None), "surface absent"),
    (dict(type_transaction=None), "type_transaction absent"),
    (dict(type_bien="Château"), "type_bien inconnu"),
])
def test_particuliers_cas_bloquants(refs, kw, motif):
    assert motif in ligne(part(refs, ("X", kw)), "X")["motif_quarantaine"]


def test_particuliers_identifiant_absent(refs):
    df = pd.DataFrame([dict(id=None, date="2022-05-11", region="Dakar", ville="Dakar",
                            type_bien="Villa", type_transaction="vente", prix=150000000,
                            surface=200, chambres=3, sdb=2, statut="Vendu", periodicite=None)])
    res = tpa.traiter_particuliers(df, *refs, aujourdhui=AUJOURDHUI)
    assert "identifiant absent" in res.iloc[0]["motif_quarantaine"]


def test_particuliers_quatre_vingt_est_corrige_et_trace(refs):
    r = ligne(part(refs, ("X", dict(type_bien="Appartement", surface="quatre-vingt", prix=60000000))), "X")
    assert r["surface"] == 80 and "quatre-vingt" in r["corrections"] and r["motif_quarantaine"] == ""


def test_particuliers_location_avec_periodicite_dans_le_prix(refs):
    r = ligne(part(refs, ("L", dict(type_transaction="Location", type_bien="Appartement",
                                    surface=80, prix="250 000 par mois"))), "L")
    assert r["type_transaction"] == "location" and r["periodicite"] == "mensuel" and r["prix"] == 250000


def test_particuliers_location_sans_periodicite_signalee(refs):
    r = ligne(part(refs, ("L", dict(type_transaction="location", type_bien="Appartement",
                                    surface=80, prix=250000))), "L")
    assert r["motif_quarantaine"] == "" and "périodicité" in r["avertissements"]


def test_particuliers_aplatissement_tolere_les_blocs_null():
    donnees = [
        {"annonce": {"id": "A1", "date": "2022-05-11", "localisation": {"region": "Dakar", "ville": "Dakar"},
                     "details": {"type": "Villa", "transaction": "vente", "prix": 1, "surface": 2,
                                 "chambres": 3, "sdb": 1}, "statut": "Vendu"}},
        {"annonce": {"id": "A2", "date": None, "localisation": None, "details": None, "statut": None}},
    ]
    plat = tpa.aplatir_particuliers(donnees)
    assert list(plat["id"]) == ["A1", "A2"]
    assert plat.loc[0, "ville"] == "Dakar" and o.est_vide(plat.loc[1, "ville"])
    assert "periodicite" in plat.columns


# ===========================================================================
# DOUBLONS ET RAPPORT
# ===========================================================================
def mini(**kw):
    base = dict(source="s", id_local="1", date="2022-01-01", type_transaction="vente",
                type_bien="Villa", region="Dakar", ville="Dakar", prix=1.0, surface=100.0,
                chambres=3, sdb=2, statut="Vendu", periodicite=None,
                avertissements="", corrections="", motif_quarantaine="", doublon="")
    base.update(kw)
    return base


def test_doublons_exact_et_conflit_marques_sans_suppression():
    df = pd.DataFrame([
        mini(id_local="1"), mini(id_local="1"),            # doublon exact
        mini(id_local="2"), mini(id_local="2", prix=2.0),  # conflit
        mini(id_local="3"),                                 # unique
    ])
    res = tc.marquer_doublons(df)
    assert len(res) == 5
    assert list(res["doublon"]) == ["", "doublon_exact", "conflit_id", "conflit_id", ""]
    assert "doublon exact" in res.loc[1, "avertissements"] and "conflit" in res.loc[2, "avertissements"]


def test_doublons_aucun():
    res = tc.marquer_doublons(pd.DataFrame([mini(id_local="1"), mini(id_local="2")]))
    assert (res["doublon"] == "").all()


def test_doublons_dataframe_vide():
    assert tc.marquer_doublons(pd.DataFrame(columns=tc.COLONNES_SCHEMA)).empty


def test_rapport_taux_et_denominateur():
    brut = pd.DataFrame({"a": ["x", None, "y", "y"], "b": [1, 2, 3, 3]})
    conservees = pd.DataFrame([mini(), mini(corrections="c"), mini(avertissements="a")])
    quarantaine = pd.DataFrame([mini(motif_quarantaine="m")])
    rap = tc.construire_rapport("test", brut, conservees, quarantaine).set_index("indicateur")["valeur"]
    assert rap["lignes_recues"] == 4 and rap["lignes_conservees"] == 3 and rap["lignes_quarantaine"] == 1
    assert rap["lignes_entierement_conformes"] == 1
    assert rap["taux_conformes_pct (denominateur : lignes recues)"] == 25.0
    assert rap["doublons_exacts_dans_le_fichier_brut"] == 1 and rap["manquantes__a"] == 1
