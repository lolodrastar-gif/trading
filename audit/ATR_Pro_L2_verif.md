# ATR Pro — Lolo 2 « 15m exact / graphique 30m » (TEST) — vérification (07/11)

Fichier : `src/lolo2/ATR_Pro_L2_15m_TEST.pine` (collé tel quel, commit d3b7c71). Pine v6,
non compilé ici. Trois relectures indépendantes (compilation v6, sémantique du mode 15m
sur 30m et du direct, modèle numérique des statistiques), puis une contre-relecture
adverse des six trouvailles non cosmétiques : 2 réfutées, 4 confirmées. La base
« ATR Pro corrigé 5 » n'est pas dans le dépôt : comparaison impossible avec ce que tu
avais, seulement avec ce que l'en-tête promet.

## 1. Compilation

Très probable. Tout ce que le fichier emploie est documenté en v6 : requêtes dans des
blocs `if` (requêtes dynamiques, actives par défaut en v6, `functions/indicator.md`),
fonction renvoyant un tuple de 11 séries passée à `request.security_lower_tf` (21
éléments de tuple sur 127 autorisés, 2 requêtes sur 40), idiome sans repeint
`[1]` + `lookahead_on` pour l'unité supérieure, paramètres `simple` tous satisfaits,
`display.pane + display.status_line + display.data_window` documenté, 17 tracés + 2
alertes sur 64. Le mélange `display.all` / somme de `display.*` dans un même `?:` est
déjà utilisé par ta v11.66 du BSP, compilée : pas un problème. À attendre : des
AVERTISSEMENTS (pas des erreurs) sur les `ta.*` dans les branches du `switch`,
inoffensifs car le choix ne change jamais en cours de route.

## 2. Ce que fait le mode 15m sur 30m, et ce que ça veut dire

- Chaque bougie 30m reçoit ses deux 15m ; le script affiche et évalue la DERNIÈRE
  (la seconde). La première 15m de chaque bougie 30m nourrit les fenêtres mais n'est
  jamais affichée, et un changement de régime confiné à elle ne déclenche jamais
  d'alerte. En direct, elle apparaît provisoirement pendant le premier quart d'heure,
  puis est remplacée. « 15m exact » veut dire « statistiques calculées en 15m, un
  échantillon par 30m », pas « affichage en 15m ». L'en-tête le dit, le titre non.
  Pour un vrai affichage 15m : mettre l'indicateur sur un graphique 15m avec l'unité
  de l'ATR vide.
- Rang et bandes regardent la même fenêtre (les N 15m précédentes, la courante
  exclue), comme promis ; vérifié programmatiquement, et en simulation « rang ≥ seuil »
  et « valeur ≥ bande » ne divergent que sur 0,03 à 0,10 % des bougies, toujours à la
  frontière d'interpolation. Hauts/bas de stabilité : N + 1 valeurs avec la courante,
  contre N dans le mode natif, négligeable.
- Données manquantes : valeurs conservées, compteur, message, alertes bloquées, remise
  à zéro au premier retour de données. Alertes : une seule par changement, à la
  clôture de la 30m, comparée au dernier régime VALIDE ; aucun double déclenchement
  dans le modèle.
- Direct : le modèle documenté implique que la 15m en formation est livrée, donc
  « Intrabougies reçues » vaut 1 pendant le premier quart d'heure puis 2, et le
  message rouge « Intrabougies absentes » ne s'affiche pas en séance normale (au pire
  un clignotement d'un tick sur une course de flux, sans compteur ni alerte).

## 3. Les quatre pièges confirmés

1. **La fenêtre compte des bougies 15m, donc moitié moins d'heures.** `Fenêtre des
   quantiles` = 500 et `Bollinger` = 34 sont passés tels quels au contexte 15m : 500 ×
   15 min = 125 h de marché, contre 250 h pour 500 bougies 30m. C'est LA raison pour
   laquelle le régime va différer massivement de ce que tu avais : en simulation
   (5 graines × 20 000 bougies 30m), le régime diffère d'un échantillonnage naïf du
   30m sur 38 % des bougies, et les alertes partent 2,3 fois plus souvent ; avec une
   fenêtre de 1 000 (mêmes heures), l'écart tombe à 0,5 % et les alertes au même
   nombre. Le script ne le dit que par le tracé « Fenêtre des quantiles (heures de
   marché) » de la fenêtre de données (125 h contre 250 h). Donc : pour comparer avec
   l'ancienne, mettre 1 000 et 68 quand l'unité de l'ATR est 15m sur un 30m, ou faire
   mettre à l'échelle dans le script (`regimeLookback × chartSeconds / askedSeconds`,
   plafonné à 5 000).
2. **La moitié gauche du graphique restera vide.** Sans `calc_bars_count`, la requête
   ne demande qu'autant de 15m qu'il y a de bougies sur le graphique (référence
   `request.security_lower_tf.md`) : deux 15m par 30m, donc la moitié récente du
   graphique seulement (10 000 bougies sur 20 000 en Premium), moins ~258 bougies de
   préchauffage 15m (ATR 14 + fenêtre 500). Les bougies plus anciennes reçoivent un
   tableau vide : gris, régime −1, aucun message (il n'est dessiné que sur la dernière
   bougie). Correction : `calc_bars_count = 100000` dans l'appel (plafond des plans
   non professionnels), et regarder le temps de chargement.
3. **Un échantillon sur deux.** Voir § 2 : à connaître avant d'adopter, pas un bug.
4. **Course de flux à la clôture.** La valeur engagée, tracée et alertée au tick de
   clôture de la 30m est ce que le flux 15m, indépendant, a livré à cet instant ; le
   manuel dit que ce flux peut, rarement, être en retard ou corrigé a posteriori.
   Après rechargement, la bougie peut donc différer et une alerte ne pas se
   reproduire. Inhérent aux données d'unité inférieure, l'en-tête l'admet : à mesurer
   en comparant la valeur à la clôture de quelques bougies en direct avec la valeur
   après rechargement.

Réfutés : l'erreur de compilation possible sur `display` (ta v11.66 fait pareil) ; le
message rouge pendant le premier quart d'heure (la 15m en formation est livrée).

## 4. Coût

Sur une bougie 30m, aucun enjeu : 8 `ta.*` par 30m (inutilisés en mode 15m) + 8 par
15m, dont trois `percentile_linear_interpolation` qui trient une fenêtre de 500. Rien
à voir avec le 10 ticks.

## 5. À vérifier dans TradingView, dans l'ordre

1. Compilation ; avertissements attendus, pas d'erreur.
2. Fenêtre de données, « Intrabougies reçues sur cette bougie » : 2 en historique ; 1
   dans la première minute après une ouverture 30m ; 0 en défilant vers la gauche là
   où le tracé s'arrête (piège 2).
3. « Fenêtre des quantiles (heures de marché) » : 125 h en mode 15m, 250 h en natif
   (piège 1) ; comparer l'ancienne et la nouvelle à heures égales, pas à bougies
   égales.
4. Noter la valeur à la clôture de quelques bougies 30m en direct, recharger, comparer
   (piège 4).
