# BSP v11.66 contre BSP TRAIL2 tri8 — lequel pour Lolo 1 en trading réel (08/11)

Fichiers comparés, sans modification : `src/BSP_v11.66.pine` (référence vérifiée) et
`src/test/BSP_trail2_tri8.pine` (la version que Lolo fait tourner). Pine non compilé ici.
Quatre relectures (classement des 51 zones de code qui diffèrent, preuve d'identité du
moteur et du maillon jamais vérifié, dépendances à TradingView, forte volatilité et
charge), un juge, trois contre-relectures : aucune réfutée.

## Verdict

**v11.66 pour le trading réel sur Lolo 1, rafales comprises. TRAIL2 reste une copie de
test, hors du graphique de trading.** Son propre en-tête le dit : « pas pour le trading
reel » (l. 19), « signaux reels non mesures » (l. 12), « Ne pas remplacer le BSP de
production avant validation TradingView A/B » (l. 34).

| Priorité | v11.66 | TRAIL2 | Gagnant |
|---|---|---|---|
| Fiabilité des calculs et des signaux | référence vérifiée ; recherches écrites à la main ; couleurs du bord réappliquées à chaque tick ; `runtime.error` seulement sur les trois gardes du graphique | mêmes valeurs du moteur ; ajoute deux comportements de TradingView jamais vérifiés, une butée de capacité à marge nulle, le piège du réglage 28 | v11.66 |
| Fidélité aux ticks 1T | dernier tick vrai sur 68,66 % des bougies (modèle, 0 % de premiers ticks perdus) ; 67,07 % à 5 % | 68,69 % ; 67,28 % à 5 % ; jamais un tick plus ancien ni en avance ; bandes grises, milliseconde partagée et zone neutre identiques | égalité en pratique |
| Charge minimale | 15 séries ; traîne à 16 porteurs ; réserve de 6 000 à 9 000 éléments ; 11 tracés | 22 séries (+47 %) ; deux balayages de plus par tick ; 3,3 à 8 fois plus d'appels au versement ; anneau permanent de 15 000 places ; 31 tracés dont 20 sondes masquées | v11.66 côté serveur ; navigateur égal ou inconnu |
| Aucun changement inutile | la référence | 3 lignes du moteur réécrites (mêmes résultats), chiffre opposé noir à 50 %, réglage 28 remplacé, 4 cases de test, 20 sondes | v11.66 |

## Les différences importantes

1. **Le moteur calcule exactement les mêmes nombres.** Trois lignes réécrites depuis le
   test3 (référence en cache, compteur saturé, préchauffage court-circuité) : identité
   prouvée, et 2 064 982 exécutions modélisées sans un bit d'écart (les mutants exprès
   sont tous détectés). `estimateStep`, `nextSignalState`, `movingAverage` et les
   constantes sont identiques au caractère près. Les différences portent sur le tick
   choisi et montré, pas sur la formule.
2. **TRAIL2 montre parfois un tick un peu plus récent de la même bougie** : 0,73 à 0,88 %
   des bougies, 0,04 point de BP en médiane, couleur différente sur 2 à 6 bougies sur
   800 000. À l'écran, les deux courbes sont pratiquement identiques.
3. **Les bandes grises des rafales sont les mêmes** (au plus 4 bougies d'écart sur
   340 000 grises, 0 bande de différence) : TradingView ne livre aucun tick 1T pendant 27
   à 164 bougies, aucune version ne peut les combler.
4. **Recherches natives** : TRAIL2 utilise `array.binary_search_leftmost/rightmost` sur
   des heures qui se répètent (milliseconde partagée). Les exemples du manuel disent
   « première/dernière occurrence », le paragraphe « Remarks » des mêmes pages décrit
   une recherche qui s'arrête au premier égal. Jamais testé sur TradingView. Si les
   « Remarks » ont raison : 0,13 à 0,17 % des bougies closes en direct et 0,23 à 0,69 %
   des valeurs du bord montreraient un tick plus ancien, à 90-96 % pendant les rafales,
   et 2 à 2,6 % des bougies après rechargement. La v11.66 n'utilise pas ces fonctions.
5. **Mémoire de couleur du bord vivant** : TRAIL2 saute la réapplication des couleurs
   qui semblent inchangées. Juste seulement si TradingView renvoie au navigateur la
   couleur remise en arrière ; non documenté. Sinon, une couleur périmée peut rester sur
   le bord sans erreur. La v11.66 réapplique les cinq couleurs à chaque tick. (Modèle :
   0 moment périmé, la situation exige un changement d'état et un retour dans la même
   bougie.)
6. **Charge serveur plus lourde** dans TRAIL2 (voir le tableau). La saccade de 15:30
   était une saturation du navigateur : aucune des deux versions ne la règle.
7. **Butée d'arrêt** : la réserve de 15 000 places de TRAIL2 a deux `runtime.error`
   (l. 2133, 2142), prouvés inatteignables, avec une marge nulle (14 999 au pire).
8. **Chiffre opposé sur l'échelle** : noir à 50 % dans TRAIL2 (réglage 22 réactivé au
   test3, ton choix du 23/10), gris Neutre dans la v11.66, qui ne lit pas ce réglage.
9. **Réglage 28** : « Reprises strictes » (décochée) dans la v11.66, la case TRAIL2
   (cochée) dans TRAIL2. Coller la v11.66 par-dessus le script TRAIL2 pourrait cocher
   « Reprises strictes » : courbe grise tout de suite et coupée après dix bougies sans
   tick, précisément en rafale.
10. **Le maillon jamais vérifié (v11.66 → opt)** est maintenant prouvé identique :
    800 000 cas aléatoires et 5,1 millions de cas exhaustifs, 0 écart.

Constat annexe, sans effet sur le verdict : le manuel (`concepts/time.md` l. 355-357)
dit que `time_close[1]` d'une bougie en direct écoulée est valide à la bougie suivante
sur un graphique en ticks ; l'en-tête de la v11.66 le déduit na du Diag 47, mesuré à
l'exécution confirmée. Les deux chemins sont codés dans les deux versions : aucune valeur
fausse dans un cas comme dans l'autre.

## Ce que seul TradingView peut trancher

- les recherches natives sur valeurs répétées : `src/test/sonde_recherche_native.pine`
  (valeurs décisives l20/r20 = 1/3 et la série de 7 = 1/10 ; un écart sur les voisins
  absents ne concerne pas TRAIL2) ;
- ce que reçoit le navigateur pour un dessin non touché après remise en arrière (la
  vérification 3 de `sonde_test4.pine` ne suffit pas : son étiquette est réécrite à
  chaque tick) ;
- l'écart de charge réel : Profiler et CSV Lolo Control, même séance ;
- comment TradingView rattache les réglages enregistrés quand on remplace le code.

## Remettre la v11.66 sans toucher à TRAIL2

1. Ne pas coller la v11.66 dans le script TRAIL2, et ne pas « Réinitialiser les
   paramètres » de TRAIL2.
2. Dans l'éditeur Pine : nouvel indicateur, y coller tout `src/BSP_v11.66.pine`,
   l'enregistrer sous un nouveau nom, « Ajouter au graphique », hors rafale (chargement de
   l'historique 1T).
3. Recopier à la main les réglages 1 à 27 depuis l'onglet Entrées de TRAIL2 (mêmes
   positions, mêmes noms). Le 22 (couleur du chiffre opposé) n'est pas lu par la v11.66.
4. Vérifier que le 28, « Reprises strictes », est décoché.
5. Ne pas laisser les deux sur Lolo 1 : deux requêtes 1T, deux bords. Retirer TRAIL2 du
   graphique ne supprime pas le script enregistré.

Différences visibles après le retour : le nom dans la légende, le chiffre opposé gris au
lieu de noir, plus de section « 6 — Tests 22h », plus de codes Diag 55 = 9 et 58 = −9.
Courbes, remplissage, couleurs et bandes grises : identiques presque partout.

Scripts et résultats : `scratchpad/compare/work/` (classify, formula, platform,
burst-load, refute).
