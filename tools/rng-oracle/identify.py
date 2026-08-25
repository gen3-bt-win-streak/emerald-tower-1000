# -*- coding: utf-8 -*-
"""観測（トレーナー名・先発2体など）から乱数状態を同定する。

使い方例:
  py identify.py --trainer JAXON --leads Marowak,Hariyama --center 0x12345678 --radius 30000
  py identify.py --leads Marowak,Hariyama --scan 0x0 0x100000   # トレーナー不明・範囲走査

同定対象は「パーティ生成(FillTrainerParty)直前の状態」。--trainer 指定時はその前提で
fill_party のみを照合、未指定時はトレーナー抽選込み(gen_battle)で照合する。
"""
import argparse, json
import towergen as tg

def match_fill(state, trainer_id, obs_species, mons_count=4):
    rng = tg.Rng(state)
    try:
        party, ot = tg.fill_party(rng, trainer_id, mons_count)
    except Exception:
        return None
    sp = [tg.SETS[s]["species"] for s in party]
    if sp[:len(obs_species)] != obs_species:
        return None
    return dict(state=state, trainer_id=trainer_id, party=party, species=sp,
                items=[tg.SETS[s]["item"] for s in party],
                moves={tg.SETS[s]["species"]: tg.SETS[s]["moves"] for s in party},
                ot_id=ot, end_state=rng.state, used=rng.used)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trainer", help="観測したトレーナー名（英名）またはID")
    ap.add_argument("--leads", required=True, help="先発2体（見えた順・カンマ区切り英名）")
    ap.add_argument("--party", help="判明している3体目以降（カンマ区切り）")
    ap.add_argument("--center", help="探索中心状態(hex)")
    ap.add_argument("--radius", type=int, default=30000)
    ap.add_argument("--scan", nargs=2, help="範囲走査 from to (hex)")
    ap.add_argument("--exclude", default="", help="この挑戦で戦済みのトレーナーID(カンマ区切り)")
    a = ap.parse_args()

    obs = a.leads.split(",") + (a.party.split(",") if a.party else [])
    tid = None
    if a.trainer:
        tid = int(a.trainer) if a.trainer.isdigit() else \
              next(t["id"] for t in tg.TRAINERS.values() if t["name"] == a.trainer.upper())
    if a.center:
        c = int(a.center, 16)
        lo, hi = c - a.radius, c + a.radius
    else:
        lo, hi = int(a.scan[0], 16), int(a.scan[1], 16)
    used = tuple(int(x) for x in a.exclude.split(",") if x)

    hits = []
    for st in range(lo, hi + 1):
        st &= 0xFFFFFFFF
        if tid is not None:
            h = match_fill(st, tid, obs)
        else:
            b = tg.gen_battle(st, used_ids=used)
            h = b if b["species"][:len(obs)] == obs else None
            if h: h["state"] = st
        if h:
            hits.append(h)
    print(f"探索 {hi-lo+1} 状態 → 一致 {len(hits)} 件")
    for h in hits[:10]:
        print(json.dumps({k: (hex(v) if k in ("state","end_state") else v)
                          for k, v in h.items() if k != "moves"}, ensure_ascii=False))
        for sp, mv in h.get("moves", {}).items():
            print(f"    {sp}: {'/'.join(mv)}")
    return hits

if __name__ == "__main__":
    main()
