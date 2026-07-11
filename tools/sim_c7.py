## C改v0.7最終合成の確定検証: argv = plain|final [seedbase]
import os, sys, collections, json
G={"__file__": os.path.abspath("sim.py")}
exec(open('sim.py').read(),G)
src=open('sim_teams.py').read()
NS=dict(G)
exec(src[src.index("TH_CM=0.5"):src.index("import sys")],NS)
generic_choose=NS["generic_choose"]
make=G["make"]; Mon=G["Mon"]; MOVES=G["MOVES"]
w2=open('sim_w2.py').read()
exec(w2[w2.index("W=["):w2.index("import json")])
RECV_SMART=True; GENGAR_RETREAT=False
SUB=["MOVE_THUNDERBOLT","MOVE_PSYCHIC","MOVE_SUBSTITUTE","MOVE_PROTECT"]
def bld(moves):
    def f():
        spec=list(W)
        spec[0]=("Gengar","Timid",{"hp":224,"spa":32,"spe":252},"Lum Berry",moves,"ABILITY_LEVITATE","M")
        team=[]
        for sp,nat,evs,item,mv,ab,gen in spec:
            d=make(sp,nat,evs,item,mv)
            team.append(Mon(sp,d["types"],ab,item,d["stats"],mv,"us",gender=gen))
        return team
    return f
best_attack=G["best_attack"]; cand_has_boom=G["cand_has_boom"]
CFG=sys.argv[1] if len(sys.argv)>1 else "final"
BASE=int(sys.argv[2]) if len(sys.argv)>2 else 400000
FINAL = CFG=="final"
if FINAL:
    P=json.load(open("learned_C7.json"))
    G["FORTRESS_THRESH"]=P["fort"]; G["TH_LAX_ATK"]=P["laxatk"]
    G["TH_DANGER"]=P["danger"]; G["TH_SOLO"]=P["solo"]
    NS["TH_CM"]=P["cm"]; NS["TH_GDANGER"]=P["gdanger"]
def early_rest(b,acts,species,th):
    m=next((x for x in b.active["us"] if x and x.alive() and x.species==species),None)
    if m is None: return
    foes=[f for f in b.active["foe"] if f and f.alive()]
    if not foes: return
    solo=max(max_hit(b,f,m) for f in foes)
    ba=best_attack(b,m,foes)
    if ba and ba[2]>=1.0: return
    if "MOVE_REST" in m.moves and m.hp<m.max_hp*th and solo<m.hp and m.hp+solo<m.max_hp+1:
        acts[m]=("move","MOVE_REST",m)
def pair_finish(b,acts):
    ours=[m for m in b.active["us"] if m and m.alive()]
    if len(ours)!=2: return
    foes=[f for f in b.active["foe"] if f and f.alive()]
    for f in foes:
        if not cand_has_boom(f): continue
        if f.hp*2<=f.max_hp: continue
        solo_kill=False; parts=[]
        for m in ours:
            a=acts.get(m)
            if a and a[0]=="move" and MOVES.get(a[1],{}).get("effect")=="EFFECT_EXPLOSION": return
            ba=best_attack(b,m,[f],relax=True)
            if ba and ba[2]>=1.0: solo_kill=True
            parts.append((m,ba))
        if solo_kill: continue
        if all(ba for _,ba in parts):
            tot=sum(ba[2]*f.hp for _,ba in parts)
            if tot>=f.hp:
                for m,ba in parts:
                    acts[m]=("move",ba[0],f)
                return
def gengar_sub_early(b,acts):
    g=next((x for x in b.active["us"] if x and x.alive() and x.species=="Gengar"),None)
    if g is None or g.sub>0 or g.hp<=g.max_hp//4 or "MOVE_SUBSTITUTE" not in g.moves: return
    foes=[f for f in b.active["foe"] if f and f.alive()]
    if not foes: return
    ba=best_attack(b,g,foes)
    if ba and ba[2]>=1.0: return
    a=acts.get(g)
    if a and a[0]=="move" and a[1] in ("MOVE_PROTECT","MOVE_SUBSTITUTE"): return
    solo=max(max_hit(b,f,g) for f in foes)
    if solo>=g.hp*0.65:
        acts[g]=("move","MOVE_SUBSTITUTE",g)
def choose(b):
    acts=winner_choose(b)
    early_rest(b,acts,"Suicune",0.6)
    early_rest(b,acts,"Snorlax",0.6)
    pair_finish(b,acts)
    if FINAL: gengar_sub_early(b,acts)
    return acts
N=20000
G["our_team"]=bld(SUB); G["our_choose"]=(choose if FINAL else winner_choose)
G["POLICY_VARIANT"]="G"; G["PROTECT_CAP"]=1
res=collections.Counter(); streak=0; best_streak=0
for i in range(N):
    b,r=G["play_battle"](seed=BASE+i)
    res[r]+=1
    if r=="win": streak+=1; best_streak=max(best_streak,streak)
    else: streak=0
print("[%s@%d] 負け率 %.3f%% (%d/%d) 最長連勝 %d"%(CFG,BASE,100*res["loss"]/N,res["loss"],N,best_streak),flush=True)
