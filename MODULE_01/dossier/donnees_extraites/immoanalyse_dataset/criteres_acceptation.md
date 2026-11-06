# Critères d'acceptation du pipeline étudiant

1. **Lecture** : les 5 sources sont lues sans erreur.
2. **Profilage** : un rapport par source (types, manquants, doublons, distributions).
3. **Normalisation** : règles documentées, testées, réversibles.
4. **Quarantaine** : chaque ligne en quarantaine a une justification.
5. **Doublons** : stratégie de rapprochement explicitée (seuil, attributs).
6. **Atpyiques** : distinction entre erreur et valeur légitime.
7. **Exports** : `donnees_propres.csv`, `quarantaine.csv`, `rapport_qualite.md`.
8. **Tests** : au moins 5 tests unitaires sur les fonctions de nettoyage.
9. **Documentation** : décisions justifiées, limites reconnues.
10. **Reproductibilité** : le pipeline s'exécute de bout en bout avec un seul script.
