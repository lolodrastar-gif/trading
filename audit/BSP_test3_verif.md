# BSP test3 — vérification (24/10)

Fichier : `src/test/BSP_test3.pine` (commit 3d8d2e3). Reconstruit à partir de la
v11.66-opt2 vérifiée (`audit/BSP_v11.66_opt2_verif.md`) et des seize zones de code
que le fichier collé le 24/10 modifie, recopiées telles quelles ; les ~1 400 lignes
de commentaires d'historique de son en-tête ne sont pas recopiées. 32 réglages,
comme annoncé. Pine non compilé ici.

## Ce qui change par rapport à l'opt2

| | Changement | Identique en sorties ? | Atteint le navigateur ? |
|---|---|---|---|
| a | Quatre cases de test (groupe « 6 — Tests 22h »), dont **« calculer » et « dessiner le bord vivant » décochées par défaut** | **Non : changement visible** | **Oui, le seul** |
| b | Chiffre d'échelle du camp opposé en noir à 50 % (`axisMinorColor` réactivé) | Non : changement visible voulu | Couleur seulement, même volume |
| c | `firstIndexAtOrAfter` / `lastIndexAtOrBefore` : recherches natives `array.binary_search_leftmost/rightmost` | Très probablement, non vérifié de première main | Non |
| d | Réserve : saut en bloc d'une queue certifiée déjà livrée (`poolDeliveredFrom`) | Oui | Non |
| e | Moteur 1T : référence en cache, compteur saturé, préchauffage court-circuité | Oui, par preuve | Non |
| f | Ligne `lastEdgeShownTime` rétablie en fin de script | Oui (corrige le §3b de l'opt2) | Non |
| — | Titre « essai moteur local », nom court « BSP test3 » | Nom seulement | Légende |

## a. Bord vivant éteint par défaut

Avec les deux cases décochées, ni le calcul ni le dessin du bord n'ont lieu :

- plus de segment, de remplissage ni de point sur la bougie en formation ;
- les courbes s'arrêtent à la dernière bougie close (décalage −1) ;
- les deux chiffres de l'échelle suivent la dernière bougie close, pas le tick en cours ;
- marché calme : volet et chiffres figés pendant toute la vie de la bougie, parfois des
  dizaines de secondes ; en rafale, une bougie dure ~10 ms, l'écart ne se voit pas ;
- « Afficher les diagnostics » coché : le bord est recalculé sur toutes les bougies
  (aucune économie serveur) et le Diag 55 reste à −1.

C'est le seul changement qui retire du travail au navigateur (5 à 9 mises à jour
d'objets de dessin par tick en moins), donc le seul qui puisse déplacer une mesure
Lolo Guard. Le choix de l'utilisateur n'est consigné que dans l'en-tête écrit par
l'autre assistant. Commentaire périmé : « tous cochés par défaut — rendu identique »
au-dessus des quatre cases. En-tête inexact : « seuls changements de code : les deux
défauts » (b à f changent aussi du code).

## b. Chiffre du camp opposé

Camp acheteur actif : chiffre BP vert, chiffre SP noir 50 % (gris neutre jusqu'ici) ;
l'inverse côté vendeur ; neutre inchangé. Courbes et remplissage intacts. Mise à jour
d'un script existant : la valeur enregistrée de ce réglage peut persister (#8A8A9A) ;
vérifier la couleur dans les réglages, onglet Entrées, section 5.

## c. Recherches natives

Dépendance : `binary_search_leftmost` doit rendre la PREMIÈRE occurrence d'une valeur
répétée (et, valeur absente, le dernier élément plus petit), `binary_search_rightmost`
la DERNIÈRE (et le premier élément plus grand). Les tableaux d'heures contiennent des
doublons à chaque milliseconde partagée (≈ 22 % des frontières) et en rafale.

- Pour : description actuelle de la référence v6 (première/dernière occurrence, voisins
  explicités), exemples « repetitive elements » ([4,5,5,5] → 1 et 3), renvoi depuis
  `array.binary_search`, mesures publiées par une réimplémentation tierce
  ([10,20,20,20,30,40] : leftmost 15/20/25 → 0/1/3, rightmost → 1/3/4).
- Contre : tradingview.com inaccessible d'ici (miroirs GitHub seulement) ; le paragraphe
  « Remarks » de ces deux entrées décrit littéralement une recherche qui s'arrête au
  premier égal trouvé.
- Si la sémantique était fausse : la valeur tracée et les couleurs changeraient sur
  ≈ 22 % des bougies d'historique (lecture du tick de N à une milliseconde partagée) et
  certaines bougies en direct.
- Gain : 3 à 4 itérations de boucle par appel atteint, 0 à 1 appel par exécution en
  direct (les sorties directes de l'opt2 couvrent le cas courant).

Recommandation : revenir aux boucles de l'opt2 (risque sans gain), ou passer la sonde
`src/test/sonde_recherche_native.pine` une minute sur TradingView : « OK » ferme la
question.

## d. Réserve certifiée

Invariant : de `poolDeliveredFrom` au dernier numéro, la réserve contient tous les
numéros, chacun livré (`trail = 0`) ; tout élément de cette plage aurait été ignoré
par `poolHasSerialFast`. Modèle différentiel : 1,57 M versements, réserve comparée
après chaque bougie, 0 écart ; les mutants (sans le plancher de purge, sans le test
« numéro suivant », sans la remise à zéro sur un prédécesseur ajouté en fin) sont tous
détectés. Gain : environ la moitié des lectures de tableau du versement au
chargement de l'historique ; minime en direct (une fois par bougie).

## e. Moteur

Même quotient sur les mêmes opérandes (la référence ne change que sur un tick avec
amplitude), compteur entier saturé équivalent à `math.min` (`warmupTarget ≥ 4`),
`warmupTarget / warmupTarget × 100 = 100.0` exactement. Modèle : ≈ 2,9 M exécutions
avec retour en arrière, 0 écart. Gain : une division par tick 1T. Le moteur n'est plus
identique octet pour octet à celui du jumeau « BSP Diag » : y reporter les trois
lignes, ou les retirer.

## Compilation

Aucune erreur trouvée : tuples rendus par `poolInsert` et `poolAbsorb` (dont un tuple
contenant un `array<Tick>`), déconstruits dans un `while` ; `var` dans une fonction
évaluée par `request.security_lower_tf` ; signatures des recherches natives (cas vides
et hors bornes exclus avant l'appel) ; `display.none` sur `fill`. Sans précédent dans
le code : le tuple contenant un tableau et la déconstruction dans la boucle. Seul
l'éditeur TradingView confirme.

## Verdict

- Lag : seul (a) peut agir, et il change l'affichage. Le reste tourne côté serveur.
- Sorties : identiques à l'opt2 hors (a) et (b), sous réserve de (c).
- À faire avant installation : sonde (c) ou retour aux boucles ; vérifier la couleur
  du chiffre opposé ; diagnostics décochés.
- Pour savoir si (a) règle la pause : CSV Lolo Guard de séances comparables, bord
  allumé puis éteint.
