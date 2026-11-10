# LOLO 2 — Filtre CHOP/ATR v0.2 : ce qui change et ce qui a été vérifié (10/11)

Fichiers : `src/lolo2/LOLO2_filtre_chop_atr_v0.1.pine` (collé tel quel) et
`src/lolo2/LOLO2_filtre_chop_atr_v0.2.pine` (131 lignes). Pine v6, non compilé ici.
Trois relectures indépendantes (compilation et sémantique de la plateforme ; modèle
différentiel v0.1 / v0.2 ; critique de conception), cinq contre-relectures adverses, puis
un contrôle final sur le fichier définitif. Aucun défaut trouvé dans la v0.2.

## 1. Ce qui ne change pas

- Le calcul : CHOP = 100 × log10(somme des True Ranges / plage High-Low) / log10(N),
  ATR, ATR / stop. Lignes identiques à la v0.1.
- Le verdict : ROUGE si CHOP ≥ seuil rouge ou ATR/stop ≥ seuil danger ; VERT si ni l'un ni
  l'autre et CHOP < seuil vert et ATR/stop < seuil vigilance ; ORANGE sinon. Aucune
  confirmation sur plusieurs clôtures, comme la v0.1.
- Les 7 réglages d'origine : mêmes positions, titres, défauts, bornes et groupes (texte
  identique ligne à ligne). Les 3 nouveaux sont à la fin.
- Le tableau : un seul, créé une fois, actualisé à la clôture ; mêmes couleurs.

## 2. Ce qui est corrigé

| Défaut de la v0.1 | v0.2 |
|---|---|
| Format `"#.1"` pour l'ATR et le stop : « 1 » n'est pas un caractère de format documenté, le résultat affiché n'est pas garanti | `"0.0"` pour l'ATR, `"0.##"` pour le stop (affiché tel que saisi, deux décimales au plus) |
| Format `"#.0"` : perd le zéro devant la virgule sous 1 (« .5 ») | `"0.0"` |
| Seuils inversés (vert au-dessus de rouge, vigilance au-dessus de danger) : la zone orange disparaissait sans rien dire | pas de verdict, « Seuils inverses / REGLAGES » en gris, tant que les seuils ne sont pas remis dans l'ordre (des seuils égaux restent acceptés) |
| Marché plat sur toute la période : « Historique insuffisant » | « Marche plat » |
| « -- » sur les trois valeurs dès qu'une seule manquait | chaque valeur disponible est affichée |
| ORANGE : « Conditions mixtes », sans dire quelle mesure retient le verdict | « CHOP moyen », « ATR en vigilance » ou « CHOP + ATR moyens » |
| « UT 1 » | « UT 1 min », « UT 1 h », « UT 30 s » |

## 3. Ce qui est ajouté, pour vérifier le filtre sur l'historique

- Fenêtre de données : CHOP, ATR / stop (%) et code du verdict (2 vert, 1 orange, 0 rouge,
  −1 indisponible), bougie par bougie. Rien n'est tracé sur le graphique.
- Fond coloré selon le verdict, option décochée par défaut ; chaque bougie prend sa
  couleur à sa clôture, jamais avant.
- Deux alertes : passage au ROUGE, passage au VERT, à la clôture seulement, avec le
  symbole et l'unité de temps dans le message.
- Taille et position du tableau, mêmes noms que le tableau LOLO 2 / TENDANCE (les deux
  sont en haut à droite par défaut).

Charge : 6 sorties sur 64 (3 valeurs, 1 fond, 2 alertes ; la v0.1 en avait 0), 12
écritures de cellule par bougie close comme la v0.1, aucune boucle, aucune requête, aucun
objet accumulé.

## 4. Vérification

- **Compilation** : aucune erreur ni avertissement prévu. Chaque appel correspond à une
  signature du manuel v6 ; contrôle statique du fichier final : 0 problème (noms,
  signatures, parenthèses, indentation, identifiants). Ce n'est pas une compilation.
- **Verdict identique à la v0.1** : modèle de la relecture, réglages par défaut, 600 000
  bougies simulées : 0 différence de verdict ; 386 réglages aléatoires à seuils dans
  l'ordre, 1,93 million de bougies : 0 différence de verdict. Les expressions ont aussi
  été évaluées mécaniquement à partir du texte des deux fichiers (960 000 évaluations,
  0 écart avec la transcription à la main).
- **Contrôle final sur le fichier définitif** (les deux fichiers lus mécaniquement,
  240 réglages × 4 000 bougies) : sur 472 000 bougies à seuils dans l'ordre, 0 différence
  de verdict ; la cause ne diffère que sur les bougies de marché plat (3 263) et en ORANGE
  (133 526, toutes conformes à une définition indépendante) ; code du verdict, fond et
  alertes conformes sur 960 000 bougies ; 488 000 bougies à seuils inversés : toutes
  « REGLAGES ».
- **Alertes** : une fois par entrée dans l'état, jamais sur la première bougie, jamais
  pendant un état indisponible.
- **Tableau** : dessiné dès le chargement (marché ouvert ou fermé), il montre la dernière
  bougie close entre deux clôtures.

## 5. Ce qu'il faut savoir (comportements hérités de la v0.1, non modifiés)

- **Pas de confirmation.** Quand le CHOP est proche de 38,2 ou 61,8, ou l'ATR/stop proche
  de 70 % ou 100 %, le verdict peut changer à des clôtures consécutives. Sur bougies
  simulées (pas des données NAS100) : 8 à 12 changements pour 100 bougies, 15 à 23 % des
  états ne durent qu'une bougie. Les alertes peuvent donc se répéter. À regarder d'abord
  sur l'historique réel avec le fond coloré. Une confirmation changerait le verdict : au
  modèle, une confirmation symétrique sur 2 clôtures laissait 7 à 40 % des clôtures
  rouges non affichées rouges ; si elle est ajoutée un jour, le ROUGE doit rester immédiat.
- **Un marché presque mort peut lire VERT.** Si une seule bougie porte toute la plage
  d'une période par ailleurs plate, le CHOP vaut 0 et l'ATR est petit : VERT. Le filtre n'a
  pas de plancher d'ATR. Sans effet en séance active.
- **Le CHOP peut dépasser 100** après un gap juste avant la fenêtre (le True Range du
  premier bar inclut le gap) : le verdict est alors ROUGE.
- **Seuils inversés** : la v0.2 n'affiche plus rien, pas même le ROUGE, jusqu'à
  correction. C'est voulu.
- **Les réglages 6 et 7 sont des ratios** (0,70 ; 1,00), le tableau affiche des
  pourcentages (70,0 %). « pts » suppose un symbole coté en points (NAS100, NQ).
- **Fenêtre de données sur la bougie en cours** : valeurs provisoires ; le tableau, lui,
  ne bouge qu'à la clôture.

Inconnu ici, à observer : ce que la v0.1 affichait réellement avec `"#.1"` ; l'instant
exact du premier affichage quand le script se charge marché ouvert, avant la première
mise à jour en direct (même règle que la v0.1) ; comment TradingView conserve les
réglages enregistrés quand on remplace le code.

## 6. À vérifier dans TradingView

1. Coller, enregistrer : pas de message rouge ; les 7 réglages gardent leurs valeurs ;
   « Tableau » et « Verification » apparaissent après.
2. Ajouter le Choppiness Index intégré (14) et l'ATR intégré (14, RMA) : sur une bougie
   close, la ligne « CHOP » de la fenêtre de données doit égaler l'intégré, et l'ATR du
   tableau celui de l'intégré.
3. Pendant une minute le tableau ne bouge pas ; il change à la clôture.
4. Mettre « CHOP favorable sous » à 70 : « Seuils inverses / REGLAGES » ; remettre 38,2.
5. Cocher le fond : bougies closes teintées, bougie en cours non ; décocher.
6. Ne pas cocher les trois lignes grises dans l'onglet Style (elles seraient tracées sur
   l'échelle des prix).
7. Alertes : condition « L2 FILTRE », « Passage au ROUGE » ou « Passage au VERT »,
   fréquence « Une fois par clôture de barre ».
8. Si les deux tableaux LOLO 2 se recouvrent, en déplacer un avec « Position ».

Scripts et résultats : `scratchpad/filtre/work/` (compile-sem, model, critic-design,
refute, final).
