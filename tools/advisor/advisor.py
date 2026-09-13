## v4リアルタイム・アドバイザー v1
## 実機の盤面を毎ターン入力 → 凍結v4ボット(条項レイヤ+2手読み探索)の推奨手を日本語で出力する。
## 使い方: PYTHONHASHSEED=0 FIDELITY2=1 python3 advisor.py
## 入力は対話式。種族は日本語/英語どちらでも可。HPは%指定。
import sys, os
_HERE=os.path.dirname(os.path.abspath(__file__))
_ENGINE=os.path.normpath(os.path.join(_HERE,"..","engine")); _SIM=os.path.normpath(os.path.join(_HERE,"..","sim"))
sys.path.insert(0,_ENGINE)  # jpnames は tools/engine
os.environ["BOOM_FIX"]="1"  # A/B完走で改善確定(100万ペア net-59 / McNemar p≈2.1e-4, 床0.2516%→0.2457%)→採用。凍結マラソン本体は不変
os.environ["FIRE_FIX"]="1"  # A/B完走で改善確定(100万ペア net-283 改善318/改悪35, McNemar p≈6.4e-51, 床0.2516%→0.2233%)→採用。単炎条項の地震温存/飛行炎10万。凍結マラソン本体は不変
os.environ["HP_ROCK"]="1"   # 2026-07-30 実機チーム変更(D案: ラグなだれ→めざ岩70/EV B4→S4/個体E6BA7F73)に追随。同一シード100万A/B測定中(hrm)。凍結マラソン本体は不変
os.environ["GROSS_A228"]="1"  # 2026-08-09 実機チーム変更(グロスEV再配分 H252/A228/B0/D24/S4=399/296/222)に追随。15章「EV再配分の最適解」。凍結マラソン本体は不変
from jpnames import JPS, JPM, JPI
JPM.setdefault("HP_ICE","めざ氷"); JPM.setdefault("HP_ROCK","めざ岩")
JP2EN={v:k for k,v in JPS.items()}
# sim_v4marathon.py → sim_z11 → sim_z4 → sim.py の exec 連鎖は cwd=tools/sim 前提の相対 open なので、読み込みの間だけ移動する
_cwd=os.getcwd(); os.chdir(_SIM)
src=open('sim_v4marathon.py').read()
ns={'__name__':'advisor','__file__':os.path.abspath('sim_v4marathon.py')}
exec(src[:src.index('if __name__')], ns)
os.chdir(_cwd)
G=ns['G']; v3_choose=ns['v3_choose']; _battle_no=ns['_battle_no']
G['VERBOSE']=False  # play_battle経由でないと未定義(Battle.lgが参照)
MOVES=ns['MOVES']; Mon=G['Mon']; Battle=G['Battle']; pool=G['pool']
# アドバイザーは1手だけ評価するので探索ロールアウトを増やす(1決定あたり0.数秒増のみ)。
# 効能: 2手読みのモンテカルロ・ノイズが減り、敵入力順(A/B)に依存しない“真の最適手”を返す。
# ※凍結マラソン本体は sim_*marathon.py 側の S=5/R=5(速度優先)のまま不変。ここはアドバイザー専用の上書き。
ns['S']=16; ns['R']=12
bySp={}
for e in pool: bySp.setdefault(e['species'],[]).append(e)

def jpmv(mv): return JPM.get(mv.replace("MOVE_",""), mv.replace("MOVE_","").title())
def sp_norm(v):
    v=v.strip()
    if not v: return None
    if v in bySp: return v
    if v in JP2EN and JP2EN[v] in bySp: return JP2EN[v]
    lv=v.lower()
    for sp in bySp:
        if sp.lower()==lv: return sp
    return None

def ask(prompt, default=None):
    s=input(prompt).strip()
    return s if s else default

def make_foe(sp, hp_pct, status, observed_idx):
    """種族+観測技からinfo-fairに代表セットを構築(実速最大セット=保守的)。"""
    cands=bySp[sp]
    obs=set()
    if observed_idx:
        # 観測技は「その種族の全候補技リスト」の番号で指定
        allmv=sorted({m for e in cands for m in e['moves']})
        for i in observed_idx:
            if 1<=i<=len(allmv): obs.add(allmv[i-1])
        cands=[e for e in cands if obs.issubset(set(e['moves']))] or bySp[sp]
    e=max(cands,key=lambda x:x['stats31']['spe'])
    ab=[a for a in e['abilities'] if a!="ABILITY_NONE"][0]
    m=Mon(sp,list(e['types']),ab,e['item'],dict(e['stats31']),list(e['moves']),"foe",set_id=e['set_id'])
    m.hp=max(1,m.max_hp*hp_pct//100) if hp_pct>0 else 0
    m.status=status; m.observed=obs
    return m

def show_moves(sp):
    allmv=sorted({m for e in bySp[sp] for m in e['moves']})
    print("  %sの候補技: %s"%(JPS.get(sp,sp)," ".join("%d:%s"%(i+1,jpmv(m)) for i,m in enumerate(allmv))))

STATUS={"":None,"なし":None,"まひ":"PAR","やけど":"BRN","ねむり":"SLP","こおり":"FRZ","どく":"PSN"}

def read_foe(label, allow_empty=False):
    while True:
        v=ask("%s 種族(空=なし): "%label,"")
        if not v and allow_empty: return None
        sp=sp_norm(v or "")
        if sp: break
        print("  ! 不明な種族。日本語名か英語名で。")
    show_moves(sp)
    hp=int(ask("  HP%% [100]: ","100"))
    st=STATUS.get(ask("  状態(まひ/やけど/ねむり/こおり/どく/なし) [なし]: ",""),None)
    oi=ask("  観測済み技の番号(スペース区切り・無ければ空): ","")
    idx=[int(x) for x in oi.split()] if oi else []
    return make_foe(sp,hp,st,idx)

def read_our(team):
    print("こちら: 1:サンダー 2:メタグロス 3:ラティオス 4:ラグラージ")
    act=ask("場の2体の番号 [1 2]: ","1 2").split()
    a,bn=int(act[0])-1,int(act[1])-1
    order=[a,bn]+[i for i in range(4) if i not in (a,bn)]
    mons=[team[i] for i in order]
    for i,m in enumerate(mons):
        alive=ask("%s HP%%(0=瀕死) [100]: "%JPS.get(m.species,m.species),"100")
        m.hp=m.max_hp*int(alive)//100
        if m.hp>0:
            st=STATUS.get(ask("  状態 [なし]: ",""),None); m.status=st
    return mons

def build_battle(turn, ours, foes, foe_bench_n):
    b=Battle(seed=1)
    b.turn=turn-1  # play側でturn+=1される想定はないが、choose系はb.turnを見る
    b.turn=turn
    b.us=ours; b.active["us"]=[m for m in ours[:2]]; b.bench["us"]=[m for m in ours[2:] if m.hp>0]
    b.active["foe"]=list((list(foes)+[None,None])[:2])  # activeスロットのNoneは実シム同様に許容
    b.bench["foe"]=[f for f in foes[2:] if f is not None and f.hp>0]
    # 未判明の控えは全プールからの代表2体で近似(爆発読み等の終盤判断に影響。判明したら入力し直すこと)
    import random as _r
    rng=_r.Random(42)
    while len(b.bench["foe"])<foe_bench_n:
        e=rng.choice(pool)
        if e['species'] in [f.species for f in b.active["foe"] if f is not None]: continue
        ab=[a for a in e['abilities'] if a!="ABILITY_NONE"][0]
        b.bench["foe"].append(Mon(e['species'],list(e['types']),ab,e['item'],dict(e['stats31']),list(e['moves']),"foe",set_id=e['set_id']))
    # b.foe(敵の全リスト)は実シム同様「実体のみ」(sample_world等が全走査するのでNone禁止)
    b.foe=[f for f in b.active["foe"] if f is not None]+list(b.bench["foe"])
    b.flags.clear()
    b.weather=None; b.wturns=0
    for k in list(getattr(b,"screens",{}) or {}): b.screens[k]=0
    b.enemy_iv=31  # オープン高連勝帯=IV31想定(保守的)
    for m in b.active["us"]+b.active["foe"]:
        if m: m.protected=False; m.flinch=False
    return b

def fmt_act(m,a):
    nm=JPS.get(m.species,m.species)
    if a is None: return "%s: (指示なし=自由枠)"%nm
    if a[0]=="switch": return "%s: 交代 → %s"%(nm,JPS.get(a[2].species,a[2].species))
    tgt=a[2]
    t=("→ "+JPS.get(tgt.species,tgt.species)) if hasattr(tgt,"species") and tgt is not m else ""
    return "%s: %s %s"%(nm,jpmv(a[1]),t)

def main():
    print("="*46)
    print(" v4 リアルタイム・アドバイザー (条項+2手読み)")
    print(" 毎ターン盤面を入力 → 推奨手を出力。Ctrl+Cで終了")
    print("="*46)
    team=G['our_team']()
    while True:
        print("\n----- 新しいターン -----")
        turn=int(ask("ターン数 [1]: ","1"))
        ours=read_our(G['our_team']())  # 毎ターン新規構築(HP%で再同期・ドリフトなし)
        fA=read_foe("敵A"); fB=read_foe("敵B",allow_empty=True)
        foes=[f for f in (fA,fB) if f]
        nb=int(ask("敵の控え残り数 [2]: ","2"))
        b=build_battle(turn,ours,(foes+[None,None])[:2],nb)
        _battle_no[0]=1
        acts=v3_choose(b)
        print("\n★ 推奨手:")
        for m in b.active["us"]:
            if m and m.hp>0: print("  "+fmt_act(m,acts.get(m)))
        print("(前提: 敵は各種族の最速セットで仮置き・ダメージ判定は全546セットの最悪ケース)")

if __name__=="__main__":
    try: main()
    except (KeyboardInterrupt,EOFError): print("\n終了")
