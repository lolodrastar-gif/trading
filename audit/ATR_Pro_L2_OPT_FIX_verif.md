# ATR Pro — Lolo 2 (15m exact) — OPT FIX : vérification (12/11)

Fichier relu : `src/lolo2/ATR_Pro_L2_15m_OPT_FIX.pine` (collage du 12/11, enregistré tel quel,
commit 922baef ; 955 lignes dont 624 vides, 331 lignes utiles). Référence : la variante TEST
auditée le 07/11 (`src/lolo2/ATR_Pro_L2_15m_TEST.pine`, rapport `audit/ATR_Pro_L2_verif.md`).
Pine v6, **non compilé ici**. Les numéros de ligne ci-dessous sont ceux du fichier sans les
lignes vides.

Méthode : diff exact TEST / OPT FIX, puis relectures indépendantes (compilation, modèle
numérique, mode 15m sur 30m et temps réel, charge), chacune avec sa propre émulation du script
en Python, et ma propre relecture ligne par ligne. État des contre-relectures adverses : voir
la fin du document.

## Verdict

- **Aucun bug de calcul trouvé.** Rang, régime et alertes sont identiques à la variante TEST
  dans les trois modes (unité du graphique, unité supérieure, unité inférieure), sur toutes
  les combinaisons bandes × échelle émulées.
- **Dans l'usage principal (graphique 30m, ATR en 15m, réglages par défaut), OPT FIX donne
  exactement les mêmes sorties que TEST** (trois émulations indépendantes, 0 écart sur les
  tracés, les messages et les alertes) **avec environ moitié moins de calculs**.
- **Trois petits défauts introduits par OPT FIX, aucun avec les réglages par défaut** (§ 4).
- **Les quatre pièges du 07/11 sont tous encore là** : cette partie du code est identique au
  caractère près (§ 5).
- « Parfait » : non, à cause de ces quatre pièges, qui tiennent au principe « 15m lu depuis
  un graphique 30m » et pas à une erreur de code.

## 1. Ce que OPT FIX change vraiment

Diff exact, cinq changements :

1. Titre, titre court, en-tête.
2. Trois booléens constants (l. 86-88) qui disent quelles statistiques sont utiles :
   `needQuantileBands`, `needBollingerBands`, `needMedianReference`.
3. `atrStats` (unité du graphique et unité supérieure) : quantiles et Bollinger calculés sur
   `raw[1]`, donc sur les N bougies PRÉCÉDENTES, comme le faisait déjà le mode 15m. Ils ne
   sont plus calculés quand ils ne servent pas (l. 112-114, 120-121, 134-136, 139-140).
4. Les statistiques de l'unité du graphique ne sont plus calculées quand une autre unité est
   demandée (l. 163). Dans TEST elles tournaient toujours, pour rien en mode 15m.
5. `lReady` découpé en quatre conditions (l. 255-259).

Rien d'autre ne bouge : requête 15m (l. 221, trois arguments en plus, toujours sans
`calc_bars_count`), instantané et compteur de données manquantes (l. 203-254), tableau,
fenêtre de données, alertes (l. 310-331).

## 2. Compilation

Très probable. Contrôle statique complet (analyse syntaxique, portées, signatures de chaque
appel contre la référence v6, qualificatifs `simple` / `series`) : 0 erreur. Ce contrôleur
retrouve 43 défauts injectés sur 43. Points regardés un par un :

- `ta.*` dans des ternaires et dans le `if` de la l. 163 : les conditions sont constantes
  (`simple bool`), donc chaque appel tourne à chaque bougie ou jamais. Au pire un
  avertissement de cohérence sur la l. 164, sans conséquence.
- Requêtes dans des `if` : requêtes dynamiques, actives par défaut en v6. 2 requêtes dans le
  source, 1 seule exécutée ; 21 éléments de tuple sur 127.
- Tracés : 17 `plot`, comptés 20 (couleur en série sur 3 d'entre eux), plus 2 alertes : 22 sur 64.
- Caractères : tiret long seulement dans des chaînes et commentaires ; le tiret demi-cadratin
  de « Rang centile 0–100 » est identique dans l'option (l. 62) et dans sa comparaison (l. 289).

Non vérifiable ici : la compilation réelle, et l'effet des lignes vides du collage à
l'intérieur du `switch` (non documenté ; si l'éditeur proteste, coller la version sans lignes
vides).

## 3. Calculs : comparaison avec TEST

- **Rang, régime, alertes** : 0 bougie différente, tous modes, toutes combinaisons (jusqu'à
  729 000 exécutions par variante dans une des émulations).
- **Mode 15m sur graphique 30m** : toutes les sorties identiques à TEST dans les 5
  combinaisons qui gardent la médiane, dont celle par défaut. Historique et tick par tick.
- **Unité du graphique et unité supérieure** : la bande de la bougie t est maintenant celle
  que TEST affichait à la bougie t-1. Avec les quantiles l'écart est minime (valeur « % de la
  normale » : médiane 0,03 point, p95 0,44, max 4,1 sur 97 435 bougies simulées ; lecture
  « au-dessus / en dessous d'une bande » changée sur 0,08 à 0,09 % des bougies). Les bandes ne
  bougent plus pendant la bougie en cours.
- **Conséquence utile** : un graphique 15m avec l'unité de l'ATR vide donne maintenant
  exactement les nombres du mode « 15m sur 30m » (valeur, bandes, rang, régime : 100 % des
  bougies clôturées dans deux émulations). Dans TEST les bandes différaient.
- Seuils : 465 794 combinaisons de seuils testées, toujours dans l'ordre, séparés d'au moins un
  pas de rang, entre 1 et 99.

## 4. Les trois défauts introduits (aucun avec les réglages par défaut)

1. **Deux lignes vides dans la fenêtre de données.** Bandes « Bollinger » ou « Aucune » ET
   échelle « Rang centile » ou « ATR (valeur) » (4 combinaisons sur 9) : la médiane n'est plus
   calculée (l. 88), donc « ATR en % de la normale » et « Quantile central de l'ATR » (l. 318,
   320) n'affichent plus rien. Rien d'autre n'en dépend. Correction la plus simple : l. 88
   `bool needMedianReference = true`.
2. **« Bollinger (comme l'original) » n'est plus l'original** sur l'unité du graphique et sur
   une unité supérieure : bandes calculées sans la bougie en cours (l. 120-121). En simulation
   l'ATR passe au-dessus de la bande haute sur 11,1 % des bougies au lieu de 9,8 %, sous la
   bande basse sur 4,4 % au lieu de 2,3 %. L'en-tête dit encore « rendu conservé » (l. 7) et
   « modes natif/HTF conservés » (l. 9) : faux pour les bandes. Le mode 15m n'est pas concerné
   (il était déjà sur la fenêtre précédente dans TEST). Correction : libellés seulement.
3. **Alertes bloquées pendant le préchauffage de Bollinger.** Mode 15m, bandes Bollinger,
   longueur Bollinger plus grande que la fenêtre des quantiles : `lReady` attend Bollinger
   (l. 258-259) alors que ni le régime ni les alertes ne l'utilisent. Le message dit « régime
   indisponible » avec un compteur qui dépasse son maximum (ex. « 650 / 500 ») alors que le
   régime est affiché. Début d'historique seulement, aucun effet en direct. Correction : retirer
   `lBollingerReady` de la l. 259.

## 5. Les quatre pièges du 07/11 : toujours là

Lignes identiques à TEST. Détail dans `audit/ATR_Pro_L2_verif.md` § 3.

1. **Fenêtre comptée en bougies 15m** : 500 = 125 h de marché, pas 250 h. Pour les mêmes heures
   qu'avant : 1000 (et 68 pour Bollinger). Seul indice dans le script : la ligne « Fenêtre des
   quantiles (heures de marché) » de la fenêtre de données.
2. **Moitié gauche du graphique vide** : sans `calc_bars_count`, la requête ne charge qu'autant
   de 15m que le graphique a de bougies. Aucun message. Sans importance pour le direct ; ne pas
   corriger si la légèreté prime (le correctif multiplie le calcul au chargement).
3. **Une 15m sur deux** : seule la seconde 15m de chaque bougie 30m est affichée et alertée.
   En simulation, environ 10 % des entrées en forte volatilité ne sont jamais alertées et un
   peu plus de 40 % le sont avec 15 minutes de retard.
4. **Course de flux à la clôture** : la valeur engagée à la clôture 30m est ce que le flux 15m
   a livré à cet instant. Rare, non mesurable ici.

Le remède commun aux pièges 2, 3 et 4 ne demande aucun code : un graphique 15m avec l'unité
de l'ATR vide (mêmes nombres, voir § 3).

Petits points déjà présents dans TEST : le préchauffage en unité du graphique ou supérieure
s'affiche comme « ATR constant sur la fenêtre » (l. 274, 312) ; « 15m » est écrit en dur dans
deux libellés du mode unité inférieure (l. 312, 321) ; avec les bandes en quantiles et
l'échelle « Rang centile », deux quantiles sont calculés pour rien.

## 6. Charge

Appels `ta.*` par tick en direct (comptés dans le code) :

| Mode | TEST | OPT FIX |
|---|---|---|
| 15m sur graphique 30m | 21 | 9 |
| Unité supérieure | 20 | 8 |
| Unité du graphique | 10 | 8 |

Tris de fenêtre (les plus chers) en mode 15m : 6 par tick, puis 3. Au chargement : environ la
moitié du travail `ta.*` en mode 15m ou unité supérieure, 1 à 3 % en unité du graphique avec
les réglages par défaut. En valeur absolue le gain reste petit avec une fenêtre de 500 : de
l'ordre de 0,2 à 0,3 s pour 20 000 bougies (estimation calée sur les seuls temps que donne le
manuel, pas une mesure). OPT FIX n'ajoute aucun calcul nulle part.

## 7. Fait-il bien son travail ?

Il calcule correctement ce pour quoi il est écrit : le rang de l'ATR 15m parmi les 500 mesures
15m précédentes, des bandes aux mêmes seuils que les régimes (bande franchie = couleur qui
change, à 0,1 à 0,3 % des bougies près), des alertes à la clôture seulement.

À savoir sur ce que cela mesure :

- **La fenêtre mélange toutes les heures.** Sur un marché ouvert 23 h, l'ATR 15m est
  mécaniquement plus haut en séance US que la nuit. Dans ma simulation (profil intrajournalier
  supposé, pas des données NQ réelles), l'heure seule explique environ les trois quarts du rang :
  rouge presque uniquement en séance US, compression sur les trois quarts des bougies de nuit.
  Le régime dit donc surtout « on est dans la partie agitée de la journée », pas « aujourd'hui
  est inhabituel pour cette heure ». À vérifier d'un coup d'œil : le rouge revient-il tous les
  jours aux mêmes heures ?
- **L'ATR 14 en 15m a une mémoire de 3 h 30.** Le rouge arrive après le début du mouvement et
  dure après sa fin.
- **Le seuil « calme / normal » sert aussi de référence 100 %.** À 50 c'est la médiane ; si on
  le change, « 100 % = habituel » change avec lui.
- Avec les bandes Bollinger, couleurs et bandes ne mesurent pas la même chose et se
  contredisent souvent ; c'est attendu.

## 8. Corrections au rapport du 07/11

- « Avertissements attendus sur les `ta.*` du `switch` » : le manuel dit qu'il n'y en a pas
  quand le paramètre est `simple`.
- « 17 tracés + 2 alertes sur 64 » : 22 sur 64.
- « 8 `ta.*` par 30m + 8 par 15m » : 10 et 11.
- « Alertes 2,3 fois plus souvent » avec la fenêtre 500 en 15m : non retrouvé. Les émulations
  du 12/11 donnent 1,4 à 1,6 fois par rapport au 30m natif et 1,05 à 1,1 fois par rapport au
  même ATR 15m sur 250 h. L'écart de régime (37 à 41 % des bougies) est retrouvé.

## 9. À vérifier dans TradingView

1. Compilation.
2. OPT FIX et TEST l'un sous l'autre, graphique 30m, ATR en 15m, mêmes réglages : courbe,
   couleurs et fenêtre de données identiques.
3. Fenêtre de données : « Intrabougies reçues sur cette bougie » vaut 2 sur les bougies
   clôturées.
4. Les alertes créées sur l'ancienne version continuent d'exécuter l'ancienne : les recréer sur
   OPT FIX.

## État des contre-relectures

Première passe interrompue par la limite d'usage après les quatre premières relectures.
Relance en cours au moment de cette version du rapport.
