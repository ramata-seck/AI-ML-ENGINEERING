# Parcours AI/ML Engineering

Mon parcours d'apprentissage pour devenir capable de préparer des données, développer et évaluer des modèles de Machine Learning, construire des applications d'IA générative et mettre ces solutions en production.

**Progression :** Python et données → Machine Learning → Deep Learning et NLP → LLM et applications IA → automatisation → déploiement et MLOps.

## Suivi de progression

| # | Module | Statut |
|---|--------|--------|
| 1 | Python pour l'IA et le Machine Learning | ✅ Terminé |
| 2 | Préparation et analyse des données | ✅ Terminé |
| 3 | Machine Learning | ⬜ À faire |
| 4 | Évaluation et amélioration des modèles | ⬜ À faire |
| 5 | Deep Learning | ⬜ À faire |
| 6 | NLP : traitement du langage naturel | ⬜ À faire |
| 7 | LLM et IA générative | ⬜ À faire |
| 8 | Prompt Engineering et API de modèles d'IA | ⬜ À faire |
| 9 | Embeddings et recherche sémantique | ⬜ À faire |
| 10 | RAG : génération augmentée par récupération | ⬜ À faire |
| 11 | Chatbots et assistants IA | ⬜ À faire |
| 12 | Automatisation et agents IA | ⬜ À faire |
| 13 | Déploiement et MLOps | ⬜ À faire |
| — | Projet final | ⬜ À faire |

## Méthode de travail

Chaque module suit la même démarche :

1. **Comprendre** : assimiler les concepts et le fonctionnement des méthodes.
2. **Pratiquer** : réaliser des exercices ciblés et manipuler les outils.
3. **Expérimenter** : comparer les approches, analyser les erreurs et justifier les choix.
4. **Livrer** : produire un mini-projet testé, documenté et reproductible.

## Les modules

### Module 1 — Python pour l'IA et le Machine Learning
- **Objectif :** acquérir les bases de programmation pour manipuler des données et développer des solutions d'IA.
- **À apprendre :** bases de Python (variables, types, conditions, boucles, fonctions, exceptions), structures de données, programmation modulaire et POO, NumPy, Pandas, fichiers CSV/JSON/Excel, notebooks Jupyter, environnements virtuels.
- **Outils :** Python, NumPy, Pandas, Jupyter Notebook.
- **Résultat attendu :** des scripts Python capables de charger, manipuler, analyser et exporter des données.

### Module 2 — Préparation et analyse des données
- **Objectif :** transformer des données brutes en données fiables pour l'entraînement des modèles.
- **À apprendre :** statistiques descriptives, analyse exploratoire (EDA), visualisation, valeurs manquantes/doublons/aberrantes, encodage et normalisation, feature engineering, découpage train/validation/test, data leakage, pipelines reproductibles.
- **Outils :** Pandas, NumPy, Matplotlib, Seaborn, scikit-learn.
- **Résultat attendu :** un jeu de données préparé, documenté et utilisable dans un pipeline de Machine Learning.

### Module 3 — Machine Learning
- **Objectif :** sélectionner, entraîner et utiliser des modèles qui font des prédictions.
- **À apprendre :** apprentissage supervisé/non supervisé, classification/régression/clustering, régression linéaire et logistique, arbres de décision, Random Forest, SVM, Gradient Boosting (XGBoost/CatBoost), K-means, baseline.
- **Outils :** scikit-learn, introduction à XGBoost ou CatBoost.
- **Résultat attendu :** un premier modèle de ML et la justification du choix de l'algorithme.

### Module 4 — Évaluation et amélioration des modèles
- **Objectif :** mesurer les performances, identifier les erreurs et améliorer les modèles rigoureusement.
- **À apprendre :** métriques de classification (précision, rappel, F1, matrice de confusion, ROC-AUC, PR-AUC) et de régression (MAE, MSE, RMSE), validation croisée, overfitting/underfitting, biais/variance, GridSearchCV/RandomizedSearchCV/Optuna, analyse des erreurs, seuil de classification, interprétabilité, introduction à SHAP.
- **Outils :** scikit-learn, Optuna, SHAP.
- **Résultat attendu :** un benchmark de plusieurs modèles avec justification du modèle retenu.

### Module 5 — Deep Learning
- **Objectif :** comprendre et entraîner des réseaux de neurones.
- **À apprendre :** neurone artificiel, tenseurs, fonctions d'activation et de perte, descente de gradient, rétropropagation, optimiseurs, régularisation, dropout, courbes d'apprentissage, MLP, CNN, introduction à RNN/LSTM, transfert d'apprentissage.
- **Outils :** PyTorch.
- **Résultat attendu :** un réseau de neurones entraîné, comparé à une approche de référence.

### Module 6 — NLP : traitement du langage naturel
- **Objectif :** traiter automatiquement du texte et construire des modèles pour les tâches linguistiques.
- **À apprendre :** nettoyage, normalisation, tokenisation, Bag of Words, TF-IDF, classification de textes, analyse de sentiments, extraction d'entités, évaluation, introduction aux Transformers.
- **Outils :** Python, scikit-learn, spaCy, NLTK, Hugging Face.
- **Résultat attendu :** un modèle réalisant une tâche NLP (classer des messages, analyser des avis clients).

### Module 7 — LLM et IA générative
- **Objectif :** comprendre les grands modèles de langage et les exploiter dans des applications concrètes.
- **À apprendre :** fonctionnement des LLM, tokens, embeddings, fenêtre de contexte, modèles API vs ouverts, température, hallucinations, biais, confidentialité, coût, latence, cas d'usage.
- **Outils :** Hugging Face, API de modèles d'IA.
- **Résultat attendu :** choisir un modèle adapté à un besoin et expliquer ses capacités, limites et coûts.

### Module 8 — Prompt Engineering et API de modèles d'IA
- **Objectif :** communiquer efficacement avec les modèles et les intégrer dans des applications Python.
- **À apprendre :** prompts clairs, messages système/utilisateur, few-shot, sorties structurées JSON, appels API depuis Python, clés API et secrets, gestion des erreurs et limites de débit, coûts en tokens, comparaison de prompts.
- **Outils :** Python, API de modèles d'IA, Pydantic.
- **Résultat attendu :** une application Python qui utilise un modèle via API et gère proprement entrées, réponses et erreurs.

### Module 9 — Embeddings et recherche sémantique
- **Objectif :** représenter le sens du texte sous forme de vecteurs et rechercher des contenus proches.
- **À apprendre :** embeddings, similarité cosinus, indexation et recherche de vecteurs, métadonnées et filtrage, recherche sémantique vs mots-clés, pertinence, précision, rappel.
- **Outils :** embeddings Hugging Face, FAISS ou Chroma.
- **Résultat attendu :** un moteur de recherche sémantique.

### Module 10 — RAG : génération augmentée par récupération
- **Objectif :** construire des applications qui s'appuient sur des documents externes pour répondre.
- **À apprendre :** principe du RAG, extraction (PDF, DOCX, TXT), chunking, embeddings et indexation, récupération, génération avec contexte, citation des sources, recherche hybride et reranking, évaluation séparée de la recherche et de la génération, analyse des erreurs.
- **Outils :** Python, FAISS ou Chroma, API de LLM ou modèle ouvert, Hugging Face.
- **Résultat attendu :** un assistant documentaire RAG qui cite ses sources et est évalué sur un jeu de questions.

### Module 11 — Chatbots et assistants IA
- **Objectif :** transformer les modèles et le RAG en assistants conversationnels utilisables.
- **À apprendre :** architecture d'un chatbot, historique et contexte, mémoire persistante, sessions, intégration LLM + RAG, validation des entrées, interface de conversation, protection des informations sensibles, évaluation.
- **Outils :** Python, API de modèles, FastAPI, Streamlit ou Gradio.
- **Résultat attendu :** un chatbot fonctionnel qui garde le contexte et peut interroger une base documentaire.

### Module 12 — Automatisation et agents IA
- **Objectif :** développer des systèmes d'IA qui utilisent des outils et exécutent des tâches en plusieurs étapes.
- **À apprendre :** automatisation vs workflow IA vs agent, appels de fonctions, workflows multi-étapes, gestion d'état, gestion des erreurs, limites et coûts, contrôles d'accès, injection de prompt, évaluation de la fiabilité, quand préférer un workflow déterministe.
- **Outils :** Python, API de LLM, LangGraph (approfondissement).
- **Résultat attendu :** un agent ou workflow avec au moins un outil, plusieurs étapes, limites et contrôles explicites.

### Module 13 — Déploiement et MLOps
- **Objectif :** rendre les modèles et applications accessibles, testables, reproductibles et maintenables en production.
- **À apprendre :** API avec FastAPI et Pydantic, Docker et Docker Compose, tests avec pytest, suivi d'expériences avec MLflow, versionnement (Git, GitHub, DVC), GitHub Actions, déploiement, surveillance (latence, erreurs, coûts, dérive), documentation de maintenance.
- **Outils :** FastAPI, Pydantic, Docker, pytest, MLflow, Git, GitHub Actions, DVC.
- **Résultat attendu :** un service IA testé, conteneurisé et déployé, avec suivi des expériences et procédure de maintenance.

## Projet final — Construire une solution complète d'IA

1. Définir un problème concret, les utilisateurs et le résultat attendu.
2. Collecter, préparer et analyser les données.
3. Choisir une approche justifiée (ML classique, Deep Learning ou LLM).
4. Entraîner ou intégrer le modèle, puis évaluer ses performances.
5. Analyser les erreurs et documenter les limites.
6. Développer une API ou une interface adaptée.
7. Si assistant documentaire : intégrer un RAG et évaluer la qualité des réponses.
8. Automatiser les tests, conteneuriser l'application et préparer le déploiement.
9. Documenter le projet et les choix techniques, puis faire une démonstration.

**Livrable :** un projet présentable sur GitHub, reproductible et testé, avec des résultats mesurés, une documentation claire et une démonstration fonctionnelle.

## Organisation du dépôt

Chaque module aura son propre dossier, avec son code, ses notebooks et son mini-projet :

```
.
├── README.md
├── module-01-python/
├── module-02-preparation-donnees/
├── module-03-machine-learning/
├── ...
└── projet-final/
```
