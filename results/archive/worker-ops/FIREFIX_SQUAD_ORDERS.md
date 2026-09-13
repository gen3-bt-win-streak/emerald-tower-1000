# 炎条項レバー（FIRE_FIX）A/B マラソン — 班（squad）作戦指令

> 注記（2026-09-13 再編）：本文の `tools/remote-audit/` は現在 `tools/sim/`（シミュ）・`tools/engine/`（エンジン）に分割、ckpt は `results/marathon-ckpt/`。原文は当時のまま。


**目的**: 単炎条項Cに足した2レバーの勝率効果を、関所3・BOOM_FIXと同じ**同一100万シードのペア比較**で測る。
- **レバー①**: T2、麻痺炎を**メタグロスの地震で確定KOできるなら爆発でなく地震**（メタグロス温存）。
- **レバー②**: T1、**飛行炎（地震無効）はサンダー10万で確定KOできるならT1で処理**（麻痺不要・メタ温存）。

OFF側＝既存ベースライン（`v4m_ckpt_*.json` 合計2516敗）を再利用し、**ON側（`ffm_ckpt_*.json`）だけ**を回す（計算量半分）。

- ON側エンジン: `sim_firefixmarathon.py`（sim_v4marathon のコピー＋`os.environ["FIRE_FIX"]=1`＋ckpt名 `ffm_`）。
- OFFは env-gated 追加のみで**byte一致**（既存v4m=FIRE_FIX0相当）なので再走不要。
- ペア集約・裁定: `aggregate_firefix.py`（net<0=負けが減る=改善 / net≈0=床の下 / net>0=改悪）。

## 班とブロック（各ボックス=4コア→4チャンク×62,500＝25万戦）
| ボックス | BASE | シード範囲 |
|---|---|---|
| 班A | `25000000` | [25,000,000 , 25,250,000) |
| 班B | `26000000` | [26,000,000 , 26,250,000) |
| 班C | `27000000` | [27,000,000 , 27,250,000) |
| 班D | `28000000` | [28,000,000 , 28,250,000) |
| 協調ボックス（本体） | 集約専任（走らせない） | — |

## 各班の実行手順（自分のBASEに置換）
```bash
cd battle-tower/tools/remote-audit
git pull --rebase origin claude/battle-tower-1000-wins-8xr0ze   # FIRE_FIX版 sim_v4marathon + ラッパを取得
chmod +x shepherd_firefix.sh
nohup ./shepherd_firefix.sh 25000000 > shepherd_firefix_run.log 2>&1 &   # 班A=25M/班B=26M/班C=27M/班D=28M
```
- **必ず `PYTHONHASHSEED=0 FIDELITY2=1`**（shepherdが各ワーカーに設定済み）。
- ckpt（`ffm_ckpt_*.json`）は追跡・コミット対象。ログは.gitignore済み。
- ~30分〜完走ごとに耐久化: `git add ffm_ckpt_*.json && git pull --rebase --autostash && git commit -m "ffm-ckpt" && git push`。
- 1ワーカー≈70戦/分。1チャンク62500戦≈14〜15時間（4コア並列でブロック全体も同壁時計）。

## 集約
協調ボックスで `python3 aggregate_firefix.py`。全16チャンク（4班×4）が揃えば net Δ・マクネマー検定・裁定を出す。
- **裁定**: net<0 かつ McNemar p<0.05 →「改善を確認」→ アドバイザーに FIRE_FIX 採用（BOOM_FIX と併用）。
- net≈0（誤差圏）→「床の下」→ 据え置き。 net>0（有意に悪化）→ 破棄。
