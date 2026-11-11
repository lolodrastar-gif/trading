# LOLO 2 - Jauge consensus technique v0.2 : corrections et verification

Fichier : `src/lolo2/LOLO2_jauge_consensus_v0.2.pine` (234 lignes). Base : `src/lolo2/LOLO2_jauge_consensus_v0.1_codex.pine`,
laissee intacte. Non compile ici.

## Ce qui change

Quatre lignes de la v0.1 sont modifiees (titre, enregistrement de la securite, libelle de la securite, alerte de choc).
Tout le reste est ajoute. Calculs, seuils, couleurs, panneau et ordre des 23 reglages : inchanges.

1. Alerte "L2 CHOC LIVE" : la condition n'exige plus une bougie non cloturee. Elle sonne des le choc avec
   "Une fois par barre" et a la cloture de la bougie avec "Une fois par cloture de barre" (avant : jamais).
2. Confirmation optionnelle de la securite : reglage "Clotures de confirmation avant d'ameliorer la securite",
   24e et dernier, 1 par defaut. Degradation immediate ; amelioration apres N clotures meilleures de suite.
   Pendant l'attente, le panneau affiche "ROUGE - CONFIRMATION k/N" ou "ORANGE - CONFIRMATION k/N".
3. "Securite brute" ajoutee dans la fenetre de donnees (provisoire pendant la bougie).

## Verification

Mes controles : diff exact, controle statique (aucun message nouveau hors variables locales), bloc de confirmation
identique ligne pour ligne a celui du filtre CHOP/ATR v0.3 (apres renommage), deja rejoue sur 6 000 000 de barres.

Trois relecteurs independants, puis un contradicteur sur chaque remarque :

- Compilation : aucun probleme trouve (signatures, types, portee des variables, indentation, ASCII).
- Comportement : emulation Python des deux versions, lignes traduites mecaniquement.
  Avec 1 cloture de confirmation, sur 1 205 258 barres (1 805 847 ticks, barres historiques et temps reel) :
  toutes les variables, les 43 cellules du panneau, les deux alertes de consensus et les deux traces existants
  sont identiques a la v0.1. Seule l'alerte de choc differe, sur les clotures de bougies en choc, comme voulu.
  Transcription manuelle recoupee sur 4 002 642 clotures. Avec 2, 3 et 5 clotures : jamais meilleur que le brut,
  degradation a la meme cloture, chaque amelioration apres N clotures meilleures de suite et egale au plus bas
  de la serie. Verifie aussi sur toutes les suites courtes possibles. 8 versions volontairement faussees sont
  toutes rejetees par ces controles.
- Temps reel, alertes, tableau : la machine ne change qu'a la cloture, temps reel = historique ; l'alerte de choc
  ne sonne ni plus souvent ni plus tot qu'avant avec "Une fois par barre" ; aucun texte perime dans la cellule
  de securite.

Une seule remarque retenue, sans changement de code : une alerte TradingView garde une copie du script et des
reglages du jour de sa creation. Il faut supprimer et recreer l'alerte "L2 CHOC LIVE" apres le passage a la v0.2,
et recreer toutes les alertes apres un changement de reglage. La note est ajoutee dans l'en-tete du script.

## Comportements a connaitre

- De ROUGE a VERT avec N clotures : N clotures si le brut est VERT tout du long, jusqu'a 2N-1 si le passage
  se fait par ORANGE (le compteur repart). Le compteur affiche est toujours exact.
- Apres "CALCUL EN COURS", la premiere valeur valide est prise sans confirmation (comme la v0.1).
- Pendant une attente vers le VERT, "VIGILANCE LIVE" ne s'affiche pas : le panneau garde "ORANGE - CONFIRMATION k/N".
- Le libelle d'attente est plus long (27 caracteres au plus contre 20) : la colonne peut s'elargir un peu.

## Non verifie

Compilation sur TradingView. Comportement du serveur d'alertes au-dela de ce que dit le manuel.
