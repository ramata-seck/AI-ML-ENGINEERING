# Compétence 8 — Éviter les fuites de données

## Objectif
Auditer tout le pipeline pour détecter et éliminer toute information disponible à l'entraînement mais pas en production. Une fuite donne des scores flatteurs en développement et une chute brutale en production.

## À la fin, tu dois savoir
- Reconnaître les 4 types de fuite
- Auditer chaque feature contre les 4 types
- Détecter une fuite par le score (gain proche de +0.99 est un signal d'alerte)
- Corriger ou exclure la feature fautive
- Documenter l'audit dans `docs/justifications.md`

## Partie A — Qu'est-ce qu'une fuite ?

### Question centrale
Est-ce que cette information serait disponible au moment où je dois prédire ?

Si la réponse est non : c'est une fuite.

### Conséquence concrète

| Environnement | Score observé |
|---|---|
| Développement (avec fuite) | R² de 0.99 |
| Production (sans fuite) | R² de 0.40 |

Le score en développement ne veut plus rien dire. Le modèle a appris un raccourci qui ne généralise pas.

### Question à te poser pour chaque feature
1. Est-elle calculable au moment de la mise en ligne de l'annonce ?
2. Contient-elle la cible ou une de ses transformations ?
3. Révèle-t-elle implicitement la source des données ?
4. A-t-elle été construite après que la cible soit connue ?

## Partie B — Les 4 types de fuite, avec cas réels du corpus

### Fuite type 1 — Variable construite à partir de la cible

Définition : une feature qui contient directement ou indirectement `prix`.

Cas réels sur ce corpus :

| Feature | Pourquoi c'est une fuite |
|---|---|
| `prix_m2` (prix divisé par surface) | Contient `prix` |
| `ratio_prix_fourchette` (prix divisé par prix_max_indicatif) | Contient `prix` |
| `prix_normalise` | Contient `prix` |
| `log_prix` comme feature | C'est la cible elle-même |

Test : vérifier qu'aucune feature ne contient `prix` dans son nom ou son calcul.

Signal d'alerte : gain proche de +0.99 lors de la mesure en comp 6.

Décision : exclure systématiquement.

### Fuite type 2 — Variable postérieure à la prédiction

Définition : une feature dont la valeur n'est connue qu'après l'événement qu'on veut prédire.

Cas réel sur ce corpus :

| Feature | Pourquoi c'est une fuite |
|---|---|
| `statut` (notamment `Vendu`, `Vente conclue`, `Acte signé`, `Loué`) | On ne le sait qu'après la vente ou la location. Au moment de la mise en ligne, on ne peut pas prédire si elle sera vendue. |

Le corpus contient 5 vocabulaires différents pour `statut` selon la source (`Vendu`, `VENDU`, `Vente conclue`, `Acte signé`, `En vente`, `Disponible`, `Loué`, `Sous offre`, `Retiré`, `À confirmer`). Cette hétérogénéité confirme que `statut` est une donnée de suivi, pas une caractéristique du bien.

Question à te poser : au moment où l'annonce est publiée, est-ce que je connais déjà cette valeur ?

Décision attendue :
- Si `statut` est postérieur : exclure de la modélisation
- Documenter comme fuite type 2 dans `docs/justifications.md`
- Ne pas l'exclure du nettoyage : il reste utile au reporting et à la quarantaine (date future + statut vendu)

### Fuite type 3 — Transformation ajustée sur tout le corpus

Définition : un scaler, un encodeur ou un imputeur fit sur l'ensemble des données (train, val, test).

Cas réels sur ce corpus :

| Transformation | Fuite si |
|---|---|
| StandardScaler sur `surface_log` | fit sur tout le jeu |
| OneHotEncoder sur `categorie` | fit sur tout le jeu |
| Imputation de `surface` | médiane calculée sur tout le jeu |
| Log transform | OK, déterministe, pas de paramètre appris |
| Alignement du vocabulaire `categorie` entre sources | OK si fait en comp 3, avant le split, avec une règle déterministe |

Signal d'alerte : la moyenne de la variable transformée sur validation est exactement 0 (au lieu de proche de 0).

Décision : fit toujours sur train only, transform sur val et test.

### Fuite type 4 — Variable qui révèle la source

Définition : une feature qui contient implicitement l'information de `source` (ou de toute variable non disponible en production).

Cas réels sur ce corpus :

| Feature | Pourquoi c'est une fuite |
|---|---|
| `source` en one-hot | Identifiant de flux, pas une caractéristique du bien |
| `surface_manquant` (indicateur) | Si les manquants sont concentrés sur une source, l'indicateur est cette source |
| Tout indicateur de manque corrélé à `source` | Révèle la source indirectement |
| `date_expiration` (spécifique à `plateforme`) | N'existe que dans une source, révèle la source |
| `quartier` (spécifique à `plateforme`) | N'existe que dans une source, révèle la source |
| `description` (spécifique à `plateforme`) | N'existe que dans une source, révèle la source |

Question à te poser : si je crée un indicateur « cette colonne manque », est-ce que le fait de manquer est aléatoire ou corrélé à la source ?

Test : croiser `isna()` avec `source`. Si 100 pourcent d'une source manque, l'indicateur est la source.

Décision :
- Ne pas créer d'indicateur de manque si le manque est corrélé à `source`
- Ne pas inclure `source` en feature (ligne de conduite par défaut)
- Retirer les colonnes spécifiques à une seule source (`date_expiration`, `quartier`, `description`) avant de concaténer

## Partie C — Le test du score

### Règle simple
R² supérieur à 0.95 sur une prédiction immobilière est suspect.
Le marché immobilier est bruité, aucune combinaison de features normales ne donne 0.99.

### Que faire si le score est suspicieusement bon
1. Lister toutes les features utilisées
2. Vérifier si l'une contient `prix` dans son calcul
3. Vérifier si l'une est postérieure à la prédiction
4. Vérifier si une transformation a été fit sur tout le jeu
5. Vérifier si une feature est corrélée à `source`

### Cas spécifique au corpus
Si tu testes `source` en feature et que le score saute de +0.05 ou plus, ce n'est pas un signal que la source est utile : c'est un signal qu'elle capture un artefact de flux. Vérifier :
- Est-ce que la source corrèle avec `prix` uniquement parce que les distributions diffèrent ?
- Est-ce que la source corrèle avec `statut` (par exemple, seule `notaires` contient `Acte signé`) ?
- En production, sur un bien nouveau, la source sera connue, mais la relation source-prix ne se reproduira peut-être pas

## À faire concrètement

### Audit 1 — Features construites
- [ ] Lister toutes les features du modèle final
- [ ] Pour chaque : est-elle calculable au moment de la mise en ligne ?
- [ ] Aucune ne contient `prix` ?

### Audit 2 — Features temporelles
- [ ] `statut` est-il disponible avant la vente ?
- [ ] `date` est bien antérieure à la vente ?
- [ ] Aucune feature n'utilise une info post-vente ?
- [ ] Aucune date future n'a été conservée par erreur (fréquent dans `plateforme`)

### Audit 3 — Transformations
- [ ] Tous les fit se font sur train only
- [ ] Moyenne train proche de 0, moyenne val différente de 0 (preuve)
- [ ] Aucun imputeur ajusté globalement
- [ ] Alignement du vocabulaire fait avant le split (déterministe) et non après (apprentissage)

### Audit 4 — Features cachées
- [ ] Aucun indicateur de manque corrélé à `source`
- [ ] `source` n'est pas une feature
- [ ] Pas de one-hot de `source`
- [ ] Colonnes spécifiques à une seule source retirées : `date_expiration`, `quartier`, `description`

### Audit 5 — Test du score
- [ ] Si R² supérieur à 0.95 : investiguer immédiatement
- [ ] Si `prix_m2` a été testé : gain proche de +0.99, exclu
- [ ] Si `source` a été testée : gain et décision documentés

## Ce qu'il faut faire
- Auditer chaque feature contre les 4 types
- Exclure `statut` si postérieur à la prédiction
- Fit sur train only systématiquement
- Ne pas créer d'indicateur de manque si corrélé à `source`
- Ne jamais utiliser `source` comme feature par défaut
- Retirer les colonnes spécifiques à une source avant concaténation
- Documenter chaque audit dans `docs/justifications.md`
- Vérifier la preuve de non-fuite (moyenne val différente de 0)

## Ce qu'il ne faut pas faire
- Se réjouir d'un R² de 0.99 sans investiguer
- Garder `statut` en pensant qu'il aide le modèle
- Créer `surface_manquant` sans vérifier le croisement avec `source`
- Fit un scaler sur train, val et test
- Utiliser `source` en one-hot
- Ignorer une feature dont l'utilité est trop forte
- Laisser `date_expiration`, `quartier`, `description` dans le corpus final : ce sont des marqueurs de source

## Ce que tu dois produire
1. Tableau d'audit `{feature, type de fuite potentiel, statut (OK, exclue, corrigée), justification}`
2. Preuve de non-fuite : moyenne train proche de 0, moyenne val différente de 0
3. Preuve de détection : `prix_m2` donne +0.99, exclu
4. Décision documentée sur `statut` (exclu ou gardé avec justification)
5. Décision documentée sur `source` (exclue ou testée avec justification)
6. Décision documentée sur les colonnes spécifiques à une source
7. Entrées dans `docs/justifications.md`

## Pièges récapitulés

| Piège | Type | Conséquence |
|---|---|---|
| `prix_m2` | 1 | Mirage de +0.99 |
| `statut` non audité | 2 | Chute en production |
| Fit global | 3 | Optimisme silencieux |
| Indicateur de manque | 4 | Proxy source |
| `source` en feature | 4 | Proxy de flux |
| Colonnes mono-source | 4 | Révèlent la source |
| R² de 0.99 accepté sans audit | Tous | Modèle inutilisable en production |

## Transition vers comp 9
L'audit anti-fuite conditionne la structure du pipeline (comp 9) :
- Toutes les transformations ajustables sont dans le pipeline, après le split
- Aucune feature dérivée de `prix` n'est ajoutée
- `statut`, si exclu, ne réapparaît pas dans le pipeline final
- `source` n'apparaît pas dans le pipeline final
- Les colonnes mono-source ont été retirées avant la concaténation, elles ne sont pas dans le pipeline
- Le pipeline reproduit exactement les conditions de la production