import os
G={"__file__": os.path.abspath("sim.py")}
exec(open('sim.py').read(),G)
for k,v in G.items(): globals()[k]=v
POLICY_VARIANT="G"; PROTECT_CAP=1
import collections

def T(spec):
    team=[]
    for sp,nat,evs,item,moves,ab,gen in spec:
        d=make(sp,nat,evs,item,moves)
        team.append(Mon(d["species"],d["types"],d["stats"],0,0,0,0) if False else Mon(sp if sp!="Mr Mime" else sp, d["types"], ab, item, d["stats"], moves, "us", gender=gen))
    return team

TEAMS={
 "A_現行(ゲンガーグロス軸)":[
  ("Gengar","Timid",{"hp":224,"spa":32,"spe":252},"Lum Berry",["MOVE_PROTECT","MOVE_PERISH_SONG","MOVE_SUBSTITUTE","MOVE_GIGA_DRAIN"],"ABILITY_LEVITATE","M"),
  ("Metagross","Adamant",{"hp":196,"atk":252,"spe":56,"df":4},"Choice Band",["MOVE_EXPLOSION","MOVE_EARTHQUAKE","MOVE_METEOR_MASH","MOVE_SHADOW_BALL"],"ABILITY_CLEAR_BODY",None),
  ("Snorlax","Adamant",{"hp":4,"atk":252,"df":252},"Quick Claw",["MOVE_SELF_DESTRUCT","MOVE_RETURN","MOVE_SHADOW_BALL","MOVE_PROTECT"],"ABILITY_THICK_FAT","M"),
  ("Latios","Timid",{"spa":252,"spe":252,"hp":4},"Bright Powder",["MOVE_PSYCHIC","MOVE_ICE_BEAM","MOVE_THUNDERBOLT","MOVE_PROTECT"],"ABILITY_LEVITATE","M")],
 "B_799世界記録型(ラティアス軸)":[
  ("Latias","Timid",{"hp":252,"spa":4,"spe":252},"Bright Powder",["MOVE_CALM_MIND","MOVE_DRAGON_CLAW","MOVE_RECOVER","MOVE_PROTECT"],"ABILITY_LEVITATE","F"),
  ("Swampert","Adamant",{"hp":252,"atk":252,"spd":4},"Leftovers",["MOVE_PROTECT","MOVE_EARTHQUAKE","MOVE_ICE_BEAM","MOVE_SURF"],"ABILITY_TORRENT","M"),
  ("Snorlax","Adamant",{"hp":188,"atk":252,"df":68},"Lum Berry",["MOVE_CURSE","MOVE_RETURN","MOVE_SHADOW_BALL","MOVE_REST"],"ABILITY_THICK_FAT","M"),
  ("Latios","Timid",{"spa":252,"spe":252,"hp":4},"Leftovers",["MOVE_PSYCHIC","MOVE_ICE_BEAM","MOVE_THUNDERBOLT","MOVE_PROTECT"],"ABILITY_LEVITATE","M")],
 "C_70連勝型(スイクン軸)":[
  ("Metagross","Adamant",{"hp":196,"atk":252,"spe":56,"df":4},"Choice Band",["MOVE_METEOR_MASH","MOVE_EARTHQUAKE","MOVE_EXPLOSION","MOVE_SHADOW_BALL"],"ABILITY_CLEAR_BODY",None),
  ("Gengar","Timid",{"spa":252,"spe":252,"hp":4},"Lum Berry",["MOVE_THUNDERBOLT","MOVE_ICE_PUNCH","MOVE_PSYCHIC","MOVE_PROTECT"],"ABILITY_LEVITATE","M"),
  ("Snorlax","Adamant",{"hp":188,"atk":252,"df":68},"Leftovers",["MOVE_CURSE","MOVE_RETURN","MOVE_SHADOW_BALL","MOVE_REST"],"ABILITY_THICK_FAT","M"),
  ("Suicune","Bold",{"hp":252,"df":252,"spd":4},"Chesto Berry",["MOVE_SURF","MOVE_ICE_BEAM","MOVE_CALM_MIND","MOVE_REST"],"ABILITY_PRESSURE",None)],
 "D_トリプル爆弾":[
  ("Gengar","Timid",{"hp":224,"spa":32,"spe":252},"Lum Berry",["MOVE_PROTECT","MOVE_PERISH_SONG","MOVE_SUBSTITUTE","MOVE_GIGA_DRAIN"],"ABILITY_LEVITATE","M"),
  ("Metagross","Adamant",{"hp":196,"atk":252,"spe":56,"df":4},"Choice Band",["MOVE_EXPLOSION","MOVE_EARTHQUAKE","MOVE_METEOR_MASH","MOVE_SHADOW_BALL"],"ABILITY_CLEAR_BODY",None),
  ("Snorlax","Adamant",{"hp":4,"atk":252,"df":252},"Quick Claw",["MOVE_SELF_DESTRUCT","MOVE_RETURN","MOVE_SHADOW_BALL","MOVE_PROTECT"],"ABILITY_THICK_FAT","M"),
  ("Claydol","Adamant",{"hp":252,"atk":252,"spd":4},"Leftovers",["MOVE_EXPLOSION","MOVE_EARTHQUAKE","MOVE_PSYCHIC","MOVE_PROTECT"],"ABILITY_LEVITATE",None)],
 "E_要塞受け":[
  ("Suicune","Bold",{"hp":252,"df":252,"spd":4},"Leftovers",["MOVE_SURF","MOVE_ICE_BEAM","MOVE_CALM_MIND","MOVE_REST"],"ABILITY_PRESSURE",None),
  ("Blissey","Bold",{"hp":252,"df":252,"spd":4},"Chesto Berry",["MOVE_SEISMIC_TOSS","MOVE_SOFT_BOILED","MOVE_THUNDER_WAVE","MOVE_PROTECT"],"ABILITY_NATURAL_CURE","F"),
  ("Skarmory","Impish",{"hp":252,"df":252,"spd":4},"Leftovers",["MOVE_DRILL_PECK","MOVE_TOXIC","MOVE_PROTECT","MOVE_REST"],"ABILITY_STURDY","M"),
  ("Latias","Timid",{"hp":252,"spa":4,"spe":252},"Bright Powder",["MOVE_CALM_MIND","MOVE_DRAGON_CLAW","MOVE_RECOVER","MOVE_PROTECT"],"ABILITY_LEVITATE","F")],
 "F_現行ラティアス差替":[
  ("Gengar","Timid",{"hp":224,"spa":32,"spe":252},"Lum Berry",["MOVE_PROTECT","MOVE_PERISH_SONG","MOVE_SUBSTITUTE","MOVE_GIGA_DRAIN"],"ABILITY_LEVITATE","M"),
  ("Metagross","Adamant",{"hp":196,"atk":252,"spe":56,"df":4},"Choice Band",["MOVE_EXPLOSION","MOVE_EARTHQUAKE","MOVE_METEOR_MASH","MOVE_SHADOW_BALL"],"ABILITY_CLEAR_BODY",None),
  ("Snorlax","Adamant",{"hp":4,"atk":252,"df":252},"Quick Claw",["MOVE_SELF_DESTRUCT","MOVE_RETURN","MOVE_SHADOW_BALL","MOVE_PROTECT"],"ABILITY_THICK_FAT","M"),
  ("Latias","Timid",{"spa":252,"spe":252,"hp":4},"Bright Powder",["MOVE_PSYCHIC","MOVE_ICE_BEAM","MOVE_THUNDERBOLT","MOVE_PROTECT"],"ABILITY_LEVITATE","F")],
}

def team_builder(spec):
    def build():
        team=[]
        for sp,nat,evs,item,moves,ab,gen in spec:
            d=make(sp,nat,evs,item,moves)
            team.append(Mon(sp,d["types"],ab,item,d["stats"],moves,"us",gender=gen))
        return team
    return build

# ---- generic role-based policy (same brain for every team) ----
TH_CM=0.5
TH_GDANGER=1.0
def generic_choose(b):
    acts={}
    foes=[m for m in b.active["foe"] if m and m.alive()]
    ours=[m for m in b.active["us"] if m and m.alive()]
    if not foes:
        for m in ours: acts[m]=("move",m.moves[0],None)
        return acts
    damp_present=any(f.species in ("Golduck","Quagsire") for f in foes)
    def incoming(m):
        hits=[]
        for f in foes:
            best=0
            for fm in f.moves:
                if fm not in MOVES or MOVES[fm]["power"]<2: continue
                _,hi=b.minmax(f,m,fm)
                best=max(best,hi)
            hits.append(best)
        hits.sort(reverse=True)
        return (hits[0] if hits else 0), sum(hits[:2])
    # perish rotation
    used=[]
    for m in ours:
        shadow=any(f.ability=="ABILITY_SHADOW_TAG" for f in foes)
        if m.perish==1 and not m.trapped and not shadow:
            bench=[x for x in b.bench["us"] if x.alive() and x not in used]
            if bench:
                used.append(bench[0]); acts[m]=("switch",m,bench[0])
    for m in ours:
        if m in acts: continue
        boom=next((mv for mv in m.moves if mv in MOVES and MOVES[mv]["effect"]=="EFFECT_EXPLOSION"),None)
        if boom and not damp_present and (m.choice is None or m.choice==boom):
            others=[x for x in ours if x is not m]+[x for x in b.bench["us"] if x.alive()]
            ally=next((x for x in ours if x is not m),None)
            ally_ok = ally is None or b.minmax(m,ally,boom)[1]==0 or "MOVE_PROTECT" in (ally.moves if ally else [])
            kills=sum(1 for t in foes if b.minmax(m,t,boom)[0]>=t.hp)
            if others and ally_ok and kills==len(foes) and kills>=1:
                acts[m]=("move",boom,None); continue
        sung=any(f.perish is not None for f in foes)
        singer="MOVE_PERISH_SONG" in m.moves
        if singer and not sung and foes:
            bench_alive=any(x.alive() for x in b.bench["us"])
            foe_bench=any(x.alive() for x in b.bench["foe"])
            sweep = False
            if bench_alive and not foe_bench and not sweep and not any(f.ability=="ABILITY_SOUNDPROOF" for f in foes):
                jib=[x for x in ours+[y for y in b.bench["us"] if y.alive()] if any(MOVES.get(mv,{}).get("effect")=="EFFECT_EXPLOSION" for mv in x.moves)]
                can_sweep = any(all(b.minmax(x,t,next(mv for mv in x.moves if MOVES[mv]["effect"]=="EFFECT_EXPLOSION"))[0]>=t.hp for t in foes) for x in jib) if jib else False
                if not can_sweep:
                    acts[m]=("move","MOVE_PERISH_SONG",m); continue
        ba=best_attack(b,m,foes)
        solo,duo=incoming(m)
        kill_now= ba and ba[2]>=1.0
        heal=next((mv for mv in m.moves if mv in MOVES and MOVES[mv]["effect"] in ("EFFECT_RESTORE_HP","EFFECT_SOFTBOILED","EFFECT_MOONLIGHT","EFFECT_MORNING_SUN","EFFECT_SYNTHESIS")),None)
        rest="MOVE_REST" in m.moves
        cm=next((mv for mv in m.moves if mv in MOVES and MOVES[mv]["effect"] in ("EFFECT_CALM_MIND","EFFECT_BULK_UP","EFFECT_DRAGON_DANCE","EFFECT_CURSE")),None)
        if kill_now:
            acts[m]=("move",ba[0],ba[1]); continue
        if heal and m.hp*2<m.max_hp and solo<m.hp:
            acts[m]=("move",heal,m); continue
        if rest and m.hp*3<m.max_hp and solo<m.hp:
            acts[m]=("move","MOVE_REST",m); continue
        if cm and duo<m.hp*TH_CM and m.stages.get("spa",0)<2 and m.stages.get("atk",0)<2:
            acts[m]=("move",cm,m); continue
        if (solo>=m.hp*TH_GDANGER or duo>=m.hp*TH_GDANGER) and m.protect_streak<1 and "MOVE_PROTECT" in m.moves:
            acts[m]=("move","MOVE_PROTECT",m); continue
        if (solo>=m.hp) and m.sub==0 and m.hp>m.max_hp//4 and "MOVE_SUBSTITUTE" in m.moves:
            acts[m]=("move","MOVE_SUBSTITUTE",m); continue
        if ba: acts[m]=("move",ba[0],ba[1])
        else:
            ba2=best_attack(b,m,foes,relax=True)
            if ba2: acts[m]=("move",ba2[0],ba2[1])
            elif "MOVE_PROTECT" in m.moves: acts[m]=("move","MOVE_PROTECT",m)
            else: acts[m]=("move",m.moves[0],b.rng.choice(foes))
    return acts

import sys
N=12000
print("=== 構築トーナメント（同一汎用ボット・各%d戦・同一シード）==="%N,flush=True)
results={}
for name,spec in TEAMS.items():
    globals()["our_team"]=team_builder(spec)
    G["our_team"]=globals()["our_team"]
    globals()["our_choose"]=generic_choose
    G["our_choose"]=generic_choose
    # rebind inside engine namespace
    import types
    res=collections.Counter()
    for i in range(N):
        b,r=G["play_battle"](seed=100000+i)
        res[r]+=1
    results[name]=res["loss"]/N
    print("%-28s 負け率 %.2f%%"%(name,100*res["loss"]/N),flush=True)
print()
for name,lr in sorted(results.items(),key=lambda x:x[1]):
    print("%.2f%%  %s"%(100*lr,name))
