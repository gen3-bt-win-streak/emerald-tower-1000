import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
G={'__file__':'calc_matchups.py'}
exec(open('calc_matchups.py').read().split("# ---------- Analysis 1")[0], G)
make=G['make']; damage_range=G['damage_range']; pool=G['pool']
BYID={e["set_id"]:e for e in pool}
IV=dict(G['IV31']); IV['atk']=2
z  = make("Zapdos","Modest",{"hp":4,"spa":252,"spe":252},"Lum Berry",[],ivs=IV)
IVL=dict(G['IV31']); IVL['atk']=0
la = make("Latios","Timid",{"hp":4,"spa":252,"spe":252},"Bright Powder",[],ivs=IVL)
mg = make("Metagross","Adamant",{"hp":252,"atk":244,"spd":8,"spe":4},"Quick Claw",[])
sw = make("Swampert","Adamant",{"hp":252,"atk":252,"spe":4},"Leftovers",[])
def tag(lo,hi,hp):
    if lo>=hp: return "確1"
    if hi>=hp: return "乱1 %.1f%%"%(100*(hi-hp+1)/(hi-lo+1))
    return "耐(%.0f%%)"%(100*hi/hp)
print("自軍S: サンダー%d ラティオス%d メタグロス%d ラグラージ%d"%(
    z["stats"]["spe"],la["stats"]["spe"],mg["stats"]["spe"],sw["stats"]["spe"]))
for sid in (435,531,627,723):
    e=BYID[sid]; hp=e["stats31"]["hp"]
    dfd={"stats":e["stats31"],"types":e["types"],"ability":e["abilities"][0],
         "item":e["item"],"species":e["species"],"level":100}
    print(f"\n=== #{sid} @{e['item']} HP{hp} S{e['stats31']['spe']} ===")
    for nm,d,mvs in (("サンダー",z,["MOVE_THUNDERBOLT","MOVE_HP_ICE"]),
                     ("ラティオス",la,["MOVE_PSYCHIC","MOVE_ICE_BEAM","MOVE_THUNDERBOLT"]),
                     ("メタグロス",mg,["MOVE_METEOR_MASH","MOVE_EXPLOSION"]),
                     ("ラグラージ",sw,["MOVE_ICE_BEAM"])):
        for mv in mvs:
            lo,hi=damage_range(d,dfd,mv)
            print(f"   {nm:6s} {mv.replace('MOVE_',''):13s} {lo}-{hi} {tag(lo,hi,hp)}")
