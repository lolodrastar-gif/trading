# LOLO 2 — Regime v0.3 (tableau seul) — vérification (02/11)

Fichier : `src/lolo2/LOLO2_regime_v0.3.pine` (commit 957c5dc), collé tel quel.
Pine non compilé ici : trois relectures indépendantes contre le manuel v6 local,
un modèle Python de l'automate de régime, puis une relecture adverse de chaque
trouvaille (20 points, 4 retirés).

## Verdict

Aucune erreur de compilation ni d'exécution trouvée. L'automate fait ce que les
commentaires promettent : entrée après `enterBars` clôtures candidates consécutives,
retour à NEUTRE après `exitBars` clôtures non candidates consécutives, jamais de
passage direct HAUSSIER ↔ BAISSIER, états figés en clôture, une alerte par
changement.

Vérifié mécaniquement (`scratchpad/lolo2/work/model_lolo2.py`) :
- Kaufman ER : fenêtres alignées, valeur toujours dans [0, 1], 64 000 barres de
  marche aléatoire sans écart avec la définition ;
- automate : les 531 441 suites de 12 clôtures {haussier, baissier, rien} pour
  11 couples (`enterBars`, `exitBars`) — 0 violation ;
- `becameUp/Down/Neutral` : exactement une fois par transition, jamais sur un tick
  non confirmé, avec le retour en arrière des `var` modélisé.

## Ce qui peut ressembler à un bug sans en être un

| Ligne | Ce qu'on voit | Pourquoi | Correction (facultative) |
|---|---|---|---|
| 126-130 | `.31 / .25`, `-.35` : pas de zéro devant la virgule | Le manuel (strings.md) : le jeton `#` n'affiche un chiffre de tête que s'il est non nul. `"#.00"` sur 0,31 donne `.31`. Non confirmé sans compiler | `"0.0"` et `"0.00"` à la place de `"#.0"` et `"#.00"` |
| 104 | NEUTRE avec « Qualite OK » | En NEUTRE, le diagnostic ne regarde que ADX/ER ; il ne dit pas que c'est le **sens** (EMA, clôture, pente, DI) qui manque | ajouter une branche « Sens absent » avant `qualityOK ? ...` |
| 80-81 | Un retournement ne passe qu'**une seule bougie** en NEUTRE | Les compteurs `upStreak/downStreak` tournent aussi pendant un régime. Avec 2/2 : 3 clôtures baissières suffisent (2 pour sortir, 1 pour entrer) ; une ré-entrée du même côté demande 2 clôtures fraîches | mettre `upStreak := 0` et `downStreak := 0` aux lignes 96 et 101 si on veut `enterBars` clôtures fraîches après NEUTRE |
| 119-121 | Le tableau a une bougie de retard | Voulu : il n'affiche que des valeurs confirmées en clôture. Sur du 10 ticks, les bougies se ferment en quelques secondes | aucune |
| 134-137 | Graphique écrasé (bougies plates) | Seulement si l'un des quatre tracés a été coché dans Style : il revient alors dans le volet et partage l'échelle du NQ. Tels quels, les tracés limités à la fenêtre de données ne touchent pas l'échelle | décocher dans Style, ou `scale = scale.none` dans `indicator()` |
| 139-141 | Alerte qui s'arrête | Limite TradingView : 15 déclenchements en 3 minutes. Sur du 10 ticks avec 2/2, un régime peut changer toutes les 2 bougies | créer l'alerte en « Une fois par clôture de barre » ; monter 2/2 si ça sature |
| 92-101 | Un régime qui ne lâche pas | Hystérésis sans limite d'âge : une clôture candidate toutes les `exitBars` bougies suffit à le tenir | aucune, c'est la nature du filtre |
| 2-3 | En-tête « v0.2 » | Commentaire non mis à jour | mettre v0.3 |

Points retirés par la relecture adverse : la lecture « non confirmée » de la dernière
bougie au chargement (faux : `barstate.isconfirmed` y est faux, le tableau garde la
dernière clôture), les bordures du tableau, le décalage de départ des EMA sur
graphique en ticks, et la recommandation « Une fois par clôture de barre » comme
obligation (c'est équivalent ici, mais c'est le choix le plus sûr).

## À faire si « ça bug » encore

Dire ce qui est vu : tableau figé sur NEUTRE, chiffre sans zéro, alerte qui ne
part pas, graphique écrasé, message rouge dans l'éditeur. Chacun renvoie à une
ligne du tableau ci-dessus.
