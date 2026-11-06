# Décisions de traitement et règles de qualité — ImmoAnalyse

Ce document présente les principales décisions prises lors du nettoyage des cinq sources de données immobilières.

L'objectif est de rendre les traitements compréhensibles, cohérents et reproductibles.

## 1. Organisation générale

Les cinq sources sont traitées individuellement à l'aide de scripts dédiés.

Les fonctions communes sont regroupées dans `outils.py` et `Traitement/traitement_commun.py` afin d'appliquer les mêmes règles lorsque cela est pertinent.

Chaque traitement produit trois résultats :

- Les lignes conservées.
- Les lignes mises en quarantaine.
- Un rapport de qualité.

Le pipeline rassemble ensuite les résultats.

## 2. Normalisation des données

### 2.1. Normalisation du texte

Les textes sont normalisés afin de faciliter les comparaisons et les rapprochements.

Les traitements communs prennent notamment en charge :

- La suppression des espaces inutiles.
- La normalisation des chaînes de caractères.
- La comparaison de valeurs équivalentes.
- La prise en compte d'alias lorsque des référentiels sont disponibles.

### 2.2. Normalisation des catégories

Les catégories sont rapprochées des valeurs présentes dans les référentiels.

Cette règle concerne notamment :

- Les régions et les villes.
- Les types de biens.
- Les statuts.
- Les types de transaction.

Une valeur inconnue n'est pas automatiquement considérée comme valide. Son traitement dépend du caractère bloquant ou non de la règle concernée.

### 2.3. Normalisation des dates

Les dates sont converties vers un format ISO lorsque leur interprétation est possible.

Les états de traitement distinguent notamment :

- `ok` : date valide.
- `corrige` : date interprétée et normalisée.
- `ambigu` : plusieurs interprétations sont possibles.
- `absent` : valeur manquante.
- `invalide` : date impossible à interpréter.

Les dates invalides ou impossibles sont mises en quarantaine lorsqu'elles constituent une anomalie bloquante.

### 2.4. Normalisation des prix

Les prix sont convertis en valeurs numériques.

Les traitements prennent en compte les formats rencontrés dans les sources, notamment :

- Les montants exprimés en FCFA.
- Les séparateurs de milliers.
- Les virgules et les points.
- Les expressions en millions ou en milliards.

Une valeur qui ne peut pas être interprétée correctement n'est pas convertie arbitrairement.

### 2.5. Normalisation des superficies

Les superficies sont converties en valeurs numériques lorsque leur interprétation est suffisamment fiable.

Les unités et les formats rencontrés sont pris en compte.

Les valeurs ambiguës ne sont pas transformées silencieusement.

### 2.6. Autres champs

Des fonctions communes permettent également de normaliser :

- Les statuts des biens.
- Les périodicités.
- Les devises.
- Les nombres entiers.
- Les types de transaction.

Les corrections sont consignées afin de garder une trace des transformations effectuées.

## 3. Gestion des valeurs manquantes et invalides

Toutes les valeurs manquantes ne provoquent pas automatiquement une mise en quarantaine.

La décision dépend du champ concerné et de son importance pour l'exploitation de la donnée.

Une anomalie est bloquante lorsqu'elle empêche de conserver une ligne suffisamment fiable.

Les anomalies non bloquantes peuvent être conservées avec un avertissement.

Chaque ligne mise en quarantaine doit être accompagnée d'un motif.

## 4. Gestion des valeurs atypiques

Une valeur atypique n'est pas nécessairement une erreur.

Les valeurs sont examinées en tenant compte :

- Des caractéristiques du bien.
- Du type de bien.
- Des référentiels disponibles.
- Des plages indicatives de prix et de superficie.
- De la cohérence des autres informations.

Les plages indicatives servent à signaler des valeurs qui méritent une vérification.

Elles ne doivent pas conduire à supprimer automatiquement une donnée potentiellement légitime.

## 5. Gestion des doublons

Le traitement distingue deux situations.

### 5.1. Doublons exacts

Les doublons exacts sont identifiés à partir des colonnes de comparaison définies dans le traitement commun.

Une ligne est signalée lorsqu'une ligne précédente présente les mêmes valeurs sur ces attributs.

### 5.2. Conflits d'identifiants

Un conflit est signalé lorsque plusieurs lignes possèdent le même identifiant local, mais présentent des informations différentes.

Ces situations sont conservées pour arbitrage.

### 5.3. Décision de traitement

Les doublons et les conflits sont signalés dans les résultats et les rapports.

Ils ne sont pas supprimés automatiquement à ce stade.

La décision finale de conservation devra être prise lors de la fusion des différentes sources, en tenant compte de leur provenance et de la fiabilité des informations.

## 6. Mise en quarantaine

Une ligne est mise en quarantaine lorsqu'elle présente une anomalie bloquante.

Chaque ligne écartée conserve son motif de quarantaine afin de permettre une vérification ultérieure.

Lors de la dernière exécution :

| Source | Conservées | Quarantaine |
|---|---:|---:|
| Plateforme | 859 | 16 |
| Historique | 518 | 10 |
| Particuliers | 599 | 132 |
| Notaires | 390 | 20 |
| Agence Teranga | 631 | 9 |
| **Total** | **2 997** | **187** |

## 7. Traçabilité des traitements

Les fonctions communes permettent de suivre les valeurs brutes et les valeurs normalisées.

Les états de traitement, corrections, avertissements et motifs de quarantaine sont utilisés pour documenter les décisions prises.

Cette traçabilité permet de comprendre pourquoi une valeur a été corrigée, conservée avec un avertissement ou mise en quarantaine.

## 8. Bilan global

Sur les 3 184 lignes reçues :

- 2 997 lignes ont été conservées.
- 187 lignes ont été mises en quarantaine.
- Le taux de conservation est de 94,13 %.
- Le taux de quarantaine est de 5,87 %.

Le bilan est vérifié par le pipeline :

**Lignes reçues = lignes conservées + lignes en quarantaine.**

## 9. Points restant à améliorer

- Documenter plus précisément les règles propres à chaque source.
- Formaliser les critères de rapprochement entre sources.
- Définir une stratégie de résolution des conflits d'identifiants.
- Produire un rapport global complémentaire au format Markdown.
- Continuer à enrichir les tests automatisés.
