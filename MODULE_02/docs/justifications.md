
# Justifications des décisions — Module 2

## 1. Définition du problème

- Type de problème : régression.
- Variable cible : prix.
- Nombre d'annonces de vente retenues : 2647.

## 2. Création des variables

- Variables numériques : ['surface', 'surface_log', 'chambres', 'sdb', 'annee', 'mois']
- Variables catégorielles : ['type_bien', 'region']
- Variable créée : surface_par_chambre.

## 3. Séparation des données

- Entraînement : 1852 annonces (69.97 %).
- Validation : 397 annonces (15.00 %).
- Test : 398 annonces (15.04 %).
- Random state : 42.

## 4. Traitement des variables numériques

- Imputation : médiane.
- Normalisation : StandardScaler.
- Justification : limiter l'influence des différences d'échelle
  et conserver les observations atypiques sans les supprimer automatiquement.

## 5. Traitement des variables catégorielles

- Imputation : modalité la plus fréquente.
- Encodage : OneHotEncoder.
- handle_unknown : ignore.

## 6. Prévention des fuites de données

Le préprocesseur est ajusté uniquement sur l'ensemble d'entraînement.
Les ensembles de validation et de test sont transformés sans réapprentissage.

## 7. Reproductibilité

Le préprocesseur est sauvegardé dans :
models/pipeline_preparation.joblib

Le rechargement et la reproduction des transformations ont été vérifiés.
