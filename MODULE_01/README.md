# ImmoAnalyse — Pipeline de nettoyage et de qualité des données immobilières

## 1. Présentation du projet

ImmoAnalyse est un projet de traitement et de contrôle de la qualité de données immobilières au Sénégal.

Il a pour objectif de regrouper et de nettoyer plusieurs sources de données immobilières afin d'obtenir un jeu de données cohérent, structuré et exploitable pour de futures analyses.

Le projet repose sur un pipeline Python qui applique des règles communes de normalisation, de validation et de contrôle de qualité aux différentes sources.

## 2. Objectifs

Le pipeline vise à :

- Lire les différentes sources de données.
- Analyser leur qualité : valeurs manquantes, doublons, types et distributions.
- Normaliser les données selon des règles communes.
- Identifier les valeurs invalides ou ambiguës.
- Mettre en quarantaine les lignes qui ne respectent pas les règles bloquantes.
- Repérer les doublons et les conflits d'identifiants.
- Produire des fichiers de données propres, de quarantaine et des rapports de qualité.
- Garantir la reproductibilité du traitement.

## 3. Sources de données

Le projet traite cinq sources :

| Source | Lignes reçues |
|---|---:|
| Plateforme | 875 |
| Historique | 528 |
| Particuliers | 731 |
| Notaires | 410 |
| Agence Teranga | 640 |
| **Total** | **3 184** |

Les données et les référentiels sont organisés dans le dossier `Dossier/`.

## 4. Architecture du projet

```text
Module_01/
│
├── Dossier/
│   └── donnees_extraites/
│       └── immoanalyse_dataset/
│           ├── sources/
│           └── referentiels/
│
├── Traitement/
│   ├── pipeline.py
│   ├── traitement_commun.py
│   ├── traitement_plateforme.py
│   ├── traitement_historique.py
│   ├── traitement_particuliers.py
│   ├── traitement_notaires.py
│   └── traitement_agence.py
│
├── Tests/
│   ├── test_outils.py
│   └── test_traitements.py
│
├── Sortie/
│
├── outils.py
├── requirements.txt
├── README.md
└── DECISIONS.md
```

### Rôle des principaux fichiers

- `outils.py` : regroupe les fonctions communes de normalisation, de conversion et de validation.
- `traitement_commun.py` : contient les fonctions partagées par les traitements individuels.
- `traitement_*.py` : contient le traitement propre à chaque source.
- `pipeline.py` : orchestre les cinq traitements et rassemble les résultats.
- `Tests/` : contient les tests automatisés.
- `Sortie/` : reçoit les fichiers produits par le pipeline.

## 5. Installation

### Prérequis

- Python 3
- pip

Depuis la racine du projet, installer les dépendances :

```bash
python3 -m pip install -r requirements.txt
```

## 6. Exécution du pipeline

Depuis la racine du projet :

```bash
python3 Traitement/pipeline.py
```

Le pipeline lance successivement les traitements des cinq sources, rassemble les résultats et vérifie le bilan global.

Les chemins des données et des sorties doivent être résolus à partir du dossier racine du projet.

## 7. Résultats obtenus

Lors de la dernière exécution complète :

| Indicateur | Résultat |
|---|---:|
| Lignes reçues | 3 184 |
| Lignes conservées | 2 997 |
| Lignes en quarantaine | 187 |
| Taux de conservation | 94,13 % |
| Taux de mise en quarantaine | 5,87 % |

La vérification du bilan est positive :

**2 997 + 187 = 3 184 lignes.**

### Fichiers globaux générés

Dans le dossier `Sortie/` :

| Fichier | Description |
|---|---|
| `donnees_propres.csv` | Ensemble des lignes conservées après traitement |
| `quarantaine.csv` | Lignes écartées avec leur motif de mise en quarantaine |
| `rapport_qualite.csv` | Rapports de qualité des différentes sources |

Des sous-dossiers contiennent également les résultats individuels de chaque source.

## 8. Tests automatisés

Les tests sont réalisés avec `pytest`.

Pour les exécuter depuis la racine du projet :

```bash
python3 -m pytest
```

Les tests couvrent notamment les fonctions communes de normalisation, de conversion, de validation et les traitements.

Lors de la dernière vérification, tous les tests passaient.

## 9. Limites

- Les règles de normalisation dépendent des informations disponibles dans les sources et les référentiels.
- Les valeurs atypiques ne sont pas nécessairement des erreurs : elles doivent être examinées selon leur contexte.
- Les doublons et les conflits d'identifiants sont signalés pour permettre un arbitrage lors de la fusion.
- Les données mises en quarantaine ne sont pas supprimées : elles sont conservées avec un motif.
- Le rapport global est actuellement exporté au format CSV.

## 10. Perspectives

Les prochaines améliorations pourront porter sur :

- L'enrichissement des tests automatisés.
- L'amélioration de la documentation des règles de qualité.
- La génération d'un rapport global au format Markdown.
- La fusion contrôlée des données issues des différentes sources.
- La préparation des données pour les analyses statistiques et la modélisation.

---
Projet réalisé dans le cadre d'un travail pratique sur le nettoyage et la qualité des données immobilières.