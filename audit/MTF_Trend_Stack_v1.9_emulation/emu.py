# Emulation personnelle (relecteur principal) de MTF Trend Stack L2 CONFLUENCE v1.9.
# Prix simules a la seconde (pas de donnees de marche), agreges en 5/10/15/30/45/60/180 s.
# Toutes les valeurs sont lues "sur la derniere bougie cloturee" de chaque unite, comme le script.
import numpy as np, math, sys
from collections import Counter

def simulate(days=12, drift_per_day=0.0, seed=1, sd_sec=0.8, tick=0.25, day_sec=23*3600):
    rng=np.random.default_rng(seed)
    n=days*day_sec
    # volatilite variable (grappes) : multiplicateur lent
    vol=np.exp(0.5*np.sin(np.arange(n)/day_sec*2*np.pi*3)+0.3*np.cumsum(rng.normal(0,0.002,n)).clip(-2,2))
    ret=rng.normal(drift_per_day/day_sec, sd_sec, n)*vol
    p=20000+np.cumsum(ret)
    p=np.round(p/tick)*tick
    v=rng.lognormal(1.0,0.8,n)*vol
    return p,v,day_sec

def agg(p,v,per):
    n=len(p)//per
    q=p[:n*per].reshape(n,per); w=v[:n*per].reshape(n,per)
    return dict(o=q[:,0],h=q.max(1),l=q.min(1),c=q[:,-1],v=w.sum(1))

def ema(x,n):
    a=2/(n+1); out=np.empty(len(x)); s=x[0]
    for i,xi in enumerate(x):
        s=xi if i==0 else a*xi+(1-a)*s
        out[i]=s
    return out

def rma(x,n):
    out=np.full(len(x),np.nan); 
    if len(x)<n: return out
    idx=np.where(~np.isnan(x))[0]
    if len(idx)<n: return out
    st=idx[0]; s=np.mean(x[st:st+n]); out[st+n-1]=s
    for i in range(st+n,len(x)):
        s=(s*(n-1)+x[i])/n; out[i]=s
    return out

def trend_state(b,f=11,s=29,confirm=True):
    ef=ema(b['c'],f); es=ema(b['c'],s)
    bull=(ef>es)&((b['c']>es) if confirm else True)
    bear=(ef<es)&((b['c']<es) if confirm else True)
    return np.where(bull,1,np.where(bear,-1,0))

def dmi(b,n=14,sm=14):
    h,l,c=b['h'],b['l'],b['c']
    up=np.r_[np.nan,h[1:]-h[:-1]]; dn=np.r_[np.nan,l[:-1]-l[1:]]
    pdm=np.where((up>dn)&(up>0),up,0.0); mdm=np.where((dn>up)&(dn>0),dn,0.0)
    pdm[0]=np.nan; mdm[0]=np.nan
    tr=np.maximum(h-l,np.maximum(np.abs(h-np.r_[np.nan,c[:-1]]),np.abs(l-np.r_[np.nan,c[:-1]])))
    tr[0]=np.nan
    atr=rma(tr,n); pdi=100*rma(pdm,n)/atr; mdi=100*rma(mdm,n)/atr
    s=pdi+mdi; dx=100*np.abs(pdi-mdi)/np.where(s==0,1,s)
    adx=rma(dx,sm)
    return pdi,mdi,adx

def er(c,n=20):
    out=np.full(len(c),np.nan); mv=np.abs(np.diff(c,prepend=np.nan))
    cs=np.nancumsum(mv)
    for i in range(n,len(c)):
        tr=cs[i]-cs[i-n]
        out[i]=0.0 if tr<=0 else min(1.0,abs(c[i]-c[i-n])/tr)
    return out

def chop(b,n=14):
    h,l,c=b['h'],b['l'],b['c']
    tr=np.maximum(h-l,np.maximum(np.abs(h-np.r_[c[0],c[:-1]]),np.abs(l-np.r_[c[0],c[:-1]]))); tr[0]=h[0]-l[0]
    out=np.full(len(c),np.nan)
    for i in range(n-1,len(c)):
        sp=h[i-n+1:i+1].max()-l[i-n+1:i+1].min(); tt=tr[i-n+1:i+1].sum()
        if sp>0 and tt>0: out[i]=100*math.log10(tt/sp)/math.log10(n)
    return out

def structure(b,per,day_sec,piv=3):
    h,l,c,v=b['h'],b['l'],b['c'],b['v']; n=len(c)
    hi=oldHi=lo=oldLo=np.nan; lastBos=0; lastIdx=None
    S=np.full(n,np.nan); B=np.zeros(n,int); A=np.full(n,np.nan); HI=np.full(n,np.nan); LO=np.full(n,np.nan); VW=np.full(n,np.nan)
    bars_day=day_sec//per; cpv=0.0; cv=0.0
    for i in range(n):
        if i%bars_day==0: cpv=0.0; cv=0.0
        cpv+=(h[i]+l[i]+c[i])/3*v[i]; cv+=v[i]; VW[i]=cpv/cv if cv>0 else np.nan
        if i>=1:
            up=(not np.isnan(hi)) and c[i]>hi and c[i-1]<=hi
            dn=(not np.isnan(lo)) and c[i]<lo and c[i-1]>=lo
            if up and not dn: lastBos=1; lastIdx=i
            elif dn and not up: lastBos=-1; lastIdx=i
        j=i-piv
        if j-piv>=0:
            win=h[j-piv:i+1]
            if h[j]==win.max() and (h[j]>h[j+1:i+1]).all() and (h[j]>=h[j-piv:j]).all():   # pivot haut : strict a droite
                oldHi=hi; hi=h[j]
            win=l[j-piv:i+1]
            if l[j]==win.min() and (l[j]<l[j+1:i+1]).all() and (l[j]<=l[j-piv:j]).all():
                oldLo=lo; lo=l[j]
        if not (np.isnan(hi) or np.isnan(oldHi) or np.isnan(lo) or np.isnan(oldLo)):
            S[i]=1 if (hi>oldHi and lo>oldLo) else (-1 if (hi<oldHi and lo<oldLo) else 0)
        B[i]=lastBos; A[i]=np.nan if lastIdx is None else i-lastIdx; HI[i]=hi; LO[i]=lo
    return S,B,A,HI,LO,VW

def run(days=12,drift=0.0,seed=1,step=5,verbose=True):
    p,v,day_sec=simulate(days,drift,seed)
    tfs=[5,10,15,30,45,60]
    bars={per:agg(p,v,per) for per in tfs+[180,day_sec]}
    st={per:trend_state(bars[per]) for per in tfs}
    q=bars[30]; pdi,mdi,adx=dmi(q); erq=er(q['c']); ch=chop(q)
    atr=rma(np.maximum(q['h']-q['l'],np.maximum(np.abs(q['h']-np.r_[np.nan,q['c'][:-1]]),np.abs(q['l']-np.r_[np.nan,q['c'][:-1]]))),14)
    atr_sma=np.full(len(atr),np.nan)
    cs=np.nancumsum(atr)
    for i in range(len(atr)):
        if i>=113: atr_sma[i]=(cs[i]-cs[i-100])/100
    m1=bars[60]; cpdi,cmdi,cadx=dmi(m1); cer=er(m1['c'])
    S1,B1,A1,H1,L1,VW1=structure(m1,60,day_sec); S3,B3,A3,H3,L3,_=structure(bars[180],180,day_sec)
    dayb=bars[day_sec]
    T=len(p); verd=Counter(); why=Counter(); mtfv=Counter(); zone=Counter(); conf_txt=Counter()
    runs=[]; cur=0; full_runs=[]; fcur=0; stale=Counter(); tot=0
    states_log=[]
    cond=Counter()
    for t in range(2*day_sec, T, step):          # 2 jours de prechauffage
        k={per:t//per-1 for per in tfs}          # derniere bougie cloturee de chaque unite
        s=[st[per][k[per]] for per in tfs]
        bulls=sum(1 for x in s if x==1); bears=sum(1 for x in s if x==-1); net=bulls-bears
        mv="FULL BULL" if bulls==6 else "FULL BEAR" if bears==6 else "Strong" if max(bulls,bears)>=5 else "No Resonance" if bulls==bears else "Lean"
        mtfv[mv]+=1; tot+=1
        states_log.append(s)
        if mv.startswith("FULL"): fcur+=step
        elif fcur: full_runs.append(fcur); fcur=0
        kq=t//30-1; k1=t//60-1; k3=t//180-1; kd=t//day_sec-1
        qp,qm,qa,qe,qv,qc=pdi[kq],mdi[kq],adx[kq],erq[kq],(atr[kq]/atr_sma[kq] if atr_sma[kq]>0 else np.nan),ch[kq]
        cp,cm,ca,ce=cpdi[k1],cmdi[k1],cadx[k1],cer[k1]
        qReady=not any(np.isnan(x) for x in (qp,qm,qa,qe,qv)); cReady=not any(np.isnan(x) for x in (cp,cm,ca,ce))
        qDir=0 if not qReady else (1 if qp>qm else -1 if qm>qp else 0); cDir=0 if not cReady else (1 if cp>cm else -1 if cm>cp else 0)
        cAgree=cReady and cDir==qDir and qDir!=0 and ca>=18 and ce>=0.20
        zone["N/A" if np.isnan(qc) else "HACHE" if qc>=61.8 else "TENDANCE" if qc<=38.2 else "TRANSITION"]+=1
        conf_txt["N/A" if not (cReady and qReady) else "OK" if cAgree else "NON / faible"]+=1
        price=m1['c'][k1]; vw=VW1[k1]
        levels=[H1[k1],L1[k1],H3[k3],L3[k3],dayb['h'][kd],dayb['l'][kd]]
        ab=[x for x in levels if not np.isnan(x) and x>price]; be=[x for x in levels if not np.isnan(x) and x<price]
        dUp=min(ab)-price if ab else np.nan; dDn=price-max(be) if be else np.nan
        vdir=1 if price>vw else -1 if price<vw else 0
        mdir=1 if (bulls>=4 and bears<=1) else -1 if (bears>=4 and bulls<=1) else 0
        hasData=qReady and not np.isnan(qc) and not np.isnan(S1[k1]) and not np.isnan(S3[k3]) and cReady
        recUp=(B1[k1]==1 and A1[k1]<=20) or (B3[k3]==1 and A3[k3]<=8); recDn=(B1[k1]==-1 and A1[k1]<=20) or (B3[k3]==-1 and A3[k3]<=8)
        bosOK=(recUp and price>H1[k1]) if mdir==1 else (recDn and price<L1[k1]) if mdir==-1 else False
        room=dUp if mdir==1 else dDn if mdir==-1 else np.nan
        roomOK=(not np.isnan(room)) and room>=20
        qualOK=qDir==mdir and qa>=18 and qe>=0.20 and qc<61.8 and cAgree
        strOK=mdir!=0 and S1[k1]==mdir and S3[k3]==mdir
        vwOK=mdir!=0 and vdir==mdir
        opp=mdir!=0 and ((S1[k1]!=0 and S1[k1]!=mdir) or (S3[k3]!=0 and S3[k3]!=mdir) or (vdir!=0 and vdir!=mdir))
        conf=hasData and mdir!=0 and qualOK and strOK and vwOK and bosOK and roomOK
        v_="N/A" if not hasData else "CONFLUENCE" if conf else "CONTRADICTION" if opp else "PARTIELLE"
        w_=("Prechauffage" if not hasData else "MTF non tranche" if mdir==0 else "Structure / VWAP oppose" if opp else "Qualite / CHOP / confirm." if not qualOK else
            "Structure inachevee" if not strOK else "VWAP non aligne" if not vwOK else "BOS non confirme/recent" if not bosOK else "Obstacle proche/inconnu" if not roomOK else "Crit. reunis")
        verd[v_]+=1; why[w_]+=1
        if mdir!=0:
            cond["sens defini"]+=1; cond["qualite OK"]+=qualOK; cond["structure OK"]+=strOK; cond["vwap OK"]+=vwOK; cond["bos OK"]+=bosOK
            cond["espace connu"]+=(not np.isnan(room)); cond["espace OK"]+=roomOK
            if bosOK: cond["bos OK : espace inconnu"]+=np.isnan(room); cond["bos OK total"]+=1
            allbut=qualOK and strOK and vwOK and bosOK
            if allbut: cond["tout sauf espace"]+=1; cond["tout sauf espace : inconnu"]+=np.isnan(room); cond["tout sauf espace : < 20"]+=((not np.isnan(room)) and room<20)
        if conf: cur+=step
        elif cur: runs.append(cur); cur=0
    S=np.array(states_log)
    res=dict(tot=tot,mtf={k:round(100*v/tot,2) for k,v in mtfv.items()},verdict={k:round(100*v/tot,3) for k,v in verd.items()},
             why={k:round(100*v/tot,2) for k,v in why.most_common()},zone={k:round(100*v/tot,1) for k,v in zone.items()},
             conf1m={k:round(100*v/tot,1) for k,v in conf_txt.items()},
             full_runs=(len(full_runs),round(float(np.mean(full_runs)),1) if full_runs else 0,round(float(np.median(full_runs)),1) if full_runs else 0),
             conf_runs=(len(runs),round(float(np.mean(runs)),1) if runs else 0),
             corr=np.round(np.corrcoef(S.T),2).tolist(),
             cond={k:int(v) for k,v in cond.items()})
    return res
if __name__=="__main__":
    for drift,name in ((0.0,"sans derive"),(400.0,"derive +400 pts/jour")):
        r=run(days=12,drift=drift,seed=7)
        print("=====",name,"| echantillons",r["tot"])
        print("verdict MTF (% du temps):",r["mtf"])
        print("etats FULL : nombre, duree moyenne s, mediane s:",r["full_runs"])
        print("zones CHOP 30s:",r["zone"],"| Conf. 1m:",r["conf1m"])
        print("verdict confluence %:",r["verdict"],"| episodes CONFLUENCE (nombre, duree moyenne s):",r["conf_runs"])
        print("explication %:",r["why"])
        print("conditions quand le sens MTF est defini:",r["cond"])
        print("correlation des 6 etats (5s,10s,15s,30s,45s,1m):"); [print("  ",row) for row in r["corr"]]
