# SR Boxes + v2.7 LIGHT : allègement de la v2.6 RANGE (20/11)

Fichier livré : `src/sr/SR_Boxes_v2.7_LIGHT.pine` (Pine v5, 509 lignes). **Non compilé ici**,
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
