"""outils.py : fonctions partagées du projet ImmoAnalyse.

Principe : chaque fonction de lecture (parse_*, canoniser, normaliser_*) renvoie
un couple (valeur, etat) et ne lève jamais d'exception sur une donnée sale.

Etats possibles :
    "ok"       valeur déjà propre, rien changé
    "corrige"  valeur normalisée de façon fiable (à tracer dans `corrections`)
    "ambigu"   valeur interprétée selon une règle documentée (à signaler)
    "absent"   valeur manquante
    "invalide" valeur impossible à interpréter (quarantaine si champ bloquant)
    "inconnu"  texte absent du référentiel (à signaler, pas de correction devinée)

Les seuils sont regroupés en haut du fichier (pas de nombres magiques dans le code).
"""
import math
import numbers
import re
import unicodedata
from datetime import date, datetime

# ---------------------------------------------------------------------------
# Configuration (seuils pédagogiques, pas des normes officielles du marché)
# ---------------------------------------------------------------------------
SEUILS = {
    "surface_min": 5,                  # m2
    "surface_max": 2_000,              # m2
    "prix_min": 100_000,               # FCFA (vente)
    "prix_max": 2_000_000_000,         # FCFA (vente)
    "loyer_mensuel_min": 25_000,       # FCFA par mois
    "loyer_mensuel_max": 5_000_000,    # FCFA par mois
    "chambres_max_petit_bien": 10,     # appartement / studio
    "sdb_marge": 2,                    # sdb > chambres + marge => atypique
}

# Type de bien hors des 7 catégories : True = quarantaine (cahier des charges), False = avertissement
TYPE_BIEN_INCONNU_BLOQUANT = True

# Nombre de mois couverts par une période de loyer
FACTEUR_PERIODICITE = {"mensuel": 1, "trimestriel": 3, "semestriel": 6, "annuel": 12}

TYPES_SANS_CHAMBRE = {"Terrain", "Local commercial"}
TYPES_ZERO_CHAMBRE_OK = TYPES_SANS_CHAMBRE | {"Studio", "Chambre"}
TYPES_PETITS = {"Appartement", "Studio"}

MOIS_FR = {
    "janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
    "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11,
    "decembre": 12,
}


# ---------------------------------------------------------------------------
# Utilitaires de base
# ---------------------------------------------------------------------------
def est_vide(v):
    """True pour None, NaN, pd.NA ou chaîne vide."""
    if v is None:
        return True
    try:
        if v != v:  # NaN
            return True
    except (TypeError, ValueError):  # pd.NA
        return True
    return isinstance(v, str) and v.strip() == ""


def _espaces(s):
    s = str(s).replace("\u00a0", " ").replace("\u202f", " ")
    return re.sub(r"\s+", " ", s).strip()


def normaliser_texte(v):
    """Supprime les espaces superflus. Renvoie None si la valeur est vide."""
    return None if est_vide(v) else _espaces(v)


def cle_texte(v):
    """Clé de comparaison : sans accents, minuscules, tirets et apostrophes = espace."""
    s = unicodedata.normalize("NFKD", _espaces(v))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[-'’]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------------------
# Catégories contrôlées : villes, régions, types de bien, statuts
# ---------------------------------------------------------------------------
def construire_index(noms, alias=None):
    """{clé de comparaison: nom canonique}. `alias` : {"dkr": "Dakar", ...}."""
    index = {cle_texte(n): n for n in noms}
    for a, canon in (alias or {}).items():
        index[cle_texte(a)] = canon
    return index


def construire_index_categories(lignes):
    """lignes : itérable de (categorie, "syn1|syn2|...") issu de referentiel_categories."""
    index = {}
    for categorie, synonymes in lignes:
        index[cle_texte(categorie)] = categorie
        for syn in str(synonymes).split("|"):
            if syn.strip():
                index[cle_texte(syn)] = categorie
    return index


def canoniser(v, index):
    """Ramène v à son nom canonique. Pas de devinette : hors index => (texte, 'inconnu')."""
    txt = normaliser_texte(v)
    if txt is None:
        return None, "absent"
    canon = index.get(cle_texte(txt))
    if canon is None:
        return txt, "inconnu"
    return canon, ("ok" if canon == txt else "corrige")


INDEX_STATUTS = construire_index(
    ["Vendu", "En vente", "Disponible", "Loué"],
    alias={"vente conclue": "Vendu", "acte signé": "Vendu", "à vendre": "En vente"},
)


def normaliser_statut(v):
    """VENDU / Vente conclue / Acte signé => Vendu. Statuts connus : Vendu, En vente, Disponible, Loué. Autres : 'inconnu'."""
    return canoniser(v, INDEX_STATUTS)


def construire_ref_categories(lignes):
    """lignes : (categorie, prix_min, prix_max, surface_min, surface_max)."""
    return {c: tuple(float(x) for x in rest) for c, *rest in lignes}


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------
def _construire_date(a, m, j):
    try:
        return date(int(a), int(m), int(j)).isoformat()
    except ValueError:
        return None


def parse_date(v):
    """Renvoie (date ISO AAAA-MM-JJ ou None, etat).

    ISO => ok. JJ/MM/AAAA => corrige, ou ambigu si jour et mois sont tous deux <= 12
    et différents (convention du dictionnaire : JJ/MM/AAAA, mais à signaler).
    '12 mars 2024' => corrige. 'hier', 32/13/2024... => invalide (pas de devinette).
    """
    if est_vide(v):
        return None, "absent"
    if isinstance(v, datetime):
        return v.date().isoformat(), "ok"
    if isinstance(v, date):
        return v.isoformat(), "ok"
    s = _espaces(v)

    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})(?:[ T].*)?", s)
    if m:
        iso = _construire_date(*m.groups())
        return (iso, "ok") if iso else (None, "invalide")

    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        j, mo, a = m.groups()
        iso = _construire_date(a, mo, j)
        if not iso:
            return None, "invalide"
        ambigu = int(j) <= 12 and int(mo) <= 12 and int(j) != int(mo)
        return iso, ("ambigu" if ambigu else "corrige")

    m = re.fullmatch(r"(\d{1,2}) ([a-z]+) (\d{4})", cle_texte(s))
    if m and m.group(2) in MOIS_FR:
        iso = _construire_date(m.group(3), MOIS_FR[m.group(2)], m.group(1))
        return (iso, "corrige") if iso else (None, "invalide")

    return None, "invalide"


def est_future(iso, aujourdhui=None):
    """True si la date ISO est postérieure à aujourd'hui (date d'exécution)."""
    if iso is None:
        return False
    ref = (aujourdhui or date.today()).isoformat()
    return iso > ref


# ---------------------------------------------------------------------------
# Nombres : prix et surfaces
# ---------------------------------------------------------------------------
def _lire_nombre(s, milliers_possibles):
    """Lit un nombre dont les séparateurs sont déjà nettoyés des espaces."""
    neg = s.startswith("-")
    s = s.lstrip("-")
    if "." in s and "," in s:
        dec = "." if s.rfind(".") > s.rfind(",") else ","
        mil = "," if dec == "." else "."
        s = s.replace(mil, "").replace(dec, ".")
    elif milliers_possibles and re.fullmatch(r"\d{1,3}([.,]\d{3})+", s):
        s = re.sub(r"[.,]", "", s)
    else:
        s = s.replace(",", ".")
    try:
        x = float(s)
    except ValueError:
        return None
    return -x if neg else x


def _nombre_natif(v):
    x = float(v)
    return (x, "ok") if math.isfinite(x) and x > 0 else (None, "invalide")


def parse_prix(v):
    """Prix de vente ou loyer, en FCFA. Renvoie (float ou None, etat).

    Gère : '37 965 000 FCFA', '58.29 millions', '1.250.000', '250,000'.
    Sans unité explicite, aucun facteur n'est deviné ('58.29' reste 58.29,
    ce qui sera signalé comme prix atypique).
    """
    if est_vide(v):
        return None, "absent"
    if isinstance(v, bool):
        return None, "invalide"
    if isinstance(v, numbers.Real):
        return _nombre_natif(v)

    s = _espaces(v).lower()
    mult = 1
    if re.search(r"milliards?", s):
        mult = 1e9
    elif re.search(r"millions?", s):
        mult = 1e6
    s = re.sub(r"milliards?|millions?", "", s)
    s = re.sub(r"f\s*cfa|xof|cfa|francs?", "", s).strip()
    if not re.fullmatch(r"-?\d[\d\s.,]*", s):
        return None, "invalide"
    s_net = re.sub(r"\s", "", s)
    x = _lire_nombre(s_net, milliers_possibles=(mult == 1))
    if x is None:
        return None, "invalide"
    x = round(x * mult, 2)
    if not math.isfinite(x) or x <= 0:
        return None, "invalide"
    etat = "ok" if (mult == 1 and re.fullmatch(r"\d+(\.\d+)?", s)) else "corrige"
    return x, etat


def parse_surface(v):
    """Surface en m2. Renvoie (float ou None, etat).

    '173.3' ok ; '85 m²', '85,5', '1 250' corrige ; texte ('quatre-vingt') invalide.
    '1,250' est ambigu (1 250 m2 ou 1,25 m2) : on retient la seule lecture comprise
    entre SEUILS[surface_min] et SEUILS[surface_max] et on renvoie 'ambigu' ;
    si aucune ou les deux sont plausibles, (None, 'ambigu').
    """
    if est_vide(v):
        return None, "absent"
    if isinstance(v, bool):
        return None, "invalide"
    if isinstance(v, numbers.Real):
        return _nombre_natif(v)

    s_brut = _espaces(v).lower()
    s = re.sub(r"\s*(m\s*[²2]|m[eè]tres?\s+carr[ée]s?|m)\s*$", "", s_brut).strip()
    if not re.fullmatch(r"-?\d[\d\s.,]*", s):
        mots = mots_vers_nombre(s)          # 'quatre-vingt' -> 80
        return (mots, "corrige") if mots is not None else (None, "invalide")
    s_net = re.sub(r"\s", "", s)

    if re.fullmatch(r"\d{1,3},\d{3}", s_net):
        lectures = [float(s_net.replace(",", ".")), float(s_net.replace(",", ""))]
        ok = [c for c in lectures
              if SEUILS["surface_min"] <= c <= SEUILS["surface_max"]]
        return (ok[0], "ambigu") if len(ok) == 1 else (None, "ambigu")

    x = _lire_nombre(s_net, milliers_possibles=False)
    if x is None or not math.isfinite(x) or x <= 0:
        return None, "invalide"
    etat = "ok" if re.fullmatch(r"\d+(\.\d+)?", s_brut) else "corrige"
    return x, etat


# ---------------------------------------------------------------------------
# Périodicité des loyers
# ---------------------------------------------------------------------------
_PERIODES = {
    "mensuel": {"mois", "mens", "mensuel", "mensuelle"},
    "trimestriel": {"trimestre", "trim", "trimestriel", "trimestrielle"},
    "semestriel": {"semestre", "sem", "semestriel", "semestrielle"},
    "annuel": {"an", "annee", "annuel", "annuelle"},
}


def normaliser_periodicite(v):
    """'/mois', 'par mois', 'mens.' => 'mensuel'. Inconnu => (None, 'invalide') : on ne devine pas."""
    if est_vide(v):
        return None, "absent"
    c = cle_texte(v)
    c = re.sub(r"^(par\s+|/)\s*", "", c).strip(" ./")
    for canon, formes in _PERIODES.items():
        if c in formes:
            return canon, ("ok" if canon == normaliser_texte(v) else "corrige")
    return None, "invalide"


# ---------------------------------------------------------------------------
# Avertissements de plausibilité (on conserve la ligne, on signale)
# ---------------------------------------------------------------------------
def _fmt(x):
    return f"{x:,.0f}".replace(",", " ")


def avertissements_plausibilite(prix=None, surface=None, type_bien=None,
                                type_transaction="vente", periodicite=None,
                                chambres=None, sdb=None, ref_cat=None):
    """Liste de messages d'avertissement (vide = aucun). `ref_cat` : construire_ref_categories()."""
    avis = []
    ref = (ref_cat or {}).get(type_bien)

    if prix is not None:
        if type_transaction == "location":
            facteur = FACTEUR_PERIODICITE.get(periodicite)
            if facteur is None:
                avis.append("périodicité du loyer absente ou inconnue : loyer non évalué")
            else:
                mensuel = prix / facteur
                if not (SEUILS["loyer_mensuel_min"] <= mensuel <= SEUILS["loyer_mensuel_max"]):
                    avis.append(f"loyer atypique ({_fmt(mensuel)} FCFA/mois équivalent)")
        else:
            if not (SEUILS["prix_min"] <= prix <= SEUILS["prix_max"]):
                avis.append(f"prix atypique ({_fmt(prix)} FCFA)")
            if ref and not (ref[0] <= prix <= ref[1]):
                avis.append(f"prix hors fourchette indicative de {type_bien}")

    if surface is not None:
        if not (SEUILS["surface_min"] <= surface <= SEUILS["surface_max"]):
            avis.append(f"surface atypique ({surface} m2)")
        if ref and not (ref[2] <= surface <= ref[3]):
            avis.append(f"surface hors plage typique de {type_bien}")

    if chambres is not None:
        if chambres < 0:
            avis.append("nombre de chambres négatif")
        else:
            if chambres == 0 and type_bien not in TYPES_ZERO_CHAMBRE_OK:
                avis.append(f"0 chambre inattendu pour {type_bien}")
            if chambres > 0 and type_bien == "Terrain":
                avis.append("chambres déclarées pour un terrain")
            if type_bien in TYPES_PETITS and chambres > SEUILS["chambres_max_petit_bien"]:
                avis.append(f"plus de {SEUILS['chambres_max_petit_bien']} chambres pour {type_bien}")
            if sdb is not None and sdb > chambres + SEUILS["sdb_marge"]:
                avis.append("salles de bain > chambres + 2")
    if sdb is not None and sdb < 0:
        avis.append("nombre de salles de bain négatif")
    return avis


# ---------------------------------------------------------------------------
# Nombres écrits en lettres (surfaces : 'quatre-vingt' => 80)
# ---------------------------------------------------------------------------
_UNITES = {"zero": 0, "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5,
           "six": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10, "onze": 11, "douze": 12,
           "treize": 13, "quatorze": 14, "quinze": 15, "seize": 16}
_DIZAINES = {"vingt": 20, "vingts": 20, "trente": 30, "quarante": 40, "cinquante": 50,
             "soixante": 60, "octante": 80, "nonante": 90}


def mots_vers_nombre(texte):
    """'quatre-vingt' => 80.0 ; 'deux cent cinquante' => 250.0 ; mot inconnu => None.

    Couvre 1 à 999 (pas de 'mille', pas de décimales) : au-delà, la valeur reste invalide.
    """
    if est_vide(texte):
        return None
    s = cle_texte(texte)
    s = re.sub(r"\bquatre vingts?\b", "octante", s)
    total = courant = 0
    for mot in s.split():
        if mot == "et":
            continue
        if mot in _UNITES:
            courant += _UNITES[mot]
        elif mot in _DIZAINES:
            courant += _DIZAINES[mot]
        elif mot in ("cent", "cents"):
            total += max(courant, 1) * 100
            courant = 0
        else:
            return None
    total += courant
    return float(total) if total > 0 else None


# ---------------------------------------------------------------------------
# Transaction, devise, entiers
# ---------------------------------------------------------------------------
INDEX_TRANSACTIONS = construire_index(
    ["vente", "location"],
    alias={"a vendre": "vente", "vendre": "vente", "sale": "vente",
           "a louer": "location", "louer": "location", "loc": "location",
           "bail": "location", "rent": "location"},
)


def normaliser_transaction(v):
    """Vente / VENTE / à vendre => vente ; Location / à louer => location. Autre => 'inconnu'."""
    return canoniser(v, INDEX_TRANSACTIONS)


INDEX_DEVISES = construire_index(
    ["FCFA"],
    alias={"XOF": "FCFA", "CFA": "FCFA", "F CFA": "FCFA", "F.CFA": "FCFA",
           "franc cfa": "FCFA", "francs cfa": "FCFA"},
)


def normaliser_devise(v):
    """FCFA, XOF, F CFA => FCFA. Autre devise (EUR, USD...) => 'inconnu' : aucune conversion."""
    return canoniser(v, INDEX_DEVISES)


def en_entier(v):
    """Chambres, salles de bain. Renvoie (int ou None, etat).

    3, 3.0 (artefact pandas), '3' => ok ; '3,0' => corrige ; 2.5, 'trois' => invalide ;
    vide => absent. Un négatif est renvoyé tel quel (signalé par avertissements_plausibilite).
    """
    if est_vide(v):
        return None, "absent"
    if isinstance(v, bool):
        return None, "invalide"
    if isinstance(v, numbers.Real):
        x = float(v)
        return (int(x), "ok") if math.isfinite(x) and x.is_integer() else (None, "invalide")
    s = _espaces(v)
    if re.fullmatch(r"-?\d+", s):
        return int(s), "ok"
    if re.fullmatch(r"-?\d+[.,]0+", s):
        return int(float(s.replace(",", "."))), "corrige"
    return None, "invalide"


# ---------------------------------------------------------------------------
# Périodicité lue dans un texte libre (prix, devise, description)
# ---------------------------------------------------------------------------
_MARQUEURS_PERIODE = {
    "mensuel": [r"(?:/|\bpar\s+)\s*mois\b", r"\bmensuel(?:le)?s?\b", r"\bmens\b\.?"],
    "trimestriel": [r"(?:/|\bpar\s+)\s*(?:trimestre|trim)\b\.?", r"\btrimestriel(?:le)?s?\b"],
    "semestriel": [r"(?:/|\bpar\s+)\s*(?:semestre|sem)\b\.?", r"\bsemestriel(?:le)?s?\b"],
    "annuel": [r"(?:/|\bpar\s+)\s*(?:annee|an)\b", r"\bannuel(?:le)?s?\b"],
}


def _sans_accents(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def extraire_periodicite(texte):
    """Cherche une périodicité EXPLICITE ('250 000 /mois', 'loyer mensuel').

    Renvoie (periodicite, etat, texte_sans_la_mention).
    etat : 'ok' (une seule trouvée), 'absent' (aucune : texte renvoyé inchangé),
    'ambigu' (plusieurs différentes : None). Pas de devinette : 'mois' seul ne suffit pas.
    """
    if est_vide(texte) or not isinstance(texte, str):
        return None, "absent", texte
    s = _sans_accents(_espaces(texte)).lower()
    trouvees = []
    for canon, motifs in _MARQUEURS_PERIODE.items():
        for motif in motifs:
            if re.search(motif, s):
                if canon not in trouvees:
                    trouvees.append(canon)
                s = re.sub(motif, " ", s)
    if not trouvees:
        return None, "absent", texte
    reste = re.sub(r"\s+", " ", s).strip(" ./")
    if len(trouvees) == 1:
        return trouvees[0], "ok", reste
    return None, "ambigu", reste


# ---------------------------------------------------------------------------
# Rangement du résultat d'une conversion (utilisé par tous les modules)
# ---------------------------------------------------------------------------
def suivre(nom, valeur_brute, valeur, etat, corr, avis, quar, bloquant=False):
    """Range le résultat d'une conversion dans corrections, avertissements ou quarantaine."""
    echec = (
        etat in ("absent", "invalide")
        or (etat == "inconnu" and bloquant)
        or (etat == "ambigu" and valeur is None)
    )
    if echec:
        (quar if bloquant else avis).append(f"{nom} {etat} : '{valeur_brute}'")
    elif etat == "corrige":
        corr.append(f"{nom} : '{valeur_brute}' -> '{valeur}'")
    elif etat == "ambigu":
        avis.append(f"{nom} ambigu : '{valeur_brute}' lu '{valeur}'")
    elif etat == "inconnu":
        avis.append(f"{nom} hors référentiel : '{valeur_brute}'")
