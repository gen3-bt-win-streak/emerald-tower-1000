# -*- coding: utf-8 -*-
"""メタグロス／ラグラージの耐久指標（546セット総当たり）— 19章§3と同じ方式"""
import statistics, sys
G={'__file__':'calc_matchups.py'}
exec(open('calc_matchups.py').read().split("# ---------- Analysis 1")[0], G)
make=G['make']; damage_range=G['damage_range']; pool=G['pool']; MOVES=G['MOVES']

def build(sp, nature, evs, item, ability, ivs=None, over=None):
    d=make(sp,nature,evs,item,[],ability=ability, ivs=(ivs or G['IV31']))
    if over: d["stats"].update(over)
    return d

IVW=dict(G['IV31']); IVW.update(df=30, spd=22, spe=30)   # めざ岩70個体 E6BA7F73
TARGETS={
 "メタグロス v4.1 (A228/B0/D24)": build("Metagross","Adamant",{"hp":252,"atk":228,"spd":24,"spe":4},"Quick Claw","ABILITY_CLEAR_BODY"),
 "メタグロス 次走 (A244/B0/D8)":  build("Metagross","Adamant",{"hp":252,"atk":244,"spd":8,"spe":4},"Quick Claw","ABILITY_CLEAR_BODY"),
 "ラグラージ (H252/A252/S4)":     build("Swampert","Adamant",{"hp":252,"atk":252,"spe":4},"Leftovers","ABILITY_TORRENT",ivs=IVW),
}
def best_dmg(d, crit=False):
    """各敵セットの最大打点(最大ロール)を返す"""
    out=[]
    for e in pool:
        att={"stats":e["stats31"],"types":e["types"],"ability":e["abilities"][0],
             "item":e["item"],"species":e["species"],"level":100}
        lo=hi=0
        for mv in e["moves"]:
            if mv not in MOVES: continue
            if MOVES[mv]["effect"]=="EFFECT_OHKO": continue   # 一撃技は別枠
            a,b=damage_range(att,d,mv,crit=crit)
            if b>hi: lo,hi=a,b
        out.append((e,lo,hi))
    return out

for name,d in TARGETS.items():
    hp=d["stats"]["hp"]; lefty = hp//16 if d["item"]=="Leftovers" else 0
    res=best_dmg(d); resc=best_dmg(d,crit=True)
    k1=[e for e,lo,hi in res if lo>=hp]
    r1=[e for e,lo,hi in res if lo<hp<=hi]
    k2=[e for e,lo,hi in res if hi<hp and lo*2>=hp]
    med=statistics.median([hi for e,lo,hi in res if hi>0]) if res else 0
    medall=statistics.median([hi for e,lo,hi in res])
    ck1=[e for e,lo,hi in resc if lo>=hp]
    zero=[e for e,lo,hi in res if hi==0]
    net=medall-lefty
    print(f"\n=== {name} ===")
    print(f"  実数値 HP{hp} / B{d['stats']['df']} / D{d['stats']['spd']} / S{d['stats']['spe']}"
          + (f" / たべのこし +{lefty}/T" if lefty else " / 回復なし"))
    print(f"  被確定OHKO      {len(k1):3d} / 546")
    print(f"  被乱数OHKO      {len(r1):3d}")
    print(f"  被確定2発       {len(k2):3d}")
    print(f"  打点ゼロ(無効)  {len(zero):3d}")
    print(f"  中央値ダメージ  {medall:.0f}  (実質 {net:.0f}/T)")
    print(f"  生存ターン      {hp/net:.1f}T  (単体・中央値基準)")
    print(f"  ダブル2体分     {hp/max(1,2*medall-lefty):.1f}T")
    print(f"  【急所時】被確定OHKO {len(ck1):3d}")
    top=sorted(res,key=lambda x:-x[2])[:6]
    print("  最大打点トップ6:")
    for e,lo,hi in top:
        print(f"    #{e['set_id']:4d} {e['species']:12s} {lo}-{hi} ({100*hi/hp:.0f}%)")
    if k1:
        print(f"  被確定OHKO一覧: "+", ".join(f"#{e['set_id']}{e['species']}" for e in k1[:20]))
