# Differentiel moteur v2.6 (plages) / v2.7 (seuils exacts) sur bougies simulees.
import random, sys
BIG=1e300; NEVER=2000000000
class L:
    __slots__=("lvl","e","broken","at","id")
    def __init__(s,lvl,e,i): s.lvl=lvl; s.e=e; s.broken=False; s.at=-1; s.id=i
def ev_level(l,sup,H,Lo,C,pH,pL,rej):
    hN,hP,bN,bP=(Lo,pL,H,pH) if sup else (H,pH,Lo,pL)
    holds=(hN>l.lvl and hP<=l.lvl) if sup else (hN<l.lvl and hP>=l.lvl)
    breaks=(not l.broken) and ((bN<l.e and bP>=l.e) if sup else (bN>l.e and bP<=l.e))
    rejects=l.broken and rej and ((bN>l.lvl and C<l.lvl) if sup else (bN<l.lvl and C>l.lvl))
    return holds,breaks,rejects
class Side:
    def __init__(s,sup,P):
        s.sup=sup; s.P=P; s.arr=[]; s.nb=0; s.scans=0
        s.b=dict(allMin=None,allMax=None,aMin=None,aMax=None,bMin=None,bMax=None,old=None)   # v2.6
        s.t=[-BIG,BIG,-BIG,BIG,BIG,-BIG,NEVER]                                               # v2.7
    def push(s,l):
        if len(s.arr)>=s.P["maxLv"]:
            o=s.arr.pop(0)
            if o.broken: s.nb-=1
        s.arr.append(l)
    def apply(s,i,bar,H,Lo,C,pH,pL,out):
        P=s.P; l=s.arr[i]; was=l.broken
        h,b,r=ev_level(l,s.sup,H,Lo,C,pH,pL,P["rej"])
        if b: l.broken=True; l.at=bar; s.nb+=1; out.append(("B",l.id))
        if h:
            l.broken=False
            if was: s.nb-=1
            out.append(("H",l.id))
        if r: out.append(("X",l.id))
        if P["hide"] and l.broken and l.at>=0 and bar-l.at>=P["hideN"]:
            s.nb-=1; del s.arr[i]; out.append(("E",l.id)); return False
        return True
    def upd26(s,bar,H,Lo,C,pH,pL,new):
        out=[]; P=s.P; b=s.b; sup=s.sup
        if not s.arr: return out
        hN,hP,bN,bP=(Lo,pL,H,pH) if sup else (H,pH,Lo,pL)
        canH=hN>hP if sup else hN<hP
        canB=bN<bP if sup else bN>bP
        canR=P["rej"] and s.nb>0 and (bN>C if sup else bN<C)
        mH=canH and b["allMin"] is not None and ((hN>b["allMin"] and hP<=b["allMax"]) if sup else (hN<b["allMax"] and hP>=b["allMin"]))
        mB=canB and b["aMin"] is not None and ((bN<b["aMax"] and bP>=b["aMin"]) if sup else (bN>b["aMin"] and bP<=b["aMax"]))
        mR=canR and b["bMin"] is not None and ((bN>b["bMin"] and C<b["bMax"]) if sup else (bN<b["bMax"] and C>b["bMin"]))
        mE=P["hide"] and b["old"] is not None and bar-b["old"]>=P["hideN"]
        if not (new or mH or mB or mR or mE): return out
        s.scans+=1
        nb=dict(allMin=None,allMax=None,aMin=None,aMax=None,bMin=None,bMax=None,old=None)
        mn=lambda a,x: x if a is None else min(a,x)
        mx=lambda a,x: x if a is None else max(a,x)
        for i in range(len(s.arr)-1,-1,-1):
            l=s.arr[i]; was=l.broken
            # gating exact de la v2.6 : evenement evalue seulement si (maybeX or new) et canX
            h,bk,r=ev_level(l,sup,H,Lo,C,pH,pL,P["rej"])
            h=h and (mH or new) and canH
            bk=bk and (mB or new) and canB
            r=r and (mR or new) and canR
            if bk: l.broken=True; l.at=bar; s.nb+=1; out.append(("B",l.id))
            if h:
                l.broken=False
                if was: s.nb-=1
                out.append(("H",l.id))
            if r: out.append(("X",l.id))
            if P["hide"] and l.broken and l.at>=0 and bar-l.at>=P["hideN"]:
                s.nb-=1; del s.arr[i]; out.append(("E",l.id))
            else:
                nb["allMin"]=mn(nb["allMin"],l.lvl); nb["allMax"]=mx(nb["allMax"],l.lvl)
                if l.broken:
                    nb["bMin"]=mn(nb["bMin"],l.lvl); nb["bMax"]=mx(nb["bMax"],l.lvl)
                    if l.at>=0: nb["old"]=mn(nb["old"],l.at)
                else:
                    nb["aMin"]=mn(nb["aMin"],l.e); nb["aMax"]=mx(nb["aMax"],l.e)
        s.b=nb; return out
    def upd27(s,bar,H,Lo,C,pH,pL,new):
        out=[]; P=s.P; sup=s.sup; hDn,hUp,bDn,bUp,rLo,rHi,xAt=s.t
        if sup: go=new or Lo>hUp or Lo<=hDn or H<bDn or H>=bUp or (H>rLo and C<rHi) or bar>=xAt
        else:   go=new or H<hDn or H>=hUp or Lo>bUp or Lo<=bDn or (Lo<rHi and C>rLo) or bar>=xAt
        if not go or not s.arr: return out
        s.scans+=1
        hN,bN=(Lo,H) if sup else (H,Lo)
        t=[-BIG,BIG,-BIG,BIG,BIG,-BIG,NEVER]
        for i in range(len(s.arr)-1,-1,-1):
            l=s.arr[i]
            if not s.apply(i,bar,H,Lo,C,pH,pL,out): continue
            v=l.lvl; e=l.e
            if sup:
                if v>=hN: t[1]=min(t[1],v)
                else: t[0]=max(t[0],v)
            else:
                if v<=hN: t[0]=max(t[0],v)
                else: t[1]=min(t[1],v)
            if l.broken:
                if P["rej"]: t[4]=min(t[4],v); t[5]=max(t[5],v)
                if P["hide"] and l.at>=0: t[6]=min(t[6],l.at+P["hideN"])
            else:
                if sup:
                    if e<=bN: t[2]=max(t[2],e)
                    else: t[3]=min(t[3],e)
                else:
                    if e>=bN: t[3]=min(t[3],e)
                    else: t[2]=max(t[2],e)
        s.t=t; return out
def run(seed,n,P):
    rnd=random.Random(seed); tick=P["tick"]
    A=[Side(True,P),Side(False,P)]; B=[Side(True,P),Side(False,P)]
    c=1000.0; pH=pL=None; nid=0; nev=0
    for bar in range(n):
        o=c; c=round((o+rnd.gauss(P["drift"],P["vol"]))/tick)*tick
        H=max(o,c)+round(abs(rnd.gauss(0,P["vol"]/2))/tick)*tick
        Lo=min(o,c)-round(abs(rnd.gauss(0,P["vol"]/2))/tick)*tick
        new=[False,False]
        if bar>0:
            for k,sup in ((0,True),(1,False)):
                if rnd.random()<P["pnew"]:
                    lvl=round((c+rnd.gauss(0,P["spread"]))/tick)*tick
                    w=P["w"]; e=lvl-w if sup else lvl+w
                    A[k].push(L(lvl,e,nid)); B[k].push(L(lvl,e,nid)); nid+=1; new[k]=True
            for k in (0,1):
                ea=A[k].upd26(bar,H,Lo,c,pH,pL,new[k]); eb=B[k].upd27(bar,H,Lo,c,pH,pL,new[k])
                sa=[(l.id,l.broken,l.at) for l in A[k].arr]; sb=[(l.id,l.broken,l.at) for l in B[k].arr]
                if ea!=eb or sa!=sb or A[k].nb!=B[k].nb:
                    print("ECART seed",seed,"bar",bar,"cote",k,ea,eb); sys.exit(1)
                nev+=len(ea)
        pH,pL=H,Lo
    return nev,sum(s.scans for s in A),sum(s.scans for s in B)
tot=[0,0,0,0]
cfgs=[]
for tick in (0.25,1.0,0.01):
  for maxLv in (1,3,10,50):
    for rej in (True,False):
      for hide in (False,True):
        for pnew,spread,vol,drift in ((0.03,6,2,0),(0.03,30,2,0.02),(0.2,3,1,0),(0.005,15,4,-0.02)):
          cfgs.append(dict(tick=tick,maxLv=maxLv,rej=rej,hide=hide,hideN=random.Random(len(cfgs)).choice((1,5,50)),pnew=pnew,spread=spread,vol=vol,drift=drift,w=random.Random(len(cfgs)+7).choice((0,0.25,1.5,3))))
N=int(sys.argv[1]) if len(sys.argv)>1 else 20000
for j,P in enumerate(cfgs):
    ev,s26,s27=run(1000+j,N,P); tot[0]+=N; tot[1]+=ev; tot[2]+=s26; tot[3]+=s27
print("configs",len(cfgs),"bougies",tot[0],"evenements",tot[1],"parcours v2.6",tot[2],"parcours v2.7",tot[3],"-> 0 ecart")
# cas par defaut : 10 niveaux, rejets on, pas de masquage
P=dict(tick=0.25,maxLv=10,rej=True,hide=False,hideN=50,pnew=0.03,spread=8,vol=2,drift=0,w=1.5)
ev,s26,s27=run(7,200000,P); print("defaut 200000 bougies x 2 cotes : evenements",ev,"parcours v2.6",s26,"v2.7",s27)
