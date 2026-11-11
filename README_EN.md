# Emerald Battle Tower — 1000-win Doubles streak (Open Level)

日本語: [README.md](README.md)

## Current team (v6, in play)

**Metagross / Latios / Politoed / Snorlax**

- Latios and Metagross take down as much of the enemy team as they can.
- Against bad matchups, Snorlax and Politoed take the hits, while Yawn and Perish Song handle set-up sweepers and close out games.
- Politoed's Damp also stops enemy Explosion.

Best v6 streak 391 / personal best 613 (v4 era) / target 1000 (world record 1316)

## Where things are

| Looking for | Go to |
|---|---|
| Sets and EVs | [Team details](#team-details-v6) below |
| Full design, play clauses, losses | [Chapter 28](docs/current/28-perish-build.md) (Japanese) |
| Narrowing down enemy sets during a battle | [Set finder](tools/setfinder/README.md) |
| Logging a lost game | [Loss log](tools/losslog/README.md), [logged games](logs/losses/README.md) |
| Smogon eligibility and legitimacy of the Pokémon | [Legitimacy](#legitimacy-of-the-pokémon) below, chapters [27](docs/evidence/27-smogon-post.md), [17](docs/evidence/17-smogon-legitimacy.md), [16](docs/evidence/16-pkhex-setup.md) |
| History of the project | [TIMELINE.md](TIMELINE.md) (Japanese) |
| All chapters | [docs/README.md](docs/README.md) (Japanese) |
| Reproducing the numbers | [Reproduce the key results](#reproduce-the-key-results) below, [tools/README.md](tools/README.md) |

## Team details (v6)

| | Metagross | Latios | Politoed | Snorlax |
|---|---|---|---|---|
| Item | Choice Band | Leftovers | Lum Berry | Chesto Berry |
| Ability | Clear Body | Levitate | **Damp** | Thick Fat |
| Nature / EVs | Adamant, 208 HP / 252 Atk / 44 SpD / 4 Spe | Timid, 40 HP / 252 SpA / 216 Spe | Calm, 240 HP / 154 Def / 108 SpD / 8 Spe | Adamant, 80 HP / 176 Atk / 248 Def / 4 Spe |
| Moves | Meteor Mash / Earthquake / Explosion / Shadow Ball | Psychic / Ice Beam / Substitute / Protect | Perish Song / Protect / Waterfall / Hypnosis | Yawn / Rest / Double-Edge / Protect |

Damp switches off all 24 enemy Explosion / Self-Destruct sets, which removes the mutual-KO draw (= loss), one of the two main loss modes of the shelved perish team (chapter 19). Perish Song is used in two ways. To flush threats: when a set-up sweeper starts using Double Team or Curse, or when very bulky Pokémon such as Suicune or Articuno are lined up, the AI switches out under the perish count and loses its boosts. And as the finisher: once the opponent is down to its last two Pokémon (no bench left to switch to), the team rides out the three counting turns, adapting to the opponent with Protect, Hypnosis, Yawn and Waterfall.

## About this repository

A research repository for a 1000-win streak in the **Pokémon Emerald Battle Tower, Doubles, Open Level (Lv100)**.
Everything here is derived from primary sources: the `pret/pokeemerald` decompilation (battle engine, AI scripts,
Battle Frontier trainer and set data), full-population damage calculation over all 546 enemy sets that can appear
after win 50, and a battle simulator that replays the AI. The documents are written in Japanese; this file is the
English entry point and reproduction guide.

Current world record for this category is 1316 wins (Jheisinho, emulator, Smogon Gen III Battle Frontier leaderboard).

The previous team, **v5** (September 2026), ran Pokémon XD Shadow Articuno (Mind Reader / Sheer Cold / Protect /
Haze; Calm 31/0/31/29/31/31, PID `2F3C902C`, XDRNG origin seed `ECFE3E26`) in Politoed's slot; it is documented in
chapter 25, with the Articuno provenance dossier in chapter 26.

## In-battle set finder

`tools/setfinder/` is a static HTML page for use on a phone during a battle. Enter what you have seen of each enemy
(species, moves, item, ability, and whether it outsped a given Speed stat) and it narrows the 546 possible sets for
all four enemies at once. Because an enemy team never repeats a species or an item, it also cross-checks the four
slots and drops sets whose item would clash. The data is embedded in the page: no server, no network requests,
no tracking. Rebuild with `PYTHONHASHSEED=0 python3 build_setfinder.py` in that directory.

## What is in here

Chapters live in `docs/current` (v6), `docs/evidence` (submission evidence), `docs/base`, `docs/history`, `docs/shelved` and `docs/infra`.
Chapter numbers are stable IDs and never change when a chapter moves.

| File | Content |
|---|---|
| `README.md` | Japanese entry point |
| `docs/README.md` | Chapter index, design principles, project status (Japanese) |
| `TIMELINE.md` | What was tried, what was dropped, and why the tree looks like this (Japanese) |
| `docs/base/00`–`03`, `20` | Rules of the facility, dangerous Pokémon / moves (full population), AI behaviour from `battle_ai_scripts.s`, Explosion digest |
| `docs/current/28-perish-build.md` | The current team (v6): Damp + Perish Song finisher, Politoed's EVs, how to survive the perish count, play clauses |
| `docs/history/25-v5-articuno-build.md` | The previous team (v5) and the base of v6: full-population screening, EV optimisation, the Articuno build |
| `docs/history/12-playbook.md` | Play rules of the v4/v5 era (frozen). The clauses still used in v6 were carried over to chapter 28 §4 |
| `docs/evidence/16-pkhex-setup.md` | How each Pokémon was prepared: PokeFinder frame search first, then PKHeX |
| `docs/evidence/17`, `27` | Smogon leaderboard rules (verbatim), eligibility of genned Pokémon, submission plan |
| `docs/evidence/18-verification-ledger.md` | Dated log of every claim that was checked against source, and every correction |
| `docs/history/26-articuno-provenance.md` | Provenance dossier for the XD Articuno: XDRNG derivation, lock chain, exhaustive proof that Calm 31/0/31/31/31/31 is impossible, acquisition route, shiny impossibility |
| `docs/history/04`–`06`, `08`–`10`, `15`, `24` | Team design history (v1 → v4), simulator results (1M-battle marathons, loss seeds) |
| `docs/shelved/11`, `19`, `21`–`23` | Axes that were measured and dropped or parked |
| `data/` | 882 Battle Frontier sets (546 in the 50+ pool), 300 trainers, danger reports (CSV/JSON) |
| `tools/engine/` | Damage engine (`calc_matchups.py`, `evlib.py`) and the pokeemerald excerpts it reads |
| `tools/xd/` | XD Articuno provenance verifier |
| `tools/setfinder/` | In-battle set finder (static HTML, see above) |
| `tools/losslog/`, `logs/losses/` | Loss log: a static HTML page to record a lost game turn by turn, and the saved games |
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

# Full-population damage tables for the early (July 2026) candidate sets (writes matchups/report.json)
python3 calc_matchups.py

# Articuno as Latios's switch-in: which of the 245 relevant sets it survives, and what each 4th move buys
python3 pivot_articuno.py   # v5 (Articuno) analysis
```

The v6 numbers in chapter 28 come from `tools/engine/evlib.py` (`make()` / `ko_fixed_list()`) with the sets in the team table.

The scripts are plain Python 3, no third-party packages. `tools/engine/evlib.py` exposes `make()`, `incoming()`, `outgoing()`,
`ko_fixed_list()` and `risk_n_list()` for ad-hoc questions; see the docstring at the top of the file.

Definitions used throughout: an enemy is a **guaranteed KO** if the *minimum* damage roll kills it; a set is in
the **OHKO-risk range** if its *maximum* roll kills us. Enemy IVs are 31 (Battle Tower after win 50), Lv100.

## Legitimacy of the Pokémon

All Pokémon of the v4 and v5 teams were created in PKHeX after first finding, with PokeFinder, a PID / IV / nature combination that
the in-game Gen 3 RNG actually produces (Method 1, egg frames, or XDRNG). PKHeX reports every Pokémon as legal,
and for the Articuno the XDRNG derivation is re-implemented independently in `tools/xd/xd_articuno_verify.py`. This matches
the current Smogon Gen III Battle Frontier rule ("genned Pokemon are allowed as long as they have legally
obtainable stats and moves", leaderboard manager's clarification of May 2026). Chapter 26 documents what this does
and does not prove: the Articuno is reachable by the real XD RNG, but it was not obtained on hardware.
The v6 Politoed is not yet documented in chapter 16.

## License

MIT for the code and documents written in this repository (see `LICENSE`). The `tools/engine/pokeemerald` excerpts and the
game-derived data tables are third-party material, reproduced for reference; Pokémon is a trademark of Nintendo /
Creatures Inc. / GAME FREAK inc.
