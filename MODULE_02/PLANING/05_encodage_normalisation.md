# Compétence 5 — Encodage catégoriel et normalisation numérique

## Objectif
Transformer les colonnes des 5 sources alignées en une matrice numérique utilisable par un modèle, en choisissant le bon encodage et le bon scaler selon la nature de chaque variable et le modèle cible.

## À la fin, tu dois savoir
- Choisir l'encodage adapté à chaque variable catégorielle du corpus aligné
- Choisir le scaler adapté à chaque variable numérique du corpus aligné
- Justifier chaque transformation par le modèle cible
- Garantir l'absence de fuite via fit sur train uniquement
- Détecter les variables qui ne doivent pas être encodées (fuite ou bruit)

## Partie A — Cartographie des variables catégorielles

### Questions à te poser pour chaque variable
1. Combien de modalités ?
2. Y a-t-il un ordre naturel entre les modalités ?
3. La variable est-elle disponible au moment de la prédiction ?
4. La variable est-elle redondante avec une autre ?
5. Quel encodage est adapté : one-hot, binaire, ordinal, frequency, exclure ?

### Le corpus aligné — analyse variable par variable

| Variable | Cardinalité | Ordre | Disponible en prod | Encodage recommandé |
|---|---|---|---|---|
| `type_transaction` | 2 (vente, location) | Non | Oui | Binaire (une seule colonne 0/1) |
| `categorie` | 7 + synonymes | Non | Oui | One-hot (7 colonnes) |
| `region` | 14 | Non | Oui | One-hot (14 colonnes) |
| `commune` | 46 | Non | Oui | Exclure ou frequency encoding |
| `statut` | 4 à 5 selon source | Non | À auditer | Voir piège ci-dessous |
| `source` | 5 (agence, historique, notaires, particuliers, plateforme) | Non | Non | Exclure ou tester en comp 6 |

### Piège spécifique à `statut`
`statut = Vendu` est une information postérieure à la mise en ligne : on ne la connaît pas au moment où on veut prédire le prix. Si tu l'utilises comme feature :
- Le modèle apprend une relation circulaire : si vendu, alors le prix était...
- En production, cette information n'existe pas : chute brutale des performances

Décision attendue : vérifier avec l'énoncé métier si `statut` est connu à la prédiction.
- Si non : exclure la variable (fuite type 2, comp 8)
- Si oui : l'inclure en one-hot

Le corpus contient d'ailleurs 5 vocabulaires différents selon la source (`Vendu`, `VENDU`, `Vente conclue`, `Acte signé`, `En vente`, `Disponible`, `Loué`, `Sous offre`, `Retiré`, `À confirmer`). Cette hétérogénéité confirme que `statut` est une donnée de suivi, pas une caractéristique du bien.

### Piège spécifique à `source`
`source` est un identifiant de flux, pas une caractéristique du bien. En one-hot, il devient un proxy de la qualité du flux, pas du bien.

Décision attendue :
- Exclure `source` du modèle final (ligne de conduite par défaut)
- Si tu veux la tester, mesurer son gain en comp 6 avec le seuil de décision
- Vérifier explicitement qu'elle n'est pas un proxy de `statut` ou de `prix` par fuite type 4 (comp 8)

### Piège spécifique à `commune`
`commune` a 46 modalités dans le référentiel géographique. En one-hot :
- 46 colonnes dont la plupart ont moins de 10 occurrences : bruit et sur-apprentissage
- Le gain attendu en CV est proche de 0 (à vérifier en comp 6)

Décision attendue : exclure `commune` du one-hot. Si elle semble importante, tester en frequency encoding en comp 6 et mesurer le gain.

## Partie B — Cartographie des variables numériques

### Questions à te poser
1. Quelle est la forme de la distribution (symétrique, asymétrique) ?
2. Y a-t-il des outliers conservés après comp 3 ?
3. Le modèle cible est-il sensible à l'échelle ?
4. Faut-il transformer avant de standardiser ?

### Le corpus aligné — analyse variable par variable

| Variable | Distribution | Transformation | Scaler |
|---|---|---|---|
| `prix` (cible) | Fortement asymétrique | log(prix) | Non applicable, c'est la cible |
| `surface` | Étendue (10 à 1500 m²) | log1p(surface) | RobustScaler si outliers conservés, sinon Standard |
| `date` | Temporelle | Extraire `annee` et `mois` | Aucun, ou cyclique si `mois` |

### Comment choisir le scaler

| Question | Si oui | Si non |
|---|---|---|
| Modèle sensible à l'échelle (linéaire, SVM, KNN, réseau) | Standardiser | Arbre, pas besoin |
| Outliers conservés (comp 3) | RobustScaler | StandardScaler |
| Distribution très asymétrique | Log puis standardiser | Standardiser directement |

## Partie C — Les règles absolues

### Fit sur train uniquement
Règle : les paramètres de l'encodeur et du scaler (moyenne, écart-type, modalités) doivent être appris sur le train seulement.

Preuve de non-fuite :
- Moyenne de la variable transformée sur train proche de 0
- Moyenne sur validation différente de 0, mais proche
- Si la moyenne val vaut 0 exactement : fuite, tu as fit sur le tout

### handle_unknown ignore
Le référentiel peut s'agrandir (nouvelle région, nouvelle catégorie). Sans cette option, le pipeline plante à la première modalité inconnue en production.

Décision : obligatoire sur tous les one-hot.

### Ne jamais encoder ce qui est déjà numérique
`surface` n'a pas besoin d'être one-hot. `prix` n'a pas besoin d'être encodé : c'est la cible.

### Aligner le vocabulaire avant d'encoder
Les 5 sources n'ont pas le même vocabulaire pour `categorie`, `statut`, `region`. L'alignement doit être fait en comp 3. Vérifier ici que l'encodage ne crée pas de doublons sémantiques :
- `Villa` et `VILLA` et `villa` doivent être une seule modalité
- `Vente conclue` et `Vendu` doivent être alignés ou distingués explicitement
- `appart` et `Appartement` doivent être une seule modalité

## À faire concrètement

### Étape 1 — Décider pour chaque variable catégorielle
- [ ] Lister les 6 catégorielles (`type_transaction`, `categorie`, `region`, `commune`, `statut`, `source`)
- [ ] Pour chacune : cardinalité, ordre, disponibilité en prod, redondance
- [ ] Écrire la décision : one-hot, binaire, frequency, exclure
- [ ] Justifier par le modèle cible et le risque de fuite

### Étape 2 — Décider pour chaque variable numérique
- [ ] Vérifier la distribution (comp 1)
- [ ] Vérifier la présence d'outliers (comp 3)
- [ ] Choisir : log et standard, log et robust, ou rien
- [ ] Justifier par le modèle cible

### Étape 3 — Auditer `statut`
- [ ] Est-il connu au moment de la prédiction ?
- [ ] Si non : exclure, documenter comme fuite type 2
- [ ] Si oui : inclure en one-hot
- [ ] Vérifier que les 5 vocabulaires des sources ne se contredisent pas après alignement

### Étape 4 — Auditer `source`
- [ ] Vérifier qu'elle n'est pas un proxy de `statut` ou de `prix`
- [ ] Décider : exclue (par défaut), ou testée en comp 6
- [ ] Documenter le choix

### Étape 5 — Vérifier la non-fuite
- [ ] Fit uniquement sur le train
- [ ] Moyenne train proche de 0, moyenne val différente de 0 (preuve)
- [ ] Documenter dans `docs/justifications.md`

## Ce qu'il faut faire
- Auditer `statut` avant tout
- Auditer `source` avant tout
- Exclure `commune` du one-hot (ou frequency si testé)
- Binaire pour `type_transaction`, pas one-hot
- One-hot pour `categorie` et `region`
- Log puis scaler sur `surface`
- Log sur `prix` (cible)
- handle_unknown ignore partout
- Fit sur train, transform sur val et test
- Vérifier la preuve de non-fuite (moyenne val différente de 0)
- Vérifier que le vocabulaire est aligné entre les 5 sources

## Ce qu'il ne faut pas faire
- Label encoding sur `categorie`
- One-hot sur `commune` (46 colonnes de bruit)
- Inclure `statut` sans auditer
- Inclure `source` sans auditer
- Fit sur tout le jeu
- Standardiser les one-hot
- Oublier handle_unknown ignore
- Log sur `prix` sans vérifier qu'aucune valeur n'est <= 0
- Encoder `type_transaction` en one-hot complet (2 colonnes redondantes)
- Laisser deux modalités sémantiquement identiques dans `categorie` à cause d'un alignement partiel

## Ce que tu dois produire
1. Tableau `{variable, type, cardinalité, ordre, dispo prod, encodage ou scaler, justification}`
2. Décision documentée sur `statut` : gardé ou exclu, avec justification métier
3. Décision documentée sur `source` : exclue ou testée, avec justification
4. Décision documentée sur `commune` : exclue ou frequency, avec justification
5. Preuve de non-fuite : moyenne train proche de 0, moyenne val différente de 0
6. Entrées dans `docs/justifications.md`

## Pièges récapitulés

| Piège | Conséquence |
|---|---|
| Label encoding `categorie` | Faux ordre appris |
| One-hot `commune` | 46 colonnes de bruit |
| `statut` non audité | Fuite type 2 |
| `source` non audité | Fuite type 4 |
| Fit global | Fuite silencieuse |
| Standardiser one-hot | Perte de sens |
| Sans handle_unknown | Crash en production |
| One-hot `type_transaction` | Redondance |
| Vocabulaire non aligné | Doublons sémantiques dans l'encodage |

## Transition vers comp 6
Le choix d'encodage détermine quelles features sont candidates pour le feature engineering :
- `commune` exclue : ne pas tester de distance à la commune en comp 6
- `statut` exclu : ne pas envisager d'interaction avec lui
- `source` exclue : ne pas tester d'interaction avec elle
- `surface` transformée : les interactions se font sur `surface_log`, pas sur `surface` brute
- `categorie` one-hot : les interactions se font avec les modalités, pas avec un label