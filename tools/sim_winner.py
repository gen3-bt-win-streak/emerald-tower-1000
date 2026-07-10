import os, collections
G={"__file__": os.path.abspath("sim.py")}
exec(open('sim.py').read(),G)
src=open('sim_teams.py').read()
NS=dict(G)
exec(src[src.index("def generic_choose"):src.index("import sys")],NS)
generic_choose=NS["generic_choose"]
make=G["make"]; Mon=G["Mon"]; MOVES=G["MOVES"]
W=[
 ("Gengar","Timid",{"spa":252,"spe":252,"hp":4},"Lum Berry",["MOVE_THUNDERBOLT","MOVE_ICE_PUNCH","MOVE_PSYCHIC","MOVE_PROTECT"],"ABILITY_LEVITATE","M"),
 ("Metagross","Adamant",{"hp":196,"atk":252,"spe":56,"df":4},"Choice Band",["MOVE_EXPLOSION","MOVE_EARTHQUAKE","MOVE_METEOR_MASH","MOVE_SHADOW_BALL"],"ABILITY_CLEAR_BODY",None),
 ("Snorlax","Adamant",{"hp":188,"atk":252,"df":68},"Leftovers",["MOVE_CURSE","MOVE_RETURN","MOVE_SHADOW_BALL","MOVE_REST"],"ABILITY_THICK_FAT","M"),
 ("Suicune","Bold",{"hp":252,"df":252,"spd":4},"Chesto Berry",["MOVE_SURF","MOVE_ICE_BEAM","MOVE_CALM_MIND","MOVE_REST"],"ABILITY_PRESSURE",None),
]
def build():
    team=[]
    for sp,nat,evs,item,moves,ab,gen in W:
        d=make(sp,nat,evs,item,moves)
        team.append(Mon(sp,d["types"],ab,item,d["stats"],moves,"us",gender=gen))
    return team
FIRE={'Charizard','Typhlosion','Ninetales','Entei','Houndoom','Arcanine','Rapidash','Magmar','Moltres','Blaziken'}
RECV_SMART=True
GENGAR_RETREAT=True
def max_hit(b,f,m):
    best=0
    for fm in f.moves:
        if fm not in MOVES or MOVES[fm]["power"]<2: continue
        _,hi=b.minmax(f,m,fm)
        best=max(best,hi)
    return best
def winner_choose(b):
    acts=generic_choose(b)
    foes=[m for m in b.active["foe"] if m and m.alive()]
    fire=[f for f in foes if f.species in FIRE]
    gross=next((m for m in b.active["us"] if m and m.alive() and m.species=="Metagross"),None)
    gengar=next((m for m in b.active["us"] if m and m.alive() and m.species=="Gengar"),None)
    # rule 1: fire lead -> gross retreats; receiver picked by incoming threat (Suicune vs Snorlax)
    if b.turn==1 and gross is not None and fire:
        wobb=any(f.species=="Wobbuffet" for f in foes)
        cands=[x for x in b.bench["us"] if x.alive() and x.species in ("Suicune","Snorlax")]
        if cands and not wobb:
            recv=min(cands,key=lambda c: sum(max_hit(b,f,c) for f in foes)/max(1,c.max_hp)) if RECV_SMART else                  next((x for x in cands if x.species=="Suicune"),cands[0])
            acts[gross]=("switch",gross,recv)
            if gengar is not None:
                ga=acts.get(gengar)
                keep = ga and ga[0]=="move" and ga[1] in MOVES and MOVES[ga[1]]["power"]>=2 and ga[2] is not None and b.minmax(gengar,ga[2],ga[1])[0]>=ga[2].hp
                if not keep:
                    acts[gengar]=("move","MOVE_PROTECT",gengar)
    # rule 3: frail Gengar voluntary retreat when pair-lethal and protect unavailable
    if GENGAR_RETREAT and gengar is not None and b.turn>=2:
        ga=acts.get(gengar)
        atk_kills = ga and ga[0]=="move" and ga[1] in MOVES and MOVES[ga[1]]["power"]>=2 and ga[2] is not None and b.minmax(gengar,ga[2],ga[1])[0]>=ga[2].hp
        duo=sum(sorted((max_hit(b,f,gengar) for f in foes),reverse=True)[:2])
        if not atk_kills and duo>=gengar.hp and gengar.protect_streak>=1:
            bench=[x for x in b.bench["us"] if x.alive()]
            if bench:
                recv=min(bench,key=lambda c: sum(max_hit(b,f,c) for f in foes)/max(1,c.max_hp))
                acts[gengar]=("switch",gengar,recv)
    return acts
import json
N=20000
for label,choose in (("汎用のみ",generic_choose),("+炎退避(スイクン受け)",winner_choose)):
    G["our_team"]=build; G["our_choose"]=choose
    G["POLICY_VARIANT"]="G"; G["PROTECT_CAP"]=1
    res=collections.Counter(); cat=collections.Counter()
    for i in range(N):
        b,r=G["play_battle"](seed=100000+i)
        res[r]+=1
        if r=="loss" and any(m.species in FIRE for m in b.foe[:2]): cat["fire"]+=1
    print("%-18s 負け率 %.3f%% (炎負け %d)"%(label,100*res["loss"]/N,cat["fire"]),flush=True)
