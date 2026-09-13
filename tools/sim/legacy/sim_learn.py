import os, collections, random, json, time
G={"__file__": os.path.abspath("sim.py")}
exec(open('sim.py').read(),G)
src=open('sim_teams.py').read()
NS=dict(G)
exec(src[src.index("TH_CM=0.5"):src.index("import sys")],NS)
generic_choose=NS["generic_choose"]
make=G["make"]; Mon=G["Mon"]; MOVES=G["MOVES"]
w2=open('sim_w2.py').read()
exec(w2[w2.index("W=["):w2.index("import json")])
W[0]=("Gengar","Timid",{"hp":224,"spa":32,"spe":252},"Lum Berry",
      ["MOVE_THUNDERBOLT","MOVE_ICE_PUNCH","MOVE_PSYCHIC","MOVE_PROTECT"],"ABILITY_LEVITATE","M")
RECV_SMART=True; GENGAR_RETREAT=False
rnd=random.Random(7)

def eval_team(team_kind, params, n, seed0):
    G["FORTRESS_THRESH"]=params.get("fort",0.50)
    G["TH_LAX_ATK"]=params.get("laxatk",0.25)
    G["TH_DANGER"]=params.get("danger",1.0)
    G["TH_SOLO"]=params.get("solo",1.0)
    NS["TH_CM"]=params.get("cm",0.5)
    NS["TH_GDANGER"]=params.get("gdanger",1.0)
    if team_kind=="A":
        G["our_team"]=G_ORIG_TEAM; G["our_choose"]=G_ORIG_CHOOSE
    else:
        G["our_team"]=build; G["our_choose"]=winner_choose
    G["POLICY_VARIANT"]="G"; G["PROTECT_CAP"]=1
    loss=0
    for i in range(n):
        _,r=G["play_battle"](seed=seed0+i)
        if r=="loss": loss+=1
    return loss/n

G_ORIG_TEAM=G["our_team"]; G_ORIG_CHOOSE=G["our_choose"]
SPACE={"fort":(0.35,0.65),"laxatk":(0.1,0.5),"danger":(0.7,1.3),"solo":(0.7,1.3),"cm":(0.3,0.8),"gdanger":(0.7,1.3)}
for team in ("A","C"):
    base=eval_team(team,{},12000,100000)
    best=({},base)
    print("[%s] 基準(フェア情報) %.3f%%"%(team,100*base),flush=True)
    for it in range(60):
        p={k:round(rnd.uniform(*v),2) for k,v in SPACE.items()}
        lr=eval_team(team,p,12000,100000)
        if lr<best[1]:
            best=(p,lr)
            print("[%s] it%d 改善 %.3f%% %s"%(team,it,100*lr,p),flush=True)
    # validate on fresh seeds
    val=eval_team(team,best[0],20000,300000)
    valb=eval_team(team,{},20000,300000)
    print("[%s] 最終: 学習後%.3f%% vs 基準%.3f%%（新シード20k検証） params=%s"%(team,100*val,100*valb,best[0]),flush=True)
    json.dump(best[0],open("learned_%s.json"%team,"w"))
