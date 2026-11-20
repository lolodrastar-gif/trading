# Frequence des parcours avec des niveaux crees comme dans le script :
# pivots de cloture 5/5, filtre de volume signe, bord a 0,5 ATR(150), 10 niveaux par cote.
import random, sys
sys.argv=[sys.argv[0],"0"]
exec(open(sys.argv[0].replace("realiste.py","diff_engine.py")).read().split("tot=[0,0,0,0]")[0])
def sim(seed,n,cp=5,maxLv=10,rej=True,volp=0.5):
    rnd=random.Random(seed); tick=0.25
    P=dict(tick=tick,maxLv=maxLv,rej=rej,hide=False,hideN=50)
    A=[Side(True,P),Side(False,P)]; B=[Side(True,P),Side(False,P)]
    cl=[];hi=[];lo=[]; c=20000.0; atr=None; trs=[]; nid=0
    cause=dict(ev=0,cell=0,rejfp=0,new=0); nev=0; why=[0,0]
    for bar in range(n):
        o=c; sd=6*(1+0.8*rnd.random())
        c=round((o+rnd.gauss(0,sd))/tick)*tick
        H=max(o,c)+round(abs(rnd.gauss(0,sd/2))/tick)*tick; Lo=min(o,c)-round(abs(rnd.gauss(0,sd/2))/tick)*tick
        cl.append(c);hi.append(H);lo.append(Lo)
        tr=H-Lo if bar==0 else max(H-Lo,abs(H-cl[-2]),abs(Lo-cl[-2])); trs.append(tr)
        if bar==149: atr=sum(trs)/150
        elif bar>149: atr=(atr*149+tr)/150
        new=[False,False]
        if atr is not None and bar>=2*cp:
            p=cl[-1-cp]; left=cl[-1-2*cp:-1-cp]; right=cl[-cp:]
            vsign=1 if c>o else -1
            if all(p<x for x in right) and all(p<=x for x in left) and vsign>0 and rnd.random()<volp:
                for X in (A,B): X[0].push(L(p,p-0.5*atr,nid))
                nid+=1; new[0]=True
            if all(p>x for x in right) and all(p>=x for x in left) and vsign<0 and rnd.random()<volp:
                for X in (A,B): X[1].push(L(p,p+0.5*atr,nid))
                nid+=1; new[1]=True
        if bar>0:
            for k in (0,1):
                s0=B[k].scans
                ea=A[k].upd26(bar,H,Lo,c,hi[-2],lo[-2],new[k]); eb=B[k].upd27(bar,H,Lo,c,hi[-2],lo[-2],new[k])
                assert ea==eb and A[k].nb==B[k].nb and [(l.id,l.broken) for l in A[k].arr]==[(l.id,l.broken) for l in B[k].arr]
                nev+=len(eb)
                if B[k].scans>s0:
                    if new[k]: cause["new"]+=1
                    elif eb: cause["ev"]+=1
                    else: cause["cell"]+=1
    return n,nev,sum(s.scans for s in A),sum(s.scans for s in B),cause
for rej in (True,False):
    for maxLv in (10,):
        n,ev,s26,s27,cause=sim(3,300000,maxLv=maxLv,rej=rej)
        print("rejets",rej,"| cote-bougies",2*n,"| evenements",ev,"| parcours v2.6 %.1f%%"%(100*s26/(2*n)),"| v2.7 %.1f%%"%(100*s27/(2*n)),"|",cause)
