# LOLO 2 - Controle Marche DMI/ST v0.6 (version Codex) : relecture

Fichier relu : `src/lolo2/LOLO2_controle_marche_v0.6_codex.pine` (collage du 11/11, enregistre tel quel, 238 lignes).
Non compile ici. Relecture complete du code, controle statique des noms et signatures contre le manuel Pine v6
(les 41 messages du controleur sont tous des faux positifs : declarations en tuple et variables locales qu'il ne lit pas).

## Verdict

Aucun bug de calcul, aucune repeinte : verdict, direction et fleches ne sont fixes qu'a la cloture ;
la machine de confirmation est celle du filtre v0.3. Deux petits defauts de fonctionnement, plusieurs remarques de conception.

## Defauts

1. Alerte "L2 CHOC ROUGE LIVE" : la condition exige une bougie non cloturee. Avec la frequence
   "Une fois par cloture de barre" elle ne se declenche jamais. Retirer `not barstate.isconfirmed`.
2. La case "Fleches ACHAT / VENTE sur le graphique" coupe aussi les alertes ACHAT / VENTE et la memoire
   d'espacement, car `showSignals` est dans `buySignal` / `sellSignal`. La sortir vers `plotshape`.

## A savoir

- Fonctionne uniquement en 1 minute exacte, bougies standard. En secondes : "UT 1 MIN REQUISE".
- Espacement : une fleche qui tombe dans l'intervalle est supprimee, pas retardee (sens oppose compris).
- Le commentaire sur le rollback des cellules du tableau n'est pas documente dans le manuel. Le code reste
  correct dans les deux cas : il reecrit les cellules a chaque tick et tout le tableau a la cloture.
- Ligne de statut : une trentaine de valeurs s'y affichent (cosmetique, `display = display.none`).
- En-tete "NAS / 1 MIN" affiche quel que soit le symbole.
- Apres "INDISPONIBLE", le premier verdict valide est pris sans confirmation (debut d'historique).

## Conception

- Le score n'est pas un vote a 4. VERT exige CHOP sous le seuil ET ATR sous le seuil (sinon ORANGE),
  plus ADX ou ER. Un 3/4 peut donc etre ORANGE ou VERT selon le vote manquant.
- CHOP, ADX et ER mesurent la meme chose (la tendance) : trois votes sur quatre sont lies.
- VERT ici = VERT du filtre v0.3 + (ADX ou ER) + pas de bougie agitee : forcement aussi rare ou plus rare.
  ROUGE = ROUGE du filtre + score <= 1 + choc + pause : forcement aussi frequent ou plus frequent.
- Fleches : VERT confirme + EMA + RSI + DMI + Supertrend. Rares et tardives dans le mouvement.
  Leur fiabilite n'est pas prouvee : a mesurer (gain d'un stop avant perte d'un stop).
