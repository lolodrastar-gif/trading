# BSP — rapport complet au 07/11/2026

Tout ce qui a été établi sur le BSP (moteur 1T affiché sur 10T, NQ, layout « lolo »)
depuis le 10/10, avec les dernières trouvailles. Chaque section renvoie au rapport
détaillé dans `audit/`. Pine n'a jamais été compilé ici : chaque conclusion de code est une
lecture contre le manuel v6, un modèle rejoué hors Pine, ou une relecture adverse.

## En bref

1. **La version installée, v11.66, est la bonne.** Neuf relectures, 42 trouvailles, 38
   corrigées le 10-11/10 ; aucune erreur de compilation ni d'exécution trouvée depuis ;
   moteur identique octet pour octet depuis la v11.4.
2. **Sept copies de test ont été vérifiées** (opt, opt2, test3, test4, anneau, v4.3,
   ITER) : toutes identiques en sorties en direct normal, à quelques choix visibles près
   (test3 : bord vivant éteint ; test3-4 : chiffre opposé sombre ; v4.3 : récupérations en
   rafale). Aucune ne peut agir sur la saccade. Aucune n'est à installer sur « lolo ».
3. **La saccade de 15:30 du 02/11 est une saturation du fil principal du navigateur**,
   tout l'onglet, pas un gel unique : 66 tâches longues par 10 s, fil occupé 35 à 72 %, 7 à
   19 images par seconde pendant 2 min 49 s. Pas la mémoire, pas le serveur. Le BSP y
   contribue par ce qu'il envoie à dessiner, pas par ce qu'il calcule. Lolo a réduit le
   coût du graphique le 04/11 : mieux.
4. **Le gris n'est pas un bug.** Quatre chemins seulement, inchangés depuis les v11.29 et
   v11.63 : zone neutre, reprise simple au-delà de dix bougies sans tick 1T, calcul
   indéfini, reprise invalidée. Les bandes grises dans le rouge sont des trous de livraison
   1T de TradingView (27 à 164 bougies d'affilée en rafale, mesuré en septembre). La case
   « Reprises strictes » décochée est inerte.
5. **Les récupérations de la v4.3 (TRAIL64, V4) ne créent pas ce gris** : sur un million
   de bougies de rafale simulées, 3 grises ajoutées, 4 retirées.
6. **Le coût serveur du script est borné et petit** : quelques centaines d'opérations par
   exécution, rien ne grossit avec la rafale. Les gains des copies de test se comptent en
   microsecondes, invisibles à l'écran.
7. **Un moteur en direct nourri par les ticks du graphique est faisable sur le papier**,
   mais repose sur trois faits jamais mesurés. Rien n'est construit avant la sonde
   d'exactitude (fournie le 07/11).
8. **Ce qui reste à mesurer**, par ordre d'intérêt : les exécutions par bougie en direct
   (la sonde), la part du dessin du BSP dans la saccade (A/B avec les cases du groupe
   « 6 — Tests 22h »), le CSV de Lolo Control d'une ouverture après la réduction du
   graphique.

## 1. Versions et règles

| Version | Date | Ce que c'est | Verdict |
|---|---|---|---|
| v11.65.1 | 10/10 | script collé, base de l'audit | 1 bug (bord ≠ série sous « Reprises strictes »), textes, code mort — `audit/BSP_v11.65.1_audit.md` |
| **v11.66** | 10-11/10 | **installée**. 42 trouvailles, 38 corrigées : correction 0 (lecture du direct à la milliseconde partagée, gardée par la tête de N), deux correctifs sous options, `DIAG_FULL`, tri du tableau figé mémorisé, bord calculé sur la dernière bougie seulement, Diag masqués décochés | aucune erreur trouvée ; rendu par défaut identique sauf la correction 0 — `audit/BSP_v11.66_corrections.md` |
| code mort | 11/10 | 91 points, 86 confirmés | aucune sortie, aucun coût touchés ; ne rien changer — `audit/BSP_v11.66_code_mort.md` |
| perf, perf-varip | 13/10 | v11.66 + 4 cases « 6 — Tests 22h » cochées par défaut ; réserve en `varip` | pour les tests A/B seulement — `audit/BSP_v11.66_lag_22h.md` |
| opt | 21/10 | sorties directes dans `pickLatest`/`pickTrail`, recherche partagée | identique |
| opt2 | 22/10 | 12 blocs : raccourcis de recherche, réserve, reprise rafraîchie | identique, 0 contre-exemple sur 80 000 cas par fonction ; 3 points de compilation — `audit/BSP_v11.66_opt2_verif.md` |
| test3 | 24/10 | 4 cases perf avec **bord éteint par défaut**, chiffre opposé sombre, recherches natives, réserve certifiée, moteur allégé | identique hors bord et chiffre ; recherches natives à vérifier par sonde — `audit/BSP_test3_verif.md` |
| test4 | 24/10 | bord rallumé, mémoire de couleur des dessins | image identique à l'installée hors chiffre opposé — `audit/BSP_test4_verif.md` |
| anneau | 26/10 | réserve circulaire de 13 000 cases | identique (3,9 M versements, 0 écart) ; coût serveur dans les deux sens — `audit/BSP_test4_anneau_verif.md` |
| v4.3 audit | 02/11 | tri8, TRAIL64 et V4 **actifs**, 20 sondes passives | identique en direct normal ; plus lourde ; copie d'audit, « pas pour le trading réel » — `audit/BSP_v43_audit_verif.md` |
| ITER | 03/11 | v4.3 avec `isSorted` par itérateur | identique (120 000 cas), moitié moins de lectures ; reste la copie d'audit — `audit/BSP_v43_iter_verif.md` |

Règles de l'auteur, respectées partout : moteur figé, aucun `varip`, trois couleurs, un
nouveau réglage toujours en fin de liste (TradingView mémorise par position), 11 tracés
sur 64 dans le principal, le jumeau « BSP Diag » partage le fichier hors DIAG-SECTION.

Ce que les copies de test ont en commun : des gains côté serveur en microsecondes, pour
un navigateur qui reçoit exactement la même chose. C'est pourquoi aucune ne peut déplacer
une mesure de saccade.

## 2. La saccade : chronologie et conclusions

- **13/10, clôture de New York (≈ 100 bougies 10T par seconde).** Audit du code en
  direct : chemin par exécution = 3 à 5 dichotomies sur la réserve, 8 à 10 sur les
  tableaux, `isSorted` du tableau vivant (≈ 10 éléments, plafond 2 000), `pickTrail` ≤ 16,
  ~1 500 opérations scalaires, 5 à 9 mises à jour de dessins ; versement une fois par
  bougie. Rien ne croît avec la rafale. Le Profiler, cumulé depuis le chargement, montre
  l'historique (requête 33 %, moteur 25 %, bloc de fin 16 %, versement 16 %) et ne peut
  rien dire de la rafale sans un delta. Fait décisif : un script lent côté serveur ne
  peut ralentir que son propre volet ; si tout le setup se fige, c'est le navigateur.
- **13-20/10.** Rechargement à 21:40 : une clôture sans lag, puis le lag revient, même page
  rechargée, aussi en séance ; un graphique témoin nu dans un autre navigateur ne lag
  jamais ; deux graphiques en ticks dans le même onglet (un seul fil) ; diagnostics,
  fenêtre de données, éditeur et Profiler ouverts pendant les épisodes. Configuration du
  16/10 : tout fermé, 1 597 barres calculées, 28 957 ticks d'historique. Lolo Guard :
  blocages de 358 à 388 ms le 21/10, 722 ms le 20/10. Fausse piste : la limite mémoire
  d'Edge (placée au maximum, aucun plafond).
- **02/11, 15:30.** CSV Lolo Control v4.0.1 (1 358 fenêtres de 10 s, onglet ouvert depuis
  10:58) : l'épisode commence à 2 s près à 09:30:00 ET et s'arrête net à 15:32:47 ; 755
  tâches de 50 à 327 ms en moins de deux minutes visibles, aucune ≥ 500 ms ; dérive du
  minuteur jusqu'à 614 ms ; mémoire calme (305 à 427 Mo). Trois instruments concordent :
  saturation de tout l'onglet, pas un gel, pas la mémoire, pas le serveur (un serveur lent
  donne des données en retard sur un navigateur inactif, l'inverse de ce qui est mesuré).
  Rien n'attribue le travail au BSP : seul un A/B peut mesurer sa part.
  `audit/lolo_control_2026-11-02.md`.
- **04/11.** Lolo a réduit le coût du graphique : « c'est mieux ». Non chiffré : il faut
  le CSV d'une ouverture dans cette configuration pour comparer tâches par 10 s,
  % occupé et images par seconde.

Ce qui peut réduire la saturation, sans toucher à la fiabilité : ce que le BSP pousse
(16 « plot counts » : 11 valeurs et 5 couleurs par bougie, un remplissage coloré sur
1 000 bougies, 5 objets de dessin réécrits à chaque tick) — cases « 6 — Tests 22h »
(bord non dessiné, puis courbes et chiffres en `display.none`), « Barres 10T dessinées »
à 500 ; la charge du reste du layout ; la séparation des deux graphiques en deux fenêtres
ou profils (deux fils) ; Profiler éteint, éditeur et fenêtre de données fermés ;
rechargement avant les rafales ; écran à 60 Hz (la sonde d'images montre déjà 60 images/s
en temps normal). Protocole : même réglage toute la séance, fixé avant 15:25, CSV de
15:25 à 15:40, comparer d'un jour à l'autre.

Ce qui n'y peut rien : toute optimisation du code serveur (opt2, anneau, tri8,
itérateur), prouvée identique en sorties et donc identique pour le navigateur.

## 3. Le gris

Le rendu ne connaît que trois couleurs. Une bougie close est grise par quatre chemins,
identiques dans la v11.66 et dans toutes les copies (la section pont-rendu ne diffère que
par une condition d'estimation inerte et un bloc d'audit inerte) :

1. **Zone neutre** (`nextSignalState`) : l'écart BP − SP est revenu dans ± « Retour au
   gris » et n'a pas ressorti au-delà de ± « Sortie du gris ». Avec les réglages de Lolo
   (1,618 / 3,618 au lieu de 2,618 / 4,236), gris dès que BP est entre 49,2 et 50,8 %,
   sortie au-delà de 51,8 / 48,2 %. Remplissage gris, plus opaque que les couleurs (60
   contre 70-78 de transparence), d'où des bandes qui ressortent. C'est le gris qui
   ondule serré autour de 50 %.
2. **Reprise simple hors fenêtre** (`greyBridge`, fenêtre de dix bougies depuis la
   v11.29) : plus de dix bougies 10T consécutives sans aucun tick 1T. Valeur reprise à
   plat, courbe grise, SANS remplissage. En rafale, TradingView ne livre aucun tick 1T
   pendant 27 à 164 bougies d'affilée (23-24/09) : dix bougies durent de 0,1 s à quelques
   secondes. Ce sont les bandes fines dans une zone pleine à 55 %, là où l'état du moteur
   ne peut pas être 0. C'est le « mal adapté aux pics de volatilité » : la fenêtre compte
   des bougies, pas des secondes ; la v11.56 avait ajouté une fenêtre en secondes, mais
   pour l'option « Estimer » seulement, en laissant volontairement les reprises simples.
3. **Calcul indéfini** : ratio na. En « Ratio des moyennes », il faut
   `RMA(amplitude, 233) ≤ 1e-8`, soit 4 100 à 5 000 ticks consécutifs sans aucun
   mouvement de prix, ou le préchauffage du début d'historique. Inatteignable en séance.
4. **Reprise invalidée** : candidat de reprise plus récent au ratio na ; mêmes conditions.

Avec « Colorer les deux courbes ensemble » décochée, la courbe du camp opposé est TOUJOURS
grise, par construction. La case « Reprises strictes » décochée est inerte (sept usages,
tous réduits au comportement v11.63) ; cochée, elle ne peut qu'ajouter du gris et couper
la courbe après dix bougies.

**Dernières trouvailles (relecture indépendante du 03-04/11).** Les récupérations de la
v4.3 ne font en général qu'ajouter des reprises rafraîchies (colorées, fenêtre remise à
zéro), donc moins de gris. La contre-relecture a trouvé trois façons rares d'en ajouter :
un tick plus récent dont l'état du moteur est réellement 0 (lecture plus fidèle), une
fenêtre qui se ferme une bougie plus tôt dans un cas de milliseconde partagée en direct,
et le ratio na. Mesuré : 3 bougies grises ajoutées et 4 retirées sur un million de bougies
de rafale simulées. Aucune ne peut faire les bandes de la capture du 03/11.

**Pour identifier une bougie grise** (« Afficher les diagnostics », fenêtre de données) :

| Lecture | Chemin |
|---|---|
| courbe entre 49,2 et 50,8 % ou ondulant autour, remplissage gris | 1, voulu |
| Diag 58 = −1, Diag 61 qui grandit de bougie en bougie, courbe plate, pas de remplissage | 2, livraison 1T |
| Diag 58 = 0, 1, −5 ou −7, courbe grise loin de 50 %, remplissage gris | 3, à signaler |
| Diag 58 = −1, Diag 61 petit, courbe plate, remplissage gris | 4, à signaler |

Un test sans réglage : recharger le graphique après la rafale ; les bandes disparaissent
si les ticks sont arrivés en retard, parce que l'historique les a.

**Leviers**, au choix de Lolo : (a) « Estimer les bougies sans tick » cochée et
« Estimation : garder la couleur (secondes) » jusqu'à 30 s — sans code, mais une
estimation, pas une mesure ; (b) deux lignes pour étendre la fenêtre en secondes aux
reprises simples (la couleur de la dernière mesure gardée pendant la rafale, valeur à
plat, rien d'inventé ; le revers : une couleur jusqu'à N secondes en retard au moment le
plus violent, raison pour laquelle la v11.56 ne l'avait pas fait) ; (c) garder le gris,
qui dit « pas de tick reçu ».

## 4. Fiabilité : prouvé, limité, inconnu

**Prouvé** (hors Pine, par modèles et relectures adverses) :
- aucune erreur de compilation ni d'exécution trouvée en neuf relectures de la v11.66 et
  dans chaque copie ; chaque accès de tableau gardé, chaque boucle bornée, aucune boucle
  descendante de la v6 non gardée ;
- la chaîne d'identité : opt2 (80 000 cas par fonction), anneau (3,9 M versements, 4,4 M
  chaînes exhaustives), v4.3 (1,2 M cas, 300 000 d'intégration), ITER (120 000 cas) ;
- le moteur `bspEngine1T` jamais touché ; les 28 (puis 32) réglages jamais déplacés ;
- la machine d'état des couleurs et ses quatre chemins, les alertes de régime du modèle.

**Limites documentées**, écrites dans l'en-tête de la v11.66 :
- livraison 1T en retard ou absente en rafale (27 à 164 bougies), reprises puis gris ;
  tout est relu au rechargement ;
- milliseconde partagée aux frontières (≈ 22 % des frontières le 25/09) : la correction 0
  lit le dernier tick de N à l'ouverture de N+1 en direct, sous garde ; résidus : tête
  absente → recul d'un tick comme avant ;
- bord vivant en avance d'un tick sur ≈ 1 % des bougies (Diag 64, historique) ;
- `time_close` na en direct sur un graphique en ticks (Diag 47) ;
- le direct et l'historique peuvent différer après rechargement (flux indépendants).

**Jamais mesuré** (le manuel ne le dit pas, le code le suppose) :
- le nombre d'exécutions du script par bougie 10T en direct : « ~10 » est une hypothèse
  (en-tête v11.66 l. 657, audit du lag) ; `sonde_test4.pine` le compte, aucun résultat
  noté ;
- qu'une barre 1T est une transaction (high = low = close) : Diag 12 = 10,00 et Diag 48 = 0
  sur l'historique seulement ;
- le coût du retour en arrière de la réserve `var` (6 000 à 9 000 objets) et de la
  livraison des 15 tableaux à chaque mise à jour : internes de TradingView ;
- si le flux du graphique continue pendant un trou 1T.

## 5. Le coût serveur

Par exécution en direct : quelques centaines d'opérations, borné (2 000, 6 000, 16, 14),
versement O(1) sur une bougie vide, purge de 6 000 recopies toutes les ~300 bougies (plus
de recopie avec l'anneau, mais deux appels de fonction par lecture et un tableau de
13 000 cases en permanence). `isSorted` pèse 2 à 4 % d'une exécution normale ; le 27,3 %
vu au Profiler le 26/10 est un cumul chargement + direct sur un appel qui inclut son corps,
et n'a pas pu être attribué (historique à tableaux de 64 à 2 000 éléments). Le tri8 ne
change que le contrôle de boucle ; l'itérateur enlève une lecture par élément ; aucun des
deux n'est mesurable autrement qu'au Profiler, même séance, ligne de `curTimesSorted`,
avant et après.

Deux postes serveur perfectibles mais petits : la lecture différée de N refaite à chacune
des ~10 exécutions de N+1, et `isSorted` du tableau vivant refait à chaque exécution.
Les mémoriser exigerait des `varip`. Gain nul sur l'écran.

Ce que le Profiler peut dire de la rafale, et comment : delta entre deux captures
(21:59 et 22:03, ou 15:29 et 15:33), Profiler sur la seule copie ouverte dans l'éditeur,
aucun réglage changé pendant la rafale, barres calculées au minimum ; lire
Δexec(ligne par mise à jour) / Δexec(ligne par bougie) = exécutions par bougie, et
Δexec(corps d'`isSorted`) / Δexec(appel) = éléments balayés. Jamais fait à ce jour.

## 6. Le moteur en direct (étude du 03-07/11)

La seule voie structurelle contre les reprises pendant les trous : un second moteur, en
direct seulement, nourri par les mises à jour du graphique 10T (close, close, close : sur
une barre 1T high = low = close, donc les formules n'ont besoin que de deux prix
successifs), avec les mêmes formules, amorcé sur l'état exact du moteur 1T à l'ouverture
de N+1 (il faut exporter deux moyennes de plus du tuple : 17 éléments sur 127, et 12
`varip`), l'historique et le rechargement restant au moteur 1T. Trois conceptions (ombre
minimale, exactitude d'abord, mesure d'abord), 130 à 200 lignes, option en fin de liste
décochée par défaut, rendu identique décochée. Le modèle donne 0,0 d'écart une fois
amorcé. Mais la contre-relecture a rejeté les quatre affirmations clés : non documentées,
non mesurées. Si TradingView regroupe les transactions en rafale, le moteur direct voit
moins que le 1T (deux transactions par mise à jour : jusqu'à 2,3 points de BP et 18 %
d'états différents). Si les deux flux calent ensemble, aucun moteur ne peut aider. Il
casse aussi la règle « aucun varip ».

Verdict : mesurer d'abord. `src/test/sonde_exactitude.pine` (85 lignes, relue, une garde
ajoutée) : au chargement, barres 1T à high ≠ low (doit être 0) et volumes concordants ;
en direct, exécutions par bougie close (doit être 10), sans changement (0), confirmées
(1), une minute au calme puis à 15:30. Règle fixée avant la mesure : 10 exécutions sur
≥ 95 % des bougies au calme, ≥ 90 % en rafale. Échec → on arrête, et la réponse est ce
chiffre. Réussite → copie de test v11.67, A/B décochée puis cochée.
`audit/BSP_moteur_direct_faisabilite.md`.

## 7. Recommandations, dans l'ordre

1. Garder la v11.66 sur « lolo » ; ne pas y empiler les copies de test. Si une copie doit
   servir, c'est pour un A/B sur un onglet séparé.
2. Poser la sonde d'exactitude une minute au calme et à 15:30, envoyer la capture de
   l'étiquette. C'est le premier chiffre jamais mesuré sur ce que le script reçoit en
   direct.
3. Envoyer le CSV de Lolo Control d'une ouverture dans la configuration allégée du 04/11,
   puis faire l'A/B « bord vivant non dessiné » un autre jour, réglé avant 15:25.
4. Pour le gris en rafale, choisir entre les trois leviers du § 3 ; je prépare (b) sur une
   copie de la v11.66 sur demande.
5. Ne rien changer au code sans mesure : chaque modification sans bug trouvé enlève de la
   fiabilité, elle n'en ajoute pas.

## 8. Index des fichiers

Sources : `src/BSP_v11.66.pine` (installée), `src/BSP_v11.65.1.pine`, `src/test/` (perf,
perf_varip, opt, opt2, test3, test4, anneau, v43_audit, v43_iter, sondes :
`sonde_recherche_native`, `sonde_test4`, `sonde_exactitude`, `sonde_mesure_DV`).
Rapports : `audit/BSP_v11.65.1_audit.md`, `BSP_v11.66_corrections.md`,
`BSP_v11.66_code_mort.md`, `BSP_v11.66_lag_22h.md`, `BSP_v11.66_opt2_verif.md`,
`BSP_test3_verif.md`, `BSP_test4_verif.md`, `BSP_test4_anneau_verif.md`,
`BSP_v43_audit_verif.md`, `BSP_v43_iter_verif.md`, `lolo_control_2026-11-02.md`,
`BSP_moteur_direct_faisabilite.md`.
