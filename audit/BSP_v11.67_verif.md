# BSP v11.67 — la v11.66 vérifiée + les améliorations de sortie de TRAIL2 (08/11)

Fichier : `src/BSP_v11.67.pine` (3 801 lignes). Construit par un script
(`scratchpad/v1167/build_v1167.py`) à partir de la variante perf de la v11.66
(`src/test/BSP_v11.66_perf.pine` = v11.66 + quatre cases « 6 — Tests 22h », rendu
identique) en recopiant le texte de « BSP TRAIL2 — essai tri8 ». Les fichiers d'origine
n'ont pas été touchés. Pine non compilé ici. Quatre relectures indépendantes (compilation
et exécution ; modèle différentiel contre TRAIL2 et contre la v11.66 ; réserve ; coût et
risques), puis quatre contre-relectures adverses : deux trouvailles réfutées, deux
nuancées, aucune erreur.

## 1. Ce qu'elle contient

Base : la v11.66. Moteur `bspEngine1T` identique octet pour octet ; recherches écrites à la
main, réserve linéaire, `isSorted` simple, bord vivant et dessin de la v11.66. Hors des 30
zones modifiées, le code est identique à la v11.66.

Repris de TRAIL2, texte copié (118 lignes sur 152 lignes de code modifiées) :

| Amélioration | Où |
|---|---|
| Chiffre de l'échelle du camp opposé : réglage 22 réactivé, noir à 50 % | réglage 22, couleurs de l'axe |
| TRAIL2 : chaque résultat 1T transporte son deuxième prédécesseur [2] (7 séries de plus, 22 au lieu de 15) ; lu par la lecture différée (source 4, avant V4) et par la reprise rafraîchie ; versé dans la réserve (trail = 1) ; Diag 58 = −9 | enveloppe du moteur, `pickSecondTrail`, sélection, reprise, `poolAbsorb` |
| Réglage 28 « Récupérer aussi le deuxième résultat 1T précédent », coché, à la place de « Reprises strictes » (retirée comme dans TRAIL2 : `strictBridges` constante fausse, son défaut) | réglage 28 |
| TRAIL64 : traîne lue jusqu'au 64e porteur quand le tableau vivant en a plus de 16, sous la garde du rang 17 | `pickTrail` étape 2 |
| V4 : rangs 2 000 à 2 255 du tableau vivant, contrôlés de proche en proche | `pickStrictOverflow` |
| Info-bulle du réglage 9 sans la mention de « Reprises strictes » | réglage 9 |

Les 32 réglages ont exactement les positions, noms, types, défauts, groupes et
info-bulles de TRAIL2 (vérifié mécaniquement) : passer de TRAIL2 à la v11.67 ne déplace
rien. 11 tracés + remplissage + ligne, comme la v11.66.

Différences voulues avec TRAIL2 (34 lignes nouvelles) :
- le bord vivant ne lit pas le [2] (TRAIL2 le lit sans lire le [1]) : deux balayages de
  moins par tick, et le bord reste celui de la v11.66 ;
- `pickSecondTrail` s'arrête dès qu'un [2] valide dépasse la borne haute (exact : les [2]
  valides ont pour numéro porteur − 2, et les heures d'une série 1T ne décroissent pas) ;
- le versement saute le [2] qui est l'élément k − 2 du même tableau (exact : il vient
  d'être traité) ;
- `POOL_MAX` 6 000 → 6 064 : avec trois enregistrements par rang, la règle de marge de la
  v11.66 (« ≥ enregistrements par versement + 64 ») donne 6 064 ; la réserve purge au-delà
  de 9 064 et garde 6 064. Sans cela, un cas construit (2 000 ticks espacés de 3 dans un
  tableau sans tick propre avant sa clôture, réserve ≥ 3 001) faisait perdre à la purge le
  seul tick de N ; TRAIL2 le perd aussi, la v11.66 non. Inatteignable par une livraison
  réelle (maximum observé au modèle : 2 083 enregistrements au-dessus de la borne, marge
  ≥ 3 917), mais la marge est rétablie.

Laissé de côté (sans effet sur les valeurs, ou dépendant de TradingView sans
vérification) : recherches natives, réserve circulaire et certificat de queue, mémoire de
couleur du bord, `isSorted` déroulé, trois lignes du moteur réécrites, raccourcis
opt/opt2, vingt sondes d'audit.

## 2. Vérification

- **Compilation** : aucune erreur ni avertissement prévu. Contrôles statiques : 0
  déclaration en double, 0 usage avant déclaration, 74 appels à la bonne arité, 200
  arguments au bon type et 86 au bon nom, tuples cohérents (22 = 22, 6, 5, 4). Lectures de
  tableau : 0 erreur sur 200 000 cas reconstruits, les quatre gardes retirées une à une
  sont détectées. Les constructions v6 employées existent déjà dans la v11.66 ou TRAIL2.
- **Bougies closes** : identiques à TRAIL2 au bit près (valeur, état, remplissage, gris,
  Diag 58) sur 14 séries × 200 000 bougies de rafale, et 10 × 40 000 adverses. Contre la
  v11.66 : la valeur diffère sur 0,66 à 0,96 % des bougies, toujours vers un tick plus
  récent de la même bougie (0 plus ancien, 0 en avance), 0,04 point en médiane ; couleur,
  gris et remplissage sur 0 à 3 bougies par 200 000. Le vrai dernier tick est gagné sur
  +47 à +71 bougies par 200 000 sans perte de premier tick, +127 à +144 à 1 %, ≈ +430 à
  5 %. Sur 24 à 37 % des bougies changées, la valeur s'éloigne un peu de celle du vrai
  dernier tick tout en venant d'un tick plus récent.
- **Réserve** : identique à TRAIL2 après chaque versement (hachage par bougie + 401
  comparaisons élément par élément par série) ; identique à une référence sans raccourci
  sur 2,6 millions de versements honnêtes ; le raccourci ne diffère que sur des [2]
  fabriqués dont l'heure contredit l'élément de même numéro, ce qu'une série 1T ne produit
  pas. Taille maximale 15 064 + 6 064 à la purge, loin des 100 000 de Pine.
- **Bord vivant** : jamais plus ancien que celui de la v11.66, jamais en avance ; plus
  récent sur 0,35 à 0,57 % des bougies (il lit la réserve, qui contient les [2]). Plus
  ancien que celui de TRAIL2 sur 0,62 à 0,74 % (TRAIL2 lit le [2] de son propre tableau),
  jamais plus récent. Accord bord / bougie close sur la valeur : 90,5-90,7 % contre
  90,8-91,0 % pour la v11.66 (la bougie close récupère des ticks que le bord ne voit pas) ;
  sur l'état, 99,4 % pour les trois.
- **Sortie anticipée de `pickSecondTrail`** : 0 écart sur 300 000 cas cohérents ; elle
  suppose que les heures 1T ne décroissent pas avec le numéro, ce qui est vrai d'une série
  1T. Si cela échouait, le choix retomberait vers celui de la v11.66, jamais plus loin.
- **Reprise rafraîchie** : la structure de la v11.66 (recalcul sur la fenêtre de reprise)
  + [2] est équivalente à la réutilisation du candidat strict de TRAIL2 (300 000 cas, 0
  écart) ; au modèle, le [2] n'y gagne jamais.

## 3. Ce qu'il faut savoir

- **Règle héritée de la v11.66, identique dans TRAIL2** : quand un candidat plus récent a
  un ratio indéfini, la bougie retombe sur sa lecture propre, en gris. Avec les nouvelles
  sources ([2], TRAIL64, V4), ce cas peut tomber sur un tick que la v11.66 n'aurait pas vu.
  Avec tes réglages (RMA 233, « Ratio des moyennes »), il faut environ 4 100 ticks de suite
  sans mouvement de prix : inatteignable en séance, et les valeurs seraient alors égales à
  1e-14 près. En SMA/WMA/HMA, 233 ticks identiques suffisent et la valeur peut différer.
  Rien n'a été changé : c'est la règle de la v11.66.
- **Diag 55 en historique** (diagnostics cochés seulement) : sur ≈ 0,1 % des bougies dans
  un modèle à 5 % de premiers ticks perdus, le bord lit un [2] de la réserve daté de la
  milliseconde de clôture et affiche 4 au lieu de 1. Aucun tracé n'en dépend ; en direct,
  `time_close` est na et le plafond de numéro s'applique.
- **Charge** (comptée, pas mesurée) : par tick au calme, +13 % de lectures par rapport à
  la v11.66 (123 contre 109 ; TRAIL2 102 mais avec ses recherches natives) ; à 64 éléments,
  +10 % (TRAIL2 ×3,1) ; au versement, +32 % de lectures et +26 % d'appels (TRAIL2 ×8
  d'appels) ; au chargement, +47 % de valeurs stockées (22 séries), comme TRAIL2. Dessin
  du bord : 9 appels par tick, comme la v11.66.
- **Réglages 22 et 28 changent de sens à la même position.** Ajouter la v11.67 comme
  NOUVEL indicateur. Si on la colle par-dessus un script v11.66 existant, la valeur
  enregistrée « Reprises strictes = décochée » pourrait éteindre TRAIL2 et le réglage 22
  garder le gris : vérifier la case 28 (cochée) et la couleur 22 (noir 50 %). Depuis
  TRAIL2, les positions et défauts concordent.

## 4. À vérifier dans TradingView

1. Compilation, comme nouvel indicateur, hors rafale.
2. « Afficher les diagnostics » une séance : Diag 58 = −9 sur quelques bougies (le modèle
   attend 0,5 à 0,9 % de bougies différentes de la v11.66).
3. Profiler, même séance, contre la v11.66 : lignes de la requête, de `poolAbsorb` et de
   `pickSecondTrail`.
4. Avant de retirer la v11.66 du graphique : les deux côte à côte un moment, hors rafale.

Scripts et résultats : `scratchpad/v1167/` (build, diffs, work/compile-runtime, model,
reserve, cost-risk, refute).
