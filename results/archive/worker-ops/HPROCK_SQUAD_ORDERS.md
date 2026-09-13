# めざ岩レバー（HP_ROCK）A/B マラソン — 班（squad）作戦指令

> 注記（2026-09-11 再編）：本文の `tools/remote-audit/` は現在 `tools/sim/`（シミュ）・`tools/engine/`（エンジン）に分割、ckpt は `results/marathon-ckpt/`。原文は当時のまま。


**目的**: D案採用（2026-07-30ユーザー決定・実機チーム変更済み）の勝率効果を、BOOM_FIX/FIRE_FIXと同じ**同一100万シードのペア比較**で測る。
- **変更内容**: ラグラージ いわなだれ→**めざめるパワー岩70**（物理・命中100・単体・追加効果なし）
- **付随変更**: EV B4→S4（めざ岩個体はS-IV30のためEV4でS156死守）／実在Method-1個体 `E6BA7F73`（31/31/30/31/22/30）の実数値 404/350/**215**/185/**207**/156 へ補正
- **狙い**: ヌケニン実効命中85.5%→95%・対岩弱点の命中安定。**代償**: スプレッド＋怯み30%の喪失・威力75→70・防−2/特防−9

OFF側＝FIRE_FIX完走ベースライン（`ffm_ckpt_*.json` 合計2233敗）を再利用し、**ON側（`hrm_ckpt_*.json`）だけ**を回す（計算量半分）。

- ON側エンジン: `sim_hprockmarathon.py`（sim_v4marathon のコピー＋`FIRE_FIX=1`＋`HP_ROCK=1`＋ckpt名 `hrm_`）。
- 両側FIRE_FIX=1で共通 → **差分はHP_ROCK（技構成＋EV＋実IV）のみ**の単一変数比較。
- ペア集約・裁定: `aggregate_hprock.py`（net<0=改善 / net≈0=床の下 / net>0=改悪）。

## 班とブロック（各ボックス=4コア→4チャンク×62,500＝25万戦）
| ボックス | BASE | シード範囲 | 状態 |
|---|---|---|---|
| 班A | `25000000` | [25,000,000 , 25,250,000) | **本体コンテナで稼働中（2026-07-30起動）** |
| 班B | `26000000` | [26,000,000 , 26,250,000) | 募集中 |
| 班C | `27000000` | [27,000,000 , 27,250,000) | 募集中 |
| 班D | `28000000` | [28,000,000 , 28,250,000) | 募集中 |

## 各班の実行手順（自分のBASEに置換）
```bash
cd battle-tower/tools/remote-audit
git pull --rebase origin claude/battle-tower-1000-wins-8xr0ze   # HP_ROCK版 sim_v4marathon + ラッパを取得
chmod +x shepherd_hprock.sh
nohup ./shepherd_hprock.sh 26000000 > shepherd_hprock_run.log 2>&1 &   # 班B=26M/班C=27M/班D=28M
```
- **必ず `PYTHONHASHSEED=0 FIDELITY2=1`**（shepherdが各ワーカーに設定済み）。
- ckpt（`hrm_ckpt_*.json`）は追跡・コミット対象。ログは.gitignore済み。
- ~30分〜完走ごとに耐久化: `git add hrm_ckpt_*.json milestones_hrm.jsonl && git pull --rebase --autostash && git commit -m "hrm-ckpt" && git push`。
- 1ワーカー≈60〜70戦/分。1チャンク62500戦≈15〜17時間（4コア並列でブロック全体も同壁時計）。

## 集約
協調ボックスで `python3 aggregate_hprock.py`。全16チャンク（4班×4）が揃えば net Δ・マクネマー検定・裁定を出す。
- **裁定基準（非劣性）**: 実機チームは変更済みのため、判定は「戻すべきか」の裁定。
  net≦0 または誤差圏 →「非劣性を確認」→ めざ岩維持（アドバイザーHP_ROCK=1のまま）。
  net>0 が有意（McNemar p<0.05）→「シミュ上は悪化」→ 実機を いわなだれ個体（`960126BD`）へ戻すか、悪化幅とヌケニン保険の価値をユーザーが天秤にかけて最終判断。
