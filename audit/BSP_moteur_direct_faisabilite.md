# BSP — un moteur en direct nourri par les ticks du graphique : faisabilité (07/11)

Question posée par Lolo le 03/11 : « trouvons autre chose de beaucoup plus fiable »
que les reprises grises pendant les trous de livraison 1T (27 à 164 bougies 10T sans
tick en rafale, mesuré en septembre). La seule voie structurelle : un second moteur,
en direct seulement, nourri par les mises à jour du graphique 10T lui-même (celles qui
dessinent les bougies), avec les mêmes formules, amorcé sur l'état exact du moteur 1T ;
l'historique et le rechargement restant au moteur 1T.

Étude en quatre phases : trois lectures (moteur et raccord, manuel v6, historique des
tentatives), trois conceptions indépendantes (ombre minimale, exactitude d'abord,
mesure d'abord), un juge, puis une contre-relecture adverse de chaque affirmation clé.
Onze agents, Pine non compilé ici.

## Verdict : ne rien construire avant d'avoir mesuré trois faits

Les trois conceptions sont faisables sur le papier (130 à 200 lignes, une option en fin
de liste décochée par défaut, aucune formule touchée, moteur 1T intact, amorçage exact
possible en RMA/EMA en exportant deux moyennes de plus du tuple : 17 éléments sur 127).
Le modèle Python donne 0,0 d'écart entre un moteur ainsi amorcé et le moteur 1T sur
3 000 ticks. Mais les trois reposent sur trois faits que le manuel ne documente nulle
part et que personne n'a jamais mesurés :

| Hypothèse | Ce qu'en dit le manuel | Ce qu'on en sait |
|---|---|---|
| H1 — une exécution du script sur la bougie 10T en direct = une transaction (pas de regroupement en rafale) | Le script s'exécute « une fois par mise à jour du flux », jamais « par transaction » (`execution-model.md` l. 145, 406, 521) | Jamais mesuré ; « ~10 exécutions par bougie » est une hypothèse écrite dans l'en-tête de la v11.66 (l. 657) et dans l'audit du lag |
| H2 — une barre 1T = une transaction (high = low = close) | « T » n'est défini que comme « ticks » du flux (`timeframes.md` l. 29-36) | Hypothèse du script (v11.66 l. 705), appuyée par Diag 12 = 10,00 sur l'historique seulement |
| H3 — pendant un trou 1T, le flux du graphique continue de livrer les transactions | Rien | Les bougies continuent de se former pendant le trou (c'est l'horloge du trou), mais au grain de la transaction, inconnu |

La contre-relecture a rejeté les quatre affirmations clés telles qu'énoncées,
précisément parce qu'elles sont non documentées et non mesurées. Si H1 est fausse en
rafale (TradingView regroupe plusieurs transactions dans une mise à jour), le moteur
direct voit moins que le 1T : au modèle, deux transactions par mise à jour donnent
jusqu'à 2,3 points de BP d'écart et 18 % d'états différents. Si H3 est fausse (les
deux flux calent ensemble), aucun moteur côté script ne peut montrer des transactions
que TradingView ne livre pas.

À noter aussi : un moteur par mise à jour exige des `varip`, que l'auteur de la v11.66
s'interdit (« aucun varip », l. 1393) ; c'est inévitable et à assumer si on construit.

## Première étape : la sonde d'exactitude

`src/test/sonde_exactitude.pine` (85 lignes, indicateur séparé, le BSP n'est pas
touché ; relue, une garde ajoutée sur tableau 1T vide). À poser sur le graphique NQ
10T, lire, retirer :

- **Au chargement**, la ligne « historique » répond à H2 et H3 sur tout l'historique
  chargé : nombre de bougies avec une barre 1T à high ≠ low (doit être 0) et nombre de
  bougies dont la somme des volumes 1T égale le volume 10T (doit être ≈ toutes).
- **En direct**, par bougie close : exécutions (doit être 10), exécutions sans
  changement de prix ni de volume (doit être 0), exécutions confirmées (doit être 1),
  ticks 1T livrés. À lire une minute au calme, puis pendant la rafale de 15:30.

Règle de décision, fixée avant la mesure : H2 = 0 sur l'historique, volumes
concordants ≥ 99 %, exécutions = 10 sur ≥ 95 % des bougies au calme et ≥ 90 % en
rafale. Si en rafale les bougies closes montrent nettement moins de 10 exécutions, le
flux du graphique est lui aussi regroupé : on arrête, le moteur direct n'apporterait
pas une mesure, et la réponse honnête est ce chiffre. Resterait alors le levier bon
marché : la fenêtre en secondes étendue aux reprises simples
(`audit/BSP_v43_iter_verif.md`, § 6).

Seconde sonde, plus complète (`src/test/sonde_mesure_DV.pine`, 368 lignes, 22
compteurs : regroupement prouvé par les extrêmes non atteints, retard 1T par bougie en
millisecondes, ombre du moteur comparée au 1T sur bougies strictes) : produite par
l'étude, non relue ligne par ligne, à ne poser que si la première passe.

## Si tout passe : ce qui serait construit

Une copie de test de la v11.66, « v11.67 [DV] » : deux moyennes exportées de plus sur
la ligne de retour du moteur (formules intactes), une case en fin de liste décochée
par défaut (rendu octet pour octet identique décochée), et 130 à 150 lignes avant le
pont : une douzaine de `varip`, amorçage à la première exécution de N+1 sur le dernier
tick 1T de N, un pas de moteur par mise à jour, et en direct la valeur du moteur
direct sur chaque bougie : plus de reprise, plus de gris de fenêtre, le gris ne
voudrait plus dire que « état neutre ». Le rechargement recalcule tout par le 1T,
comme aujourd'hui. Validation : A/B case décochée (identique), puis case cochée en
rafale, puis comparaison avant/après rechargement.

## Ce que ça ne change pas

La saccade du navigateur mesurée le 02/11. Un moteur en direct remplace des reprises
par des mesures ; il ne décharge pas le fil principal du navigateur.
