# Guide Apprenant — Module 2 ImmoAnalyse

## Objectif du module

Transformer 5 flux bruts hétérogènes (Excel, CSV `;` mojibake, CSV , JSON imbriqué, CSV `;` avec header dupliqué) en un jeu de données préparé, documenté, reproductible, utilisable dans un pipeline de Machine Learning.

Règle absolue : chaque décision \= une preuve chiffrée. Pas de « je pense que », pas de « c'est la méthode ».

## Les 5 sources brutes (à ne jamais modifier)

| Fichier | Format | Schéma clé |
| :---- | :---- | :---- |
| `agence_teranga.xlsx` | Excel, 2 feuilles (`Annonces` \+ `Params`) | `Code`, `Date`, `Region`, `Ville`, `Type`, `Prix_FCFA`, `Surface_m2`, `Chambres`, `SDB`, `Statut` |
| `import_historique.csv` | CSV `;`, mojibake (`Thiï¿½s`) | `ID`, `DateVente`, `Region`, `Ville`, `TypeBien`, `Prix`, `Surface`, `Chambres`, `SallesBain` |
| `notaires.csv` | CSV `,` | `id_acte`, `date_acte`, `region`, `ville`, `type_bien`, `montant_fcfa`, `superficie`, `nb_chambres`, `statut` |
| `particuliers.json` | JSON imbriqué | `id`, `date`, `localisation{region,ville}`, `details{type,transaction,prix,surface}`, `statut` |
| `plateforme_immo_sn.csv` | CSV `;` avec header dupliqué en cours de fichier | 15 colonnes (`ref_plateforme`, `quartier`, `devise`, `description`…) |

Conséquence structurante : il n'y a pas une table d'entrée mais cinq. Une étape 0 de concaténation est obligatoire, avec ajout d'une colonne `source` (texte, valeurs : `agence`, `historique`, `notaires`, `particuliers`, `plateforme`).

## Les référentiels (à ne jamais modifier)

| Fichier | Rôle |
| :---- | :---- |
| `referentiels/referentiel_geographique.csv` | 14 régions × 46 villes |
| `referentiels/referentiel_categories.csv` | 7 catégories \+ synonymes \+ fourchettes prix/surface |
| `referentiels/dictionnaire_donnees.csv` | Définition attendue des 9 champs cibles |
| `referentiels/regles_metier.md` | Règles bloquantes / normalisables / avertissements |

## Sortie attendue (dossier `sortie/`)

| Livrable | Contenu |
| :---- | :---- |
| `sortie/donnees_propres.csv` | Corpus nettoyé et concaténé |
| `sortie/quarantine.csv` | Lignes rejetées \+ raison |
| `sortie/avertissements.csv` | Lignes conservées avec anomalie signalée |
| `sortie/rapport_qualite.md` | Les 6 mesures imposées par `regles_metier.md` |
| `notebooks/02_preparation_analyse.ipynb` | Notebook exécutable de bout en bout |
| `models/pipeline_preparation.joblib` | Pipeline sérialisé |
| `reports/dictionnaire_features.csv` | Variables finales documentées |
| `docs/justifications.md` | Registre des décisions |

## Les 9 compétences — ordre officiel

| \# | Compétence | Fiche |
| :---- | :---- | :---- |
| 1 | Types, distributions, stats descriptives | `01_types_statistiques.md` |
| 2 | EDA \+ viz diagnostiques (par source) | `02_eda.md` |
| 3 | Nettoyage : manquants, doublons, aberrants | `03_traitement_anomalies.md` |
| 4 | Viz de restitution | `04_visualisations.md` |
| 5 | Encodage \+ normalisation | `05_encodage_normalisation.md` |
| 6 | Feature engineering | `06_feature_engineering.md` |
| 7 | Split train/val/test | `07_split_train_val_test.md` |
| 8 | Data leakage | `08_data_leakage.md` |
| 9 | Pipeline reproductible | `09_pipeline_reproductible.md` |

## Démarche — la même pour chaque compétence

1. Comprendre — quelle notion dois-je maîtriser ?  
2. Observer — que disent les 5 sources réelles ?  
3. Mesurer — quel chiffre me donne la réponse ?  
4. Décider — quel choix je fais ?  
5. Justifier — quelle preuve j'écris dans `docs/justifications.md` ?

Si l'une de ces 5 étapes manque, la compétence n'est pas validée.

## Les 10 questions à te poser à chaque étape

1. Quelle question est-ce que je cherche à répondre ?  
2. Quelle source est concernée (les 5 ont des anomalies différentes) ?  
3. Quelle mesure chiffrée y répond ?  
4. Que disent réellement les données ?  
5. Quelle décision je prends ?  
6. Quelle preuve je peux montrer en soutenance ?  
7. Qu'est-ce qui pourrait me faire changer d'avis ?  
8. Quelle règle métier s'applique ici ?  
9. Est-ce que je risque une fuite de données ?  
10. Où est-ce que je documente la décision ?

## Ce qu'il faut faire

- Lire la fiche en entier avant de coder  
- Traiter les 5 sources séparément avant de concaténer  
- Mesurer avant de décider  
- Documenter au moment où tu décides, pas à la fin  
- Respecter l'ordre des compétences  
- Vérifier chaque décision contre les règles métier et le README

## Ce qu'il ne faut pas faire

- Modifier les fichiers de `sources/` ou de `referentiels/`  
- Sauter une compétence  
- Décider sans preuve chiffrée  
- Toucher au test avant la comp 9  
- Considérer une fiche comme « lue » sans avoir répondu à ses questions  
- Considérer que les 5 sources se comportent pareil

## Pièges transverses

| Piège | Conséquence |
| :---- | :---- |
| Traiter avant de mesurer | Nettoyage arbitraire |
| Décider sans chiffrer | Argument non défendable |
| Confondre diagnostic / restitution | Figures incohérentes |
| Fuite de données | Score flatteur → chute en prod |
| Documentation a posteriori | Justification inventée |
| Ignorer le mojibake | Jointures silencieusement cassées |
| Ignorer le header dupliqué | Doublons non vus |

&nbsp;