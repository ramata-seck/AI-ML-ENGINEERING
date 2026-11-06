# Compétence 6 — Feature engineering : créer et sélectionner

## Objectif
Créer quelques variables candidates à partir des colonnes réelles du corpus, mesurer leur gain réel en validation croisée sur le train, garder l'utile, exclure le reste.

Règle absolue : créer une variable ne prouve pas qu'elle est utile. Le seul juge est le gain en validation croisée.

## À la fin, tu dois savoir
- Créer 3 à 5 variables candidates pertinentes et justifiées métier
- Mesurer leur gain par validation croisée sur train
- Décider garder ou exclure avec un seuil chiffré
- Reconnaître une fuite déguisée (gain proche de +0.99)
- Documenter chaque décision

## Partie A — Quelles variables créer ?

### Questions à te poser pour chaque candidate
1. Quelle idée métier justifie cette variable ?
2. Est-elle dérivée de la cible ? Si oui, fuite type 1, rejeter.
3. Est-elle dérivée d'une variable révélant la source ? Fuite type 4.
4. Est-elle redondante avec une variable existante ?
5. Quel gain mesurable attends-tu ?

### Candidates réelles sur ce corpus

| Candidate | Idée métier | Risque |
|---|---|---|
| `surface_log` | Distribution étalée | Aucun, transformation utile |
| `annee` | Effet marché annuel | Faible signal, à mesurer |
| `mois` | Saisonnalité | Faible signal, à mesurer |
| `distance_dakar_km` | Proximité capitale | Redondant avec `region` |
| `ratio_prix_fourchette` | Positionnement dans le segment | Contient `prix`, fuite type 1 |
| `prix_m2` (prix divisé par surface) | Prix au m² | Contient `prix`, fuite type 1 |
| `source` en feature | Effet flux | Fuite type 4 probable, révèle le flux |
| `surface_par_chambre` | Densité | `chambres` n'existe pas dans le dictionnaire cible uniformément |
| `est_hors_fourchette` | Signal d'anomalie | Redondant avec comp 3 |
| `indicateur_manquant_surface` | Manque | Fuite type 4 si corrélé à la source |

### Règle de tri
Sur ces candidates, maximum 5 à tester, au moins 1 à rejeter sur principe (`prix_m2`, `ratio_prix_fourchette`).

## Partie B — Comment mesurer le gain

### La méthode
1. Choisir une baseline : le modèle le plus simple possible avec la variable principale (`categorie`).
2. Ajouter une candidate à la fois, jamais deux en même temps.
3. Mesurer en validation croisée sur le train, avec k=5.
4. Comparer au score de la baseline.
5. Appliquer le seuil.

### Pourquoi la CV et pas la validation
La validation peut donner un bon score par hasard.
La CV moyenne sur 5 folds donne une mesure plus robuste, moins sensible à la chance d'un découpage.

### Le seuil de décision

| Gain en R² vs baseline | Décision |
|---|---|
| Supérieur à +0.01 | Garder |
| Entre -0.01 et +0.01 | Neutre, garder seulement si sens métier fort |
| Inférieur à -0.01 | Exclure |

## Partie C — Le test de la fuite

### La règle
Si une candidate donne un gain proche de +0.99, ce n'est pas une bonne nouvelle : c'est une fuite.

### Pourquoi
Un modèle qui prédit le prix à 99 pourcent de R² à partir d'une feature en apparence banale recopie la réponse. La feature contient la cible, ou un proxy direct.

### Le test à faire consciemment
- Créer volontairement `prix_m2` et `ratio_prix_fourchette`
- Les mesurer
- Constater le gain proche de +0.99
- Rejeter les deux
- Documenter dans `docs/justifications.md` : test de fuite effectué, résultat attendu, feature rejetée

C'est un rite de passage de la comp 6. Tu dois avoir vu le mirage pour le reconnaître en production.

### Piège spécifique au multi-source
`source` peut sembler utile parce qu'elle corrèle avec le prix (les sources n'ont pas les mêmes distributions). Avant de la garder :
- Mesurer son gain en CV
- Se demander : est-ce qu'elle capture une vraie caractéristique du bien, ou juste un artefact de flux ?
- En production, sur un bien nouveau, la source sera connue, mais la distribution de prix dépend de la source pour des raisons qui ne se reproduiront peut-être pas

Décision attendue : exclure `source` par défaut, la tester seulement si le gain est très fort et la justifier métier.

## Partie D — Résultat attendu sur ce corpus

Tableau attendu (valeurs à recalculer, ceci donne l'ordre de grandeur) :

| Variable | Gain en R² attendu | Décision |
|---|---|---|
| `categorie` (baseline) | référence | Garder |
| `region` | +0.002 | Garder, sens métier |
| `surface_log` | entre -0.03 et +0.01 | Garder, métier fort, à réévaluer |
| `annee` | -0.005 | Exclure |
| `mois` | -0.003 | Exclure |
| `distance_dakar_km` | +0.001 | Exclure, redondant |
| `ratio_prix_fourchette` | +0.99 | Fuite, rejeter |
| `prix_m2` | +0.99 | Fuite, rejeter |
| `source` | +0.01 à +0.05 selon le corpus | Exclure par principe (fuite type 4) |

## À faire concrètement

### Étape 1 — Lister les candidates
- [ ] Écrire 3 à 5 candidates avec idée métier
- [ ] Identifier au moins 1 qui doit être rejetée sur principe (fuite)

### Étape 2 — Baseline
- [ ] Modèle avec `categorie` seule
- [ ] Score CV de référence chiffré

### Étape 3 — Mesure une par une
- [ ] Pour chaque candidate : score CV avec `categorie` et la candidate
- [ ] Gain calculé
- [ ] Décision par seuil

### Étape 4 — Test de fuite
- [ ] Créer volontairement `prix_m2`
- [ ] Mesurer et constater +0.99
- [ ] Rejeter et documenter
- [ ] Refaire le test avec `source` en feature pour voir si elle déclenche une fuite type 4

### Étape 5 — Décision finale
- [ ] Tableau complet `{variable, R² seul, gain, décision, justification}`
- [ ] Mise à jour `reports/dictionnaire_features.csv`
- [ ] Entrées dans `docs/justifications.md`

## Ce qu'il faut faire
- Mesurer par CV sur train, jamais val ou test
- Baseline explicite : `categorie` seule
- Une candidate à la fois pour isoler la responsabilité
- Seuil chiffré : +0.01 et -0.01
- Garder `surface_log` même si gain proche de 0, sens métier fort, à réévaluer plus tard
- Tester la fuite volontairement
- Documenter chaque décision avec le chiffre
- Tester explicitement `source` avant de l'exclure par principe

## Ce qu'il ne faut pas faire
- Créer `prix_m2` en pensant qu'il sera utile
- Créer `surface_manquant` comme indicateur sans vérifier le croisement avec `source`
- Créer 10 variables sans mesurer
- Garder tout au cas où
- Changer plusieurs variables à la fois
- Tester sur val (biais d'optimisme)
- Se réjouir d'un R² de 0.99 sans vérifier qu'aucune feature ne contient `prix`
- Créer `distance_dakar_km` et la garder si `region` est déjà dans le modèle (redondance)
- Garder `source` parce qu'elle améliore le score sans vérifier qu'elle ne fuit pas

## Ce que tu dois produire
1. Liste des candidates avec idée métier
2. Tableau `{variable, R² seul, gain avec baseline, décision, justification}`
3. Preuve du test de fuite : `prix_m2` donne +0.99, rejeté
4. Preuve du test de fuite type 4 : `source` testée, décision documentée
5. Mise à jour `reports/dictionnaire_features.csv`
6. Entrées dans `docs/justifications.md`

## Pièges récapitulés

| Piège | Conséquence |
|---|---|
| `prix_m2` | Fuite type 1, mirage |
| `ratio_prix_fourchette` | Fuite type 1 |
| Indicateur de manque | Fuite type 4 |
| `source` en feature | Fuite type 4 probable |
| `distance_dakar` | Redondance avec `region` |
| Créer sans mesurer | Complexité et sur-apprentissage |
| Tester sur val | Optimisme trompeur |
| Se réjouir d'un R² de 0.99 | Mirage non détecté |

## Transition vers comp 7
La sélection finale de features fige la forme du jeu utilisé pour le split :
- Si `commune` exclue : pas de split stratifié sur `commune`
- Si `statut` exclu : pas de split stratifié sur `statut`
- Si `source` exclue : le split doit quand même vérifier que les 5 sources sont présentes dans chaque ensemble
- Si `categorie` porte le signal : stratifier par `categorie` en comp 7
- Si fuite détectée : vérifier qu'aucune feature finale ne contient `prix`