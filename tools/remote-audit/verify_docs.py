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
os.environ.setdefault("GROSS_A228", "1")  # 実機現行=グロスA228/B0/D24(2026-08-09採用)。旧EVで検算する場合は GROSS_A228=0

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
    exp = {'Zapdos': (322, 383, 299), 'Metagross': (364, 399, 177),
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
FAST15 = {454: (299, 112, 131), 455: (299, 112, 131), 522: (289, 112, 131), 656: (289, 122, 143),
          714: (289, 130, 153), 752: (289, 112, 131), 511: (285, 104, 123), 780: (279, 122, 143),
          874: (279, 130, 153), 742: (278, 110, 130), 743: (278, 110, 130), 769: (216, 130, 153),
          875: (216, 130, 153), 739: (196, 118, 140), 791: (194, 142, 168)}


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
    rec("§8.4", "#732ブースター spe149・確定OHKO", "spe149 / 118-139%",
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
    rec("§8.5", "ラティ兄妹の対グロス最大（確1不能の根拠）", "44%", "%d%%" % lati_max, lati_max == 44)
    e771 = best_hit(foe(771), GROSS)
    rec("§8.5", "#771エンテイの対グロス最大", "115%", "%d%%" % pct(e771[1], GROSS.max_hp),
        pct(e771[1], GROSS.max_hp) == 115)


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
    old = copy.deepcopy(GROSS)   # 旧A252型(v3): 405/296/216/S176 に明示ピン(歴史比較を現行EVから独立させる)
    old.stats["atk"] = 405; old.stats["df"] = 296; old.stats["spd"] = 216; old.stats["spe"] = 176
    v4f = copy.deepcopy(GROSS)   # v4凍結型: 381/307/227/S177
    v4f.stats["atk"] = 381; v4f.stats["df"] = 307; v4f.stats["spd"] = 227; v4f.stats["spe"] = 177
    ttar = sorted([e['set_id'] for e in pool if e['species'] == 'Tyranitar'])
    rec("§8.6b", "バンギラスのセット数(オープン限定)", "10", str(len(ttar)), len(ttar) == 10)
    worst = 0
    for sid in ttar:
        f = foe(sid)
        lo, hi, mv = best_hit(f, GROSS)
        worst = max(worst, pct(hi, GROSS.max_hp))
    rec("§8.6b", "バンギの対グロス最大(=一度も確1できない)", "63%", "%d%%" % worst, worst == 63)

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
    n1 = sum(1 for e in pool if best_hit(foe(e['set_id']), v4f)[0] >= GROSS.max_hp)
    c1 = sum(1 for e in pool if best_hit(foe(e['set_id']), GROSS)[0] >= GROSS.max_hp)
    rec("§8.6b", "被確1セット数 A252型→v4凍結→現行A228（耐久振りの実利は維持）", "22 → 19 → 19",
        "%d → %d → %d" % (o1, n1, c1), o1 == 22 and n1 == 19 and c1 == 19)
    tie = sum(1 for e in pool if e['stats31']['spe'] == 177)
    faster = sum(1 for e in pool if e['stats31']['spe'] == 176)
    rec("§8.6b", "S4(176→177)の効果: 同速の敵 / 抜けるようになる敵", "0 / 20",
        "%d / %d" % (tie, faster), tie == 0 and faster == 20)


# ---------------------------------------------------------------- §1 先発適性（ラグ先発敗北の分析）
def sec_lead():
    """12-playbook §1「なぜラグ先発にしないのか」(2026-08-09) の数値を再計算。
    軸=即死ライン数と、その即死ラインが種族名から読めるか（可視性）。"""
    from collections import Counter, defaultdict
    counts = {}
    mvs = {}
    for nm, m in (("Metagross", GROSS), ("Swampert", SWAMP), ("Zapdos", ZAP), ("Latios", LATI)):
        c1 = c1max = c2 = 0
        lethal = []
        for e in pool:
            lo, hi, mv = best_hit(foe(e['set_id']), m)
            if lo >= m.max_hp:
                c1 += 1
                lethal.append(mv)
            if hi >= m.max_hp:
                c1max += 1
            if 2 * lo >= m.max_hp:
                c2 += 1
        counts[nm] = (c1, c1max, c2)
        mvs[nm] = Counter(v.replace("MOVE_", "") for v in lethal)
    rec("§1", "被確1/被OHKO圏/被確2 グロス（A228採用後。被確1は不変・OHKO圏+1=#647）", "19/29/140",
        "%d/%d/%d" % counts["Metagross"], counts["Metagross"] == (19, 29, 140))
    rec("§1", "被確1/被OHKO圏/被確2 ラグ（即死ラインは2倍・被確2は逆に優位）", "38/47/94",
        "%d/%d/%d" % counts["Swampert"], counts["Swampert"] == (38, 47, 94))
    rec("§1", "被確1/被OHKO圏/被確2 サンダー / ラティ", "32/57/225 / 35/51/213",
        "%d/%d/%d / %d/%d/%d" % (counts["Zapdos"] + counts["Latios"]),
        counts["Zapdos"] == (32, 57, 225) and counts["Latios"] == (35, 51, 213))
    g = mvs["Metagross"]
    rec("§1", "グロス即死ラインの内訳（全て種族名で可視）", "オバヒ11/だいもんじ5/地震3",
        "%d/%d/%d" % (g["OVERHEAT"], g["FIRE_BLAST"], g["EARTHQUAKE"]),
        (g["OVERHEAT"], g["FIRE_BLAST"], g["EARTHQUAKE"]) == (11, 5, 3) and sum(g.values()) == 19)
    s = mvs["Swampert"]
    grass = s["SOLAR_BEAM"] + s["LEAF_BLADE"] + s["GIGA_DRAIN"]
    rec("§1", "ラグ即死ラインの内訳（爆発+草＝セット依存で不可視）", "爆発18/草20",
        "爆発%d/草%d" % (s["EXPLOSION"], grass), s["EXPLOSION"] == 18 and grass == 20 and sum(s.values()) == 38)
    by_sp = defaultdict(lambda: [0, 0])
    for e in pool:
        boom = any(MOVES.get(m, {}).get("effect") == "EFFECT_EXPLOSION" for m in e['moves'])
        by_sp[e['species']][0 if boom else 1] += 1
    pure = [sp for sp, (b, n) in by_sp.items() if b and not n]
    nmix = sum(1 for sp, (b, n) in by_sp.items() if b and n)
    rec("§1", "種族名から爆発持ちと確定できる種族数（全14種族が持ち/非持ち混在）", "0（混在14）",
        "%d（混在%d）" % (len(pure), nmix), pure == [] and nmix == 14)


# ---------------------------------------------------------------- §8.9 レジアイス全6セット
def sec_regice():
    """12-playbook §8.9 (2026-08-10)。A228採用の主目的だったレジアイス対面の全数固定。"""
    reg = sorted(e['set_id'] for e in pool if e['species'] == 'Regice')
    rec("§8.9", "レジアイスのセット列挙", "[763, 774, 785, 796, 838, 839]", str(reg),
        reg == [763, 774, 785, 796, 838, 839])
    res = {}
    for sid in reg:
        f = foe(sid)
        lo, hi = dmg(GROSS, f, "MOVE_METEOR_MASH")
        res[sid] = (lo, hi, f.max_hp)
    k1 = [s for s in reg if res[s][0] >= res[s][2]]
    rec("§8.9", "コメパン(A399)確1の4セット", "[763, 774, 785, 839]", str(k1), k1 == [763, 774, 785, 839])
    rec("§8.9", "#796(B極振り@たべのこし) コメパン通らず=確2どまり", "265-312 / HP364",
        "%d-%d / HP%d" % res[796], res[796] == (265, 312, 364) and 2 * 265 >= 364)
    lo, hi, hp = res[838]
    nko = sum(1 for r in range(85, 101) if hi * r // 100 >= hp)
    rec("§8.9", "#838(のろい/カウンター@たべのこし) コメパン乱1・非致死時のカウンター返しはグロス即死",
        "311-366 / 7ロール=43.7% / 返し>=622>=364",
        "%d-%d / %d/16 / %d" % (lo, hi, nko, 2 * lo), (lo, hi) == (311, 366) and nko == 7 and 2 * lo >= 364)
    bo796 = dmg(GROSS, foe(796), "MOVE_EXPLOSION")
    bo838 = dmg(GROSS, foe(838), "MOVE_EXPLOSION")
    rec("§8.9", "たべのこし2種への正解筋=爆発は両方確1", "796: 435-512 / 838: 513-604",
        "796: %d-%d / 838: %d-%d" % (bo796 + bo838), bo796[0] >= 364 and bo838[0] >= 343)


# ---------------------------------------------------------------- §15b メタグロスEV再配分の最適解
def sec_evopt():
    """15-v4-real-build「メタグロスEV再配分の最適解」(2026-08-09) の全数値を再計算。
    実数値の式: A=int((306+ev//4)*1.1) / B=296+ev//4 / D=216+ev//4（H252/S4固定）"""
    import copy

    def gross_ev(aev, bev, dev):
        m = copy.deepcopy(GROSS)
        m.stats["atk"] = int((306 + aev // 4) * 1.1)
        m.stats["df"] = 296 + bev // 4
        m.stats["spd"] = 216 + dev // 4
        return m

    cur = gross_ev(164, 44, 44)   # 旧v4凍結型(検証基準線)
    new = gross_ev(228, 0, 24)
    rec("§15b", "実数値式の整合（A228/B0/D24=現行399/296/222・2026-08-09採用）", "399/296/222",
        "%d/%d/%d" % (GROSS.stats["atk"], GROSS.stats["df"], GROSS.stats["spd"]),
        (new.stats["atk"], new.stats["df"], new.stats["spd"]) ==
        (GROSS.stats["atk"], GROSS.stats["df"], GROSS.stats["spd"]) == (399, 296, 222))

    def off_min(m, f):
        best = 0
        for mv in ("MOVE_METEOR_MASH", "MOVE_EARTHQUAKE"):
            a = dict(species=m.species, stats=m.eff(), types=m.types, ability=m.ability, item=m.item, level=100)
            d = dict(species=f.species, stats=f.eff(), types=f.types, ability=f.ability, item=None, level=100)
            best = max(best, damage_range(a, d, mv)[0])
        return best

    def k1set(aev):
        m = gross_ev(aev, 0, 0)
        return {e['set_id'] for e in pool if off_min(m, foe(e['set_id'])) >= foe(e['set_id']).max_hp}

    k164, k220, k228 = k1set(164), k1set(220), k1set(228)
    rec("§15b", "コメパン/地震の確1数 A164 / A220 / A228", "64 / 79 / 83",
        "%d / %d / %d" % (len(k164), len(k220), len(k228)),
        (len(k164), len(k220), len(k228)) == (64, 79, 83))
    regice = {763, 774, 785, 839}
    rec("§15b", "A228で新たに確1化するレジアイス4種", "[763, 774, 785, 839]",
        str(sorted(regice & (k228 - k164))), regice <= (k228 - k164))
    lo = damage_range(dict(species="Metagross", stats=gross_ev(228, 0, 24).eff(), types=GROSS.types,
                           ability=GROSS.ability, item=GROSS.item, level=100),
                      dict(species="Regice", stats=foe(763).eff(), types=foe(763).types,
                           ability=foe(763).ability, item=None, level=100), "MOVE_METEOR_MASH")[0]
    rec("§15b", "A228(399)コメパン最小 vs レジアイス#763 HP364", "367", str(lo), lo == 367)

    def hi_in(f, m):
        return best_hit(f, m)[1]

    f647, f622 = foe(647), foe(622)
    rec("§15b", "#647最大被弾 D44/D32/D24/D20", "360/362/366/368",
        "/".join(str(hi_in(f647, gross_ev(164, 0, d))) for d in (44, 32, 24, 20)),
        [hi_in(f647, gross_ev(164, 0, d)) for d in (44, 32, 24, 20)] == [360, 362, 366, 368])
    rec("§15b", "#622最大被弾 D24/D16/D8", "360/362/366",
        "/".join(str(hi_in(f622, gross_ev(164, 0, d))) for d in (24, 16, 8)),
        [hi_in(f622, gross_ev(164, 0, d)) for d in (24, 16, 8)] == [360, 362, 366])

    def over364(m):
        return {e['set_id'] for e in pool if hi_in(foe(e['set_id']), m) >= 364}

    base_over = over364(cur)
    d32_over = over364(gross_ev(164, 0, 32))
    d24_over = over364(gross_ev(164, 0, 24))
    rec("§15b", "B0/D32: 確定1発耐え喪失（全546走査）", "0件", "%d件" % len(d32_over - base_over),
        d32_over == base_over)
    rec("§15b", "B0/D24: 確定1発耐え喪失は#647のみ", "[647]", str(sorted(d24_over - base_over)),
        d24_over - base_over == {647})
    maro = hi_in(foe(470), gross_ev(164, 0, 44))
    rhy = hi_in(foe(499), gross_ev(164, 0, 44))
    rec("§15b", "B0の物理上限: ガラガラ#470(元から確定圏)/サイドン#499", "488(134%) / 338(92%)",
        "%d(%d%%) / %d(%d%%)" % (maro, pct(maro, 364), rhy, pct(rhy, 364)),
        maro == 488 and rhy == 338 and pct(rhy, 364) == 92)
    ohko_647 = sum(1 for r in range(85, 101) if 366 * r // 100 >= 364)
    rec("§15b", "#647転落時のOHKO率（max366・16ロール中）", "1/16=6.2%", "%d/16" % ohko_647, ohko_647 == 1)
    # A228でも水耐久の合算確殺ライン（グロスEQ+サンダー10まん）はフリップしない
    g228 = gross_ev(228, 0, 24)
    flips = []
    for e in pool:
        if e['species'] not in ('Lapras', 'Milotic'):
            continue
        f = foe(e['set_id'])
        zt = dmg(ZAP, f, "MOVE_THUNDERBOLT")[0]
        old_kill = dmg(cur, f, "MOVE_EARTHQUAKE")[0] + zt >= f.max_hp
        new_kill = dmg(g228, f, "MOVE_EARTHQUAKE")[0] + zt >= f.max_hp
        if old_kill != new_kill:
            flips.append(e['set_id'])
    rec("§15b", "ラプラス/ミロカロス12セット: グロスEQ+TB合算の確殺フリップ（A381→A399）", "0件",
        "%d件" % len(flips), flips == [])


# ---------------------------------------------------------------- §8.8 水耐久・地震耐え（合算打点）
def sec_bulk():
    """実戦報告「じしん+10まんで落ちない」「デンリュウ/ブースターがじしんを耐える」の数値化。
    要点=タイプ一致の有無で撃ち手が変わる（じしん=ラグ / 10まん=サンダー）。"""
    def dmgv(att, f, mv):
        a = dict(species=att.species, stats=att.eff(), types=att.types, ability=att.ability, item=att.item, level=100)
        d = dict(species=f.species, stats=f.eff(), types=f.types, ability=f.ability, item=None, level=100)
        return damage_range(a, d, mv)
    f456 = foe(456)
    gq = dmgv(GROSS, f456, "MOVE_EARTHQUAKE"); sq = dmgv(SWAMP, f456, "MOVE_EARTHQUAKE")
    zt = dmgv(ZAP, f456, "MOVE_THUNDERBOLT")
    rec("§8.8", "ラプラス#456 グロス地震+サンダー10万（乱数）", "374-440 / HP401",
        "%d-%d / HP%d" % (gq[0] + zt[0], gq[1] + zt[1], f456.max_hp),
        gq[0] + zt[0] == 374 and gq[0] + zt[0] < f456.max_hp)
    rec("§8.8", "ラプラス#456 ラグ地震+サンダー10万（確殺）", "405-477 / HP401",
        "%d-%d / HP%d" % (sq[0] + zt[0], sq[1] + zt[1], f456.max_hp),
        sq[0] + zt[0] == 405 and sq[0] + zt[0] >= f456.max_hp)
    # 最硬2セット: 最強の組み合わせでも乱数
    hard = []
    for sid in (822, 823):
        f = foe(sid)
        s_ = dmgv(SWAMP, f, "MOVE_EARTHQUAKE"); z_ = dmgv(ZAP, f, "MOVE_THUNDERBOLT")
        if s_[0] + z_[0] < f.max_hp <= s_[1] + z_[1]:
            hard.append(sid)
    rec("§8.8", "ラグ地震+サンダー10万でも乱数のラプラス", "[822, 823]", str(hard), hard == [822, 823])
    # じしん耐え: グロス地震で耐えるが、ラグ地震なら少なくとも乱1以上になるセット
    upgraded = []
    for e in pool:
        if e['species'] not in ('Ampharos', 'Flareon'):
            continue
        f = foe(e['set_id'])
        g = dmgv(GROSS, f, "MOVE_EARTHQUAKE"); s_ = dmgv(SWAMP, f, "MOVE_EARTHQUAKE")
        if g[1] < f.max_hp <= s_[1]:
            upgraded.append(e['set_id'])
    rec("§8.8", "グロス地震では耐えるがラグ地震なら落ちるセット", "[422, 540, 710]",
        str(sorted(upgraded)), sorted(upgraded) == [422, 540, 710])
    # タイプ一致倍率の確認
    ratio_eq = (sq[0] / gq[0])
    lt = dmgv(LATI, f456, "MOVE_THUNDERBOLT")
    ratio_tb = (lt[0] / zt[0])
    rec("§8.8", "地震の撃ち手倍率（ラグ/グロス）", "約1.30", "%.2f" % ratio_eq, 1.27 <= ratio_eq <= 1.33)
    rec("§8.8", "10まんの撃ち手倍率（ラティ/サンダー）", "約0.63", "%.2f" % ratio_tb, 0.60 <= ratio_tb <= 0.66)



# ---------------------------------------------------------------- §4.3 敵の爆発（危険ウィンドウ）
def sec_enemyboom():
    """実機で被弾した「敵ラス1の爆発」の数値化。AI原文の解禁条件は 12-playbook §4.3 に記載。"""
    ours = [("Zapdos", ZAP), ("Metagross", GROSS), ("Latios", LATI), ("Swampert", SWAMP)]

    def dv(f, att, mv):
        a = dict(species=f.species, stats=f.eff(), types=f.types, ability=f.ability, item=f.item, level=100)
        d = dict(species=att.species, stats=att.eff(), types=att.types, ability=att.ability, item=None, level=100)
        return damage_range(a, d, mv)

    boom = [e for e in pool if any(MOVES.get(m, {}).get("effect") == "EFFECT_EXPLOSION" for m in e['moves'])]
    rec("§4.3", "爆発/自爆を持つ敵セット数", "24", str(len(boom)), len(boom) == 24)
    # メタグロスは全爆発を確定耐え
    worst = 0; ko = 0
    for e in boom:
        f = foe(e['set_id'])
        mv = [m for m in e['moves'] if MOVES.get(m, {}).get("effect") == "EFFECT_EXPLOSION"][0]
        lo, hi = dv(f, GROSS, mv)
        worst = max(worst, pct(hi, GROSS.max_hp))
        if hi >= GROSS.max_hp:
            ko += 1
    rec("§4.3", "メタグロスが爆発でOHKOされるセット数 / 最大被弾", "0 / 74%",
        "%d / %d%%" % (ko, worst), ko == 0 and worst == 74)
    # フォレトス2セットは他3体を確定OHKO
    for sid in (575, 671):
        f = foe(sid)
        mv = [m for m in f.moves if MOVES.get(m, {}).get("effect") == "EFFECT_EXPLOSION"][0]
        koed = [nm for nm, m in ours if dv(f, m, mv)[0] >= m.max_hp]
        rec("§4.3", "フォレトス#%d の爆発が確定OHKOする自駒" % sid, "Zapdos/Latios/Swampert",
            "/".join(koed), koed == ["Zapdos", "Latios", "Swampert"])


# ---------------------------------------------------------------- §15c 次回リセットEV(A244/D8)とS振り棄却
def sec_ev244():
    """15-v4-real-build「2026-08-16 訂正・確定」＝A244/B0/D8採用とS振り全面棄却の再計算。"""
    import copy

    def gross(aev, dev, sev=4, hev=252):
        m = copy.deepcopy(GROSS)
        m.stats["hp"] = 301 + hev // 4
        m.stats["atk"] = int((306 + aev // 4) * 1.1)
        m.stats["df"] = 296
        m.stats["spd"] = 216 + dev // 4
        m.stats["spe"] = 176 + sev // 4
        return m

    rec("§15c", "A実数値式 A244/A248/A252", "403/404/405",
        "/".join(str(gross(a, 0).stats["atk"]) for a in (244, 248, 252)),
        [gross(a, 0).stats["atk"] for a in (244, 248, 252)] == [403, 404, 405])

    def off_min(m, f):
        return max(damage_range(
            dict(species=m.species, stats=m.eff(), types=m.types, ability=m.ability, item=m.item, level=100),
            dict(species=f.species, stats=f.eff(), types=f.types, ability=f.ability, item=None, level=100),
            mv)[0] for mv in ("MOVE_METEOR_MASH", "MOVE_EARTHQUAKE"))

    def k1set(aev):
        m = gross(aev, 0)
        return {e['set_id'] for e in pool if off_min(m, foe(e['set_id'])) >= foe(e['set_id']).max_hp}

    ks = {a: k1set(a) for a in (228, 232, 236, 240, 244, 248, 252)}
    got = [len(ks[a]) for a in (228, 232, 236, 240, 244, 248, 252)]
    rec("§15c", "確1数 A228/232/236/240/244/248/252", "83/84/85/85/88/88/88",
        "/".join(map(str, got)), got == [83, 84, 85, 85, 88, 88, 88])
    rec("§15c", "A244で新規確1化＝バンギラス3種", "[860, 861, 868]",
        str(sorted(ks[244] - ks[240])), ks[244] - ks[240] == {860, 861, 868})
    rec("§15c", "A248/A252はA244から1件も増えない（死票）", "増分0/0",
        "増分%d/%d" % (len(ks[248] - ks[244]), len(ks[252] - ks[244])),
        ks[248] == ks[252] == ks[244])

    def ko_set(m):
        """最強単発の最小ロールで落とされる=被確定OHKO"""
        out = set()
        for e in pool:
            f = foe(e['set_id'])
            blo = bhi = 0
            for mv in f.moves:
                if mv not in MOVES or MOVES[mv]["power"] < 2:
                    continue
                lo, hi = dmg(f, m, mv)
                if hi > bhi:
                    blo, bhi = lo, hi
            if blo >= m.stats["hp"]:
                out.add(e['set_id'])
        return out

    n244, n252 = len(ko_set(gross(244, 8))), len(ko_set(gross(252, 0)))
    rec("§15c", "被確定OHKO数 A244/D8 vs A252/D0（508EV同額）", "19 vs 22",
        "%d vs %d" % (n244, n252), (n244, n252) == (19, 22))
    rec("§15c", "A252案が失う3件（D0で確定OHKO化）", "[611, 718, 771]",
        str(sorted(ko_set(gross(252, 0)) - ko_set(gross(244, 8)))),
        ko_set(gross(252, 0)) - ko_set(gross(244, 8)) == {611, 718, 771})
    hi622 = [best_hit(foe(622), gross(244, d))[1] for d in (8, 16, 24)]
    rec("§15c", "#622キュウコン最大被弾 D8/D16/D24", "366/362/360",
        "/".join(map(str, hi622)), hi622 == [366, 362, 360])

    # --- S振り棄却 ---
    s176 = [e for e in pool if e['stats31']['spe'] == 176]
    rec("§15c", "プールのS176ちょうど（S4=177で抜ける）", "20セット",
        "%dセット" % len(s176), len(s176) == 20)
    band = [e for e in pool if 177 < e['stats31']['spe'] <= 239]
    rec("§15c", "S178-239帯（S252でのみ抜ける）", "133セット",
        "%dセット" % len(band), len(band) == 133)
    # S振り検討時はDも0（余剰EVを全てSへ回す前提）なのでD216基準で崖を測る
    cliff = ko_set(gross(244, 0, hev=228)) - ko_set(gross(244, 0, hev=252))
    rec("§15c", "D216基準・HP364→358の崖で確定OHKO化する3件", "[560, 618, 643]",
        str(sorted(cliff)), cliff == {560, 618, 643})
    fast = [e['species'] for e in pool if e['set_id'] in (560, 618, 643)]
    over239 = all(BY_ID[s]['stats31']['spe'] > 239 for s in (560, 618, 643))
    rec("§15c", "その3件はS252(239)でも抜けない", "全てS>239",
        "S%s" % [BY_ID[s]['stats31']['spe'] for s in (560, 618, 643)], over239)

    # --- 12章 バンギにはコメパン（じしんは確1ゼロ）---
    g = gross(244, 8)
    eq_k1 = [s for s in range(860, 870) if dmg(g, foe(s), "MOVE_EARTHQUAKE")[0] >= foe(s).max_hp]
    rec("§8.6b", "じしんで確1になるバンギラス", "0セット", "%dセット" % len(eq_k1), eq_k1 == [])
    mm = dmg(g, foe(860), "MOVE_METEOR_MASH")
    eq = dmg(g, foe(860), "MOVE_EARTHQUAKE")
    rec("§8.6b", "A403 vs #860(HP341) コメパン/じしん", "341-402(確1) / 227-268(確2)",
        "%d-%d / %d-%d" % (mm[0], mm[1], eq[0], eq[1]),
        (mm, eq) == ((341, 402), (227, 268)) and mm[0] >= foe(860).max_hp)

    # --- 03章 きあいパンチ×爆発 ---
    fp = [e for e in pool if "MOVE_FOCUS_PUNCH" in e['moves']]
    rec("§03", "プールのきあいパンチ持ち", "11セット", "%dセット" % len(fp), len(fp) == 11)
    tm = G.get('type_mult') or NS.get('type_mult')
    imm = [e for e in fp if 'ABILITY_WONDER_GUARD' in e['abilities']
           or 'TYPE_GHOST' in e['types']]
    rec("§03", "爆発を無効化できるきあいパンチ持ち（＝両立可能な例外）", "0セット",
        "%dセット" % len(imm), len(imm) == 0)
    boom = damage_range(
        dict(species="Metagross", stats=foe(835).eff(), types=foe(835).types,
             ability=foe(835).ability, item=foe(835).item, level=100),
        dict(species="Machamp", stats=foe(810).eff(), types=foe(810).types,
             ability=foe(810).ability, item=None, level=100), "MOVE_EXPLOSION")
    rec("§03", "グロス#835の爆発がカイリキー#810(HP384)を確定で消す", "最小≥384",
        "%d-%d" % boom, boom[0] >= foe(810).max_hp)


SECTIONS = {"spec": sec_spec, "1.5": sec_speed, "1.6b": sec_retreat, "8.1": sec_81, "8.2": sec_82,
            "8.3": sec_83, "8.4": sec_84, "8.5": sec_85, "8.6": sec_86, "8.6b": sec_ttar, "8.8": sec_bulk,
            "4.3": sec_enemyboom, "15": sec_15, "15b": sec_evopt, "1": sec_lead, "8.9": sec_regice,
            "15c": sec_ev244}

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
