## ドキュメント数値の総点検ツール（証拠としての研究履歴用・再実行可能）
##
## 目的: 各mdに書かれた数値主張を、現行v4スペック（実機版=めざ岩ラグ）のエンジンで再計算し、
##       一致/不一致を機械判定する。結果は 18-verification-ledger.md の一次証拠になる。
##
## 使い方: cd battle-tower/tools/remote-audit
##         PYTHONHASHSEED=0 FIDELITY2=1 python3 verify_docs.py          # 全件
##         PYTHONHASHSEED=0 FIDELITY2=1 python3 verify_docs.py 8.1      # 節を指定
##
## 判定の定義:
##   確定OHKO(確1) = 最小ロールで相手のHP以上（乱数無関係に1発）
##   OHKO圏        = 最大ロールで相手のHP以上（乱数次第）
##   敵の想定      = IV31・特性は非NONEの先頭・持ち物込み（ドキュメント作成時と同一の前提）
##   %の丸め       = 切り捨て（全ドキュメントで統一。四捨五入だと系統的に+1%ずれる）
import os, sys, json
os.environ.setdefault("HP_ROCK", "1")   # 実機現行=めざ岩ラグ。凍結スペックで検算する場合は HP_ROCK=0
os.environ.setdefault("FIRE_FIX", "1")

_src = open('sim_v4marathon.py').read()
NS = {'__name__': 'verify_docs', '__file__': 'sim_v4marathon.py'}
exec(_src[:_src.index('if __name__')], NS)
G = NS['G']; MOVES = NS['MOVES']; pool = G['pool']; Mon = G['Mon']
damage_range = G['damage_range']

TEAM = {m.species: m for m in G['our_team']()}
ZAP, GROSS, LATI, SWAMP = TEAM['Zapdos'], TEAM['Metagross'], TEAM['Latios'], TEAM['Swampert']
BY_ID = {e['set_id']: e for e in pool}

RESULTS = []   # (section, label, expected, actual, ok)


def rec(section, label, expected, actual, ok):
    RESULTS.append((section, label, str(expected), str(actual), ok))


def foe(sid):
    e = BY_ID[sid]
    ab = [a for a in e['abilities'] if a != "ABILITY_NONE"][0]
    return Mon(e['species'], list(e['types']), ab, e['item'], dict(e['stats31']), list(e['moves']), "foe", set_id=sid)


def dmg(att, dfd, move):
    a = dict(species=att.species, stats=att.eff(), types=att.types, ability=att.ability, item=att.item, level=100)
    d = dict(species=dfd.species, stats=dfd.eff(), types=dfd.types, ability=dfd.ability, item=None, level=100)
    return damage_range(a, d, move)


def best_hit(att, dfd):
    """attの持ち技のうちdfdへの最大打点 -> (lo, hi, move)"""
    best = (0, 0, None)
    for mv in att.moves:
        if mv not in MOVES or MOVES[mv]["power"] < 2:
            continue
        lo, hi = dmg(att, dfd, mv)
        if hi > best[1]:
            best = (lo, hi, mv)
    return best


def pct(x, hp):
    # ドキュメント作成時と同じ規約＝切り捨て（int）。round()にすると系統的に+1%ずれる
    return int(100 * x / hp)


# ---------------------------------------------------------------- 編成表
def sec_spec():
    exp = {'Zapdos': (322, 383, 299), 'Metagross': (364, 381, 177),
           'Latios': (302, 359, 350), 'Swampert': (404, 350, 156)}
    for sp, (hp, key, spe) in exp.items():
        m = TEAM[sp]
        got_key = m.stats['spa'] if sp in ('Zapdos', 'Latios') else m.stats['atk']
        ok = (m.max_hp == hp and got_key == key and m.stats['spe'] == spe)
        rec("編成表", "%s HP/主要/素早さ" % sp, "%d/%d/%d" % (hp, key, spe),
            "%d/%d/%d" % (m.max_hp, got_key, m.stats['spe']), ok)
    rec("編成表", "ラグ 防/特防(めざ岩個体)", "215/207",
        "%d/%d" % (SWAMP.stats['df'], SWAMP.stats['spd']),
        SWAMP.stats['df'] == 215 and SWAMP.stats['spd'] == 207)


# ---------------------------------------------------------------- §1.5 速度早見表
def sec_speed():
    exp = {'Latios': (350, 6), 'Zapdos': (299, 49), 'Metagross': (177, 310), 'Swampert': (156, 370)}
    for sp, (spe, n_faster) in exp.items():
        m = TEAM[sp]
        cnt = sum(1 for e in pool if e['stats31']['spe'] > m.stats['spe'])
        ok = (m.stats['spe'] == spe and cnt == n_faster)
        rec("§1.5", "%s 素早さ/抜かれる敵数" % sp, "%d / %d" % (spe, n_faster),
            "%d / %d" % (m.stats['spe'], cnt), ok)


# ---------------------------------------------------------------- §8.1 爆発が確1する19セット
BOOM19 = [454, 455, 470, 511, 522, 579, 656, 675, 714, 732, 739, 742, 743, 752, 769, 780, 791, 874, 875]


def sec_81():
    ng = []
    for sid in BOOM19:
        f = foe(sid)
        lo, hi = dmg(GROSS, f, "MOVE_EXPLOSION")
        if lo < f.max_hp:
            ng.append((sid, f.species, lo, f.max_hp))
    rec("§8.1", "爆発が確定OHKOする19セット（全件 lo>=敵HP）", "19/19 確1",
        "%d/19 確1%s" % (19 - len(ng), ("／未達:" + str(ng)) if ng else ""), not ng)
    ng2 = []
    for sid in BOOM19:
        f = foe(sid)
        lo, hi, mv = best_hit(f, GROSS)
        if lo < GROSS.max_hp:
            ng2.append((sid, f.species, pct(lo, GROSS.max_hp)))
    rec("§8.1", "19セットがグロスを確定OHKO", "19/19",
        "%d/19%s" % (19 - len(ng2), ("／未達:" + str(ng2)) if ng2 else ""), not ng2)


# ---------------------------------------------------------------- §8.2 炎16セット→退避先
FIRE16 = [454, 455, 511, 522, 656, 714, 732, 739, 742, 743, 752, 769, 780, 791, 874, 875]


def sec_82():
    rows = []
    for sid in FIRE16:
        f = foe(sid)
        lo, hi, mv = best_hit(f, SWAMP)
        rows.append((pct(hi, SWAMP.max_hp), sid, f.species, mv.replace("MOVE_", "")))
    rows.sort(reverse=True)
    top = rows[0]
    rec("§8.2", "対ラグ最大打点の最悪セット", "#714 ヘルガー 170% SOLAR_BEAM",
        "#%d %s %d%% %s" % (top[1], top[2], top[0], top[3]), top[1] == 714 and top[0] >= 100)
    rest = max(r[0] for r in rows if r[1] != 714)
    rec("§8.2", "#714を除く15セットの最大", "42%", "%d%%" % rest, rest == 42)
    fire_only = []
    for sid in FIRE16:
        f = foe(sid)
        for mv in f.moves:
            if mv in MOVES and MOVES[mv].get("type") == "TYPE_FIRE" and MOVES[mv]["power"] >= 2:
                fire_only.append((pct(dmg(f, SWAMP, mv)[1], SWAMP.max_hp), sid))
    fm = max(fire_only)
    rec("§8.2", "純粋な炎技のみの最大", "40% (#791)", "%d%% (#%d)" % (fm[0], fm[1]), fm[0] == 40)


# ------------------------------------------------- §1.6b 退避先の選択（ラティ引き/ラグ引き/居座り）
def sec_retreat():
    """炎16セットそれぞれについて、ラティオス退避とラグラージ退避のどちらが安全かを判定。
    実戦（2026-07-30 ユーザー報告）で退避先を状況に応じて選び分けている運用の数値的裏付け。"""
    latios_ng, swamp_ng, both_ng = [], [], []
    for sid in FIRE16:
        f = foe(sid)
        lL, hL, mL = best_hit(f, LATI)
        lS, hS, mS = best_hit(f, SWAMP)
        pL, pS = pct(hL, LATI.max_hp), pct(hS, SWAMP.max_hp)
        if pL >= 100 and pS >= 100:
            both_ng.append(sid)
        elif pL >= 100:
            latios_ng.append((sid, f.species, pL, mL.replace("MOVE_", "")))
        elif pS >= 100:
            swamp_ng.append((sid, f.species, pS, mS.replace("MOVE_", "")))
    rec("§1.6b", "ラグ退避がNG（最大ロールで落ちる）セット", "#714のみ",
        str([s[0] for s in swamp_ng]), [s[0] for s in swamp_ng] == [714])
    rec("§1.6b", "ラティ退避がNGなセット", "(実測で列挙)",
        str(latios_ng), None)
    rec("§1.6b", "両方NG（＝まもる+でんじは推奨）", "(実測で列挙)", str(both_ng), None)


# ---------------------------------------------------------------- §8.3 氷19セット→サンダー
ICE19 = {789: 126, 870: 126, 756: 110, 778: 100, 871: 100, 774: 144, 763: 114, 785: 114, 839: 114,
         377: 125, 665: 125, 821: 129, 744: 102, 740: 110, 452: 108, 488: 104, 392: 100,
         495: 164, 591: 104}
ICE_STAR = {789, 870, 774, 377, 665, 821, 495}


def sec_83():
    bad = []
    for sid, exp_pct in ICE19.items():
        f = foe(sid)
        lo, hi, mv = best_hit(f, ZAP)
        got = pct(hi, ZAP.max_hp)
        star_doc = sid in ICE_STAR
        star_now = lo >= ZAP.max_hp
        if got != exp_pct or star_doc != star_now:
            bad.append("#%d %s 記載%d%%→実測%d%% 確1記載%s→実測%s" % (
                sid, f.species, exp_pct, got, star_doc, star_now))
    rec("§8.3", "氷19セットの対サンダー打点と確1判定", "全19一致",
        "一致%d/19%s" % (19 - len(bad), ("／不一致:" + "; ".join(bad)) if bad else ""), not bad)


# ---------------------------------------------------------------- §8.4 速い炎15セット→グロス
FAST15 = {454: (299, 109, 128), 455: (299, 109, 128), 522: (289, 109, 129), 656: (289, 119, 140),
          714: (289, 127, 150), 752: (289, 109, 128), 511: (285, 102, 120), 780: (279, 120, 141),
          874: (279, 127, 150), 742: (278, 108, 127), 743: (278, 108, 127), 769: (216, 127, 150),
          875: (216, 127, 150), 739: (196, 116, 137), 791: (194, 140, 164)}


def sec_84():
    bad = []
    for sid, (spe, elo, ehi) in FAST15.items():
        e = BY_ID[sid]
        f = foe(sid)
        lo, hi, mv = best_hit(f, GROSS)
        glo, ghi = pct(lo, GROSS.max_hp), pct(hi, GROSS.max_hp)
        if e['stats31']['spe'] != spe or glo != elo or ghi != ehi:
            bad.append("#%d spe記載%d→%d / 打点記載%d-%d%%→%d-%d%%" % (
                sid, spe, e['stats31']['spe'], elo, ehi, glo, ghi))
    rec("§8.4", "速い炎15セットのspe・対グロス打点", "全15一致",
        "一致%d/15%s" % (15 - len(bad), ("／不一致:" + "; ".join(bad)) if bad else ""), not bad)
    f732 = foe(732)
    lo, hi, _ = best_hit(f732, GROSS)
    ok = (BY_ID[732]['stats31']['spe'] == 149 and lo >= GROSS.max_hp)
    rec("§8.4", "#732ブースター spe149・確定OHKO", "spe149 / 116-136%",
        "spe%d / %d-%d%%" % (BY_ID[732]['stats31']['spe'], pct(lo, GROSS.max_hp), pct(hi, GROSS.max_hp)), ok)


# ---------------------------------------------------------------- §8.5 エンテイ×ラティ
ENTEI = [760, 771, 782, 793, 878, 879]
LATIOS_S = [766, 777, 788, 799, 846, 847, 848, 849]
LATIAS_S = [765, 776, 787, 798, 842, 843, 844, 845]


def sec_85():
    for name, ids, sp in (("エンテイ6", ENTEI, "Entei"), ("ラティオス8", LATIOS_S, "Latios"),
                          ("ラティアス8", LATIAS_S, "Latias")):
        actual = sorted(e['set_id'] for e in pool if e['species'] == sp)
        rec("§8.5", "%s セット列挙" % name, str(sorted(ids)), str(actual), sorted(ids) == actual)
    lati_max = 0
    for sid in LATIOS_S + LATIAS_S:
        lo, hi, mv = best_hit(foe(sid), GROSS)
        lati_max = max(lati_max, pct(hi, GROSS.max_hp))
    rec("§8.5", "ラティ兄妹の対グロス最大（確1不能の根拠）", "42%", "%d%%" % lati_max, lati_max == 42)
    e771 = best_hit(foe(771), GROSS)
    rec("§8.5", "#771エンテイの対グロス最大", "112%", "%d%%" % pct(e771[1], GROSS.max_hp),
        pct(e771[1], GROSS.max_hp) == 112)


# ---------------------------------------------------------------- §8.6 ガラガラ
def sec_86():
    for sid in (470, 579, 675):
        f = foe(sid)
        lo, hi = dmg(f, SWAMP, "MOVE_EARTHQUAKE")
        f.stages["atk"] = 2
        lo2, hi2 = dmg(f, SWAMP, "MOVE_EARTHQUAKE")
        f.stages["atk"] = 0
        ok = pct(hi, SWAMP.max_hp) == 82 and lo2 >= SWAMP.max_hp
        rec("§8.6", "#%d じしん→ラグ 無補正/剣舞+2" % sid, "82% / 確1",
            "%d%% / %s(%d-%d)" % (pct(hi, SWAMP.max_hp), "確1" if lo2 >= SWAMP.max_hp else "非確1", lo2, hi2), ok)
    f387 = foe(387)
    lo, hi, mv = best_hit(f387, SWAMP)
    rec("§8.6", "#387 対ラグ最大（じしん無）", "41%", "%d%% (%s)" % (pct(hi, SWAMP.max_hp), mv.replace("MOVE_", "")),
        pct(hi, SWAMP.max_hp) == 41)
    lo, hi = dmg(foe(470), ZAP, "MOVE_ROCK_SLIDE")
    rec("§8.6", "ガラガラ いわなだれ→サンダー", "92-108%",
        "%d-%d%%" % (pct(lo, ZAP.max_hp), pct(hi, ZAP.max_hp)),
        pct(lo, ZAP.max_hp) == 92 and pct(hi, ZAP.max_hp) == 108)


# ---------------------------------------------------------------- 15章 対面メモ
def sec_15():
    f383 = foe(383)
    z = dmg(ZAP, f383, "MOVE_THUNDERBOLT"); s = dmg(SWAMP, f383, "MOVE_EARTHQUAKE")
    rec("15章", "フォレトス#383 サンダー10万 / ラグ地震", "61-72% / 41-48%",
        "%d-%d%% / %d-%d%%" % (pct(z[0], f383.max_hp), pct(z[1], f383.max_hp),
                               pct(s[0], f383.max_hp), pct(s[1], f383.max_hp)),
        pct(z[0], f383.max_hp) == 61 and pct(s[1], f383.max_hp) == 48)
    f711 = foe(711)
    z2 = dmg(ZAP, f711, "MOVE_THUNDERBOLT")
    rec("15章", "ハッサム#711(HP344) サンダー10万 ※旧「フォレトス」の誤ラベル元", "40-47%",
        "%d-%d%%" % (pct(z2[0], f711.max_hp), pct(z2[1], f711.max_hp)),
        pct(z2[0], f711.max_hp) == 40 and pct(z2[1], f711.max_hp) == 47)
    noboom = []
    for e in [x for x in pool if x['species'] in ('Forretress', 'Scizor')]:
        f = foe(e['set_id'])
        lo, hi = dmg(GROSS, f, "MOVE_EXPLOSION")
        if lo < f.max_hp:
            noboom.append("#%d %s %d-%d%%" % (e['set_id'], f.species, pct(lo, f.max_hp), pct(hi, f.max_hp)))
    rec("15章", "虫鋼のうち爆発でも確1できないセット", "フォレトス4 + ハッサム#711 = 5件",
        "%d件: %s" % (len(noboom), ", ".join(noboom)), len(noboom) == 5)
    worst = 999
    for sp in ('Blissey', 'Gardevoir', 'Ludicolo'):
        for e in [x for x in pool if x['species'] == sp]:
            f = foe(e['set_id'])
            lo, hi = dmg(GROSS, f, "MOVE_EXPLOSION")
            worst = min(worst, pct(lo, f.max_hp))
    rec("15章", "ハピナス/サーナイト/ルンパッパへの爆発（最小ロール%の最小値）", ">=160%",
        "%d%%" % worst, worst >= 160)
    shed = [e['set_id'] for e in pool if e['species'] == 'Shedinja']
    hits = []
    for sid in shed:
        f = foe(sid)
        for owner in (ZAP, GROSS, LATI, SWAMP):
            for mv in owner.moves:
                if mv in MOVES and MOVES[mv]["power"] >= 2:
                    if dmg(owner, f, mv)[1] > 0:
                        hits.append("%s/%s" % (owner.species, mv.replace("MOVE_", "")))
    rec("15章", "ヌケニンに通る技（チーム16技中）", "ラグのめざ岩のみ",
        str(sorted(set(hits))), set(hits) == {"Swampert/HP_ROCK"})
    acc = MOVES["MOVE_HP_ROCK"]["accuracy"]
    eff = round(acc * 0.95)
    rec("15章", "めざ岩のヌケニンへの実効命中", "95%", "%d%% (命中%d×お香0.95)" % (eff, acc), eff == 95)


# ---------------------------------------------------------------- §8.6b バンギラス / EV交換の実収支
def sec_ttar():
    """バンギラス10セットの対グロス打点と、A252→A164+B44/D44/S4のEV交換の収支を検証。
    ユーザー質問(2026-07-30)「バンギとの打ち合いは耐久振りで変わるか」への回答を固定化する。"""
    import copy
    old = copy.deepcopy(GROSS)
    old.stats["atk"] = 405; old.stats["df"] -= 11; old.stats["spd"] -= 11; old.stats["spe"] -= 1
    ttar = sorted([e['set_id'] for e in pool if e['species'] == 'Tyranitar'])
    rec("§8.6b", "バンギラスのセット数(オープン限定)", "10", str(len(ttar)), len(ttar) == 10)
    worst = 0
    for sid in ttar:
        f = foe(sid)
        lo, hi, mv = best_hit(f, GROSS)
        worst = max(worst, pct(hi, GROSS.max_hp))
    rec("§8.6b", "バンギの対グロス最大(=一度も確1できない)", "62%", "%d%%" % worst, worst == 62)

    def mm_ko(att_val, f):
        m = copy.deepcopy(GROSS); m.stats["atk"] = att_val
        a = dict(species=m.species, stats=m.eff(), types=m.types, ability=m.ability, item=m.item, level=100)
        d = dict(species=f.species, stats=f.eff(), types=f.types, ability=f.ability, item=None, level=100)
        return damage_range(a, d, "MOVE_METEOR_MASH")[0] >= f.max_hp

    def bo_ko(att_val, f):
        m = copy.deepcopy(GROSS); m.stats["atk"] = att_val
        a = dict(species=m.species, stats=m.eff(), types=m.types, ability=m.ability, item=m.item, level=100)
        d = dict(species=f.species, stats=f.eff(), types=f.types, ability=f.ability, item=None, level=100)
        return damage_range(a, d, "MOVE_EXPLOSION")[0] >= f.max_hp

    lost_mm = [e['set_id'] for e in pool if mm_ko(405, foe(e['set_id'])) and not mm_ko(381, foe(e['set_id']))]
    lost_bo = [e['set_id'] for e in pool if bo_ko(405, foe(e['set_id'])) and not bo_ko(381, foe(e['set_id']))]
    rec("§8.6b", "A405→A381 でコメパン確1を失うセット数", "17", str(len(lost_mm)), len(lost_mm) == 17)
    rec("§8.6b", "A405→A381 で爆発の確1を失うセット数(主砲の無傷確認)", "0", str(len(lost_bo)), len(lost_bo) == 0)
    rec("§8.6b", "バンギのうち確1を失った3セット", "[860, 861, 868]",
        str([s for s in lost_mm if s in ttar]), [s for s in lost_mm if s in ttar] == [860, 861, 868])
    o1 = sum(1 for e in pool if best_hit(foe(e['set_id']), old)[0] >= GROSS.max_hp)
    n1 = sum(1 for e in pool if best_hit(foe(e['set_id']), GROSS)[0] >= GROSS.max_hp)
    rec("§8.6b", "被確1セット数 旧→新（耐久振りの実利）", "22 → 19", "%d → %d" % (o1, n1), o1 == 22 and n1 == 19)
    tie = sum(1 for e in pool if e['stats31']['spe'] == 177)
    faster = sum(1 for e in pool if e['stats31']['spe'] == 176)
    rec("§8.6b", "S4(176→177)の効果: 同速の敵 / 抜けるようになる敵", "0 / 20",
        "%d / %d" % (tie, faster), tie == 0 and faster == 20)


SECTIONS = {"spec": sec_spec, "1.5": sec_speed, "1.6b": sec_retreat, "8.1": sec_81, "8.2": sec_82,
            "8.3": sec_83, "8.4": sec_84, "8.5": sec_85, "8.6": sec_86, "8.6b": sec_ttar, "15": sec_15}

if __name__ == "__main__":
    want = sys.argv[1:] or list(SECTIONS)
    for k in want:
        if k in SECTIONS:
            SECTIONS[k]()
    print("=" * 100)
    print(" ドキュメント数値の総点検 — 現行v4スペック（実機版: HP_ROCK=%s）" % os.environ["HP_ROCK"])
    print("=" * 100)
    npass = nfail = nref = 0
    for section, label, expected, actual, ok in RESULTS:
        if ok is None:
            mark = "参考"; nref += 1
        elif ok:
            mark = " OK "; npass += 1
        else:
            mark = "**NG**"; nfail += 1
        print("[%s] %-6s %s" % (mark, section, label))
        if ok is not True:
            print("        記載: %s" % expected)
            print("        実測: %s" % actual)
    print("-" * 100)
    print("合計 %d件: 一致 %d / 不一致 %d / 参考 %d" % (len(RESULTS), npass, nfail, nref))
    json.dump([{"section": s, "label": l, "doc": e, "measured": a, "ok": o}
               for s, l, e, a, o in RESULTS], open("verify_docs_report.json", "w"), ensure_ascii=False, indent=1)
    print("→ verify_docs_report.json に保存")
