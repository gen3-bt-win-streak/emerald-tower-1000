## 関所3集計: PIVOT_ON(敵AIの不利対面ピボット交代#5/#6を有効化) vs PIVOT_OFF(v4公式ベースライン)
## 同一100万シード(4ブロック×25万)のペア比較。両者はチーム/持ち物/EV完全同一=ピボットAIの有無だけの差。
## 目的: net Δ が誤差圏(<0.02pp)なら「ピボット未実装は0.2516%を楽観化していない=床として認定」。
## PIVOT_ON負け > OFF なら真の負け率は高い方(=敵AIがピボットで我々に不利)。
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
    d={}; tot=0
    for b in BLOCKS:
        s=set(); done=True
        for st in STARTS:
            f="%s_ckpt_%d_%d.json"%(prefix,b,st)
            if not os.path.exists(f): done=False; continue
            c=json.load(open(f)); tot+=c["i"]
            if c["i"]<CHUNK: done=False
            s|=set(c["losses"])
        d[b]=(s,done)
    return d,tot

on,ton=load("pivotm")    # PIVOT_ON
off,toff=load("v4m")     # PIVOT_OFF ベースライン(2516)

print("=== 関所3: PIVOT_ON(#5/#6ピボット有効) vs PIVOT_OFF(v4公式) 同一シード ===")
print("block | ON負け | OFF負け | ON完走 | OFF完走")
tON=tOFF=0; alldone=True
for b in BLOCKS:
    sON,dON=on[b]; sOFF,dOFF=off[b]; tON+=len(sON); tOFF+=len(sOFF)
    if not dON: alldone=False
    print("%d | %d | %d | %s | %s"%(b,len(sON),len(sOFF),"✓" if dON else "…","✓" if dOFF else "…"))
print("合計 | ON=%d | OFF=%d   (ON進捗 %d戦)"%(tON,tOFF,ton))
lo,hi=wilson(tON,ton)
print("[PIVOT_ON] %d戦 負け%d 負け率%.4f%% Wilson95%%CI[%.4f%%,%.4f%%]"%(ton,tON,100*tON/max(1,ton),100*lo,100*hi))

# ペア差分(完走ブロックのみ厳密。部分完走ブロックはシード集合が非対称なので除外)
done_blocks=[b for b in BLOCKS if on[b][1] and off[b][1]]
if done_blocks:
    ON=set().union(*[on[b][0] for b in done_blocks])
    OFF=set().union(*[off[b][0] for b in done_blocks])
    N=len(done_blocks)*BLOCKN
    only_on=len(ON-OFF)    # ピボット有効で新たに負け(=敵AIが強くなった方向)
    only_off=len(OFF-ON)   # ピボット有効で勝ちに転じた(RNGずれ由来の対称ノイズ含む)
    nd=only_on+only_off
    net=only_on-only_off
    chi=(abs(only_on-only_off)-1)**2/nd if nd else 0
    p=math.erfc(math.sqrt(chi/2)) if nd else 1
    dp=100*net/N   # net Δ(pp)
    print("\n[ピボット分離: %d万ペア(完走%dブロック)]"%(N//10000,len(done_blocks)))
    print("  ON のみ負け %d / OFF のみ負け %d → net %+d (不一致ペア%d)"%(only_on,only_off,net,nd))
    print("  McNemar χ²=%.2f p≈%.3e"%(chi,p))
    print("  PIVOT_ON=%.4f%% / PIVOT_OFF=%.4f%% / net Δ=%+.4fpp"%(100*len(ON)/N,100*len(OFF)/N,dp))
    # 床の認定
    seN=math.sqrt(nd)/N   # net countのSE≈√(不一致ペア数), 率SE
    up95=(net+1.96*math.sqrt(nd))/N*100  # net Δの上側95%(pp)
    print("  net Δ 上側95%%≈%+.4fpp"%up95)
    if alldone:
        if up95<0.02:
            verd="床として認定: ピボット交代の未実装は公式0.2516%%を有意に楽観化していない(net Δ上側95%%<0.02pp)"
        elif net>0 and p<0.05:
            verd="要注意: ピボット有効で有意に負けが増える(net%+d,p<0.05)→ 真の負け率はPIVOT_ON側 %.4f%% を採用すべき"%(net,100*len(ON)/N)
        else:
            verd="判定保留: net Δ上側95%%≥0.02ppだが有意でない→追加サンプルor人間頑健性で保守側を採用"
        print("  → 裁定: %s"%verd)
    else:
        print("  (全16チャンク未完走。完走ブロックのみの暫定値)")
else:
    print("\n(ペア差分はブロック完走待ち)")
