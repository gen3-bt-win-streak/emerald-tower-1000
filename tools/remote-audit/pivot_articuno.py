#!/usr/bin/env python3
"""フリーザー＝ラティオスの後出し枠、という定義での4枠目比較（2026-09-11 走者の役割定義）。

対象P = ラティオスに効果抜群（2倍以上）の攻撃技を持つセットのうち、その技をフリーザーが等倍以下で受けるもの。
手順（走者定義の最悪ケース）: フリーザーはその技を最大乱数で受けて着地 → 以後、敵は毎ターンフリーザーへの最大打点技を
最大乱数・必中で撃つ（先手なら「行動→被弾」、後手なら「被弾→行動」、たべのこし1/16回復）。得られる行動回数 k から
  E1  こころのめ→零度        : k>=2 で 1.00、k==1 で 0.29
  零度単体（リフ/毒/鈴の相方） : 1-0.71^k
  リフレクター→零度           : リフ後の k' で 1-0.71^(k'-1)（リフ無しと良い方）
  どくどく（まもる交互）       : 鋼/毒/ねむる等で不可でなければ k>=4 で 1.00（近似）
零度無効（がんじょう／ヌケニン）は零度系 0。
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from evlib import *
import evlib
tm = evlib._G['type_mult']

LATIOS = make("Latios", "Timid", {"hp": 40, "spa": 252, "spe": 216}, "Lum Berry", ["MOVE_PSYCHIC"])
IV = dict(evlib._G["IV31"]); IV["atk"] = 0; IV["spa"] = 29
ART = make("Articuno", "Calm", {"hp": 236, "df": 208, "spd": 60, "spe": 4}, "Leftovers",
           ["MOVE_SHEER_COLD"], ability="ABILITY_PRESSURE", ivs=IV)
HP = ART["stats"]["hp"]; SPE = ART["stats"]["spe"]
print("Latios", LATIOS["stats"], "Articuno", ART["stats"])

def maxdmg(e, defender, reflect=False):
    """敵の各技のフリーザー/ラティオスへの最大ダメ (hi, move, physical)"""
    best = (0, None, False)
    for mk in e["moves"]:
        mv = MOVES[mk]
        if mv["power"] < 2 or mv["effect"] == "EFFECT_OHKO": continue
        for ab in abil(e):
            att = dict(stats=e["stats31"], types=e["types"], ability=ab, item=e["item"], species=e["species"], level=100)
            lo, hi = damage_range(att, defender, mk)
            a, b = evlib._hitmult(mk); hi *= b
            phys = mv["type"] in PHYSICAL
            if reflect and phys: hi //= 2
            if hi > best[0]: best = (hi, mk, phys)
    return best

def se_on_latios(e):
    out = []
    for mk in e["moves"]:
        mv = MOVES[mk]
        if mv["power"] < 2 or mv["effect"] == "EFFECT_OHKO": continue
        if tm(mv["type"], LATIOS["types"], None) >= 20:
            out.append(mk)
    return out

def k_actions(e, first_hit, reflect=False, cap=30):
    hp = HP - first_hit
    if hp <= 0: return 0
    dmg, mk, phys = maxdmg(e, ART, reflect)
    k = 0
    for _ in range(cap):
        faster = SPE > e["stats31"]["spe"]
        if faster:
            k += 1
            hp -= dmg
            if hp <= 0: return k
        else:
            hp -= dmg
            if hp <= 0: return k
            k += 1
        hp = min(HP, hp + HP // 16)
    return cap

def immune_ohko(e):
    return "ABILITY_STURDY" in abil(e) or e["species"] == "Shedinja"

def toxic_ok(e):
    if "TYPE_STEEL" in e["types"] or "TYPE_POISON" in e["types"]: return False
    if any(m in e["moves"] for m in ("MOVE_REST", "MOVE_HEAL_BELL", "MOVE_AROMATHERAPY", "MOVE_REFRESH")): return False
    return True

rows = []
for i, e in enumerate(pool):
    se = se_on_latios(e)
    if not se: continue
    # ラティオス狙いの技をフリーザーが受ける：等倍以下のものだけ後出し対象
    worst = 0; wmk = None
    for mk in se:
        mv = MOVES[mk]
        if tm(mv["type"], ART["types"], None) > 10: continue
        for ab in abil(e):
            att = dict(stats=e["stats31"], types=e["types"], ability=ab, item=e["item"], species=e["species"], level=100)
            lo, hi = damage_range(att, ART, mk); a, b = evlib._hitmult(mk); hi *= b
            if hi > worst: worst, wmk = hi, mk
    if wmk is None: continue   # ラティオス弱点技が全てフリーザーにも抜群（例: 該当なしのはず）
    k0 = k_actions(e, worst)
    kR = k_actions(e, worst, reflect=True)
    dmgA, mkA, physA = maxdmg(e, ART)
    imm = immune_ohko(e)
    e1 = 0 if imm else (1.0 if k0 >= 2 else (0.29 if k0 == 1 else 0))
    sc = 0 if imm else 1 - 0.71 ** k0
    rf = 0 if imm else max(sc, (1 - 0.71 ** (kR - 1)) if kR >= 2 else 0)
    tx = 1.0 if (toxic_ok(e) and k0 >= 4) else 0.0
    status = any(m in e["moves"] for m in ("MOVE_THUNDER_WAVE", "MOVE_GLARE", "MOVE_STUN_SPORE", "MOVE_SLEEP_POWDER",
                                          "MOVE_HYPNOSIS", "MOVE_SPORE", "MOVE_SING", "MOVE_GRASS_WHISTLE", "MOVE_YAWN",
                                          "MOVE_LOVELY_KISS", "MOVE_TOXIC", "MOVE_WILL_O_WISP"))
    rows.append(dict(i=i, name=name(i), se=JPM.get(wmk, wmk), hit=worst, k=k0, kR=kR, best=JPM.get(mkA, mkA), bd=dmgA,
                     phys=physA, imm=imm, e1=e1, sc=sc, rf=rf, tx=tx, status=status,
                     spe=e["stats31"]["spe"], moves=[JPM.get(m, m) for m in e["moves"]]))

n = len(rows)
print(f"\n後出し対象P = {n} セット（ラティオス弱点技持ち、フリーザーが等倍以下で受ける）")
from collections import Counter
print("k分布:", dict(sorted(Counter(min(r['k'], 6) for r in rows).items())), "(6=6以上)")
print("フリーザーへの最大打点が物理:", sum(1 for r in rows if r['phys']), " 特殊:", sum(1 for r in rows if not r['phys']))
print("状態異常技持ち:", sum(1 for r in rows if r['status']), " 零度無効:", sum(1 for r in rows if r['imm']))
for key, label in (("e1", "こころのめ+零度"), ("sc", "零度単体（相方が支援技）"), ("rf", "リフレクター+零度"), ("tx", "どくどく+まもる（近似）")):
    tot = sum(r[key] for r in rows); cert = sum(1 for r in rows if r[key] >= 0.99)
    print(f"  {label:22s} 成功率合計 {tot:6.1f}/{n}  平均 {tot/n:.3f}  確定 {cert}")
print("\nk<=1（フリーザーが後出ししても何もできない相手）:")
for r in sorted(rows, key=lambda r: (r['k'], -r['bd'])):
    if r['k'] <= 1:
        print(f"  {r['name']:16s} S{r['spe']:3d} 着地被弾{r['se']}{r['hit']:4d} 以後{r['best']}{r['bd']:4d} k={r['k']} {'零度無効' if r['imm'] else ''}")
print("\nk=2〜3（こころのめの有無で差が出る帯）:")
for r in sorted(rows, key=lambda r: (r['k'], -r['bd'])):
    if 2 <= r['k'] <= 3:
        print(f"  {r['name']:16s} S{r['spe']:3d} 着地{r['hit']:4d} 以後{r['best']}{r['bd']:4d}{'物' if r['phys'] else '特'} k={r['k']} kR={r['kR']} E1 {r['e1']:.2f} 零度 {r['sc']:.2f} リフ {r['rf']:.2f} 毒 {r['tx']:.0f} {'状態異常' if r['status'] else ''}")
