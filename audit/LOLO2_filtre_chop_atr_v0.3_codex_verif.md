# LOLO 2 - Filtre CHOP/ATR v0.3 (version Codex) : relecture

Fichier relu : `src/lolo2/LOLO2_filtre_chop_atr_v0.3_codex.pine` (collage du 10/11, enregistre tel quel).
Reference : `src/lolo2/LOLO2_filtre_chop_atr_v0.2.pine`. Non compile ici.

## Verdict

Conforme a la demande. Aucun defaut de calcul trouve. Trois retouches conseillees, dont une seule compte vraiment (unite du plancher).

## Ce qui a ete controle

- Diff exact v0.2 -> v0.3 : seules les lignes prevues changent (titre, en-tete, 2 reglages a la fin,
  verdict brut, machine de confirmation, affichage sur le verdict confirme, plot "Verdict brut").
  Calculs CHOP / ATR, couleurs, tableau, formats : identiques octet pour octet.
- Reglages : 12, positions 1 a 10 inchangees, 11 et 12 nouveaux.
- Controle statique (noms, signatures, parentheses, indentation, ASCII) : 0 probleme.
- Machine de confirmation rejouee en Python sur 6 000 000 de barres simulees :
  - 1 cloture de confirmation : verdict confirme = verdict brut sur chaque barre (0 ecart),
    donc identique a la v0.2 quand le plancher vaut 0 ;
  - 2, 3, 5, 20 clotures : 487 007 ameliorations, toutes precedees du nombre voulu de clotures
    consecutives meilleures, et toutes egales au plus bas verdict brut de la serie (0 exception) ;
  - le verdict confirme n'est jamais meilleur que le brut ; une degradation est immediate.

## Retouches conseillees

1. Unite du plancher. Le reglage attend un ratio (0.15) alors que le tableau et la fenetre de donnees
   affichent un pourcentage (15.0 %). Saisir 15 transformerait tous les VERT en ORANGE sans rien signaler.
   Ajouter une info-bulle et refuser un plancher >= seuil de vigilance ("REGLAGES" / "Plancher trop haut").
2. Cause sur une barre. Apres une amelioration partielle (ROUGE vers ORANGE alors que le brut est VERT),
   le tableau affiche pendant une barre "Contexte a examiner" a cote de "ORANGE - ATTENDRE"
   (38 974 barres sur 4 800 000 simulees avec 2 clotures ou plus). Afficher "Confirmation 0/N" a la place.
3. Ligne de statut. Les deux nouveaux reglages numeriques s'y ajoutent (valeur par defaut display.all).
   `display = display.none` la laisse comme en v0.2.

## A savoir (sans retouche)

- Apres "DONNEES...", le premier verdict valide est pris tout de suite, sans confirmation.
  En pratique cela ne concerne que le debut de l'historique.
- Avec 1 cloture et plancher 0, la ligne "Verdict" de la fenetre de donnees montre sur la bougie en cours
  le verdict de la cloture precedente (la v0.2 montrait une valeur provisoire). Barres cloturees : identiques.

## Version retouchee (second collage du 10/11)

Fichier : `src/lolo2/LOLO2_filtre_chop_atr_v0.3_codex_r2.pine`, enregistre tel quel.
Diff exact contre la premiere v0.3 : 7 lignes, toutes dans les trois retouches demandees
(info-bulle et `display.none` sur les 2 reglages, `floorOk` avec "Plancher trop haut" / "REGLAGES",
cause "Confirmation k/N" des que le brut depasse le verdict confirme). Machine de confirmation inchangee.
Controle statique : 0 probleme. Avec plancher 0, `floorOk` est toujours vrai (vigilance >= 0.1),
donc l'identite avec la v0.2 a 1 cloture reste acquise. Non compile ici.
