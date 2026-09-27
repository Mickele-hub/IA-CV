# Évaluation du pipeline de matching — résultats et analyse

## Méthode

30 CV réels (anonymisés) comparés à 5 offres d'emploi réelles, avec des classements de référence produits par deux recruteurs humains indépendants. Le pipeline SmartCV AI calcule un score pour chaque paire CV/offre, on en déduit un classement, comparé aux classements humains via la corrélation de rang de Spearman (échelle -1 à +1 : +1 = accord parfait, 0 = aucun lien, -1 = désaccord total).

Dataset : Vanetik, N.; Kogan, G. *Job Vacancy Ranking with Sentence Embeddings, Keywords, and Named Entities*. Information 2023, 14, 468.

## Résultats

| Mesure | Valeur |
|---|---|
| CV évalués | 29 (1 CV vide ignoré) |
| Corrélation pipeline vs Annotateur 1 | **-0.458** |
| Corrélation pipeline vs Annotateur 2 | **-0.148** |
| Accord entre les 2 annotateurs humains (référence) | 0.191 |

## Interprétation

Le résultat est négatif : le pipeline classe les offres **à l'inverse** de ce que jugent les humains, sur ce dataset. Même l'accord entre les deux recruteurs humains est modeste (0.191), ce qui est normal (le jugement humain sur un CV est en partie subjectif), mais le pipeline fait significativement pire que le hasard, ce qui indique un vrai problème plutôt qu'une simple difficulté du problème.

**Hypothèse principale : le bruit textuel domine le signal.**
Les offres d'emploi de ce dataset contiennent d'importants blocs de texte hors-sujet (avantages sociaux, mentions légales, description de l'entreprise, politique de non-discrimination), parfois plus longs que la partie décrivant réellement le poste. Exemple observé : une offre de ~2000 mots dont environ 15% seulement concernent les compétences recherchées. Le score sémantique (`calculate_match_score`) encode le texte brut dans son intégralité (après un nettoyage qui ne fait que normaliser les espaces, sans retirer ce bruit), ce qui peut faire dominer la similarité par du texte générique plutôt que par les compétences réelles.

Observation appuyant cette hypothèse : sur la majorité des 29 CV, le pipeline classe systématiquement les **mêmes offres** en tête ou en fin de classement, presque indépendamment du contenu du CV — signe d'un biais structurel (probablement lié à la longueur/au style du texte de l'offre) plutôt que d'une vraie évaluation compétence par compétence.

## Pistes d'amélioration (non implémentées ici)

1. **Nettoyer les offres d'emploi avant l'encodage sémantique** : isoler la section "compétences requises"/"responsabilités" et exclure les sections légales/avantages avant de calculer l'embedding.
2. **Pondérer le score final entre similarité sémantique et recouvrement de compétences** (`compare_skills`) plutôt que de se reposer uniquement sur la similarité sémantique globale — le recouvrement de compétences est probablement un signal plus robuste au bruit.
3. **Tester avec des offres plus courtes/mieux structurées** pour confirmer que le problème vient bien de la longueur/du bruit et non du modèle lui-même.

## Bonus : bug de code trouvé pendant l'investigation

`app/services/text_cleaner.py` contenait deux définitions de `clean_text()` et `normalize_text()` (probablement les restes d'une fusion Git mal résolue) — corrigé dans cette PR (aucun changement de comportement, juste suppression du code mort).
