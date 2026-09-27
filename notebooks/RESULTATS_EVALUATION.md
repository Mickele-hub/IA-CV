# Évaluation du pipeline de matching — résultats et analyse

## Méthode

30 CV réels (anonymisés) comparés à 5 offres d'emploi réelles, avec des classements de référence produits par deux recruteurs humains indépendants. Le pipeline SmartCV AI calcule un score pour chaque paire CV/offre, on en déduit un classement, comparé aux classements humains via la corrélation de rang de Spearman (échelle -1 à +1 : +1 = accord parfait, 0 = aucun lien, -1 = désaccord total).

Dataset : Vanetik, N.; Kogan, G. *Job Vacancy Ranking with Sentence Embeddings, Keywords, and Named Entities*. Information 2023, 14, 468.

## Résultats — progression en 3 étapes

| Étape | Description | Corrélation vs Annotateur 1 | Corrélation vs Annotateur 2 |
|---|---|---|---|
| 1 | Score sémantique brut (`calculate_match_score` d'origine) | -0.458 | -0.148 |
| 2 | + extraction des phrases pertinentes avant l'embedding (`extract_relevant_excerpt`) | -0.379 | -0.141 |
| 3 | + score combiné : 50% sémantique + 50% recouvrement de compétences (`calculate_combined_score`) | **-0.104** | **-0.000** |
| — | *Accord entre les 2 annotateurs humains (référence)* | *0.191* | *0.191* |

CV évalués : 29 (1 CV vide ignoré sur les 30).

## Interprétation

**Étape 1 — diagnostic du problème initial.** Le score sémantique brut était en désaccord quasi systématique avec le jugement humain (corrélation négative). Hypothèse retenue : les offres d'emploi contiennent d'importants blocs de texte hors-sujet (avantages sociaux, mentions légales, présentation d'entreprise), et le modèle d'embedding (`all-MiniLM-L6-v2`) tronque automatiquement tout texte au-delà d'environ 256 tokens en ne gardant que le début — souvent la partie la moins pertinente du texte.

**Étape 2 — première correction.** L'ajout de `extract_relevant_excerpt()`, qui priorise les phrases denses en mots-clés de compétences/exigences avant l'encodage, améliore légèrement le résultat mais ne suffit pas : le score sémantique global reste sensible à des similarités de style d'écriture qui n'ont rien à voir avec l'adéquation réelle des compétences.

**Étape 3 — score combiné.** Ajouter `calculate_skill_overlap_score()` (proportion des compétences requises par l'offre effectivement présentes dans le CV, indépendant du bruit textuel) et le combiner à 50/50 avec le score sémantique donne le meilleur résultat des trois : la corrélation avec l'Annotateur 2 devient neutre (0.000, ni bonne ni mauvaise) et celle avec l'Annotateur 1 se rapproche nettement de zéro (-0.104, contre -0.458 au départ).

**Limite persistante.** Même le score combiné n'atteint pas le niveau d'accord entre les deux recruteurs humains eux-mêmes (0.191). Cela suggère qu'une partie du jugement humain repose sur des éléments qu'aucune des deux approches ne capture (séniorité globale, compétences transférables, "potentiel" perçu, qualité de présentation du CV) — une limite connue des systèmes de matching automatique documentée dans la littérature scientifique du domaine, pas un simple bug à corriger.

## Pistes non explorées (hors délai du projet)

- Pondérer différemment le score combiné (ex: 30% sémantique / 70% compétences, ou l'inverse) et chercher le poids optimal.
- Utiliser un NER (reconnaissance d'entités nommées) pour extraire des compétences au-delà du dictionnaire fixe `skills.json`.
- Tester sur un dataset plus large pour confirmer que la tendance observée est stable (30 CV / 5 offres reste un échantillon modeste).

## Recommandation pour l'équipe

`calculate_combined_score()` a été ajoutée dans `matcher.py` **en plus** de `calculate_match_score()`, sans remplacer cette dernière : l'API actuelle (`/analyze`) continue d'utiliser le score sémantique seul. Vu les résultats ci-dessus, il serait pertinent d'en discuter en groupe : basculer `analyzer.py` sur `calculate_combined_score()` améliorerait probablement la qualité perçue du matching en production, mais c'est un changement de comportement qui mérite une décision collective plutôt qu'un changement silencieux dans cette PR.

## Bonus : bug de code trouvé pendant l'investigation

`app/services/text_cleaner.py` contenait deux définitions de `clean_text()` et `normalize_text()` (probablement les restes d'une fusion Git mal résolue) — corrigé dans une PR précédente (aucun changement de comportement, juste suppression du code mort).
