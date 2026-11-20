# Bord droit des boites : modele des executions du script et de leur retard d'affichage.
# Question : quand une bougie M s'affiche, la boite la contient-elle en entier (bord >= M+1) ?
# La bougie s'affiche des son premier tick ; le resultat du script arrive apres. On regarde
# donc l'ecran avec le dernier resultat DEJA arrive, en retard de `lag` bougies entieres
# (lag = 0 : seule la cloture de la bougie precedente n'est pas encore arrivee).
def run(P, eco, market_open_at_load=True, lag=0, miss_close=(), nhist=40, nrt=30, ticks=3, legacy=None):
    committed=dict(right=None,done=0); snaps=[]          # snaps : (barre, confirme, bord visible)
    def execute(bar,confirmed,realtime,islast,islch):
        st=dict(committed)                                # retour arriere avant chaque execution
        runOnBar=(not eco) or confirmed
        if runOnBar and (islast or islch):
            nextBarComing=confirmed and (realtime or not islast)
            if legacy=="v2.6": rightX=bar+1               # v2.6 et premiere v2.7
            elif legacy=="retouche1": rightX=bar+(2 if nextBarComing else 1)
            else: rightX=bar+P+(1 if nextBarComing else 0)
            st["right"]=rightX; st["done"]=rightX
        if not runOnBar and legacy is None:
            if st["done"]<bar+P: st["right"]=bar+P
        if not runOnBar and legacy=="retouche1":
            if st["done"]<bar+1: st["right"]=bar+1
        return st
    for b in range(nhist):
        last=(b==nhist-1)
        st=execute(b,True,False,islast=(last and not market_open_at_load),islch=last)
        committed.update(st)
    snaps.append((nhist-1,True,committed["right"]))
    for m in range(nhist,nhist+nrt):
        for t in range(ticks):
            st=execute(m,False,True,True,False); snaps.append((m,False,st["right"]))
        if m not in miss_close:
            st=execute(m,True,True,True,False); committed.update(st); snaps.append((m,True,st["right"]))
    # a la naissance de la bougie M : dernier resultat arrive = dernier tick non confirme de M-1-lag
    bad=0; tot=0
    for M in range(nhist+1+lag,nhist+nrt):
        seen=[r for (b,c,r) in snaps if b<M-1-lag or (b==M-1-lag and not c)]
        tot+=1
        if seen[-1] < M+1: bad+=1
    # regime etabli : apres l'arrivee du premier tick de M, la bougie M doit etre dans la boite
    steady=sum(1 for (b,c,r) in snaps if b>=nhist and not c and r<b+1)
    return bad,tot,steady
print("bougies qui s'ouvrent avec la boite arretee avant leur bord droit / total  (regime etabli : ticks hors boite)")
for name,kw in (("v2.6 et 1re v2.7 (bord +1 a la cloture)",dict(P=1,legacy="v2.6")),
                ("retouche precedente (bord +2 a la cloture)",dict(P=1,legacy="retouche1")),
                ("marge 1",dict(P=1)),("marge 2 (defaut)",dict(P=2)),("marge 3",dict(P=3))):
    for eco in (True,False):
        out=[]
        for lag in (0,1,2):
            bad,tot,steady=run(eco=eco,lag=lag,**kw); out.append("retard %d bougie(s) : %d/%d"%(lag,bad,tot))
        print(" %-44s eco %-5s | %s | regime etabli : %d"%(name,eco," ; ".join(out),steady))
# cas particuliers avec la marge par defaut
print("marge 2, marche ferme au chargement puis reouverture :",run(P=2,eco=True,market_open_at_load=False))
print("marge 2, clotures non executees sur 3 bougies        :",run(P=2,eco=True,miss_close=(50,51,52)))
