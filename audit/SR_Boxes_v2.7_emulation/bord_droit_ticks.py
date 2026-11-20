# Graphique en ticks : TradingView place ce qui depasse la derniere bougie selon l'HEURE
# (1 emplacement = 1 seconde, lu sur l'axe de la capture 100T), pas selon le nombre de bougies.
# Hypothese du modele : un bord droit pose a l'indice (bougie + k) est ancre a l'heure
# (ouverture de cette bougie + k secondes), et l'ancre n'est renvoyee que si l'indice change.
# On mesure la part du temps ou la bougie en cours n'est PAS entierement dans la boite.
import random, math
def sim(rule, mean_dur, pad=2, delta=0.3, nb=4000, seed=1, slot=1.0, late=0.0):
    rnd=random.Random(seed)
    t=[0.0]
    for i in range(nb): t.append(t[-1]+max(0.05, rnd.lognormvariate(math.log(mean_dur)-0.32, 0.8)))
    events=[]                      # (heure d'affichage, heure d'ancrage)
    last_idx=None
    for i in range(6, nb):
        dur=[t[j+1]-t[j] for j in range(i-5,i)]            # 5 dernieres bougies fermees
        # executions sur la bougie i : a l'ouverture puis ~4 par seconde, puis la cloture
        times=[t[i]]
        while times[-1]+0.25 < t[i+1]: times.append(times[-1]+0.2+0.1*rnd.random())
        for k,x in enumerate(times+[t[i+1]]):
            closing=(k==len(times))
            age=x-t[i]
            if rule=="v2.8":
                if not closing: continue
                idx=i+pad+1
            elif rule=="par tick, marge seule":
                idx=i+pad+(1 if closing else 0)
            elif rule=="v2.9":                                 # marge comptee depuis l'instant present
                idx=i+pad+min(300,math.ceil(max(0.0,age-late)/slot))
            elif rule=="duree des bougies recentes":           # variante ecartee : boite longue
                e=math.ceil(max(max(dur), age)/slot); idx=i+pad+min(300,e)
            if idx!=last_idx:
                events.append((x+delta, t[i]+(idx-i)*slot)); last_idx=idx
    # balayage du temps : toutes les 50 ms
    bad=0; tot=0; msum=0; ev=0; anchor=None; j=6; tau=t[10]
    while tau < t[nb-2]:
        while ev<len(events) and events[ev][0]<=tau: anchor=events[ev][1]; ev+=1
        while t[j+1]<=tau: j+=1
        if anchor is not None:
            margin=math.floor((anchor-t[j])/slot+1e-9)      # emplacements entre la bougie en cours et le bord
            tot+=1; msum+=max(margin,-1)
            if margin<1: bad+=1
        tau+=0.05
    return 100*bad/tot, msum/tot
print("part du temps ou la bougie en cours depasse de la boite | marge moyenne affichee (emplacements)")
for mean in (0.5, 1.5, 3.5, 10):
    print("bougies de %.1f s en moyenne :"%mean)
    for rule in ("v2.8","par tick, marge seule","duree des bougies recentes","v2.9"):
        b,m=sim(rule,mean)
        print("   %-28s %5.1f %%   | %5.1f"%(rule,b,m))
print("v2.9, bougies de 3,5 s, selon le retard d'affichage (s) :", {d: sim("v2.9",3.5,delta=d)[0].__round__(2) for d in (0.1,0.3,1.0,2.0)})
print("v2.9, bougies de 3,5 s, age mesure avec 0,5 s de retard :", round(sim("v2.9",3.5,late=0.5)[0],2), "% ; marge 3 :", round(sim("v2.9",3.5,pad=3,late=0.5)[0],2), "%")
