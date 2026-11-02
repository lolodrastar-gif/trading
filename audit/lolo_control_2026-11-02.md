# Lolo Control du 02/11 — la saccade de 15:30 (ouverture US)

Source : `lolo-control-2026-11-02.csv` (Lolo Control v4.0.1, layout « lolo »,
onglet ouvert à 10:58, jamais rechargé, 1 358 fenêtres de mesure de 10 s).
Lecture faite deux fois, par deux analyses indépendantes, qui concordent.
Scripts : `scratchpad/guard/analyze_control.py`, `agg5.py`, `indep/s0..s5`.

## Ce que l'extension mesure

- `longTask` : tâches du fil principal ≥ 50 ms (API Long Tasks) ; `totalMs`
  = somme de leurs durées dans la fenêtre. Le « % occupé » = totalMs / durée
  de la fenêtre est une **borne basse** : les tâches < 50 ms ne sont pas vues.
- `rafProbe` : sonde d'images d'environ 1,5 s lancée toutes les ~20 s ;
  ~92 rappels = 60 images/s. Elle n'échantillonne que ~7 % du temps.
- `timer.maxDriftMs` : retard maximal d'un minuteur à 1 s ; 12 ms en temps
  normal.
- `heapMB` : mémoire JavaScript de l'onglet.

## Journée

| Créneau (Paris) | Tâches ≥ 50 ms / 10 s | % occupé | Plus longue | Images/s |
|---|---|---|---|---|
| 11:03 – 14:35 (hors séance US) | 0,1 | 0,1 % | 193 ms | 60 |
| 14:35 – 15:10 | 2,8 | 1,7 – 2,9 % | 204 ms | ≥ 49 |
| 15:20 – 15:25 | 1,7 | 1,1 % | 150 ms | 58 – 63 |
| 15:25 – 15:30 (montée) | 5,8 | 3,9 % | 257 ms | 45 – 70 |
| **15:29:58 – 15:32:47 (ouverture US)** | **66** (23 à 102 par fenêtre) | **48 % en moyenne, 35 à 72 % par fenêtre** | **327 ms** | **7 – 19** |
| 15:35 – 15:50 | 8,8 | 5,8 % | 190 ms | ≥ 44 |
| 15:50 – 15:56 | 15,9 | 10,7 % | 139 ms | ≥ 41 |

L'épisode commence à 2 s près à 09:30:00 ET et s'arrête net à 15:32:47. Sur
2 min 49 s, 114 s ont été mesurées visibles ; pendant les 56 s où l'onglet
était caché (Lolo a quitté l'onglet 66 s après l'ouverture), aucune tâche
n'est enregistrée, et la charge reprend à l'instant où il redevient visible.
La dérive du minuteur atteint 614 ms, plus que la plus longue tâche (327 ms) :
la file d'attente du fil principal était profonde, plusieurs tâches à la suite.

## Ce que ça établit

1. **Ce n'est pas un gel unique**, c'est une saturation : 755 tâches de 50 à
   327 ms en moins de deux minutes visibles (73 ms en moyenne), aucune ≥ 500 ms.
   À 7 – 19 images par seconde avec des à-coups de 70 à 330 ms, c'est
   exactement « ça saccade de fou ».
2. **C'est tout l'onglet**, pas un indicateur : trois instruments indépendants
   (tâches longues, minuteur, sonde d'images) le disent en même temps. Les
   bougies saccadaient autant que le BSP ; le BSP est juste là où ça se voit.
3. **La mémoire n'y est pour rien** : 305 – 427 Mo pendant l'épisode, stable.
4. **Le côté serveur n'est pas visible dans ce fichier**, et ne peut pas, à lui
   seul, produire un fil principal saturé : un serveur lent donne des données en
   retard sur un navigateur *inactif*, l'inverse de ce qui est mesuré. Ce qui
   sature, c'est le travail de redessin du layout à chaque tick, dans le
   navigateur.
5. **Rien dans ce fichier n'attribue le travail au BSP** ni à quoi que ce soit
   d'autre : pas d'attribution par script, par étude ni par volet. Seul un test
   A/B (BSP dessinant moins, ou retiré) peut mesurer sa part.

## Deux autres épisodes

- **14:37 – 15:06** : mémoire en dents de scie 180 ↔ 829 Mo (collecte toutes
  les 20 à 40 s, allocation médiane 16 Mo/s), fil principal à 1 – 3 %, tâches
  de 50 à 204 ms (pauses de collecte plausibles). Ça commence juste après le
  seul masquage/affichage de l'onglet entre 14:18 et 15:31 (14:36:55) : une
  action de Lolo, à identifier (éditeur Pine ? Profiler ? autre fenêtre ?).
  Pendant l'épisode de 15:30, la mémoire était calme : ce n'est pas la cause.
- **15:50 – 15:56** : seconde poussée, plus douce (16 tâches / 10 s, 11 %).

## Conséquences pour l'optimisation

- Optimiser le code serveur du BSP ne touche pas ces 48 %.
- Ce qui peut les réduire : ce que le BSP envoie à dessiner (groupe « 6 — Tests
  22h » : bord vivant non dessiné, puis courbes et chiffres en display.none),
  la charge du reste du layout, la séparation des deux graphiques en deux
  fenêtres de navigateur (deux fils principaux), l'écran 60 Hz (la sonde
  d'images montre déjà 60 images/s en temps normal).
- Protocole : même réglage toute la séance, fixé avant 15:25, Profiler éteint
  et éditeur fermé, CSV Lolo Control de 15:25 à 15:40, comparer le « % occupé »
  et les tâches / 10 s de l'épisode d'ouverture d'un jour à l'autre.
- Note pour Lolo Control : l'alerte DEGRADATION n'a sonné qu'une fois (critère
  sur les tâches ≥ 150 ms) alors que la saturation à 45 – 72 % a duré deux
  minutes ; un critère sur le % occupé ou sur le nombre de tâches ≥ 50 ms la
  verrait.
