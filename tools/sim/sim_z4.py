## Z軸 v0.2 アーム: B=炎退避 C=集中コンボ移植 D=合体とどめ移植 E=ラグ持ち物QC
import os, collections
G={"__file__": os.path.abspath("sim.py")}
exec(open('sim.py').read(),G)
src=open('sim_teams.py').read()
NS=dict(G)
exec(src[src.index("def team_builder"):src.index("import sys")],NS)
team_builder=NS["team_builder"]; generic_choose=NS["generic_choose"]
MOVES=G["MOVES"]; best_attack=G["best_attack"]; cand_has_boom=G["cand_has_boom"]
FIRE={'Charizard','Typhlosion','Ninetales','Entei','Houndoom','Arcanine','Rapidash','Magmar','Moltres','Blaziken'}
def WRspec(swamp_item):
    return [
     ("Zapdos","Modest",{"hp":4,"spa":252,"spe":252},"Leftovers",
      ["MOVE_THUNDERBOLT","MOVE_DRILL_PECK","MOVE_THUNDER_WAVE","MOVE_PROTECT"],"ABILITY_PRESSURE",None),
     ("Metagross","Adamant",{"hp":252,"atk":252,"df":4},"Lum Berry",
      ["MOVE_METEOR_MASH","MOVE_EARTHQUAKE","MOVE_EXPLOSION","MOVE_PROTECT"],"ABILITY_CLEAR_BODY",None),
     ("Latios","Timid",{"hp":4,"spa":252,"spe":252},"Bright Powder",
      ["MOVE_PSYCHIC","MOVE_ICE_BEAM","MOVE_THUNDERBOLT","MOVE_PROTECT"],"ABILITY_LEVITATE","M"),
     ("Swampert","Adamant",{"hp":252,"atk":252,"df":4},swamp_item,
      ["MOVE_EARTHQUAKE","MOVE_ICE_BEAM","MOVE_ROCK_SLIDE","MOVE_PROTECT"],"ABILITY_TORRENT","M"),
    ]
ARM={"fire":False,"focus":False,"pair":False}
def z_choose(b):
    acts=generic_choose(b)
    ours=[m for m in b.active["us"] if m and m.alive()]
    foes=[f for f in b.active["foe"] if f and f.alive()]
    gross=next((m for m in ours if m.species=="Metagross"),None)
    # v0.1 爆発連携(常時)
    boomer=None
    for m in ours:
        a=acts.get(m)
        if a and a[0]=="move" and MOVES.get(a[1],{}).get("effect")=="EFFECT_EXPLOSION":
            boomer=m; break
    if boomer is not None:
        ally=next((x for x in ours if x is not boomer),None)
        if ally is not None and "TYPE_GHOST" not in ally.types:
            if "MOVE_PROTECT" in ally.moves and ally.protect_streak<1:
                acts[ally]=("move","MOVE_PROTECT",ally)
            else:
                ba=best_attack(b,boomer,foes,relax=True)
                if ba: acts[boomer]=("move",ba[0],ba[1])
                elif "MOVE_PROTECT" in boomer.moves: acts[boomer]=("move","MOVE_PROTECT",boomer)
    # B: 炎リード→グロスはラグラージへ退避(T1のみ・爆発プラン時は除く)
    if ARM["fire"] and b.turn==1 and gross is not None and any(f.species in FIRE for f in foes):
        a=acts.get(gross)
        booming = a and a[0]=="move" and MOVES.get(a[1],{}).get("effect")=="EFFECT_EXPLOSION"
        if not booming:
            recv=next((x for x in b.bench["us"] if x.alive() and x.species=="Swampert"),None)
            if recv is not None:
                acts[gross]=("switch",gross,recv)
    # C: 集中コンボ(敵グロスほぼ満タン→じしん+10まん / レジロック→コメパン+サイキネ相当)
    if ARM["focus"] and gross is not None and len(ours)==2:
        mate=next((x for x in ours if x is not gross),None)
        ga=acts.get(gross)
        gross_boom = ga and ga[0]=="move" and MOVES.get(ga[1],{}).get("effect")=="EFFECT_EXPLOSION"
        if not gross_boom and mate is not None:
            egross=next((f for f in foes if f.species=="Metagross" and f.hp*4>f.max_hp*3),None)
            if egross is not None and (gross.choice in (None,"MOVE_EARTHQUAKE")):
                mba=best_attack(b,mate,[egross],relax=True)
                if mba:
                    acts[gross]=("move","MOVE_EARTHQUAKE",egross)
                    acts[mate]=("move",mba[0],egross)
    # D: 自爆持ちHP50%超×合算確殺→2枚集中(C改v0.7移植)
    if ARM["pair"] and len(ours)==2:
        for f in foes:
            if not cand_has_boom(f): continue
            if f.hp*2<=f.max_hp: continue
            skip=False; parts=[]
            for m in ours:
                a=acts.get(m)
                if a and a[0]=="move" and MOVES.get(a[1],{}).get("effect")=="EFFECT_EXPLOSION": skip=True; break
                ba=best_attack(b,m,[f],relax=True)
                if ba and ba[2]>=1.0: skip=True; break
                parts.append((m,ba))
            if skip: continue
            if all(ba for _,ba in parts) and sum(ba[2]*f.hp for _,ba in parts)>=f.hp:
                for m,ba in parts:
                    acts[m]=("move",ba[0],f)
                break
    return acts

N=20000
CASES=[
 ("v0.1基準","Chesto Berry",{}),
 ("B炎退避","Chesto Berry",{"fire":True}),
 ("C集中移植","Chesto Berry",{"focus":True}),
 ("D合体とどめ移植","Chesto Berry",{"pair":True}),
 ("EラグQC","Quick Claw",{}),
 ("B+C+D+E","Quick Claw",{"fire":True,"focus":True,"pair":True}),
]
for label,item,ov in CASES:
    for k in ARM: ARM[k]=ov.get(k,False)
    G["our_team"]=team_builder(WRspec(item)); G["our_choose"]=z_choose
    G["POLICY_VARIANT"]="G"; G["PROTECT_CAP"]=1
    res=collections.Counter(); fapp=0; floss=0
    for i in range(N):
        b,r=G["play_battle"](seed=100000+i)
        res[r]+=1
        if any(m.species in FIRE for m in b.foe[:2]):
            fapp+=1
            if r=="loss": floss+=1
    print("%-12s %.3f%% / 炎リード %.2f%% (%d/%d)"%(label,100*res["loss"]/N,100*floss/max(1,fapp),floss,fapp),flush=True)
