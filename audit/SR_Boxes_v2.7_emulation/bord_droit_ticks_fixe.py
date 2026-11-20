# Graphique en ticks, bord droit FIXE (v2.10). Meme modele que bord_droit_ticks.py :
# 1 emplacement = 1 seconde a droite de la derniere bougie, ancre horaire renvoyee a l'ecran
# seulement si l'indice du bord change.
#   "fixe pur"  : bord a F emplacements de la bougie, jamais allonge
#   "v2.10"     : bord a F emplacements ; allonge seulement si la bougie dure plus de F-2 s
#                 (avance minimale de 2 s sur l'instant present), sans jamais valoir F+1
import random, math
def sim(F, mean_dur, rule="v2.10", delta=0.3, nb=6000, seed=3, slot=1.0):
    rnd=random.Random(seed); t=[0.0]
    for i in range(nb): t.append(t[-1]+max(0.05, rnd.lognormvariate(math.log(mean_dur)-0.32, 0.8)))
    events=[]; last_idx=None; moved=0
    for i in range(6, nb):
        times=[t[i]]
        while times[-1]+0.25 < t[i+1]: times.append(times[-1]+0.2+0.1*rnd.random())
        grew=False
        for x in times+[t[i+1]]:
            age=max(0.0,x-t[i])
            k=F
            if rule!="fixe pur":
                k=max(F, 2+math.ceil(age/slot))
                if rule=="v2.10" and k==F+1: k=F+2
            if k>F: grew=True
            idx=i+min(350,k)
            if idx!=last_idx: events.append((x+delta, t[i]+(idx-i)*slot)); last_idx=idx
        moved+=grew
    bad=0; tot=0; ev=0; anchor=None; j=6; tau=t[10]
    while tau < t[nb-2]:
        while ev<len(events) and events[ev][0]<=tau: anchor=events[ev][1]; ev+=1
        while t[j+1]<=tau: j+=1
        if anchor is not None:
            tot+=1
            if math.floor((anchor-t[j])/slot+1e-9)<1: bad+=1
        tau+=0.05
    return round(100*bad/tot,2), round(100*moved/(nb-6),1)
print("(part du temps ou la bougie en cours depasse de la boite %, part des bougies pendant lesquelles le bord bouge %)")
for mean in (1.5,3.5,6,10):
    print("bougies de %.1f s en moyenne :"%mean)
    for F in (4,8,12,20):
        print("   marge %2d | fixe pur %s | sans la regle F+1 %s | v2.10 %s"%(F,sim(F,mean,"fixe pur"),sim(F,mean,"sans F+1"),sim(F,mean)))
print("v2.10, marge 12, bougies de 3,5 s, selon le retard d'affichage (s) :", {d: sim(12,3.5,delta=d) for d in (0.1,0.3,1.0,2.0)})
