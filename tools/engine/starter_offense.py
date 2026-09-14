## 歴代スタメンの火力指数と確定n発（546セット全数・走者定義=最低ロール）
## 使い方: cd battle-tower/tools/engine && PYTHONHASHSEED=0 python3 starter_offense.py
import sys, os, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evlib
from evlib import *          # make, pool, EHP, MOVES, damage_range, abil, ko_fixed_list, JPS, JPM, N

IV31 = dict(evlib._G["IV31"])
def iv(**kw):
    d = dict(IV31); d.update(kw); return d

# ---- 歴代スタメンの採用構成（出典: 05章・09章・15章・25章）-------------------
# 攻撃技のみ。自爆技は別枠（ATK_BOOM）で数える。
ROSTER = [
 ("ゲンガー v1",   "05章", make("Gengar","Timid",{"hp":224,"spa":32,"spe":252},"Lum Berry",[]),
    ["MOVE_GIGA_DRAIN"], []),
 ("ゲンガー C改",  "09章", make("Gengar","Timid",{"hp":224,"spa":32,"spe":252},"Bright Powder",[]),
    ["MOVE_THUNDERBOLT","MOVE_PSYCHIC"], []),
 ("メタグロス v1/C改@ハチマキ","05/09章", make("Metagross","Adamant",{"hp":196,"atk":252,"spd":4,"spe":56},"Choice Band",[]),
    ["MOVE_METEOR_MASH","MOVE_EARTHQUAKE","MOVE_SHADOW_BALL"], ["MOVE_EXPLOSION"]),
 ("メタグロス v4.2@フィラ",  "15章", make("Metagross","Adamant",{"hp":252,"atk":248,"spd":6,"spe":4},"Leftovers",[]),
    ["MOVE_METEOR_MASH","MOVE_EARTHQUAKE"], ["MOVE_EXPLOSION"]),
 ("メタグロス v5@ハチマキ",  "25章", make("Metagross","Adamant",{"hp":252,"atk":252,"spe":4},"Choice Band",[]),
    ["MOVE_METEOR_MASH","MOVE_EARTHQUAKE","MOVE_SHADOW_BALL"], ["MOVE_EXPLOSION"]),
 ("カビゴン v1@ツメ",   "05章", make("Snorlax","Adamant",{"hp":4,"atk":252,"df":252},"Quick Claw",[],ability="ABILITY_THICK_FAT"),
    ["MOVE_RETURN","MOVE_SHADOW_BALL"], ["MOVE_SELF_DESTRUCT"]),
 ("カビゴン C改@たべのこし","09章", make("Snorlax","Adamant",{"hp":188,"atk":252,"df":68},"Leftovers",[],ability="ABILITY_THICK_FAT"),
    ["MOVE_RETURN","MOVE_SHADOW_BALL"], []),
 ("カビゴン v5@カゴ",   "25章", make("Snorlax","Adamant",{"hp":76,"atk":182,"df":252},"Leftovers",[],ability="ABILITY_THICK_FAT"),
    ["MOVE_BODY_SLAM","MOVE_EARTHQUAKE"], []),
 ("ラティオス v1",  "05章", make("Latios","Timid",{"hp":4,"spa":252,"spe":252},"Bright Powder",[],ivs=iv(atk=7)),
    ["MOVE_PSYCHIC","MOVE_ICE_BEAM","MOVE_THUNDERBOLT"], []),
 ("ラティオス v4/v5","15/25章", make("Latios","Timid",{"hp":40,"spa":252,"spe":216},"Bright Powder",[],ivs=iv(atk=7)),
    ["MOVE_PSYCHIC","MOVE_ICE_BEAM","MOVE_THUNDERBOLT"], []),
 ("スイクン C改",  "09章", make("Suicune","Bold",{"hp":252,"df":252,"spd":4},"Chesto Berry",[]),
    ["MOVE_SURF","MOVE_ICE_BEAM"], []),
 ("サンダー v4",   "15章", make("Zapdos","Modest",{"df":84,"spa":174,"spe":252},"Lum Berry",[],ivs=iv(atk=10,df=30)),
    ["MOVE_THUNDERBOLT","MOVE_HP_ICE"], []),
 ("ラグラージ v4", "15章", make("Swampert","Adamant",{"hp":248,"atk":252,"spe":8},"Leftovers",[],ivs=iv(df=30,spd=30,spe=30)),
    ["MOVE_EARTHQUAKE","MOVE_ICE_BEAM","MOVE_HP_ROCK"], []),
 ("フリーザー v5", "25章", make("Articuno","Calm",{"hp":236,"df":208,"spd":60,"spe":4},"Leftovers",[],ivs=iv(atk=0,spa=29)),
    [], []),
]

def best_lo(m, mks):
    """各敵セットについて「最低ロールが最大になる技」の lo を返す（命中率は見ない）"""
    out=[]
    for i,e in enumerate(pool):
        b=0
        for mk in mks:
            w=None
            for ab in abil(e):   # 相手特性は最悪ケース
                dfd=dict(species=e["species"],stats=e["stats31"],types=e["types"],ability=ab,item=e["item"],level=100)
                lo,hi=damage_range(m,dfd,mk)
                if w is None or lo<w: w=lo
            if w>b: b=w
        out.append(b)
    return out

print("=== 歴代スタメンの火力指数（546セット・最低ロール基準）===")
print("火力指数 = 最低ロール ÷ 敵HP の中央値(%)。確定n発 = 最低ロールでもn発で落ちる敵の数。")
print(f"{'メンバー':30s} {'出典':9s} {'火力指数':>7s} {'確1':>5s} {'確2':>5s} {'確3':>5s} {'確2不能':>7s} {'爆発確1':>7s}")
RESULT={}
for label, src, m, mks, boom in ROSTER:
    if not mks:
        print(f"{label:30s} {src:9s} {'—':>7s} {'—':>5s} {'—':>5s} {'—':>5s} {'546':>7s} {'—':>7s}")
        RESULT[label]=None; continue
    lo = best_lo(m, mks)
    ratio = sorted(lo[i]/EHP[i] for i in range(N))
    idx = statistics.median(ratio)*100
    k1=[i for i in range(N) if lo[i]>=EHP[i]]
    k2=[i for i in range(N) if lo[i]*2>=EHP[i]]
    k3=[i for i in range(N) if lo[i]*3>=EHP[i]]
    bm = len(best_lo_boom:=([i for i in range(N) if (bl:=best_lo(m,boom))[i]>=EHP[i]])) if boom else 0
    print(f"{label:30s} {src:9s} {idx:6.1f}% {len(k1):5d} {len(k2):5d} {len(k3):5d} {N-len(k2):7d} {(bm if boom else 0) or '—':>7}")
    RESULT[label]=(m,mks,lo,k1,k2,k3)

# 25章の公表値と突き合わせ
print("\n=== 25章§0 の公表値との突き合わせ（ko_fixed_list 経由）===")
for label, mks in [("メタグロス v5@ハチマキ",["MOVE_METEOR_MASH","MOVE_EARTHQUAKE","MOVE_SHADOW_BALL"]),
                   ("ラティオス v4/v5",["MOVE_PSYCHIC","MOVE_ICE_BEAM","MOVE_THUNDERBOLT"]),
                   ("カビゴン v5@カゴ",["MOVE_BODY_SLAM","MOVE_EARTHQUAKE"])]:
    m=RESULT[label][0]
    a1=len(ko_fixed_list(m,mks,1)); a2=len(ko_fixed_list(m,mks,2))
    b1=len(RESULT[label][3]);       b2=len(RESULT[label][4])
    print(f"  {label:26s} ko_fixed_list 確1={a1} 確2={a2} / 最大lo基準 確1={b1} 確2={b2}"
          + ("  ← 一致" if (a1,a2)==(b1,b2) else "  ← 差あり（命中率の扱い）"))

# 確定2発が取れない敵（種族単位）
print("\n=== 確定2発が取れない敵（種族単位・上位のみ）===")
for label,_,m,mks,_ in ROSTER:
    if not mks: continue
    r=RESULT[label]
    miss=[i for i in range(N) if i not in set(r[4])]
    sp={}
    for i in miss: sp[JPS.get(pool[i]["species"],pool[i]["species"])]=sp.get(JPS.get(pool[i]["species"],pool[i]["species"]),0)+1
    top=sorted(sp.items(), key=lambda x:(-x[1],x[0]))[:8]
    print(f"  {label:30s} {len(miss):3d}セット / {len(sp)}種族: " + "・".join(f"{k}{v}" for k,v in top))
