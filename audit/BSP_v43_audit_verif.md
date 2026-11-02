# BSP v4.3 « audit TRAIL64 » — vérification (02/11)

Fichier : `src/test/BSP_v43_audit.pine` (commit afaf7a3), reconstruit à partir de
l'anneau vérifié (`audit/BSP_test4_anneau_verif.md`) et des 12 zones que le fichier
collé modifie ; l'en-tête d'historique n'est pas recopié. Pine non compilé ici.
Trois relectures indépendantes, puis 35 points passés à une relecture adverse
(13 reclassés « confirmation, pas un défaut », 0 défaut trouvé).

Son propre en-tête le dit : copie d'audit A/B, « pas pour le trading réel ».

## Ce qui change par rapport à l'anneau

| Zone | Changement | Effet sur les sorties |
|---|---|---|
| `isSorted` | boucle déroulée par 8 (« tri8 ») | aucun : même booléen, mêmes lectures, mêmes comparaisons (1,2 M de cas modélisés, 0 écart) |
| `poolAbsorb` | ne renvoie plus l'objet réserve, seulement le plancher | aucun : l'objet était déjà modifié sur place, `tickPool := …` était une auto-affectation |
| `pickTrail` | traîne lue jusqu'au 64e porteur au lieu du 16e, **actif par défaut** (`TRAIL64_RECOVERY_TEST = true`), sous une garde sur le rang 17 | ne joue que si le tableau vivant a **plus de 16 éléments** ; choisit alors un tick de N plus récent, jamais plus ancien, jamais après la clôture stricte (modèle réaliste : 100 000 cas, 10 528 choix différents, tous plus récents) |
| `pickStrictOverflow` (nouveau) | lecture séquentielle contrôlée des rangs 2000 à 2255 du tableau vivant, **actif par défaut** (`V4_STRICT_OVERFLOW_TEST = true`) | ne joue que si le tableau vivant a **plus de 2 000 éléments** ; même propriété (40 000 cas, 0 écart avec un oracle) |
| sélection `rec*` | le candidat v4 passe avant la traîne et la réserve | cohérent en aval (300 000 cas d'intégration, 0 valeur pire, 0 mesure perdue) |
| sondes 70 à 89 | 20 tracés et compteurs derrière `const AUDIT_RECOVERY_DIAGNOSTICS = false` | aucun tant que la constante est fausse |
| titre | « BSP tri8C v4.3 — audit TRAIL64 (TEST) » | nom seulement |

En direct normal (1 à 10 ticks dans le tableau vivant), les sorties sont donc
**identiques à l'anneau**. Les deux récupérations ne s'activent que sur des
tableaux vivants anormalement longs (blocs livrés en retard), dont on ne sait pas
s'ils existent en direct : les sondes 70 à 89 servent précisément à le mesurer.

La garde du rang 17 est exacte (les heures de la traîne sont monotones quand les
numéros le sont) : les sondes 86 à 89 ne peuvent compter que 0 sur un tableau trié.

## Compilation

Probable : aucune construction hors du manuel v6, aucun conflit d'identifiant,
budget de tracés 36 sur 64. Non vérifiable ici : le plafond de taille du code
compilé. Les sondes passent `precision = 0` sans `format` : si on les active,
elles hériteraient du `%` de `format.percent` (cosmétique).

## Coût côté serveur

- **Pas plus légère en direct normal, plutôt un peu plus lourde** : +25 à 30
  opérations sur le chemin actif, +55 à 90 opérations de globales d'audit (sauf si
  le compilateur les élimine, non documenté), 20 sorties de plus déclarées (valeur
  na, `display.none` ; leur transmission au navigateur n'est pas documentée). Le
  tri8 n'économise que du contrôle de boucle, sur des tableaux de 9 éléments ou
  plus ; `isSorted` pèse 2 à 4 % d'une exécution normale.
- **Nettement plus lourde dans les régimes qu'elle vise** : +49 à 145 lectures par
  appel de `pickTrail` dès que le tableau vivant dépasse 16 éléments, +514 à 770
  lectures par exécution au-delà de 2 000.
- Nuance apportée par la relecture adverse : les deux recherches dans la réserve
  ne sont en O(1) que si le dernier tick versé est daté avant l'ouverture de la
  bougie en cours ; à une milliseconde partagée (22 % des frontières le 25/09,
  davantage en rafale), elles font leurs 13 pas. Microsecondes, côté serveur.

## Rapport avec la saccade de 15:30

Aucun. Le CSV de Lolo Control du 02/11 montre une saturation du fil principal du
navigateur (`audit/lolo_control_2026-11-02.md`) ; rien de ce que change la v4.3
ne touche ce que le navigateur dessine.

## Ce qu'on peut en faire

- Ne pas l'installer sur « lolo ».
- Si chat veut savoir si ses deux récupérations servent à quelque chose : copie
  séparée, `AUDIT_RECOVERY_DIAGNOSTICS = true`, sur un onglet léger, une séance
  entière, puis lire les compteurs 70 à 89 dans la fenêtre de données. Tous à zéro :
  TRAIL64 et V4 sont inutiles en direct, à retirer. Sinon, les chiffres disent
  combien de bougies auraient changé.
- Le tri8 ne se juge qu'au Profiler, sur la ligne de `curTimesSorted`, avant et
  après, même séance.
