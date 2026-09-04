"""期待値ベースのEV監査ヘルパー。
使い方:
  import sys; sys.path.insert(0,'<repo>/battle-tower/tools/remote-audit')
  from evlib import *
  m = make("Metagross","Adamant",dict(hp=252,atk=244,spd=8,spe=4),"Metal Coat",[],ability="ABILITY_CLEAR_BODY")
  print(defense(m))   # (期待被KO, 2発圏, 落ちうるセット数)
  print(offense(m,["MOVE_METEOR_MASH","MOVE_EARTHQUAKE"]))  # (期待KO, 確定KO数)
"""
import sys, os
_HERE=os.getcwd()
os.chdir('/home/user/daily-tasks/battle-tower/tools/remote-audit'); sys.path.insert(0,'.')
_G={'__file__':'calc_matchups.py'}
exec(open('calc_matchups.py').read().split("# ---------- Analysis 1")[0], _G)
make=_G['make']; damage_range=_G['damage_range']; pool=_G['pool']; MOVES=_G['MOVES']; PHYSICAL=_G['PHYSICAL']
try:
    from jpnames import JPS, JPM
except Exception:
    JPS, JPM = {}, {}
os.chdir(_HERE)
# 追加技（プロジェクト独自のめざパ）
MOVES.setdefault("MOVE_HP_ICE",  dict(effect="EFFECT_HIT",power=70,type="TYPE_ICE", accuracy=100,target="MOVE_TARGET_SELECTED",priority=0))
MOVES.setdefault("MOVE_HP_ROCK", dict(effect="EFFECT_HIT",power=70,type="TYPE_ROCK",accuracy=100,target="MOVE_TARGET_SELECTED",priority=0))
MOVES.setdefault("MOVE_HP_DARK", dict(effect="EFFECT_HIT",power=70,type="TYPE_DARK",accuracy=100,target="MOVE_TARGET_SELECTED",priority=0))
N=len(pool)
EHP=[e["stats31"]["hp"] for e in pool]
ESPE=[e["stats31"]["spe"] for e in pool]

def sid(i): return pool[i]["set_id"]
def name(i):
    e=pool[i]; return f"#{e['set_id']}{JPS.get(e['species'],e['species'])}"
def find(setid):
    for i in range(N):
        if pool[i]["set_id"]==setid: return i
    return None
def abil(e): return [a for a in set(e["abilities"]) if a!="ABILITY_NONE"]

def rolls(hi):
    """第3世代の16通りのダメージ乱数（hi=100%ロール）"""
    return [hi*(85+i)//100 for i in range(16)]
def pks(hi, thr):
    """そのロールでthr以上になる確率（16分の何本か）"""
    return sum(1 for x in rolls(hi) if x>=thr)/16
def nrolls(hi, thr):
    return sum(1 for x in rolls(hi) if x>=thr)

def _hitmult(mk):
    ef=MOVES[mk]["effect"]
    if ef=="EFFECT_DOUBLE_HIT": return (2,2)
    if ef=="EFFECT_MULTI_HIT":  return (2,3)
    return (1,1)

def incoming(m, curse=0, crit=False):
    """各敵セットについて (被KO確率, 最大ダメ, 技) を返す。curse=のろい段数(防御1.5^n相当)"""
    mm=dict(m); mm["stats"]=dict(m["stats"])
    mm["stats"]["df"]=int(m["stats"]["df"]*[1,1.5,2.0,2.5,3.0][curse])
    hp=m["stats"]["hp"]; out=[]
    for e in pool:
        bp=0.0; bhi=0; bmk=""
        for mk in e["moves"]:
            mv=MOVES[mk]
            if mv["power"]<2 or mv["effect"]=="EFFECT_OHKO": continue
            for ab in abil(e):
                att=dict(stats=e["stats31"],types=e["types"],ability=ab,item=e["item"],species=e["species"],level=100)
                lo,hi=damage_range(att,mm,mk,crit=crit)
                a,b=_hitmult(mk); hi*=b
                acc=(mv["accuracy"] or 100)/100
                p=pks(hi,hp)*acc
                if p>bp or (p==bp and hi>bhi): bp,bhi,bmk=p,hi,mk
        out.append((bp,bhi,bmk))
    return out

def defense(m, curse=0):
    """(期待被KO数, 2発圏の期待数, 1発で落ちうるセット数) — 546セット合計"""
    hp=m["stats"]["hp"]; inc=incoming(m,curse)
    p1=sum(x[0] for x in inc)
    p2=0.0; g=0
    half=(hp+1)//2
    for i,(p,hi,mk) in enumerate(inc):
        if hi>=hp: g+=1
    mm=dict(m); mm["stats"]=dict(m["stats"]); mm["stats"]["df"]=int(m["stats"]["df"]*[1,1.5,2.0,2.5,3.0][curse])
    for e in pool:
        b2=0.0
        for mk in e["moves"]:
            mv=MOVES[mk]
            if mv["power"]<2 or mv["effect"]=="EFFECT_OHKO": continue
            for ab in abil(e):
                att=dict(stats=e["stats31"],types=e["types"],ability=ab,item=e["item"],species=e["species"],level=100)
                lo,hi=damage_range(att,mm,mk); a,b=_hitmult(mk); hi*=b
                x=pks(hi,half)*((mv["accuracy"] or 100)/100)
                if x>b2: b2=x
        p2+=b2
    return round(p1,2), round(p2,2), g

def outgoing(m, mks, atk_mul=1.0, spa_mul=1.0):
    """各敵について (KO確率, (lo,hi), 技)"""
    d=dict(m); d["stats"]=dict(m["stats"])
    d["stats"]["atk"]=int(m["stats"]["atk"]*atk_mul)
    d["stats"]["spa"]=int(m["stats"]["spa"]*spa_mul)
    res=[]
    for i,e in enumerate(pool):
        bp=0.0; bw=(0,0); bmk=""
        for mk in mks:
            w=None
            for ab in abil(e):
                dfd=dict(species=e["species"],stats=e["stats31"],types=e["types"],ability=ab,item=e["item"],level=100)
                lo,hi=damage_range(d,dfd,mk)
                if w is None or (lo,hi)<w: w=(lo,hi)
            p=pks(w[1],EHP[i])*((MOVES[mk]["accuracy"] or 100)/100)
            if p>bp or (p==bp and w[1]>bw[1]): bp,bw,bmk=p,w,mk
        res.append((bp,bw,bmk))
    return res

def offense(m, mks, atk_mul=1.0, spa_mul=1.0):
    """(期待KO数, 確定KO数) — 546セット合計。確定KO = 最低乱数でも落とせる"""
    o=outgoing(m,mks,atk_mul,spa_mul)
    return round(sum(x[0] for x in o),2), sum(1 for i,x in enumerate(o) if x[1][0]>=EHP[i])

def compare(label_a, m_a, label_b, m_b, mks, curse=0, atk_mul=1.0):
    """2つの型を並べて表示し、乱数が動いたセットを列挙する"""
    da=defense(m_a,curse); db=defense(m_b,curse)
    oa=offense(m_a,mks,atk_mul); ob=offense(m_b,mks,atk_mul)
    print(f"{label_a:28s} {m_a['stats']} 守{da} 攻{oa}")
    print(f"{label_b:28s} {m_b['stats']} 守{db} 攻{ob}")
    ia=incoming(m_a,curse); ib=incoming(m_b,curse)
    diff=[(name(i), round(ia[i][0]*16), round(ib[i][0]*16), JPM.get(ia[i][2],ia[i][2])) for i in range(N) if abs(ia[i][0]-ib[i][0])>1e-9]
    print(f"  被弾で乱数が動いたセット {len(diff)}件（A本/16 → B本/16）:")
    for d in diff[:40]: print("   ",d)
    ga=outgoing(m_a,mks,atk_mul); gb=outgoing(m_b,mks,atk_mul)
    diff2=[(name(i), round(ga[i][0]*16), round(gb[i][0]*16)) for i in range(N) if abs(ga[i][0]-gb[i][0])>1e-9]
    print(f"  攻撃で乱数が動いたセット {len(diff2)}件:")
    for d in diff2[:40]: print("   ",d)
