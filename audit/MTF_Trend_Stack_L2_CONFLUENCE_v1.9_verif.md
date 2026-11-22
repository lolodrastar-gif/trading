# MTF Trend Stack - Lolo 2 CONFLUENCE v1.9 : vérification (22/11)

Fichier relu : `src/lolo2/MTF_Trend_Stack_L2_CONFLUENCE_v1.9.pine` (collage du 22/11, enregistré
tel quel, commit 69efdd2, 479 lignes). Les « l. N » ci-dessous sont les lignes de ce fichier.
Pine v6, **non compilé ici**. Usage visé : graphique NQ en 100 ticks, lecture des deux tableaux
en direct.

Méthode :

1. Sept relectures indépendantes, une par angle : compilation, moteur des six tendances et
   alertes, graphique en ticks et plateforme, qualité de marché, structure et confluence,
   charge et robustesse, libellés. Chacune a écrit sa propre émulation en Python.
2. Une contre-relecture adverse par relecture, chargée de réfuter chaque constat et chaque
   point annoncé « correct », avec sa propre émulation.
3. Ma lecture ligne à ligne et ma propre émulation des deux tableaux
   (`audit/MTF_Trend_Stack_v1.9_emulation/emu.py`, 12 séances simulées de 23 h au pas d'une
   seconde), écrite avant de lire les leurs.

Limites :

- Aucune donnée de marché ici. Toutes les fréquences viennent de prix simulés (marches
  aléatoires au pas de 0,25 point, avec ou sans tendance). Ce sont des ordres de grandeur, pas
  des mesures sur le NQ.
- Rien n'a été observé sur TradingView.
- Le site de documentation de TradingView n'est pas joignable depuis cette session. Les points
  qui s'appuient sur la documentation viennent d'extraits renvoyés par un moteur de recherche
  et sont classés « probable » au mieux.

## Verdict

- **Aucune erreur de calcul trouvée.** Règle des six tendances, ADX / DMI, ER de Kaufman, ATR
  relatif, CHOP, pivots, cassures, structure, VWAP, références les plus proches : tout
  correspond aux formules annoncées (§ 1).
- **Tout est bien lu sur la dernière bougie clôturée** de chaque unité de temps, de la même
  façon dans les 11 demandes. Sur un graphique en secondes, l'émulation ne trouve aucun écart
  entre historique et temps réel.
- **Aucune erreur de compilation trouvée à la lecture.** Un avertissement probable (l. 229),
  sans effet sur les valeurs.
- **Ton cas d'usage, le graphique en 100 ticks, n'est pas décrit par la documentation.** En
  direct, chaque case montre très probablement la dernière bougie clôturée de son unité. Trois
  tests de deux minutes le confirment (§ 2).
- **Les deux alertes ne servent probablement à rien sur le 100 ticks** : TradingView n'exécute
  pas d'alertes sur les intervalles en ticks. Créées sur un graphique en secondes, elles
  sonneraient environ 12 fois par heure et par sens sur un marché sans tendance (§ 3).
- **Les tableaux disent plus qu'ils ne mesurent.** Sur un marché simulé sans aucune tendance,
  « FULL BULL » ou « FULL BEAR » est affiché 38 à 40 % du temps, « Conf. 1m OK » 37 à 38 %, le
  mot « ACHAT » ou « VENTE » 70 % (§ 3, § 4).
- **« CONFLUENCE » est rare, brève, et refusée quand aucun niveau connu n'est devant le prix.**
  Elle ne peut pas s'afficher sur de nouveaux plus hauts au-dessus du plus haut de la veille.
  Plus la tendance simulée est propre, plus elle est rare (§ 4).
- **Fiable ?** Comme tableau de contexte lu en direct : oui, sous réserve des tests du § 2.
  Comme signal : non, rien ne le montre et le script ne le prétend pas. Pour les alertes sur
  le 100 ticks : non.

## 1. Ce qui est juste

Chaque point a été retrouvé par la contre-relecture avec son propre code.

- **Six tendances** (l. 63-70) : hausse si EMA 11 au-dessus de l'EMA 29 et clôture au-dessus de
  l'EMA 29, baisse en miroir, sinon neutre. Comptage, verdict et couleurs cohérents sur les
  4 096 combinaisons possibles (l. 88-100, 263-271).
- **Lecture en bougie clôturée** : les 11 demandes utilisent le même schéma (valeur de la
  bougie précédente avec `lookahead_on`, l. 75, 230, 384, 389). Aucune bougie en cours n'entre
  dans un calcul.
- **Pas de repeinture sur un graphique en secondes** : 0 bougie différente entre historique et
  temps réel sur graphiques 1 s et 5 s émulés, alertes identiques. C'est le modèle du manuel,
  pas une observation de la plateforme.
- **ADX / DMI, ER, ATR relatif, CHOP** (l. 206-224) : égaux à des versions écrites d'après les
  définitions d'origine, à 10⁻¹³ près. Le CHOP ne donne jamais de fausse valeur : il affiche N/A
  si l'amplitude est nulle.
- **Structure** (l. 347-384) : un pivot n'est utilisé qu'après ses 3 bougies de confirmation ;
  la cassure est testée sur les niveaux connus avant la bougie ; les libellés « HH + HL »,
  « LH + LL », « MIXTE » correspondent au calcul.
- **Références les plus proches** (l. 394-409) : bon niveau, bon nom.
- **Verdict et explication du second tableau ne se contredisent jamais** : « CONFLUENCE » va
  toujours avec « Crit. reunis », « CONTRADICTION » avec « Structure / VWAP oppose ».
- **Données manquantes** : tant qu'une mesure manque, le verdict est N/A, jamais une fausse
  confluence (l. 418). Divisions par zéro et logarithmes protégés.
- **Tableaux** : 36 cellules sur 36 et 22 sur 22, aucune hors limites.
- **Limites de TradingView** : 11 demandes sur 40 permises, 34 valeurs sur 127.
- **Garde-fous de réglages** (l. 44-60, 191-201) : EMA rapide plus longue que la lente, deux
  unités identiques, confirmation plus courte que l'unité de qualité, seuils CHOP inversés
  s'arrêtent sur un message clair. Aucun ne se déclenche avec les réglages par défaut sur le
  100 ticks.
- **Hausse et baisse traitées de façon symétrique.**

## 2. Ton graphique en 100 ticks

### 2.1 Ce qui n'est pas documenté

Le script demande des bougies de 5 s à 1 min, 3 min et jour depuis un graphique en ticks
(l. 75, 233-236, 387-389). La documentation décrit ces demandes depuis un graphique en temps.
Elle ne dit rien du graphique en ticks : ni comment les bougies demandées sont alignées sur
les barres de 100 ticks, ni ce que vaut l'historique après rechargement.

Ce qui est établi par le code : les deux tableaux ne dépendent pas des barres de 100 ticks.
Tous les calculs se font dans les unités demandées. Les barres du graphique ne servent qu'aux
deux EMA tracées (l. 146-149) et au déclenchement des alertes (l. 153, 155).

Lecture la plus probable en direct : chaque case montre la dernière bougie clôturée de son
unité, mise à jour au premier tick qui suit la clôture. Tu lis déjà les tableaux sur ton
100 ticks, donc la demande est acceptée ; il reste à vérifier l'alignement.

Trois tests, deux minutes chacun :

1. **Horloge** : regarder la case ADX avec une horloge à la seconde. Elle doit rester fixe 30 s
   et ne changer qu'à hh:mm:00 et hh:mm:30, à une seconde près.
2. **Graphique 30 secondes** à côté, avec l'indicateur DMI intégré (14, 14) : sur la dernière
   bougie clôturée, ADX, +DI et −DI doivent égaler les cases ADX et DMI à 0,1 près.
3. **Graphique 1 minute** avec EMA 11 et EMA 29 : sur la dernière bougie clôturée, la ligne
   « 1m » doit dire BULL si l'EMA 11 est au-dessus de l'EMA 29 et la clôture au-dessus de
   l'EMA 29.

Si un test échoue, ou pour ne dépendre que d'un comportement documenté : mettre l'indicateur
sur un graphique 5 secondes de la même mise en page et garder le 100 ticks pour le prix.

### 2.2 Les deux alertes

- **Probablement indisponibles sur le 100 ticks.** L'article d'aide de TradingView sur les
  intervalles en ticks indique que les alertes côté serveur n'y fonctionnent pas (lu par
  extraits, par deux relecteurs séparément). Test : ouvrir « Créer une alerte » sur le
  100 ticks et voir si les deux conditions sont proposées.
- **Sur un graphique en temps**, les réglages par défaut n'acceptent que 1 s ou 5 s : à partir
  de 10 s le script s'arrête sur son propre message (l. 56).
- **Sur un graphique 1 s ou 5 s**, l'alerte part à la clôture de la bougie du graphique qui
  affiche le nouvel état : environ 1 s ou 5 s après l'affichage en marché actif, davantage en
  marché calme.
- **Elles sonnent souvent** : voir § 3.2.

### 2.3 Autres points propres aux ticks

- **Les deux EMA tracées sont celles des barres de 100 ticks** (l. 146-149). Elles ne
  correspondent à aucune ligne du tableau et peuvent se croiser à contresens. Le réglage
  s'appelle pourtant « sanity check » (l. 39) et il est coché par défaut.
- **Après un rechargement, l'historique peut être décalé d'une barre de 100 ticks par rapport
  au direct** (hypothèse, comportement non documenté). Sans effet sur les tableaux, qui ne
  lisent que la dernière barre.
- **Échauffement** : les six tendances dépendent encore du point de départ de l'historique
  pendant 40 à 140 bougies de leur unité ; toute la colonne Qualité attend 114 bougies de 30 s
  (57 min), parce qu'elle attend l'ATR relatif (l. 238) ; la structure 3 min demande 1 h 30 de
  bougies en médiane, jusqu'à 4 h 30. Si TradingView charge la profondeur habituelle, tout est
  rempli dès le chargement. Test : recharger marché ouvert, « Explication » ne doit pas
  afficher « Prechauffage / volume ».
- **Option « Chart »** dans une liste d'unités de temps, sur le 100 ticks : résultat inconnu
  (l. 47-49, 192-193). À ne pas utiliser.

## 3. Premier tableau : six tendances et Qualité

### 3.1 « FULL BULL / FULL BEAR » n'est pas rare et ne prouve pas une tendance

- **Sans aucune tendance** (marche aléatoire simulée), l'un des deux est affiché 38 à 40 % du
  temps. Cinq émulations indépendantes, dont la mienne, donnent le même chiffre.
- **Les six lignes ne sont pas six confirmations.** C'est le même calcul sur six unités
  emboîtées du même prix. Corrélation entre lignes voisines : 0,78 à 0,91 ; entre 5 s et
  1 min : 0,23. Cela vaut environ deux avis indépendants. En pratique deux lignes décident :
  quand la 5 s et la 1 min sont haussières, le verdict est FULL BULL 86 % du temps.
- **La ligne 45 s n'apporte presque rien** : quand 30 s et 1 min sont d'accord, elle dit la
  même chose 97,6 % du temps.
- **La case Verdict est verte ou rouge 54 à 55 % du temps sans tendance**, parce que « Strong »
  (5 sur 6) a la même couleur que FULL (l. 270-271).
- **Avec une tendance simulée**, FULL BULL monte à 29 %, 39 % et 64 % du temps selon sa force.
  L'information existe, mais l'écart entre « pas de tendance » et « tendance modérée » n'est
  que du simple au double.

Lecture juste : FULL BULL = « la minute est haussière et aucun repli n'est en cours sur les
unités courtes ».

### 3.2 Les alertes sonnent souvent

Mesuré sur graphique 1 s émulé, sans tendance :

- environ 12 alertes par heure et par sens ;
- épisodes FULL de 30 s en médiane, 1 min en moyenne ; 30 % durent 10 s ou moins ;
- 41 % des alertes arrivent 10 s ou moins après la fin de l'empilement précédent du même
  sens : c'est la ligne 5 s qui sort puis revient ;
- environ 4 alertes par heure et par sens suivent une absence d'au moins 60 s.

### 3.3 Retard après un retournement

Après un retournement en V régulier, chaque ligne bascule environ 16 bougies de sa propre
unité après le sommet : 80 s pour la ligne 5 s, 8 min pour la 30 s, 16 min pour la 1 min.

- Le FULL existant disparaît vite : 53 s en médiane, par la ligne 5 s.
- Le FULL opposé arrive avec la ligne 1 min : environ 16 min après le sommet.
- Passage d'un range à une tendance : premier FULL après 2 min 30 à 5 min selon la pente,
  quand il n'était pas déjà affiché par hasard (ce qui arrive une fois sur cinq).

C'est le retard normal d'un croisement EMA 11 / 29 lu en bougie clôturée.

### 3.4 Mots du tableau qui disent autre chose que le calcul

- **« FLAT »** (l. 127) : avec la bande neutre à 0, réglage par défaut, il ne veut jamais dire
  « plat ». Il s'affiche quand le croisement des EMA et la clôture sont en désaccord : repli ou
  début de retournement. Chaque ligne l'affiche 16 % du temps.
- **« Strong »** : 5 sur 6, même couleur que FULL, alors que la sixième ligne est opposée 16 %
  du temps.
- **« Lean »** : couvre de 1 contre 0 à 4 contre 2 et reste gris. Or le second tableau traite
  4 contre 0 ou 1 comme un sens (l. 417).
- **« No Resonance »** : presque toujours un conflit 2 contre 2 ou 3 contre 3.
- **« TF 1-3 », « TF 4-6 »** : « BULL (2/1) » veut dire 2 lignes haussières, 1 baissière. Rien
  ne vérifie que les six unités sont saisies de la plus courte à la plus longue.

### 3.5 Colonne Qualité

- **« Conf. 1m : OK (close) » s'affiche 37 à 38 % du temps sans aucune tendance.** Les seuils
  18 et 0,20 sont au niveau du bruit : sur une marche aléatoire, l'ADX médian vaut 22 et l'ER
  médian 0,19. Le filtre écarte bien les ranges serrés (OK 1 % du temps) et laisse passer les
  tendances nettes (95 %). Entre les deux il trie peu.
- **« OK » ne dit rien de la force du 30 s affichée juste au-dessus.** Il teste le sens du
  30 s contre celui de la minute, puis l'ADX et l'ER de la minute seulement (l. 243). Dans
  35 % des « OK » sur bruit, le 30 s ne passe pas lui-même les deux seuils. Les cases ADX et
  ER ne changent jamais de couleur.
- **« NON / faible » mélange deux causes** : sens opposé (environ un cas sur quatre) et force
  insuffisante. Les valeurs de la minute ne sont affichées nulle part.
- **Retard** : après le début d'une tendance nette, « OK » apparaît au bout de 7 min en
  médiane ; après sa fin, il reste 9 min 30. Après un retournement il valide encore l'ancien
  sens : dans un marché simulé qui s'inverse toutes les 20 min, 43 % des « OK » pointent
  contre le mouvement en cours.
- **Le CHOP n'est pas seulement informatif.** Il ne touche pas aux deux alertes, comme le dit
  l'en-tête (l. 6). Mais il entre dans le verdict de confluence (l. 418 et 427) : un CHOP à
  61,8 ou plus interdit « CONFLUENCE ». Son poids propre est faible, environ 1 point de temps.
- **Zones du CHOP sur du bruit** : HACHE 9 %, TENDANCE 18 %, TRANSITION 73 %. « TENDANCE » ne
  donne aucun sens. La part de HACHE dépend surtout du bruit à l'intérieur des bougies : elle
  monte en marché lent.
- **« ATR relatif »** : 1,00 = moyenne des 100 dernières bougies de 30 s, soit 50 min. À
  volatilité constante il reste entre 0,90 et 1,11 : un écart de moins de 10 % est du bruit.
- **Après un gros gap de réouverture** (week-end, changement de contrat), le CHOP affiche une
  fausse « TENDANCE » pendant 13 bougies de 30 s et l'ATR relatif est gonflé. Une réouverture
  quotidienne ordinaire ne produit presque rien.
- **Arrondis aux seuils** : on peut lire « 0.20 » pour un ER de 0,196 qui échoue au test
  (0,9 % des lectures).

## 4. Second tableau : Structure et Confluence

### 4.1 « CONFLUENCE » est rare et brève ; le tableau est orange presque tout le temps

Sans tendance (simulation) :

| Verdict | Part du temps |
|---|---|
| CONFLUENCE (▲ et ▼) | 1,2 à 1,9 % |
| CONTRADICTION | 40 à 42 % |
| PARTIELLE | 56 à 58 % |

- Un épisode de confluence dure 80 s en médiane (2 min 40 en moyenne) ; 4 à 5 épisodes par
  sens et par séance de 23 h.
- Le verdict change environ 25 fois par heure et l'explication 42 fois : il dépend à chaque
  instant des lignes 5 s à 15 s et de la qualité 30 s, sans mémoire.
- « CONTRADICTION » et « PARTIELLE » ont le même orange (l. 454).

Treize conditions doivent être vraies en même temps (l. 417-431) : au moins 4 lignes sur 6 dans
le sens et au plus 1 contre, sens du DMI 30 s, ADX et ER du 30 s, CHOP, sens, ADX et ER de la
minute, structure 1 min, structure 3 min, VWAP, prix au-delà du dernier pivot 1 min, espace
d'au moins 20 points.

### 4.2 Sans niveau connu devant le prix, la confluence est impossible

C'est le point de conception le plus important du second tableau.

- Pour une confluence haussière, la l. 423 exige que la dernière clôture 1 min soit au-dessus
  du dernier pivot haut 1 min. Ce pivot ne peut donc jamais être la « référence au-dessus ».
  Il reste le pivot haut 3 min et le plus haut de la veille.
- Si le prix est au-dessus des deux, « Ref. au-dessus » affiche « N/A (inconnu) », « Espace »
  affiche « N/A », et le verdict reste « PARTIELLE » avec « Obstacle proche/inconnu » (l. 426).
  **Le tableau ne peut pas afficher « CONFLUENCE ▲ » sur de nouveaux plus hauts au-dessus du
  plus haut de la veille.** Miroir à la baisse.
- L'infobulle du réglage d'espace l'annonce (l. 336) : « une absence de niveau connu ne prouve
  pas qu'un passage est libre ». C'est un choix prudent, pas une erreur. Mais la case reste
  grise et le texte confond « obstacle proche » et « aucun niveau connu ».

Mesures en simulation :

- 92 % du temps passé en « CONFLUENCE ▲ », la référence au-dessus est « H veille ».
- Au-dessus du plus haut de la veille, « CONFLUENCE ▲ » est 37 fois plus rare qu'à l'intérieur
  du range, et le tableau y affiche environ 5 fois plus de « CONFLUENCE ▼ » que de « ▲ ».
- Quand tous les autres critères sont réunis, la confluence est refusée faute de niveau connu
  dans 26 à 42 % des cas sans tendance, et dans 60 % des cas avec une tendance légère.
- **Plus la tendance simulée est propre, plus la confluence est rare** : 0,1 à 0,3 % du temps
  pendant une hausse d'une heure, contre 1,2 à 1,9 % sur du bruit. Pendant cette hausse le
  tableau écrit « CONTRADICTION » 42 à 68 % du temps, parce que la structure 3 min affiche
  encore l'état d'avant.

### 4.3 Le critère « BOS » ne fait pas ce que dit son commentaire

- Le commentaire (l. 421-422) dit que le prix doit rester du bon côté du niveau « déjà connu au
  moment de la cassure ». Le code compare au **dernier** pivot 1 min confirmé (l. 423-424), qui
  peut être plus récent que la cassure.
- Un pivot haut est toujours au-dessus de la clôture qui le confirme. Chaque nouveau pivot
  haut, environ 3 min après un sommet local, éteint donc le critère jusqu'à ce que le prix
  clôture au-dessus.
- Le critère revient à : « dernière clôture 1 min au-delà du dernier pivot 1 min confirmé ».
  Avec un sens défini il est vrai 51 % du temps.
- Les deux réglages « BOS récent » (20 et 8 bougies) n'ont presque aucun effet : les passer à
  300 et 100 change la part de confluence de 1,57 % à 1,58 %.
- L'explication « BOS non confirme/recent » peut s'afficher alors que la ligne « Dernier BOS »
  montre un BOS récent en vert.

### 4.4 « Structure » : deux derniers sommets, deux derniers creux, sans le prix

- La structure compare les deux derniers pivots hauts confirmés et les deux derniers pivots bas
  (l. 375-376). Rien n'impose qu'ils alternent, rien ne limite leur âge, et le prix actuel
  n'entre pas dans le calcul.
- « HH + HL ▲ » peut rester vert alors que la dernière clôture 1 min est déjà sous le dernier
  pivot bas : 15 à 16 % du temps en simulation.
- C'est le critère le plus sévère : avec un sens défini, les structures 1 min et 3 min sont
  toutes deux alignées 14 à 16 % du temps. Sans lui la confluence occuperait 7,5 % du temps.
- Âge de l'information en 3 min : le pivot le plus récent a 19 min en médiane, le plus ancien
  des quatre 72 min. Le tableau dit « (CLOSE) », pas l'âge.

### 4.5 Les distances partent de la dernière clôture 1 minute, pas du prix en cours

- « Ref. au-dessus », « Ref. en-dessous », « Espace sens MTF », l'écart au VWAP et le test du
  pivot utilisent la clôture de la dernière bougie 1 min terminée (l. 400-414), vieille de 0 à
  60 s.
- Écart entre ce prix et le prix en cours, à volatilité de séance simulée : 5 points en
  médiane, 10 à 15 points une fois sur dix. Le seuil d'espace n'est que de 20 points.
- La référence affichée « au-dessus » est déjà franchie par le prix en cours 7 à 8 % du temps.
- **« ACHAT x pt » / « VENTE x pt »** (l. 456) se lit comme un ordre et un objectif. C'est
  seulement la distance à la prochaine référence dans le sens des six lignes. Le mot est
  affiché 70 % du temps sans aucune tendance.
- Un niveau exactement égal à la clôture est ignoré (comparaisons strictes, l. 404 et 407) :
  le tableau affiche alors le niveau suivant, plus loin.

### 4.6 Âge des cassures

- **Compté en bougies, pas en temps** (l. 377) : bougies de 1 min ou de 3 min, pas barres de
  100 ticks. « 8b » sur la ligne 3 min veut dire 24 minutes.
- **La pause de 17 h à 18 h (New York) et le week-end ne font pas vieillir une cassure.** Une
  cassure 1 min du vendredi 16 h 45 reste « récente » jusqu'au dimanche 18 h 07.
- **Chaque nouveau franchissement du même niveau recrée une cassure** et remet l'âge à zéro
  (l. 358-365) : 23 % des cassures haussières en simulation.

### 4.7 La case « Explication »

- Elle ne nomme que le premier critère manquant, dans un ordre fixe (l. 455). Quand elle
  affiche « Qualite / CHOP / confirm. », un autre critère manque aussi dans 96 % des cas.
- « VWAP non aligne » ne peut pratiquement jamais s'afficher : un prix du mauvais côté du VWAP
  est déjà pris par « Structure / VWAP oppose ». 0 fois sur toutes les simulations.
- « PARTIELLE » s'affiche aussi quand aucun sens n'existe : la moitié des « PARTIELLE » vont
  avec « MTF non tranche ».
- Toute donnée manquante donne le même texte « Prechauffage / volume », sans dire laquelle.

### 4.8 VWAP et veille

- **« VWAP jour »** repart de zéro au changement de jour du contrat, probablement 18 h New York.
  À 9 h 30 il contient déjà 15 h 30 de nuit. Ce n'est pas un VWAP de séance cash ; le
  commentaire du code le dit (l. 326-327, 378), pas le tableau.
- **« H veille / B veille »** : plus haut et plus bas de la séance complète précédente, nuit
  comprise (probable).
- **Premières minutes après 18 h** : pendant la première minute le tableau compare encore la
  clôture et le VWAP de la séance précédente. Ensuite le VWAP repose sur 1 à 3 bougies et le
  prix change de côté 36 à 45 % du temps d'une minute à l'autre. À ne pas lire le premier
  quart d'heure.
- **Sous le VWAP** le texte est « EN-DESSOUS -12.5 pt », avec un signe moins en trop (l. 452).

## 5. Commentaires qui ne correspondent plus au code

Aucun ne change un calcul.

- l. 2-3, 162, 258 : « tableau unique », « une SEULE table ». Le script en crée deux (l. 259,
  448).
- l. 6 : « le CHOP est informatif ». Vrai pour les deux alertes, faux pour la confluence (§ 3.5).
- l. 39 : « sanity check » pour deux EMA qui ne vérifient aucune ligne du tableau (§ 2.3).
- l. 54 : le message d'erreur cite « 5, 15, 60, 240, D, W » alors que les réglages par défaut
  sont en secondes.
- l. 56 : le message recommande « the 100T chart », cas que la documentation ne décrit pas.
- l. 72-73 : « documented non-repainting HTF pattern ». Documenté pour une unité supérieure à
  celle d'un graphique en temps, pas pour un graphique en ticks.
- l. 184-185 : « Min ADX / Min ER pour confirmation ». Les mêmes seuils servent aussi au 30 s
  dans la confluence (l. 427).
- l. 288 : l'en-tête « 30s (close) » coiffe aussi « Conf. 1m », « TF 1-3 » et « TF 4-6 ».
- l. 421-422 : commentaire du critère BOS (§ 4.3).

## 6. Cas particuliers

- **Marché arrêté ou flux figé** : les deux tableaux gardent couleurs et verdict du dernier
  tick, sans heure ni signe de péremption (l. 260, 449).
- **Contrat continu NQ1!** : le jour du changement de contrat, « H / B veille », les pivots en
  mémoire, les moyennes et le VWAP mélangent deux contrats de prix différents, sauf ajustement
  activé sur le graphique. Pas de problème sur un contrat daté comme NQZ2026.
- **Jours fériés CME** : le découpage du « jour » par TradingView n'a pas été vérifié. Le VWAP
  pourrait cumuler deux séances.
- **Bande neutre** (l. 23) : un seul cran (0,05 %) vaut environ 12 points d'écart entre les
  deux EMA sur le NQ. Presque toutes les lignes courtes passent alors en « FLAT ». Réglage à 0
  par défaut : sans effet tant qu'on n'y touche pas.
- **Graphique en temps de plus d'une minute** : les unités 1 min, 3 min et jour de la structure
  sont fixes et ne sont pas contrôlées (l. 387-389). Hors de ton usage.
- **Deux tableaux au même endroit** : « Top Left » et « Bottom Left » existent dans les deux
  listes de position. Par défaut ils ne se recouvrent pas.
- **Symbole sans volume** : « VWAP jour » affiche « N/A (volume) » et la confluence reste N/A ;
  le premier tableau n'est pas touché.

## 7. Charge

Légère à moyenne.

- 11 demandes sur 8 unités distinctes : la minute est demandée trois fois (l. 83, 235, 387), le
  30 s deux fois (l. 81, 233).
- À chaque tick : 58 cellules de tableau réécrites (36 + 22), dont 29 ne changent jamais, et 4
  tableaux de valeurs recréés (l. 85-86, 398-399). Les 29 autres cellules ne peuvent changer
  qu'à la clôture d'une bougie demandée, au plus toutes les 5 s.
- Calculé pour rien : l'ATR relatif de la minute et le VWAP 3 min (`cv`, `unusedConfirmChop`,
  `srPrice3`, `srVwap3`, l. 235 et 388).
- Aucun dessin qui s'accumule, boucles de 6 tours au plus.
- Pour comparaison, le BTM Cockpit réécrit environ 290 cellules par tick.

Le coût réel sur le 100 ticks ne peut pas être mesuré ici. Test : Profiler de l'éditeur Pine, à
l'ouverture de New York.

## 8. À vérifier sur TradingView

1. Compilation, et la présence d'un avertissement orange à la l. 229.
2. Les trois tests du § 2.1 (horloge, graphique 30 s, graphique 1 min).
3. « Créer une alerte » sur le 100 ticks : les deux conditions sont-elles proposées ?
4. Rechargement marché ouvert : aucune case N/A, pas de « Prechauffage / volume ».
5. Un jour où le NQ fait de nouveaux plus hauts au-dessus du plus haut de la veille avec les
   six lignes haussières : « Ref. au-dessus : N/A (inconnu) » et jamais « CONFLUENCE ▲ ».
6. Pendant une « CONFLUENCE ▲ » : environ 3 bougies 1 min après le dernier sommet local, le
   verdict repasse à « PARTIELLE » avec « BOS non confirme/recent » alors que « Dernier BOS 1m »
   est encore vert.
7. Vers 18 h 05 New York : l'âge du dernier BOS n'a pas bougé pendant la pause ; l'écart au
   VWAP repart près de zéro.
8. Sur une période que tu juges sans direction : compter la part de « FULL » et de
   « Conf. 1m OK ». Si elle dépasse un tiers, les chiffres simulés se confirment sur le NQ.

## 9. Corrections possibles, de la plus petite à la plus grande

Aucune n'est compilée. Le fichier collé n'est pas modifié. Une version corrigée serait un
fichier à part, sur demande.

| Point | Correction | Taille |
|---|---|---|
| Signe sous le VWAP (§ 4.8) | l. 452, branche EN-DESSOUS : `str.tostring(math.abs(srVwapGap), "#.0")` | 1 mot |
| « ACHAT / VENTE » (§ 4.5) | l. 456 : « HAUSSE » et « BAISSE » | 2 mots |
| « FLAT » (§ 3.4) | l. 127 : « NEUTRE – » | 1 mot |
| Texte BOS (§ 4.3) | l. 455 : « Prix pas au-dela du pivot 1m » ; commentaire l. 421-422 | 1 texte |
| Niveau inconnu ou proche (§ 4.2) | l. 455 : `not srRoomOK ? (na(srRoom) ? "Aucun niveau connu devant" : "Obstacle proche")` | 1 ligne |
| EMA tracées (§ 2.3) | l. 39 : décoché par défaut, ou titre « EMA des barres du graphique » | 1 mot |
| Commentaires (§ 5) | l. 2-3, 6, 162, 258 | texte |
| « NON / faible » (§ 3.5) | l. 277, fin de ligne : `cAgree ? "OK (cloture)" : qDirection == 0 or cDirection != qDirection ? "NON (sens)" : "FAIBLE " + str.tostring(ca, "#.0") + " / " + str.tostring(ce, "#.00")` | 1 ligne |
| Cases ADX et ER sous les seuils (§ 3.5) | l. 297 : `bgcolor = qReady and qa < mqAdxNoisy ? COLOR_WARNING : rowBg` ; l. 301 de même avec `qe < mqErNoisy` | 2 lignes |
| Niveau au prix ignoré (§ 4.5) | l. 404 : `>=` ; l. 407 : `<=` | 2 signes |
| Bande neutre (§ 6) | l. 23 : `step = 0.005` | 1 mot |
| Âge des cassures en minutes (§ 4.6) | mémoriser l'heure de la cassure au lieu de l'indice (l. 355, 362, 365, 377), comparer en minutes (l. 419-420, 465, 467), afficher « min » (l. 440) | 8 lignes |
| Alertes moins fréquentes (§ 3.2) | exiger une absence de N bougies avant de sonner de nouveau | quelques lignes |
| Confluence sans niveau connu (§ 4.2) | l. 426 : `bool srRoomOK = srMtfDir != 0 and (na(srRoom) or srRoom >= srMinRoom)` | changement de règle |
| Structure 3 min (§ 4.2, 4.4) | l. 428 : exiger « pas opposée » au lieu de « alignée » | changement de règle |

Les deux dernières changent ce que « CONFLUENCE » veut dire. Effet simulé de l'avant-dernière :
la part de temps en confluence passe de 1,6 % à 2,8 % sans tendance. Elles sont à décider, pas à
appliquer d'office.

Réglage sans toucher au code : monter « Min ADX » vers 25 et « Min ER » vers 0,30 divise par
deux les « OK » sur du bruit (19 % au lieu de 38 %). Mais ces deux seuils servent aussi à la
confluence, qui devient alors nettement plus rare.
