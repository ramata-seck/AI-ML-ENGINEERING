# Compétence 9 — Pipeline reproductible

## Objectif
Empaqueter tout le prétraitement dans un objet unique, sérialisable, reproductible, qui garantit que les transformations appliquées à l'entraînement seront identiques à celles appliquées en production.

## À la fin, tu dois savoir
- Reconnaître ce qui doit aller dans le pipeline et ce qui doit rester à l'extérieur
- Garantir que le pipeline s'exécute de bout en bout sans intervention manuelle
- Vérifier la reproductibilité : relancer donne les mêmes résultats
- Sérialiser et recharger le pipeline
- Détecter les signes d'un pipeline incomplet ou non reproductible

## Partie A — Pourquoi un pipeline ?

### Question centrale
Si je redonne mes données brutes à quelqu'un d'autre, est-ce qu'il obtiendra le même modèle que moi ?

### Sans pipeline
- Chaque étape (nettoyage, encodage, scaler) est faite à la main
- Un ordre différent donne un résultat différent
- Impossible de reproduire
- Impossible de servir le modèle en production

### Avec pipeline
- Toutes les transformations sont dans un seul objet
- Ordre figé
- Paramètres appris sur train only
- Sérialisable, rechargeable, utilisable en production

### Règle
Le pipeline est la mémoire du prétraitement.
Si une transformation n'est pas dans le pipeline, elle sera oubliée en production.

### Spécificité multi-source
Le pipeline doit inclure l'étape 0 de concaténation des 5 sources, ou documenter explicitement qu'elle est faite en amont avec le fichier de sortie. Ne pas laisser la concaténation dans un notebook qui ne sera jamais rejoué.

## Partie B — Ce qui doit être dans le pipeline

### Question à te poser pour chaque étape
Cette étape apprend-elle des paramètres à partir des données ?

- Si oui : elle doit être dans le pipeline
- Si non : elle peut être à l'extérieur

### Étapes qui apprennent des paramètres, donc dans le pipeline

| Étape | Ce qu'elle apprend |
|---|---|
| OneHotEncoder | Les modalités de `categorie`, `region`, `type_transaction` |
| StandardScaler ou RobustScaler | Moyenne, écart-type, ou médiane et IQR |
| SimpleImputer | Médiane, mode |
| Log transform | Aucun paramètre, peut être à l'extérieur, mais plus propre dans le pipeline |
| Sélection de features | Aucun paramètre, peut être à l'extérieur, mais documenter |

### Décision attendue sur ce corpus
Dans le pipeline :
- Concaténation des 5 sources (ou import de `donnees_propres.csv`)
- Encodage de `categorie`, `region`, `type_transaction`
- Scaler de `surface_log`
- Imputation (si appliquée à ce stade)

Hors pipeline, mais documenté :
- Log sur `prix` (cible)
- Création de `surface_log`
- Alignement du vocabulaire entre sources (fait en comp 3)
- Suppression de `commune`, `statut`, `source`, `date_expiration`, `quartier`, `description` (fait en comp 3 ou 5)

## Partie C — Les 6 vérifications obligatoires

### Vérification 1 — Ordre correct
Le pipeline doit s'exécuter dans un ordre qui respecte les dépendances :
1. Imputation (avant scaler, sinon les NaN cassent le scaler)
2. Encodage
3. Transformation (log)
4. Scaler

Question : si j'inverse deux étapes, est-ce que ça plante ? Est-ce que ça change le résultat ?

### Vérification 2 — Fit sur train only
Rappel comp 5 et 8 : le fit du pipeline se fait sur train. Le transform s'applique à val et test.

Question : si je regarde les paramètres appris du pipeline (moyenne, modalités), est-ce qu'ils correspondent au train seul ?

### Vérification 3 — Reproductibilité
Question centrale : si je relance le pipeline avec la même graine, est-ce que j'obtiens exactement le même résultat ?

Checklist :
- [ ] Graine fixée pour le split (comp 7)
- [ ] Graine fixée pour le modèle (si Random Forest, etc.)
- [ ] Relancer donne les mêmes scores
- [ ] Documenter la graine dans `docs/justifications.md`

Signal d'alerte : deux exécutions successives donnent des scores différents, reproductibilité cassée.

### Vérification 4 — Sérialisation et rechargement
Question : si je sérialise le pipeline et que je le recharge dans un nouvel environnement, est-ce qu'il produit les mêmes prédictions ?

Checklist :
- [ ] Pipeline sérialisé dans `models/pipeline_preparation.joblib`
- [ ] Rechargé dans un notebook séparé
- [ ] Appliqué à un échantillon du test
- [ ] Prédictions identiques aux prédictions d'origine

Signal d'alerte : le rechargement produit une erreur ou des prédictions différentes, le pipeline est incomplet ou dépend d'un état externe.

### Vérification 5 — Cohérence avec la production
Question centrale : en production, je recevrai une seule ligne brute, d'une seule source. Est-ce que le pipeline sait la transformer ?

Checklist :
- [ ] Tester le pipeline sur une seule ligne brute
- [ ] Tester sur une ligne de chaque source (les 5 ont des schémas différents)
- [ ] Vérifier que `handle_unknown="ignore"` protège contre les nouvelles modalités
- [ ] Vérifier qu'aucune transformation ne dépend d'un batch (par exemple, fréquence calculée sur tout le corpus)

Signal d'alerte : le pipeline fonctionne sur un batch mais plante sur une ligne, il dépend d'un état collectif.

### Vérification 6 — Cohérence multi-source
Question : le pipeline traite-t-il les 5 sources de la même façon, ou en privilégie-t-il une ?

Checklist :
- [ ] Le pipeline s'applique aux 5 sources après alignement
- [ ] Aucune transformation ne dépend du fait d'être dans une source particulière
- [ ] Aucune colonne spécifique à une source n'est utilisée (rappel comp 8)
- [ ] Les modalités de `categorie` et `region` couvrent bien les 5 sources

## À faire concrètement

### Étape 1 — Concevoir le pipeline
- [ ] Lister toutes les transformations
- [ ] Identifier celles qui apprennent des paramètres
- [ ] Les mettre dans le pipeline
- [ ] Figer l'ordre

### Étape 2 — Vérifier les 6 critères
- [ ] Ordre correct
- [ ] Fit sur train only
- [ ] Reproductibilité (mêmes scores après relance)
- [ ] Sérialisation et rechargement OK
- [ ] Application sur une ligne brute de chaque source OK
- [ ] Cohérence multi-source OK

### Étape 3 — Documenter
- [ ] Structure du pipeline dans `docs/justifications.md`
- [ ] Graine utilisée
- [ ] Ordre des transformations et pourquoi cet ordre

### Étape 4 — Sérialiser
- [ ] Sauvegarder dans `models/pipeline_preparation.joblib`
- [ ] Documenter la procédure de rechargement

## Ce qu'il faut faire
- Tout ce qui apprend des paramètres va dans le pipeline
- Fit sur train only
- Graine fixée et documentée
- Sérialisation testée (rechargement donne les mêmes prédictions)
- Application sur une ligne testée, pour chaque source
- Ordre documenté
- Étape 0 de concaténation incluse ou documentée

## Ce qu'il ne faut pas faire
- Faire du prétraitement à la main hors pipeline (oubli garanti en production)
- Fit sur val ou test
- Changer la graine entre deux exécutions
- Sérialiser sans tester le rechargement
- Tester uniquement sur un batch sans vérifier le cas d'une ligne
- Utiliser un état externe (une variable calculée ailleurs) sans l'inclure dans le pipeline
- Oublier handle_unknown ignore, crash à la première modalité inconnue
- Ignorer les spécificités des 5 sources dans le test

## Ce que tu dois produire
1. `models/pipeline_preparation.joblib`, pipeline sérialisé
2. Documentation `docs/pipeline.md` :
   - structure (étapes et ordre)
   - paramètres appris sur train only
   - graine fixée
   - procédure de rechargement
3. Preuve des 6 vérifications dans `docs/justifications.md`
4. Section Reproductibilité dans le rapport final

## Pièges récapitulés

| Piège | Conséquence |
|---|---|
| Prétraitement à la main hors pipeline | Oubli en production |
| Fit sur val ou test | Fuite type 3 |
| Graine non fixée | Non reproductible |
| Sérialisation non testée | Pipeline cassé en production |
| Batch-only non testé sur une ligne | Crash en production |
| État externe non inclus | Résultats non reproductibles |
| handle_unknown manquant | Crash sur nouvelle modalité |
| Sources non testées individuellement | Une source peut casser le pipeline |
| Colonnes mono-source dans le pipeline | Fuite type 4 |

## Transition vers comp 10 et 11
Le pipeline est le livrable technique final. Il est évalué en comp 10 (grille) et questionné en comp 11 (soutenance) :
- Grille (comp 10) : présence du fichier joblib, preuve des 6 vérifications, documentation
- Soutenance (comp 11) : montrez-moi que votre pipeline produit les mêmes résultats après rechargement, quel paramètre appris peut fuiter si mal placé, comment votre pipeline gère une ligne de chaque source