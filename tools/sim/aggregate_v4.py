## v4ネイティブ100万戦の集計: 16チャンクckpt(各班のgitバックアップ含む)を合算。
## 連勝統計は「負けシード列」から各250kブロック単位で再計算(サブシャード境界の連勝断絶を補正)。
## v3.1マラソン(同一シード)との100万戦フルペア比較も出力。
import json, glob, os, math, sys

SP=os.path.dirname(os.path.abspath(__file__)); os.chdir(os.path.join(SP,"..","..","results","marathon-ckpt"))  # ckpt/milestones は results/marathon-ckpt/（2026-09-13 再編）
BLOCKS=[25000000,26000000,27000000,28000000]
STARTS=[0,62500,125000,187500]; CHUNK=62500; BLOCKN=250000

def load_chunks():
    chunks={}
    for b in BLOCKS:
        for s in STARTS:
            f="v4m_ckpt_%d_%d.json"%(b,s)
            if not os.path.exists(f):
                print("!! 欠損:",f); continue
            chunks[(b,s)]=json.load(open(f))
    return chunks

def wilson(k,n,z=1.96):
    if n==0: return (0,0)
    p=k/n; d=1+z*z/n
    c=p+z*z/(2*n); h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))
    return ((c-h)/d,(c+h)/d)

def streaks_from_losses(loss_seeds, base, n):
    ## [base, base+n)の負けシード集合→連勝長のリスト(勝ち連続数)。境界を跨ぐ連勝も正しく1本に統合される。
    L=sorted(s-base for s in loss_seeds if base<=s<base+n)
    runs=[]; prev=-1
    for x in L:
        runs.append(x-prev-1); prev=x
    runs.append((n-1)-prev)   # 最後の負け以降〜ブロック末尾までの連勝
    return runs

def main():
    ch=load_chunks()
    have=len(ch);
    print("=== v4ネイティブ100万戦 集計 (チャンク %d/16) ==="%have)
    total_n=0; total_losses=0; all_loss=set()
    per_block_done={}
    for b in BLOCKS:
        blk_loss=set(); blk_n=0; done=True
        for s in STARTS:
            c=ch.get((b,s))
            if c is None or c["i"]<CHUNK: done=False
            if c is not None:
                blk_loss|=set(c["losses"]); blk_n+=c["i"]
        per_block_done[b]=done
        total_n+=blk_n; total_losses+=len(blk_loss); all_loss|=blk_loss
        print("  W%d: %d/%d戦 負け%d %s"%(b,blk_n,BLOCKN,len(blk_loss),"✓完走" if done else "…途中"))
    lo,hi=wilson(total_losses,total_n)
    print("\n[全体] %d戦 負け%d 負け率%.4f%% Wilson95%%CI[%.4f%%,%.4f%%]"%(
        total_n,total_losses,100*total_losses/max(1,total_n),100*lo,100*hi))

    # 連勝統計(全ブロック完走時のみ確定値)
    if all(per_block_done.values()):
        s1000=0; longest=0; all_runs=[]
        for b in BLOCKS:
            bl=[s for s in all_loss if b<=s<b+BLOCKN]
            runs=streaks_from_losses(bl,b,BLOCKN)
            all_runs+=runs
            s1000+=sum(1 for r in runs if r>=1000)
            longest=max(longest,max(runs))
        print("[連勝] 1000連勝 %d本 / 最長 %d (250kブロック連続チェーンで再計算)"%(s1000,longest))
        # 事前登録レンジ照合
        print("[事前登録照合] 負け率0.24-0.40%%: %s / 1000連勝85-350本: %s"%(
            "✓" if 0.0024<=total_losses/total_n<=0.0040 else "✗",
            "✓" if 85<=s1000<=350 else "✗"))

    # v3.1(同一シード)との100万戦ペア比較。※v3.1完走ckptは ../../results/marathon-ckpt/ に配置
    v31=set()
    for b in BLOCKS:
        cands=["../../results/marathon-ckpt/v3m_ckpt_%d.json"%b, "v3m_ckpt_%d.json"%b]
        f=next((c for c in cands if os.path.exists(c)), None)
        if f: v31|=set(json.load(open(f))["losses"])
    if v31 and all(per_block_done.values()):
        v4only=all_loss-v31; v31only=v31-all_loss
        n_disc=len(v4only)+len(v31only)
        # McNemar連続補正χ²
        if n_disc>0:
            chi=(abs(len(v4only)-len(v31only))-1)**2/n_disc
            from math import erf,sqrt
            p=math.erfc(math.sqrt(chi/2))  # 近似(χ²1自由度→正規)
        else: p=1.0
        print("\n[v4 vs v3.1 同一100万戦ペア] v4のみ負け%d / v3.1のみ負け%d → v4 net %+d (McNemar p≈%.4f)"%(
            len(v4only),len(v31only),len(v31only)-len(v4only),p))
        print("  v3.1公式=0.2822%% / v4=%.4f%% → 差 %+.4f%%pt"%(100*total_losses/total_n,100*total_losses/total_n-0.2822))

if __name__=="__main__": main()
