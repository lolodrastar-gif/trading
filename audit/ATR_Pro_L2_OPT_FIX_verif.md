# ATR Pro — Lolo 2 (15m exact) — OPT FIX : vérification (12/11)

Fichier relu : `src/lolo2/ATR_Pro_L2_15m_OPT_FIX.pine` (collage du 12/11, enregistré tel quel,
commit 922baef ; 955 lignes dont 624 vides, 331 lignes utiles). Référence : la variante TEST
auditée le 07/11 (`src/lolo2/ATR_Pro_L2_15m_TEST.pine`, rapport `audit/ATR_Pro_L2_verif.md`).
Pine v6, **non compilé ici**. Les numéros de ligne ci-dessous sont ceux du fichier sans les
lignes vides.

Méthode :

1. Diff exact TEST / OPT FIX.
2. Cinq relectures indépendantes : compilation, modèle numérique, mode 15m sur 30m et temps
   réel, charge, adéquation à l'usage. Chacune a écrit sa propre émulation du script en Python.
3. Une contre-relecture adverse par relecture, chargée de réfuter chaque constat avec sa
   propre émulation et ses propres données.
4. Ma relecture ligne par ligne.

Résultat des contre-relectures : 28 constats, 28 confirmés, 0 réfuté. Plusieurs ordres de
grandeur ont été corrigés ; les fourchettes ci-dessous en tiennent compte. Beaucoup de ces 28
constats sont le même défaut vu par plusieurs relecteurs.

Limite : toutes les fréquences viennent de données simulées. Ce sont des ordres de grandeur,
pas des mesures sur le NQ. Rien n'a été observé sur TradingView.

## Verdict

- **Aucun bug de calcul trouvé.** Rang, régime et alertes sont identiques à la variante TEST
  dans les trois modes (unité du graphique, unité supérieure, unité inférieure), sur toutes
  les combinaisons bandes × échelle émulées. Seule exception : le cas limite du défaut 3, en
  début d'historique.
- **Dans l'usage principal (graphique 30m, ATR en 15m, réglages par défaut), OPT FIX donne
  exactement les mêmes sorties que TEST** (0 écart sur les tracés, les messages et les
  alertes, en historique et tick par tick) **avec environ moitié moins de calculs**.
- **Trois petits défauts introduits par OPT FIX, aucun avec les réglages par défaut** (§ 4).
- **Les quatre pièges du 07/11 sont tous encore là** : cette partie du code est identique au
  caractère près (§ 5).
- « Parfait » : non, à cause de ces quatre pièges, qui tiennent au principe « 15m lu depuis
  un graphique 30m » et pas à une erreur de code.
- **À ne pas oublier en l'ajoutant au graphique** : l'unité de temps de l'ATR est vide par
  défaut (l. 40), malgré le titre « 15m exact ». Tant qu'elle n'est pas mise sur 15,
  l'indicateur calcule l'ATR du graphique.

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

- **Rang, régime, alertes** : 0 bougie différente, tous modes, toutes combinaisons, sur
  plusieurs millions d'exécutions émulées par variante.
- **Mode 15m sur graphique 30m** : toutes les sorties identiques à TEST dans les 5
  combinaisons qui gardent la médiane, dont celle par défaut. Historique et tick par tick.
  Dans les 4 autres, seules les deux lignes du défaut 1 changent.
- **Unité du graphique et unité supérieure** : les bandes de la bougie t sont exactement
  celles que TEST affichait une bougie plus tôt (une bougie de l'unité supérieure plus tôt en
  mode supérieur). Conséquences avec les réglages par défaut :
  - Upper et Lower ont une valeur différente de TEST sur 55 à 72 % des bougies. Middle reste
    à 100.
  - La courbe « % de la normale » est divisée par la médiane de la fenêtre précédente. Elle
    diffère de TEST sur 41 à 70 % des bougies. L'écart est de moins de 1 point sur 95 % des
    bougies (médiane 0,03 à 0,08 point). Quelques bougies isolées vont bien plus loin, quand
    la médiane de la fenêtre saute : maximum de 0,6 à 41 points selon la série simulée.
  - La lecture « au-dessus / en dessous d'une bande » change sur 0,1 à 0,2 % des bougies.
  - Le premier tracé arrive une bougie plus tard (bougie 513 au lieu de 512).
  - Les bandes ne bougent plus pendant la bougie en cours.
- **Conséquence utile** : un graphique 15m avec l'unité de l'ATR vide donne maintenant
  exactement les nombres du mode « 15m sur 30m » aux mêmes instants (valeur, bandes, rang,
  régime : 100 % des bougies clôturées dans quatre émulations). Dans TEST les bandes
  différaient. Condition : les deux graphiques voient le même historique 15m ; sinon l'ATR
  diffère pendant les premières centaines de bougies seulement.
- Seuils : 465 794 combinaisons de seuils testées, toujours dans l'ordre, séparés d'au moins un
  pas de rang, entre 1 et 99.

## 4. Les trois défauts introduits (aucun avec les réglages par défaut)

1. **Deux lignes vides dans la fenêtre de données.** Bandes « Bollinger » ou « Aucune » ET
   échelle « Rang centile » ou « ATR (valeur) » (4 combinaisons sur 9, dans les trois modes) :
   la médiane n'est plus calculée (l. 88), donc « ATR en % de la normale » et « Quantile
   central de l'ATR » (l. 318, 320) gardent leur titre mais n'affichent plus rien. Rien
   d'autre n'en dépend : courbe, bandes, rang, régime et alertes sont inchangés. Deux
   corrections possibles :
   - l. 88 `bool needMedianReference = true`. Les deux lignes reviennent. Coût : un calcul de
     quantile par bougie dans ces 4 combinaisons seulement, de l'ordre de 0,03 à 0,05 s pour
     10 000 bougies avec la fenêtre 500 (estimation).
   - ou masquer les deux lignes quand elles sont vides : `display = needMedianReference ?
     display.data_window : display.none` aux l. 318 et 320. Aucun calcul en plus.
2. **« Bollinger (comme l'original) » n'est plus l'original** sur l'unité du graphique et sur
   une unité supérieure : bandes calculées sans la bougie en cours (l. 120-121). Les bandes
   sont celles de TEST décalées d'une bougie vers la droite. En simulation, l'ATR passe
   au-dessus de la bande haute sur 1,3 à 2,7 points de bougies en plus (par exemple 12,1 % au
   lieu de 10,4 %) et sous la bande basse sur 0,2 à 2,5 points en plus. Couleurs et alertes
   inchangées. L'en-tête se contredit : la l. 4 annonce le changement, la l. 9 dit encore
   « modes natif/HTF conservés » (faux), la l. 7 dit « rendu conservé » (ambigu). Dans le
   mode 15m rien ne change : les bandes Bollinger y étaient déjà sur la fenêtre précédente
   dans TEST. Correction conseillée : libellés seulement (l. 7, l. 9, et une infobulle sur la
   l. 46 disant « mesure courante exclue »). Ne pas renommer l'option elle-même : la l. 87 et
   les réglages enregistrés en dépendent. Pour retrouver les bandes de TEST à la place :
   `raw` au lieu de `raw[1]` aux l. 120-121, et corriger alors les commentaires l. 4 et
   l. 109-111.
3. **`lReady` attend Bollinger pour rien.** Mode 15m, bandes Bollinger, longueur Bollinger
   plus grande que la fenêtre des quantiles : `lReady` attend la fin du préchauffage de
   Bollinger (l. 258-259) alors que ni le régime ni les alertes ne l'utilisent. Exemple
   fenêtre 500, Bollinger 800, ATR 14 : pas prêt de la 514e à la 813e bougie 15m. Sur
   l'historique cela ne se voit pas (le message n'est dessiné que sur la dernière bougie, les
   alertes ne partent qu'en direct). Cela n'atteint le direct que si l'historique 15m chargé
   est plus court que longueur Bollinger + longueur ATR : en pratique un plan à 5 000 bougies
   avec une longueur Bollinger d'au moins 4 987. Dans ce cas : alertes bloquées et message
   « Préchauffage 15m … régime indisponible » au-dessus d'un régime affiché, jusqu'à ce que
   les bougies manquantes soient arrivées en direct, et de nouveau après chaque rechargement.
   Correction : l. 259 `bool lReady = lReadyBase and lQuantilesReady and lMedianReady`.
   Émulée : 0 écart avec TEST sur l'état prêt et les alertes.

## 5. Les quatre pièges du 07/11 : toujours là

Lignes identiques à TEST. Détail dans `audit/ATR_Pro_L2_verif.md` § 3.

1. **Fenêtre comptée en bougies 15m** : 500 = 125 h de marché, pas 250 h. Bollinger 34 =
   8 h 30, pas 17 h. Les libellés des deux réglages (l. 45, 47) ne le disent pas ; l'infobulle
   de l'unité de temps (l. 40) et l'en-tête le laissent entendre ; seule la ligne « Fenêtre
   des quantiles (heures de marché) » de la fenêtre de données donne les heures. Effet : le
   régime diffère de celui du réglage 1000 sur 15 à 40 % des bougies selon la simulation ; le
   nombre d'alertes change peu (1,0 à 1,3 fois). Pour les mêmes heures qu'avant : 1000, et 68
   pour Bollinger. À savoir : 1000 / 68 égalise les heures, pas l'indicateur. Par rapport au
   même indicateur lancé directement en 30m, le régime diffère encore sur 20 à 30 % des
   bougies, parce que l'ATR 14 est lui-même calculé sur des bougies 15m (3 h 30 au lieu de 7 h).
2. **Moitié gauche du graphique vide** : sans `calc_bars_count`, la requête ne charge qu'autant
   de 15m que le graphique a de bougies. Aucun message (le tableau n'est dessiné que sur la
   dernière bougie). Bougies utilisables : 9 744 sur 20 000, 4 744 sur 10 000, 2 244 sur 5 000.
   Ce constat repose sur la règle par défaut écrite dans le manuel ; à confirmer sur le
   graphique (§ 9). Sans importance pour le direct. Si la partie gauche compte : ajouter
   `, calc_bars_count = 41000` en dernier argument de la requête l. 221 pour un graphique de
   20 000 bougies (environ le double du travail au chargement). Sinon ne rien toucher : c'est
   le plus léger.
3. **Une 15m sur deux** : seule la seconde 15m de chaque bougie 30m est affichée et alertée
   (annoncé par l'infobulle l. 40). En simulation, 10 à 30 % des entrées 15m dans un régime ne
   donnent jamais d'alerte et 30 à 47 % sont alertées 15 minutes après la clôture 15m. Toute
   transition visible sur les bougies 30m clôturées est alertée exactement une fois.
4. **Course de flux à la clôture** : la valeur engagée à la clôture 30m est ce que le flux 15m
   a livré à cet instant. Seul un retard de quelques secondes est une vraie course : en
   simulation il change le régime sur moins de 0,1 % des clôtures pour un retard jusqu'à 5 s.
   Les deux autres cas (une seule 15m reçue, aucune 15m reçue) demandent une panne du flux
   15m de 15 ou 30 minutes. Fréquence réelle inconnue, non mesurable ici. Aucun durcissement
   de code conseillé.

Le remède commun aux pièges 2, 3 et 4 ne demande aucun code : un graphique 15m avec l'unité
de l'ATR vide (mêmes nombres, voir § 3 ; aucune requête d'intrabougies). Des alertes créées
là partiront à chaque entrée 15m, y compris celles que le panneau 30m ne montre jamais sur
une bougie clôturée.

Petits points déjà présents dans TEST :

- Unité du graphique ou supérieure avec moins d'historique que la fenêtre : le tableau dit
  « ATR constant sur la fenêtre » (moins de 500 bougies), puis rien entre 500 et 513 bougies
  (l. 274, 312). Hors usage principal.
- « 15m » est écrit en dur dans deux libellés du mode unité inférieure (l. 312, 321) et dans
  le titre, alors que l'unité est un réglage libre, vide par défaut.
- Avec les bandes en quantiles et l'échelle « Rang centile », deux quantiles sont calculés
  pour rien. Négligeable avec la fenêtre 500 (0,15 à 0,2 s pour 20 000 bougies, estimation).
- Les messages des deux alertes (l. 327-328) ne portent ni le symbole ni l'unité de temps,
  contrairement aux autres indicateurs LOLO 2 (`{{ticker}} {{interval}}`). Sans code : ajouter
  ces deux mots-clés dans le message au moment de créer l'alerte.

## 6. Charge

Appels `ta.*` par exécution (comptés dans le code, réglages par défaut) :

| Mode | TEST | OPT FIX |
|---|---|---|
| 15m sur graphique 30m | 21 | 9 |
| Unité supérieure | 20 | 8 |
| Unité du graphique | 10 | 8 |

Tris de fenêtre (les plus chers) en mode 15m : 6, puis 3. Au chargement : environ la
moitié du travail `ta.*` en mode 15m ou unité supérieure, 1 à 3 % en unité du graphique avec
les réglages par défaut. En valeur absolue le gain reste petit avec une fenêtre de 500 : de
l'ordre de 0,2 à 0,3 s pour 20 000 bougies (estimation calée sur les seuls temps que donne le
manuel, pas une mesure). OPT FIX n'ajoute aucun calcul nulle part.

## 7. Fait-il bien son travail ?

Il calcule correctement ce pour quoi il est écrit : le rang de l'ATR 15m parmi les 500 mesures
15m précédentes, des bandes aux mêmes seuils que les régimes (bande franchie = couleur qui
change, à 0,05 à 0,3 % des bougies près), des alertes à la clôture seulement.

À savoir sur ce que cela mesure :

- **La fenêtre mélange toutes les heures.** Sur un marché ouvert 23 h, l'ATR 15m est
  mécaniquement plus haut en séance US que la nuit. L'ampleur dépend du vrai profil de la
  journée, qui n'a pas été mesuré. En simulation, l'heure seule explique 9 % du rang si la
  séance US est 1,5 fois plus agitée que la nuit, 31 % à 2,3 fois, et deux tiers à trois
  quarts à 5,5 fois. Dans ce dernier cas le rouge tombe presque uniquement en séance US et
  62 % des alertes de forte volatilité tombent dans les trois mêmes heures. Allonger la
  fenêtre ne supprime pas l'effet. Le régime dit donc surtout « on est dans la partie agitée
  de la journée », pas « aujourd'hui est inhabituel pour cette heure ». À vérifier d'un coup
  d'œil : le rouge revient-il tous les jours aux mêmes heures ?
- **L'ATR 14 en 15m a une mémoire de 3 h 30.** Le rouge arrive après le début du mouvement et
  dure après sa fin.
- **Le seuil « calme / normal » sert aussi de référence 100 %.** À 50 c'est la médiane ; si on
  le change, « 100 % = habituel » change avec lui.
- Avec les bandes Bollinger, couleurs et bandes ne mesurent pas la même chose et se
  contredisent souvent ; c'est voulu et identique à TEST.

## 8. Corrections au rapport du 07/11

- « Avertissements attendus sur les `ta.*` du `switch` » : le manuel dit qu'il n'y en a pas
  quand le paramètre est `simple`.
- « 17 tracés + 2 alertes sur 64 » : 22 sur 64.
- « 8 `ta.*` par 30m + 8 par 15m » : 10 et 11.
- « Alertes 2,3 fois plus souvent » avec la fenêtre 500 en 15m : non retrouvé, dans aucune
  des simulations du 12/11. Elles donnent 1,3 à 1,9 fois par rapport au 30m natif et 1,0 à
  1,3 fois par rapport au même ATR 15m sur 250 h. La bonne formule est « alertes sur d'autres
  bougies », pas « beaucoup plus d'alertes ». L'écart de régime avec le 30m natif (37 à 46 %
  des bougies) est retrouvé.
- « `calc_bars_count = 100000` » pour remplir la moitié gauche : 41000 suffit pour un
  graphique de 20 000 bougies ; 100000 couvre tous les plans mais charge 5 fois plus de 15m
  que le défaut sur un tel graphique.

## 9. À vérifier dans TradingView

1. Compilation.
2. Après l'ajout : mettre « Unité de temps de l'ATR » sur 15 (vide par défaut).
3. OPT FIX et TEST l'un sous l'autre, graphique 30m, ATR en 15m, mêmes réglages : courbe,
   couleurs et fenêtre de données identiques.
4. Fenêtre de données : « Intrabougies reçues sur cette bougie » vaut 2 sur les bougies
   clôturées. En remontant vers la gauche, noter où elle passe à 0 (piège 2).
5. Alertes : celles créées sur TEST continuent d'exécuter TEST. Elles restent justes, les
   conditions sont identiques. Si tu en crées sur OPT FIX, supprime les anciennes pour ne pas
   tout recevoir en double.
6. Les heures du rouge sur une semaine : toujours les mêmes ? (§ 7)

## 10. Si une version corrigée est voulue

Rien n'est à corriger avec les réglages par défaut. Les corrections possibles, toutes
petites :

- l. 88 : `bool needMedianReference = true` (défaut 1).
- l. 259 : retirer `lBollingerReady` (défaut 3).
- l. 7 et l. 9 de l'en-tête, infobulle sur la l. 46 (défaut 2, libellés seulement).
- Optionnel : une branche « préchauffage » avant `constantWindow` dans le message l. 312 ;
  `{{ticker}} {{interval}}` dans les deux messages d'alerte.
