# Grille d'évaluation — Module 2 ImmoAnalyse

## Objectif
Fournir une grille transparente pour évaluer le rendu final. Chaque critère est observable et mesurable. Un apprenant doit pouvoir s'auto-évaluer avant de rendre.

## À la fin, tu dois savoir
- Comprendre comment tu seras évalué
- Vérifier avant de rendre que chaque critère est satisfait
- Prioriser les critères à fort coefficient
- Identifier les critères éliminatoires

## Structure de l'évaluation

| Bloc | Poids | Composante |
|---|---|---|
| A. Conformité du rendu | 10 pourcent | Livrables présents, format, reproductibilité |
| B. Compétences techniques | 55 pourcent | 9 compétences, pondérées selon complexité |
| C. Qualité de la documentation | 15 pourcent | `justifications.md`, `dictionnaire_features.csv` |
| D. Rapport final | 10 pourcent | Structure, figures, conclusions |
| E. Soutenance | 10 pourcent | Questions orales (comp 11) |

## A. Conformité du rendu (10 pourcent)

### Critères éliminatoires (0 si manquant)
- [ ] `models/pipeline_preparation.joblib` présent et rechargeable
- [ ] `notebooks/02_preparation_analyse.ipynb` exécutable de bout en bout sans intervention
- [ ] `docs/justifications.md` présent (au moins une entrée par décision)
- [ ] `sources/` et `referentiels/` non modifiés
- [ ] `sortie/` contient les trois fichiers propres, quarantaine, avertissements

### Critères de qualité

| Critère | Points |
|---|---|
| Tous les livrables présents | 3 |
| Notebook exécutable sans erreur | 3 |
| Reproductibilité (graine fixée, mêmes scores) | 2 |
| Format des CSV respecté | 1 |
| Nomenclature des fichiers respectée | 1 |

## B. Compétences techniques (55 pourcent)

| # | Compétence | Poids | Ce qui est vérifié |
|---|---|---|---|
| 1 | Types et stats | 5 pourcent | Types corrects par source, skew chiffré, choix de cible justifié |
| 2 | EDA et viz diagnostiques | 6 pourcent | 3 à 5 insights actionnables, tests statistiques, Simpson testé, qualité par source |
| 3 | Nettoyage | 12 pourcent | 3 fichiers produits, 6 mesures produites, mojibake corrigé, header dupliqué filtré, doublons d'ID arbitrés |
| 4 | Viz de restitution | 6 pourcent | V1 à V6 produites, conclusions chiffrées, lien avec comp 3 |
| 5 | Encodage et normalisation | 8 pourcent | Choix justifiés, `statut` audité, `source` auditée, `commune` exclue, preuve non-fuite |
| 6 | Feature engineering | 6 pourcent | 3 à 5 candidates, gains chiffrés, test de fuite documenté, `source` testée |
| 7 | Split | 4 pourcent | Mann-Kendall, stratification par catégorie, vérification par source, graine fixée, test scellé |
| 8 | Anti-fuite | 6 pourcent | 4 types audités, `prix_m2` exclu, `statut` décidé, `source` décidée, colonnes mono-source retirées |
| 9 | Pipeline | 4 pourcent | 6 vérifications documentées, sérialisation testée, cohérence multi-source |

### Détail par compétence — critères observables

Comp 3 — Nettoyage (12 pourcent)
- [ ] `quarantine.csv`, `avertissements.csv`, `donnees_propres.csv` présents (3)
- [ ] 6 mesures obligatoires produites (3)
- [ ] Mécanisme des manquants identifié par source (2)
- [ ] Mojibake corrigé sur `historique` (2)
- [ ] Header dupliqué filtré sur `plateforme` (1)
- [ ] Doublons d'ID arbitrés (1)

Comp 5 — Encodage (8 pourcent)
- [ ] Tableau de décision par variable (2)
- [ ] `statut` audité et décidé avec justification métier (2)
- [ ] `source` audité et décidée (1)
- [ ] `commune` exclue ou frequency justifié (1)
- [ ] Preuve non-fuite (moyenne val différente de 0) (2)

Comp 8 — Anti-fuite (6 pourcent)
- [ ] Les 4 types audités (2)
- [ ] `prix_m2` testé et exclu (1)
- [ ] `statut` audité (1)
- [ ] `source` auditée (1)
- [ ] Colonnes mono-source retirées (1)

## C. Qualité de la documentation (15 pourcent)

### `docs/justifications.md`

| Critère | Points |
|---|---|
| Chaque décision a une preuve chiffrée | 6 |
| Les décisions de nettoyage sont tracées (corrigé, quarantaine, averti) | 3 |
| Le test de fuite de comp 6 est documenté | 2 |

### `reports/dictionnaire_features.csv`

| Critère | Points |
|---|---|
| Toutes les features utilisées sont documentées | 2 |
| Type, transformation, justification par feature | 2 |

## D. Rapport final (10 pourcent)

Structure attendue :
1. Introduction : objectif, corpus (5 sources), démarche (1 point)
2. Comp 1 et 2 : types, EDA, insights (1 point)
3. Comp 3 : nettoyage avec les 6 mesures (2 points)
4. Comp 4 : V1 à V6 avec conclusions chiffrées (2 points)
5. Comp 5 et 6 : encodage, features, décisions (2 points)
6. Comp 7, 8, 9 : split, anti-fuite, pipeline (1 point)
7. Conclusion : bilan et limites (1 point)

Critères de lisibilité : figures titrées, axes avec unités, conclusions sous chaque figure.

## E. Soutenance (10 pourcent)

| Critère | Points |
|---|---|
| Comprend et défend chaque décision de nettoyage | 2 |
| Explique le mojibake et pourquoi il faut le corriger avant les jointures | 1 |
| Explique le test de fuite et pourquoi `prix_m2` est exclu | 1 |
| Justifie le split (aléatoire, temporel, stratifié) et la vérification par source | 2 |
| Montre que le pipeline est reproductible | 1 |
| Explique comment le pipeline gère une ligne de chaque source | 1 |
| Reconnaît ses limites (ce qu'il n'a pas fait) | 1 |
| Répond à la question piège sur `source` | 1 |

Voir `11_questions_soutenance.md` pour la liste détaillée.

## Notation finale

| Niveau | Score | Signification |
|---|---|---|
| Excellent | 90 à 100 | Toutes les compétences validées, documentation complète, soutenance convaincante |
| Très bien | 80 à 89 | Compétences techniques solides, 1 ou 2 critères mineurs incomplets |
| Bien | 70 à 79 | Compétences de base validées, documentation partielle |
| Passable | 60 à 69 | Compétences de base validées, plusieurs décisions non justifiées |
| Insuffisant | Moins de 60 | Une compétence majeure non validée ou critère éliminatoire manquant |

## Auto-évaluation avant de rendre

### Checklist critique
- [ ] Notebook exécutable de bout en bout
- [ ] Tous les livrables présents
- [ ] Chaque décision de `justifications.md` a un chiffre
- [ ] Test de fuite documenté (comp 6)
- [ ] Pipeline sérialisé et rechargé avec succès
- [ ] Les 6 figures V1 à V6 présentes avec conclusions
- [ ] `statut` audité (comp 5)
- [ ] `source` auditée (comp 5 et 6)
- [ ] `commune` exclue ou justifiée
- [ ] Split scellé (test non touché)
- [ ] Graine fixée
- [ ] Mojibake corrigé sur `historique`
- [ ] Header dupliqué filtré sur `plateforme`
- [ ] Doublons d'ID arbitrés sur `plateforme`
- [ ] Colonnes mono-source retirées (`date_expiration`, `quartier`, `description`)

### Ce qui fait perdre le plus de points
1. Notebook non exécutable : -10 points automatique
2. Décisions non justifiées : jusqu'à -15 points
3. `prix_m2` conservé dans le modèle : -6 points (fuite type 1)
4. `statut` non audité : -2 points (comp 5)
5. `source` non auditée : -2 points (comp 5 et 6)
6. Pipeline non sérialisé : -4 points (comp 9)
7. Fichiers `sources/` ou `referentiels/` modifiés : -10 points (violation du README)
8. Mojibake non corrigé : -3 points (comp 3)

## Ce qu'il faut faire
- Relire la grille avant de rendre
- Vérifier les critères éliminatoires en premier
- Auto-évaluer chaque compétence avec la checklist
- Documenter les limites dans la conclusion

## Ce qu'il ne faut pas faire
- Rendre sans avoir relancé le notebook de bout en bout
- Compter sur la chance pour les critères éliminatoires
- Négliger `justifications.md` (15 pourcent de la note)
- Oublier la preuve de non-fuite
- Rendre un pipeline non testé
- Modifier les fichiers sources ou référentiels