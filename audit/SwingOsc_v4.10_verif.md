# Swing Oscillator — v4.10 (code allégé) : vérification (04/11)

Fichiers : `src/swing/SwingOsc_v4.9.pine` (ton fichier, collé tel quel) et
`src/swing/SwingOsc_v4.10.pine` (la version allégée). Pine v5, non compilé ici.
Trois relectures indépendantes (attribution du Profiler et inventaire du coût,
proposition de réécriture, modèle d'équivalence), une construction, puis trois
relectures adverses (compilation v5, identité stricte, gain réel) : aucune n'a
trouvé de défaut.

## 1. Ce qui ne change pas

- `indicator()` : identique, sauf « v4.9 » → « v4.10 » dans le titre et le nom court
  (pour que les deux cohabitent sur un graphique). `precision = 4` et
  `max_bars_back = 5000` conservés.
- Les 15 réglages : mêmes positions, titres, valeurs par défaut, info-bulles, groupes
  (TradingView mémorise les réglages par position). Aucun réglage ajouté.
- Les tracés : mêmes 7 tracés visibles, même remplissage, même fond, mêmes 7
  diagnostics de la fenêtre de données, dans le même ordre, avec les mêmes titres.
- Les formules : les deux moyennes `ta.*` sont appelées à chaque bougie, avec les
  mêmes arguments, depuis les mêmes endroits.

## 2. Ce qui change (le code, pas le résultat)

| v4.9 | v4.10 | Pourquoi c'est identique |
|---|---|---|
| `selectedType == "HMA"`, `switch selectedType` (5 comparaisons de chaînes par appel, 2 appels par bougie), `maType == "EMA"` etc. (l. 350-352, 372, 402, 519) | cinq drapeaux `var bool isSMA … isWMA` calculés une fois ; `switch` sur les drapeaux | `maType` est un réglage, constant pendant toute l'exécution ; même branche `ta.*` choisie à chaque bougie |
| `bool reopenFixActive = sautReouverture and chart.is_heikinashi` (chaque bougie) | `var bool` | réglage et `chart.is_heikinashi` (« simple bool ») sont fixes |
| `oscLength`, `recursiveMa`, `windowMa`, `recursiveAlpha` recalculés chaque bougie | `var` | ne dépendent que des réglages, mêmes expressions, même ordre des opérandes |
| chaîne Heikin Ashi `cleanOpen` recalculée à chaque bougie | recalculée seulement pendant les 20 bougies après une pause (là où elle est lue) | hors fenêtre, la valeur n'est jamais lue ; dans la fenêtre, la chaîne part de la bougie de reprise dans les deux versions |
| récurrence d'oubli EMA/RMA entretenue à chaque bougie après la première pause | entretenue seulement pendant sa fenêtre | hors fenêtre, jamais lue ; remise à zéro à chaque pause dans les deux versions |
| boucle d'oubli SMA/WMA sur `période` itérations, avec des termes à zéro et `weightTotal` accumulé | boucle sur les seules bougies depuis la reprise ; somme des poids `n(n+1)/2` ou `n` calculée une fois | ajouter 0,0 ne change pas un flottant ; la somme des poids est un entier exact dans les deux cas |
| `maType == "HMA" and not na(thresholdRaw) and thresholdRaw <= 0.0` évalué deux fois | `hmaNegative` évalué une fois | même expression |
| en-tête de 169 lignes | en-tête de 45 lignes | un commentaire n'a aucun effet |

Lignes de code : 243 contre 247 ; fichier : 408 lignes contre 532.

## 3. Vérification

- **Modèle Python** (`scratchpad/swing/work/model/swing_model.py`, transcription des
  deux versions, formules TradingView des cinq moyennes, pauses ≥ 30 min et
  presque-pauses, Heikin Ashi) : 3 700 jeux de réglages × 3 000 bougies (11,1 millions
  de bougies), comparaison `==` bougie par bougie de l'oscillateur, de la ligne zéro
  et sa couleur, du remplissage, des quatre lignes de canal, du fond, de l'indice de
  couleur et des 7 diagnostics : **IDENTIQUE** partout. Contrôles négatifs : une
  mutation volontaire (`>` au lieu de `>=` sur la pause, `× (1/total)` au lieu de
  `/ total`) est détectée.
- **Compilation v5** (relecture adverse) : `switch` sans expression avec branche par
  défaut (v5), `var` initialisées depuis des réglages (en v5 elles gardent le
  qualificatif de leur valeur initiale, donc la longueur passée à `ta.ema`/`ta.rma`/
  `ta.hma` reste « input int » comme avant ; guide de migration v6, § « Mutable
  variables are always series »), fonction lisant des variables globales déclarées
  avant elle, boucle `for` à borne série, lignes repliées à 5 espaces, aucun
  tabulateur, tous les identifiants déclarés avant usage.
- **Gain réel** (relecture adverse) : hors des deux appels `ta.*` et des 17 sorties
  (inchangés, et sans doute dominants), 18 à 21 % d'opérations scalaires en moins par
  bougie selon le type de moyenne, plus la chaîne Heikin Ashi et la récurrence
  d'oubli hors de leurs fenêtres, et la moitié des itérations de la boucle d'oubli.
  Gain raisonné, non mesuré : seul le Profiler, même graphique, même séance, peut le
  chiffrer.

## 4. Les 34,2 % de la ligne 320

La ligne `bool reopenFixActive = sautReouverture and chart.is_heikinashi` est une
constante : elle ne peut pas coûter 34 % par elle-même. Ce que le manuel documente
(`writing/profiling-and-optimization.md`) : une ligne repliée est comptée sur sa
première ligne ; une structure `if`/`switch` porte le temps de toutes ses conditions ;
les déclarations, réglages et `var` ne sont pas profilés ; du code interne s'exécute
AVANT la première ligne profilée et APRÈS la dernière, hors de toute ligne, donc les
pourcentages ne font pas 100 ; les résultats sont des estimations gonflées par les
minuteurs du Profiler. La ligne 320 est la première ligne profilée du script.

Candidats, du plus au moins étayé :

1. Du travail sans ligne naturelle (mise en place des réserves d'historique, valeurs
   « simple » évaluées paresseusement) affiché « à côté » de la première ligne — le
   manuel documente ce genre de relocalisation pour `request.*()`, pas pour ce cas.
2. `max_bars_back = 5000` : coût DOCUMENTÉ (`error-messages.md` : « using
   max_bars_back = 5000 in a script that references up to only 700 bars back causes
   an excessive use of resources » ; `functions/indicator.md` : la valeur fixe la
   taille MINIMALE de toutes les réserves d'historique). Attribution au Profiler non
   documentée. C'est le seul coût par bougie amovible du script ; gardé en v4.10 par
   principe d'identité.
3. L'évaluation de `chart.is_heikinashi` : aucun coût documenté.

Tests d'une minute dans TradingView :
- survoler la ligne : lire les millisecondes absolues et le nombre d'exécutions (1 =
  coût unique au premier bar ; = nombre de bougies = coût par bougie) ;
- sur la v4.10, cette expression est un `var` (exécuté une fois) et la première
  ligne profilée devient `reopenBar` : regarder où les 34 % se déplacent ;
- sur une copie, remplacer `max_bars_back = 5000` par rien, et ajouter
  `max_bars_back(barBody, 500)` juste après `float barBody = …` ; comparer le temps
  TOTAL du Profiler. Les valeurs ne peuvent pas changer (une réserve d'historique ne
  modifie aucun calcul), mais une réserve trop courte donnerait une erreur
  d'exécution : c'est un essai, à faire sur une copie, pas sur la v4.10.

## 5. Pour l'installer

Coller la v4.10 comme un NOUVEL indicateur à côté de la v4.9 (titres différents),
reporter tes réglages (mêmes positions, mêmes défauts), et comparer en direct sur le
10 ticks : courbes, couleurs, remplissage, fond, fenêtre de données — tout doit se
superposer exactement. Puis profiler les deux, même séance. Ensuite seulement,
retirer la v4.9.

Ce qui n'a pas été fait, et pourquoi : pas de 16e réglage pour couper les
diagnostics (aucune économie documentée pour un tracé `display.none`, et un réglage
de plus que tu n'as pas demandé) ; pas de changement de `max_bars_back` (identité
d'abord) ; pas de passage en Pine v6 ; aucun tracé supprimé ni déplacé.
