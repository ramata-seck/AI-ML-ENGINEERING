# Compétence 1 — Types, distributions, statistiques descriptives

## Objectif
Identifier le type réel de chaque colonne dans chaque source, décrire sa distribution, et choisir la bonne statistique selon la forme observée.

## À la fin, tu dois savoir
- Classer chaque colonne de chaque source dans son type réel
- Choisir entre moyenne et médiane selon la distribution
- Détecter une distribution asymétrique et le chiffrer
- Justifier le choix de transformation de `prix`

## Partie A — Les types de données

### Questions à te poser
1. Quel est le type attendu selon `dictionnaire_donnees.csv` ?
2. Quel est le type réel dans les données ?
3. Y a-t-il un écart ? Si oui, est-ce réparable (conversion) ou structurel (à traiter en comp 3) ?

### Pièges spécifiques aux 5 sources
- `prix` peut arriver en texte : `"65575000 FCFA"` (particuliers), `"147.52 millions"` (plateforme), `"à négocier"` (plateforme), `"None FCFA"` (particuliers).
- `surface` peut arriver en texte : `"quatre-vingt"` (particuliers), `"367,4"` (historique, virgule décimale).
- `date` peut être ISO (`2023-12-16`), `JJ/MM/AAAA` (`02/12/2023`), ou impossible (`32/13/2024` dans notaires et plateforme).
- `import_historique.csv` a un encodage cassé (mojibake) : `Linguï¿½re`, `Thiï¿½s`, `Kï¿½dougou`. Toute jointure sur `region` échouera tant que ce n'est pas corrigé.
- `plateforme_immo_sn.csv` a un header dupliqué en cours de fichier — la lecture naïve peut produire des lignes corrompues.
- `agence_teranga.xlsx` a une deuxième feuille `Params` (Version, Source, Date_export, Contact) qui ne doit pas être concaténée comme données.

### Ce que tu dois décider
Pour chaque colonne de chaque source : type confirmé / à convertir / à traiter en comp 3.

## Partie B — Comprendre la distribution

### Questions à te poser
1. La distribution de `prix` est-elle symétrique ou asymétrique ?
2. La moyenne est-elle un bon résumé ou est-elle tirée par les extrêmes ?
3. La médiane est-elle plus représentative ?
4. Le skewness dépasse-t-il 1 en valeur absolue ?
5. Que se passe-t-il si je prends le logarithme de `prix` ?
6. Les distributions sont-elles les mêmes selon la source ?

### Quand utiliser quelle statistique

| Statistique | À utiliser quand |
|---|---|
| Moyenne | Distribution symétrique |
| Médiane | Distribution asymétrique (par défaut sur `prix`) |
| Écart-type | Comparer la dispersion entre groupes |
| IQR (Q3 − Q1) | Détection robuste d'extrêmes |
| Skewness | Justifier une transformation |
| Kurtosis | Repérer des extrêmes fréquents |

### Règles à connaître
- Si `|skew| > 1` : envisager une transformation (`log` sur `prix`).
- Une moyenne très supérieure à la médiane : asymétrie à droite (typique des prix).
- Une moyenne très inférieure à la médiane : asymétrie à gauche (rare sur des prix).

## Partie C — Vérifier la normalité

### Questions à te poser
1. La distribution de `log(prix)` est-elle proche d'une normale ?
2. Le QQ-plot est-il aligné sur la diagonale ?
3. Le test de Shapiro-Wilk donne-t-il `p > 0.05` ?
4. Si Shapiro et QQ-plot se contredisent, lequel croire ?

### Pièges
- Shapiro devient hypersensible sur n > 5000 : croiser avec QQ-plot.
- La normalité parfaite n'est pas un objectif — c'est un moyen de rendre le log utile.

## À faire concrètement

### Bloc 1 — Types par source
- [ ] Lister les colonnes et leur type réel, source par source
- [ ] Comparer au type attendu du dictionnaire
- [ ] Identifier les conversions nécessaires
- [ ] Compter les `NaN` produits par chaque conversion

### Bloc 2 — Statistiques descriptives
- [ ] Calculer count, moyenne, médiane, écart-type, Q1, Q3, skew, kurtosis
- [ ] Faire le tableau par catégorie de bien et par source
- [ ] Comparer moyenne vs médiane : conclure sur l'asymétrie

### Bloc 3 — Distribution de `prix`
- [ ] Observer `prix` brut et `log(prix)`
- [ ] Chiffrer le skew dans les deux cas
- [ ] QQ-plot sur `log(prix)`
- [ ] Shapiro sur un échantillon
- [ ] Décision : garder `prix` ou modéliser `log(prix)`

### Bloc 4 — Distribution de `surface`
- [ ] Même démarche que `prix`
- [ ] Repérer les valeurs à 0 ou négatives (incohérentes avec la règle métier `surface > 0`)
- [ ] Repérer les valeurs > 2000 m² (avertissement, pas erreur)

### Bloc 5 — Distribution des catégorielles
- [ ] Compter les effectifs de `categorie`, `region`, `statut`, `type_transaction`
- [ ] Identifier les modalités rares (< 10 occurrences)
- [ ] Décider : garder / regrouper / exclure (à traiter en comp 3)

## Ce qu'il faut faire
- Vérifier les types réels avant toute analyse, source par source
- Médiane + skew systématiquement sur `prix`
- Comparer brut et log, avec chiffres
- Croiser test statistique et QQ-plot
- Documenter chaque décision avec la valeur chiffrée
- Traiter chaque source séparément avant de comparer

## Ce qu'il ne faut pas faire
- Rapporter la moyenne seule sur `prix`
- Conclure sur la distribution sans skew ni QQ-plot
- Utiliser Shapiro seul sur n > 5000
- Convertir sans vérifier combien de `NaN` sont créés
- Confondre « count » (non-nuls) et « nombre total de lignes »
- Concaténer avant d'avoir compris les types de chaque source
- Lire `plateforme_immo_sn.csv` sans détecter le header dupliqué

## Ce que tu dois produire
1. Tableau `{source, champ, type attendu, type réel, écart, action}`
2. Tableau de stats descriptives (count, mean, median, std, Q1, Q3, skew, kurtosis) par source
3. Comparaison chiffrée `prix` vs `log(prix)` avec skew avant/après
4. Justification écrite du choix de cible dans `docs/justifications.md`
5. Liste des modalités rares à traiter en comp 3

## Pièges récapitulés

| Piège | Conséquence |
|---|---|
| Ignorer les types réels | Conversions ratées, `NaN` silencieux |
| Mean sans median | Décision biaisée |
| Shapiro seul sur gros n | Faux positif |
| Skew non chiffré | Choix de transformation non défendable |
| Décider des modalités rares ici | Empêche sur la comp 3 |
| Traiter les 5 sources comme une seule | Anomalies spécifiques noyées |

## Transition vers comp 2
Trois livrables alimentent directement l'EDA :
- Le tableau des types conditionne les tests à faire (khi2 sur catégorielles, corrélation sur numériques).
- Le skew de `prix` orientera la viz diagnostique et le choix de `log`.
- Les modalités rares sont la première brique du nettoyage à décider en comp 3.