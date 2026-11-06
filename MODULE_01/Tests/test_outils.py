"""Tests de outils.py : cas conformes, invalides et limites. Lancer : pytest -v"""
from datetime import date

import pytest

import outils as o

VILLES = o.construire_index(["Dakar", "Guédiawaye", "Thiès", "Saint-Louis"], alias={"Dkr": "Dakar"})
TYPES = o.construire_index_categories([
    ("Appartement", "appart|appartement|appt"),
    ("Local commercial", "local|local commercial|bureau|magasin"),
])
REF = o.construire_ref_categories([("Villa", 80e6, 450e6, 120, 450), ("Terrain", 8e6, 90e6, 80, 1500)])


# --- base -------------------------------------------------------------------
@pytest.mark.parametrize("v,attendu", [
    (None, True), (float("nan"), True), ("", True), ("   ", True),
    ("Dakar", False), (0, False),
])
def test_est_vide(v, attendu):
    assert o.est_vide(v) is attendu


def test_normaliser_texte():
    assert o.normaliser_texte("  Keur   Massar ") == "Keur Massar"
    assert o.normaliser_texte("\u00a0") is None


# --- canoniser --------------------------------------------------------------
@pytest.mark.parametrize("v,attendu", [
    ("Dakar", ("Dakar", "ok")),
    ("DAKAR", ("Dakar", "corrige")),
    ("dakar ", ("Dakar", "corrige")),
    ("Dkr", ("Dakar", "corrige")),
    ("Guediawaye", ("Guédiawaye", "corrige")),
    ("GUÉDIAWAYE", ("Guédiawaye", "corrige")),
    ("THIÈS", ("Thiès", "corrige")),
    ("Saint Louis", ("Saint-Louis", "corrige")),
    ("Atlantis", ("Atlantis", "inconnu")),
    (None, (None, "absent")),
])
def test_canoniser_villes(v, attendu):
    assert o.canoniser(v, VILLES) == attendu


def test_canoniser_types():
    assert o.canoniser("appt", TYPES) == ("Appartement", "corrige")
    assert o.canoniser("MAGASIN", TYPES) == ("Local commercial", "corrige")
    assert o.canoniser("Château", TYPES) == ("Château", "inconnu")


@pytest.mark.parametrize("v,attendu", [
    ("Vendu", ("Vendu", "ok")), ("VENDU", ("Vendu", "corrige")),
    ("Vente conclue", ("Vendu", "corrige")), ("Acte signé", ("Vendu", "corrige")),
    ("En vente", ("En vente", "ok")), ("Retiré", ("Retiré", "inconnu")),
])
def test_statut(v, attendu):
    assert o.normaliser_statut(v) == attendu


# --- dates ------------------------------------------------------------------
@pytest.mark.parametrize("v,attendu", [
    ("2024-03-01", ("2024-03-01", "ok")),
    ("13/03/2024", ("2024-03-13", "corrige")),     # sans ambiguïté
    ("01/03/2024", ("2024-03-01", "ambigu")),      # jour et mois <= 12
    ("05/05/2024", ("2024-05-05", "corrige")),     # jour = mois : pas ambigu
    ("12 mars 2024", ("2024-03-12", "corrige")),
    ("1 Août 2023", ("2023-08-01", "corrige")),
    ("29/02/2024", ("2024-02-29", "corrige")),     # bissextile
    ("29/02/2023", (None, "invalide")),
    ("32/13/2024", (None, "invalide")),
    ("2024-02-30", (None, "invalide")),
    ("hier", (None, "invalide")),
    ("", (None, "absent")),
    (None, (None, "absent")),
])
def test_parse_date(v, attendu):
    assert o.parse_date(v) == attendu


def test_est_future():
    ref = date(2026, 10, 29)
    assert o.est_future("2026-10-30", ref) is True
    assert o.est_future("2026-10-29", ref) is False
    assert o.est_future(None, ref) is False


# --- prix -------------------------------------------------------------------
@pytest.mark.parametrize("v,attendu", [
    (43758000, (43758000.0, "ok")),
    ("43758000", (43758000.0, "ok")),
    ("37 965 000 FCFA", (37965000.0, "corrige")),
    ("26\u00a0620\u00a0000", (26620000.0, "corrige")),
    ("58.29 millions", (58290000.0, "corrige")),
    ("57,62 millions", (57620000.0, "corrige")),
    ("1.250.000", (1250000.0, "corrige")),
    ("250,000", (250000.0, "corrige")),
    ("1,5 milliard", (1.5e9, "corrige")),
    ("58.29", (58.29, "ok")),                      # pas de facteur deviné
    (0, (None, "invalide")),
    (-5000, (None, "invalide")),
    ("-5000", (None, "invalide")),
    ("gratuit", (None, "invalide")),
    (float("inf"), (None, "invalide")),
    (True, (None, "invalide")),
    (None, (None, "absent")),
    (float("nan"), (None, "absent")),
])
def test_parse_prix(v, attendu):
    assert o.parse_prix(v) == attendu


# --- surface ----------------------------------------------------------------
@pytest.mark.parametrize("v,attendu", [
    (120, (120.0, "ok")),
    ("173.3", (173.3, "ok")),
    ("85 m²", (85.0, "corrige")),
    ("85m2", (85.0, "corrige")),
    ("85,5", (85.5, "corrige")),
    ("1 250", (1250.0, "corrige")),
    ("1,250", (1250.0, "ambigu")),                 # 1,25 m2 invraisemblable
    ("12,345", (12.345, "ambigu")),                # 12 345 m2 invraisemblable
    ("0,500", (500.0, "ambigu")),                  # 0,5 m2 invraisemblable
    ("2,500", (None, "ambigu")),                   # 2,5 m2 et 2 500 m2 hors plage : pas de devinette
    ("quatre-vingt", (80.0, "corrige")),                # nombre en lettres : voir DECISIONS.md
    ("quatre-vingt-seize-mille", (None, "invalide")),   # hors périmètre
    ("0", (None, "invalide")),
    ("-12", (None, "invalide")),
    (None, (None, "absent")),
])
def test_parse_surface(v, attendu):
    assert o.parse_surface(v) == attendu


# --- périodicité ------------------------------------------------------------
@pytest.mark.parametrize("v,attendu", [
    ("mensuel", ("mensuel", "ok")),
    ("/mois", ("mensuel", "corrige")),
    ("par mois", ("mensuel", "corrige")),
    ("mens.", ("mensuel", "corrige")),
    ("Mensuelle", ("mensuel", "corrige")),
    ("par an", ("annuel", "corrige")),
    ("trimestre", ("trimestriel", "corrige")),
    ("quinzaine", (None, "invalide")),
    (None, (None, "absent")),
])
def test_periodicite(v, attendu):
    assert o.normaliser_periodicite(v) == attendu


# --- avertissements ---------------------------------------------------------
def test_aucun_avertissement():
    assert o.avertissements_plausibilite(
        prix=200e6, surface=300, type_bien="Villa", chambres=4, sdb=3, ref_cat=REF) == []


def test_prix_hors_fourchette():
    avis = o.avertissements_plausibilite(prix=521e6, surface=300, type_bien="Villa", ref_cat=REF)
    assert avis == ["prix hors fourchette indicative de Villa"]


def test_prix_et_surface_atypiques():
    avis = o.avertissements_plausibilite(prix=50_000, surface=3, type_bien="Villa")
    assert any("prix atypique" in a for a in avis)
    assert any("surface atypique" in a for a in avis)


def test_loyer_selon_periodicite():
    # 600 000 par an = 50 000 par mois : normal
    assert o.avertissements_plausibilite(prix=600_000, type_transaction="location", periodicite="annuel") == []
    # 600 000 par mois est dans la plage ; 10 000 par mois ne l'est pas
    assert o.avertissements_plausibilite(prix=10_000, type_transaction="location", periodicite="mensuel")
    # périodicité absente : signalée, pas devinée
    avis = o.avertissements_plausibilite(prix=250_000, type_transaction="location")
    assert "périodicité" in avis[0]


def test_chambres():
    assert o.avertissements_plausibilite(chambres=0, type_bien="Terrain") == []
    assert o.avertissements_plausibilite(chambres=0, type_bien="Villa") == ["0 chambre inattendu pour Villa"]
    assert o.avertissements_plausibilite(chambres=3, type_bien="Terrain") == ["chambres déclarées pour un terrain"]
    assert o.avertissements_plausibilite(chambres=12, type_bien="Studio")
    assert o.avertissements_plausibilite(chambres=1, sdb=4, type_bien="Villa") == ["salles de bain > chambres + 2"]
    assert o.avertissements_plausibilite(chambres=-1, type_bien="Villa") == ["nombre de chambres négatif"]


# --- nombres en lettres -----------------------------------------------------
@pytest.mark.parametrize("v,attendu", [
    ("quatre-vingt", (80.0, "corrige")),
    ("Quatre-Vingt", (80.0, "corrige")),
    ("quatre-vingt-dix", (90.0, "corrige")),
    ("soixante-dix", (70.0, "corrige")),
    ("soixante et onze", (71.0, "corrige")),
    ("deux cent cinquante m2", (250.0, "corrige")),
    ("trois cents", (300.0, "corrige")),
    ("mille", (None, "invalide")),               # hors périmètre : pas de devinette
    ("beaucoup", (None, "invalide")),
])
def test_surface_en_lettres(v, attendu):
    assert o.parse_surface(v) == attendu


# --- transaction et devise --------------------------------------------------
@pytest.mark.parametrize("v,attendu", [
    ("vente", ("vente", "ok")), ("Vente", ("vente", "corrige")), ("VENTE ", ("vente", "corrige")),
    ("à louer", ("location", "corrige")), ("Location", ("location", "corrige")),
    ("echange", ("echange", "inconnu")), (None, (None, "absent")),
])
def test_transaction(v, attendu):
    assert o.normaliser_transaction(v) == attendu


@pytest.mark.parametrize("v,attendu", [
    ("FCFA", ("FCFA", "ok")), ("fcfa", ("FCFA", "corrige")), ("XOF", ("FCFA", "corrige")),
    ("F CFA", ("FCFA", "corrige")), ("EUR", ("EUR", "inconnu")), (None, (None, "absent")),
])
def test_devise(v, attendu):
    assert o.normaliser_devise(v) == attendu


# --- entiers ----------------------------------------------------------------
@pytest.mark.parametrize("v,attendu", [
    (3, (3, "ok")), (3.0, (3, "ok")), ("3", (3, "ok")), ("3,0", (3, "corrige")),
    (0, (0, "ok")), (-1, (-1, "ok")), (2.5, (None, "invalide")), ("trois", (None, "invalide")),
    (True, (None, "invalide")), (None, (None, "absent")), (float("nan"), (None, "absent")),
])
def test_en_entier(v, attendu):
    assert o.en_entier(v) == attendu


# --- périodicité dans un texte libre ---------------------------------------
@pytest.mark.parametrize("v,periode,etat,reste", [
    ("250 000 FCFA /mois", "mensuel", "ok", "250 000 fcfa"),
    ("250000 par mois", "mensuel", "ok", "250000"),
    ("FCFA/an", "annuel", "ok", "fcfa"),
    ("loyer mensuel", "mensuel", "ok", "loyer"),
    ("1 500 000 / trimestre", "trimestriel", "ok", "1 500 000"),
    ("600 000 par semestre", "semestriel", "ok", "600 000"),
    ("loyer mensuel ou /an", None, "ambigu", "loyer ou"),
    ("caution de 3 mois", None, "absent", "caution de 3 mois"),   # 'mois' seul ne suffit pas
    ("43758000", None, "absent", "43758000"),
    (None, None, "absent", None),
])
def test_extraire_periodicite(v, periode, etat, reste):
    p, e, r = o.extraire_periodicite(v)
    assert (p, e) == (periode, etat)
    if etat != "ambigu":
        assert r == reste


def test_prix_apres_retrait_periodicite():
    _, _, texte = o.extraire_periodicite("250 000 FCFA /mois")
    assert o.parse_prix(texte) == (250000.0, "corrige")


# --- suivre -----------------------------------------------------------------
def test_suivre_range_selon_l_etat():
    corr, avis, quar = [], [], []
    o.suivre("prix", "abc", None, "invalide", corr, avis, quar, bloquant=True)
    o.suivre("ville", "Dkr", "Dakar", "corrige", corr, avis, quar)
    o.suivre("surface", "1,250", 1250.0, "ambigu", corr, avis, quar, bloquant=True)
    o.suivre("surface", "0,500", None, "ambigu", corr, avis, quar, bloquant=True)
    assert len(quar) == 2 and len(corr) == 1 and len(avis) == 1
