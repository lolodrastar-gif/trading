# BSP v11.66 — lag de 22:00 : ce que dit le code, ce que dit le Profiler, et comment trancher (13/10)

Fichier audité : `src/BSP_v11.66.pine` (commit 6b050fe). Rien n'y a été modifié.
Fichiers de test : `src/test/BSP_v11.66_perf.pine` et `src/test/BSP_v11.66_perf_varip.pine` (§6).

Méthode : quatre relecteurs indépendants (coût serveur par exécution, charge poussée au navigateur, mécanique du moteur Pine, comportement spécifique à la rafale), chacun contredit par un sceptique. 48 trouvailles, aucune réfutée ; 20 reclassées, presque toujours pour ramener une affirmation sur les internes de TradingView au rang d'hypothèse. Tout ce qui suit distingue les FAITS (lus dans le code) des HYPOTHÈSES (internes de la plateforme, non documentés).

## 1. Les deux captures du Profiler

| Ligne | Code | Part |
|---|---|---|
| 2259 | `request.security_lower_tf(…)` | 33 % |
| 2242 | appel du moteur `bspEngine1T` (dans l'enveloppe) | 25,3 % |
| 2243-2249 | les sept lectures `[1]` de la traîne | ≈ 2,9 % |
| 3536 | `if barstate.isconfirmed` (bloc de fin) | 16,5 % |
| 3553 | `poolAbsorb(…)` (versement dans la réserve) | 15,7 % |
| (non montré) | tout le reste | ≈ 50 %, dispersé |

Ces parts sont **cumulées depuis le chargement du script**. Elles sont dominées par l'historique : 60 000 ticks du moteur et ~5 000 bougies versées dans la réserve, une fois. Elles sont presque identiques aux profils précédents pris au chargement (v11.52 : requête 43 %, moteur 33 %, bloc de fin 14 %). **Elles ne montrent rien de la rafale de 22:00**, et ne peuvent pas : le Profiler ne mesure que le code du script, pas ce que le moteur Pine fait entre deux exécutions (retour en arrière des `var`, livraison des quinze tableaux, envoi au navigateur), ni le navigateur.

Pour voir le coût de la rafale avec le Profiler, il faut un **delta** : survoler une ligne affiche son temps absolu et son nombre d'exécutions. Capture à 21:59, capture à 22:03, et lire la différence. Trois précautions, sans lesquelles la mesure est fausse :

1. Le Profiler instrumente la copie du script **ouverte dans l'éditeur Pine**. Si le BSP de ta bibliothèque est aussi sur le graphique, deux BSP tournent pendant la rafale : retirer l'autre avant de mesurer.
2. Ne jamais changer un réglage pendant la rafale : chaque changement recompile et rejoue tout l'historique (plusieurs secondes de charge, justement ce que le profil cumulé montre).
3. Avant de mesurer, réduire la part de l'historique dans le cumul : « Barres calculées » (réglages du script, section Calcul) au minimum, « Historique 1T demandé » à 20 000.

Lignes à lire dans le delta (nombre d'exécutions Δexec, temps Δt) :

- **2299** (`int count0 = …`, exécutée à chaque mise à jour) et **3539** (une fois par bougie) : Δexec(2299) / Δexec(3539) = **exécutions par bougie**. Toute l'analyse suppose ~10 (un tick 1T = une exécution). Si c'est moins, TradingView regroupe les mises à jour et tous les coûts « par tick » sont à diviser d'autant.
- **2318** (`isSorted` du tableau vivant) et **1742** (corps de sa boucle) : Δexec(1742) / Δexec(2318) = **éléments balayés par exécution**. Attendu ≈ 10. Si c'est des centaines, les tableaux vivants sont démesurés en rafale et cette ligne est le poste n° 1 (§2).
- **2259** moins **2242** moins **2243-2249** : coût de livraison des quinze tableaux par le moteur Pine.
- **3553** : versement, une fois par bougie ; et **1994** (boucle de purge) : une recopie de 6 000 éléments toutes les ~300 bougies, soit toutes les ~3 s en rafale.

## 2. Ce que le code fait à chaque tick en direct (faits)

Chemin courant d'une exécution en direct (bougie N+1 vivante, lecture différée de N, bord vivant) :

- 3 à 5 dichotomies sur la **réserve** (6 000 à 9 000 éléments → 13-14 pas chacune) : fenêtre de récupération (2516), base du bord (3254), plafond du bord (3289) ; plus deux sur le chemin « sans mesure » (reprise rafraîchie 2632, reprise du bord 3341).
- 8 à 10 dichotomies sur les **tableaux** de N et de N+1 (≈ 10 éléments → 4 pas).
- `isSorted` du **tableau vivant** (2318) : une boucle de `count0` itérations, non mémorisée (le tableau figé, lui, l'est depuis la v11.66). ≈ 10 en régime normal ; **plafonnée à 2 000**.
- `pickTrail` : ≤ 16 itérations, une ou deux fois.
- ~1 500 instructions scalaires, 4 `candidateValues`, ~57 variables `var` scalaires.
- 5 à 9 mises à jour d'objets de dessin du bord (lignes, étiquettes, remplissage).
- Une fois par bougie (exécution confirmée) : versement du tableau vivant (O(1) sur une bougie vide, ~10 ajouts en fin de réserve sur une bougie normale, une insertion au milieu seulement pour un tick en retard) ; purge de 6 000 recopies toutes les ~300 bougies.

Conclusions établies par les relecteurs et tenues par les sceptiques :

- **Rien ne croît avec la rafale** dans le travail propre du script : toutes les boucles sont bornées (2 000, 6 000, 16, 14), le versement est O(1) sur une bougie vide, aucune quadratique, aucun chemin d'erreur d'exécution ni de limite Pine (500 ms par boucle, nombre de dessins : 5 objets créés une fois).
- La lecture prolongée du direct (v11.66, 2399-2418) coûte 0 sur une bougie vide et au plus 3 dichotomies bornées sinon.
- Un tick 1T hors contexte, une bougie vide, un `time_close` na (toutes les bougies en direct) : chemins déjà prévus, pas de surcoût.
- Deux postes serveur perfectibles mais petits en régime normal : la lecture différée de N (2401-2493) est recalculée à l'identique à chacune des ~10 exécutions de N+1 (5 dichotomies, ~60 instructions) ; `isSorted` du tableau vivant est refait à chaque exécution. Les mémoriser exigerait des `varip` (règle de l'auteur : aucun). Gain nul sur l'écran.
- **Une seule hypothèse côté script** qui pourrait peser : si, à 22:00, TradingView range des centaines de ticks dans un tableau vivant (ce qui a été observé au chargement du 24/09, pas en direct), `isSorted` passe à jusqu'à 2 000 itérations par exécution. Le delta Δexec(1742)/Δexec(2318) le dit. Si c'est le cas : `SCAN_MAX` 2 000 → 256 (une constante, sorties identiques hors de ce régime ; en rafale, une bougie à plus de ~25 bougies d'un tableau démesuré perd sa récupération par la réserve).

**Ordre de grandeur** : quelques centaines d'opérations par exécution. Même à 1 000 exécutions par seconde, cela ne sature pas un serveur, et le Profiler cumulé (33 % pour la requête, 16 % pour le versement, le reste dispersé sous le pour cent) ne montre aucune ligne du corps du script qui pèse.

## 3. Ce que le code ne peut pas montrer (hypothèses, non mesurables ici)

| Poste | Nature | Ce que ça ferait |
|---|---|---|
| Retour en arrière de la réserve `var tickPool` (6 000-9 000 objets de 10 champs) avant chaque mise à jour en direct | Interne Pine, non documenté : copie complète (coûteux) ou journal des changements (nul) | Le BSP seul prend du retard ; les autres volets ne bougent pas |
| Livraison des 15 tableaux de `request.security_lower_tf` à chaque mise à jour | Interne Pine | Idem |
| Retour en arrière / validation des 5 objets de dessin | Documenté dans le principe, coût inconnu | Idem, plus un envoi au navigateur |
| Validation (commit) de ~300 séries et ~45 `var` à chaque bougie close : × 10 en rafale | Interne Pine, vaut pour tout indicateur | Idem |
| Envoi au navigateur : 16 « plot counts » (11 valeurs + 5 couleurs par bougie), remplissage coloré par bougie sur 1 000 bougies (`show_last`), 5 objets de dessin réécrits par 9 appels à chaque tick | Fait pour l'inventaire ; coût navigateur inconnu | **Tout l'onglet** ralentit : un seul fil d'exécution pour tous les volets |
| Les deux autres oscillateurs du layout, leurs remplissages ; le flux 10T lui-même à 100 bougies/s | Hors BSP | Idem |
| Rechargement en cascade : une reconnexion pendant la rafale recalcule TOUS les indicateurs ; le BSP seul coûte plusieurs secondes (60 000 ticks de moteur) | Hypothèse, aucune observation | Tout se fige puis se redessine depuis la gauche |

Point décisif, factuel : **un script lent côté serveur ne peut ralentir que son propre volet** — ses messages arrivent en retard, les autres indicateurs et le prix continuent. Si tout le setup se fige (« fait tout planter »), la cause est dans le navigateur (quantité de mises à jour à ingérer et dessiner, tous indicateurs confondus) ou dans un rechargement général, pas dans le temps de calcul du BSP. Le BSP y contribue par ce qu'il pousse (plus qu'un indicateur simple : un `plot(close)` pousse 1 série, le BSP 16 plus 5 dessins), pas par ce qu'il calcule.

## 4. Protocole de test — trois fenêtres par soir : 21:50, 21:55, 22:00 (Paris)

Préparation, une fois :

- Vérifier qu'aucun **BSP Diag** ni ancienne version n'est chargé sur un autre graphique ou un autre onglet. Un indicateur **masqué (œil)** continue de calculer et d'envoyer : le retirer, pas le masquer.
- Pendant les tests : éditeur Pine fermé, Profiler fermé, fenêtre de données fermée (ils chargent le même onglet).
- Un seul changement par fenêtre ; **réglé avant 21:45**, jamais pendant la rafale.
- Noter pour chaque fenêtre : le setup entier se fige ? seul le BSP est en retard ? le BSP se redessine depuis la gauche (rechargement) ? durée.

| Soir | 21:50 | 21:55 | 22:00 |
|---|---|---|---|
| 1 | **BSP retiré** du graphique | BSP v11.66 normal | `perf` : « courbes et remplissage » décoché (le script tourne, rien n'est dessiné) |
| 2 | `perf` : « dessiner le bord vivant » décoché | `perf` : « calculer » ET « dessiner le bord » décochés | `perf` : « Afficher le remplissage » décoché + « Barres 10T dessinées » à 100 |
| 3 | `perf-varip` normal | `perf` : « chiffres sur l'échelle » décoché | Profiler : captures à 21:59 et 22:03 (§1, avec les trois précautions) |

Lecture :

| Observation | Conclusion |
|---|---|
| Ça lag autant **sans** BSP (soir 1, 21:50) | Ce n'est pas le BSP : flux 10T + autres indicateurs + navigateur. Alléger le layout (autres oscillateurs, nombre de graphiques, onglets), tester un autre navigateur ou la version bureau. |
| Ça lag avec BSP, plus sans ; plus de lag avec « rien dessiné » (soir 1, 22:00) | Le navigateur : ce que le BSP pousse. Les soirs 2 et 3 disent quoi (bord, remplissage, échelle). |
| Ça lag encore avec « rien dessiné » | Le serveur ou le transport : soir 3 (`varip`, Profiler) ; sinon la livraison des 15 tableaux, non corrigeable dans le script. |
| « Dessiner le bord » décoché suffit | Les objets de dessin du bord. Remède possible (v11.67) : bord en tracés `plot` au lieu de lignes, avec un léger changement visuel à la jonction ; à décider sur la mesure. |
| « Calculer le bord » décoché nécessaire, « dessiner » seul ne suffit pas | Le calcul du bord côté serveur (ses dichotomies) : mémoriser entre deux ticks (`varip`). |
| Remplissage off ou `show_last` 100 suffit | Le dessin des courbes : baisser « Barres 10T dessinées » (300-500) ou le remplissage en rafale. |
| `varip` seul suffit | Le retour en arrière de la réserve : passer la réserve en `varip` dans la v11.67 (sorties identiques, prouvé : elle n'est modifiée qu'à l'exécution confirmée). |
| Seul le BSP est en retard, le reste fluide | Serveur : Profiler du soir 3, lignes 2318/1742, 2259/2242, 3553. |
| Le BSP se redessine depuis la gauche | Rechargement en cascade : « Barres calculées » 1 500 et « Historique 1T demandé » 25 000 raccourcissent le rechargement (chargement seulement, rien en direct). |

## 5. Réglages sans code, applicables tout de suite

- « Barres calculées » (section Calcul des réglages) : 5 000 → ~1 500, et « Historique 1T demandé » : 60 000 → 25 000. Effet au (re)chargement seulement : plus court, donc une reconnexion pendant la rafale coûte moins. Règle de l'info-bulle : 10 × barres calculées + 43 × longueur (233) = 25 000.
- « Barres 10T dessinées » : 1 000 → 500 réduit de moitié ce que le navigateur redessine. Visible seulement en rafale (500 bougies ≈ 5 s de courbe à 100 bougies/s ; en régime calme, plusieurs minutes).
- Retirer, et non masquer, tout indicateur inutile pendant la clôture.

## 6. Les fichiers de test

`src/test/BSP_v11.66_perf.pine` : la v11.66 à l'identique, plus quatre cases en fin de liste, groupe « 6 — Tests 22h », **toutes cochées par défaut** (rendu identique) :

- « calculer le bord vivant » : décochée, le bord n'est ni calculé ni affiché ; l'échelle suit la bougie close.
- « dessiner le bord vivant » : décochée, le bord est calculé (l'échelle le suit) mais aucun objet de dessin n'est mis à jour.
- « chiffres sur l'échelle » : décochée, les deux tracés d'échelle sont en `display.none`.
- « courbes et remplissage » : décochée, les deux courbes et le remplissage sont en `display.none`.

`src/test/BSP_v11.66_perf_varip.pine` : le même fichier, un seul mot changé (ligne 2380) : `varip array<Tick> tickPool`. Sorties identiques, prouvé par les relecteurs : la réserve n'est écrite qu'à l'exécution confirmée (3553), qui est la dernière de la bougie ; aucune exécution intermédiaire ne la modifie ; `var` et `varip` y laissent donc le même contenu. Seul le mécanisme de retour en arrière change. Si le compilateur refuse `varip` sur un tableau de type utilisateur, le dire : la variante tombe, pas le reste.

Les ternaires `display = … ? … : display.none` sont la construction déjà compilée dans la v11.66 (Diag). Le paramètre `display` de `fill()` existe en v6. Pine non compilé ici : signaler toute erreur avec son numéro de ligne.

Ces fichiers sont temporaires : après les tests, remettre la v11.66, ou la v11.67 qui n'intégrera que ce que les tests auront désigné.

## 7. Ce qui n'a pas changé

La v11.66 installée reste la bonne version. Aucune correction de code n'est justifiée par cet audit : il n'y a pas de boucle qui explose, pas de chemin d'erreur, pas de poste caché dans le corps du script. Ce qui reste à mesurer est entre le script et l'écran, et seuls les tests du §4 peuvent le désigner.

## 8. Résolution (13/10, soir)

Observation de l'utilisateur : page rechargée vers 21:45, clôture de 22:00 sans aucun lag, setup complet, BSP v11.66 en place.

Conclusion : la cause est l'**onglet du navigateur chargé depuis le matin**, pas le script. Un graphique TradingView garde en mémoire, côté navigateur, toutes les bougies reçues en direct depuis le chargement de la page, avec les valeurs de chaque indicateur (sur un 10T de NQ : 100 000 à 200 000 bougies par jour). Le script est borné (barres calculées, barres dessinées, réserve purgée) ; le graphique et l'onglet ne le sont pas. La rafale de 22:00 (≈ 100 bougies/s) sature un onglet qui traîne la journée entière, et passe sur un onglet frais.

Routine retenue :

1. Recharger la page vers 21:40, chaque jour (pas à 21:58 : le rechargement du BSP dure plusieurs secondes). Après une session de nuit, idem vers 15:20.
2. « Barres calculées » (section Calcul) à 1 500 et « Historique 1T demandé » à 25 000 : rechargement plus court, rien ne change en direct.
3. Moins d'onglets et de graphiques ouverts en parallèle.

Les versions de test du §6 n'ont pas eu à servir ; elles restent dans `src/test/` si le lag réapparaissait sur un onglet frais, ce qui désignerait alors un autre maillon (§4). La v11.66 reste la version installée.

## 9. Suite (14-16/10) : le rechargement ne suffit pas

Le §8 concluait trop vite sur une seule clôture sans lag. Observations suivantes de l'utilisateur :

- le lag revient, même page rechargée, et aussi **en séance** lors de gros mouvements : tout le setup se décale d'environ 2 s, puis rattrape ;
- un **graphique témoin** (NQ 10T nu, sans indicateur, dans un autre navigateur) **ne lag jamais** au même moment : flux TradingView, réseau et machine (Ryzen 9 9700X, 32 Go) hors de cause ;
- le layout contient **deux graphiques en ticks dans le même onglet** (prix à gauche ; BSP + deux oscillateurs à droite), donc un seul fil d'exécution pour les deux ;
- pendant ces épisodes, « Afficher les diagnostics » était **cochée**, la **fenêtre de données ouverte**, l'**éditeur Pine** (et le Profiler) ouverts ; « Historique 1T demandé » à 50 000 et « Barres calculées » à 5 000 pour 987 barres dessinées.

Lecture : une file d'attente sur le fil de l'onglet (le retard se résorbe seul quand le débit retombe), alimentée par plusieurs charges simultanées. Les captures du Profiler ne tranchent pas : cumulées depuis le chargement, elles montrent surtout le moteur sur l'historique.

Configuration appliquée le 16/10, sans changer une ligne de la v11.66 :

1. diagnostics décochés, fenêtre de données fermée, éditeur Pine et Profiler fermés ;
2. « Historique 1T demandé » 28 957 et « Barres calculées » 1 597 (règle : 10 × barres calculées + 43 × longueur ≥ 26 000 ; les 987 barres dessinées restent identiques) ;
3. page rechargée après ces changements.

Si le lag persiste dans cette configuration : test de l'œil sur le BSP (dessin contre calcul), puis séparation des deux graphiques dans deux profils de navigateur (un processus, donc un cœur, par graphique), puis les cases de `src/test/BSP_v11.66_perf.pine` pour isoler la partie du dessin qui pèse.

## 10. 20/10 : le lag revient en configuration propre ; une limite mémoire dans Edge

- 20/10 vers 17:12, configuration propre (§9) : nouveau décrochage de ~2 s en séance ; une extension de mesure a relevé un blocage du fil de l'onglet de 722 ms ; le témoin nu est resté fluide ; un rechargement a rétabli la fluidité. Navigateur : Microsoft Edge.
- Trouvé ensuite dans Edge (`edge://settings/system`, « Contrôles des ressources ») : **limite de mémoire du navigateur fixée à 3 Go, toujours active**, dépassée (3,7 Go utilisés), six onglets endormis par Edge. Une limite basse déclenche des récupérations de mémoire forcées (onglets endormis, nettoyages agressifs dans les pages), ce qui est compatible avec un blocage long sur un onglet au tas devenu gros au fil de la journée, et avec un rechargement qui règle tout.

Actions retenues, sans toucher au BSP ni au layout : désactiver la limite (ou la porter au maximum), exclure tradingview.com de la mise en veille des onglets, redémarrer Edge, puis observer. Si 22:00 déborde encore malgré cela : séparation du prix et du BSP dans deux profils, sur une copie du layout (§9).
