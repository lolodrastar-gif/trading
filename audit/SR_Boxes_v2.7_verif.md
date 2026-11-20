# SR Boxes + v2.7 LIGHT : allègement de la v2.6 RANGE (20/11)

Fichier livré : `src/sr/SR_Boxes_v2.7_LIGHT.pine` (Pine v5, 544 lignes). **Non compilé ici**,
aucune mesure TradingView : le gain est à lire dans le Profiler (§ 5).

Référence : la v2.6 RANGE collée le 20/11 (0,7 s au Profiler ; bloc `if runOnBar` 37,2 %,
dont `updateSide` 18,8 % + 16,1 %). Le collage n'est pas enregistré dans le dépôt : sa logique
de niveaux est transcrite dans `audit/SR_Boxes_v2.7_emulation/diff_engine.py` (`upd26`).

## Verdict

- **Mêmes signaux que la v2.6.** Cassures, reconquêtes, rejets, expirations, compteurs et
  états des niveaux : 0 écart sur 5,76 millions de bougies simulées (192 combinaisons de
  réglages), bougie par bougie et dans le même ordre.
- **Moins de travail par bougie**, sur les quatre postes ci-dessous. Ordre de grandeur
  attendu : le bloc `if runOnBar` (37 % du temps) divisé par 2 à 3, soit environ un quart à un
  tiers du temps total en moins. C'est une estimation par comptage, pas une mesure.
- **Aucun bug de calcul trouvé dans la v2.6.** Son filtre par plages est juste, mais peu
  sélectif. Quatre fragilités corrigées (§ 3).
- Réglages identiques (mêmes libellés, même ordre, mêmes défauts) : les valeurs déjà choisies
  sont conservées si le code est collé à la place de la v2.6.

## 1. Pourquoi la v2.6 restait lourde

1. **Le filtre par plages laisse presque tout passer.** La reconquête concerne tous les
   niveaux, cassés ou non. Avec 10 niveaux par côté, la plage « du plus bas au plus haut »
   contient presque toujours la bougie. Simulation (pivots de clôture 5/5, 10 niveaux,
   300 000 bougies) : la v2.6 parcourt les niveaux sur 40 % des bougies de chaque côté.
2. **Même sans parcours, `updateSide` coûte à chaque bougie** : un appel de fonction, une
   douzaine de variables locales, sept lectures de champs, une vingtaine de comparaisons.
   C'est la partie visible sur ta capture (lignes à 0,4 – 1,2 % chacune).
3. **En Pine v5, `and` évalue toujours ses deux côtés.** `tooClose()` et les deux filtres de
   volume étaient donc calculés à chaque bougie, pivot ou non.
4. **Quatre `ta.*` tournaient pour rien à chaque bougie** : trois fenêtres de 25 bougies
   pour un gradient lu seulement à la création d'une boîte, et `ta.cum` pour un bandeau lu
   seulement sur la dernière bougie.

## 2. Ce que fait la v2.7

1. **Seuils exacts au lieu de plages.** Après chaque parcours, le script retient pour chaque
   côté le niveau juste au-dessus et juste au-dessous du bas (ou du haut) de la bougie. Tant
   que la bougie suivante reste entre les deux, aucun niveau n'a été traversé : 7 comparaisons
   par côté, écrites directement dans le corps du script, sans appel de fonction. Même
   simulation : 29 % de bougies avec parcours au lieu de 40 % (21 % au lieu de 36 % sans les
   marqueurs de rejet). Le reste est incompressible avec ces règles : il y a un vrai
   événement sur 17 % des bougies.
2. **Parcours plus court.** Une fonction par côté (`scanSup`, `scanRes`) : plus de choix
   « support ou résistance » à chaque niveau, et les comparaisons servent à la fois à
   l'événement et au seuil. Environ moitié moins d'opérations par niveau (comptage du code).
3. **Rendu sorti du parcours.** Bord droit des boîtes et niveau le plus proche : une petite
   boucle sur la dernière bougie seulement. La dernière bougie ne force plus de parcours.
4. **Création évaluée seulement sur une bougie de pivot** (`if` imbriqués) ; gradient mesuré
   à la création, sur la même fenêtre.
5. **Reconquête d'un niveau non cassé** : le losange est posé, mais la boîte n'est plus
   repeinte avec les couleurs qu'elle a déjà (3 appels de dessin en moins, même rendu).

## 3. Fiabilité : ce qui est corrigé

- **Étiquette de prix du niveau le plus proche** : la v2.6 la créait une fois puis la
  déplaçait. TradingView efface les labels les plus anciens au-delà de 500 ; après 500
  losanges, croix ou « Break », l'étiquette disparaissait sans revenir tant que le niveau le
  plus proche ne changeait pas. Elle est maintenant recréée à chaque clôture.
- **Bord gauche d'une boîte** borné à la première bougie (un « Lookback » plus grand que
  l'historique donnait une position négative).
- **Fenêtre du gradient** limitée à 2500 (au lieu de 5000) pour rester dans le tampon de
  5000 barres avec le pivot maximal. Défaut inchangé : 25.
- **Bandeau « pas de volume »** : tableau créé seulement si le flux n'a aucun volume.

Non modifié, à connaître : la limite de 500 labels de TradingView efface toujours les plus
anciens losanges, croix et labels de cassure ; en mode éco (défaut) rien ne bouge pendant la
bougie en cours.

## 4. Vérification

- `diff2.py` : modèle de la v2.6 (plages) contre transcription ligne à ligne de `scanSup` /
  `scanRes` et des déclencheurs. 192 configurations (pas de cotation, 1 à 50 niveaux, rejets
  oui / non, masquage oui / non, densités de niveaux), 30 000 bougies chacune : 2 343 109
  événements, 0 écart.
- Le banc détecte les erreurs : 7 fautes injectées une à une (`<=` en `<`, seuil décalé,
  expiration oubliée), 7 détectées.
- `realiste.py` : fréquences de parcours avec des niveaux créés par de vrais pivots.
- Contrôle de syntaxe simple (indentation, lignes coupées, parenthèses) : 0 anomalie. Les
  constructions risquées sont celles que la v2.6 utilisait déjà.
- Limites : bougies simulées (marche aléatoire), pas de données de marché ; le gradient
  suppose que `ta.highest` renvoie `na` tant que sa fenêtre n'est pas pleine (sans effet avec
  les réglages par défaut : l'ATR 150 bloque toute création avant).

## 5. À vérifier dans TradingView

1. Compilation (aucun avertissement attendu de plus que la v2.6).
2. v2.6 et v2.7 sur le même graphique, mêmes réglages : boîtes, couleurs, labels et losanges
   identiques. Seule différence visible possible : aucune.
3. Profiler : temps total, et part du bloc `if runOnBar`.
4. Alertes : une alerte garde le script du moment où elle a été créée. Recréer celles de la
   v2.6 sur la v2.7 et supprimer les anciennes.

## 6. Retouche du 20/11 : bord droit des boîtes

Demande : boîtes « décalées », la bougie passe à côté de la boîte. Mesure sur les deux
captures :

- capture de référence : la boîte finit une bougie après la dernière bougie (bord à 918 px,
  dernière bougie centrée à 883 px, pas de 35 px) ;
- capture de la v2.7 : la boîte finit au centre exact de la bougie en cours (teinte de la
  boîte jusqu'à la colonne 532, centre de la bougie 518 – 546). La moitié droite de la bougie
  est hors de la boîte.

Cause : en mode éco le script n'agit qu'à la clôture et posait le bord droit une barre plus
loin. Cette barre devient aussitôt la bougie en formation. La v2.6 faisait la même chose.

Correction (affichage seulement, aucun signal modifié, moteur non touché) :

- à une clôture suivie d'une nouvelle bougie, le bord droit est posé deux barres plus loin :
  la bougie en formation est entièrement dans la boîte, sans calcul pendant sa formation ;
- marché fermé (dernière bougie du graphique) : une barre plus loin, comme la référence ;
- graphique chargé marché fermé puis réouverture : seul cas où le script prolonge les boîtes
  pendant la bougie en cours, jusqu'à sa clôture.

Vérifié par un petit modèle des états de bougie (historique, ticks, clôture, retour arrière
entre deux ticks) : dans les 6 cas (mode éco oui / non × marché ouvert, fermé, réouverture),
la boîte finit toujours une bougie après la bougie affichée. Non observé sur TradingView.

Non modifié : l'étiquette de prix du niveau le plus proche reste posée sur la dernière
bougie clôturée.

Remarque, sans changement de code : sur la capture de la v2.7, la boîte commence 3 bougies
avant la bougie du pivot. C'est l'écart entre les réglages « Lookback » et « Pivot de
confirmation ». Avec deux valeurs égales, la boîte commence sur la bougie du pivot, comme
sur la capture de référence.

## 7. Seconde retouche du 20/11 : une bougie d'avance

Retour après le § 6 : « c'est mieux, mais des fois ça recommence comme avant ».

Cause la plus probable (déduite, non observée sur TradingView) : une nouvelle bougie
s'affiche dès son premier tick, alors que le résultat du script arrive un peu après. Avec le
§ 6, le bord posé à la clôture précédente tombait exactement au centre de la bougie qui
s'ouvre. La boîte s'arrêtait donc au milieu de chaque nouvelle bougie pendant ce retard,
puis se corrigeait. Plus la plateforme est chargée, plus cela dure et se voit. L'indicateur
d'origine a le même défaut (il pose le bord une barre plus loin à chaque tick).

Correction (affichage seulement, moteur et signaux non touchés) : nouveau réglage, déclaré
en dernier pour ne pas décaler les réglages enregistrés, « Marge à droite des boîtes
(bougies) », 2 par défaut. Le bord droit est posé à ce nombre de bougies après la bougie en
cours. Avec 2, la bougie qui s'ouvre est déjà dans la boîte avant toute mise à jour.

Modèle `bord_droit.py` (exécutions du script, retour arrière entre deux ticks, résultat
affiché en retard). Bougies qui s'ouvrent avec la boîte arrêtée avant leur bord droit :

| Version | Résultat en retard de moins d'une bougie | En retard d'une bougie entière |
|---|---|---|
| v2.6 et première v2.7 | toutes, et pendant toute la bougie | toutes |
| Retouche du § 6 | toutes, le temps du retard | toutes |
| Marge 1 | toutes, le temps du retard | toutes |
| Marge 2 (défaut) | aucune (0 sur 29) | toutes |
| Marge 3 | aucune | aucune (0 sur 28) |

Mêmes résultats en mode éco et hors mode éco. Cas vérifiés avec la marge 2 : marché fermé
au chargement puis réouverture, et clôtures non exécutées sur trois bougies : 0 bougie hors
boîte.

À savoir :

- La marge 2 suffit tant que le retard d'affichage reste plus court qu'une bougie : toujours
  le cas en 1 minute et plus. Sur un graphique en secondes ou en ticks, le retard peut
  dépasser une bougie : monter le réglage à 3 ou plus.
- En contrepartie la boîte dépasse la bougie en cours de deux bougies au lieu d'une (une
  seule pendant l'instant qui suit l'ouverture d'une bougie).
- Marché fermé : la boîte finit deux bougies après la dernière.

## 8. v2.8 : bord droit durci et version visible (20/11)

Fichier : `src/sr/SR_Boxes_v2.8.pine` (550 lignes). Le fichier v2.7 reste tel qu'il était au
§ 7. Affichage seulement : moteur, signaux et réglages identiques. **Non compilé ici.**

Retour après le § 7 : « toujours le même problème, ça déconne parfois », avec une capture où
les deux boîtes finissent au centre exact de la dernière bougie (bord à 354 px, bougie
341 – 367), puis une capture « comme ça que je veux » où elles finissent deux bougies après
la dernière.

Constat : la capture en défaut n'est pas reproductible avec le fichier du § 7. La boîte
rouge y est née à la clôture de l'avant-dernière bougie (pivot à 2 bougies, lookback 5) et
ce même passage pose le bord droit au moins deux barres plus loin. Elle correspond en
revanche au fichier du § 6 (bord posé une barre plus loin). Deux explications possibles,
non départagées ici :

1. ce graphique tournait encore avec le code précédent ;
2. TradingView n'annonce pas les états de bougie comme le manuel le décrit (« dernière
   bougie », « temps réel » à la clôture), ce qui faussait la règle du § 6 et du § 7.

Ce que fait la v2.8 :

- **Numéro de version dans le nom** : le graphique affiche « SR+ 2.8 ». Si ce n'est pas ce
  qui est écrit, le graphique ne tourne pas avec ce fichier.
- **Bord droit sans condition d'état** : à chaque clôture il est posé à la marge plus une
  barre ; pendant la bougie, à la marge. Seul `barstate.isconfirmed` est utilisé, comme le
  mode éco lui-même.
- **Rendu sur les dernières bougies quel que soit l'état annoncé** (`islast`,
  `islastconfirmedhistory`, `isrealtime` ou distance à `last_bar_index`).
- **Boîte neuve ou réutilisée** : créée directement à la bonne longueur.

Modèle `bord_droit_v28.py` : 16 façons d'annoncer les états × mode éco oui / non, avec une
boîte créée en direct. Distance entre la bougie affichée et le bord droit, pire cas :

| Version | Résultat à l'heure ou en retard de moins d'une bougie | En retard d'une bougie entière |
|---|---|---|
| § 6 | boîte arrêtée au milieu ou avant, dans les 32 cas | idem |
| § 7, marge 2 | 16 cas sur 32 en défaut (boîtes qui reculent si la clôture n'est pas annoncée « dernière bougie ») | milieu de bougie |
| v2.8, marge 2 | 1 bougie après, dans les 32 cas | milieu de bougie |
| v2.8, marge 3 | 2 bougies après | 1 bougie après |

Avec les états annoncés comme dans le manuel et sans retard : § 6 milieu de bougie à chaque
ouverture ; § 7 et v2.8 une bougie après à l'ouverture, deux ensuite.

À savoir :

- Marché fermé, la boîte finit trois bougies après la dernière (marge 2 plus la barre de la
  clôture).
- Reste hors de portée : un affichage en retard d'une bougie entière ou plus (graphique en
  secondes ou en ticks). Remède : monter la marge.
- Si le défaut revient alors que le graphique affiche bien « SR+ 2.8 » : noter l'unité de
  temps, la valeur de la marge, et si la boîte se corrige seule au bout d'un instant.

## 9. v2.9 : graphiques en ticks (20/11)

Fichier : `src/sr/SR_Boxes_v2.9.pine` (595 lignes). Affichage seulement : moteur, signaux et
réglages identiques. **Non compilé ici.**

Retour après le § 8 : « ça déconne toujours », avec une capture datée, puis « je suis sur
100 tick ».

### Cause

Elle se lit sur l'axe du temps de la capture : les bougies durent 3 à 5 s (18:04:36,
18:04:47, 18:04:54 toutes les deux bougies), alors que les emplacements à droite de la
dernière bougie avancent de 1 s chacun (18:04:56, 18:04:58, 18:05). Sur un graphique en
ticks, TradingView place donc ce qui dépasse la dernière bougie selon l'heure, pas selon le
nombre de bougies.

Conséquence : un bord droit posé « 3 barres après la bougie qui clôture » est en réalité
posé 3 secondes après l'ouverture de cette bougie. Si elle a duré 3 s, le bord tombe sur la
bougie suivante ; si elle a duré plus, il reste derrière. Les trois captures en défaut
(§ 6, § 7, § 8) s'expliquent ainsi avec des bougies de 2 à 3,5 s ; la capture « comme ça que
je veux » correspond à des bougies d'environ 1 s.

**Correction des § 7 et § 8** : le retard d'affichage et l'hypothèse d'un ancien code
n'étaient pas la bonne explication. La marge comptée en bougies ne pouvait pas suffire sur
un graphique en ticks.

Limite : c'est une déduction (axe du temps, trois captures cohérentes), pas un comportement
documenté ni observé ici. Hypothèse du modèle : l'ancre horaire n'est renvoyée à l'écran
que si l'indice du bord change.

### Ce que fait la v2.9

- Graphiques en ticks, en range ou en secondes : le bord droit est posé à « marge »
  emplacements après l'instant présent, et rafraîchi à chaque mise à jour, y compris en
  mode éco (au plus 20 appels de dessin, le moteur ne tourne toujours qu'à la clôture). Il
  avance d'un emplacement par seconde tant que la bougie dure et revient à la marge à
  chaque nouvelle bougie. L'âge de la bougie est mesuré à l'horloge depuis la première
  mise à jour vue (variable `varip`), donc sans dépendre d'un flux en différé.
- Graphiques en minutes et plus : règle du § 8, inchangée.
- Marge à 0 : boîtes prolongées jusqu'au bord droit de l'écran (`extend.right`), sans
  aucune mise à jour.
- Le graphique doit afficher « SR+ 2.9 ».

### Modèle `bord_droit_ticks.py`

Part du temps où la bougie en cours dépasse de la boîte, retard d'affichage 0,3 s :

| Durée moyenne des bougies | v2.8 | v2.9 | Marge moyenne affichée en v2.9 |
|---|---|---|---|
| 0,5 s | 4,5 % | 0,0 % | 2,3 emplacements |
| 1,5 s | 30,2 % | 0,0 % | 3,4 |
| 3,5 s | 63,9 % | 0,0 % | 5,4 |
| 10 s | 94,5 % | 0,0 % | 11,9 |

v2.9, bougies de 3,5 s, selon le retard d'affichage : 0,0 % à 0,3 s ; 0,5 % à 1 s ; 18 % à
2 s (la marge de 2 s est alors consommée : monter la marge à 3 ou 4).

Variante écartée : marge fixe plus la durée des bougies récentes. Même taux, mais boîtes
deux fois plus longues (10,3 emplacements pour des bougies de 3,5 s).

### À savoir

- Sur un graphique en ticks, le rendu « exactement 2 bougies après, en permanence » n'existe
  pas : l'emplacement à droite est une seconde, pas une bougie. La boîte finit 2
  emplacements après la bougie à son ouverture, puis s'allonge tant qu'elle dure.
- Sur un marché lent (bougies de 30 s et plus), la boîte s'allonge d'autant ; plafond à 300
  emplacements.
