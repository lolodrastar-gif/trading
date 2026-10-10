# BSP v11.66 — corrections de la v11.65.1

Date : 10/10/2026. Fichier corrigé : `src/BSP_v11.66.pine` (base : `src/BSP_v11.65.1.pine`,
le script collé tel quel). Diff : `git diff --no-index src/BSP_v11.65.1.pine src/BSP_v11.66.pine`.

## Méthode

Neuf relectures indépendantes du code (compilation Pine v6, erreurs d'exécution, logique de
la série, cohérence bord/série sur toutes les combinaisons d'options, charge en rafale,
moteur et estimation, réserve, textes, diagnostics), puis chaque trouvaille contredite par
trois relecteurs distincts (réfutation, reconstruction du scénario, validité du correctif).
36 trouvailles ; 13 confirmées à trois voix avant une coupure de quota, le reste jugé par
moi ligne à ligne (section « Jugées à la main »).

**Limite inchangée :** aucun compilateur Pine n'existe hors de TradingView. Le script n'a été
ni compilé ni exécuté ; la latence n'est pas mesurée. Les deux relectures « compilation » et
« exécution » n'ont trouvé aucune erreur (chaque indice de tableau prouvé dans les bornes,
chaque boucle `for` gardée contre l'itération descendante de la v6, aucune boucle proche de
la limite de 500 ms, arité de chaque appel, qualificateurs `simple`, paramètre `active` des
réglages accepté en v6 depuis juillet 2025).

## Vérification du diff v11.65.1 → v11.66

Cinq relecteurs indépendants du diff (compilation v6, rendu par défaut et équivalence des
réécritures, les deux correctifs et l'égalité bord/série cas par cas, contrat du script
jumeau, relecture « à l'œil neuf » de chaque hunk), puis deux vérificateurs contradictoires
par trouvaille :

- **aucun problème de compilation, d'exécution ou de rendu** trouvé : qualificateurs
  (`const bool` dans les conditions, `int(na)`), portée des tuples dans `if edgeNeeded`,
  appels nus de `poolInsert`, ordre des déclarations, 11 `plot()`, 28 réglages aux mêmes
  positions, aucune ligne à guillemets déséquilibrés, moteur identique octet pour octet ;
- `candidateIndex` et `inBoundsCount` réécrits : prouvés équivalents dans tous les cas (y
  compris bar 0, tableau vide, aucun élément dans les bornes) ;
- les sept cas de la coupure stricte (tick propre indéfini, tick indéfini de la réserve
  avec repli, reprise invalidée, reprise rafraîchie, reprise simple, estimation, mesure
  fraîche) : bord = série pour la valeur, l'état et le remplissage ; `lastShownWarm` :
  toujours vrai dès que `lastBuyer` existe avec « Masquer » coché (rendu par défaut
  inchangé), estimation grise série ET bord sinon ;
- avec `DIAG_FULL = true`, chaque calcul gardé se réduit exactement à l'ancien code ;
- trois imprécisions de texte dans le nouvel en-tête, corrigées (consigne de report vers le
  jumeau ; « prédécesseur » → « élément livré » pour le code −8 ; libellé du Diag 61).

## Ce qui est garanti

- Moteur `bspEngine1T` et enveloppe `bspEngine1TWithTrail` : identiques octet pour octet.
- Rendu PAR DÉFAUT identique (toutes les options décochées ; « Garder la couleur »,
  « Masquer pendant le préchauffage », remplissage et opacité cochés) : chaque changement de
  code est soit sous une option, soit une réécriture prouvée équivalente, soit du calcul que
  rien ne lit dans le script principal.
- 11 `plot()`, 28 réglages, mêmes positions.

## Corrections de comportement (sous options seulement)

1. **« Reprises strictes » : bord ≠ série après la coupure** (edge, lignes ~3246-3253).
   Après dix bougies sans tick (courbe coupée), une bougie dont le tick a un ratio indéfini
   (calcul indéfini `curUndefined`, reprise invalidée `edgeRefreshUndefined`) remet la fenêtre
   à zéro dans la série, qui retrace `lastBuyer` en gris ; le bord ne traçait rien
   (`edgeCarryValue` testait encore `missingRun < 10`) et reprenait `buyerPercent` (na après
   la coupure) au lieu de `lastBuyer`. Correctif :
   ```pine
   bool edgeCarryValue = edgeCarryAllowed and (not strictBridges or missingRun < BRIDGE_MAX_BARS or curUndefined or edgeRefreshUndefined)
   float edgeBuyer = ... : (edgeCarryValue ? lastBuyer : na)
   ```
   Hors option, `buyerPercent == lastBuyer` dans tous les cas atteignables (vérifié cas par cas).

2. **Estimation colorée pendant le préchauffage** (`hideUntilWarm` décoché + « Estimer »
   coché ; lignes ~2450, 2707, 2747-2787, 3237). L'info-bulle promet « le signal reste gris
   avant la fin, même si ce réglage est décoché » ; l'état d'une estimation vient de
   `nextSignalState` sans information de préchauffage et pouvait passer à ±1. Nouvelle
   mémoire `var bool lastShownWarm` (préchauffage du dernier tick tracé : mesure, reprise
   rafraîchie, calcul indéfini, reprise invalidée ; remise à `false` avec les autres
   mémoires). `estState` et `edgeEstState` restent à 0 tant qu'elle est fausse. Par défaut,
   `hideUntilWarm` coché implique `lastBuyer` na avant préchauffage : aucune estimation
   possible, rien ne change.

## Textes mis en accord avec le code

| Où | Avant | Après |
|---|---|---|
| Info-bulle « Garder la couleur » | « DÉCOCHÉ — toute reprise est grise tout de suite » | … reprises simples et rafraîchies ; une estimation garde sa couleur dans sa fenêtre (voulu, [DD]) |
| En-tête §5 | idem | idem |
| Info-bulle « Masquer pendant le préchauffage » | — | précise que l'estimation reste grise aussi (v11.66) |
| Info-bulle diagnostics, bandeau de section | « décalés d'une bougie » | sauf Diag 55, non décalé (bord de la bougie en cours) |
| Libellé Diag 55 | −1 sans la coupure stricte ; −2 sans condition | −1 inclut « courbe coupée par Reprises strictes » ; −2 « (option plafond prudent) » |
| Info-bulles citant Diag 05, 14, 18, 21/22, 27, 33, 63, 64 | absents du principal | renvoient au script « BSP Diag » |
| En-tête §4 réserve | « 6 000 éléments au plus » | 6 000 à 9 000 entre deux purges |
| En-tête §5, LIMITES, commentaire ligne ~2663 | « HMA à dénominateur négatif » rend na | impossible : HMA → WMA en « Ratio des moyennes » |
| LIMITES, traîne | fin perdue retrouvée seulement si livrée pendant N+1 | aussi depuis le tableau de N (réserve, Diag 58 = −7) ; le bord, qui ne lit pas sa traîne, y reste en retard d'un tick |
| Constantes | « tickHistoryInput, en fin de liste » | 25e réglage |
| Commentaire de l'échelle | « la non dominante la couleur choisie » | couleur Neutre (22e réglage non lu) |
| `poolInsert` | « inatteignable sur une réserve triée par numéro » | inatteignable parce que l'ordre des heures refuse ce cas |
| `movingAverage` | — | avertissement du compilateur attendu et justifié (kind est simple) |

## Allègements sans effet sur le rendu

- **`const bool DIAG_FULL = false`** (true dans « BSP Diag ») : compile hors du principal les
  dix-neuf compteurs que rien n'y lit, le balayage du Diag 63 (`looseScan`), `measureQuality`,
  les mémoires du bord des Diag 64/10/47 (`lastEdgeShownTime`, `lastConfirmedCount`,
  `confirmedCloseKnownCount`), `firstTickOffsetMs`, `valueMissingWithData`, Diag 59. Les
  trois compteurs tracés (Diag 12, 30, 33) et `previousLastSerial` (plafond de compte de la
  frontière partagée, Diag 12/33) restent actifs. Les deux fichiers ne diffèrent plus que par
  cette constante et la section DIAG-SECTION.
- **Bord calculé seulement sur la dernière bougie** (`edgeNeeded = barstate.islast or
  showDiagnostics`) : trois dichotomies sur la réserve, deux sur le tableau courant, deux
  `candidateValues` et `estimateStep` par bougie d'historique épargnés. Gain au
  (re)chargement seulement : en direct `barstate.islast` est vrai à chaque exécution.
- **Dichotomies en double retirées** : `candidateIndex` réutilise `boundsLastIndex` quand
  `ownUpper == exactUpper` (toujours une fois le verrou actif) ; `inBoundsCount` se déduit de
  `firstInBoundsIndex` et `boundsLastIndex` au lieu de refaire les deux recherches
  (`countBetween` retiré). Même formule, mêmes gardes.
- `emptyInts` en `var` (jamais écrit, alloué à chaque exécution auparavant).
- `trailAdded` / `elementAdded` : appels directs à `poolInsert` (deux booléens morts par
  élément versé).
- Branches mortes des couleurs de l'axe (`axisState == -1 ? neutralColor : neutralColor`).
- Diag 58 : code −8 pour un élément livré relu depuis la réserve avec source = la bougie
  elle-même (inatteignable par construction ; affiché « 1 » jusqu'ici, ce qui aurait masqué
  un tableau figé différent du tableau versé, Diag 10).

## Jugées à la main (quota de vérification coupé) — retenues

Les textes ci-dessus (Diag 55, « décalés », renvois au script Diag, 25e réglage, réserve
6 000-9 000, échelle, HMA), le correctif 2, DIAG_FULL, `emptyInts`, les dichotomies, l'axe.

## Écartées — à ne pas appliquer sans mesure

- **`varip` sur la réserve** (relecture « charge », confiance 0,6). Hypothèse : TradingView
  restaure chaque `var` avant chaque exécution ; une réserve de 6 000 à 9 000 objets copiée
  ~1 000 fois par seconde serait LE mécanisme de lag interne au script. La réserve n'est
  écrite qu'à l'exécution confirmée : `varip` donnerait un contenu identique à chaque
  exécution. Non appliqué : l'auteur a écrit « aucun varip » comme décision de conception,
  et le coût réel de la restauration n'est pas documenté. **C'est le test A/B le plus
  rentable au profileur** : une ligne (`varip array<Tick> tickPool`), à essayer un soir de
  clôture, et à garder seulement si le profileur le justifie.
- **Verrou de clôture inerte en direct ?** (relecture « série », 1 voix sur 2). Si
  `time_close[1]` est na en direct sur un graphique en ticks, `prevCloseKnown` est faux,
  `ownUpper = time − 1`, et la série écarte le dernier tick de N à chaque milliseconde
  partagée (le bord l'avait montré) : retard d'un tick sur ≈ 22 % des frontières en rafale,
  puis valeur différente après rechargement. Les mesures de l'auteur (Diag 63 en direct,
  Diag 25 = 2) semblent dire le contraire. À trancher avec le script Diag en direct : Diag 46
  (clôture connue) et Diag 25 sur quelques bougies de rafale. Si c'est confirmé, le
  correctif proposé est `int ownUpper = closeIsLastTrade ? (prevCloseKnown ? exactUpper : time) : neighbourUpper`
  — il échange un retard systématique contre l'avance d'un tick que le bord accepte déjà.
- **POOL_MAX 6 000 → 2 000-3 000, SCAN_MAX 2 000 → 500** : plausibles (aucune lecture ne
  remonte au-delà du dernier élément sous une borne récente), mais ces valeurs ont été
  fixées sur profileur et modèle par l'auteur ; gain en direct faible (purge et décalages
  d'insertion plus courts).
- **Cache du tri du tableau figé** (`isSorted` relu à chaque exécution de N+1) : 10 à 30
  itérations par exécution en direct, repose sur l'hypothèse Diag 10 = 0.
- **Compteur des refus de `poolInsert`** : panne silencieuse hypothétique (horodatage non
  monotone côté plateforme), diagnostic seulement, pour le script Diag.
- Appels `movingAverage` hors du `if weightedMode` : toucherait le moteur pour un
  avertissement bénin.

## Lag en rafale : ce que dit l'analyse

Coût du script par exécution, hors plateforme : deux `isSorted` sur ~10 à 30 éléments,
~8 dichotomies, `pickTrail` sur 16 éléments, ~1 500 opérations scalaires, 7 à 11 mises à
jour de dessins — quelques centaines de microsecondes au plus. Rien ne grossit avec la
rafale (les tableaux y sont plus petits). Le versement ne tourne qu'une fois par bougie ; la
purge recopie 6 000 références toutes les ~300 bougies.

Les trois postes que le code ne peut pas mesurer, par ordre de suspicion :
1. la restauration de la réserve `var` à chaque exécution (test `varip`, ci-dessus) ;
2. la livraison des 15 tableaux de `request.security_lower_tf` à chaque tick ;
3. l'envoi au navigateur des 7 à 11 mises à jour de dessins et des 11 séries, puis le rendu
   d'un graphique 10T à 100 bougies par seconde.

Test qui tranche : Profiler Pine à 21:50, puis retrait du BSP du layout à la clôture
suivante. Si le lag persiste sans lui, la cause est ailleurs.

## Script « BSP Diag »

Reporter dans le jumeau : `const bool DIAG_FULL = true`, les deux correctifs de
comportement, les textes partagés. Sa section DIAG-SECTION reste la sienne ; `-8` du Diag 58
y est à ajouter si son libellé est repris.
