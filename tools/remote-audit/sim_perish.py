#!/usr/bin/env python3
"""P軸(ほろびパ)シミュレータ — 19-perish-team.md の構築を既存エンジンに載せる。

  ルージュラ @ラムのみ    ねこだまし/スキルスワップ/ひかりのかべ/まもる
  ラプラス   @カゴのみ    ほろびのうた/のろい/ねむる/まもる
  ソーナンス @たべのこし  あまえる/しんぴのまもり/カウンター/ミラーコート
  ムウマ     @カムラのみ  ほろびのうた/こらえる/いたみわけ/スキルスワップ

**sim.py は一切改変しない。** ソースを読み込んでメモリ上で execute() にフックを1行挿し、
不足効果(いたみわけ/あまえる/しんぴのまもり/自軍側の壁)をここで実装する。
凍結マラソン(sim_v4marathon.py)は sim.py をこのファイル経由では読まないので影響ゼロ。

使い方:
    python3 sim_perish.py <開始シード> <戦数> [--verbose]
"""
import os, sys, random, collections, json

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

# ---------------------------------------------------------------- エンジン読み込み＋フック挿入
_SRC = open('sim.py', encoding='utf-8').read()
_ANCHOR = '        mv=MOVES[move]; eff=mv["effect"]\n'
assert _SRC.count(_ANCHOR) == 1, "execute() のアンカーが一意に取れない（sim.py が変わった？）"
_SRC = _SRC.replace(_ANCHOR, _ANCHOR +
                    '        if _PERISH_HOOK(self, att, move, target, mv["effect"]): return\n')

NS = {'__name__': 'sim_perish_engine', '__file__': 'sim.py'}


def _hook_placeholder(*a, **k):
    return False


NS['_PERISH_HOOK'] = _hook_placeholder
exec(compile(_SRC, 'sim.py(perish-hooked)', 'exec'), NS)

MOVES = NS['MOVES']; Mon = NS['Mon']; Battle = NS['Battle']; make = NS['make']
STAGE_KEYS = NS['STAGE_KEYS']; PHYSICAL = NS['PHYSICAL']

# ---------------------------------------------------------------- 不足効果の実装
# 実装根拠は 19-perish-team.md §2 と pokeemerald 一次資料。

def _perish_hook(b, att, move, target, eff):
    """True を返すと sim.py 側の以降の処理をスキップ（＝この技はここで完結）。"""
    # --- いたみわけ: 双方のHPを平均化。みがわり持ちには失敗（Cmd_painsplitdmgcalc） ---
    if eff == "EFFECT_PAIN_SPLIT":
        t = target
        if t is None or not t.alive() or t.sub > 0:
            b.lg("%s pain split failed" % att.species); return True
        avg = (att.hp + t.hp) // 2
        att.hp = min(att.max_hp, avg); t.hp = min(t.max_hp, avg)
        b.lg("%s pain split -> %d / %d" % (att.species, att.hp, t.hp)); return True

    # --- あまえる: A-2（Cmd_statbuffchange 相当。クリアボディ/しろいけむり/かいりきバサミは無効） ---
    if eff == "EFFECT_ATTACK_DOWN_2":
        t = target
        if t is None or not t.alive(): return True
        if t.protected:
            b.lg("%s protected from charm" % t.species); return True
        if t.ability in ("ABILITY_CLEAR_BODY", "ABILITY_WHITE_SMOKE", "ABILITY_HYPER_CUTTER"):
            b.lg("%s ability blocked charm" % t.species); return True
        if t.sub > 0:
            b.lg("%s sub blocked charm" % t.species); return True
        old = t.stages["atk"]; t.stages["atk"] = max(-6, old - 2)
        b.lg("%s charm: %s atk %d -> %d" % (att.species, t.species, old, t.stages["atk"]))
        return True

    # --- しんぴのまもり: 自軍サイドに5ターン。状態異常と混乱を遮断 ---
    if eff == "EFFECT_SAFEGUARD":
        b.screens[att.side + "_safeguard"] = 5
        b.lg("%s safeguard (%s side)" % (att.species, att.side)); return True

    # --- 壁: sim.py は foe 側しか実装していないので us 側をここで足す ---
    if eff == "EFFECT_REFLECT" and att.side == "us":
        b.screens["us_reflect"] = 5; b.lg("%s reflect (us)" % att.species); return True
    if eff == "EFFECT_LIGHT_SCREEN" and att.side == "us":
        b.screens["us_light"] = 5; b.lg("%s light screen (us)" % att.species); return True
    return False


NS['_PERISH_HOOK'] = _perish_hook

# --- Battle.__init__ を包んで us 側の壁/しんぴのまもりキーを足す ---
_orig_init = Battle.__init__
def _init(self, *a, **k):
    _orig_init(self, *a, **k)
    self.screens.update({"us_reflect": 0, "us_light": 0,
                         "us_safeguard": 0, "foe_safeguard": 0})
Battle.__init__ = _init

# --- calc に us 側の壁を反映（ダブルは ×1/2 ではなく ×2/3。pokemon.c:3267/3318） ---
_orig_calc = Battle.calc
def _calc(self, att, dfd, move, crit=False, spread=False):
    dmg = _orig_calc(self, att, dfd, move, crit=crit, spread=spread)
    if dfd.side == "us" and not crit and dmg:
        mt = MOVES[move]["type"]
        allies = sum(1 for m in self.active["us"] if m is not None and m.alive())
        r = (2, 3) if allies == 2 else (1, 2)
        if self.screens["us_reflect"] > 0 and mt in PHYSICAL:
            dmg = dmg * r[0] // r[1]
        if self.screens["us_light"] > 0 and mt not in PHYSICAL:
            dmg = dmg * r[0] // r[1]
    return dmg
Battle.calc = _calc

# --- しんぴのまもり: 状態異常を弾く ---
_orig_try_status = Battle.try_status
def _try_status(self, dfd, st, src=None):
    if self.screens.get(dfd.side + "_safeguard", 0) > 0 and (src is None or src.side != dfd.side):
        self.lg("%s safeguarded" % dfd.species); return False
    return _orig_try_status(self, dfd, st, src)
Battle.try_status = _try_status

# --- end_turn: 追加した side status のカウントダウン ---
_orig_end_turn = Battle.end_turn
def _end_turn(self):
    r = _orig_end_turn(self)
    for k in ("us_reflect", "us_light", "us_safeguard", "foe_safeguard"):
        if self.screens.get(k, 0) > 0: self.screens[k] -= 1
    return r
Battle.end_turn = _end_turn

# ---------------------------------------------------------------- 自軍編成
# 実数値は 19-perish-team.md §0 と一致すること（起動時に assert する）
SPREADS = [
    # (種族, 性格, EV, 持ち物, 技, 特性, 期待実数値 H/B/D/S)
    ("Lapras", "Bold", {"hp": 252, "df": 252, "spd": 4}, "Chesto Berry",
     ["MOVE_PERISH_SONG", "MOVE_CURSE", "MOVE_REST", "MOVE_PROTECT"],
     "ABILITY_SHELL_ARMOR", (464, 284, 227, 156)),
    ("Jynx", "Timid", {"hp": 4, "df": 252, "spe": 252}, "Lum Berry",
     ["MOVE_FAKE_OUT", "MOVE_SKILL_SWAP", "MOVE_LIGHT_SCREEN", "MOVE_PROTECT"],
     "ABILITY_OBLIVIOUS", (272, 169, 226, 317)),
    ("Wobbuffet", "Bold", {"hp": 252, "df": 252, "spd": 4}, "Leftovers",
     ["MOVE_CHARM", "MOVE_SAFEGUARD", "MOVE_COUNTER", "MOVE_MIRROR_COAT"],
     "ABILITY_SHADOW_TAG", (584, 236, 153, 102)),
    ("Misdreavus", "Bold", {"hp": 252, "df": 252, "spd": 4}, "Salac Berry",
     ["MOVE_PERISH_SONG", "MOVE_ENDURE", "MOVE_PAIN_SPLIT", "MOVE_SKILL_SWAP"],
     "ABILITY_LEVITATE", (324, 240, 207, 206)),
]


def perish_team():
    team = []
    for sp, nat, ev, item, mv, ab, exp in SPREADS:
        d = make(sp, nat, ev, item, mv)
        m = Mon(d["species"], d["types"], ab, d["item"], d["stats"], d["moves"], "us")
        got = (m.stats["hp"], m.stats["df"], m.stats["spd"], m.stats["spe"])
        assert got == exp, "%s の実数値が19章と不一致: %s != %s" % (sp, got, exp)
        team.append(m)
    return team  # [Lapras(先発), Jynx(先発), Wobbuffet(控え), Misdreavus(控え)]


NS['our_team'] = perish_team

# ---------------------------------------------------------------- 方策
TRAP_ABILITIES = ("ABILITY_SHADOW_TAG", "ABILITY_ARENA_TRAP", "ABILITY_MAGNET_PULL")


def _traps_us(f, m):
    """f(敵)の特性が m(自駒)の交代を封じるか。battle_main.c:4248 準拠。"""
    if f.ability == "ABILITY_SHADOW_TAG": return True
    if f.ability == "ABILITY_ARENA_TRAP":
        return "TYPE_FLYING" not in m.types and m.ability != "ABILITY_LEVITATE"
    if f.ability == "ABILITY_MAGNET_PULL":
        return "TYPE_STEEL" in m.types
    return False


def _swap_priority(b, foes, me):
    """スキルスワップの優先順位: ①交代封じ特性 ②ぼうおん ③撃たない（19章 §4.1）"""
    for f in foes:
        if any(_traps_us(f, x) for x in b.active["us"] if x is not None and x.alive()):
            return f
    for f in foes:
        if f.ability == "ABILITY_SOUNDPROOF":
            return f
    return None


def _fakeout_target(b, foes, singer):
    """ラプラスをワンパンし得る側を優先。ゴーストにはねこだましが通らない。"""
    best = None; bestd = -1
    for f in foes:
        if "TYPE_GHOST" in f.types: continue
        d = 0
        for mv in NS['cand_moves'](f):
            if mv not in MOVES or MOVES[mv]["power"] < 2: continue
            d = max(d, b.pminmax(f, singer, mv)[1])
        if d > bestd: bestd, best = d, f
    return best


def _best_switchin(b, bench, foes):
    """今の敵2体からの最大被弾が最小の控えを選ぶ。"""
    def worst(m):
        d = 0
        for f in foes:
            for mv in NS['cand_moves'](f):
                if mv not in MOVES or MOVES[mv]["power"] < 2: continue
                d = max(d, b.pminmax(f, m, mv)[1])
        return d - m.hp  # 余裕が大きいほど小さい
    return min(bench, key=worst)


def perish_choose(b):
    acts = {}
    foes = [m for m in b.active["foe"] if m and m.alive()]
    if not foes: return acts
    ours = [m for m in b.active["us"] if m and m.alive()]
    bench = [m for m in b.bench["us"] if m and m.alive()]
    enemy_counted = any(f.perish is not None for f in foes)
    reserved = []

    for m in ours:
        sp = m.species

        # ① 交代封じ / ぼうおん の没収（19章 §4.1 の優先順位）
        if sp in ("Jynx", "Misdreavus") and "MOVE_SKILL_SWAP" in m.moves:
            tgt = _swap_priority(b, foes, m)
            if tgt is not None:
                acts[m] = ("move", "MOVE_SKILL_SWAP", tgt); continue

        # ② カウント持ちは最終ターン(perish<=1)に退避
        if m.perish is not None and m.perish <= 1:
            avail = [x for x in bench if x not in reserved]
            if avail and not any(_traps_us(f, m) for f in foes):
                # 敵にカウントが乗っているなら、ソーナンスを最優先で場に置く。
                # ShouldSwitchIfPerishSong は「かげふみが場にいる」だけで封殺されるので、
                # ここでソーナンスを出せないと敵は最終ターンに逃げて巡が丸ごと無駄になる。
                wob = next((x for x in avail if x.species == "Wobbuffet"), None)
                if wob is not None and any(f.perish is not None for f in foes):
                    rep = wob
                else:
                    rep = _best_switchin(b, avail, foes)
                reserved.append(rep)
                acts[m] = ("switch", m, rep); continue

        # ③ 歌う —— ★控えに生存が1体以上ある時だけ（19章 §1 の閾値）
        #    場の自駒は全員カウントを受けるので、控えが0だと全滅→B_OUTCOME_DREW→敗北
        if sp in ("Lapras", "Misdreavus") and "MOVE_PERISH_SONG" in m.moves:
            trapped = any(_traps_us(f, x) for f in foes for x in ours)
            singable = [f for f in foes if f.ability != "ABILITY_SOUNDPROOF"]
            if (not enemy_counted) and (not trapped) and singable and len(bench) >= 1 \
               and m.perish is None:
                acts[m] = ("move", "MOVE_PERISH_SONG", m)
                b.flags["perish_used"] += 1
                continue

        # ④ ムウマ: こらえる→カムラ発動→いたみわけ
        if sp == "Misdreavus":
            if m.hp * 4 <= m.max_hp and "MOVE_PAIN_SPLIT" in m.moves:
                acts[m] = ("move", "MOVE_PAIN_SPLIT", max(foes, key=lambda f: f.hp)); continue
            if m.hp * 2 <= m.max_hp and "MOVE_ENDURE" in m.moves and m.protect_streak == 0:
                acts[m] = ("move", "MOVE_ENDURE", m); continue
            acts[m] = ("move", "MOVE_PAIN_SPLIT", max(foes, key=lambda f: f.hp)); continue

        # ⑤ ルージュラ: 着地ターンはねこだまし → ひかりのかべ → まもる
        if sp == "Jynx":
            if m.first_turn and "MOVE_FAKE_OUT" in m.moves:
                singer = next((x for x in ours if x.species == "Lapras"), m)
                t = _fakeout_target(b, foes, singer)
                if t is not None:
                    acts[m] = ("move", "MOVE_FAKE_OUT", t); continue
            if b.screens["us_light"] == 0 and "MOVE_LIGHT_SCREEN" in m.moves:
                acts[m] = ("move", "MOVE_LIGHT_SCREEN", m); continue
            acts[m] = ("move", "MOVE_PROTECT", m); continue

        # ⑥ ソーナンス: あまえる → しんぴのまもり → 返し技
        if sp == "Wobbuffet":
            tgt = next((f for f in foes if f.stages["atk"] > -2
                        and f.ability not in ("ABILITY_CLEAR_BODY", "ABILITY_WHITE_SMOKE",
                                              "ABILITY_HYPER_CUTTER")), None)
            if tgt is not None and "MOVE_CHARM" in m.moves:
                acts[m] = ("move", "MOVE_CHARM", tgt); continue
            if b.screens["us_safeguard"] == 0 and "MOVE_SAFEGUARD" in m.moves:
                acts[m] = ("move", "MOVE_SAFEGUARD", m); continue
            phys = sum(1 for f in foes for mv in NS['cand_moves'](f)
                       if mv in MOVES and MOVES[mv]["power"] >= 2 and MOVES[mv]["type"] in PHYSICAL)
            spec = sum(1 for f in foes for mv in NS['cand_moves'](f)
                       if mv in MOVES and MOVES[mv]["power"] >= 2 and MOVES[mv]["type"] not in PHYSICAL)
            acts[m] = ("move", "MOVE_COUNTER" if phys >= spec else "MOVE_MIRROR_COAT", foes[0])
            continue

        # ⑦ ラプラス: 歌えないターンは のろい → ねむる → まもる
        if sp == "Lapras":
            if m.hp * 2 <= m.max_hp and "MOVE_REST" in m.moves and not m.item_used:
                acts[m] = ("move", "MOVE_REST", m); continue
            if m.stages["df"] < 2 and "MOVE_CURSE" in m.moves:
                acts[m] = ("move", "MOVE_CURSE", m); continue
            acts[m] = ("move", "MOVE_PROTECT", m); continue

        acts[m] = ("move", m.moves[0], m)
    return acts


NS['our_choose'] = perish_choose

play_battle = NS['play_battle']

# ---------------------------------------------------------------- 走行
if __name__ == "__main__":
    base = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    verbose = "--verbose" in sys.argv
    wins = 0; losses = []; flags = collections.Counter(); turns = []
    for i in range(n):
        seed = base + i
        b, r = play_battle(seed, verbose=verbose)
        turns.append(b.turn)
        for k, v in b.flags.items(): flags[k] += v
        if r == "win": wins += 1
        else: losses.append(seed)
    lose = n - wins
    print("=" * 72)
    print(" P軸(ほろびパ) %d戦  シード %d〜%d" % (n, base, base + n - 1))
    print("=" * 72)
    print(" 勝ち %d / 負け %d  →  **負け率 %.4f%%**" % (wins, lose, 100.0 * lose / n))
    print(" 平均ターン数 %.2f  (最大 %d)" % (sum(turns) / len(turns), max(turns)))
    if losses[:20]:
        print(" 負けシード(先頭20): %s" % losses[:20])
    print("\n フラグ上位:")
    for k, v in flags.most_common(15):
        print("   %-28s %d" % (k, v))
    json.dump({"base": base, "n": n, "wins": wins, "losses": losses,
               "flags": dict(flags), "avg_turns": sum(turns) / len(turns)},
              open("perish_result_%d_%d.json" % (base, n), "w"), ensure_ascii=False, indent=1)
