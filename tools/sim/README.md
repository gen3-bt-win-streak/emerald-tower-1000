# tools/sim/ — シミュレータと検証

**マラソンは 2026-09-05 に終了している。**以後の判断は全数計算（`../engine/`）と走者定義の指標で行う
方針に切り替えた（`../../docs/history/24-pick4-audit.md` §10）。ここにあるのは、その時点までの
シミュレータ本体・集計・文書検証と、`legacy/` に退避した v0期のスナップショット。

各ディレクトリの役割と旧パス対応は [`../README.md`](../README.md) を見ること。

## 主なスクリプト

| ファイル | 用途 |
|---|---|
| `sim.py` | `../engine/calc_matchups.py` を exec してダメージ表を取り込む土台 |
| `sim_teams.py` → `sim_z4.py` → `sim_z11.py` → `sim_zsearch.py` | 構築と探索ボットの積み上げ |
| `sim_*marathon.py` | 100万戦マラソン本体（v4／v5／pivot／boomfix／firefix／hprock） |
| `shepherd_*.sh` | マラソンを分割実行して ckpt を書き出す進行役 |
| `aggregate_*.py` | `../../results/marathon-ckpt/` の ckpt を集計する |
| `verify_docs.py` | 章に書かれた数値をエンジンで再計算して突き合わせる（94項目） |
| `remote_run.py` | 忠実度モードの A/B smoke 検証 |

## 走らせ方

```bash
cd battle-tower/tools/sim
PYTHONHASHSEED=0 FIDELITY2=1 python3 verify_docs.py | tail -2
# → 合計 94件: 一致 92 / 不一致 0 / 参考 2

python3 aggregate_v4.py | head -3
# → チャンク 16/16 … 負け594 ✓完走
```

比較検証では `PYTHONHASHSEED=0` を必ず付ける（付けないと出力の行順が揺れる）。

## 注意

- **ckpt の置き場**：`*marathon.py` と `shepherd_*.sh` は**このディレクトリに**ckpt を書く。
  マラソンを再開した場合、完走後に `../../results/marathon-ckpt/` へ移すこと（集計スクリプトは
  そちらを読む）。
- **`verify_docs.py` の部分実行**：節を指定して走らせると `verify_docs_report.json` が
  その節ぶんだけで上書きされる。追跡ファイルなので、commit 前に全件で走らせ直すか
  `git checkout -- verify_docs_report.json` で戻すこと。
- **`.gitignore`**：`verify*.py` が無視対象に入っている。新しく `verify_*.py` を足すときは
  `git add -f` が要る。
- `legacy/` は実行できない（[`legacy/README.md`](legacy/README.md)）。
