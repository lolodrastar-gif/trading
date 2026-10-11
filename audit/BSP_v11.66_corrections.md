# BSP v11.66 — corrections de la v11.65.1

Date : 10-11/10/2026. Fichier corrigé : `src/BSP_v11.66.pine` (base : `src/BSP_v11.65.1.pine`,
le script collé tel quel). Diff : `git diff --no-index src/BSP_v11.65.1.pine src/BSP_v11.66.pine`.

## Méthode

Neuf relectures indépendantes du code (compilation Pine v6, erreurs d'exécution, logique de
la série, cohérence bord/série sur toutes les combinaisons d'options, charge en rafale,
moteur et estimation, réserve, textes, diagnostics), une relecture de complétude (« qu'ont-ils
manqué ? »), puis chaque trouvaille contredite par trois vérificateurs distincts (réfutation,
reconstruction du scénario, validité du correctif ; retenue à 2 voix sur 3 au moins).
**42 trouvailles, 38 confirmées, 4 rejetées** — tableau complet en fin de document.

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

## Vérification de la dernière série (tri mémorisé, lignes Diag masquées, textes)

Trois relecteurs (compilation, équivalence, textes) : aucune erreur de compilation ; le tri
mémorisé est prouvé équivalent au recalcul dans tous les cas (historique, mises à jour en
direct, bougie sans exécution confirmée, bar 0/1) ; `display = showDiagnostics ?
display.data_window : display.none` attendu valide (paramètre `display` de type « input
plot_display » ; référence TradingView non joignable ici, confiance ≈ 0,9 — repli si le
compilateur refuse : remettre `display = display.data_window`, seules les lignes vides
reviennent). Neuf imprécisions de texte et de commentaires relevées, toutes corrigées
(consigne de report vers le jumeau, §3 de l'en-tête et commentaire des frontières en direct,
« rechargement le relira » conditionné au verrou, option « attribution par numéro » et
Diag 64 inactifs en direct, commentaires d'`isSorted`, renvoi du Diag 10, « rendu par défaut
identique » précisé).

## Ce qui est garanti

- Moteur `bspEngine1T` et enveloppe `bspEngine1TWithTrail` : identiques octet pour octet.
- Rendu PAR DÉFAUT identique (toutes les options décochées ; « Garder la couleur »,
  « Masquer pendant le préchauffage », remplissage et opacité cochés) à l'historique, et en
  direct partout sauf la correction 0 ci-dessous (acceptée le 11/10) : chaque autre
  changement de code est soit sous une option, soit une réécriture prouvée équivalente, soit
  du calcul que rien ne lit dans le script principal.
- 11 `plot()`, 28 réglages, mêmes positions.
- Seule différence visible par défaut : diagnostics décochés, les sept lignes « Diag » vides
  n'apparaissent plus dans la fenêtre de données (c'était la promesse de l'info-bulle).

## Correction 0 — le direct à la milliseconde partagée (rendu par défaut)

Acceptée le 11/10. Sur un graphique en ticks, `time_close` est na à l'exécution confirmée
d'une bougie en direct (mesuré par l'auteur : Diag 47 figé en direct), donc `time_close[1]`
est na pendant N+1 : `prevCloseKnown` est faux, `ownUpper = time − 1` même verrou actif, et
la lecture différée écartait le dernier tick de N daté de la milliseconde d'ouverture de
N+1 — tick que le bord avait montré et qu'un rechargement relit (≈ 22 % des frontières en
rafale le 25/09).

Correctif (lignes ~2280-2297) : verrou actif et clôture inconnue, le tableau propre est lu
**comme au bord** — jusqu'à l'ouverture de N+1 incluse, sous le plafond de compte « premier
numéro daté dès l'ouverture de N + 9 » ([DC]) :

```pine
bool liveOwnRead = hasPrevBar and blockSorted and closeIsLastTrade and not prevCloseKnown
int liveScan = math.min(count1, SCAN_MAX)
int liveFirstIndex = liveOwnRead and count1 > 0 ? firstIndexAtOrAfter(times1, prevOpen) : liveScan
int liveOwnCap = liveOwnRead and liveFirstIndex < liveScan ? array.get(serial1, liveFirstIndex) + EXPECTED_TICKS - 1 : na
int candidateIndex = not na(liveOwnCap) ? math.min(lastIndexAtOrBefore(times1, time), lastIndexAtOrBefore(serial1, liveOwnCap)) : ownUpper == exactUpper ? boundsLastIndex : lastIndexAtOrBefore(times1, ownUpper)
```

C'est plus sûr que le correctif d'une ligne proposé d'abord (`ownUpper = time`) : sans le
plafond de compte, la série aurait pu prendre plusieurs ticks de N+1 datés de la même
milliseconde et rangés en queue du tableau de N. Avec lui, la série suit exactement la
règle du bord et hérite seulement de son risque déjà mesuré (premier tick de N perdu ET
premier tick de N+1 à la milliseconde partagée dans le tableau de N : avance d'un tick,
≈ 1 % des bougies au Diag 64 du 25/09). Historique (clôture connue) : rien ne change. Pour
revenir à l'ancien comportement : remplacer `not na(liveOwnCap) ? … :` par rien dans
`candidateIndex`.

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
| En-tête §5, commentaire du pont | « seuls le préchauffage, la 1re bougie de séance, hors 1T coupent la courbe » | par défaut ; « Reprises strictes » la coupe aussi |
| En-tête §6 | plafond du bord sans l'option | mentionne l'option « plafond prudent » |
| Info-bulle « Garder la couleur » | « Reprises strictes », en fin de liste | en fin de la section « 2 — Rendu 10T » (TradingView regroupe par groupe) |
| Titres Diag 12, 33, 58 | renvoient aux Diag 25, 32, 48, 62 | précisent « script BSP Diag » |
| En-tête v11.66, jumeau | seule la DIAG-SECTION diffère | diffèrent aussi titre, nom court, défaut et info-bulle de « Afficher les diagnostics » |
| LIMITES, verrou de clôture | recul d'un tick « tant que le verrou n'est pas actif » | en direct le verrou est sans effet (time_close na à la confirmation) : recul possible à chaque milliseconde partagée, relu au rechargement |

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
  un tableau figé différent du tableau versé, Diag 10). Les vérificateurs ont jugé ce cas
  sans effet visible (1 voix sur 3) ; le code −8 est gardé parce qu'il ne coûte rien.
- **Tri du tableau figé mémorisé** : `isSorted(times1, serial1)` était refait à chaque
  mise à jour de N+1 sur le même tableau. Le résultat est mémorisé à l'exécution confirmée
  de N (bougie, taille, valeur) et réutilisé si la bougie et la taille concordent ; sinon
  recalculé. Gain : 10 à 30 itérations par exécution en direct, la moitié de tout `isSorted`
  au chargement, 2 000 itérations par bougie sur les tableaux démesurés.
- **Diagnostics décochés : `display.none`** sur les sept tracés de diagnostic (ils restaient
  listés, vides, dans la fenêtre de données).

## Écartées — à ne pas appliquer sans mesure

- **`varip` sur la réserve** (relecture « charge » ; 2 vérificateurs sur 3, mais à confiance
  0,4 : contenu identique prouvé, coût de la restauration non démontré ; le troisième
  rappelle que le profileur de l'auteur place le bloc de la réserve à ≈ 5 % en direct). Hypothèse : TradingView
  restaure chaque `var` avant chaque exécution ; une réserve de 6 000 à 9 000 objets copiée
  ~1 000 fois par seconde serait LE mécanisme de lag interne au script. La réserve n'est
  écrite qu'à l'exécution confirmée : `varip` donnerait un contenu identique à chaque
  exécution. Non appliqué : l'auteur a écrit « aucun varip » comme décision de conception,
  et le coût réel de la restauration n'est pas documenté. **C'est le test A/B le plus
  rentable au profileur** : une ligne (`varip array<Tick> tickPool`), à essayer un soir de
  clôture, et à garder seulement si le profileur le justifie.
- ~~**Verrou de clôture inerte en direct**~~ — **appliqué le 11/10 (correction 0)**, avec
  un plafond de compte en plus. Analyse d'origine : (relecture « série » ; 1 voix sur 3, mais les trois
  vérificateurs ont confirmé la chaîne ligne à ligne — seule la prémisse plateforme reste non
  mesurée). Prémisse : sur un graphique en ticks, `time_close` est na à l'exécution confirmée
  d'une bougie en direct — l'auteur l'a lui-même mesuré (Diag 47 figé en direct, v11.51) —,
  donc `time_close[1]` est na pendant N+1, `prevCloseKnown` est faux, `ownUpper = time − 1`
  même verrou actif, et la série écarte le dernier tick de N daté de la milliseconde
  d'ouverture de N+1, que le bord avait montré ; au rechargement il est relu. Effet : recul
  d'un tick sur les frontières partagées en direct (≈ 22 % des frontières en rafale le
  25/09). **Documenté dans les LIMITES, non corrigé** : le correctif
  `int ownUpper = closeIsLastTrade ? (prevCloseKnown ? exactUpper : time) : neighbourUpper`
  change le rendu par défaut et échange ce recul contre l'avance d'un tick quand l'élément
  est en fait le premier tick de N+1 (risque que le bord accepte déjà, Diag 64). C'est une
  décision de conception à prendre par l'auteur ; vérification possible avec le script Diag
  en direct : Diag 46 (clôture connue) et Diag 39 sur des bougies de rafale.
  Conséquence de la même prémisse : en direct, l'option « Frontière partagée : attribution
  par numéro » (`boundaryMs` exige `prevCloseKnown`) et le Diag 64 (bord en avance) ne
  peuvent pas se déclencher ; écrit dans les LIMITES.
- **POOL_MAX 6 000 → 2 000-3 000, SCAN_MAX 2 000 → 500** (2 voix sur 3 chacune, à
  confiance 0,45-0,55) : aucune lecture ne remonte au-delà du dernier élément sous une
  borne récente, mais le coût amorti de la purge est inchangé (≈ 20 copies par bougie
  quelle que soit la taille), les décalages d'`array.insert` ne dépendent pas de POOL_MAX
  (ils déplacent les seuls éléments plus récents), et le gain ne joue qu'au chargement des
  jours à tableaux démesurés. Non appliqué. Si l'auteur réduit quand même : **POOL_MAX ≥
  2 × POOL_BLOCK_MAX + 64** (un tableau verse un élément ET son prédécesseur par rang ; la
  proposition initiale « POOL_MAX 3 000 avec POOL_BLOCK_MAX 2 000 » était fausse).
- **Compteur des refus de `poolInsert`** (0 voix sur 3) : toutes les paires (numéro, heure)
  viennent du même contexte 1T, un refus n'est pas atteignable par les données.
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
comportement, les textes partagés, le tri mémorisé. Sa section DIAG-SECTION reste la sienne :
y reporter à la main le code `-8` du Diag 58, les libellés des Diag 55/58 et, si souhaité,
`display = showDiagnostics ? display.data_window : display.none` (inutile si ses
diagnostics restent cochés). Diffèrent aussi, par nécessité, le titre, le nom court, le
défaut et l'info-bulle de « Afficher les diagnostics ».

## Tableau des 42 trouvailles

Voix = vérificateurs sur 3 qui ont jugé la trouvaille réelle. « v11.66 » = traitée dans le
fichier corrigé.

| # | Domaine | Trouvaille | Voix | Suite |
|---|---|---|---|---|
| 1 | compilation | avertissements du compilateur sur les `ta.*` de `movingAverage` (switch) | 3 | commentaire, v11.66 (bénin : kind est simple) |
| 2 | compilation | idem sur les appels de `movingAverage` sous `if weightedMode` | 2 | bénin, moteur non touché |
| 3 | compilation | dix-neuf compteurs écrits jamais lus dans le principal | 3 | DIAG_FULL, v11.66 |
| 4 | compilation | balayage du Diag 63 calculé, Diag 63 absent | 2 | DIAG_FULL, v11.66 |
| 5 | compilation | `firstTickOffsetMs`, `valueMissingWithData`, `trailAdded`/`elementAdded` jamais lus | 3 | v11.66 |
| 6 | exécution | `firstTickOffsetMs` calculé à chaque exécution | 3 | v11.66 |
| 7 | série | info-bulle « Garder la couleur » fausse pour l'estimation | 2 | v11.66 |
| 8 | série | code mort de la lecture différée | 3 | DIAG_FULL, v11.66 |
| 9 | série | verrou de clôture inerte en direct | 1 | correction 0, v11.66 (acceptée le 11/10) |
| 10 | bord | `valueMissingWithData` jamais lu | 2 | v11.66 |
| 11 | bord | le bord ne lit pas sa propre traîne ; LIMITES fausse | 2 | LIMITES, v11.66 |
| 12 | charge | réserve `var` restaurée à chaque mise à jour → `varip` | 2 | A/B à mesurer, non appliqué |
| 13 | charge | POOL_MAX / marge 3-4 × trop grands | 2 | non appliqué (voir ci-dessus) |
| 14 | charge | tri du tableau figé refait à chaque mise à jour | 3 | v11.66 |
| 15 | charge | bord calculé sur chaque bougie d'historique | 3 | v11.66 |
| 16 | charge | SCAN_MAX 2 000 → 500 | 2 | non appliqué (chargement seulement) |
| 17 | charge | compteurs morts restaurés à chaque mise à jour | 2 | DIAG_FULL, v11.66 |
| 18 | charge | trois dichotomies en double | 3 | v11.66 |
| 19 | charge | `emptyInts` alloué à chaque exécution | 3 | v11.66 |
| 20 | moteur | estimation colorée pendant le préchauffage | 3 | correctif 2, v11.66 |
| 21 | moteur | commentaire « HMA à dénominateur négatif » | 3 | v11.66 |
| 22 | moteur | branches mortes des couleurs de l'axe | 3 | v11.66 |
| 23 | réserve | Diag 63 et trois compteurs de réserve non tracés | 2 | DIAG_FULL, v11.66 |
| 24 | réserve | en-tête « 6 000 au plus » | 3 | v11.66 |
| 25 | réserve | refus silencieux de `poolInsert` | 0 | rejetée |
| 26 | texte | « Garder la couleur » décochée et estimation | 3 | v11.66 |
| 27 | texte | « Masquer pendant le préchauffage » et estimation | 3 | v11.66 (texte + correctif 2) |
| 28 | texte | Diag 55 : −1 et −2 | 3 | v11.66 |
| 29 | texte | « décalés d'une bougie » — pas le Diag 55 | 2 | v11.66 |
| 30 | texte | info-bulles renvoyant à des Diag absents | 3 | v11.66 |
| 31 | texte | « tickHistoryInput, en fin de liste » | 3 | v11.66 |
| 32 | texte | « COMMENT ÇA MARCHE » §4 réserve | 3 | v11.66 |
| 33 | texte | échelle : « la couleur choisie » | 3 | v11.66 |
| 34 | diagnostics | ~25 séries et ~20 compteurs morts | 2 | DIAG_FULL, v11.66 |
| 35 | diagnostics | balayage du Diag 63 à chaque tick, diagnostics cochés | 2 | DIAG_FULL, v11.66 |
| 36 | diagnostics | Diag 58 : rang 1 affiché « 1 » | 1 | rejetée (inatteignable) ; code −8 gardé |
| 37 | complétude | lignes « Diag » vides dans la fenêtre de données | 3 | v11.66 |
| 38 | complétude | « seuls … coupent la courbe » ignore « Reprises strictes » | 3 | v11.66 |
| 39 | complétude | titres Diag renvoyant aux Diag 25/32/48/62 | 2 | v11.66 |
| 40 | complétude | contrat du jumeau et code mort hors section | 2 | DIAG_FULL + en-tête, v11.66 |
| 41 | complétude | « Reprises strictes », « en fin de liste » | 3 | v11.66 |
| 42 | complétude | défauts 5 000 barres / 60 000 ticks pour 1 000 dessinées | 1 | rejetée (réglage documenté) |
