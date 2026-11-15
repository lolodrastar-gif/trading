# BTM - Trend Cockpit v8.1 : vérification de conception (15/11)

Fichier relu : `src/lolo2/BTM_Trend_Cockpit_v8.1.pine` (collage du 15/11, enregistré tel
quel, commit 311278d, 480 lignes). Les « l. N » ci-dessous sont les lignes de ce fichier.
Pine v6, **non compilé ici**.

**État : version 1, provisoire.** Trois relectures sur cinq sont terminées (compilation,
logique des jauges, volume et charge). Les deux autres (multi-unités et temps réel,
adéquation à l'usage) et les contre-relectures adverses tournent encore. Ce rapport sera mis
à jour à leur retour. Ce qui est écrit ici a été recoupé de deux façons :

1. par ma lecture ligne par ligne du code ;
2. par ma propre émulation Python des cinq jauges, écrite sans reprendre le code des
   relecteurs (`quick.py`, 3 × 300 000 bougies simulées). Elle retrouve leurs chiffres
   principaux : libellé Ichimoku, Supertrend au retournement, pied de panneau, pente, biais
   de l'activité en direct.

Limite : il n'y a aucune donnée de marché ici. Toutes les fréquences viennent de bougies
simulées (marche aléatoire au pas de 0,25, avec ou sans dérive). Ce sont des ordres de
grandeur, pas des mesures sur le NQ. Rien n'a été observé sur TradingView.

## Verdict

- **Pas d'erreur de calcul trouvée dans les cinq jauges.** Les scores restent entre 0 et 100,
  la barre est toujours du côté de l'état affiché, les conventions sont justes (Supertrend,
  ordre des sorties DMI et MACD, nuage lu sous la bougie courante).
- **Pas de repeinture sur les bougies clôturées.** Les unités supérieures sont lues sur la
  bougie précédente terminée, avec la bonne écriture (`[1]` et `lookahead_on`).
- **Aucune erreur de compilation trouvée à la lecture.** Un avertissement certain (l. 268),
  un possible (l. 387). À confirmer dans l'éditeur.
- **Mais la conception a des défauts réels, presque tous dans ce que le panneau dit.**
  Plusieurs libellés ne décrivent pas ce qui est calculé. Douze points sont visibles avec les
  réglages par défaut (§ 2).
- **Sur ton usage (1 minute ou moins)**, les plus gênants sont : le libellé « IN CLOUD », la
  barre Supertrend, le mot « TRENDING », la ligne d'activité en direct, le bloc
  « SELL / BUY » qui n'utilise pas le volume à cette unité, et les alertes de consensus en
  retard d'une bougie avec la fréquence conseillée (§ 7).
- **Charge : moyenne, pas légère.** 8 ou 9 requêtes par bougie, environ 290 appels de tableau
  par tick, et un calcul complet des jauges fait en double pour rien avec les réglages par
  défaut (§ 5).
- **Ce que c'est** : un tableau de bord de cinq suiveurs de tendance classiques, calculés sur
  le même prix. Il décrit ce que le prix vient de faire. Sur un marché simulé sans aucune
  tendance, le bandeau affiche tout de même « BULLISH BIAS » ou « BEARISH BIAS » une bougie
  sur deux (§ 6).

## 1. Ce qui est juste

- **Bornes** : scores entre 0 et 100, pente entre −100 et +100, états −1 / 0 / +1. Relecture
  « logique » : 6,6 millions de bougies simulées, y compris des cas extrêmes, aucun score du
  mauvais côté de 50 pour un état directionnel.
- **Conventions** : `ta.supertrend` direction négative = hausse (l. 166). `ta.dmi` et
  `ta.macd` dépaquetés dans le bon ordre (l. 156, 161). Nuage lu à `[déplacement − 1]`
  (l. 174-175), comme le nuage tracé sous la bougie par l'Ichimoku de TradingView.
- **Pente** (l. 184-185) : `ta.linreg(…, 0) − ta.linreg(…, 1)` est bien la pente de la
  régression par bougie.
- **Unités supérieures** (l. 195, l. 229-230) : `[1]` avec `lookahead_on`, donc bougie
  précédente terminée, identique en historique et en temps réel.
- **Mode LIVE** : les bougies clôturées ne changent plus, comme l'annonce l'en-tête (l. 16).
- **Bougie blanche** : elle ne peut pas clignoter. Le volume d'une bougie ne fait que monter
  et les 100 bougies de référence sont figées.
- **Tableau** : 17 rangées sur 20 au maximum, aucune cellule hors limites, aucune fusion qui
  se chevauche (6 144 dispositions testées par la relecture « compilation »).
- **Limites de TradingView** : 9 requêtes exécutées sur 40 permises, 37 éléments de tuple sur
  127.
- **Pas d'erreur d'exécution** avec les réglages par défaut sur un graphique en temps
  (minutes, heures, jours, secondes).

## 2. Défauts visibles avec les réglages par défaut

### D1. ICHIMOKU affiche « IN CLOUD » alors que le prix est hors du nuage (l. 182, l. 417)

L'état vaut +1 seulement si le prix est au-dessus du nuage **et** Tenkan au-dessus de Kijun.
Dans tous les autres cas l'état vaut 0 et le libellé de l'état 0 est « IN CLOUD ». Prix
au-dessus du nuage avec Tenkan encore sous Kijun : le panneau écrit « IN CLOUD » en orange.
C'est faux, le prix est dehors.

Simulation : le libellé est à l'écran sur environ 30 % des bougies d'un marché sans tendance
et il est faux un peu plus d'une fois sur deux. Cela fait 16 à 23 % de toutes les bougies
(7 à 15 % en marché orienté). Ma propre émulation donne 17 %.

### D2. SUPERTREND : barre pleine sur la bougie même du retournement (l. 167)

La barre vaut 40 % plus 60 % × la distance entre le prix et la ligne Supertrend, plafonnée à
3 ATR. Or au retournement la nouvelle ligne est placée, par construction, à environ 3 ATR du
prix. Résultat : « 100 % » dès la première bougie d'une tendance vieille d'une bougie.
L'en-tête dit « full = strongest » (l. 7).

Simulation (la mienne et celle de la relecture) : 95 % des retournements affichent 100 % sur
la bougie du retournement. Ensuite la barre **baisse** : 96 % une bougie après, 92 % après
2, 86 % après 5, 83 % après 10. Sur l'ensemble des bougies la médiane est vers 90 % et la
barre ne descend jamais sous 40 % (7 voyants). Cette jauge est donc presque toujours presque
pleine : elle mesure la distance au stop, pas la force de la tendance.

Hors défaut : le « 3.0 » de la l. 167 est écrit en dur au lieu du réglage « Factor ».

### D3. Pied de panneau : « TRENDING » veut seulement dire « pas RANGING » (l. 316-317, l. 477-479)

« RANGING » exige les deux conditions : ADX sous 20 **et** pente dans la zone plate. Tout le
reste s'affiche « TRENDING ». ADX à 16 et pente à 18 % : la rangée ADX dit « NO TREND » et le
pied dit « TRENDING » juste dessous.

Simulation sur un marché sans tendance : « TRENDING » sur 83 à 85 % des bougies. « TRENDING »
pendant que la rangée ADX dit « NO TREND » : 23 à 24 %. « TRENDING » pendant que le bandeau
dit « NO CLEAR BIAS » : 37 à 39 %.

### D4. Une jauge neutre n'est pas vide (l. 369-373, en-tête l. 6-7)

La longueur de la barre est l'écart du score à 50, dessiné dans la couleur de l'état. Quand
l'état est neutre, la barre est orange mais elle peut rester longue, et rien ne dit de quel
côté elle penche. Exemple : prix 3 ATR au-dessus de l'EMA 200, EMA 50 au-dessus, mais pente
de l'EMA 50 tout juste négative : « MOVING AVG, 12 voyants orange, 69 %, MIXED ». La
situation baissière symétrique donne exactement la même rangée. L'en-tête dit
« empty = neutral ».

Simulation : barre orange de 4 voyants ou plus sur 21 % des bougies pour MOVING AVG, 33 %
pour MACD (mes chiffres ; la relecture trouve 22 % et 32 %), 22 % pour ICHIMOKU et 7,5 % pour
ADX (relecture seule). Maximum : 12 voyants pour MOVING AVG, 13 pour ICHIMOKU, 8 pour MACD et
ADX.

### D5. Ligne d'activité en direct : elle lit « LOW » pendant la première moitié de presque toutes les bougies (l. 302-306, l. 471-472)

En mode LIVE avec « Use the live candle » coché (les deux par défaut), le volume **en cours**
de la bougie est classé parmi 100 bougies **terminées**. Une partie de bougie est comparée à
des bougies entières. La lecture démarre à 0 % à chaque ouverture et monte jusqu'à la
clôture. Les briques sont aussi les plus pâles à chaque ouverture (l. 450).

Simulation (volume arrivant régulièrement, mes chiffres et ceux de la relecture sont
identiques) :

| Avancement de la bougie | Rang affiché | Bougies lues « LOW » |
|---|---|---|
| 30 % | 4 | 97 % |
| 50 % | 16 | 81 % |
| 70 % | 31 | 58 % |
| 90 % | 44 | 38 % |
| clôture | 50 | 31 % |

Le « × avg » a le même biais : 0,5 à mi-bougie pour une bougie exactement normale. Le défaut
disparaît avec « Confirmed bars only » ou en décochant « Use the live candle ».

### D6. Bloc VOLUME « SELL x % / BUY y % » : ce n'est pas du volume acheteur ou vendeur (l. 274-296, l. 462-468)

- **Graphique 1 minute ou moins (ton usage)** : le graphique n'est pas au-dessus de l'unité
  intrabarre (1 minute par défaut). Le code passe par le repli des l. 290-295. Avec la fenêtre
  par défaut d'une bougie, le volume s'élimine du calcul : BUY % = 100 × (clôture − bas) /
  (haut − bas). C'est la position du prix dans la bougie, rien d'autre. Le même résultat sort
  avec 50 fois plus de volume. Le panneau écrit pourtant « VOLUME », « SELL », « BUY ». Seule
  l'infobulle d'un réglage le dit (l. 88-89).
- **Graphique au-dessus de 1 minute** : c'est le volume des bougies 1 minute qui ont clôturé
  en hausse contre celui de celles qui ont clôturé en baisse. Toute une minute va d'un seul
  côté, même si elle clôture un tick au-dessus de son ouverture. C'est une approximation
  connue, pas du volume à l'initiative des acheteurs.
- **En direct, première minute de chaque bougie** : le tableau ne contient qu'une seule
  minute, donc la lecture vaut 0, 50 ou 100 % et bascule d'un côté à l'autre.

### D7. Voyants d'unités inférieures au graphique, mode LIVE : la dernière sous-bougie n'est jamais lue (l. 235)

Ne concerne pas un graphique 1 minute : là, les sept voyants passent par `request.security`.

Sur un graphique plus haut, les voyants plus bas passent par `request.security_lower_tf` et
le code lit l'avant-dernier élément du tableau (`k − 2`). C'est juste pendant qu'une bougie
se forme. Mais à la clôture et en historique, le dernier élément est terminé et il n'est
jamais lu. Graphique 30 minutes : le voyant « 15m » ne montre jamais la deuxième bougie 15
minutes de chaque bougie, et pendant le premier quart d'heure il montre une bougie clôturée
15 à 30 minutes plus tôt. Le commentaire l. 224 promet « the last completed intrabar ».

Part des sous-bougies jamais affichées : 20 % (graphique 5m, voyant 1m), 33 % (15m / 5m),
50 % (30m / 15m), 60 % (5m / 3m). Effet sur la rangée TIMEFRAMES (sorties brutes de la
relecture temps réel, pas encore contre-vérifiées) : au moins un voyant de la mauvaise
couleur 4 à 11 % du temps, verdict du consensus faux 1 à 2 % du temps.

Cas particulier : le voyant 3 minutes sur un graphique 5 minutes. 3 ne divise pas 5. La
lecture est irrégulière, et en mode « Confirmed bars only » elle peut utiliser une bougie 3
minutes pas encore terminée. Le manuel ne dit pas comment TradingView range ces
sous-bougies.

### D8. Alertes : la bonne fréquence dépend du mode, et l'en-tête n'en donne qu'une (l. 16-17, l. 323-326)

L'en-tête conseille « Once per bar close » en mode LIVE. C'est juste pour les alertes
« Indicators agree » en LIVE : une alerte par changement, aucun retard. Mais :

- **Alertes « TF consensus » sur un graphique 1 minute** : les sept voyants sont des bougies
  précédentes terminées. Le consensus change au premier tick de la bougie. Avec « Once per bar
  close » l'alerte part à la clôture de cette bougie : **une bougie entière après le
  panneau**, dans 100 % des cas. « Once per bar » sonne au premier tick et l'état ne peut plus
  changer dans la bougie.
- **Mode « Confirmed bars only »** : tout est décalé d'une bougie dans le code (`cv[1]`).
  Avec « Once per bar close », toutes les alertes partent exactement une bougie après la
  clôture qui a créé l'état (1 minute en 1m, 5 minutes en 5m). Il faut « Once per bar ».
- **Unité d'indicateur supérieure au graphique** : même mécanisme, même retard d'une bougie
  du graphique avec « Once per bar close ».
- **LIVE avec « Once per bar »** sur les alertes « Indicators agree » : 22 à 30 % des alertes
  portent sur un état disparu à la clôture.
- Les messages ne donnent pas l'unité de temps (`{{interval}}`), contrairement à tes autres
  scripts LOLO 2.

### D9. Les cinq jauges sont calculées deux fois (l. 195-196)

Avec « Indicator timeframe » vide (défaut), la l. 194 calcule les jauges sur le graphique.
La l. 195 les recalcule dans une requête sur la même unité, et ses 12 résultats ne sont
jamais lus (l. 198-199, l. 213-214). Cela fait 14 appels `ta.*` et une requête de trop à
chaque bougie et à chaque tick : 28 % de tous les calculs `ta.*` sur un graphique 5 minutes,
38 % sur un graphique 1 minute. Rien de visible à l'écran, seulement de la charge.

### D10. Pente : « 100 % » se lit aussi sur du bruit, et la zone plate est étroite (l. 29-34, l. 185)

- Les préréglages (9,5 à 11,5 ATR) sont à peu près le 95e centile d'une marche aléatoire
  sans tendance : 9,3 à 13,4 ATR selon la finesse des bougies simulées, 10,6 à 10,8 dans mon
  émulation. Avec 11,5, un marché sans tendance affiche 100 % sur 2 à 5 % des bougies. Ce
  n'est pas une erreur : « top 5 % » est tenu. Mais 100 % ne prouve pas une tendance.
- Avec « Flat below 15 % », un marché sans tendance est **hors** de la zone plate 73 à 76 %
  du temps. Le badge de pente dit donc « BULLISH » ou « BEARISH » les trois quarts du temps
  sur du bruit.
- La pente divise un mouvement de 50 bougies par un ATR de 14 bougies. Quand la volatilité
  change dans la journée, la lecture change sans que le marché change. Modèle de journée
  (pas des données NQ), graphique 5 minutes : 100 % sur 0,02 % des bougies juste après
  l'ouverture de New York, sur 18,5 % en soirée.
- « Calibrated on real data » (l. 15, l. 29-30) : invérifiable ici. Rien ne le contredit.

### D11. Bougies grises et blanches : une seule couleur, qu'elles montent ou qu'elles baissent (l. 313-320)

C'est voulu et annoncé (l. 14). Conséquence : une bougie blanche qui perd 40 points ressemble
à une bougie blanche qui en gagne 40. Modèle de journée, graphique 5 minutes : presque
toutes les bougies de la première heure de la séance de New York sont blanches, parce que le
volume y dépasse tout ce qui précède dans les 100 dernières bougies. « Plus active que 90 %
des bougies récentes » veut alors surtout dire « il est 15 h 30 à Paris ». Sur une journée,
23 à 34 % des bougies sont d'une seule couleur.

À voir à l'écran : le manuel ne dit pas si `barcolor` repeint aussi les mèches et les
bordures.

### D12. Contraste : texte blanc sur le vert vif (l. 333, l. 346)

Thème sombre, lecture haussière : le bandeau, les badges et les libellés des voyants verts
sont en blanc sur `#00E676`. Contraste calculé : 1,67 pour 1. Le minimum courant pour du
petit texte est 4,5 pour 1. Rendu non observé ici.

## 3. Défauts hors réglages par défaut ou hors usage courant

- **Seuils bas : le côté haussier gagne par ordre de test** (l. 219, l. 265). Avec
  « Timeframes needed » à 3 : trois voyants verts, quatre rouges, le verdict est « BULLISH »
  et l'alerte haussière part. Simulation : « BULLISH » avec une majorité baissière sur 6 à 7 %
  des bougies. Aucun cas avec les valeurs par défaut (4 sur 5 et 5 sur 7).
- **« Regression length » change le sens de 100 %** (l. 80, l. 185). Les préréglages ne
  valent que pour 50. Avec 200 : 100 % sur 27 à 30 % des bougies d'un marché sans tendance.
  Avec 10 : jamais 100 %.
- **Étiquette d'unité fausse** (l. 141-144) : graphique en secondes « 0m » ou « 1m » au lieu
  de 30S ; 90 minutes « 2H » ; mensuel « 4W ». Juste pour 1m à 4H, jour et semaine.
- **Graphique en ticks (ta mise en page 10T)** : quatre décisions du code reposent sur
  `timeframe.in_seconds("10T")`, que le manuel ne définit pas. Selon la valeur renvoyée, le
  script peut s'arrêter sur une erreur. Dans tous les cas l'en-tête ne peut pas afficher
  « 10T ». À ne pas utiliser sur le 10 ticks sans test.
- **Détection de l'actif** (l. 124-132) : tous les contrats à terme et CFD sont classés
  « INDICES » (or GC1!, pétrole CL1!, bitcoin BTC1!). Juste pour NQ1! et un CFD NAS100.
- **16 réglages numériques sans minimum** (l. 41 à 66). « Displacement » à 0 lit `[−1]` :
  erreur d'exécution. Une longueur à 0 aussi.
- **« Volume source » forcé sur Volume pour un symbole sans volume** (l. 268-271, l. 302) :
  toutes les bougies blanches et « 100 % activity · HIGH ». Sans effet sur le NQ.
- **« Indicator timeframe » déplace aussi la pente, les bougies grises et le pied de
  panneau**, ce que l'infobulle ne dit pas (l. 39-40, l. 211-214).
- **Graphique dont l'unité n'est pas un diviseur des voyants** (2m, 3m, 10m, 45m) : en mode
  « Confirmed bars only », certains voyants supérieurs changent encore en cours de bougie.

## 4. Petits points

- **Flèche vers le haut sur les égalités** (l. 431, l. 444) : « 2/5 ▲ MIXED » pour deux
  haussiers et deux baissiers. Environ 6 % des bougies simulées.
- **MACD : saut d'une demi-barre au passage du zéro** (l. 162). Un MACD directionnel ne peut
  pas afficher moins de 50 %.
- **Rangée ADX** (l. 158, l. 408) : le nombre affiché est l'ADX, la barre est une autre
  grandeur (ADX × écart des DI). « ADX 32, UPTREND » avec un seul voyant est possible.
- **Arrondis** (l. 385, l. 408) : ADX 19,6 s'affiche « ADX 20 · NO TREND ».
- **Égalité Span A = Span B comptée baissière** (l. 180) : 0,3 à 0,7 % des bougies.
- **`ta.percentrank` compte « inférieur ou égal »** (l. 302) : une bougie sans volume après
  100 bougies sans volume vaut 100 %. Négligeable sur le NQ en minutes. Visible avec de très
  petits volumes entiers (graphiques en secondes).
- **Avertissement de compilation certain** l. 268 : `ta.cum` dans le second terme d'un `and`,
  que la v6 n'évalue pas toujours. La valeur reste juste.
- **Colonne 9 du tableau** : deux largeurs demandées (l. 357 et l. 461). L'une des deux est
  ignorée.
- **Libellés des voyants plus larges que les voyants** sur une fenêtre étroite (l. 350,
  l. 388). Rendu non observable ici.
- **Code mort** : `COL_*` (l. 23-27), `stCol` (l. 137), `iScore` (l. 220), `nTf` et
  `consScore` (l. 261, l. 264).

## 5. Charge

Réglages par défaut :

| | Graphique 1 minute | Graphique 5 minutes |
|---|---|---|
| Requêtes par bougie | 8 | 9, dont 3 en unité inférieure |
| Appels `ta.*` par bougie, graphique | 20 | 20 |
| Appels `ta.*` dans les requêtes | 17 | 30 |
| Appels de tableau par tick | 288 | 288 |

- Le tableau est vidé puis reconstruit à chaque tick : 268 cellules, 18 fusions. C'est
  nécessaire pour les cellules qui changent, pas pour les 56 qui ne changent jamais.
- Le doublon D9 est la seule part purement inutile. Il se retire en quelques lignes.
- Sur un graphique au-dessus de 1 minute, le découpage du volume demande tout l'historique
  1 minute (jusqu'à 100 000 barres) alors que le panneau n'affiche que la dernière bougie.
- Comparaison : ta jauge L2 (`LOLO2_jauge_consensus_v0.2.pine`) fait ses cinq lectures sans
  aucune requête.

## 6. Ce que le panneau dit vraiment

- Les cinq jauges sont cinq suiveurs de tendance calculés sur le même prix. Dans mon
  émulation leurs états sont corrélés à 0,6 en moyenne (0,4 à 0,7 selon la paire). « 4 sur 5
  d'accord » n'est donc pas quatre confirmations indépendantes.
- Sur une marche aléatoire sans dérive : bandeau « BULLISH BIAS » ou « BEARISH BIAS » sur
  50 % des bougies ; consensus des unités « BULLISH » ou « BEARISH » sur 61 % (relecture) ;
  chaque jauge directionnelle 60 à 70 % du temps, Supertrend 100 %.
- Le panneau décrit ce que le prix vient de faire. L'en-tête le dit honnêtement :
  « directional confirmation only, no trade signals ».
- Recouvrement avec ce que tu as déjà : DMI / ADX et Supertrend ont les mêmes réglages que
  dans ta jauge L2. Ce que le cockpit ajoute : EMA 50 / 200, MACD, Ichimoku, pente, sept
  unités de temps, volume, coloration des bougies.

## 7. Ton usage : 1 minute ou moins

- **Voyants** : aucun retard, les sept passent par la bougie précédente terminée.
- **Bloc SELL / BUY** : position de la clôture dans la bougie, pas du volume (D6).
- **Activité en direct** : biaisée vers « LOW » (D5).
- **Alertes « TF consensus »** : une bougie de retard avec « Once per bar close » (D8).
- **Graphique en secondes** : étiquette d'en-tête fausse (« 0m » ou « 1m »).
- **Mise en page 10 ticks** : comportement inconnu, à tester avant tout usage.

## 8. À vérifier sur TradingView

1. Compilation, et le texte exact des avertissements.
2. Prix au-dessus du nuage avec Tenkan sous Kijun : le panneau écrit-il « IN CLOUD » ?
3. Bougie de retournement du Supertrend : la barre est-elle pleine ?
4. Ouverture d'une bougie : la ligne d'activité repart-elle vers 0 % et « LOW » ?
5. Graphique 1 minute : le bloc SELL / BUY suit-il seulement la position du prix dans la
   bougie ?
6. Bougies blanches et grises : mèches et bordures repeintes ou non.
7. Largeur des libellés dans les voyants et hauteur de la première rangée de briques.

## 9. Corrections possibles, de la plus petite à la plus grande

Aucune n'est compilée. Le fichier collé n'est pas modifié. Une version corrigée serait un
fichier à part, sur demande.

| Défaut | Correction | Taille |
|---|---|---|
| D1 | l. 417 : « IN CLOUD » devient « MIXED » | 1 mot |
| D3 | l. 478 : « TRENDING » devient « NOT RANGING » | 1 mot |
| D5 | l. 90 : valeur par défaut `false` | 1 mot |
| D7 | l. 235 : `j = confOnly or barstate.isconfirmed ? k - 1 : k - 2` | 1 ligne |
| D9 | l. 195-196 : requête placée dans `if useHtfInd` | 5 lignes |
| D4 | l. 374 : flèche ▲ ou ▼ ajoutée au texte quand l'état est neutre | 2 lignes |
| D6 | l. 462-468 : « DOWN / UP » et « close position » quand le repli est actif | 4 lignes |
| D8 | sans toucher au code : « Once per bar » en mode confirmé et pour le consensus en 1 minute | réglage |
| Seuils bas | l. 219, l. 265 : exiger aussi la majorité | 2 lignes |
| Réglages | `minval = 1` sur 16 réglages | 16 mots |
| D2 | l. 165-167 : mesurer l'avancée de la ligne depuis le retournement | changement de formule |
| D10 | l. 185 : diviser par la plage moyenne sur la fenêtre de régression | changement de formule |

Les deux dernières changent ce que la jauge mesure. Elles sont à décider, pas à appliquer
d'office.
