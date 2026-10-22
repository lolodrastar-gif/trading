# BSP v11.66-opt2 — vérification du candidat (22/10)

Fichier : `src/test/BSP_v11.66_opt2.pine` (commit 9815799), transcrit tel quel du candidat
collé le 22/10, produit par un autre assistant à partir de la v11.66-opt installée
(`src/test/BSP_v11.66_opt.pine`, commit 2fd8a68). Pine non compilé ici : TradingView
seul tranche la compilation.

## Question posée

« Est-il mieux ? », au sens : fait-il moins lagger le setup en rafale. Deux questions
distinctes :

1. **Change-t-il quelque chose de ce que le navigateur reçoit ?** Non. Voir §4.
2. **Est-il identique en sorties et compilable ?** Identique : oui, sans contre-exemple.
   Compilable : très probable, trois points nouveaux à confirmer dans l'éditeur. Voir §2, §3.

## 1. Ce qui change (diff corps à corps, hors en-tête)

20 hunks, 287 lignes de diff, regroupés en douze blocs. Réglages : 28, même ordre, mêmes
défauts, mêmes libellés, octet pour octet. Tracés : 11 `plot`, 1 `fill`, 1 `hline`,
2 lignes, 2 étiquettes, 1 remplissage de lignes, mêmes `display`, mêmes `set_*` par tick,
`calc_bars_count = 5000`. Seuls le titre et le nom court changent (« BSP opt2 »).

| Bloc | Changement | Gain par exécution en direct |
|---|---|---|
| H1 | `firstIndexAtOrAfter` : sorties directes quand la cible est avant le premier ou après le dernier élément | ≤ 11 itérations évitées sur le tableau propre, cas courant |
| H2 | `lastIndexAtOrBefore` : idem | ≤ 11 itérations, cas courant (borne au-delà du bloc) |
| H3 | `poolRankBySerial` : sorties directes et rang deviné quand la fin de la réserve est contiguë | ≤ 13-14 itérations sur la réserve, cas courant |
| H4 | `poolLastAtOrBefore` : sorties directes | ≤ 13-14 itérations, cas courant (`time − 1` au-delà de la réserve) |
| H5 | `poolInsert` : trois cas explicites (au-delà, en deçà, égal au dernier numéro) | une lecture de moins par élément versé, à l'exécution confirmée seulement |
| H6 | `pickLatest` : réserve ignorée si son dernier élément ne bat pas déjà le tableau propre ; plafond de numéro cherché seulement s'il peut borner | une dichotomie de réserve évitée quand le tableau vivant porte le tick le plus récent (le cas normal) |
| H7 | `candidateValues` : un seul `array.get` de réserve au lieu de six | 5 lectures de moins par candidat venu de la réserve |
| H8 | `pickTrail` : numéro et contexte lus seulement si l'heure est dans la fenêtre | ≤ 2 lectures de moins par élément de traîne hors fenêtre, 16 éléments au plus |
| H9 | `boundsLastIndex`, `candidateIndex` gardés par `hasPrevBar and blockSorted` | rien en régime normal ; 1-2 dichotomies de moins sur un bloc non trié (Diag 49) |
| H10 | reprise rafraîchie : réutilise le candidat de la récupération stricte quand il existe | un `pickLatest` et un `pickTrail` de moins sur une bougie sans mesure dont le candidat strict est dépassé |
| H11 | `estimateStep` appelé seulement quand son résultat peut servir | ≈ 38 opérations scalaires de moins par bougie, option « Estimer » cochée seulement |
| H12 | suppression de `lastEdgeShownTime := DIAG_FULL and edgeFresh ? curCandidateTime : na` ; journal de versions retiré de l'en-tête | une affectation constante de moins ; voir la réserve §3b |

Tout cela se compte en microsecondes côté serveur TradingView. Aucune de ces lignes ne
s'exécute dans le navigateur.

## 2. Identité des sorties

**Rejeu différentiel en Python** (scripts du jumeau dans le bac à sable de session,
`fuzz_bsp.py`) : les deux versions des fonctions pures, transcrites ligne à ligne,
comparées sur des entrées aléatoires respectant les invariants du script (préfixes triés,
réserve triée par numéro strictement croissant et heure non décroissante, trous de
numéros, heures égales aux frontières, bornes na, fenêtre vide, plafond de numéro
au-dessous, égal, au-dessus du candidat, `onlyNewer` avec numéro montré na).

| Fonction | Cas | Contre-exemples dans les invariants |
|---|---|---|
| firstIndexAtOrAfter | 80 000 (62 794 valides) | 0 |
| lastIndexAtOrBefore | 80 000 (62 731) | 0 |
| poolRankBySerial | 80 000 (59 764) | 0 |
| poolLastAtOrBefore | 80 000 (59 764) | 0 |
| poolInsert, état de la réserve compris | 80 000 (66 903) | 0 |
| poolAbsorb, réserve comparée après chaque versement | 13 861 pas | 0 |
| pickLatest | 80 000 (59 994) | 0 |
| pickTrail | 80 000 (64 563) | 0 |
| candidateValues | 80 000 | 0 |
| bloc de reprise rafraîchie (H10, composite) | 80 000 (61 632) | 0 |

Cinq graines, puis une sixième de 8 000 cas rejouée à part : même résultat. Les seules
différences apparaissent sur des entrées qui violent les invariants (réserve mélangée,
tableau non trié déclaré trié, tailles désalignées) ; chaque site d'appel a été relu pour
établir que le script ne produit jamais ces entrées (`blockSorted`, `curSorted`,
`curAligned`, construction de la réserve par `poolInsert` seul).

**Relecture par bloc** : trois relecteurs indépendants par bloc (équivalence des sorties,
compilation, coût), chargés de réfuter. 36 verdicts, tous « équivalent », confiance haute
(H3 compilation : moyenne). Argument de H10, le seul bloc non mécanique : la fenêtre de
reprise contient la fenêtre stricte (`refreshLower ≤ certainLower`), le maximum strict
domine donc tout candidat de reprise, et `newerThanShown` est monotone dans l'ordre
(heure, numéro) : si le maximum strict n'est pas plus récent que la valeur tracée, aucun
candidat ne l'est. Dans le script, cette branche ne peut d'ailleurs être atteinte qu'avec
un candidat strict dépassé (sinon `hasMeasure` serait vrai) : elle rend toujours « aucun »,
comme avant.

**Critique de complétude** : diff refait indépendamment, identique ; aucune ligne de code
hors des douze blocs ; ordre des effets de bord inchangé (la réserve n'est écrite qu'en fin
de script, à l'exécution confirmée, après toutes les lectures, dans les deux fichiers).

## 3. Compilation : trois points nouveaux

a. **Dépendance au `and` paresseux.** Deux lignes lisent un tableau derrière un `and` :
   `guess >= 0 and guess < size and array.get(pool, guess).serial == target` (H3) et
   `not na(serialCap) and poolRank >= 0 and array.get(pool, poolRank).serial > serialCap`
   (H6). La v11.66 et la v11.66-opt n'ont jamais compté sur l'évaluation paresseuse : elles
   gardent chaque lecture par un ternaire. Pine v6 évalue `and`/`or` en court-circuit
   (notes de version v6, novembre 2024 : second opérande non évalué si le premier décide),
   et le script est en `//@version=6` : pas d'erreur attendue. Le rejeu en évaluation
   non paresseuse donne 9 220 erreurs d'exécution sur entrées valides (`array.get` à un rang
   négatif dès qu'un trou de numéros dépasse la taille de la réserve) : c'est bien une
   dépendance réelle, acceptable en v6 seulement. Mitigation à coût nul :
   `int guessSerial = guess >= 0 and guess < size ? array.get(pool, guess).serial : na`
   puis `if guessSerial == target`, et de même pour H6.

b. **Jumeau « BSP Diag » cassé.** La ligne supprimée en H12 est la seule écriture de
   `lastEdgeShownTime`. Dans le script principal elle vaut `na` en constante
   (`DIAG_FULL = false`) : aucune sortie ne change. Mais le jumeau partage le fichier octet
   pour octet hors DIAG-SECTION avec `DIAG_FULL = true` : dérivé de l'opt2, son Diag 64
   (`edgeAheadCount`) resterait à 0 pour toujours, sans erreur de compilation. Pour garder
   le contrat du jumeau, remettre la ligne en fin de script.

c. **`if`/`else` rendant un tuple en fin de fonction** (`candidateValues`, H7). Aucun
   précédent dans le code. La documentation Pine (structures conditionnelles, système de
   types) admet qu'une structure `if` rende un tuple et qu'une fonction rende le résultat de
   la structure qui termine son corps ; les deux branches ont les mêmes six types. Seul le
   compilateur confirme l'unification d'un tuple de champs de type utilisateur avec un
   tuple de variables locales.

Autres points relus sans réserve : portée des variables déclarées dans les blocs, tuples
déclarés dans un `else` au niveau du script, réaffectation d'un `bool` par `:=`, nombre de
blocs locaux (≈ 123 → 147, loin des limites), aucun nouvel avertissement de fonction
appelée conditionnellement (fonctions pures, sans `ta.*` ni historique).

Perdu au passage : l'en-tête de 1 400 lignes (journal des versions, contrat du jumeau), les
commentaires d'invariants de `pickLatest` (réserve triée par numéro et par heure, ceux-là
mêmes dont H6 dépend) et du cas inatteignable de `poolInsert` ; deux commentaires devenus
faux restent (`lastEdgeShownTime` « affectée en fin de script »). Rien de tout cela ne
compile ni ne s'exécute.

## 4. Effet sur le lag : aucun possible

Ce que TradingView envoie au navigateur pour ce script : les valeurs par bougie des
11 tracés, du remplissage et de la ligne, les mises à jour des 5 objets de dessin, les
métadonnées des réglages, le titre. Tout est identique entre opt et opt2, titre mis à part.
Le code Pine lui-même s'exécute sur les serveurs TradingView ; les commentaires ne font
pas partie du compilé.

Les mesures de Lolo Guard (tâches longues, blocages de 358 à 388 ms le 21/10) décrivent le
fil d'exécution de l'onglet Edge. Un script serveur ne peut ni bloquer ce fil ni le
libérer : il n'y a rien dans l'opt2 qui puisse déplacer ces chiffres. La conclusion de
`audit/BSP_v11.66_lag_22h.md` ne bouge pas : témoin nu fluide, rechargement qui remet
d'aplomb avec le même BSP, Profiler normal ; la somme du layout sur un seul fil dépasse le
seuil en rafale, et le BSP y est une part, pas le déclencheur.

## 5. Verdict

- Sorties : identiques à la v11.66-opt installée, zéro contre-exemple.
- Compilation : très probable ; trois points nouveaux (§3), dont deux se corrigent en trois
  lignes (ternaires en H3 et H6, ligne `lastEdgeShownTime` restaurée).
- Lag : aucun effet possible, ni en mieux ni en moins bien.
- Gain réel : quelques dichotomies de moins par exécution, côté serveur. Invisible.

Recommandation : ne pas l'installer pour le lag, il n'y a rien à y gagner. Si on veut
l'installer quand même, appliquer d'abord les trois corrections du §3a-b, compiler dans
TradingView et comparer les Diag 11, 12, 30, 33, 55, 58, 61 sur les mêmes bougies que
l'opt. Les leviers du lag restent ceux du rapport 22h : 60 ou 120 Hz sur l'écran du
layout, rechargement avant les rafales, séparation des deux graphiques en deux processus.
