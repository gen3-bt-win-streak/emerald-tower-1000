# Emerald Battle Tower (Doubles, Open Level) — 1000-win-streak project

Public repository: https://github.com/gen3-bt-win-streak/emerald-tower-1000

A research repository for a 1000-win streak in the **Pokémon Emerald Battle Tower, Doubles, Open Level (Lv100)**.
Everything here is derived from primary sources: the `pret/pokeemerald` decompilation (battle engine, AI scripts,
Battle Frontier trainer and set data), full-population damage calculation over all 546 enemy sets that can appear
after win 50, and a battle simulator that replays the AI. The documents are written in Japanese; this file is the
English entry point and reproduction guide.

Current world record for this category is 1316 wins (Jheisinho, emulator, Smogon Gen III Battle Frontier leaderboard).

## Team (v5, September 2026)

| | Metagross | Latios | Articuno | Snorlax |
|---|---|---|---|---|
| Item | Choice Band | Bright Powder | Leftovers | Chesto Berry |
| Nature / EVs | Adamant, 252 HP / 252 Atk / 4 Spe | Timid, 40 HP / 252 SpA / 216 Spe | Calm, 236 HP / 208 Def / 60 SpD / 4 Spe | Adamant, 76 HP / 182 Atk / 252 Def |
| Moves | Meteor Mash / Earthquake / Explosion / Shadow Ball | Psychic / Ice Beam / Thunderbolt / Protect | Mind Reader / Sheer Cold / Protect / Haze | Body Slam / Curse / Rest / Earthquake |
| Origin | Egg (Emerald) | Southern Island, Method 1 | **Pokémon XD Shadow Articuno** (Haze is a purify move), Calm 31/0/31/29/31/31, PID `2F3C902C`, XDRNG origin seed `ECFE3E26` | Egg (Emerald) |

Lead: Metagross + Latios. Back: Articuno (switch-in for everything Latios cannot take; both leads are immune to
Earthquake) and Snorlax (last Pokémon, Curse win condition). Metagross's Explosion is the answer to the "no other
sure KO" sets (OHKO-move users, Focus Band Blissey), with Articuno's Protect covering the partner slot.

## What is in here

Chapters live in `docs/current`, `docs/base`, `docs/history`, `docs/shelved` and `docs/infra`.
Chapter numbers are stable IDs and never change when a chapter moves.

| File | Content |
|---|---|
| `README.md` | Japanese overview and chapter index |
| `docs/base/00`–`03`, `20` | Rules of the facility, dangerous Pokémon / moves (full population), AI behaviour from `battle_ai_scripts.s`, Explosion digest |
| `docs/current/25-v5-articuno-build.md` | The current team: full-population screening, EV optimisation, the Articuno build |
| `docs/current/12-playbook.md` | The play rules actually used at the console, with every loss so far analysed and turned into a clause |
| `docs/current/16-pkhex-setup.md` | How each Pokémon was prepared: PokeFinder frame search first, then PKHeX |
| `docs/current/17`, `27` | Smogon leaderboard rules (verbatim), eligibility of genned Pokémon, submission plan |
| `docs/current/18-verification-ledger.md` | Dated log of every claim that was checked against source, and every correction |
| `docs/current/26-articuno-provenance.md` | Provenance dossier for the XD Articuno: XDRNG derivation, lock chain, exhaustive proof that Calm 31/0/31/31/31/31 is impossible, acquisition route, shiny impossibility |
| `docs/history/04`–`06`, `08`–`10`, `15`, `24` | Team design history (v1 → v4), simulator results (1M-battle marathons, loss seeds) |
| `docs/shelved/11`, `19`, `21`–`23` | Axes that were measured and dropped or parked |
| `data/` | 882 Battle Frontier sets (546 in the 50+ pool), 300 trainers, danger reports (CSV/JSON) |
| `tools/engine/` | Damage engine (`calc_matchups.py`, `evlib.py`) and the pokeemerald excerpts it reads |
| `tools/xd/` | XD Articuno provenance verifier |
| `tools/sim/` | Simulators and verification scripts (`legacy/` = v0-era snapshots, not runnable) |
| `tools/README.md` | What each tools directory is for, which way the dependencies point, and an old → new path table |

## Reproduce the key results

```bash
git clone https://github.com/gen3-bt-win-streak/emerald-tower-1000.git
cd emerald-tower-1000/tools/xd

# XD Articuno provenance: XDRNG constants, PokeFinder test vectors (11 vectors, 110 states),
# forward derivation of PID 2F3C902C from seed ECFE3E26, PKHeX reverse-search port, lock chain,
# exhaustive direct-path enumeration. Exit code 0 == all 42 checks pass. Runs in about a second.
python3 xd_articuno_verify.py

cd ../engine

# Full-population damage tables for the team (writes matchups/report.json)
python3 calc_matchups.py

# Articuno as Latios's switch-in: which of the 245 relevant sets it survives, and what each 4th move buys
python3 pivot_articuno.py
```

The scripts are plain Python 3, no third-party packages. `tools/engine/evlib.py` exposes `make()`, `incoming()`, `outgoing()`,
`ko_fixed_list()` and `risk_n_list()` for ad-hoc questions; see the docstring at the top of the file.

Definitions used throughout: an enemy is a **guaranteed KO** if the *minimum* damage roll kills it; a set is in
the **OHKO-risk range** if its *maximum* roll kills us. Enemy IVs are 31 (Battle Tower after win 50), Lv100.

## Legitimacy of the Pokémon

All four Pokémon were created in PKHeX after first finding, with PokeFinder, a PID / IV / nature combination that
the in-game Gen 3 RNG actually produces (Method 1, egg frames, or XDRNG). PKHeX reports every Pokémon as legal,
and for the Articuno the XDRNG derivation is re-implemented independently in `tools/xd/xd_articuno_verify.py`. This matches
the current Smogon Gen III Battle Frontier rule ("genned Pokemon are allowed as long as they have legally
obtainable stats and moves", leaderboard manager's clarification of May 2026). Chapter 26 documents what this does
and does not prove: the Articuno is reachable by the real XD RNG, but it was not obtained on hardware.

## License

MIT for the code and documents written in this repository (see `LICENSE`). The `tools/engine/pokeemerald` excerpts and the
game-derived data tables are third-party material, reproduced for reference; Pokémon is a trademark of Nintendo /
Creatures Inc. / GAME FREAK inc.
