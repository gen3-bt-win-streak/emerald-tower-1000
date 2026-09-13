## Stage3集計: v5(A252+ツメ交換) vs v4(A164+ツメ交換) を同一シードで比較。
## 両者はツメ交換が共通=EV(A252 vs A164)だけの差。v5<v4ならA252優位、v5>v4ならA164優位。
import json, os, math
SP=os.path.dirname(os.path.abspath(__file__)); os.chdir(os.path.join(SP,"..","..","results","marathon-ckpt"))  # ckpt/milestones は results/marathon-ckpt/（2026-09-11 再編）
BLOCKS=[25000000,26000000,27000000,28000000]; STARTS=[0,62500,125000,187500]; CHUNK=62500; BLOCKN=250000

def wilson(k,n,z=1.96):
    if n==0: return (0,0)
    p=k/n; d=1+z*z/n; c=p+z*z/(2*n); h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))
    return ((c-h)/d,(c+h)/d)
def streaks(loss,base,n):
    L=sorted(s-base for s in loss if base<=s<base+n); runs=[]; prev=-1
    for x in L: runs.append(x-prev-1); prev=x
    runs.append((n-1)-prev); return runs

def load(prefix):
    d={}
    for b in BLOCKS:
        s=set(); done=True
        for st in STARTS:
            f="%s_ckpt_%d_%d.json"%(prefix,b,st)
            if not os.path.exists(f): done=False; continue
            c=json.load(open(f));
            if c["i"]<CHUNK: done=False
            s|=set(c["losses"])
        d[b]=(s,done)
    return d

v5=load("v5m"); v4=load("v4m")
print("=== Stage3: v5(A252+交換) vs v4(A164+交換) 同一シード ===")
print("block | v5損失 | v4損失 | v5完走 | v4完走")
tv5=tv4=0; alldone=True
for b in BLOCKS:
    s5,d5=v5[b]; s4,d4=v4[b]; tv5+=len(s5); tv4+=len(s4)
    if not d5: alldone=False
    print("%d | %d | %d | %s | %s"%(b,len(s5),len(s4),"✓" if d5 else "…","✓" if d4 else "…"))
print("合計 | %d | %d"%(tv5,tv4))
n5=sum(len(json.load(open("v5m_ckpt_%d_%d.json"%(b,st)))["losses"]) and 0 or 0 for b in BLOCKS for st in STARTS)  # placeholder
# 進捗戦数
tot5=0
for b in BLOCKS:
    for st in STARTS:
        f="v5m_ckpt_%d_%d.json"%(b,st)
        if os.path.exists(f): tot5+=json.load(open(f))["i"]
lo,hi=wilson(tv5,tot5)
print("\n[v5] %d戦 負け%d 負け率%.4f%% Wilson95%%CI[%.4f%%,%.4f%%]"%(tot5,tv5,100*tv5/max(1,tot5),100*lo,100*hi))
if alldone:
    V5=set().union(*[v5[b][0] for b in BLOCKS]); V4=set().union(*[v4[b][0] for b in BLOCKS])
    s1000=0; longest=0
    for b in BLOCKS:
        r=streaks(V5,b,BLOCKN); s1000+=sum(1 for x in r if x>=1000); longest=max(longest,max(r))
    print("[v5連勝] 1000連勝%d本 / 最長%d"%(s1000,longest))
    vo=len(V5-V4); po=len(V4-V5); nd=vo+po
    chi=(abs(vo-po)-1)**2/nd if nd else 0; p=math.erfc(math.sqrt(chi/2)) if nd else 1
    print("\n[EV分離: v5(A252) vs v4(A164) 同一100万ペア]")
    print("  v5(A252)のみ負け %d / v4(A164)のみ負け %d → net %+d"%(vo,po,po-vo))
    print("  McNemar χ²=%.1f p≈%.2e"%(chi,p))
    print("  v5(A252)=%.4f%% / v4(A164)=%.4f%%"%(100*tv5/1e6,100*tv4/1e6))
    verd = "A252優位(EVはA252が上・A164は損)" if tv5<tv4-30 else ("A164優位(EVもA164が上)" if tv5>tv4+30 else "互角(EV差は誤差圏→A164を人間頑健性で維持)")
    print("  → 裁定: %s"%verd)
