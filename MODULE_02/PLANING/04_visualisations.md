# Compétence 4 — Visualisations de restitution

## Objectif
Produire les figures finales du rapport. Elles montrent le corpus après nettoyage et prouvent que les décisions de la comp 3 ont produit un jeu propre, cohérent et exploitable.

Ces figures sont différentes des viz diagnostiques de la comp 2.
En comp 2 : données brutes, but décider.
En comp 4 : données propres, but prouver.

## À la fin, tu dois savoir
- Distinguer une viz diagnostique d'une viz de restitution
- Choisir le bon graphique pour la bonne question
- Produire une figure lisible (titre, axes, unités)
- Écrire une conclusion chiffrée sous chaque figure
- Relier chaque figure à une décision de la comp 3

## Diagnostic vs restitution

| Critère | Diagnostic (comp 2) | Restitution (comp 4) |
|---|---|---|
| Données | Brutes | Propres |
| But | Décider | Prouver |
| Figure manquants | Heatmap des NaN | Absence des NaN et tableau comparatif |
| Figure outliers | Boîtes brutes | Boîtes dans les fourchettes du référentiel |
| Figure `prix` | Distribution brute et skew | Distribution `log(prix)` justifiée |
| Figure par source | Une par source | Comparaison des sources après alignement |
| Conclusion | Action à mener | Résultat obtenu |

Règle d'or : un graphique = une question + une conclusion chiffrée.
Pas de graphique parce que c'est joli.

## Les 6 figures de restitution obligatoires

### V1 — Distribution de la cible
Question : la cible est-elle modélisable telle quelle, ou faut-il la transformer ?

Ce que la figure doit montrer :
- Panneau gauche : `prix` brut après nettoyage, skew encore > 1
- Panneau droit : `log(prix)`, skew proche de 0
- Annoter le skew avant et après

Conclusion à écrire : skew passe de X à Y, décision de modéliser `log(prix)` (confirmé par comp 1).

### V2 — Prix par catégorie de bien
Question : `categorie` structure-t-elle le prix, et de combien ?

Ce que la figure doit montrer :
- Boîtes triées par médiane croissante
- Échelle log
- Ratio médiane max sur médiane min chiffré

Conclusion à écrire : ratio max sur min de X, `categorie` est la variable prioritaire (comp 6).

### V3 — Paradoxe de Simpson sur données propres
Question : la relation `prix` et `surface` tient-elle par catégorie, ou est-elle un artefact ?

Ce que la figure doit montrer :
- Panneau gauche : nuage global avec pente
- Panneau droit : nuages par catégorie avec pente par groupe
- `r` global annoté, `r` moyen par groupe

Conclusion à écrire : `r` global de X, `r` par catégorie proche de 0, paradoxe actif. Implication : pas de `prix_m2` (fuite), pas de `surface` seule en feature directe.

### V4 — Matrice de corrélation
Question : quelles variables numériques sont redondantes ?

Ce que la figure doit montrer :
- Uniquement les numériques
- Échelle -1 à +1 fixe
- Paires |r| > 0.8 listées à part

Conclusion à écrire : paires redondantes identifiées, décision de vérifier le VIF en comp 5 et 6, conserver une seule des deux.

### V5 — Preuve du nettoyage
Question : le nettoyage a-t-il effectivement supprimé les anomalies ?

Ce que la figure doit montrer :
- Tableau comparatif avant et après
- Nombre de manquants par colonne
- Nombre de valeurs hors fourchette
- Nombre de doublons
- Nombre de lignes en quarantaine
- Taux d'enregistrements conformes par source

Conclusion à écrire : taux de conformité de X pourcent avant, Y pourcent après. Preuve que les décisions de comp 3 ont produit un jeu exploitable.

### V6 — Comparaison des sources après nettoyage
Question : les 5 sources produisent-elles des distributions comparables après alignement ?

Ce que la figure doit montrer :
- Distribution de `prix` par source (boxplot ou violin)
- Distribution de `surface` par source
- Médianes et effectifs annotés par source

Conclusion à écrire : les sources X et Y sont alignées, la source Z reste structurellement différente (écrire pourquoi), décision pour comp 5 et 7 sur la façon de traiter la source Z.

Cette figure est importante dans ce corpus : 5 sources hétérogènes peuvent produire des distributions très différentes. Il faut le voir avant d'encoder.

## À faire concrètement

### Étape 1 — Vérifier que tu es bien sur les données propres
- [ ] Les données de comp 4 sont celles sorties de comp 3 (`donnees_propres.csv`)
- [ ] Pas de retraitement ici, uniquement restitution

### Étape 2 — Construire chaque figure
- [ ] V1 à V6 produites
- [ ] Chaque figure sauvegardée dans `reports/figures/`
- [ ] Chaque figure a un titre qui énonce la conclusion
- [ ] Chaque figure a des axes avec unités
- [ ] Chaque figure a une conclusion chiffrée en markdown juste en dessous

### Étape 3 — Relier chaque figure à une décision
Pour chaque figure, écrire : cette figure justifie ou confirme la décision X prise en comp 3.

### Étape 4 — Cohérence avec comp 2
- [ ] Comparer les figures diagnostiques (comp 2) aux figures de restitution (comp 4)
- [ ] Si une distribution a changé de forme de façon suspecte, vérifier qu'aucun nettoyage abusif n'a eu lieu

## Ce qu'il faut faire
- Travailler sur les données propres, pas les brutes
- Choisir le graphique selon la question
- Titrer chaque figure avec sa conclusion
- Annoter les chiffres clés sur le graphique (skew, r, ratio)
- Écrire une conclusion chiffrée sous chaque figure
- Relier chaque figure à une décision de comp 3
- Sauvegarder dans `reports/figures/`
- Utiliser la source comme variable de couleur ou de panneau quand c'est pertinent

## Ce qu'il ne faut pas faire
- Refaire les viz diagnostiques ici
- Décider du nettoyage ici (c'est comp 3)
- Graphique sans conclusion
- Échelle brute qui écrase les petites valeurs
- Barplot avec 46 modalités (`commune`) sans tri ni regroupement
- Scatter sans couleur quand il y a des sous-groupes
- Heatmap de corrélation incluant des one-hot
- Figure sans titre qui dit ce qu'on doit y voir
- Figure comparant les sources sans avoir aligné les échelles

## Ce que tu dois produire
1. V1 à V6 sauvegardées dans `reports/figures/`
2. Pour chaque figure : titre, axes, conclusion chiffrée
3. Tableau récapitulatif `{figure, question, décision comp 3 justifiée}`
4. Section Visualisations dans `sortie/rapport_qualite.md` ou dans le rapport final

## Pièges récapitulés

| Piège | Conséquence |
|---|---|
| Viz de comp 2 refaites | Perte de temps, incohérence |
| Graphique sans conclusion | Figure décorative |
| Échelle brute sur `prix` | Petites valeurs écrasées |
| Barplot avec 46 modalités | Illisible |
| Corrélation avec one-hot | Illisible |
| Pas de lien avec comp 3 | Figure hors-sol |
| Sources comparées sans alignement | Fausse impression de différence |

## Transition vers comp 5
Les figures de restitution préparent les décisions d'encodage :

| Figure | Conséquence comp 5 |
|---|---|
| V1 log prix | Cible = `log(prix)` |
| V2 catégorie porte le signal | `categorie` en one-hot prioritaire |
| V3 Simpson | Éviter `surface` seule, envisager interaction |
| V4 corrélations | Scaler robuste si outliers conservés |
| V5 conformité | Base de la reproductibilité du pipeline (comp 9) |
| V6 comparaison des sources | Décider si `source` reste dans le modèle (attention fuite type 4 en comp 8) |