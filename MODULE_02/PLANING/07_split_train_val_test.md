# Compétence 7 — Découpage train, validation, test

## Objectif
Découper le corpus propre et enrichi en trois ensembles sans fuite, avec une stratégie justifiée par les données et une reproductibilité garantie.

## À la fin, tu dois savoir
- Choisir le ratio de découpage adapté
- Choisir la stratégie (aléatoire, temporelle, stratifiée)
- Justifier pourquoi ce choix avec une preuve
- Ne jamais toucher au test avant la fin
- Vérifier que le split est reproductible
- Vérifier que les 5 sources sont représentées dans chaque ensemble

## Partie A — Pourquoi trois ensembles

### Questions à te poser
1. À quoi sert le train ? Apprendre.
2. À quoi sert la validation ? Comparer des modèles, choisir.
3. À quoi sert le test ? Évaluation finale, une seule fois.

### Règle absolue
Le test ne sert jamais à prendre une décision.
Si tu regardes le test avant la fin, tu ne peux plus l'utiliser comme estimation honnête.

## Partie B — Choisir le ratio

### Questions à te poser
1. Combien de lignes ai-je après nettoyage, et par source ?
2. Y a-t-il assez de données pour trois ensembles stables ?
3. Le corpus est-il déséquilibré entre catégories ? Entre sources ?

### Ratios usuels

| Ratio | Quand |
|---|---|
| 70 / 15 / 15 | Standard, corpus moyen (plus de 1000 lignes) |
| 80 / 10 / 10 | Corpus petit |
| 60 / 20 / 20 | Besoin d'une validation plus stable |

Décision attendue sur ce corpus : 70/15/15. Le corpus après nettoyage dépasse largement 1000 lignes, chaque ensemble sera stable.

### Piège spécifique au multi-source
Les 5 sources n'ont pas le même volume. Si une source est très minoritaire (par exemple 100 lignes sur 2500), un split aléatoire simple peut :
- Sous-représenter cette source dans la validation
- Produire une validation non représentative
- Fausser l'évaluation de la généralisation

Décision attendue : vérifier les effectifs par source après split. Si une source est sous-représentée dans un ensemble, stratifier aussi par `source` en plus de `categorie`.

## Partie C — Choisir la stratégie

### La question centrale
Le marché immobilier évolue-t-il dans le temps ?

### Réponse à obtenir — preuve exigée
- Test de Mann-Kendall sur les prix médians par année (déjà fait en comp 2)
- Si p > 0.05 : pas de tendance, split aléatoire acceptable
- Si p < 0.05 : tendance, split temporel obligatoire

### Piège spécifique au multi-source
Les sources ne couvrent pas les mêmes périodes :
- `historique` semble couvrir 2018 à 2020
- `agence` couvre 2018 à 2025
- `notaires` couvre 2018 à 2025
- `particuliers` couvre 2018 à 2025
- `plateforme` couvre 2018 à 2028 (avec des dates futures suspectes)

Conséquence : un split purement temporel peut déséquilibrer les sources (le train contiendrait surtout les sources historiques, le test surtout les récentes). Si tu choisis temporel, il faut stratifier par source et vérifier les effectifs.

Décision attendue sur ce corpus :
- Si Mann-Kendall donne p > 0.05 sur le prix médian par année, split aléatoire stratifié par `categorie` et vérifié par `source`
- Si p < 0.05, split temporel avec stratification par `source`

### Les trois stratégies

| Stratégie | Quand | Preuve à fournir |
|---|---|---|
| Aléatoire | Pas de tendance temporelle | Mann-Kendall p > 0.05 |
| Temporelle | Marché évolutif | Mann-Kendall p < 0.05 |
| Stratifiée | Variable cible déséquilibrée | Proportions égales vérifiées |

## Partie D — La stratification

### Questions à te poser
1. Quelle variable porte le signal principal ? `categorie` (comp 6)
2. Y a-t-il un déséquilibre entre ses modalités ?
3. Si on ne stratifie pas, une modalité rare peut se retrouver absente d'un ensemble.
4. Faut-il aussi stratifier par `source` ?

### Décision attendue
Stratifier par `categorie`. C'est elle qui porte le signal. Chaque ensemble doit contenir les mêmes proportions.
Vérifier ensuite les proportions par `source` dans chaque ensemble. Si elles divergent de plus de 2 points, ajouter `source` à la stratification.

### Preuve à produire

Tableau 1 : proportions de `categorie` dans chaque ensemble.

| Catégorie | Pourcentage dans train | Pourcentage dans val | Pourcentage dans test |
|---|---|---|---|
| Appartement | ... | ... | ... |
| Villa | ... | ... | ... |
| ... | ... | ... | ... |

Les proportions doivent être identiques à 0.5 point près.

Tableau 2 : effectifs par source dans chaque ensemble.

| Source | Train | Val | Test | Écart attendu |
|---|---|---|---|---|
| agence | ... | ... | ... | proportionnel au volume |
| historique | ... | ... | ... | ... |
| notaires | ... | ... | ... | ... |
| particuliers | ... | ... | ... | ... |
| plateforme | ... | ... | ... | ... |

Si une source est absente d'un ensemble ou fortement sous-représentée, revoir la stratification.

## Partie E — La reproductibilité

### Question à te poser
Si je relance le split demain, est-ce que j'obtiens les mêmes lignes dans train ?

### La règle
- Fixer une graine (random_state), sinon deux exécutions donnent deux splits et les résultats ne sont pas comparables
- Documenter la graine dans `docs/justifications.md`

### Vérification
- [ ] Relancer le split donne les mêmes lignes dans train
- [ ] Documenter la graine

## À faire concrètement

### Étape 1 — Vérifier les prérequis
- [ ] Corpus propre (sortie comp 3)
- [ ] Features sélectionnées (sortie comp 6)
- [ ] Doublons déjà supprimés (sinon fuite)
- [ ] Vocabulaire aligné entre les 5 sources (sinon les proportions par catégorie sont faussées)

### Étape 2 — Décider le ratio
- [ ] Chiffrer la taille du corpus total et par source
- [ ] Choisir 70/15/15 ou autre, justifier

### Étape 3 — Décider la stratégie
- [ ] Reprendre le test Mann-Kendall (comp 2)
- [ ] p > 0.05 : aléatoire, p < 0.05 : temporelle
- [ ] Documenter la preuve
- [ ] Vérifier les périodes couvertes par chaque source

### Étape 4 — Décider la stratification
- [ ] Variable principale : `categorie`
- [ ] Vérifier que les proportions sont respectées à 0.5 point près
- [ ] Vérifier les effectifs par source dans chaque ensemble
- [ ] Ajouter `source` à la stratification si nécessaire

### Étape 5 — Fixer la graine
- [ ] Documenter la graine utilisée
- [ ] Vérifier la reproductibilité en relançant

### Étape 6 — Vérifier l'absence de fuite
- [ ] Aucun ID (`ref_plateforme`, `Code`, `id_acte`, `ID`, `id`) présent dans deux ensembles
- [ ] Aucun bien ne se retrouve dans train et test

### Étape 7 — Sceller le test
- [ ] Écrire dans `docs/justifications.md` : test scellé à partir de maintenant
- [ ] Ne plus l'utiliser avant comp 9

## Ce qu'il faut faire
- Preuve chiffrée pour la stratégie (Mann-Kendall)
- Stratifier par `categorie`
- Vérifier les effectifs par source dans chaque ensemble
- Fixer la graine et la documenter
- Vérifier les proportions dans chaque ensemble
- Vérifier l'absence d'ID dans deux ensembles
- Sceller le test explicitement

## Ce qu'il ne faut pas faire
- Splitter après le feature engineering
- Splitter avec les doublons encore présents
- Ne pas stratifier sur `categorie`
- Ignorer les différences de volume entre sources
- Changer la graine pour améliorer les résultats
- Toucher au test avant comp 9
- Split temporel sans preuve de tendance
- Split aléatoire sans avoir vérifié l'absence de tendance
- Laisser un ID dans deux ensembles

## Ce que tu dois produire
1. Tableau `{ensemble, count, pourcentage}` : train, val, test
2. Tableau des proportions de `categorie` dans chaque ensemble
3. Tableau des effectifs de `source` dans chaque ensemble
4. Preuve de la stratégie : résultat Mann-Kendall et décision
5. Preuve de l'absence d'ID partagé entre ensembles
6. Graine documentée dans `docs/justifications.md`
7. Déclaration formelle : test scellé

## Pièges récapitulés

| Piège | Conséquence |
|---|---|
| Doublons après split | Fuite silencieuse |
| Pas de stratification | Modalités rares absentes |
| Sources inégalement réparties | Validation non représentative |
| Split aléatoire sans test de tendance | Biais temporel non détecté |
| Test non scellé | Estimation finale biaisée |
| Graine non fixée | Non reproductible |
| Graine changée après résultats | Malhonnêteté |
| ID partagé entre ensembles | Fuite silencieuse |

## Transition vers comp 8
Le split est la condition de l'anti-fuite :
- Toutes les transformations qui apprennent des paramètres (imputation, scaler, encodeur) se font désormais sur train only
- Toute variable créée en comp 6 doit être vérifiée : ne contient-elle pas `prix` ?
- Toute feature doit être disponible en production au moment de la prédiction
- Vérifier en particulier que `source` n'a pas été retenue par inadvertance

Le test scellé est la garantie que tu ne peux plus tricher par inadvertance.