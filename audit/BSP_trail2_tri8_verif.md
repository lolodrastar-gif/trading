# BSP TRAIL2 « essai tri8 » — audit complet (08/11)

Fichier : `src/test/BSP_trail2_tri8.pine` (commit 986a91a), collé tel quel avec son
en-tête complet (4 380 lignes, code à partir de la ligne 1552). Pine non compilé ici.
Quatre relectures indépendantes (compilation et exécution ; valeurs et modèle de rafale ;
réserve contre une version de référence ; coût, lag et comparaison avec les autres
versions), puis cinq contre-relectures adverses : aucune trouvaille réfutée, trois
nuancées. Tout ce qui est chiffré vient de modèles Python, pas de TradingView.

## Ce que c'est

La v4.3 d'audit (`audit/BSP_v43_audit_verif.md` : tri8, TRAIL64 et V4 actifs, 20 sondes
passives) plus une idée : chaque résultat 1T transporte aussi son DEUXIÈME prédécesseur
([2]). 25 zones de code changent :

| Changement | Lignes |
|---|---|
| 7 séries de plus demandées à TradingView (22 au lieu de 15) | 2724-2740 |
| `pickSecondTrail` : les [2] des 64 premiers porteurs du tableau vivant, utilisés dans la lecture des bougies closes, la reprise rafraîchie, le bord vivant et la reprise du bord | 2481-2497, 3007, 3162, 3870, 3921 |
| la réserve verse aussi les [2] ; capacité 13 000 → 15 000 | 2290-2348, 2117 |
| le 28e réglage « Reprises strictes » est REMPLACÉ, à la même position, par « Récupérer aussi le deuxième résultat 1T précédent », coché par défaut ; `strictBridges` devient une constante fausse | 1794-1799 |
| Diag 55 = 9 et Diag 58 = −9 pour cette source | 4120, 4124 |

## 1. Propre, sans bug ?

Oui, dans tout ce qui a pu être vérifié ici.

- **Compilation et exécution** : aucun problème trouvé. Vérifications statiques
  (déclarations, portées, arité, 528 arguments typés, tailles de tuple, usage avant
  déclaration : 0 erreur, et 8 défauts injectés exprès tous détectés) ; les 9 nouveaux
  appels passent les bons tableaux aux bons paramètres ; 0 lecture hors tableau sur
  200 000 cas aux quatre appels de `pickSecondTrail` et à la lecture de la source 4 (la
  garde `secondTrailAligned` est indispensable : sans elle, 65 249 erreurs). 22 éléments
  de tuple sur 127 permis. `engineRaw[2]` est le même opérateur que le `[1]` qui tourne
  depuis la v11.46.
- **Réserve** : identique, champ par champ, à une version de référence sans aucun
  raccourci, sur 4,8 millions de versements (1,7 million de purges, la tête de l'anneau
  ayant fait de nombreux tours) et 280 000 aux constantes réelles. Le nouveau raccourci
  (« + 2 ») est exact et nécessaire : la règle de la v4.3 perdrait des [2] (193 cas sur
  800). Les mutants demandés sont tous détectés.
- **Capacité 15 000** : prouvée et atteinte exactement. Au plus 9 000 au début d'un
  versement, au plus trois écritures par rang ([2], [1], le tick), au plus 2 000 rangs :
  14 999 avant la dernière écriture. Marge nulle, comme l'anneau. Avec l'ancienne
  capacité, le `runtime.error` partirait. En données réalistes : 10 940 au plus.
- **Valeurs** : 0 violation des 9 invariants (6 graines × 40 000 bougies adverses). Un
  tick [2] est toujours daté strictement dans la fenêtre de la bougie, jamais en avance,
  jamais plus ancien que celui qu'il remplace, et passe la garde « ne jamais reculer ».
  Case décochée : identique à la v4.3.

Non vérifiable ici : la compilation elle-même, la limite de taille du compilé (+7,5 %
par rapport à la v4.3), la limite de 1 000 variables (603 explicites contre 571), la
mémoire. Si l'éditeur affiche une erreur, la plus probable serait une limite de taille.

Cosmétique : la ligne 14 de l'en-tête (« Aucune modification ... des sélections ... ou
des 15 canaux ») est devenue fausse ; les commentaires de `poolAbsorb` ne parlent pas des
[2] ; le Diag 58 = −7 mélange maintenant les prédécesseurs de profondeur 1 et 2.

## 2. Mieux pour le lag ?

Non.

- **Navigateur** : il reçoit exactement les mêmes 49 sorties que la v4.3 (mêmes tracés,
  mêmes options d'affichage, mêmes objets du bord, mêmes appels de dessin par tick). Seuls
  les Diag 55 et 58 changent, masqués par défaut. La saccade de 15:30 est une saturation
  du navigateur (`audit/lolo_control_2026-11-02.md`) : TRAIL2 ne peut ni l'aider ni,
  plausiblement, l'aggraver.
- **Serveur** : plus lourd. Deux nouveaux balayages à chaque exécution en direct (lecture
  des bougies closes, bord), sans sortie anticipée : environ +50 lectures de tableau et
  +12 appels de fonction par exécution au calme ; 640 à 1 280 lectures quand le tableau
  vivant dépasse 64 éléments (régime vu au chargement, pas en direct) ; 0 pendant les
  trous gris (tableau vide). Au versement, une fois par bougie : 3,3 fois plus d'appels de
  fonction (186 contre 56 par bougie de dix ticks). Au chargement : +47 % de valeurs
  stockées, environ +5 à 10 % de temps (estimation).
- Trois raccourcis exacts existent si on gardait TRAIL2 : arrêter le balayage dès qu'un
  [2] dépasse la borne haute (lecture différée et reprise ; divise le coût par deux) ;
  sauter le balayage du bord quand la lecture propre est déjà le dernier élément ; sauter
  l'insertion d'un [2] qui est l'élément k−2 du même tableau (garde `k − 2 ≥ startRank`).
  Tous trois vérifiés au modèle, sorties identiques.

## 3. Plus fiable que les autres versions ?

À peine, dans un cas étroit, et pas là où tu le vois.

| Modèle de rafale, 200 000 bougies, graine 1 | v11.66 | v4.3 | TRAIL2 |
|---|---|---|---|
| Bougies grises | 84 289 | 84 289 | 84 289 |
| Grises sans remplissage (trous de livraison) | 31 749 | 31 749 | 31 749 |
| Bandes grises dans une zone colorée | 1 016 | 1 016 | 1 016 |
| Bougies montrant un tick plus ancien que le vrai dernier | 62 290 | 62 225 | 62 225 |
| Valeur changée par TRAIL2 par rapport à la v4.3 | | | 1 395 (0,70 %) |
| Couleur changée par TRAIL2 | | | 0 |

- TRAIL2 ne montre jamais un tick plus ancien que la v4.3 ; il change la valeur sur 0,65
  à 0,8 % des bougies (médiane 0,04 point de BP), presque jamais la couleur (0 à 4 sur
  800 000 bougies).
- Le vrai dernier tick n'est rattrapé que si le dernier tick de N ET le premier de N+1 sont
  perdus tous les deux : 0 / 0,034 / 0,175 % des bougies selon que 0, 1 ou 5 % des
  bougies perdent leur premier tick (le Diag 64 suggère environ 1 %). Environ 95 % des
  changements sont autre chose : à la milliseconde partagée, l'avant-dernier tick au lieu
  de l'antépénultième, jamais le dernier.
- **Les bandes grises de ta capture ne changent pas** : pendant un trou de 27 à 164
  bougies, rien n'est livré, il n'y a aucun porteur à lire. 0 bougie sauvée quand le trou
  se termine par un gros paquet ; au plus la dernière bougie du trou sinon.
- La milliseconde partagée (Diag 63), que l'en-tête de ta v11.66 désigne comme le premier
  résidu de fidélité (v11.49 : « pas la profondeur de la traîne »), est inchangée : TRAIL2
  utilise la même fenêtre stricte.
- La zone neutre est inchangée.
- Bord vivant : il lit maintenant le [2] de son propre tableau, mais toujours pas le [1].
  Il peut donc montrer un tick de profondeur 2 alors qu'un tick plus récent de profondeur
  1 existe (cas construits ; 0 fois dans le modèle de rafale à la dernière mise à jour).
  L'accord entre le bord et la bougie close est inchangé au modèle de base et un peu moins
  bon quand des premiers ticks se perdent : la bougie close gagne des ticks que le bord ne
  voyait pas. La couleur, elle, ne change pas.

TRAIL2 ne suit pas le plan écrit dans ton en-tête (v11.48, l. 921-923 du fichier) :
mesurer d'abord la profondeur 2 et 3 avec les seules heures et numéros (4 tableaux
d'entiers), recherche éteinte, puis décider. Ici : 7 séries complètes, actives par
défaut, profondeur 3 jamais regardée, et une mesure seulement à travers les valeurs déjà
changées (Diag 58 = −9, qui ne compte pas les [2] venus de la réserve, notés −7).

## 4. Le piège du 28e réglage

« Reprises strictes » (décochée par défaut) est remplacée à la même position par la case
TRAIL2 (cochée par défaut). Si tu colles ce code sur un script BSP déjà enregistré qui a
des instances sur le graphique, l'ancienne valeur « décochée » peut s'appliquer à la case
TRAIL2 : la récupération serait éteinte sans signe sur le graphique, alors que les 7
séries de plus restent demandées. Le manuel ne dit pas comment TradingView rattache les
valeurs enregistrées. Pour éviter : ajouter TRAIL2 comme NOUVEL indicateur (ce que dit son
en-tête) ou « Réinitialiser les paramètres », vérifier que la case est cochée ; Diag 58 =
−9 ou Diag 55 = 9 prouvent qu'elle travaille (leur absence ne prouve rien).

## Verdict

- Propre : oui, aucun bug trouvé ; à compiler dans TradingView.
- Lag : non, même charge pour le navigateur, un peu plus pour le serveur.
- Fiabilité : un gain réel mais minuscule et non mesuré, qui ne touche ni les bandes
  grises, ni la milliseconde partagée, ni la zone neutre.
- Recommandation : ne pas l'installer sur « lolo ». Si on veut savoir si la profondeur 2
  vaut quelque chose, faire d'abord la copie de mesure prévue par l'en-tête (heures et
  numéros des prédécesseurs 2 et 3, compteurs passifs, récupération éteinte), une séance,
  puis décider sur les chiffres.

Scripts et résultats : `scratchpad/trail2/work/` (compile-runtime, semantics, reserve,
cost-lag-compare, refute).
