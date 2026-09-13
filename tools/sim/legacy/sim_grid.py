import os, collections, itertools
G={"__file__": os.path.abspath("sim.py")}
exec(open('sim.py').read(),G)
src=open('sim_teams.py').read()
NS=dict(G)
exec(src[src.index("def generic_choose"):src.index("import sys")],NS)
generic_choose=NS["generic_choose"]
make=G["make"]; Mon=G["Mon"]

GROSS=("Metagross","Adamant",{"hp":196,"atk":252,"spe":56,"df":4},"Choice Band",["MOVE_EXPLOSION","MOVE_EARTHQUAKE","MOVE_METEOR_MASH","MOVE_SHADOW_BALL"],"ABILITY_CLEAR_BODY",None)
GENGARS={
 "サポ":("Gengar","Timid",{"hp":224,"spa":32,"spe":252},"Lum Berry",["MOVE_PROTECT","MOVE_PERISH_SONG","MOVE_SUBSTITUTE","MOVE_GIGA_DRAIN"],"ABILITY_LEVITATE","M"),
 "フルアタ":("Gengar","Timid",{"spa":252,"spe":252,"hp":4},"Lum Berry",["MOVE_THUNDERBOLT","MOVE_ICE_PUNCH","MOVE_PSYCHIC","MOVE_PROTECT"],"ABILITY_LEVITATE","M"),
 "攻ほろび":("Gengar","Timid",{"spa":252,"spe":252,"hp":4},"Lum Berry",["MOVE_PERISH_SONG","MOVE_THUNDERBOLT","MOVE_GIGA_DRAIN","MOVE_PROTECT"],"ABILITY_LEVITATE","M"),
}
LAXES={
 "じばく恩返し":("Snorlax","Adamant",{"hp":4,"atk":252,"df":252},"Quick Claw",["MOVE_SELF_DESTRUCT","MOVE_RETURN","MOVE_SHADOW_BALL","MOVE_PROTECT"],"ABILITY_THICK_FAT","M"),
 "のろいじばく":("Snorlax","Adamant",{"hp":188,"atk":252,"df":68},"Quick Claw",["MOVE_CURSE","MOVE_REST","MOVE_SELF_DESTRUCT","MOVE_SHADOW_BALL"],"ABILITY_THICK_FAT","M"),
 "のろい恩返し":("Snorlax","Adamant",{"hp":188,"atk":252,"df":68},"Leftovers",["MOVE_CURSE","MOVE_RETURN","MOVE_SHADOW_BALL","MOVE_REST"],"ABILITY_THICK_FAT","M"),
}
SLOT4={
 "ラティ現行":("Latios","Timid",{"spa":252,"spe":252,"hp":4},"Bright Powder",["MOVE_PSYCHIC","MOVE_ICE_BEAM","MOVE_THUNDERBOLT","MOVE_PROTECT"],"ABILITY_LEVITATE","M"),
 "瞑想ラティ":("Latios","Timid",{"spa":252,"spe":252,"hp":4},"Bright Powder",["MOVE_CALM_MIND","MOVE_PSYCHIC","MOVE_ICE_BEAM","MOVE_PROTECT"],"ABILITY_LEVITATE","M"),
 "瞑想スイクン":("Suicune","Bold",{"hp":252,"df":252,"spd":4},"Chesto Berry",["MOVE_SURF","MOVE_ICE_BEAM","MOVE_CALM_MIND","MOVE_REST"],"ABILITY_PRESSURE",None),
}
def team_builder(spec):
    def build():
        team=[]
        for sp,nat,evs,item,moves,ab,gen in spec:
            d=make(sp,nat,evs,item,moves)
            team.append(Mon(sp,d["types"],ab,item,d["stats"],moves,"us",gender=gen))
        return team
    return build

N=10000
results={}
for gn,ln,sn in itertools.product(GENGARS,LAXES,SLOT4):
    spec=[GENGARS[gn],GROSS,LAXES[ln],SLOT4[sn]]
    G["our_team"]=team_builder(spec); G["our_choose"]=generic_choose
    G["POLICY_VARIANT"]="G"; G["PROTECT_CAP"]=1
    res=collections.Counter()
    for i in range(N):
        b,r=G["play_battle"](seed=100000+i); res[r]+=1
    lr=res["loss"]/N
    results[(gn,ln,sn)]=lr
    print("%-6s x %-7s x %-7s : %.2f%%"%(gn,ln,sn,100*lr),flush=True)

print()
print("=== ランキング ===")
for k,v in sorted(results.items(),key=lambda x:x[1])[:10]:
    print("%.2f%%  %s"%(100*v," x ".join(k)))
print()
print("=== 軸ごとの限界効果（平均負け率）===")
for axis,names in (("ゲンガー",GENGARS),("カビ",LAXES),("4枠目",SLOT4)):
    for nm in names:
        vals=[v for k,v in results.items() if nm in k]
        print("%s=%-8s 平均 %.2f%%"%(axis,nm,100*sum(vals)/len(vals)))
