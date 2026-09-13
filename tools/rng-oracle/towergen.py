# -*- coding: utf-8 -*-
"""バトルタワー敵生成の消費単位まで正確な再現（pokeemerald battle_tower.c / pokemon.c 移植）。

移植元（pret/pokeemerald master・原文は ../engine/pokeemerald/）:
- LCRNG: gRngValue = gRngValue * 0x41C64E6D + 0x6073; Random() は上位16bit
- Random32() = Random() | (Random() << 16)  ※下位半分が先
- SetNextFacilityOpponent: 周回8以降(連勝49以上)は trainerId = 200 + Random()%100。
  同一挑戦内で戦済みのIDは引き直し（1消費/試行）
- FillTrainerParty: otID=Random32() → 各枠 monId=monSet[Random()%len] を
  種族重複/持ち物重複/同一index で棄却再抽選 → 採用時 性格一致まで PID=Random32() 棄却ループ
- ChooseSpecialBattleTowerTrainer: 記録ミックス無しのセーブでは消費ゼロでFALSE
"""
import csv, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")

MULT, ADD, MASK = 0x41C64E6D, 0x6073, 0xFFFFFFFF
NATURES = ["Hardy","Lonely","Brave","Adamant","Naughty","Bold","Docile","Relaxed","Impish","Lax",
           "Timid","Hasty","Serious","Jolly","Naive","Modest","Mild","Quiet","Bashful","Rash",
           "Calm","Gentle","Sassy","Careful","Quirky"]
NAT_IDX = {n: i for i, n in enumerate(NATURES)}
FRONTIER_MONS_HIGH_TIER = 849

class Rng:
    __slots__ = ("state", "used")
    def __init__(self, state): self.state = state & MASK; self.used = 0
    def rand(self):            # Random(): 上位16bit
        self.state = (self.state * MULT + ADD) & MASK
        self.used += 1
        return self.state >> 16
    def rand32(self):          # Random32(): 下位が先
        lo = self.rand(); hi = self.rand()
        return lo | (hi << 16)
    def skip(self, n):         # 歩留まり消費（フレーム等）
        for _ in range(n): self.rand()

def _load():
    sets = {}
    for r in csv.DictReader(open(f"{DATA}/frontier_sets.csv")):
        item = r["item"] if r["item"] not in ("", "None") else None
        sets[int(r["set_id"])] = dict(set_id=int(r["set_id"]), species=r["species"],
                                      item=item, nature=r["nature"],
                                      moves=[r[f"move{i}"] for i in (1,2,3,4)],
                                      lategame=int(r["lategame_trainer_count"]))
    trainers = {t["id"]: t for t in json.load(open(f"{HERE}/frontier_trainers.json"))}
    return sets, trainers

SETS, TRAINERS = _load()

def pick_trainer(rng, used_ids=()):
    """SetNextFacilityOpponent（周回8以降＝連勝49+の定常域）"""
    while True:
        tid = 200 + rng.rand() % 100
        if tid not in used_ids:
            return tid

def fill_party(rng, trainer_id, mons_count=4, open_level=True):
    """FillTrainerParty。戻り値: (採用set_idリスト, otID)"""
    pool = TRAINERS[trainer_id]["mon_set"]
    n = len(pool)
    ot_id = rng.rand32()
    chosen = []
    while len(chosen) < mons_count:
        mon_id = pool[rng.rand() % n]
        if not open_level and mon_id > FRONTIER_MONS_HIGH_TIER:
            continue
        s = SETS[mon_id]
        if any(SETS[c]["species"] == s["species"] for c in chosen):
            continue
        if s["item"] is not None and any(SETS[c]["item"] == s["item"] for c in chosen):
            continue
        if mon_id in chosen:
            continue
        # CreateMonWithEVSpreadNatureOTID: 性格一致までPID再抽選
        want = NAT_IDX[s["nature"]]
        while rng.rand32() % 25 != want:
            pass
        chosen.append(mon_id)
    return chosen, ot_id

def gen_battle(state, used_ids=(), gap_frames=0, mons_count=4):
    """トレーナー抽選 → (会話等のフレーム消費) → パーティ生成。
    戻り値: dict(trainer_id, name, cls, party[set_id], ot_id, end_state, used)"""
    rng = Rng(state)
    tid = pick_trainer(rng, used_ids)
    rng.skip(gap_frames)
    party, ot = fill_party(rng, tid, mons_count)
    t = TRAINERS[tid]
    return dict(trainer_id=tid, name=t["name"], cls=t["cls"], party=party,
                species=[SETS[s]["species"] for s in party],
                items=[SETS[s]["item"] for s in party],
                ot_id=ot, end_state=rng.state, used=rng.used)

if __name__ == "__main__":
    import sys
    st = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0
    b = gen_battle(st)
    print(json.dumps(b, ensure_ascii=False, indent=2))
