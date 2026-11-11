# tools/ — スクリプトの置き場

役割ごとにフォルダを分けてある。**v6 の数値は `engine/` から出す。**

| フォルダ | 中身 | 状態 |
|---|---|---|
| [`engine/`](engine/README.md) | 全数計算エンジン。v6 の数値はここから出す | 現役 |
| [`setfinder/`](setfinder/README.md) | タワー型サーチ。対戦中に敵の型を絞る | 現役 |
| [`losslog/`](losslog/README.md) | タワー敗戦ログ。負けた試合を記録する | 現役 |
| `publish/` | 公開版を作るスクリプト。非公開で、公開版には入らない | 現役 |
| [`xd/`](xd/xd_articuno_verify.py) | v5 のフリーザーの来歴検証（42項目） | 記録 |
| [`smogon/`](smogon/README.md) | Smogon 調査のメモ | 記録 |
| [`sim/`](sim/README.md) | シミュレータ。マラソンは 2026-09-05 に終了 | 記録 |
| [`advisor/`](advisor/README.md) | v4 構成の補助 UI。v6 でも使わない | 凍結 |
| [`rng-oracle/`](rng-oracle/README.md) | 観測から敵生成の乱数を同定する試み（21章） | 保留 |

<details>
<summary>各フォルダの細かい説明</summary>

| フォルダ | 役割 |
|---|---|
| `engine/` | 全数計算エンジン（`calc_matchups.py`・`evlib.py`）と pokeemerald 抜粋。ほぼ全ての数値の出どころ |
| `setfinder/` | タワー型サーチ（静的HTML）。見えた種族・技・持ち物・特性・素早さから敵の型を4体同時に絞り込む |
| `losslog/` | タワー敗戦ログ（静的HTML）。負けた試合をターンごとに記録し、書き出しを `logs/losses/` に保存する（`ingest.py`） |
| `publish/` | 公開リポジトリへのエクスポート（`make_public_export.sh`）。非公開 |
| `xd/` | XD産フリーザーの来歴検証（`xd_articuno_verify.py`・42項目）。v5 の構成で使った。依存ゼロ |
| `smogon/` | Smogon調査のプロンプトと回答原文、スレッド取り込み |
| `sim/` | シミュレータ・集計・文書検証。`legacy/` は v0期のスナップショット |
| `advisor/` | アドバイザー（Lambda／Docker／ブラウザコンソール）。盤面入力が v4 の4体（サンダー／メタグロス／ラティオス／ラグラージ）のままなので凍結。v6 でも使わない。配備CI `deploy-advisor.yml` は **no-op ではない**。2026-09-13・09-14 の push でも Lambda のコードを更新した（当時は変数 `ENABLE_ADVISOR_DEPLOY` が true。今の値は未確認）。下の「注意」の見張り対象を作業ブランチへ push すると、v4 のアドバイザーが再配備されうる。止めるならリポジトリ変数を外す（走者判断） |
| `rng-oracle/` | 観測から敵生成シードを同定する試み（実機キャリブレーション待ちで棚上げ） |

旧記載（2026-09-14。**誤り**。2026-11-11 に訂正）：「配備CI `deploy-advisor.yml` はリポジトリ変数 `ENABLE_ADVISOR_DEPLOY` が未設定なので既に no-op」。

旧表の cwd 列：engine＝`tools/engine`、xd＝`tools/xd`、sim＝`tools/sim`、setfinder＝`tools/setfinder`、losslog＝`tools/losslog`、advisor＝`tools/advisor`、publish＝リポジトリ直下、smogon＝—、rng-oracle＝`tools/rng-oracle`。

</details>

## 実行例

v6 の4体を `evlib` で作る定義は [`engine/README.md`](engine/README.md) の折りたたみにある。

<details>
<summary>記録（v5／2026-07 の候補）</summary>

`tools/` のある階層（公開版ではリポジトリの一番上）から実行する。

```bash
python3 tools/xd/xd_articuno_verify.py     # → 42/42 checks passed
python3 tools/engine/calc_matchups.py      # → tools/engine/matchups/report.json
python3 tools/engine/pivot_articuno.py     # v5 期の検証 → 後出し枠245セットの判定
```

`calc_matchups.py` の `CANDS` は 2026-07 の初期候補で、v6 ではない。

旧表記（2026-09 時点）：

```bash
cd battle-tower/tools/xd     && python3 xd_articuno_verify.py    # → 42/42 checks passed
cd battle-tower/tools/engine && python3 calc_matchups.py         # → matchups/report.json
cd battle-tower/tools/engine && python3 pivot_articuno.py        # → 後出し枠245セットの判定
```

</details>

`engine/` の監査系の一部（`attack_cover.py`・`durability_audit.py`・`move_audit.py`・`dura_gross_swampert.py`。v4 期の構成で固定）は、
`tools/engine` に入ってから実行する。`publish/` はリポジトリの一番上から。ほかのフォルダは各 README を見る。

`evlib.py` は `make()` `incoming()` `outgoing()` `ko_fixed_list()` `risk_n_list()` を公開していて、
その場の疑問を全数で確かめるのに使う（冒頭の docstring 参照）。

## 依存の向き

`sim/`・`advisor/`・`rng-oracle/` は `engine/` を読む。**`tools/engine/` の名前を変えると、これらが同時に壊れる。**

<details>
<summary>図と細かい説明</summary>

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

</details>

## 環境変数

| 変数 | 用途 |
|---|---|
| `PYTHONHASHSEED=0` | 出力行順の固定。比較検証では必ず付ける（付けないと `durability_audit.py` 等が揺れる） |
| `FIDELITY2=1` | シミュの忠実度モード。`verify_docs.py`・`remote_run.py`・マラソン系で使う |
| `BT_DATA` | `data/` の場所を上書き（既定はリポジトリ相対） |

## 注意

- **見張り対象を変えて push すると、そのまま本番の Lambda に配備されうる**（経緯は上の折りたたみの `advisor/` の行）。
  `advisor/` と、`engine/`・`sim/`・`data/` の一部は、非公開側の配備用ワークフロー（`deploy-advisor.yml`）が
  見張っている。気軽に書き換えない。見張られているのは `engine/` の `calc_matchups.py`・`jpnames.py`・`pokeemerald/`、
  `sim/` の `sim.py`・`sim_teams.py`・`sim_z4.py`・`sim_z11.py`・`sim_zsearch.py`・`sim_v4marathon.py`、
  `data/` の `frontier_sets.csv`・`trainers.csv`。
- `engine/pokeemerald/` の `egg_groups.h`・`gen_3.h`・`species_base_stats.h`・`species_info_c.c`・
  `test_species_info.h` は**同一内容のスタブ**（実データは `species_info.h` ほかにある）。
- `sim/sim_teams.py` と `sim/legacy/sim_teams.py` は**同一内容**。再編時に rename 検出が交差しないよう、
  legacy 側だけ先に別コミットで動かしてある。

## 旧 → 新パス対応表（2026-09-13 再編）

古い文書に書かれたパスを、今の場所に読み替える表。2026-11 の章の移動も含む。

<details>
<summary>対応表を開く</summary>

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

**2026-11-11 の章の移動**（これも `git mv`）

| 移動前 | 移動後 |
|---|---|
| `docs/current/12-playbook.md`・`25-v5-articuno-build.md`・`26-articuno-provenance.md` | `docs/history/` |
| `docs/current/16-pkhex-setup.md`・`17-smogon-legitimacy.md`・`18-verification-ledger.md`・`27-smogon-post.md` | `docs/evidence/`（Smogon 提出の証拠をまとめた新しいフォルダ） |

</details>
