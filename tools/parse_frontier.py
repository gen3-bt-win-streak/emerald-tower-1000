#!/usr/bin/env python3
"""Parse pokeemerald battle frontier data into CSVs + danger report for the Battle Tower project."""
import re, csv, json, os
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__)) + "/pokeemerald"
OUT = "/home/user/daily-tasks/battle-tower/data"
os.makedirs(OUT, exist_ok=True)

def read(name):
    with open(f"{D}/{name}", encoding="utf-8", errors="replace") as f:
        return f.read()

# ---------- constants: FRONTIER_MON_* -> id ----------
mon_const = {}
for m in re.finditer(r"#define\s+(FRONTIER_MON_\w+)\s+(\d+)", read("frontier_mons_constants.h")):
    mon_const[m.group(1)] = int(m.group(2))
HIGH_TIER = 849

# ---------- constants: FRONTIER_TRAINER_* -> id ----------
tr_const = {}
for m in re.finditer(r"#define\s+(FRONTIER_TRAINER_\w+)\s+(\d+)", read("frontier_trainers_constants.h")):
    tr_const[m.group(1)] = int(m.group(2))

# ---------- item table: BATTLE_FRONTIER_ITEM_* -> ITEM_* ----------
bf_item_idx = {}
for m in re.finditer(r"#define\s+(BATTLE_FRONTIER_ITEM_\w+)\s+(\d+)", read("battle_frontier.h")):
    bf_item_idx[m.group(1)] = int(m.group(2))
held = {}
tbl = re.search(r"gBattleFrontierHeldItems\[\]\s*=\s*\{(.*?)\};", read("battle_tower.c"), re.S).group(1)
for m in re.finditer(r"\[(BATTLE_FRONTIER_ITEM_\w+)\]\s*=\s*(ITEM_\w+)", tbl):
    held[m.group(1)] = m.group(2)

def pretty(sym, prefix):
    return sym.replace(prefix, "", 1).replace("_", " ").title().strip()

# ---------- species info ----------
sp = {}
txt = read("species_info.h")
for m in re.finditer(r"\[(SPECIES_\w+)\]\s*=\s*\{(.*?)\n    \}", txt, re.S):
    body = m.group(2)
    d = {}
    g = lambda k: re.search(k, body)
    hp = g(r"\.baseHP\s*=\s*(\d+)"); spd = g(r"\.baseSpeed\s*=\s*(\d+)")
    ty = g(r"\.types\s*=\s*\{\s*(TYPE_\w+),\s*(TYPE_\w+)\s*\}")
    ab = g(r"\.abilities\s*=\s*\{\s*(ABILITY_\w+),\s*(ABILITY_\w+)\s*\}")
    if not (ty and ab):
        continue
    d["types"] = (ty.group(1), ty.group(2))
    d["abilities"] = (ab.group(1), ab.group(2))
    d["baseSpeed"] = int(spd.group(1)) if spd else 0
    d["baseHP"] = int(hp.group(1)) if hp else 0
    sp[m.group(1)] = d

# ---------- frontier mon sets ----------
sets = {}
txt = read("battle_frontier_mons.h")
for m in re.finditer(
    r"\[(FRONTIER_MON_\w+)\]\s*=\s*\{\s*"
    r"\.species\s*=\s*(SPECIES_\w+),\s*"
    r"\.moves\s*=\s*\{(.*?)\},\s*"
    r"\.itemTableId\s*=\s*(BATTLE_FRONTIER_ITEM_\w+),\s*"
    r"\.evSpread\s*=\s*(.*?),\s*"
    r"\.nature\s*=\s*(NATURE_\w+)", txt, re.S):
    const, species, moves, item, ev, nature = m.groups()
    sid = mon_const[const]
    moves = [x.strip() for x in moves.split(",")]
    sets[sid] = dict(const=const, species=species, moves=moves, item=item,
                     ev=ev.replace("F_EV_SPREAD_", "").replace(" ", ""), nature=nature)
assert len(sets) == 882, len(sets)

# ---------- trainer mon-set lists (expand via real C preprocessor) ----------
import subprocess
cpp_input = f'#include "{D}/frontier_mons_constants.h"\n#include "{D}/battle_frontier_trainer_mons.h"\n'
expanded = subprocess.run(["cpp", "-P", "-"], input=cpp_input, capture_output=True,
                          text=True, check=True).stdout

trainer_monsets = {}
for m in re.finditer(r"const u16 (gBattleFrontierTrainerMons_\w+)\[\]\s*=\s*\{(.*?)\};", expanded, re.S):
    ids = [int(x, 0) for x in re.findall(r"-?(?:0x[0-9A-Fa-f]+|\d+)", m.group(2))]
    trainer_monsets[m.group(1)] = [i for i in ids if 0 <= i < 882 and i != 0xFFFF]
assert all(len(v) > 0 for v in trainer_monsets.values()), "empty monset after cpp expansion"

# ---------- trainers ----------
trainers = {}
txt = read("battle_frontier_trainers.h")
for m in re.finditer(
    r"\[(FRONTIER_TRAINER_\w+)\]\s*=\s*\{\s*"
    r"\.facilityClass\s*=\s*(FACILITY_CLASS_\w+),\s*"
    r"\.trainerName\s*=\s*_\(\"([^\"]+)\"\)(.*?)\.monSet\s*=\s*(gBattleFrontierTrainerMons_\w+)", txt, re.S):
    const, fclass, name, _, monset = m.groups()
    tid = tr_const[const]
    trainers[tid] = dict(const=const, fclass=fclass, name=name, monset=monset)
assert len(trainers) == 300, len(trainers)

def fixed_iv(tid):
    for lim, iv in ((99, 3), (119, 6), (139, 9), (159, 12), (179, 15), (199, 18), (219, 21)):
        if tid <= lim:
            return iv
    return 31

# ---------- lategame pool (battles 50+ = trainers 200-299) ----------
lategame_sets_all = set()
set_users = defaultdict(list)   # set id -> lategame trainer ids
for tid in range(200, 300):
    for s in trainer_monsets[trainers[tid]["monset"]]:
        lategame_sets_all.add(s)
        set_users[s].append(tid)
lategame_lv50 = {s for s in lategame_sets_all if s <= HIGH_TIER}

# ---------- write frontier_sets.csv ----------
with open(f"{OUT}/frontier_sets.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["set_id", "species", "type1", "type2", "ability1", "ability2", "base_speed",
                "item", "nature", "ev_spread", "move1", "move2", "move3", "move4",
                "lv50_allowed", "in_pool_battle50plus", "lategame_trainer_count"])
    for sid in sorted(sets):
        s = sets[sid]
        info = sp.get(s["species"], {})
        ty = info.get("types", ("?", "?")); ab = info.get("abilities", ("?", "?"))
        mv = [x.replace("MOVE_", "").replace("_", " ").title() for x in s["moves"]]
        w.writerow([sid, pretty(s["species"], "SPECIES_"),
                    ty[0].replace("TYPE_", "").title(), ty[1].replace("TYPE_", "").title(),
                    pretty(ab[0], "ABILITY_"), pretty(ab[1], "ABILITY_"),
                    info.get("baseSpeed", ""),
                    pretty(held[s["item"]], "ITEM_"), s["nature"].replace("NATURE_", "").title(),
                    s["ev"], *mv,
                    int(sid <= HIGH_TIER), int(sid in lategame_sets_all), len(set_users.get(sid, []))])

# ---------- write trainers.csv ----------
with open(f"{OUT}/trainers.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["trainer_id", "name", "facility_class", "fixed_iv", "monset_size", "set_ids"])
    for tid in sorted(trainers):
        t = trainers[tid]
        ms = trainer_monsets[t["monset"]]
        w.writerow([tid, t["name"], t["fclass"].replace("FACILITY_CLASS_", ""), fixed_iv(tid),
                    len(ms), "|".join(map(str, sorted(ms)))])

# ---------- danger report over the battle-50+ pool ----------
def sets_with_move(moves, pool):
    res = []
    for sid in sorted(pool):
        hit = [mv for mv in sets[sid]["moves"] if mv in moves]
        if hit:
            res.append(sid)
    return res

def sets_with_item(items, pool):
    return [sid for sid in sorted(pool) if held[sets[sid]["item"]] in items]

def sets_with_ability(abils, pool):
    """species where the dangerous ability is possible (either slot)"""
    res = []
    for sid in sorted(pool):
        ab = sp.get(sets[sid]["species"], {}).get("abilities", ())
        if any(a in abils for a in ab):
            res.append(sid)
    return res

def sets_with_type(t, pool):
    return [sid for sid in sorted(pool)
            if t in sp.get(sets[sid]["species"], {}).get("types", ())]

MOVES = {
    "OHKO": {"MOVE_FISSURE", "MOVE_HORN_DRILL", "MOVE_GUILLOTINE", "MOVE_SHEER_COLD"},
    "SLEEP": {"MOVE_SPORE", "MOVE_HYPNOSIS", "MOVE_SLEEP_POWDER", "MOVE_LOVELY_KISS",
              "MOVE_SING", "MOVE_GRASS_WHISTLE", "MOVE_YAWN"},
    "EXPLOSION": {"MOVE_EXPLOSION", "MOVE_SELF_DESTRUCT", "MOVE_SELFDESTRUCT"},
    "DESTINY_BOND": {"MOVE_DESTINY_BOND", "MOVE_GRUDGE"},
    "PERISH_SONG": {"MOVE_PERISH_SONG"},
    "PROTECT": {"MOVE_PROTECT", "MOVE_DETECT"},
    "COUNTER": {"MOVE_COUNTER", "MOVE_MIRROR_COAT"},
    "TRICK": {"MOVE_TRICK"},
    "EVASION": {"MOVE_DOUBLE_TEAM", "MOVE_MINIMIZE"},
    "ATTRACT": {"MOVE_ATTRACT"},
    "CONFUSE_RAY": {"MOVE_CONFUSE_RAY", "MOVE_SWAGGER", "MOVE_FLATTER", "MOVE_TEETER_DANCE"},
    "CURSE_GHOST_TRAP": {"MOVE_MEAN_LOOK", "MOVE_BLOCK", "MOVE_SPIDER_WEB"},
    "ENCORE_TAUNT": {"MOVE_ENCORE", "MOVE_TAUNT", "MOVE_TORMENT", "MOVE_DISABLE"},
}
ITEMS = {
    "QUICK_CLAW": {"ITEM_QUICK_CLAW"},
    "BRIGHT_POWDER_LAX": {"ITEM_BRIGHT_POWDER", "ITEM_LAX_INCENSE"},
    "FOCUS_BAND": {"ITEM_FOCUS_BAND"},
    "KINGS_ROCK": {"ITEM_KINGS_ROCK"},
    "SCOPE_LENS": {"ITEM_SCOPE_LENS"},
}
ABILS = {
    "DAMP": {"ABILITY_DAMP"},
    "SOUNDPROOF": {"ABILITY_SOUNDPROOF"},
    "STURDY": {"ABILITY_STURDY"},
    "WONDER_GUARD": {"ABILITY_WONDER_GUARD"},
    "SHADOW_TAG_ARENA_TRAP": {"ABILITY_SHADOW_TAG", "ABILITY_ARENA_TRAP"},
}

def describe(sid):
    s = sets[sid]
    return {
        "set_id": sid,
        "species": pretty(s["species"], "SPECIES_"),
        "item": pretty(held[s["item"]], "ITEM_"),
        "moves": [x.replace("MOVE_", "").replace("_", " ").title() for x in s["moves"]],
        "abilities": [pretty(a, "ABILITY_") for a in sp.get(s["species"], {}).get("abilities", ()) if a != "ABILITY_NONE"],
        "lv50": sid <= HIGH_TIER,
        "n_lategame_trainers": len(set_users.get(sid, [])),
    }

# レポートはオープンレベル基準（定常プール546セット全体）。各エントリのlv50フラグで判別可能
POOL = lategame_sets_all
report = {"pool_size_battle50plus_total": len(lategame_sets_all),
          "pool_size_battle50plus_lv50": len(lategame_lv50),
          "report_pool": "open_level_546",
          "open_only_sets_in_pool": sorted(s for s in lategame_sets_all if s > HIGH_TIER)}
for label, mv in MOVES.items():
    report["move_" + label] = [describe(s) for s in sets_with_move(mv, POOL)]
for label, it in ITEMS.items():
    report["item_" + label] = [describe(s) for s in sets_with_item(it, POOL)]
for label, ab in ABILS.items():
    report["abil_" + label] = [describe(s) for s in sets_with_ability(ab, POOL)]
report["type_GHOST"] = [describe(s) for s in sets_with_type("TYPE_GHOST", POOL)]
report["open_only_described"] = [describe(s) for s in sorted(lategame_sets_all) if s > HIGH_TIER]

with open(f"{OUT}/../..//battle-tower/data/danger_report.json", "w") as f:
    json.dump(report, f, indent=1, ensure_ascii=False)

# ---------- trainer class summary (battles 50+) ----------
cls = defaultdict(lambda: dict(ids=[], sets=set()))
for tid in range(200, 300):
    c = trainers[tid]["fclass"].replace("FACILITY_CLASS_", "")
    cls[c]["ids"].append(tid)
    cls[c]["sets"] |= set(trainer_monsets[trainers[tid]["monset"]])  # オープンレベル基準（全セット）
DNITE_TTAR = set(range(850, 870))
BIRDS_DOGS_MAX = set(range(870, 882))
with open(f"{OUT}/trainer_classes_battle50plus.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["facility_class", "trainer_ids", "iv_range", "open_pool_size",
                "has_OHKO", "has_sleep", "has_explosion", "has_ghost", "has_damp_species",
                "has_counter", "has_quick_claw", "has_dnite_or_ttar", "has_birds_dogs_max"])
    for c in sorted(cls):
        ids = cls[c]["ids"]; pool = cls[c]["sets"]
        ivr = "/".join(sorted({str(fixed_iv(t)) for t in ids}, key=int))
        w.writerow([c, ",".join(map(str, ids)), ivr, len(pool),
                    int(bool(sets_with_move(MOVES["OHKO"], pool))),
                    int(bool(sets_with_move(MOVES["SLEEP"], pool))),
                    int(bool(sets_with_move(MOVES["EXPLOSION"], pool))),
                    int(bool(sets_with_type("TYPE_GHOST", pool))),
                    int(bool(sets_with_ability(ABILS["DAMP"], pool))),
                    int(bool(sets_with_move(MOVES["COUNTER"], pool))),
                    int(bool(sets_with_item(ITEMS["QUICK_CLAW"], pool))),
                    int(bool(pool & DNITE_TTAR)),
                    int(bool(pool & BIRDS_DOGS_MAX))])

print("pool battle50+ total sets:", len(lategame_sets_all))
print("pool battle50+ Lv50 sets:", len(lategame_lv50))
print("open-only sets in pool:", report["open_only_sets_in_pool"])
for k in list(MOVES) + ["type_GHOST"]:
    key = ("move_" + k) if k in MOVES else k
    print(f"{key}: {len(report[key])} sets ->", [d['species'] + '#' + str(d['set_id']) for d in report[key]][:20])
for k in ITEMS:
    print(f"item_{k}: {len(report['item_'+k])}")
for k in ABILS:
    print(f"abil_{k}:", [d['species'] + '#' + str(d['set_id']) for d in report['abil_' + k]])
