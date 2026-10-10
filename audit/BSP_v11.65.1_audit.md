# Audit de BSP v11.65.1 (1T sur 10T)

Date : 10/10/2026. Relecture statique du code collé, ligne par ligne.
**Limite :** aucun compilateur Pine n'existe hors de TradingView. Le script n'a donc
été ni compilé ni exécuté ici, et sa latence n'a pas été mesurée.

## 1. Erreurs d'exécution et compilation : rien trouvé

- **Accès aux tableaux.** Chaque `array.get` est gardé, soit par un test de taille, soit par
  `curSorted` / `blockSorted`, qui imposent `curAligned` / `blockAligned` (les quinze
  tableaux ont la même taille). C'est le cas dans `candidateValues`, `poolAbsorb`,
  `pickTrail`, `pickBoundary`, `curOwnCap` et `firstTickOffsetMs`.
- **Boucles `for` en v6.** En v6, une boucle `for` dont la borne de fin est plus petite que
  celle de départ tourne à l'envers. Toutes les boucles sont gardées contre ce cas :
  `size > 1`, `n > first`, `n > 0`, et `excess > 3000` pour la purge.
- **Coût des boucles.** Chaque boucle a un plafond : `SCAN_MAX` = 2 000, `TRAIL_SCAN_MAX` = 16,
  64 pour le balayage des diagnostics, et `POOL_MAX` pour la purge.
- **Types.** Les types des tableaux renvoyés par `request.security_lower_tf` correspondent
  aux séries du moteur (int → `array<int>`, float → `array<float>`).
- **Ordre des déclarations.** Chaque variable est déclarée avant d'être utilisée.
- **Arguments.** Le nombre d'arguments est correct pour `estimateStep`, `pickLatest`,
  `pickTrail`, `pickBoundary`, `candidateValues` et `poolAbsorb`.
- **Comptes annoncés.** 11 `plot()` (2 courbes, 2 chiffres d'échelle, 7 diagnostics) et
  28 réglages : conforme à l'en-tête.
- **Moteur `bspEngine1T`.** Les formules B, S et TR, l'écrêtage, le préchauffage et
  l'hystérésis sont cohérents. `rangeReference[1]` est bien lu sur la barre 1T précédente.
- **Avertissements seulement.** Les variables `trailAdded`, `elementAdded` et
  `firstTickOffsetMs` ne sont pas lues dans le script principal, de même que la plupart des
  compteurs qui ne sont plus tracés. `axisMinorColor` est inactif, mais c'est voulu.

## 2. Comportement par défaut : conforme

Avec les options 23, 24, 27 et 28 décochées :

- une bougie sans tick est toujours reprise ;
- « Garder la couleur » s'applique pendant dix bougies ;
- le bord lit son propre tableau jusqu'au premier numéro reçu + 9.

C'est le comportement de la v11.63 annoncé.

Le bord et la série suivent la même politique pour la valeur, l'état et le remplissage, dans
chaque cas : mesure, reprise rafraîchie, calcul indéfini, reprise invalidée, estimation et
reprise simple. Le correctif v11.65.1 (estimation au bord coupée dès la 11e bougie en mode
strict) est cohérent avec `carryAllowed`, puisque `missingRun` ne compte pas la bougie en
cours au bord.

## 3. Un bug trouvé, seulement avec l'option « Reprises strictes » cochée (28e réglage)

Le bord et la série ne donnent pas la même valeur dans un cas :

- « Reprises strictes » est cochée ;
- la courbe est déjà coupée (10 bougies ou plus sans tick) ;
- la bougie en cours reçoit un tick dont le ratio est indéfini (calcul indéfini ou reprise
  invalidée).

Ce qui se passe :

- **Série** (lecture différée) : `undefinedMeasure` ou `refreshUndefined` remet
  `missingRun` à 0. `carryAllowed` redevient donc vrai et la bougie trace `lastBuyer` en gris.
- **Bord** : `edgeCarryValue` teste encore `missingRun < 10`, donc il ne trace rien.

Deuxième écart dans la même situation : la série reprend `lastBuyer`, alors que le bord
reprend `buyerPercent`, qui vaut `na` après une coupure.

Avec l'option décochée (défaut), `buyerPercent == lastBuyer` dans tous les cas : le
correctif ci-dessous ne change rien au rendu par défaut.

### Correctif (deux lignes, section BORD VIVANT)

```pine
// avant
bool edgeCarryValue = edgeCarryAllowed and (not strictBridges or missingRun < BRIDGE_MAX_BARS)
float edgeBuyer = edgeFresh ? curBuyer : edgeRefreshed ? edgeRefreshBuyer : curUndefined and not na(curOwnFallback) ? curOwnFallback : edgeEstimated ? edgeEstClamped : (edgeCarryValue ? buyerPercent : na)

// après
bool edgeCarryValue = edgeCarryAllowed and (not strictBridges or missingRun < BRIDGE_MAX_BARS or curUndefined or edgeRefreshUndefined)
float edgeBuyer = edgeFresh ? curBuyer : edgeRefreshed ? edgeRefreshBuyer : curUndefined and not na(curOwnFallback) ? curOwnFallback : edgeEstimated ? edgeEstClamped : (edgeCarryValue ? (strictBridges ? lastBuyer : buyerPercent) : na)
```

Il faut reporter le même correctif dans « BSP Diag v11.65 ».

## 4. Lag en rafale

### Ce que le script coûte à chaque tick en direct

Le coût est faible et borné. À chaque exécution :

- 8 lectures `[1]` ;
- 2 appels à `isSorted` sur environ 10 éléments (2 000 au pire, si un tableau est démesuré) ;
- 6 à 8 dichotomies sur la réserve (6 000 à 9 000 éléments, soit environ 14 pas chacune) ;
- `pickTrail` sur 16 éléments au plus ;
- environ 10 appels `line.set_*`, `label.set_*` et `linefill.set_*`.

Cela fait de l'ordre de quelques centaines d'opérations. Aucune ne grandit avec la rafale :
pendant une rafale, les tableaux 1T sont souvent vides.

`poolAbsorb` ne tourne qu'une fois par bougie, à sa confirmation. Il ajoute environ
10 éléments, et une recopie de 6 000 références a lieu toutes les ~300 bougies, soit
toutes les 3 s environ dans une rafale à 100 bougies par seconde.

Avec les diagnostics décochés, le balayage du Diag 63 (`looseScan`) ne tourne pas.

### Ce qui n'est pas mesurable par lecture du code

1. **La requête 1T** (`request.security_lower_tf`) renvoie 15 tableaux à chaque mise à jour,
   dont 7 pour la traîne. C'est TradingView qui la calcule. C'est le premier poste au
   profileur (43 % au chargement en v11.52).
2. **Les dessins du bord** (2 lignes, 1 remplissage, 2 points) sont mis à jour à chaque
   tick, soit environ 100 fois par seconde en rafale, et redessinés par le navigateur.
3. **La sauvegarde de la réserve à chaque bougie** (mécanisme de retour en arrière de
   TradingView) : la réserve est un tableau `var` de 6 000 à 9 000 objets. Son coût réel
   n'est pas documenté. Si le profileur ou le test de retrait accuse le script, réduire
   `POOL_MAX` est un levier à essayer.

### Pistes pour alléger, sans toucher au moteur

- **Historique 1T demandé.** Le défaut est 60 000. La règle est 10 × « Barres calculées »
  + 43 × « Longueur » : pour environ 1 800 barres, 30 000 suffisent. Cela ne joue que sur
  le chargement et les rechargements.
- **Calculs du bord sur les bougies d'historique.** Dans le script principal, ils ne servent
  qu'au Diag 64, qui n'est pas tracé. Les limiter à `barstate.islast` accélérerait le
  chargement, mais pas le direct.
- **« Barres 10T dessinées ».** Le défaut est 1 000 ; 500 allège le rendu du remplissage.

### Le test qui tranche

1. Lancer le Pine Profiler vers 21:50.
2. À une autre clôture de New York, retirer le BSP du layout et comparer la fluidité.

Si le lag reste sans le BSP, la cause est ailleurs (navigateur, autres indicateurs, nombre
de graphiques). S'il disparaît, regarder dans le profileur la ligne de
`request.security_lower_tf` et le bloc de fin de script.
