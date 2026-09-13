# tools/ — スクリプトの置き場

役割ごとに分けてある。**現行の数値を出すのは `engine/` と `xd/` の2つだけ**で、`sim/` は
2026-09-05 に終了したマラソンの資産、`advisor/` は実機プレイ中の補助、`publish/` は公開エクスポート。

| ディレクトリ | 役割 | cwd | 現役か |
|---|---|---|---|
| `engine/` | 全数計算エンジン（`calc_matchups.py`・`evlib.py`）と pokeemerald 抜粋。ほぼ全ての数値の出どころ | `tools/engine` | ✅ |
| `xd/` | XD産フリーザーの来歴検証（`xd_articuno_verify.py`・42項目） | `tools/xd` | ✅ |
| `sim/` | シミュレータ・集計・文書検証。`legacy/` は v0期のスナップショット | `tools/sim` | 記録 |
| `advisor/` | アドバイザー（Lambda／Docker／ブラウザコンソール） | `tools/advisor` | 任意 |
| `publish/` | 公開リポジトリへのエクスポート（`make_public_export.sh`） | リポジトリ直下 | ✅ |
| `smogon/` | Smogon調査のプロンプトと回答原文、スレッド取り込み | — | 記録 |
| `rng-oracle/` | 観測から敵生成シードを同定する試み（実機キャリブレーション待ち） | `tools/rng-oracle` | 保留 |

## 実行例

```bash
cd battle-tower/tools/xd     && python3 xd_articuno_verify.py    # → 42/42 checks passed
cd battle-tower/tools/engine && python3 calc_matchups.py         # → matchups/report.json
cd battle-tower/tools/engine && python3 pivot_articuno.py        # → 後出し枠245セットの判定
```

`evlib.py` は `make()` `incoming()` `outgoing()` `ko_fixed_list()` `risk_n_list()` を公開していて、
その場の疑問を全数で確かめるのに使う（冒頭の docstring 参照）。

## 依存の向き

```
engine/calc_matchups.py   ←  engine/evlib.py           ←  engine/pivot_articuno.py ほか監査系
        ↑                                                         
        └─ sim/sim.py（__file__ を差し替えて engine 側を exec）
                ↑
                └─ sim/sim_teams.py → sim_z4 → sim_z11 → sim_zsearch → sim_*marathon.py
                                                                 ↑
                          advisor/{advisor,advisor_web,lambda_handler}.py・sim/verify_docs.py・sim/remote_run.py
```

- `engine/calc_matchups.py` は自分のディレクトリの `pokeemerald/` と `../../data` を読む。
- `sim/sim.py` はそれを `exec` する際に `__file__` を一時的に差し替えるので、`pokeemerald/` と
  `data/` は engine 側に解決する。**`tools/engine/` を別名にすると `sim.py`・`advisor` 3本・
  `rng-oracle` 2本が同時に壊れる。**
- `xd/xd_articuno_verify.py` は完全に自己完結（依存ゼロ）。

## 環境変数

| 変数 | 用途 |
|---|---|
| `PYTHONHASHSEED=0` | 出力行順の固定。比較検証では必ず付ける（付けないと `durability_audit.py` 等が揺れる） |
| `FIDELITY2=1` | シミュの忠実度モード。`verify_docs.py`・`remote_run.py`・マラソン系で使う |
| `BT_DATA` | `data/` の場所を上書き（既定はリポジトリ相対） |

## 旧 → 新パス対応表（2026-09-11 再編）

再編前は `tools/remote-audit/` に全部入っていた。当時の文書（`results/archive/worker-ops/` や
`docs/history/` の各章）はそのままの表記なので、読み替えにはこの表を使う。

| 再編前 | 再編後 |
|---|---|
| `tools/remote-audit/calc_matchups.py`・`evlib.py`・`jpnames.py`・`pokeemerald/` | `tools/engine/` |
| `tools/remote-audit/pivot_articuno.py`・`attack_cover.py`・`durability_audit.py`・`crosscheck_tables.py`・`parse_frontier.py` ほか監査系 | `tools/engine/` |
| `tools/remote-audit/xd_articuno_verify.py` | `tools/xd/` |
| `tools/remote-audit/sim_*.py`・`aggregate_*.py`・`shepherd_*.sh`・`verify_docs.py`・`remote_run.py` | `tools/sim/` |
| `tools/remote-audit/*_ckpt_*.json`・`milestones_*.jsonl` | `results/marathon-ckpt/` |
| `tools/remote-audit/advisor*.py`・`lambda_handler.py`・`make_lambda_zip.sh` | `tools/advisor/` |
| `Dockerfile.advisor`・`playbook-console.html`（ルート直下） | `tools/advisor/` |
| `tools/make_public_export.sh` | `tools/publish/` |
| `tools/sim*.py`・`learned_*.json`・`calc_matchups.py`（ルート直下の v0期） | `tools/sim/legacy/` |
| `tools/remote-audit/*_SQUAD_ORDERS.md`・`worker_*_alive.txt`・`README.md` | `results/archive/worker-ops/` |
| 章 `NN-*.md`（ルート直下） | `docs/{current,base,history,shelved,infra}/` |

移動は全件 `git mv` なので `git log --follow <新パス>` で再編前まで遡れる。ディレクトリ単位の履歴
（`git log -- tools/remote-audit`）は再編時点で止まるので、この表で読み替えること。

## 注意

- `engine/pokeemerald/` の `egg_groups.h`・`gen_3.h`・`species_base_stats.h`・`species_info_c.c`・
  `test_species_info.h` は**同一内容のスタブ**（実データは `species_info.h` ほかにある）。
- `sim/sim_teams.py` と `sim/legacy/sim_teams.py` は**同一内容**。再編時に rename 検出が交差しないよう、
  legacy 側だけ先に別コミットで動かしてある。
