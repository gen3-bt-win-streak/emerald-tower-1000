# -*- coding: utf-8 -*-
"""v4.1 全16技の限界価値監査（546セット総当たり）"""
import collections
G={'__file__':'calc_matchups.py'}
exec(open('calc_matchups.py').read().split("# ---------- Analysis 1")[0], G)
make=G['make']; damage_range=G['damage_range']; pool=G['pool']; MOVES=G['MOVES']
MOVES["MOVE_HP_ROCK"]=dict(MOVES["MOVE_ROCK_SLIDE"]); MOVES["MOVE_HP_ROCK"].update(power=70,accuracy=100,effect="EFFECT_HIT",target="MOVE_TARGET_SELECTED")
IVZ=dict(G['IV31']); IVZ['atk']=2
IVL=dict(G['IV31']); IVL['atk']=0
IVW=dict(G['IV31']); IVW.update(df=30,spd=22,spe=30)
Z =make("Zapdos","Modest",{"hp":4,"spa":252,"spe":252},"Lum Berry",[],ivs=IVZ)
MG=make("Metagross","Adamant",{"hp":252,"atk":244,"spd":8,"spe":4},"Quick Claw",[])
LA=make("Latios","Timid",{"hp":4,"spa":252,"spe":252},"Bright Powder",[],ivs=IVL)
SW=make("Swampert","Adamant",{"hp":252,"atk":252,"spe":4},"Leftovers",[],ivs=IVW)
KIT=[("サンダー","10まんボルト",Z,"MOVE_THUNDERBOLT"),
     ("サンダー","めざ氷70",Z,"MOVE_HP_ICE"),
     ("メタグロス","コメットパンチ",MG,"MOVE_METEOR_MASH"),
     ("メタグロス","じしん",MG,"MOVE_EARTHQUAKE"),
     ("メタグロス","だいばくはつ",MG,"MOVE_EXPLOSION"),
     ("ラティオス","サイコキネシス",LA,"MOVE_PSYCHIC"),
     ("ラティオス","れいとうビーム",LA,"MOVE_ICE_BEAM"),
     ("ラティオス","10まんボルト",LA,"MOVE_THUNDERBOLT"),
     ("ラグラージ","じしん",SW,"MOVE_EARTHQUAKE"),
     ("ラグラージ","れいとうビーム",SW,"MOVE_ICE_BEAM"),
     ("ラグラージ","めざ岩70",SW,"MOVE_HP_ROCK")]
def dfd(e): return {"stats":e["stats31"],"types":e["types"],"ability":e["abilities"][0],
                    "item":e["item"],"species":e["species"],"level":100}
k1={}; touch={}; maxd={}
for own,label,d,m in KIT:
    key=(own,label); s=set(); t=set(); mm={}
    for e in pool:
        lo,hi=damage_range(d,dfd(e),m)
        mm[e["set_id"]]=hi
        if hi>0: t.add(e["set_id"])
        if lo>=e["stats31"]["hp"]: s.add(e["set_id"])
    k1[key]=s; touch[key]=t; maxd[key]=mm
print("=== 各技の確定OHKO数と『その技を抜くと失われる唯一の確1』===")
print(f"{'持ち主':10s} {'技':16s} {'確1':>4s} {'単独確1':>6s} {'打点ゼロ':>7s}  失う相手")
for own,label,d,m in KIT:
    key=(own,label)
    others=set().union(*[v for kk,v in k1.items() if kk!=key])
    uniq=k1[key]-others
    names=[f"#{i}{[e for e in pool if e['set_id']==i][0]['species']}" for i in sorted(uniq)][:8]
    print(f"{own:10s} {label:16s} {len(k1[key]):4d} {len(uniq):6d} {546-len(touch[key]):7d}  {' '.join(names)}")
print("\n=== 持ち主ごと：その技を抜くと『自分が一切触れなくなる』敵が何体増えるか ===")
for own in ("サンダー","メタグロス","ラティオス","ラグラージ"):
    mine=[(l,d,m) for o,l,d,m in KIT if o==own]
    base=set()
    for e in pool:
        if max(damage_range(d,dfd(e),m)[1] for l,d,m in mine)==0: base.add(e["set_id"])
    print(f" {own}（現状 触れない {len(base)}）")
    for l,d,m in mine:
        rest=[x for x in mine if x[0]!=l]
        if not rest: continue
        z=set()
        for e in pool:
            if max(damage_range(dd,dfd(e),mm)[1] for _,dd,mm in rest)==0: z.add(e["set_id"])
        print(f"   {l:16s} を抜くと → {len(z)} (+{len(z)-len(base)})")
print("\n=== 『その技が持ち主の最大打点になる』セット数（削り効率の指標）===")
for own in ("サンダー","メタグロス","ラティオス","ラグラージ"):
    mine=[(l,d,m) for o,l,d,m in KIT if o==own]
    cnt=collections.Counter()
    for e in pool:
        best=max(mine,key=lambda x: damage_range(x[1],dfd(e),x[2])[1])
        if damage_range(best[1],dfd(e),best[2])[1]>0: cnt[best[0]]+=1
    print(f" {own}: {dict(cnt)}")
