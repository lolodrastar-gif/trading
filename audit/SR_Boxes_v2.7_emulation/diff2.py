# Differentiel v2.6 (modele du code colle) / v2.7 final (scanSup + scanRes, transcrits ligne a ligne).
import random, sys, os
here=os.path.dirname(os.path.abspath(__file__))
code=open(os.path.join(here,"diff_engine.py")).read()
exec(code.split("tot=[0,0,0,0]")[0])
def upd27(s,bar,H,Lo,C,pH,pL,new):
    out=[]; P=s.P; hDn,hUp,bDn,bUp,rLo,rHi,xAt=s.t
    if s.sup: go=new or Lo>hUp or Lo<=hDn or H<bDn or H>=bUp or (H>rLo and C<rHi) or bar>=xAt
    else:     go=new or H<hDn or H>=hUp or Lo>bUp or Lo<=bDn or (Lo<rHi and C>rLo) or bar>=xAt
    if not go or not s.arr: return out
    s.scans+=1
    hDn,hUp,bDn,bUp,rLo,rHi,xAt=-BIG,BIG,-BIG,BIG,BIG,-BIG,NEVER
    for i in range(len(s.arr)-1,-1,-1):
        l=s.arr[i]; v=l.lvl; gone=False
        side=(Lo>v) if s.sup else (H<v)            # above / below
        if l.broken:
            back=False
            if side: back=(pL<=v) if s.sup else (pH>=v)
            if back:
                l.broken=False; out.append(("H",l.id)); s.nb-=1
            else:
                if P["rej"]:
                    if ((H>v and C<v) if s.sup else (Lo<v and C>v)): out.append(("X",l.id))
                if P["hide"]:
                    if l.at>=0 and bar-l.at>=P["hideN"]:
                        s.nb-=1; del s.arr[i]; out.append(("E",l.id)); gone=True
        else:
            e=l.e
            if (H<e) if s.sup else (Lo>e):
                if (pH>=e) if s.sup else (pL<=e):
                    l.broken=True; l.at=bar; out.append(("B",l.id)); s.nb+=1
            else:
                if side:
                    if (pL<=v) if s.sup else (pH>=v): out.append(("H",l.id))
        if not gone:
            if s.sup:
                if side: hDn=max(hDn,v)
                else: hUp=min(hUp,v)
            else:
                if side: hUp=min(hUp,v)
                else: hDn=max(hDn,v)
            if l.broken:
                if P["rej"]: rLo=min(rLo,v); rHi=max(rHi,v)
                if P["hide"]: xAt=min(xAt,l.at+P["hideN"])
            else:
                e=l.e
                if s.sup:
                    if e<=H: bDn=max(bDn,e)
                    else: bUp=min(bUp,e)
                else:
                    if e>=Lo: bUp=min(bUp,e)
                    else: bDn=max(bDn,e)
    s.t=[hDn,hUp,bDn,bUp,rLo,rHi,xAt]; return out
Side.upd27=upd27
tot=[0,0,0,0]; cfgs=[]
for tick in (0.25,1.0,0.01):
  for maxLv in (1,3,10,50):
    for rej in (True,False):
      for hide in (False,True):
        for pnew,spread,vol,drift in ((0.03,6,2,0),(0.03,30,2,0.02),(0.2,3,1,0),(0.005,15,4,-0.02)):
          cfgs.append(dict(tick=tick,maxLv=maxLv,rej=rej,hide=hide,hideN=random.Random(len(cfgs)).choice((1,5,50)),pnew=pnew,spread=spread,vol=vol,drift=drift,w=random.Random(len(cfgs)+7).choice((0,0.25,1.5,3))))
N=int(sys.argv[1])
for j,P in enumerate(cfgs):
    ev,s26,s27=run(5000+j,N,P); tot[0]+=N; tot[1]+=ev; tot[2]+=s26; tot[3]+=s27
print("configs",len(cfgs),"bougies",tot[0],"evenements",tot[1],"parcours v2.6",tot[2],"parcours v2.7",tot[3],"-> 0 ecart")
