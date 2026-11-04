# BSP v4.3 « contrôle tri itérateur » (BSP_ITER) — vérification, et le gris de la capture (03/11)

Fichier : `src/test/BSP_v43_iter.pine` (commit ec4d1aa), reconstruit à partir de la
v4.3 d'audit (`audit/BSP_v43_audit_verif.md`) et des trois zones que le fichier collé
modifie ; l'en-tête d'historique n'est pas recopié. Pine non compilé ici.

## 1. Ce que change l'itérateur

| Zone | Changement | Effet sur les sorties |
|---|---|---|
| en-tête | deux lignes de commentaire | aucun |
| `indicator()` | titre « BSP v4.3 — controle tri iterateur (ESSAI) », nom court « BSP_ITER » | nom seulement |
| `isSorted` (l. 479-499) | la boucle « tri8 » est remplacée par `for [rank, currentTime] in times`, avec `break` dès qu'un contrôle échoue et `break` au rang `size - 1` | aucun : même booléen |

Le manuel v6 documente cette forme (`language/loops.md`, « second form », et `break`
qui sort de la boucle sans réévaluer l'en-tête). Le préfixe contrôlé reste
`min(taille, SCAN_MAX = 2000)` : l'arrêt au rang `size - 1` se fait AVANT
l'itération qui lirait au-delà. Les mêmes contrôles sont faits dans le même ordre
(na, heure qui recule, numéro qui ne monte pas, tailles différentes).

Vérifié mécaniquement (`fuzz_issorted_iter.py`, deux graines, 80 000 tableaux de
0 à 2 400 éléments avec trous na, heures qui reculent, numéros qui stagnent, tailles
différentes) : 0 écart entre la boucle de référence et l'itérateur, 0 lecture hors
tableau, et exactement moitié moins d'appels `array.get` (l'heure vient de
l'itérateur, le numéro est encore lu au même rang).

Gain côté serveur : non mesurable ici. Il ne se juge qu'au Profiler, sur la ligne de
`curTimesSorted`, avant et après, même séance. Le fichier reste la copie d'audit v4.3 :
TRAIL64 et V4 actifs, 20 sondes passives, « pas pour le trading réel » selon son propre
en-tête.

## 2. D'où vient le gris

Le rendu ne connaît que trois couleurs. Une bougie close est grise par exactement
quatre chemins, tous présents à l'identique dans la v11.66 installée (la section
« pont des trous » jusqu'au rendu ne diffère entre v11.66 et ITER que par la condition
de l'estimation rendue pure en test4 et par le bloc d'audit inerte de la v4.3) :

1. **Zone neutre** (l. 395-409, `nextSignalState`) : l'écart BP−SP est revenu dans
   ± « Retour au gris » et n'a pas ressorti au-delà de ± « Sortie du gris ». Avec les
   réglages de la capture (1,618 et 3,618 au lieu de 2,618 et 4,236), le gris revient
   dès que BP est entre 49,2 et 50,8 % et ne repart qu'au-delà de 51,8 / 48,2 %. Le
   remplissage est gris. C'est le gris qui ondule serré autour de 50 % sur la capture.
2. **Reprise simple hors fenêtre** (l. 1796-1811, `greyBridge`) : plus de dix bougies
   10T consécutives sans AUCUN tick 1T du moteur. La valeur est reprise (plateau), la
   courbe passe au gris, SANS remplissage (`fillSuppressed`, l. 2173). En rafale,
   TradingView ne livre parfois aucun tick 1T pendant 27 à 164 bougies d'affilée
   (en-tête, info-bulle « Reprises strictes ») : sur un graphique qui défile à une
   bougie par seconde, ce sont des bandes de quelques secondes. Ce sont les bandes
   fines à l'intérieur du rouge à 55 %, là où aucun autre chemin n'est possible : à un
   écart de 10 %, l'état du moteur ne peut pas être 0.
3. **Calcul indéfini** (l. 1746, `undefinedMeasure`) : un tick lu, mais le ratio du
   moteur est na. En « Ratio des moyennes », cela demande `RMA(amplitude, 233)` ≤ 1e-8
   (l. 1095-1103) : le préchauffage, ou des milliers de ticks consécutifs sans
   amplitude. Gris immédiat, remplissage gris.
4. **Reprise invalidée** (l. 1597, `refreshUndefined`) : un candidat de reprise
   rafraîchie plus récent que la valeur tracée, mais au ratio na. Mêmes conditions
   que le chemin 3. Gris immédiat, la mémoire passe au gris.

Le bord vivant suit les mêmes règles (l. 2300-2400).

## 3. Les dernières modifications peuvent-elles créer du gris ?

- **ITER** : non. `isSorted` rend le même booléen (0 écart sur 80 000 cas) ; rien
  d'autre ne change.
- **v4.3 (TRAIL64, V4)** : elles ne font qu'ajouter des candidats de reprise, jamais
  plus anciens que ceux de la v11.66 (`audit/BSP_v43_audit_verif.md`), et seulement
  quand le tableau vivant dépasse 16 ou 2 000 éléments, c'est-à-dire en rafale. Un
  candidat de plus donne en général une reprise RAFRAÎCHIE : couleur du tick, fenêtre
  des dix bougies remise à zéro (l. 1797), donc MOINS de gris de chemin 2. La
  relecture adverse (§ 5) a trouvé trois façons, rares, d'en AJOUTER : un tick plus
  récent dont l'état du moteur est réellement 0 (lecture plus fidèle, impossible dans
  une zone pleine à 55 %), une fenêtre de dix bougies qui se ferme une bougie plus tôt
  dans un cas de milliseconde partagée en direct, et le chemin 4, qui exige un ratio
  na (préchauffage ou 4 000 ticks de suite sans amplitude). Mesuré sur un million de
  bougies de rafale simulées : 3 bougies grises ajoutées, 4 retirées.
- **test4, anneau** : vérifiées identiques (`audit/BSP_test4_verif.md`,
  `audit/BSP_test4_anneau_verif.md`).

Conclusion : le gris de la capture vient des chemins 1 et 2, qui sont dans la
v11.66 installée depuis les v11.63-64, et pour le chemin 2 de la livraison 1T de
TradingView en rafale, pas du code. La relecture indépendante du 03/11 (trois volets,
passe adverse) est résumée au § 5.

## 4. Pour le prouver sur une bougie grise

Cocher « Afficher les diagnostics », survoler une bougie grise, lire la fenêtre de
données (Diag 58 = source du tick affiché, −1 quand aucun tick n'a été lu pour la
bougie ; Diag 61 = âge en millisecondes de la valeur tracée, clôture moins heure du
tick dont elle vient) :

| Lecture | Chemin |
|---|---|
| courbe entre 49,2 et 50,8 %, ou qui ondule autour, remplissage gris | 1 : zone neutre, voulue |
| Diag 58 = −1, Diag 61 qui grandit de bougie en bougie, courbe plate, PAS de remplissage | 2 : reprise simple au-delà de dix bougies sans tick (livraison 1T) |
| Diag 58 = 0, 1, −5 ou −7, courbe grise loin de 50 %, remplissage gris | 3 : calcul indéfini — à me signaler, ce serait une vraie anomalie |
| Diag 58 = −1, Diag 61 petit (quelques ms), courbe plate, remplissage gris | 4 : reprise invalidée — idem, à me signaler |

Comparer aussi la même bougie sur la v11.66 : si elle est grise au même endroit,
ni l'ITER ni la v4.3 n'y sont pour rien.

## 5. Relecture indépendante (03-04/11)

Trois relectures en parallèle, puis une contre-relecture adverse (une seule des six a
pu tourner, la limite d'utilisation ayant coupé les autres ; c'était celle du point
qui comptait).

- **Chemins du gris** : les quatre chemins du § 2 sont confirmés, avec leurs
  signatures (le gris de reprise simple n'a pas de remplissage ; le gris neutre a un
  remplissage plus opaque que les couleurs, 60 contre 70-78 de transparence, ce qui
  le fait ressortir). Détail notable : avec « Colorer les deux courbes ensemble »
  décochée, la courbe du camp opposé est TOUJOURS grise, par construction. La section
  pont-rendu ne diffère de la v11.66 que par la condition de l'estimation (inerte,
  option décochée) et le bloc d'audit inerte. Le sélecteur de reprise rafraîchie
  réécrit en test4 : 200 000 cas, 0 écart avec la v11.66 à 16 porteurs.
- **Modèle des récupérations en rafale** (1,2 million de bougies 10T simulées,
  livraisons en retard de 27 à 164 bougies, blocs de 2 300 ticks, millisecondes
  partagées) : même nombre de bougies grises avec et sans TRAIL64/V4, à quelques
  unités près par 200 000, dans les deux sens. Les bandes grises fines dans une zone
  pleine sont des reprises simples au-delà de dix bougies, identiques dans toutes les
  versions (31 749 sur 84 289 bougies grises du modèle, 355 bandes de 1 à 5 bougies
  et 526 de 6 à 20 à l'intérieur d'une zone colorée, octet pour octet les mêmes). Le
  bord vivant n'utilise que `pickLatest` : TRAIL64 et V4 ne le touchent pas.
- **Contre-relecture** : la relecture avait écrit que TRAIL64/V4 ne pouvaient ajouter
  du gris QUE par un ratio na. Faux : les deux autres mécanismes du § 3 existent, 3
  bougies ajoutées et 4 retirées sur un million, chaque ajout étant une lecture plus
  fidèle. Aucun des trois ne peut produire les bandes de la capture.
- **Itérateur** : syntaxe et portée conformes au manuel (`language/loops.md`), aucune
  comparaison avec na sur un préfixe trié, aucune lecture au-delà du rang `size − 1`,
  valeur de retour inchangée ; deux graines supplémentaires (40 000 cas) et un fuzz à
  trois voies boucle simple / tri8 / itérateur (40 000 cas) : 0 écart. Précision : le
  prédécesseur direct de l'itérateur est la boucle « tri8 » de la v4.3, elle-même
  identique à la boucle simple de l'anneau. Hors des trois zones, le fichier est
  identique à la v4.3.

## 6. Ce qu'on peut faire pour les pics de volatilité

Le chemin 2 est le seul qui « s'adapte mal » : la fenêtre de dix bougies est comptée
en bougies, et en rafale dix bougies durent 0,1 s. Le script contient déjà, depuis la
v11.56, une fenêtre en SECONDES (« Estimation : garder la couleur (secondes) », 3 s
par défaut) — mais seulement pour l'option « Estimer les bougies sans tick », pas
pour les reprises simples (info-bulle l. 317 : « Les reprises simples et rafraîchies
ne sont pas concernées »).

Deux leviers, sans toucher au moteur ni aux valeurs tracées :

- **Sans code** : cocher « Estimer les bougies sans tick ». Une bougie sans tick trace
  alors une estimation depuis son OHLC 10T, colorée pendant dix bougies OU 3 s. C'est
  une estimation, pas une mesure (l'en-tête : « un vrai BSP 1T n'estime pas »).
- **Petit changement de code** (à décider, pas fait) : étendre la fenêtre en secondes
  aux reprises simples — `bridgeWindow` deviendrait « dix bougies OU dernier tick du
  moteur plus jeune que N secondes ». Une bougie sans tick garderait la couleur de la
  dernière mesure pendant la rafale ; la valeur resterait un plateau, aucune valeur
  n'est inventée. Une ligne dans la série, une dans le bord ; à compiler dans
  TradingView.

Ce que ça ne change pas : la saccade de 15:30 du 02/11 (`audit/lolo_control_2026-11-02.md`),
qui est une saturation du navigateur, pas une question de gris.
