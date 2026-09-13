## 2手読み探索ボット（決定化サンプリングexpectimax・情報パリティ維持）
## 方式: 危険局面でのみ起動。候補手（ルール手+一点変更）×サンプル世界S×乱数R で
##       そのターンを完全シミュレート→残り深さはオートパイロット→局面評価の平均で選択。
## 覗き見なし: 世界は候補セットからサンプルして実セットを上書き（ロールアウト内の参照は全てサンプル）
import copy, random
_src=open('sim_v08fair.py').read()
exec(_src[:_src.index("BASE=int")])   # エンジン+公平max_hit+v0.8 choose+bld を継承
ai_choose=G["ai_choose"]; STAGE_KEYS=G["STAGE_KEYS"]; cand_entries=G["cand_entries"]

S=2; R=2; D=3; MARGIN=0.5
_battle_no=[0]

# ---- 行動の抽象記述（deepcopy間で翻訳可能に） ----
def describe(b,acts):
    out=[]
    for i,m in enumerate(b.active["us"]):
        if m is None or not m.alive(): out.append(None); continue
        a=acts.get(m)
        if a is None: out.append(None); continue
        if a[0]=="switch":
            out.append(("switch",b.bench["us"].index(a[2]) if a[2] in b.bench["us"] else 0)); continue
        t=a[2]
        if t is None: td=("us",i)
        elif t.side=="foe": td=("foe",b.active["foe"].index(t) if t in b.active["foe"] else 0)
        else: td=("us",b.active["us"].index(t) if t in b.active["us"] else i)
        out.append(("move",a[1],td))
    return out
def apply_desc(bc,desc):
    acts={}
    for i,d in enumerate(desc):
        m=bc.active["us"][i]
        if m is None or not m.alive() or d is None: continue
        if d[0]=="switch":
            idx=d[1]
            if idx<len(bc.bench["us"]) and bc.bench["us"][idx].alive():
                acts[m]=("switch",m,bc.bench["us"][idx])
            continue
        _,mv,td=d
        if td[0]=="foe":
            t=bc.active["foe"][td[1]] if td[1]<len(bc.active["foe"]) else None
            if t is None or not t.alive():
                alive=[f for f in bc.active["foe"] if f and f.alive()]
                t=alive[0] if alive else None
        else:
            t=bc.active["us"][td[1]]
        acts[m]=("move",mv,t)
    return acts

# ---- 世界サンプリング ----
def sample_world(b,wrnd,rollseed):
    bc=copy.deepcopy(b)
    bc.rng=random.Random(rollseed)
    bc.log=[]
    for m in bc.foe:
        es=cand_entries(m)
        if not es: continue
        e=wrnd.choice(es)
        st=e["stats31"] if bc.enemy_iv>=31 else e["stats21"]
        frac=m.hp/m.max_hp
        alive=m.hp>0
        m.stats=dict(st); m.max_hp=st["hp"]
        m.hp=max(1,int(round(frac*st["hp"]))) if alive else 0
        m.types=list(e["types"])
        abil=[a for a in e["abilities"] if a!="ABILITY_NONE"]
        m.ability=wrnd.choice(abil) if abil else "ABILITY_NONE"
        m.item=e["item"]; m.moves=list(e["moves"]); m.set_id=e["set_id"]
    return bc

# ---- 1ターン完全シミュレート（play_battleのループ本体を忠実に再現） ----
def sim_turn(bc,our_acts):
    bc.turn+=1
    if bc.turn>120: return "loss"
    for m in bc.active["us"]+bc.active["foe"]:
        if m: m.protected=False; m.endure=False; m.flinch=False; m.dmg_phys=(0,None); m.dmg_spec=(0,None); m.took_dmg=False; m.destiny=False
    foe_acts={}
    for m in bc.active["foe"]:
        if m and m.alive():
            if m.perish==1 and not m.trapped and not any(x is not None and x.alive() and x.ability=="ABILITY_SHADOW_TAG" for x in bc.active["us"]):
                bench=[x for x in bc.bench["foe"] if x.alive()]
                if bench:
                    foe_acts[m]=("switch",m,bench[0]); continue
            foe_acts[m]=ai_choose(bc,m)
    allacts=[]; swapped={}
    for m,a in list(our_acts.items())+list(foe_acts.items()):
        if a[0]=="switch":
            side=m.side
            if a[2] not in bc.bench[side] or not a[2].alive() or m not in bc.active[side]: continue
            idx=bc.active[side].index(m)
            bc.bench[side].append(m); bc.bench[side].remove(a[2]); bc.active[side][idx]=a[2]
            a[2].choice=None
            m.perish=None; m.stages={k:0 for k in STAGE_KEYS}; m.acc_st=0; m.eva_st=0; m.sub=0; m.attract=False; m.cnf=0
            swapped[m]=a[2]
            bc.on_entry(a[2])
        else:
            allacts.append((m,a))
    if swapped:
        allacts=[(m,(a[0],a[1],swapped.get(a[2],a[2]))) for m,a in allacts]
    qc_proc=bc.rng.random()<0.20
    def order_key(item):
        m,a=item
        mv=a[1]
        pri=MOVES[mv]["priority"] if mv in MOVES else 0
        qc=1 if (qc_proc and m.item=="Quick Claw") else 0
        return (-pri,-qc,-m.eff()["spe"],bc.rng.random())
    allacts.sort(key=order_key)
    for m,a in allacts:
        if not m.alive(): continue
        if m not in bc.active["us"]+bc.active["foe"]: continue
        bc.execute(m,a)
        r=bc.result()
        if r: return r
    bc.end_turn()
    r=bc.result()
    if r: return r
    bc.replace_fainted()
    return bc.result()

# ---- 評価関数 ----
def score(bc,r,tused):
    if r=="win": return 100.0-tused
    if r=="loss": return -100.0
    s=0.0
    for m in bc.us: s+=(m.hp/m.max_hp+0.7) if m.alive() else 0.0
    for m in bc.foe: s-=(m.hp/m.max_hp+0.7) if m.alive() else 0.0
    return s*10.0-tused*0.3

def rollout(b,desc,wseed,rseed):
    bc=sample_world(b,random.Random(wseed),rseed)
    r=sim_turn(bc,apply_desc(bc,desc))
    t=1
    while r is None and t<D:
        r=sim_turn(bc,choose(bc))
        t+=1
    return score(bc,r,t)

# ---- 候補手生成: ルール手 + 一点変更 ----
def gen_candidates(b,rule_acts):
    base=describe(b,rule_acts)
    cands=[base]
    for i,m in enumerate(b.active["us"]):
        if m is None or not m.alive(): continue
        alts=[]
        for j,f in enumerate(b.active["foe"]):
            if f is None or not f.alive(): continue
            ba=best_attack(b,m,[f],relax=True)
            if ba: alts.append(("move",ba[0],("foe",j)))
        if "MOVE_PROTECT" in m.moves: alts.append(("move","MOVE_PROTECT",("us",i)))
        if "MOVE_SUBSTITUTE" in m.moves and m.sub==0: alts.append(("move","MOVE_SUBSTITUTE",("us",i)))
        if "MOVE_REST" in m.moves and m.hp<m.max_hp: alts.append(("move","MOVE_REST",("us",i)))
        if "MOVE_CALM_MIND" in m.moves: alts.append(("move","MOVE_CALM_MIND",("us",i)))
        if "MOVE_CURSE" in m.moves: alts.append(("move","MOVE_CURSE",("us",i)))
        for a in alts:
            if base[i]==a: continue
            d=list(base); d[i]=a; cands.append(d)
    uniq=[]; seen=set()
    for d in cands:
        k=repr(d)
        if k not in seen: seen.add(k); uniq.append(d)
    return uniq[:12]

# ---- 起動条件: 危険局面のみ ----
def should_search(b):
    foes=[f for f in b.active["foe"] if f and f.alive()]
    ours=[m for m in b.active["us"] if m and m.alive()]
    if not foes or not ours: return False
    for m in ours:
        hits=sorted((max_hit(b,f,m) for f in foes),reverse=True)
        if sum(hits[:2])>=m.hp: return True
    for f in foes:
        if cand_has_boom(f) and f.hp*2>f.max_hp: return True
    return False

SEARCH_ON=True
_stats={"turns":0,"searched":0,"deviated":0}
def search_choose(b):
    if b.turn==0: _battle_no[0]+=1
    _stats["turns"]+=1
    rule=choose(b)
    if not SEARCH_ON or not should_search(b): return rule
    _stats["searched"]+=1
    cands=gen_candidates(b,rule)
    if len(cands)<=1: return rule
    bno=_battle_no[0]
    scores=[]
    for ci,d in enumerate(cands):
        tot=0.0
        for s in range(S):
            wseed=(bno*7919+b.turn*131+s*17)&0x7FFFFFFF
            for k in range(R):
                rseed=(bno*104729+b.turn*257+ci*31+s*7+k)&0x7FFFFFFF
                tot+=rollout(b,d,wseed,rseed)
        scores.append(tot/(S*R))
    rule_score=scores[0]
    bi=max(range(len(cands)),key=lambda i:scores[i])
    if bi==0 or scores[bi]<rule_score+MARGIN: return rule
    _stats["deviated"]+=1
    return apply_desc(b,cands[bi])

# ---- 実行 ----
if __name__=="__main__" or True:
    import sys, collections, time
    if "SMOKE" in os.environ:
        N=int(os.environ.get("SMOKE","300")); BASE=100000
    else:
        N=int(sys.argv[2]) if len(sys.argv)>2 else 20000
        BASE=int(sys.argv[1]) if len(sys.argv)>1 else 100000
    G["our_team"]=bld; G["our_choose"]=search_choose
    G["POLICY_VARIANT"]="G"; G["PROTECT_CAP"]=1
    t0=time.time()
    res=collections.Counter()
    for i in range(N):
        _battle_no[0]+=1
        b,r=G["play_battle"](seed=BASE+i)
        res[r]+=1
        if (i+1)%2000==0:
            print("  ...%d戦 負け%.3f%% (%.0f戦/分)"%(i+1,100*res["loss"]/(i+1),(i+1)/max(1,(time.time()-t0))*60),flush=True)
    dt=time.time()-t0
    print("[探索@%d] 負け率 %.3f%% (%d/%d)  %.0f戦/分  探索率%.0f%% 逸脱%d回"%(
        BASE,100*res["loss"]/N,res["loss"],N,N/dt*60,
        100*_stats["searched"]/max(1,_stats["turns"]),_stats["deviated"]),flush=True)
