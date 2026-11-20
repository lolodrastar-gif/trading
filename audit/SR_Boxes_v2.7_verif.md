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
