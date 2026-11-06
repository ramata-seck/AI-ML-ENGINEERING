# Compétence 2 — EDA + visualisations diagnostiques

## Objectif
Poser des questions aux 5 sources et y répondre par des mesures chiffrées, pour décider ce qu'il faudra nettoyer en compétence 3.

Cette compétence produit des figures diagnostiques : elles servent à décider, pas à illustrer le rapport final. Elles seront remplacées en comp 4 par les figures de restitution (après nettoyage).

## À la fin, tu dois savoir
- Formuler une question EDA et y répondre par un chiffre
- Identifier le mécanisme des manquants (structurel vs aléatoire)
- Mesurer les relations entre variables
- Tester le paradoxe de Simpson sur `prix` vs `surface` par `categorie`
- Tester la tendance temporelle sur `date`
- Produire une liste d'insights qui orientent la comp 3

## Ce qu'est une EDA (et ce qu'elle n'est pas)

Une EDA n'est pas un catalogue de graphiques.
C'est une démarche :
1. Je pose une question
2. Je choisis la mesure qui y répond
3. J'interprète le résultat
4. J'écris l'implication pour la suite

Si un graphique ne répond pas à une question, il ne sert à rien.

## Spécificité multi-source

Les 5 sources n'ont pas les mêmes anomalies :

| Source | Anomalies à diagnostiquer |
|---|---|
| `agence` | Casse incohérente (`ZIGUINCHOR` vs `touba`), surfaces négatives (`-30`, `-12`), `prix = 0` |
| `historique` | Mojibake (`Thiï¿½s`, `Linguï¿½re`), `N/A`, séparateurs d'espaces (`26 620 000`), virgules décimales (`367,4`), villes vides |
| `notaires` | Statuts variables (`Vendu` / `VENDU` / `Vente conclue` / `Acte signé`), dates impossibles (`32/13/2024`), `montant_fcfa` vides |
| `particuliers` | `prix` en string (`"65575000 FCFA"`), `"None FCFA"`, `surface = "quatre-vingt"` |
| `plateforme` | `"147.52 millions"`, `"à négocier"`, doublons d'ID (`PLT-00801`), dates futures (`2028-12-01`), `categorie = "appart"` |

Conséquence : l'EDA doit se faire par source avant toute concaténation.

## Les 6 blocs à couvrir

### Bloc A — Vue d'ensemble
Questions :
- Combien de lignes par source, de colonnes par source ?
- Quelle est la période couverte par la date, source par source ?
- Quels sont les effectifs par `categorie`, `region`, `statut`, `type_transaction` ?
- Y a-t-il un déséquilibre criant entre modalités ?
- Combien de lignes dans chaque source sont en doublon exact ?

Ce que tu dois obtenir : un chiffre pour chaque réponse. Pas de « beaucoup de », « surtout ».

### Bloc B — Manquants et leur mécanisme
Questions :
- Combien de manquants par colonne, source par source ?
- Les manquants sont-ils répartis uniformément ou concentrés ?
- Si je croise avec la source, est-ce que 100 % d'une source manque sur une colonne ?
- Si oui : mécanisme structurel, imputation par groupe en comp 3.
- Si non : mécanisme aléatoire, médiane ou mode en comp 3.

Piège à anticiper : si le manque est concentré sur une source, créer un indicateur de manque revient à révéler la source, donc fuite type 4 (comp 8).

### Bloc C — Relations entre variables
Questions :
- `prix` et `surface` sont-ils corrélés ? Linéairement ? Monotonement ?
- La corrélation Pearson et Spearman divergent-elles ? Si oui : relation non-linéaire.
- `prix` varie-t-il significativement selon `categorie` ? (test ANOVA)
- `categorie` et `region` sont-ils indépendants ? (test khi2)
- Y a-t-il des paires de numériques redondantes ? (VIF)

Règle : une corrélation sans test ne vaut rien. Un test sans interprétation non plus.

### Bloc D — Le paradoxe de Simpson
Question centrale : la relation `prix` et `surface` existe-t-elle à l'intérieur de chaque catégorie, ou seulement globalement par composition ?

Démarche :
1. Mesurer la corrélation globale.
2. Mesurer la corrélation par catégorie.
3. Comparer.

Si la corrélation globale est modérée et que celles par groupe sont proches de 0 : paradoxe de Simpson actif.
Implication comp 6 : ne pas utiliser `surface` comme prédicteur direct, envisager une interaction `categorie × surface`.

### Bloc E — Tendance temporelle
Questions :
- Le prix médian évolue-t-il dans le temps ?
- Y a-t-il une tendance monotone significative ?
- Y a-t-il des pics ou des trous anormaux ?
- Y a-t-il des dates futures (anomalie visible dans `plateforme`) ?

Test à faire : Mann-Kendall (non-paramétrique, robuste).
Si p > 0.05 : pas de tendance, split aléatoire acceptable (comp 7).
Si p < 0.05 : tendance, split temporel obligatoire (comp 7).

### Bloc F — Aberrants (diagnostic, pas décision)
Questions :
- Combien d'observations sortent visuellement des boîtes ?
- Ces observations sont-elles plausibles au vu des fourchettes du `referentiel_categories.csv` ?
- Y a-t-il des valeurs impossibles (négatives, nulles sur `prix` ou `surface`) ?
- Y a-t-il des incohérences entre `region` et `ville` par rapport au `referentiel_geographique.csv` ?

Ne pas décider ici. La décision (conserver / signaler / quarantaine) se prend en comp 3 avec les règles métier.

## À faire concrètement

### Diagnostic D1 — Effectifs et déséquilibres
- [ ] Compter les lignes et la période, source par source
- [ ] Compter les effectifs par catégorielles
- [ ] Identifier les déséquilibres (ex. 80 % Dakar, 5 % Matam)
- [ ] Compter les doublons exacts par source

### Diagnostic D2 — Manquants et mécanisme
- [ ] Compter les manquants par colonne, source par source
- [ ] Croiser avec la source : y a-t-il un 100 % sur une source ?
- [ ] Conclure structurel ou aléatoire pour chaque colonne

### Diagnostic D3 — Distribution brute de `prix` par catégorie
- [ ] Visualiser sans nettoyage
- [ ] Identifier les catégories où la dispersion est la plus forte
- [ ] Ne rien décider ici

### Diagnostic D4 — Relations numériques
- [ ] Pearson et Spearman sur `prix` et `surface`
- [ ] VIF si plusieurs numériques ajoutées
- [ ] Repérer les divergences Pearson/Spearman

### Diagnostic D5 — Paradoxe de Simpson
- [ ] Corrélation globale `prix` et `surface`
- [ ] Corrélation par catégorie
- [ ] Conclure : paradoxe actif ou non

### Diagnostic D6 — Tendance temporelle
- [ ] Prix médian par année, source par source
- [ ] Test Mann-Kendall
- [ ] Conclure : tendance ou pas, conditionne le split

### Diagnostic D7 — Tests croisés
- [ ] ANOVA `prix` ~ `categorie`
- [ ] Khi2 `categorie` et `region`
- [ ] Toutes les p-values notées

### Diagnostic D8 — Qualité par source
- [ ] Pour chaque source : taux de manquants sur `prix`, `surface`, `date`
- [ ] Pour chaque source : nombre de valeurs non numériques sur `prix`
- [ ] Pour chaque source : nombre de dates non interprétables
- [ ] Pour chaque source : nombre de doublons d'ID

## Ce qu'il faut faire
- Formuler une question avant chaque figure
- Chiffrer chaque résultat (r, p, %, count)
- Croiser manquants et source
- Comparer Pearson et Spearman
- Tester Simpson par catégorie
- Tester la tendance pour décider du split
- Traiter les 5 sources séparément avant de les comparer
- Lister les insights qui orientent la comp 3

## Ce qu'il ne faut pas faire
- Produire des graphiques sans conclusion
- Déclarer un outlier ici (c'est comp 3, avec le référentiel)
- Interpréter `surface` comme prédicteur direct sans tester Simpson
- Conclure à une causalité depuis une corrélation
- Confondre cette EDA avec la restitution (comp 4)
- Ignorer un test statistique sous prétexte que « visuellement c'est clair »
- Concaténer avant d'avoir diagnostiqué chaque source

## Ce que tu dois produire
1. Tableau EDA structuré (manquants, corrélations, tests) avec valeurs chiffrées, par source
2. 4 figures diagnostiques minimum : manquants, distribution `prix` par catégorie, Simpson, tendance temporelle
3. Liste de 3 à 5 insights orientés comp 3, formulés ainsi :
   > « `surface` manque à 100 % sur la source X, mécanisme structurel, imputation par groupe en comp 3, pas d'indicateur de manque (fuite type 4). »
4. Entrées dans `docs/justifications.md`

## Pièges récapitulés

| Piège | Conséquence |
|---|---|
| 20 graphes sans conclusion | Aucun insight actionnable |
| Outliers déclarés sans référentiel | Sur-nettoyage en comp 3 |
| Simpson ignoré | Mauvais choix de features en comp 6 |
| Tendance non testée | Split inadapté en comp 7 |
| Confondre diagnostic et restitution | Figures sales dans le rapport |
| Manquants croisés sans la source | Fuite type 4 en comp 8 |
| Mojibake non vu | Jointures cassées, EDA faussée |

## Transition vers comp 3
Chaque insight doit déboucher sur une action de nettoyage :

| Insight EDA | Action en comp 3 |
|---|---|
| Manquants concentrés sur une source | Imputation par groupe, pas d'indicateur |
| Valeurs hors fourchette du référentiel | Vérifier, signaler, ou quarantaine |
| Paradoxe de Simpson actif | Ne pas créer `prix_m2` (fuite type 1) |
| Pas de tendance temporelle | Split aléatoire acceptable |
| Modalités rares | Regrouper ou exclure |
| Doublons probables entre sources | Ne pas fusionner sans preuve |
| Dates futures | Quarantaine ou avertissement |
| Mojibake dans une source | Normalisation d'encodage en priorité |