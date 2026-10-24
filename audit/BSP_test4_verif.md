# BSP test4 — vérification (24/10)

Fichier : `src/test/BSP_test4.pine` (commit 4634496), reconstruit à partir du test3
vérifié (`audit/BSP_test3_verif.md`) et des zones que le fichier collé modifie ;
l'en-tête d'historique n'est pas recopié. 32 réglages. Pine non compilé ici.
Différence avec le test3 : le bord vivant revient par défaut, et son code change.

## Ce qui change par rapport au test3

| | Changement | Identique ? | Gain par tick en direct |
|---|---|---|---|
| — | « Calculer » et « Dessiner le bord vivant » cochés par défaut | Image du test3 bord allumé = image installée | — |
| 1 | Base de numéro et premier rang du bord calculés seulement sans clôture connue | Oui, prouvé | 0 : en direct la clôture n'est jamais connue |
| 2 | Recherche dans la réserve sautée si son dernier élément ne peut pas battre le tableau propre | Oui, prouvé (réserve triée par numéro et heure) | ≈ 1 lecture de tableau |
| 3 | Lectures du repli du bord seulement quand il sert | Oui, prouvé | 2 lectures de tableau |
| 4 | Objets créés seulement si calcul et dessin cochés, couleur transparente `hiddenColor` | Oui (alpha 100 partout, x = 0 à la création) | — |
| 5 | Mémoire de couleur `var` : `set_color` sauté si la couleur voulue est déjà appliquée | Oui sous le retour en arrière documenté ; voir ci-dessous | 9 → 4 appels de dessin sur un tick stable ; les 4 `set_xy` restent |

Côté serveur, le total est de l'ordre de quelques microsecondes par tick. Côté
navigateur, les deux lignes du bord bougent toujours à chaque tick : une mise à jour
de dessin part toujours. Au mieux 3 petits objets en moins par mise à jour, soit
10 à 30 µs ; zéro si TradingView renvoie tout le dessin. Rien de mesurable face aux
blocages de 358 à 388 ms.

## La mémoire de couleur (5)

Le manuel v6 documente que les modifications d'un dessin `var` faites pendant une
exécution non confirmée sont annulées avant l'exécution suivante, en même temps que
les variables `var`. Mémoire et objet partent de la même couleur, sont écrits
ensemble, annulés ensemble : un appel n'est sauté que si l'objet a déjà la bonne
couleur. Modèle : ≈ 915 000 événements simulés, 0 écart avec l'opt2.

Ce que le manuel ne dit pas : ce que le navigateur reçoit. Si TradingView
n'envoyait que les appels effectués sans repousser l'annulation, le test4 laisserait
à l'écran une couleur périmée (exemple minimal : tick 1 vert, tick 2 gris, le test4
garde le vert). L'opt2 et le test3, qui réappliquent tout à chaque tick, sont sûrs
dans tous les cas. Deuxième dépendance : `==` sur les couleurs doit comparer la
transparence.

## Autres points

- Compilation : rien de bloquant. Le paramètre `second` de `edgeSameColor` porte le
  nom d'une variable intégrée ; avertissement possible, à renommer (`colorA`,
  `colorB`).
- Hérité du test3 : recherches natives (sonde à passer), chiffre opposé sombre
  (choix de l'utilisateur), réserve certifiée et moteur (identiques).
- Mise à jour en place d'une instance du test3 : les cases « bord » enregistrées
  décochées peuvent rester décochées ; vérifier la section 6.

## Sonde

`src/test/sonde_test4.pine` vérifie en une minute sur un graphique en direct :
recherches natives, égalité des couleurs avec transparence, et que la couleur d'un
dessin changée sur un tick revient bien au tick suivant dans le navigateur. Trois
« OK » et une étiquette dont la couleur suit toujours son texte : le test4 est sûr.

## Verdict

- Image : identique à la version installée, hors chiffre opposé sombre et nom.
- Lag : aucun changement attendu par rapport à la version installée.
- Deux dépendances non vérifiées sur TradingView, pour un gain invisible : (c) et (5).
- Deux options propres : passer la sonde, ou demander à l'autre assistant de retirer
  (5) et (c) ; le test4 devient alors identique par preuve.
