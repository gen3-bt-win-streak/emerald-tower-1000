"""こころのめ／零度／リフレクター／くろいきり の4技案を、後出しモデルで測る。
pivot_articuno.py のロジックを踏襲し、リフレクターの軽減を ダブル敵2体生存の ×2/3
（pokemon.c:3269）に修正。両手を状況で選べる前提で per-set の max を取る。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from evlib import *
import evlib
from collections import Counter
tm = evlib._G['type_mult']
LATIOS = make("Latios","Timid",{"hp":40,"spa":252,"spe":216},"Lum Berry",["MOVE_PSYCHIC"])
IV=dict(evlib._G["IV31"]); IV["atk"]=0; IV["spa"]=29
ART = make("Articuno","Calm",{"hp":236,"df":208,"spd":60,"spe":4},"Leftovers",
           ["MOVE_SHEER_COLD"], ability="ABILITY_PRESSURE", ivs=IV)
HP=ART["stats"]["hp"]; SPE=ART["stats"]["spe"]

def maxdmg(e, defender, reflect=False, mode="double2"):
    best=(0,None,False)
    for mk in e["moves"]:
        mv=MOVES[mk]
        if mv["power"]<2 or mv["effect"]=="EFFECT_OHKO": continue
        for ab in abil(e):
            att=dict(stats=e["stats31"],types=e["types"],ability=ab,item=e["item"],species=e["species"],level=100)
            lo,hi=damage_range(att,defender,mk); a,b=evlib._hitmult(mk); hi*=b
            phys=mv["type"] in PHYSICAL
            if reflect and phys:
                hi = 2*(hi//3) if mode=="double2" else hi//2
            if hi>best[0]: best=(hi,mk,phys)
    return best

def k_actions(e, first_hit, reflect=False, mode="double2", cap=30):
    hp=HP-first_hit
    if hp<=0: return 0
    dmg,mk,phys = maxdmg(e,ART,reflect,mode)
    k=0
    for _ in range(cap):
        if SPE > e["stats31"]["spe"]:
            k+=1; hp-=dmg
            if hp<=0: return k
        else:
            hp-=dmg
            if hp<=0: return k
            k+=1
        hp=min(HP, hp+HP//16)
    return cap

def immune(e): return "ABILITY_STURDY" in abil(e) or e["species"]=="Shedinja"

rows=[]
for i,e in enumerate(pool):
    se=[mk for mk in e["moves"] if MOVES[mk]["power"]>=2 and MOVES[mk]["effect"]!="EFFECT_OHKO"
        and tm(MOVES[mk]["type"], LATIOS["types"], None)>=20]
    if not se: continue
    worst=0; wmk=None
    for mk in se:
        if tm(MOVES[mk]["type"], ART["types"], None) > 10: continue
        for ab in abil(e):
            att=dict(stats=e["stats31"],types=e["types"],ability=ab,item=e["item"],species=e["species"],level=100)
            lo,hi=damage_range(att,ART,mk); a,b=evlib._hitmult(mk); hi*=b
            if hi>worst: worst,wmk=hi,mk
    if wmk is None: continue
    k0=k_actions(e,worst)
    kR2=k_actions(e,worst,reflect=True,mode="double2")
    kR1=k_actions(e,worst,reflect=True,mode="single")
    imm=immune(e)
    e1 = 0 if imm else (1.0 if k0>=2 else (0.29 if k0==1 else 0))
    sc = 0 if imm else 1-0.71**k0
    # リフレクター→零度（x2/3）
    rf = 0 if imm else max(sc, (1-0.71**(kR2-1)) if kR2>=2 else 0)
    # リフレクター→こころのめ→零度：リフ1手のあと k' で E1 判定
    e1R = 0 if imm else (1.0 if kR2>=3 else (0.29 if kR2==2 else 0))
    rows.append(dict(i=i,name=name(i),k=k0,kR2=kR2,kR1=kR1,imm=imm,e1=e1,sc=sc,rf=rf,e1R=e1R,
                     both=max(e1,rf,e1R), phys=maxdmg(e,ART)[2]))
n=len(rows)
print(f"後出し対象P = {n} セット")
print(f"k分布: {dict(sorted(Counter(min(r['k'],6) for r in rows).items()))}")
print(f"kR分布(リフ x2/3): {dict(sorted(Counter(min(r['kR2'],6) for r in rows).items()))}")
print()
for key,label in (("e1","こころのめ+零度（現行4技）"),
                  ("rf","リフレクター+零度"),
                  ("e1R","リフレクター→こころのめ→零度"),
                  ("both","【新案】4技で状況に応じて選ぶ")):
    tot=sum(r[key] for r in rows); cert=sum(1 for r in rows if r[key]>=0.99)
    print(f"  {label:30s} 合計 {tot:6.1f}/{n}  平均 {tot/n:.3f}  確定 {cert}")
print()
gain=[r for r in rows if r['both']>r['e1']+1e-9]
print(f"新案がこころのめ単独より良くなるセット = {len(gain)}")
for r in sorted(gain,key=lambda r:-(r['both']-r['e1']))[:12]:
    print(f"   {r['name']:16s} k={r['k']} kR={r['kR2']} E1 {r['e1']:.2f} → 新案 {r['both']:.2f}（{'物理' if r['phys'] else '特殊'}）")
print()
print("※参考：リフレクターを ×1/2 で計算した旧 pivot_articuno.py との kR 差")
diff=[r for r in rows if r['kR1']!=r['kR2']]
print(f"   kR が変わるセット {len(diff)} / {n}")
