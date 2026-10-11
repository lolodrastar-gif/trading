# BSP v11.66 — code mort (audit du 11/10)

Fichier : `src/BSP_v11.66.pine` (commit 6b050fe, 3560 lignes). Lecture seule : rien n'a été modifié.

## Méthode

1. Passe mécanique : on part des sorties du script principal (`plot`, `fill`, `hline`, `line/label/linefill.set_*`, `runtime.error`, réglages) et on remonte les dépendances. `DIAG_FULL = false` est replié comme une constante.
2. Trois relecteurs indépendants, chacun avec un angle :
   - ce qui n'atteint aucune sortie ;
   - le flux de contrôle (branches inatteignables, conditions toujours vraies ou fausses, doublons) ;
   - les fonctions et déclarations.
3. Chaque relecteur a été contre-vérifié par un sceptique chargé de réfuter ses trouvailles.

Résultat : 91 trouvailles, 86 confirmées, 5 corrigées (numéro de Diag ou coût mal attribués), aucune réfutée. Les sceptiques en ont ajouté quelques-unes, du même ordre (gardes redondantes).

## Verdict

Il y a du code mort dans le script principal, mais :

- **aucun ne change une sortie** : courbes, couleurs, remplissage, bord, échelle et les sept Diag ;
- **aucun n'a de coût mesurable** : ce sont des opérations scalaires, sans boucle. Le plus « cher » est une recherche dichotomique en double, d'environ 11 comparaisons, sur les exécutions en direct ;
- **la plus grande partie est voulue** : c'est le code du jumeau « BSP Diag », qui partage le fichier à l'octet près hors DIAG-SECTION.

Le compilateur Pine écarte en principe ce qui n'influence aucune sortie. Ce n'est pas vérifiable ici ; le Profiler le montrera, puisque ces lignes y apparaîtront ou non.

## 1. Code du jumeau « BSP Diag » (voulu)

### 1a. Désactivé par `DIAG_FULL` : compilé en constante, coût nul

| Lignes | Code | Diag du jumeau |
|---|---|---|
| 2655-2682 | balayage `looseScan` (lastInWindow, réserve, traîne) | 63 |
| 2773 | `firstTickOffsetMs` | (jumeau) |
| 2782 | `valueMissingWithData` | (jumeau) |
| 2959-2962 | `measureQuality` (vaut 0) | 34 |
| 2986-3039 | quinze compteurs `var` (bloc `if countNow and DIAG_FULL`) | 15, 17, 18, 22, 26, 27, 35, 39, 48, 49, 57, 60, 62, 63 |
| 3046-3054, 3560 | `lastEdgeShownTime`, `edgeAheadOfClose`, `edgeAheadCount` | 64 |
| 3063, 3537-3538 | `confirmedCloseKnownCount` | 47 |
| 3067-3071, 3554 | `lastConfirmedCount`, `frozenMismatch` | 10 |
| 3075-3084 | `executedBars`, `skippedBars` | 59 |
| 3090-3101 | `undeliveredSum`, `headGapSum`, `shortfallSum` | 41, 43, 42 |

Les lignes 3554 et 3560 restent exécutées, mais elles affectent seulement `na`.

### 1b. Non désactivé : calculé à chaque exécution, lu par le seul jumeau

Ce sont des opérations scalaires simples.

| Lignes | Code | Diag du jumeau |
|---|---|---|
| 1428, 2301 | `PLAUSIBLE_TICK_CAP`, `oversizedBlock` | 15 |
| 2344, 2610 | `prevClose = close[1]`, `priceMismatch` | 35 (et 34) |
| 2428, 2458 | `skippedTail`, `boundaryShared` | 39 (et 27, 34) |
| 2453, 2721 | `outOfBoundsCount`, `ambiguousAttribution` | 27 (et 34) |
| 2467-2469 | `emptyBar`, `staleData`, `unsortedBlock` | 18, 17, 49 |
| 2603-2604 | `recovered := false`, `tailRecovered := false` (écritures mortes ; `fromNeighbour := false` juste dessous, lui, est vivant : Diag 58) | 57, 62, 34 |
| 2697-2713 | `inBoundsSpan`, `interiorSerialGap`, `headSerialGap`, `undeliveredSerials`, `blockShortfall` | 41, 42, 43, 45 |
| 2720 | `overCount` | 48 |
| 2769-2770 | `shownReferenceSerial`, `boundarySetAside` (toujours faux ici) | 63 |
| 2957 | `priceCompared` | 34 |
| 2965 | `bridgeEffective` | 22 |
| 2997 | `barWasRealtime` | (jumeau) |
| 3111 | `unattributedShortfall` (vaut 0 − 0) | 45 |

Ces lignes pourraient être désactivées par `DIAG_FULL`, comme le reste. Sorties inchangées dans les deux fichiers.

## 2. Branches inatteignables

**Voulues : gardes de sûreté documentées, à garder.**

- `poolInsert`, `if pos >= size` (1903, 1909-1910) : documentée [DI].
- Diag 58, `recOffset == 1 ? -8.0` (3517) : documentée v11.66.
- Repli `isSorted` du tri mémorisé (2316) : documenté [DU].
- Contrôle du contexte 1T, `wrongContext` (2442, 3278) : Diag 03 et 26.
- Vérification des tailles et du tri des quinze tableaux (`blockAligned`, `curAligned`, `isSorted`) : Diag 49.

**Fortuites : sans effet.**

- `startBuyer = startFromClosed ? buyerPercent : edgeBuyer` (3416) : la branche `: edgeBuyer` n'est jamais lue. Le bloc qui lit `startBuyer` exige déjà `startFromClosed`.
- `pickLatest`, `arrayUpper` (2019) : le repli `array.get(times, size - 1)` n'est atteint par aucun appel. C'est la généralité documentée « upper na = sans borne haute ».
- `nextSignalState`, `if na(currentSpread)` (1679) : aucun des trois appelants ne lui passe na. Garde défensive.
- Valeurs `-1` de `recOffset` et `na` de `recSource` (2549, 2553) : jamais lues.

## 3. Valeurs imposées par la syntaxe ou ignorées

- **Éléments de tuple jamais lus.** Pine oblige à nommer chaque élément d'un tuple. Les valeurs sont calculées de toute façon dans la fonction.
  - `recContext` (2554) ;
  - `curPrice`, `curReference` (3302) ;
  - `edgePickTime`, `edgePickSerial` (3341) ;
  - `edgeRefreshContext`, `edgeRefreshPrice`, `edgeRefreshReference` (3344) ;
  - `edgeEstReferenceStep` (3364) ;
  - `loose0Index`, `loose0Time`, `looseTrailIndex`, `looseTrailTime` (2658, 2680 ; jumeau seulement).
- **Retour de `poolInsert` (`inserted`, 1888-1914) jamais lu.** Le commentaire [DU] de 1981-1982 le note déjà. Une variable booléenne par élément versé.

## 4. Réglage conservé

`axisMinorColor` (1582) et son groupe `G_AXIS` (1413) : la valeur n'est lue nulle part. C'est le 22e des 28 réglages. Le retirer décalerait les réglages 23 à 28 enregistrés dans les layouts. Il est gardé à dessein (`active = false`).

## 5. Redondances (sorties inchangées)

Environ 25 gardes ou alias répètent une condition déjà assurée. Exemples :

- `contextMultiplier` (2441) et `readTickIndex` (2427) : alias de `readContext` et de `candidateIndex`.
- `attributedCount = inBoundsCount` (2454) et `neighbourUsable = recFound` (2556) : alias.
- `activeFillBase` (3180) et `edgeFillBase` (3397) : alias.
- `edgeRefreshLower` (3334) : identique à `refreshLower` (2624).
- `serialBlockUsable` (2489) : identique à `boundsHasTick`.
- `inBoundsSpan` (2697) : identique à `inBoundsCount`.
- `liveFirstIndex` (2401) : même dichotomie que `firstInBoundsIndex` (2449). Elle tourne deux fois sur les exécutions en direct où la lecture prolongée est active.
- `refreshNeeded and` (2647), `hasMeasure and` (2783), `estimateGaps and` (2836, 3368), `not na(close[1])` (2836), `curOtherSource == 1` (3295) : déjà impliqués par la suite de la condition.
- `if greyBridge or undefinedMeasure or refreshUndefined` (2948) : les deux derniers cas ont déjà l'état 0.
- Gardes `na(…)` et `size > 0` devant des fonctions qui gèrent déjà le cas vide ou na.

**Moteur (`bspEngine1T`, 2125-2224).** Deux `if validRange` consécutifs, un alias `buyerRatio = lastBuyerShare`, etc. Ces redondances sont conservées volontairement : le moteur est figé à l'octet près depuis la v11.4.

## Recommandation

Ne rien changer à la v11.66 installée. Aucun de ces points ne touche le rendu ni la charge. Un nettoyage, par exemple :

- désactiver par `DIAG_FULL` les lignes du §1b ;
- retirer `inserted` et la branche `: edgeBuyer` ;
- réutiliser `firstInBoundsIndex`,

devrait être reporté dans le jumeau, réinstallé, et compilé dans TradingView, qu'on ne peut pas faire tourner ici. Pour un gain nul à l'écran, ce risque ne vaut pas la peine. À regrouper avec une prochaine version qui change autre chose.
