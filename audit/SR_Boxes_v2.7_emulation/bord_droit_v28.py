# Bord droit des boites, v2.8 : meme question que bord_droit.py, mais sans faire confiance aux
# indicateurs d'etat de TradingView. On essaie toutes les facons dont la plateforme pourrait
# annoncer une cloture en direct (derniere bougie ou non, temps reel ou non) et la derniere
# bougie d'historique, et on verifie que la bougie affichee reste dans la boite.
import itertools
def run(version, P, eco, rt_close_isrt, rt_close_islast, hist_last_islast, lbi_ahead, lag, newbox_at, nhist=40, nrt=24, ticks=3):
    com=dict(old=None, new=None, done=0); snaps=[]
    def execute(bar, confirmed, realtime, islast, islch, lbi):
        st=dict(com); runOnBar=(not eco) or confirmed
        if runOnBar and bar==newbox_at and st["new"] is None:          # creation d'une boite
            st["new"]=bar+P+1 if version=="v2.8" else bar
        if version=="v2.8": renderNow=islast or islch or realtime or bar>=lbi-1
        else: renderNow=islast or islch
        if runOnBar and renderNow:
            if version=="v2.8": rightX=bar+P+(1 if confirmed else 0)
            elif version=="v2.7 marge": rightX=bar+P+(1 if (confirmed and (realtime or not islast)) else 0)
            else: rightX=bar+(2 if (confirmed and (realtime or not islast)) else 1)   # retouche 1
            st["old"]=rightX; st["done"]=rightX
            if st["new"] is not None: st["new"]=rightX
        if not runOnBar:
            pad=1 if version=="retouche 1" else P
            if st["done"]<bar+pad:
                st["old"]=bar+pad
                if st["new"] is not None: st["new"]=bar+pad
        return st
    for b in range(nhist):
        last=(b==nhist-1)
        st=execute(b,True,False,islast=(last and hist_last_islast),islch=last,lbi=nhist)
        com.update(st)
    snaps.append((nhist-1,True,dict(com)))
    for m in range(nhist,nhist+nrt):
        for t in range(ticks):
            st=execute(m,False,True,True,False,m); snaps.append((m,False,st))
        st=execute(m,True,rt_close_isrt,rt_close_islast,False,m+(1 if lbi_ahead else 0)); com.update(st); snaps.append((m,True,dict(st)))
    worst=99
    # a) naissance de la bougie M : dernier resultat arrive = dernier tick de M-1-lag (cloture non arrivee)
    for M in range(nhist+1+lag,nhist+nrt):
        seen=[s for (b,c,s) in snaps if b<M-1-lag or (b==M-1-lag and not c)][-1]
        for k in ("old","new"):
            if seen[k] is not None: worst=min(worst,seen[k]-M)
    # b) juste apres chaque cloture, la bougie suivante est deja la
    if lag==0:
        for (b,c,s) in snaps:
            if c and b>=nhist:
                for k in ("old","new"):
                    if s[k] is not None: worst=min(worst,s[k]-(b+1))
            if not c:
                for k in ("old","new"):
                    if s[k] is not None: worst=min(worst,s[k]-b)
    return worst      # nombre de barres entre la bougie affichee et le bord droit (0 = milieu de bougie)
variants=list(itertools.product((True,False),(True,False),(True,False),(True,False)))
print("pire cas, sur 16 facons d'annoncer les etats x mode eco oui/non x boite creee en direct :")
print("(0 = la boite s'arrete au milieu de la bougie ; 1 = une bougie apres ; negatif = avant la bougie)")
for version,P in (("retouche 1",1),("v2.7 marge",2),("v2.8",2),("v2.8",3)):
    for lag in (0,1):
        res=[]
        for eco in (True,False):
            for (isrt,isl,hl,la) in variants:
                res.append(run(version,P,eco,isrt,isl,hl,la,lag,newbox_at=52))
        print(" %-11s marge %d | resultat en retard de %d bougie entiere : pire cas %2d | cas a 0 ou moins : %2d / %d"%(version,P,lag,min(res),sum(1 for r in res if r<=0),len(res)))
print("etats annonces comme dans le manuel, sans retard :",
      {v+" m"+str(P): run(v,P,True,True,True,False,False,0,52) for v,P in (("retouche 1",1),("v2.7 marge",2),("v2.8",2))})
