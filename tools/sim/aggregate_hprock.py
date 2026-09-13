## めざ岩レバー(D案: ラグいわなだれ→めざ岩70+EV B4→S4)のA/B集計: HP_ROCK ON(hrm) vs OFF=FIRE_FIX完走(ffm, 2233敗/100万)
## 同一100万シード(4ブロック×25万)のペア比較。両者はチーム/持ち物/EV/シード完全同一
## =両側FIRE_FIX=1で共通、ラグの技構成(なだれ⇔めざ岩)とEV(B4⇔S4)・実IV補正だけの差。
## 目的: net<0(ON側で負けが減る)が有意なら「修正は勝率を改善する真のレバー」。
##      net≈0(誤差圏)なら「この誤選択も0.2516%床の下=勝率不変」。
import json, os, math
SP=os.path.dirname(os.path.abspath(__file__)); os.chdir(os.path.join(SP,"..","..","results","marathon-ckpt"))  # ckpt/milestones は results/marathon-ckpt/（2026-09-11 再編）
BLOCKS=[25000000,26000000,27000000,28000000]; STARTS=[0,62500,125000,187500]; CHUNK=62500; BLOCKN=250000

def wilson(k,n,z=1.96):
    if n==0: return (0,0)
    p=k/n; d=1+z*z/n; c=p+z*z/(2*n); h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))
    return ((c-h)/d,(c+h)/d)

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

on,ton=load("hrm")    # FIRE_FIX=ON(修正)
off,toff=load("ffm")  # OFF=ベースライン(2516)

print("=== めざ岩レバー: HP_ROCK ON(hrm) vs OFF=ffmベースライン 同一シード ===")
print("block | ON負け | OFF負け | ON完走 | OFF完走")
tON=tOFF=0; alldone=True
for b in BLOCKS:
    sON,dON=on[b]; sOFF,dOFF=off[b]; tON+=len(sON); tOFF+=len(sOFF)
    if not dON: alldone=False
    print("%d | %d | %d | %s | %s"%(b,len(sON),len(sOFF),"✓" if dON else "…","✓" if dOFF else "…"))
print("合計 | ON=%d | OFF=%d   (ON進捗 %d戦)"%(tON,tOFF,ton))
lo,hi=wilson(tON,ton)
print("[HP_ROCK ON] %d戦 負け%d 負け率%.4f%% Wilson95%%CI[%.4f%%,%.4f%%]"%(ton,tON,100*tON/max(1,ton),100*lo,100*hi))

done_blocks=[b for b in BLOCKS if on[b][1] and off[b][1]]
if done_blocks:
    ON=set().union(*[on[b][0] for b in done_blocks])
    OFF=set().union(*[off[b][0] for b in done_blocks])
    N=len(done_blocks)*BLOCKN
    only_on=len(ON-OFF)    # 修正で新たに負け(=改悪・回帰)
    only_off=len(OFF-ON)   # 修正で勝ちに転じた(=改善・爆発誤選択を回避できた分)
    nd=only_on+only_off
    net=only_on-only_off   # <0 なら改善(負けが減る)
    chi=(abs(only_on-only_off)-1)**2/nd if nd else 0
    p=math.erfc(math.sqrt(chi/2)) if nd else 1
    dp=100*net/N
    print("\n[修正分離: %d万ペア(完走%dブロック)]"%(N//10000,len(done_blocks)))
    print("  ON のみ負け %d(改悪) / OFF のみ負け %d(改善) → net %+d (不一致ペア%d)"%(only_on,only_off,net,nd))
    print("  McNemar χ²=%.2f p≈%.3e"%(chi,p))
    print("  ON=%.4f%% / OFF=%.4f%% / net Δ=%+.4fpp (負なら改善)"%(100*len(ON)/N,100*len(OFF)/N,dp))
    lo95=(net-1.96*math.sqrt(nd))/N*100  # net Δ の下側95%
    print("  net Δ 下側95%%≈%+.4fpp"%lo95)
    if alldone:
        if net<0 and p<0.05:
            verd="改善を確認: 修正で負けが有意に減る(net%+d,p<0.05)。0.2516%%床は下がる=勝率改善レバー"%net
        elif abs(dp)<0.01 or p>=0.05:
            verd="床の下: 修正の勝率影響は誤差圏(net%+d,p≈%.2f)。誤選択は稀で0.2516%%床を有意に動かさない"%(net,p)
        else:
            verd="要検討: net%+d p≈%.2e"%(net,p)
        print("  → 裁定: %s"%verd)
    else:
        print("  (全16チャンク未完走。完走ブロックのみの暫定値)")
else:
    print("\n(ペア差分はブロック完走待ち)")
