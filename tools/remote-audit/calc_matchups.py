#!/usr/bin/env python3
"""
Gen3 (Emerald) exact damage calculator over the Battle Tower open-level steady pool (546 sets).
Ported from pokeemerald CalculateBaseDamage (pokemon.c:3106) + Cmd_typecalc (STAB->type mods)
+ ApplyRandomDmgMultiplier (85-100%). Level 100, neutral weather, no stat stages, no screens.
"""
import re, csv, json, os
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__)) + "/pokeemerald"
DATA = "/home/user/daily-tasks/battle-tower/data"
OUT = os.path.dirname(os.path.abspath(__file__)) + "/matchups"
os.makedirs(OUT, exist_ok=True)

def read(name):
    return open(f"{D}/{name}", encoding="utf-8", errors="replace").read()

# ---------- species base stats ----------
SPEC = {}
for m in re.finditer(r"\[(SPECIES_\w+)\]\s*=\s*\{(.*?)\n    \}", read("species_info.h"), re.S):
    b = m.group(2)
    g = lambda k: int(re.search(rf"\.{k}\s*=\s*(\d+)", b).group(1))
    ty = re.search(r"\.types\s*=\s*\{\s*(TYPE_\w+),\s*(TYPE_\w+)\s*\}", b)
    ab = re.search(r"\.abilities\s*=\s*\{\s*(ABILITY_\w+),\s*(ABILITY_\w+)\s*\}", b)
    if not (ty and ab):
        continue
    SPEC[m.group(1)] = dict(
        hp=g("baseHP"), atk=g("baseAttack"), df=g("baseDefense"),
        spe=g("baseSpeed"), spa=g("baseSpAttack"), spd=g("baseSpDefense"),
        types=(ty.group(1), ty.group(2)), abilities=(ab.group(1), ab.group(2)))

def spec_key(pretty_name):
    return "SPECIES_" + pretty_name.upper().replace(" ", "_").replace("-", "_").replace("'", "").replace(".", "")

# ---------- moves ----------
MOVES = {}
for m in re.finditer(r"\[(MOVE_\w+)\]\s*=\s*\{(.*?)\},", read("battle_moves.h"), re.S):
    b = m.group(2)
    def gi(k, default=0):
        mm = re.search(rf"\.{k}\s*=\s*(-?\d+)", b)
        return int(mm.group(1)) if mm else default
    eff = re.search(r"\.effect\s*=\s*(EFFECT_\w+)", b)
    ty = re.search(r"\.type\s*=\s*(TYPE_\w+)", b)
    tg = re.search(r"\.target\s*=\s*(MOVE_TARGET_\w+)", b)
    MOVES[m.group(1)] = dict(effect=eff.group(1) if eff else "?", power=gi("power"),
                             type=ty.group(1) if ty else "TYPE_NONE", accuracy=gi("accuracy"),
                             target=tg.group(1) if tg else "MOVE_TARGET_SELECTED", priority=gi("priority"))

def move_key(pretty):
    k = "MOVE_" + pretty.upper().replace(" ", "_").replace("-", "_").replace("'", "")
    return {"MOVE_FAINT_ATTACK": "MOVE_FAINT_ATTACK", "MOVE_SOFT_BOILED": "MOVE_SOFT_BOILED",
            "MOVE_WILL_O_WISP": "MOVE_WILL_O_WISP", "MOVE_SELF_DESTRUCT": "MOVE_SELF_DESTRUCT",
            "MOVE_MUD_SLAP": "MOVE_MUD_SLAP", "MOVE_DOUBLE_EDGE": "MOVE_DOUBLE_EDGE",
            "MOVE_LOCK_ON": "MOVE_LOCK_ON", "MOVE_X_SCISSOR": "MOVE_X_SCISSOR"}.get(k, k)

# ---------- type chart (parse gTypeEffectiveness triples) ----------
tchart = defaultdict(dict)   # tchart[atk][def] = mult (x10)
tbl = re.search(r"const u8 gTypeEffectiveness\[336\]\s*=\s*\{(.*?)\};", read("battle_main.c"), re.S).group(1)
rows = re.findall(r"(TYPE_\w+),\s*(TYPE_\w+),\s*(TYPE_MUL_\w+)", tbl)
MUL = {"TYPE_MUL_NO_EFFECT": 0, "TYPE_MUL_NOT_EFFECTIVE": 5, "TYPE_MUL_NORMAL": 10, "TYPE_MUL_SUPER_EFFECTIVE": 20}
# NOTE: the two ghost-immunity rows (Normal/Fighting -> Ghost = 0) sit AFTER the
# TYPE_FORESIGHT sentinel in gTypeEffectiveness so Foresight can skip them. We don't
# model Foresight (no enemy set carries it vs us in practice), so include them.
for a, d, mu in rows:
    if a == "TYPE_FORESIGHT":
        continue
    tchart[a][d] = MUL[mu]

def type_mult(move_type, def_types, def_ability):
    if def_ability == "ABILITY_LEVITATE" and move_type == "TYPE_GROUND":
        return 0
    m = 10
    seen = set()
    for dt in def_types:
        if dt in seen:
            continue
        seen.add(dt)
        m = m * tchart.get(move_type, {}).get(dt, 10) // 10
    return m  # x10 scale per unique type

PHYSICAL = {"TYPE_NORMAL", "TYPE_FIGHTING", "TYPE_FLYING", "TYPE_POISON", "TYPE_GROUND",
            "TYPE_ROCK", "TYPE_BUG", "TYPE_GHOST", "TYPE_STEEL"}

NATURE = {  # (up, down) stat keys, neutral if same
    "Hardy": None, "Docile": None, "Serious": None, "Bashful": None, "Quirky": None,
    "Lonely": ("atk", "df"), "Brave": ("atk", "spe"), "Adamant": ("atk", "spa"), "Naughty": ("atk", "spd"),
    "Bold": ("df", "atk"), "Relaxed": ("df", "spe"), "Impish": ("df", "spa"), "Lax": ("df", "spd"),
    "Timid": ("spe", "atk"), "Hasty": ("spe", "df"), "Jolly": ("spe", "spa"), "Naive": ("spe", "spd"),
    "Modest": ("spa", "atk"), "Mild": ("spa", "df"), "Quiet": ("spa", "spe"), "Rash": ("spa", "spd"),
    "Calm": ("spd", "atk"), "Gentle": ("spd", "df"), "Sassy": ("spd", "spe"), "Careful": ("spd", "spa")}

EVMAP = {"HP": "hp", "ATTACK": "atk", "DEFENSE": "df", "SPEED": "spe", "SP_ATTACK": "spa", "SP_DEFENSE": "spd"}

def calc_stats(base, ivs, evs, nature, level=100):
    st = {}
    st["hp"] = (2 * base["hp"] + ivs["hp"] + evs.get("hp", 0) // 4) * level // 100 + level + 10
    for k in ("atk", "df", "spe", "spa", "spd"):
        v = (2 * base[k] + ivs[k] + evs.get(k, 0) // 4) * level // 100 + 5
        nu = NATURE.get(nature)
        if nu:
            if nu[0] == k: v = v * 110 // 100
            elif nu[1] == k: v = v * 90 // 100
        st[k] = v
    return st

# item hold effects that matter for damage
TYPE_BOOST = {  # item pretty name -> (type, percent)
    "Charcoal": ("TYPE_FIRE", 10), "Mystic Water": ("TYPE_WATER", 10), "Magnet": ("TYPE_ELECTRIC", 10),
    "Miracle Seed": ("TYPE_GRASS", 10), "Never Melt Ice": ("TYPE_ICE", 10), "Sharp Beak": ("TYPE_FLYING", 10),
    "Poison Barb": ("TYPE_POISON", 10), "Soft Sand": ("TYPE_GROUND", 10), "Hard Stone": ("TYPE_ROCK", 10),
    "Silver Powder": ("TYPE_BUG", 10), "Spell Tag": ("TYPE_GHOST", 10), "Metal Coat": ("TYPE_STEEL", 10),
    "Twisted Spoon": ("TYPE_PSYCHIC", 10), "Black Belt": ("TYPE_FIGHTING", 10), "Black Glasses": ("TYPE_DARK", 10),
    "Silk Scarf": ("TYPE_NORMAL", 10), "Sea Incense": ("TYPE_WATER", 5), "Dragon Fang": ("TYPE_DRAGON", 10),
    "Deep Sea Tooth": None, "Light Ball": None}  # special-cased below

def damage_range(attacker, defender, move_name, crit=False, assume_def_ability=None):
    """attacker/defender: dict(stats, types, ability, item, species, level). Returns (min,max) damage; 0 if immune."""
    mv = MOVES[move_name]
    power = mv["power"]
    if power < 2:
        return (0, 0)
    mtype = mv["type"]
    atk = attacker["stats"]["atk"]; spa = attacker["stats"]["spa"]
    df = defender["stats"]["df"]; spd = defender["stats"]["spd"]
    def_ab = assume_def_ability if assume_def_ability else defender["ability"]

    # ability-based immunities / modifiers
    if def_ab == "ABILITY_WONDER_GUARD":
        if type_mult(mtype, defender["types"], def_ab) < 20:
            return (0, 0)
    if def_ab == "ABILITY_VOLT_ABSORB" and mtype == "TYPE_ELECTRIC": return (0, 0)
    if def_ab == "ABILITY_WATER_ABSORB" and mtype == "TYPE_WATER": return (0, 0)
    if def_ab == "ABILITY_FLASH_FIRE" and mtype == "TYPE_FIRE": return (0, 0)

    if attacker["ability"] in ("ABILITY_HUGE_POWER", "ABILITY_PURE_POWER"):
        atk *= 2
    item = attacker.get("item", "")
    tb = TYPE_BOOST.get(item)
    if tb and tb[0] == mtype:
        if mtype in PHYSICAL: atk = atk * (100 + tb[1]) // 100
        else: spa = spa * (100 + tb[1]) // 100
    if item == "Choice Band":
        atk = atk * 150 // 100
    if item == "Deep Sea Tooth" and attacker["species"] == "Clamperl": spa *= 2
    if item == "Light Ball" and attacker["species"] == "Pikachu": spa *= 2
    if item == "Thick Club" and attacker["species"] in ("Cubone", "Marowak"): atk *= 2
    if def_ab == "ABILITY_THICK_FAT" and mtype in ("TYPE_FIRE", "TYPE_ICE"):
        spa //= 2
    if attacker["ability"] == "ABILITY_HUSTLE":
        atk = atk * 150 // 100

    if mv["effect"] == "EFFECT_EXPLOSION":
        df //= 2

    level = attacker.get("level", 100)
    if mtype in PHYSICAL:
        dmg = atk * power * (2 * level // 5 + 2) // df // 50
        if dmg == 0: dmg = 1
    else:
        dmg = spa * power * (2 * level // 5 + 2) // spd // 50
    dmg += 2
    if crit:
        dmg *= 2
    # STAB
    if mtype in attacker["types"]:
        dmg = dmg * 15 // 10
    # type effectiveness (per defender type, x/10 each)
    seen = set()
    if def_ab == "ABILITY_LEVITATE" and mtype == "TYPE_GROUND":
        return (0, 0)
    for dt in defender["types"]:
        if dt in seen: continue
        seen.add(dt)
        dmg = dmg * tchart.get(mtype, {}).get(dt, 10) // 10
    if dmg == 0:
        return (0, 0)
    lo = dmg * 85 // 100
    if lo == 0: lo = 1
    return (lo, dmg)

# ---------- load enemy pool ----------
pool = []
for r in csv.DictReader(open(f"{DATA}/frontier_sets.csv")):
    if r["in_pool_battle50plus"] != "1":
        continue
    sk = spec_key(r["species"])
    if sk == "SPECIES_MR_MIME": sk = "SPECIES_MR_MIME"
    base = SPEC[sk]
    evs = {}
    for part in r["ev_spread"].split("|"):
        evs[EVMAP[part]] = 255 if len(r["ev_spread"].split("|")) == 2 else 170
    moves = []
    for i in (1, 2, 3, 4):
        nm = r[f"move{i}"]
        if nm and nm != "None":
            mk = move_key(nm)
            if mk == "MOVE_SELFDESTRUCT": mk = "MOVE_SELF_DESTRUCT"
            if mk not in MOVES:
                # fix common name diffs
                alt = {"MOVE_FAINT_ATTACK": "MOVE_FAINT_ATTACK", "MOVE_SMELLING_SALT": "MOVE_SMELLINGSALT",
                       "MOVE_SAND_ATTACK": "MOVE_SAND_ATTACK"}.get(mk)
                mk = alt if alt in MOVES else mk
            moves.append(mk)
    entry = dict(set_id=int(r["set_id"]), species=r["species"], item=r["item"], nature=r["nature"],
                 base=base, evs=evs, moves=moves, types=base["types"], abilities=base["abilities"])
    for iv in (21, 31):
        ivs = {k: iv for k in ("hp", "atk", "df", "spe", "spa", "spd")}
        entry[f"stats{iv}"] = calc_stats(base, ivs, evs, r["nature"])
    pool.append(entry)

missing = [m for e in pool for m in e["moves"] if m not in MOVES]
assert not missing, f"missing moves: {set(missing)}"
print(f"pool loaded: {len(pool)} sets")

# ---------- our candidates ----------
IV31 = {k: 31 for k in ("hp", "atk", "df", "spe", "spa", "spd")}
def make(species_pretty, nature, evs, item, moves, ability=None, ivs=IV31):
    sk = spec_key(species_pretty)
    base = SPEC[sk]
    ab = ability if ability else base["abilities"][0]
    return dict(species=species_pretty, stats=calc_stats(base, ivs, evs, nature), types=base["types"],
                ability=ab, item=item, level=100, moves=moves, nature=nature, evs=evs)

CANDS = {
    "Metagross_CB": make("Metagross", "Adamant", {"hp": 252, "atk": 252, "df": 4}, "Choice Band",
                         ["MOVE_EXPLOSION", "MOVE_METEOR_MASH", "MOVE_EARTHQUAKE", "MOVE_SHADOW_BALL"]),
    "Metagross_Lum": make("Metagross", "Adamant", {"hp": 252, "atk": 252, "df": 4}, "Lum Berry",
                          ["MOVE_EXPLOSION", "MOVE_METEOR_MASH", "MOVE_EARTHQUAKE", "MOVE_SHADOW_BALL"]),
    "Gengar_CS": make("Gengar", "Timid", {"spa": 252, "spe": 252, "hp": 4}, "Bright Powder",
                      ["MOVE_THUNDERBOLT", "MOVE_ICE_PUNCH", "MOVE_PSYCHIC", "MOVE_SLUDGE_BOMB", "MOVE_FIRE_PUNCH", "MOVE_GIGA_DRAIN"]),
    "Gengar_HS": make("Gengar", "Timid", {"hp": 252, "spe": 252, "spa": 4}, "Bright Powder",
                      ["MOVE_THUNDERBOLT", "MOVE_ICE_PUNCH", "MOVE_PSYCHIC"]),
    "Latios_CS": make("Latios", "Timid", {"spa": 252, "spe": 252, "hp": 4}, "Lum Berry",
                      ["MOVE_PSYCHIC", "MOVE_ICE_BEAM", "MOVE_THUNDERBOLT", "MOVE_DRAGON_CLAW"]),
    "Latios_Modest": make("Latios", "Modest", {"spa": 252, "spe": 252, "hp": 4}, "Lum Berry",
                          ["MOVE_PSYCHIC", "MOVE_ICE_BEAM", "MOVE_THUNDERBOLT", "MOVE_DRAGON_CLAW"]),
    "Snorlax_HD": make("Snorlax", "Careful", {"hp": 188, "atk": 68, "spd": 252}, "Leftovers",
                       ["MOVE_RETURN", "MOVE_SHADOW_BALL", "MOVE_EARTHQUAKE", "MOVE_SELF_DESTRUCT", "MOVE_BODY_SLAM"],
                       ability="ABILITY_THICK_FAT"),
    "Snorlax_HA": make("Snorlax", "Adamant", {"hp": 252, "atk": 252, "spd": 4}, "Leftovers",
                       ["MOVE_RETURN", "MOVE_SHADOW_BALL", "MOVE_EARTHQUAKE", "MOVE_SELF_DESTRUCT", "MOVE_BODY_SLAM"],
                       ability="ABILITY_THICK_FAT"),
    "Zapdos": make("Zapdos", "Modest", {"spa": 252, "spe": 252, "hp": 4}, "Leftovers",
                   ["MOVE_THUNDERBOLT", "MOVE_HIDDEN_POWER", "MOVE_DRILL_PECK"]),
    "Suicune": make("Suicune", "Bold", {"hp": 252, "df": 252, "spd": 4}, "Leftovers",
                    ["MOVE_SURF", "MOVE_ICE_BEAM"]),
    "Salamence": make("Salamence", "Adamant", {"hp": 4, "atk": 252, "spe": 252}, "Lum Berry",
                      ["MOVE_EARTHQUAKE", "MOVE_ROCK_SLIDE", "MOVE_AERIAL_ACE", "MOVE_DRAGON_CLAW"],
                      ability="ABILITY_INTIMIDATE"),
    "Swampert": make("Swampert", "Adamant", {"hp": 252, "atk": 252, "spd": 4}, "Lum Berry",
                     ["MOVE_EARTHQUAKE", "MOVE_ROCK_SLIDE", "MOVE_SURF"]),
}

# HP Ice for Zapdos: custom special 70 ice
MOVES["MOVE_HP_ICE"] = dict(effect="EFFECT_HIT", power=70, type="TYPE_ICE", accuracy=100,
                            target="MOVE_TARGET_SELECTED", priority=0)
CANDS["Zapdos"]["moves"] = ["MOVE_THUNDERBOLT", "MOVE_HP_ICE", "MOVE_DRILL_PECK"]

# Runtime-computed powers: Return/Frustration = 102 (enemies: max friendship default,
# friendship forced to 0 when the set has Frustration -> both hit max power).
# Enemy Hidden Power: IV21 and IV31 both yield HP Dark 70 (all LSB/bit2 = 1).
MOVES["MOVE_RETURN"] = dict(MOVES["MOVE_RETURN"], power=102)
MOVES["MOVE_FRUSTRATION"] = dict(MOVES["MOVE_FRUSTRATION"], power=102)
MOVES["MOVE_HIDDEN_POWER"] = dict(MOVES["MOVE_HIDDEN_POWER"], power=70, type="TYPE_DARK")

# ---------- Analysis 1: our coverage vs pool ----------
def enemy_as_defender(e, iv):
    # worst-case ability branch chosen per move at call time
    return dict(species=e["species"], stats=e[f"stats{iv}"], types=e["types"],
                ability=None, item=e["item"], level=100)

def coverage(att_key, move, iv=31):
    att = CANDS[att_key]
    res = dict(guaranteed=[], possible=[], never=[], immune=[])
    for e in pool:
        d = enemy_as_defender(e, iv)
        worst = None
        for ab in set(a for a in e["abilities"] if a != "ABILITY_NONE"):
            lo, hi = damage_range(att, dict(d, ability=ab), move)
            if worst is None or (lo, hi) < worst:
                worst = (lo, hi)
        lo, hi = worst
        hp = e[f"stats{iv}"]["hp"]
        tag = f"#{e['set_id']} {e['species']}"
        if hi == 0:
            res["immune"].append(tag)
        elif lo >= hp and e["item"] != "Focus Band":
            res["guaranteed"].append(tag)
        elif hi >= hp:
            res["possible"].append(tag + (" (FocusBand)" if e["item"] == "Focus Band" else f" ({lo*100//hp}-{hi*100//hp}%)"))
        else:
            res["never"].append(tag + f" ({lo*100//hp}-{hi*100//hp}%)")
    return res

# ---------- Analysis 2: incoming damage vs our candidates ----------
def incoming(def_key, iv=31, crit=False):
    """for each enemy set: best single-move damage vs our candidate; return OHKO list and heavy hitters"""
    dfd = CANDS[def_key]
    hp = dfd["stats"]["hp"]
    ohko, heavy = [], []
    for e in pool:
        best = (0, 0, "")
        for mk in e["moves"]:
            mv = MOVES[mk]
            if mv["power"] < 2:
                continue
            # enemy attacker: worst-case ability branch (max damage)
            for ab in set(a for a in e["abilities"] if a != "ABILITY_NONE"):
                atk = dict(species=e["species"], stats=e[f"stats{iv}"], types=e["types"],
                           ability=ab, item=e["item"], level=100)
                lo, hi = damage_range(atk, dfd, mk, crit=crit)
                if hi > best[1]:
                    best = (lo, hi, mk)
        lo, hi, mk = best
        if lo >= hp:
            ohko.append(f"#{e['set_id']} {e['species']} {mk.replace('MOVE_','')} 確定 ({lo}-{hi}/{hp})")
        elif hi >= hp:
            ohko.append(f"#{e['set_id']} {e['species']} {mk.replace('MOVE_','')} 乱数 ({lo*100//hp}-{hi*100//hp}%)")
        elif hi >= hp * 8 // 10:
            heavy.append(f"#{e['set_id']} {e['species']} {mk.replace('MOVE_','')} ({lo*100//hp}-{hi*100//hp}%)")
    return ohko, heavy

# ---------- Analysis 3: speed ----------
def speed_report(iv=31):
    ours = {k: v["stats"]["spe"] for k, v in CANDS.items()}
    rep = {}
    for k, s in ours.items():
        faster = [f"#{e['set_id']} {e['species']} ({e[f'stats{iv}']['spe']})" for e in pool if e[f"stats{iv}"]["spe"] > s]
        tied = [f"#{e['set_id']} {e['species']}" for e in pool if e[f"stats{iv}"]["spe"] == s]
        rep[k] = dict(speed=s, n_faster=len(faster), faster=faster, tied=tied)
    return rep

results = {}

# Explosion coverage (CB / Lum)
for key in ("Metagross_CB", "Metagross_Lum"):
    cov = coverage(key, "MOVE_EXPLOSION")
    results[f"explosion_{key}"] = {k: len(v) for k, v in cov.items()}
    results[f"explosion_{key}_detail"] = cov
# other Metagross moves
for mv in ("MOVE_METEOR_MASH", "MOVE_EARTHQUAKE", "MOVE_SHADOW_BALL"):
    cov = coverage("Metagross_CB", mv)
    results[f"cov_Metagross_CB_{mv}"] = {k: len(v) for k, v in cov.items()}
# Latios / Gengar / Zapdos nukes
for att, mv in (("Latios_Modest", "MOVE_ICE_BEAM"), ("Latios_Modest", "MOVE_PSYCHIC"),
                ("Latios_Modest", "MOVE_THUNDERBOLT"), ("Gengar_CS", "MOVE_THUNDERBOLT"),
                ("Gengar_CS", "MOVE_ICE_PUNCH"), ("Gengar_CS", "MOVE_PSYCHIC"),
                ("Zapdos", "MOVE_THUNDERBOLT"), ("Snorlax_HA", "MOVE_SELF_DESTRUCT"),
                ("Snorlax_HA", "MOVE_RETURN")):
    cov = coverage(att, mv)
    results[f"cov_{att}_{mv}"] = {k: len(v) for k, v in cov.items()}

# Incoming
for key in CANDS:
    ohko, heavy = incoming(key)
    results[f"in_{key}"] = dict(n_ohko=len(ohko), ohko=ohko, n_heavy=len(heavy))
    ohko_c, _ = incoming(key, crit=True)
    results[f"in_{key}_crit"] = dict(n_ohko_crit=len(ohko_c))

results["speed"] = speed_report()

with open(f"{OUT}/report.json", "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)

# ---------- console summary ----------
print("\n=== 爆発カバレッジ (対546セット・敵IV31・持ち物/特性は最悪ケース) ===")
for key in ("Metagross_CB", "Metagross_Lum"):
    r = results[f"explosion_{key}"]
    print(f"{key}: 確1={r['guaranteed']} 乱1={r['possible']} 耐え={r['never']} 無効={r['immune']}")
print("\n=== 爆発を確定で耐える敵 (CB) ===")
for t in results["explosion_Metagross_CB_detail"]["never"]:
    print(" ", t)
print("\n=== 単体技カバレッジ (確1数/乱1数/無効数) ===")
for k in results:
    if k.startswith("cov_"):
        r = results[k]
        print(f"{k}: 確1={r['guaranteed']} 乱1={r['possible']} 耐え={r['never']} 無効={r['immune']}")
print("\n=== 被弾: 各候補を1発で落としうる敵セット数 (非急所/急所込み) ===")
for key in CANDS:
    print(f"{key}: OHKO敵={results[f'in_{key}']['n_ohko']} (急所込み={results[f'in_{key}_crit']['n_ohko_crit']}), 8割以上={results[f'in_{key}']['n_heavy']}")
print("\n=== 素早さ ===")
for k, v in results["speed"].items():
    print(f"{k}: 実数値{v['speed']} / 抜かれる={v['n_faster']}セット 同速={len(v['tied'])}")
