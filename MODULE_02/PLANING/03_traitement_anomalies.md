# Compétence 3 — Nettoyage : manquants, doublons, incohérences, aberrants

## Objectif
Appliquer les règles métier ImmoAnalyse aux 5 sources pour produire un corpus propre, avec trois sorties distinctes :
- quarantaine : lignes irrécupérables
- avertissements : lignes conservées avec anomalie signalée
- données propres : lignes conformes

Chaque décision doit être chiffrée et tracée dans `docs/justifications.md`.

## À la fin, tu dois savoir
- Classer chaque anomalie dans une des 3 catégories métier
- Distinguer un manque structurel d'un manque aléatoire
- Détecter les 3 types de doublons, y compris les doublons d'ID au sein d'une même source
- Corriger le mojibake avant toute jointure
- Vérifier la cohérence `region` et `ville` via le référentiel géographique
- Détecter les outliers via les fourchettes du référentiel catégoriel
- Produire les 6 mesures imposées par `regles_metier.md`

## Partie A — Les 3 catégories métier

### Questions à te poser pour chaque anomalie
1. Cette anomalie rend-elle la ligne inutilisable (prix nul, surface absente, date impossible) ?
2. Ou puis-je la corriger de façon fiable (synonyme connu, séparateur de milliers, casse) ?
3. Ou dois-je la conserver en signalant (surface atypique mais plausible, prix extrême mais réel) ?

### Les 3 catégories — d'après `regles_metier.md`

Bloquantes, allant en quarantaine :
- `prix` absent, non numérique, ou <= 0 après normalisation
- `surface` absente, non numérique, ou <= 0 après normalisation
- date non interprétable (ex. `32/13/2024`)
- date future pour une transaction déclarée vendue
- identifiant absent

Normalisables, avec correction fiable documentée :
- casse et espaces dans `region`, `ville`, `categorie`
- séparateurs de milliers dans `prix` (espace, virgule)
- virgule décimale dans `surface`
- suffixes `FCFA` ou `millions` si l'unité est explicite
- synonymes de catégories (`appart` vers `Appartement`)
- dates `JJ/MM/AAAA` ou ISO
- mojibake dans `historique` (encodage UTF-8 mal interprété)

Avertissements, à conserver en signalant :
- `surface` < 5 m² ou > 2000 m²
- `prix` < 100 000 FCFA ou > 2 000 000 000 FCFA
- `region` et `ville` incompatibles
- `categorie` absente du référentiel
- doublon probable entre sources

### Décision structurante
Chaque ligne des 5 sources doit finir dans exactement un des trois fichiers : `quarantine.csv`, `avertissements.csv`, `donnees_propres.csv`.

## Partie B — Anomalies spécifiques par source

### `agence_teranga.xlsx`
- Surfaces négatives (`-30`, `-12`) : bloquant, quarantaine
- `prix = 0` : bloquant, quarantaine
- Casse incohérente (`ZIGUINCHOR`, `touba`, `KEUR MASSAR`, `KÉDOUGOU`) : normalisable
- `statut` avec 4 modalités (`Vendu`, `En vente`, `Disponible`, `Loué`) : à aligner avec les autres sources
- Feuille `Params` à ne pas concaténer

### `import_historique.csv`
- Mojibake (`Thiï¿½s`, `Linguï¿½re`, `Kï¿½dougou`, `Sï¿½dhiou`, `Vï¿½lingara`, `Mï¿½dina`, `Kï¿½bï¿½mer`, `Guinguinï¿½o`, `Mbackï¿½`, `Salï¿½mata`) : normalisable en priorité, sinon jointures cassées
- `prix` en texte avec espaces (`26 620 000`) : normalisable
- `prix = N/A` : bloquant
- `surface` avec virgule décimale (`367,4`) : normalisable
- `ville` vide : bloquant ou avertissement selon la règle appliquée
- `categorie` en majuscules (`STUDIO`, `MAISON`, `VILLA`, `TERRAIN`, `APPARTEMENT`, `CHAMBRE`, `LOCAL COMMERCIAL`) : normalisable
- Séparateur de colonnes `;` avec mojibake potentiel sur la colonne `Ville`

### `notaires.csv`
- `statut` avec 5 variantes (`Vendu`, `VENDU`, `Vente conclue`, `Acte signé`) : normalisable
- `date_acte` impossible (`32/13/2024`) : bloquant
- `montant_fcfa` vide : bloquant
- `surface` très grande (jusqu'à 1498 m²) : vérifier cohérence avec `categorie`
- `id_acte` : format propre, pas de doublon visible

### `particuliers.json`
- `prix` en string : `"65575000 FCFA"` (normalisable), `"None FCFA"` (bloquant)
- `surface = "quatre-vingt"` : bloquant (non convertible de façon fiable)
- `surface = null` : bloquant
- JSON imbriqué : nécessite un aplatissement (`localisation.region`, `details.prix`, etc.)
- `transaction` : `vente` ou `location`, à réconcilier avec `type_transaction` des autres sources
- `statut` inclut `À confirmer` : à aligner avec les autres modalités

### `plateforme_immo_sn.csv`
- Header dupliqué en cours de fichier (environ ligne 221 dans la lecture brute) : à filtrer
- Doublons d'ID : `PLT-00801` apparaît deux fois, `PLT-00790` deux fois, `PLT-00544` deux fois, `PLT-00058` deux fois, `PLT-00711` deux fois, `PLT-00799` deux fois, `PLT-00625` deux fois, `PLT-00656` deux fois, `PLT-00692` deux fois, `PLT-00716` deux fois, `PLT-00171` deux fois, `PLT-00491` deux fois, `PLT-00494` deux fois, `PLT-00398` deux fois, `PLT-00676` deux fois. Dédoublonner avant tout.
- `prix = "à négocier"` : bloquant
- `prix = "147.52 millions"` : normalisable si l'unité est confirmée
- `categorie = "appart"` en minuscule : normalisable
- Dates futures (`2028-12-01`) : bloquant pour les transactions vendues
- `date_expiration` : colonne propre à cette source, à exclure du corpus final
- `devise` : `FCFA` ou `FCFA/mois` selon `type_transaction`, à harmoniser

## Partie C — Manquants : comprendre le mécanisme avant de choisir

### Questions à te poser
1. Combien de manquants par colonne, par source ?
2. Les manquants sont-ils uniformes ou concentrés ?
3. Croisés avec la source : y a-t-il 100 % de manque sur une source ?
4. Si oui : structurel, imputation par groupe obligatoire.
5. Si non : aléatoire, médiane (numérique) ou mode (catégoriel).

### Piège à éviter absolument
Si les manquants de `surface` sont concentrés sur une source, créer un indicateur `surface_manquant` revient à révéler la source. Le modèle apprendra un raccourci qui ne généralise pas : fuite type 4 (comp 8).

Décision attendue : vérifier le croisement avant de choisir l'imputation. Ne pas créer d'indicateur de manque si le manque est corrélé à la source.

## Partie D — Doublons

### Questions à te poser
1. Y a-t-il des lignes strictement identiques (doublon exact) ?
2. Y a-t-il des lignes qui décrivent le même bien avec des libellés différents (doublon probable) ?
3. Y a-t-il un conflit : même bien annoncé à des prix très différents entre sources ?
4. Y a-t-il des IDs dupliqués au sein d'une même source ?

### Les 3 types

| Type | Signature | Décision attendue |
|---|---|---|
| Exact | Toutes les colonnes identiques | Supprimer |
| Probable | Même `commune` + `categorie` + surface proche | Ne pas fusionner sans preuve |
| Conflit | Même bien, prix incompatibles | Signaler uniquement |
| ID dupliqué | Même `ref_plateforme` ou `Code` ou `id_acte` | Vérifier si contenu identique, sinon arbitrer |

### Règle absolue
Dédoublonner avant le split (comp 7). Sinon, un même bien peut se retrouver dans train et test : fuite silencieuse.

## Partie E — Incohérences géographiques

### Questions à te poser
1. La paire (`region`, `ville`) existe-t-elle dans `referentiel_geographique.csv` ?
2. Si non : laquelle des deux est fausse ? Peux-tu le prouver ?
3. Si tu ne peux pas prouver : signaler (avertissement), ne pas corriger.

### Exemple typique
`region = "Dakar"` avec `commune = "Thiès"` : la commune appartient à la région Thiès dans le référentiel, incohérence certaine.

### Piège spécifique au corpus
`historique` contient des villes avec mojibake (`Thiï¿½s`, `Linguï¿½re`). Tant que le mojibake n'est pas corrigé, toute jointure avec le référentiel produit un faux positif d'incohérence.

Ordre obligatoire : corriger l'encodage, puis tester la cohérence.

## Partie F — Outliers

### Questions à te poser
1. Cette valeur sort-elle de la fourchette du référentiel catégoriel pour sa `categorie` ?
2. Est-elle plausible ? Exemple : villa à 400 M dans la fourchette Villa (80 M à 450 M) : normal.
3. Est-elle certainement fausse ? Exemple : maison à 5 M, sous la fourchette Maison (35 M à 180 M) : à vérifier.
4. L'IQR par catégorie confirme-t-il le hors-fourchette ?

### Pourquoi pas l'IQR global
Une villa à 400 M est un outlier global mais normal pour sa catégorie. L'IQR global génère des faux positifs. Le référentiel catégoriel est la référence métier.

### Décision attendue

| Cas | Décision |
|---|---|
| Dans la fourchette | Conserver |
| Hors fourchette mais plausible | Avertissement |
| Hors fourchette et erreur certaine | Quarantaine |
| Prix <= 0 ou surface <= 0 | Quarantaine |

Résultat attendu : conserver les outliers plausibles, la cible log réduit déjà leur impact.

## À faire concrètement

### Étape 1 — Audit initial par source
- [ ] Compter les manquants par colonne, source par source
- [ ] Croiser manquants et source
- [ ] Compter les doublons exacts, probables, et d'ID
- [ ] Compter les erreurs de conversion par champ (`prix`, `surface`, `date`)
- [ ] Compter les dates futures
- [ ] Compter les IDs absents

### Étape 2 — Normalisation
- [ ] Corriger le mojibake sur `historique`
- [ ] Filtrer le header dupliqué sur `plateforme`
- [ ] Casse et espaces : `region`, `ville`, `categorie`
- [ ] Séparateurs de milliers, virgules décimales
- [ ] Synonymes via le référentiel (`appart` vers `Appartement`)
- [ ] Dates vers format ISO uniforme
- [ ] Aligner `statut` sur un vocabulaire unique
- [ ] Aplatir le JSON `particuliers`
- [ ] Retirer la feuille `Params` de `agence`

### Étape 3 — Quarantaine
- [ ] Appliquer les 5 règles bloquantes
- [ ] Écrire chaque ligne rejetée dans `quarantine.csv` avec la raison

### Étape 4 — Doublons
- [ ] Supprimer les doublons exacts
- [ ] Lister les doublons probables
- [ ] Lister les conflits
- [ ] Arbitrer les IDs dupliqués

### Étape 5 — Incohérences géographiques
- [ ] Croiser (`region`, `ville`) avec le référentiel
- [ ] Corriger si déterministe, sinon avertissement

### Étape 6 — Outliers
- [ ] Croiser avec les fourchettes du référentiel catégoriel
- [ ] Classer : conservé, avertissement, quarantaine
- [ ] IQR par `categorie` en confirmation

### Étape 7 — Imputation (si nécessaire)
- [ ] Mécanisme vérifié avant de choisir
- [ ] Imputation par groupe ou médiane
- [ ] Fit sur train uniquement (préparer pour comp 5 et 7)
- [ ] Documenter le choix

### Étape 8 — Mesures obligatoires

| Mesure | Ce qu'elle prouve |
|---|---|
| Taux de manquants par colonne | État initial |
| Nombre de doublons exacts | Qualité de la source |
| Nombre de doublons probables | Risque de fuite entre sources |
| Nombre d'erreurs de conversion par champ | Qualité du parsing |
| Nombre de corrigés, quarantaine, avertissements | Volume de traitement |
| Taux d'enregistrements entièrement conformes | Santé globale du corpus |

## Ce qu'il faut faire
- Classer chaque ligne dans une des 3 catégories métier
- Traiter la quarantaine en premier
- Normaliser uniquement ce qui est fiable et documenté
- Signaler les avertissements sans les supprimer
- Utiliser le référentiel catégoriel pour les outliers
- Dédoublonner et imputer avant le split, avec fit sur train only pour l'imputation
- Documenter chaque décision dans `docs/justifications.md`
- Produire les 6 mesures obligatoires dans `sortie/rapport_qualite.md`

## Ce qu'il ne faut pas faire
- Créer un indicateur de manque corrélé à la source
- Supprimer un prix hors fourchette globale sans vérifier la fourchette de sa catégorie
- Corriger une incohérence `region` et `ville` ambiguë
- Fusionner deux doublons probables entre sources sans preuve
- Imputer ou dédoublonner après le split
- Imputer la moyenne sur `prix`
- Corriger silencieusement une valeur sans la tracer
- Concaténer avant d'avoir nettoyé chaque source

## Ce que tu dois produire
1. `sortie/quarantine.csv` : lignes rejetées et raison
2. `sortie/avertissements.csv` : lignes conservées avec anomalie signalée
3. `sortie/donnees_propres.csv` : corpus nettoyé
4. Tableau `{source, champ, pourcentage manquants, mécanisme, traitement}`
5. Tableau `{type doublon, nombre, décision}`
6. Tableau `{source, champ, méthode outlier, nombre, décision}`
7. Les 6 mesures obligatoires dans `sortie/rapport_qualite.md`
8. Entrées dans `docs/justifications.md` pour chaque décision

## Pièges récapitulés

| Piège | Conséquence |
|---|---|
| Indicateur de manque comme proxy source | Fuite type 4 |
| Outlier jugé sur fourchette globale | Faux positifs (villas) |
| Corriger `region` et `ville` ambigu | Bruit introduit |
| Fusionner doublons probables | Perte d'information |
| Imputer avant split | Statistiques de validation dans train |
| Dédoublonner après split | Fuite silencieuse |
| Correction non tracée | Non reproductible |
| Mojibake non corrigé avant jointure | Faux positifs géographiques |
| Header dupliqué non filtré | Doublons invisibles |
| Feuille `Params` concaténée | Ligne parasite |

## Transition vers comp 4
Le nettoyage produit trois jeux :
- `donnees_propres.csv` : base des figures de restitution (comp 4)
- `avertissements.csv` : base d'une figure alertes dans le rapport
- `quarantine.csv` : preuve de la qualité du tri

Les figures de restitution montreront l'effet du nettoyage : distribution `prix` propre, `prix` par catégorie propre, Simpson sur données propres, corrélations sur données propres.