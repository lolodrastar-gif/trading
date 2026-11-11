# LOLO 2 - Jauge consensus technique v0.1 (version Codex) : relecture

Fichier relu : `src/lolo2/LOLO2_jauge_consensus_v0.1_codex.pine` (collage du 11/11, enregistre tel quel, 191 lignes).
Non compile ici (l'utilisateur indique qu'il compile et fonctionne). Relecture complete, controle statique des noms
et signatures contre le manuel Pine v6 : tous les messages du controleur sont des faux positifs (tuples, variables
locales, fonctions utilisateur, variable de boucle).

## Verdict

Aucun bug de calcul, aucune repeinte. Les 5 lectures, le consensus et la securite sont enregistres a la cloture
seulement ; le panneau n'affiche que la derniere bougie cloturee. Seul le choc est lu pendant la bougie en cours.
La fusion des cellules une seule fois sur la premiere bougie est conforme au manuel (cellules non encore definies
acceptees). L'ecriture en direct de la cellule de securite ne laisse pas de texte perime : chaque cloture
reecrit tout le panneau.

## Defaut

1. Alerte "L2 CHOC LIVE" : la condition exige une bougie non cloturee. Avec la frequence
   "Une fois par cloture de barre" elle ne se declenche jamais. Retirer `not barstate.isconfirmed`.

## A savoir

- Fonctionne uniquement en 1 minute exacte, bougies standard.
- Aucune confirmation : consensus et securite changent a chaque cloture ; les deux alertes de consensus
  peuvent se repeter quand une mesure tourne autour d'un seuil.
- Un choc ne colore que sa bougie : pas de pause ensuite (le Controle v0.6 en a une).
- Si la securite n'est pas calculable, le consensus passe aussi en "INDISPONIBLE" (couplage par `allReady`).
- Ligne de statut : les reglages numeriques s'y affichent (cosmetique).

## Conception

- Les 5 lectures (EMA, RSI, DMI, Supertrend, ROC) suivent toutes la tendance du meme prix : elles sont liees.
  "ACHAT FORT" resume une hausse deja faite ; ce ne sont pas cinq confirmations independantes.
- La securite = verdict brut du filtre v0.3 + choc de bougie, sans confirmation ni plancher ATR.
  Filtre v0.3, Controle v0.6 et Jauge v0.1 peuvent donc afficher trois couleurs differentes au meme instant.
- Fiabilite des alertes non prouvee : a mesurer (gain d'un stop avant perte d'un stop), comme pour le Controle.
- Charge : une trentaine de cellules reecrites par cloture, 2 ecritures par tick seulement pendant un choc.
