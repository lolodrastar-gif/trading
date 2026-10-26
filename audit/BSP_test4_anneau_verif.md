# BSP anneau (réserve circulaire) — vérification (26/10)

Fichier : `src/test/BSP_test4_anneau.pine` (commit eb34af3). Il est reconstruit à
partir du test4 vérifié (`audit/BSP_test4_verif.md`) et des zones que modifie le
fichier collé, renvoyé deux fois à l'identique. L'en-tête d'historique n'est pas
recopié. Pine non compilé ici.

## Ce qui change par rapport au test4

16 zones de diff, toutes dans le stockage de la réserve, plus le titre et l'en-tête :

- `TickPool { entries, head, count }` remplace `array<Tick>` ; capacité fixe de
  13 000 cases (6 000 + 3 000 + 2 × 2 000).
- Toutes les lectures passent par `poolRead(rang logique)`.
- Ajout en fin : `array.set` dans une case libre.
- Insertion intérieure : `array.insert`, puis retrait d'une case libre (`pop` ou
  `remove`).
- Purge : la tête avance de `excess`, `count := 6000`. La boucle de recopie des
  6 000 références disparaît.
- Titre « test4 reserve circulaire », nom court « BSP anneau ».

Rien d'autre ne change : moteur, lecture différée, bord vivant, couleurs,
32 réglages et fin de script sont identiques au test4, ligne de code par ligne de
code.

## Identité des sorties : oui

Trois vérifications indépendantes, sans aucun contre-exemple :

| Vérification | Ampleur | Résultat |
|---|---|---|
| Fuzz différentiel test4 / anneau (réserve, certificat `deliveredFrom`, recherches, `pickLatest`) | 3,9 M versements : 100 000 aux constantes réelles (553 purges qui font tourner la tête), 3,8 M sur 10 jeux de constantes réduites ; 15,5 M séries de requêtes | 0 écart ; 7 mutants volontairement faux, tous détectés |
| Preuve par cas de `poolPlace`, `poolAppend` et purge, puis vérification exhaustive | toute capacité de 1 à 32, chaque tête, chaque compte, chaque rang ; 4,4 M chaînes de 3 à 5 opérations | 0 écart |
| Relecture adverse + vérification refaite de zéro | 703 cas limites à 13 000 cases, 2,2 M écritures | 0 écart |

- Capacité : un versement commence toujours avec 9 000 éléments au plus et ajoute au
  plus 2 éléments par rang, sur 2 000 rangs au plus. Avant toute écriture le compte
  vaut donc au maximum 12 999. L'erreur « capacite interne depassee » est
  inatteignable, avec une marge nulle.
- Retour en arrière (rollback) : comme dans le test4, la réserve n'est modifiée qu'à
  l'exécution confirmée (`barstate.isconfirmed`), sans `varip`.
- Les 25 appels de `poolRead` restent dans le rang `[0, count)`. Point vérifié en
  lisant le code, pas en l'exécutant. Une lecture hors rang ne planterait plus,
  contrairement au test4 : elle lirait une case périmée sans rien signaler.

## Compilation

Probable, mais rien n'a été compilé ici. Deux constructions sont nouvelles dans ce
code et le manuel ne les documente que par analogie :

- `pool.count :=` dans une fonction ordinaire (le manuel ne le montre que dans des
  méthodes) ;
- `.serial` lu directement sur le résultat d'une fonction utilisateur.

Si l'éditeur refusait la seconde, il suffit de passer par une variable intermédiaire
(`Tick t = poolRead(...)`).

## Coût

Tout le coût est côté serveur :

| Ce qui baisse | Ce qui monte |
|---|---|
| Plus de boucle de recopie de 6 000 éléments, une fois toutes les ~300 bougies | Chaque lecture de la réserve passe par deux appels de fonction, y compris dans les recherches faites à chaque tick |
| | Une insertion intérieure déplace en natif environ 8 fois plus d'éléments |
| | Un tableau `var` de 13 000 cases en permanence, au lieu de 6 000 à 9 000 éléments. Le coût de ce stockage pour le retour en arrière n'est pas documenté |

Bilan serveur : non mesuré, et peut aller dans les deux sens. Côté navigateur, rien
ne change en dehors du nom : mêmes tracés, même remplissage, mêmes 5 objets du bord
vivant. Aucun effet n'est attendu sur les blocages mesurés par Lolo Guard.

## Le 27,3 % du Profiler sur `isSorted`

Captures non vues. Les numéros cités (2549 et 1880-1892) tombent exactement sur
l'anneau avec son en-tête complet, soit +1 454 lignes : ligne 1095 pour l'appel,
bloc 426-438 pour le corps. Ils ne correspondent pas au test4. La capture a donc
probablement été prise avec l'anneau chargé.

- **Un seul coût, affiché deux fois.** La ligne d'appel inclut le corps de la
  fonction, et l'appel sur le tableau figé est mémorisé. Il ne faut pas les
  additionner.
- **C'est du temps serveur cumulé.** Le chiffre additionne le chargement de
  l'historique et le direct depuis l'activation du Profiler, qui recharge lui-même
  le script.
- **Le coût par exécution est faible en direct.** Le tableau vivant compte 1 à
  10 éléments, soit 4 à 7 tours de boucle. À l'historique, un tableau porte souvent
  les ticks des 5 à 6 bougies suivantes (environ 64 tours), parfois jusqu'à 2 000.
- **On ne sait pas si l'historique domine.** Les queues d'historique sont
  intermittentes ; sans elles, le direct rattrape l'historique en 5 à 17 minutes de
  marché calme.
- **Le chiffre est inattendu.** Au profil du 13/10, `isSorted` n'était pas dans les
  trois premiers postes. Seuls les champs « Executions » permettent de trancher
  (procédure ci-dessous).
- **Il ne peut pas causer un blocage du navigateur.** Pine s'exécute sur les serveurs
  de TradingView (manuel : `welcome.md`, `profiling-and-optimization.md`). `isSorted`
  renvoie un booléen interne : une version plus rapide, à sorties identiques, envoie
  au navigateur exactement les mêmes tracés et dessins.

### Validation incrémentale proposée : à ne pas faire

- **Avec `var`**, la mémoire est remise à l'état confirmé avant chaque exécution en
  direct. Elle ne servirait jamais à l'intérieur d'une bougie : gain nul.
- **Avec `varip`**, il faut prouver que le début du tableau n'a pas changé, ce qui
  oblige à le relire. Le modèle donne 17 à 20 lectures par exécution contre 10 à 11
  aujourd'hui.
- **Faire confiance au début du tableau sans le relire** n'est pas sûr : le manuel ne
  garantit pas que les données intrabarres en direct ne font que s'allonger. Le
  modèle trouve 14 à 28 % de résultats faux dans ces scénarios.
- **Un faux « trié » corromprait la réserve.** `poolAbsorb` exige un tableau trié ;
  un tableau désordonné y entrerait et la fausserait jusqu'au rechargement suivant.
- **Cela casse la règle « pas de varip ».**
- **Aucune fonction native** ne fait ce contrôle moins cher avec un résultat
  identique.

### Lire le Profiler sans mélanger historique et direct

1. Activer le Profiler, puis relever **Time** et **Executions** sur :
   - la ligne 2549 (appel sur le tableau vivant) ;
   - le bloc 1880 (corps de `isSorted`) ;
   - la ligne 1886 (premier tour de boucle) ;
   - la ligne 2547 (appel sur le tableau figé).

   Attendu : Executions(2549) ≈ nombre de bougies calculées, et ligne 2547 ≈ 0.
   Executions(1886) / Executions(2549) donne le nombre d'éléments par bougie
   d'historique.
2. Laisser tourner N minutes sans rien toucher, relever à nouveau, puis faire les
   différences (Δ) :
   - Δ(1886) / Δ(2549) = éléments lus par exécution en direct (4 à 7 attendus) ;
   - ΔTime(2549) / ΔExecutions(2549) = coût par exécution en direct.

   Des centaines d'éléments par exécution en direct signaleraient d'énormes tableaux
   vivants : ce serait alors le seul cas à étudier, toujours côté serveur.

## Ce qui tranche pour les blocages

- **Ce que Lolo Guard mesure.** Il mesure le retard d'un minuteur de 500 ms, ce qui
  donne une borne basse de la durée du blocage.
- **Les 5 blocages du 21/10** (358 à 388 ms) précèdent le test3, le test4 et
  l'anneau : aucune de ces versions ne peut les avoir causés.
- **Mesurer pendant des fenêtres comparables**, avec le Profiler éteint et l'éditeur
  Pine fermé (tous deux font travailler le navigateur), sur trois configurations :
  - A : le BSP tel quel ;
  - B : groupe « 6 — Tests 22h », avec « dessiner le bord vivant », « chiffres sur
    l'échelle » et « courbes et remplissage » décochés ;
  - C : le BSP retiré.
- **Lecture du résultat :**
  - A ≈ B ≈ C : le BSP n'y est pour rien ;
  - B et C plus bas que A : c'est le dessin du BSP ;
  - seulement C plus bas : c'est sa simple présence. Aucun de ces trois cas
    n'implique le temps de calcul de `isSorted`.
