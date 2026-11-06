# Questions de soutenance — Module 2 ImmoAnalyse

## Objectif
Préparer l'apprenant aux questions orales posées lors de la soutenance. Chaque question vise à vérifier que la décision a été comprise, pas seulement exécutée.

## À la fin, tu dois savoir
- Répondre à une question en 30 secondes
- Justifier une décision avec un chiffre
- Reconnaître ce que tu n'as pas fait (limites)
- Ne jamais dire « c'est la méthode » sans preuve

## Les 4 types de questions

| Type | Exemple | Ce que ça vérifie |
|---|---|---|
| Pourquoi | Pourquoi log(prix) et pas prix ? | Compréhension de la décision |
| Chiffre | Combien d'outliers avez-vous exclus ? | Preuve mesurée |
| Contre-factuel | Que se passe-t-il si vous ne faites pas X ? | Compréhension du risque |
| Limites | Qu'est-ce qui n'a pas marché ? | Honnêteté intellectuelle |

## Questions par compétence

### Comp 1 — Types et statistiques
1. Quelle est la skewness de `prix` avant et après log ?
2. Pourquoi la médiane plutôt que la moyenne ?
3. Qu'est-ce qu'un QQ-plot et que vous a-t-il appris ?
4. Si un champ est mal typé, quelle est la conséquence concrète sur la suite ?
5. Combien de valeurs de `prix` étaient en texte dans `particuliers` et dans `plateforme` ?

Critère de réussite : chaque réponse contient un chiffre et une conséquence.

### Comp 2 — EDA
1. Quels insights avez-vous tirés de l'EDA ?
2. Avez-vous détecté un paradoxe de Simpson ? Sur quelles variables ?
3. Qu'est-ce que le test Mann-Kendall vous a appris ? Quelle décision avez-vous prise avec ce résultat ?
4. Comment avez-vous identifié le mécanisme des manquants ?
5. Comment avez-vous mesuré la qualité de chaque source ?
6. Quelle source contient le plus d'anomalies ?

Critère de réussite : chaque insight est chiffré et oriente une décision en comp 3 ou 7.

### Comp 3 — Nettoyage
1. Combien de lignes en quarantaine, combien en avertissements, source par source ?
2. Quelle est la différence entre une règle bloquante et un avertissement ?
3. Avez-vous créé un indicateur de manque ? Pourquoi oui ou non ?
4. Comment avez-vous décidé du sort d'un outlier ?
5. Qu'est-ce qu'un doublon probable ? Avez-vous fusionné ?
6. Comment avez-vous corrigé le mojibake de `historique` ?
7. Comment avez-vous filtré le header dupliqué de `plateforme` ?
8. Combien d'IDs dupliqués avez-vous trouvés dans `plateforme` ? Que sont-ils devenus ?
9. Quelles lignes de `agence` avez-vous mises en quarantaine à cause des surfaces négatives ?

Critère de réussite : chaque décision est justifiée par un chiffre et une règle métier.

Question piège : pourquoi ne pas simplement supprimer toutes les lignes avec des manquants ?
Réponse attendue : perte massive d'information et biais (les manquants sont concentrés sur une source, supprimer revient à exclure cette source).

Question piège : pourquoi ne pas garder la feuille `Params` d'Excel avec les données ?
Réponse attendue : c'est une ligne de métadonnées, pas une annonce. Elle corromprait le corpus.

### Comp 4 — Viz de restitution
1. Quelle est la différence entre une viz diagnostique et une viz de restitution ?
2. Quelle figure justifie le choix de log(prix) ?
3. Comment prouvez-vous que votre nettoyage a effectivement supprimé les anomalies ?
4. La figure V6 montre-t-elle que les 5 sources sont alignées ? Sinon, qu'est-ce que ça implique pour la suite ?

Critère de réussite : la réponse nomme une figure précise et le chiffre qu'elle contient.

### Comp 5 — Encodage
1. Pourquoi one-hot pour `categorie` et pas label encoding ?
2. Qu'avez-vous décidé pour `statut` et pourquoi ?
3. Qu'avez-vous décidé pour `source` et pourquoi ?
4. Qu'avez-vous décidé pour `commune` et pourquoi ?
5. Comment prouvez-vous qu'il n'y a pas de fuite dans votre encodage ?
6. Pourquoi handle_unknown ignore ?

Critère de réussite : chaque réponse est ancrée sur le corpus réel, pas générique.

Question piège : pourquoi ne pas one-hot `commune` ? Elle contient peut-être de l'information.
Réponse attendue : 46 modalités, bruit, gain mesuré proche de 0 en CV. Test fait en comp 6.

Question piège : pourquoi ne pas utiliser `source` en one-hot ?
Réponse attendue : `source` est un identifiant de flux, pas une caractéristique du bien. Elle corrèle avec le prix uniquement parce que les distributions diffèrent. En production, elle ne généralise pas de façon fiable. Fuite type 4.

### Comp 6 — Feature engineering
1. Quelles features avez-vous créées ?
2. Quelles features avez-vous exclues ?
3. Quel est le gain de votre meilleure candidate ?
4. Avez-vous testé `prix_m2` ? Quel score a-t-il donné ? Pourquoi l'avoir exclu ?
5. Avez-vous testé `source` en feature ? Quel gain ? Décision ?
6. Comment mesurez-vous le gain d'une feature ?

Critère de réussite : la réponse au point 4 doit citer le gain proche de +0.99 et le mot fuite. La réponse au point 5 doit mentionner la fuite type 4.

Question piège : votre modèle a un R² de 0.99, c'est excellent non ?
Réponse attendue : c'est un signal d'alarme. Une feature contient probablement `prix`, ou `source` a été gardée par erreur.

### Comp 7 — Split
1. Quel ratio avez-vous choisi et pourquoi ?
2. Votre split est-il aléatoire ou temporel ? Quelle preuve ?
3. Comment garantissez-vous que le test est scellé ?
4. Pourquoi stratifier par `categorie` ?
5. Comment avez-vous vérifié que les 5 sources sont représentées dans chaque ensemble ?
6. Si vous relancez le split, obtenez-vous les mêmes lignes ? Comment ?

Critère de réussite : chaque réponse est chiffrée (ratio, graine, résultat du test de tendance, effectifs par source).

Question piège : les sources ne couvrent pas les mêmes périodes, un split aléatoire est-il vraiment correct ?
Réponse attendue : oui, si Mann-Kendall ne détecte pas de tendance, mais il faut vérifier les effectifs par source dans chaque ensemble. Si une source est absente d'un ensemble, il faut stratifier par source en plus de `categorie`.

### Comp 8 — Anti-fuite
1. Citez les 4 types de fuite. Pour chacun, un exemple sur votre corpus.
2. Avez-vous une fuite de type 2 ? Laquelle ?
3. Comment vérifiez-vous qu'un scaler n'est pas fitté sur tout le jeu ?
4. Qu'est-ce qu'une fuite de type 4 et comment la prévenir ?
5. Comment détectez-vous une fuite sans la voir ? (test du score)
6. Pourquoi les colonnes `date_expiration`, `quartier`, `description` doivent-elles être retirées avant concaténation ?

Critère de réussite : la réponse au point 1 cite les 4 types et un cas réel du corpus pour chacun.

### Comp 9 — Pipeline
1. Qu'est-ce qui est dans votre pipeline ?
2. Qu'est-ce qui est hors du pipeline, et pourquoi ?
3. Montrez-moi que votre pipeline est reproductible.
4. Que se passe-t-il si une nouvelle modalité apparaît en production ?
5. Comment avez-vous sérialisé votre pipeline ?
6. Comment votre pipeline traite-t-il une ligne de la source `particuliers` (JSON imbriqué) versus une ligne de la source `plateforme` (CSV) ?

Critère de réussite : l'apprenant montre le rechargement du pipeline, pas seulement le décrit.

## Questions transverses

1. Quelle décision vous a demandé le plus d'hésitation ? Pourquoi ?
2. Quelle décision regrettez-vous ou changeriez-vous ?
3. Quelle est la limite principale de votre travail ?
4. Si vous aviez deux fois plus de temps, que feriez-vous ?
5. Quelle décision repose sur l'hypothèse la plus fragile ?
6. Comment avez-vous géré les 5 sources simultanément sans y perdre le fil ?

Critère de réussite : la réponse reconnaît une faiblesse réelle, pas une fausse modestie.

## Les réponses à ne jamais donner

- « C'est la méthode » : sans preuve, ne convainc pas
- « Je ne sais pas » : dire « je n'ai pas mesuré, mais voici comment je le ferais »
- « Ça marche bien » : sans chiffre, non défendable
- « C'est mieux » : que quoi ? Avec quel chiffre ?
- Inventer un chiffre : disqualifiant
- « J'ai suivi le tutoriel » : ne montre pas la compréhension

## Comment préparer la soutenance

### Avant
- [ ] Relire `docs/justifications.md` et retrouver le chiffre de chaque décision
- [ ] Préparer 3 slides : nettoyage, features, pipeline
- [ ] Anticiper les 2 questions les plus dures et les préparer
- [ ] Savoir ouvrir `quarantine.csv`, `avertissements.csv`, `donnees_propres.csv` à la demande
- [ ] Connaître le nombre de lignes par source avant et après nettoyage

### Pendant
- [ ] Répondre en 30 secondes puis laisser le jury relancer
- [ ] Chiffrer dès que possible
- [ ] Admettre ce que tu n'as pas fait
- [ ] Montrer que tu comprends le risque (fuite, biais, sur-apprentissage)
- [ ] Montrer le rechargement du pipeline si demandé

### Après
- [ ] Noter les questions posées et tes réponses
- [ ] Identifier ce qui t'a surpris, c'est la vraie note de progression

## Ce qu'il faut faire
- Préparer un chiffre pour chaque décision
- Assumer les limites honnêtement
- Montrer (pas seulement décrire) le pipeline
- Reconnaître une fuite même si elle est corrigée
- Citer les règles métier quand c'est pertinent
- Connaître les spécificités des 5 sources

## Ce qu'il ne faut pas faire
- Réciter sans comprendre
- Inventer un chiffre
- Nier une faiblesse évidente
- Dire « c'est la méthode » sans preuve
- Se contenter de « ça marche »
- Ignorer les questions sur les sources individuelles

## Ce que tu dois produire
Aucun livrable direct : ta préparation est ton livrable. Mais tu dois pouvoir :
1. Ouvrir `justifications.md` et retrouver le chiffre d'une décision en 30 secondes
2. Montrer le pipeline rechargé
3. Citer le gain de `prix_m2`
4. Nommer la limite principale de ton travail
5. Expliquer pourquoi `statut` a été exclu (ou gardé)
6. Expliquer pourquoi `source` a été exclue (ou gardée)
7. Citer une anomalie par source (mojibake sur `historique`, header dupliqué sur `plateforme`, prix en string sur `particuliers`, statuts variables sur `notaires`, surfaces négatives sur `agence`)

## Pièges récapitulés

| Piège | Conséquence |
|---|---|
| Pas de chiffre prêt | Réponse non défendable |
| Nier une faiblesse | Crédibilité perdue |
| Inventer un chiffre | Disqualifiant |
| Décrire sans montrer | Faible impression |
| Réciter sans comprendre | Repérable en 2 questions |
| Ignorer les spécificités des sources | Preuve d'une lecture superficielle |
