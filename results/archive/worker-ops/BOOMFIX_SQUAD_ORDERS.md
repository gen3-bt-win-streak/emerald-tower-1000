# 爆発“まもる税”修正 A/B マラソン — 班（squad）作戦指令

**目的**: 探索の爆発候補採点を「相方まもる込み」にした修正（`BOOM_FIX`）の勝率効果を、
関所3と同じ**同一100万シードのペア比較**で測る。OFF側＝既存ベースライン（`v4m_ckpt_*.json` 合計2516敗）
を再利用し、**ON側（`bfm_ckpt_*.json`）だけ**を回す（計算量半分）。

- ON側エンジン: `sim_boomfixmarathon.py`（sim_v4marathon のコピー＋`os.environ["BOOM_FIX"]=1`＋ckpt名 `bfm_`）。
- OFFは追加ガードのみで**byte一致**（既存v4m=BOOM_FIX0相当）なので再走不要。
- ペア集約・裁定: `aggregate_boomfix.py`（net<0=負けが減る=改善 / net≈0=床の下）。

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
git pull --rebase origin claude/battle-tower-1000-wins-8xr0ze   # 修正版 sim_zsearch(718cc9f)+ラッパを取得
chmod +x shepherd_boomfix.sh
nohup ./shepherd_boomfix.sh 25000000 > shepherd_boomfix_run.log 2>&1 &   # 班A=25M/班B=26M/班C=27M/班D=28M
```
- **必ず `PYTHONHASHSEED=0 FIDELITY2=1`**（shepherdが各ワーカーに設定済み）。
- ckpt（`bfm_ckpt_*.json`）は追跡・コミット対象。ログは.gitignore済み。
- ~30分〜完走ごとに耐久化: `git add bfm_ckpt_*.json && git pull --rebase --autostash && git commit -m "bfm-ckpt" && git push`。
- 1ワーカー≈71戦/分。1チャンク62500戦≈14〜15時間（4コア並列でブロック全体も同壁時計）。

## 集約
協調ボックスで `python3 aggregate_boomfix.py`。全16チャンク（4班×4）が揃えば net Δ・マクネマー検定・裁定を出す。
