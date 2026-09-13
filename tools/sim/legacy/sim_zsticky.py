## Z探索ボット最終形: A252変種+退避+探索S3R3+sticky(爆発ペア/退避保護)
## sticky = 探索の1点変更が safety 不変条件を却下できない:
##   (1) 爆発するなら相方は必ずまもる。まもれないなら爆発中止（ルール行動へ差し戻し）
##   (2) ルールのグロス退避指示は保持
## 検証: 1万シードペア比較 素0.800% vs sticky0.520% (不一致53:25, McNemar p≈0.002)
import sys, collections, random, copy, json, os, time
_z=open('sim_z11.py').read()
exec(_z[:_z.index("\nCASES=")])
G["SMART_SENDIN"]=0; RETREAT=True
NS["TH_GDANGER"]=1.15
def spec_a252():
    s=WRspec("Quick Claw")
    z=list(s[0]); z[3]="Lum Berry"; s[0]=tuple(z)
    g=list(s[1]); g[3]="Leftovers"; s[1]=tuple(g)
    return s
rule_choose=z5_choose
max_hit=fair_maxhit
ai_choose=G["ai_choose"]; STAGE_KEYS=G["STAGE_KEYS"]
bld=lambda: team_builder(spec_a252())()
_s=open('sim_zsearch.py').read()
exec(_s[_s.index("S=3; R=3"):_s.index("BASE=int")])
G["our_team"]=bld
G["POLICY_VARIANT"]="G"; G["PROTECT_CAP"]=1

def sticky_choose(b):
    acts=search_choose(b)
    ours=[m for m in b.active["us"] if m and m.alive()]
    boomer=None
    for m in ours:
        a=acts.get(m)
        if a and a[0]=="move" and MOVES.get(a[1],{}).get("effect")=="EFFECT_EXPLOSION":
            boomer=m; break
    if boomer is not None:
        ally=next((x for x in ours if x is not boomer),None)
        if ally is not None and "TYPE_GHOST" not in ally.types:
            aa=acts.get(ally)
            protecting = aa and aa[0]=="move" and MOVES.get(aa[1],{}).get("effect")=="EFFECT_PROTECT"
            if not protecting:
                if "MOVE_PROTECT" in ally.moves and ally.protect_streak<1:
                    acts[ally]=("move","MOVE_PROTECT",ally)
                else:
                    rule=rule_choose(b)
                    ra=rule.get(boomer)
                    rb = ra and ra[0]=="move" and MOVES.get(ra[1],{}).get("effect")=="EFFECT_EXPLOSION"
                    if ra is not None and not rb:
                        acts[boomer]=ra
    rule=rule_choose(b)
    gross=next((m for m in ours if m.species=="Metagross"),None)
    if gross is not None:
        ra=rule.get(gross)
        if ra is not None and ra[0]=="switch":
            acts[gross]=ra
    return acts
G["our_choose"]=sticky_choose

if __name__=="__main__":
    # 基準シード(10万番台ブロック)での本測定
    BASE=int(sys.argv[1]) if len(sys.argv)>1 else 100000
    N=int(sys.argv[2]) if len(sys.argv)>2 else 20000
    res=collections.Counter(); t0=time.time()
    for i in range(N):
        _battle_no[0]=i+1
        b,r=G["play_battle"](seed=BASE+i)
        res[r]+=1
        if (i+1)%2000==0: print("  ...%d戦 負け%.3f%%"%(i+1,100*res["loss"]/(i+1)),flush=True)
    print("[Zsticky@%d] 負け率 %.3f%% (%d/%d) %.0f戦/分"%(BASE,100*res["loss"]/N,res["loss"],N,N/(time.time()-t0)*60),flush=True)
