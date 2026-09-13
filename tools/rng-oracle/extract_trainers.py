# -*- coding: utf-8 -*-
"""pokeemerald原文から「トレーナーID→名前/クラス/monSetプール」を抽出して frontier_trainers.json を作る。
入力: ../engine/pokeemerald/ の battle_frontier_trainers.h ほか（pret/pokeemerald master）
"""
import json, re, subprocess, os
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine", "pokeemerald")

# 1) トレーナー定数 → ID
tconst = {}
for m in re.finditer(r"#define\s+(FRONTIER_TRAINER_\w+)\s+(\d+)",
                     open(f"{SRC}/battle_frontier_trainers_constants.h").read()):
    tconst[m.group(1)] = int(m.group(2))

# 2) monSet配列（cppでマクロ展開して数値化）
expanded = subprocess.run(
    ["cpp", "-P"], input=open(f"{SRC}/battle_frontier_mons_constants.h").read()
    + open(f"{SRC}/battle_frontier_trainer_mons.h").read(),
    capture_output=True, text=True).stdout
monsets = {}
for m in re.finditer(r"const u16 (gBattleFrontierTrainerMons_\w+)\[\]\s*=\s*\{([^}]*)\}", expanded):
    vals = [int(x) for x in re.findall(r"-?\d+", m.group(2))]
    assert vals[-1] == -1, m.group(1)
    monsets[m.group(1)] = vals[:-1]

# 3) トレーナー本体（名前・クラス・monSet参照）
trainers = {}
body = open(f"{SRC}/battle_frontier_trainers.h").read()
for m in re.finditer(
        r"\[(FRONTIER_TRAINER_\w+)\]\s*=\s*\{\s*"
        r"\.facilityClass\s*=\s*(\w+),\s*"
        r'\.trainerName\s*=\s*_\("([^"]*)"\)'
        r".*?\.monSet\s*=\s*(\w+)", body, re.S):
    tid = tconst[m.group(1)]
    trainers[tid] = dict(id=tid, const=m.group(1), cls=m.group(2),
                         name=m.group(3), mon_set=monsets[m.group(4)])

assert len(trainers) == 300, len(trainers)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontier_trainers.json")
json.dump([trainers[i] for i in sorted(trainers)], open(out, "w"), ensure_ascii=False)
n2099 = [t for t in trainers.values() if 200 <= t["id"] <= 299]
allsets = sorted({s for t in n2099 for s in t["mon_set"]})
print(f"trainers: {len(trainers)} / ID200-299: {len(n2099)} / union of their pools: {len(allsets)} sets"
      f" (min {allsets[0]} max {allsets[-1]})")
