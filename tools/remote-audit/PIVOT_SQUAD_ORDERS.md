# 関所3 PIVOT_ON マラソン — 班（squad）作戦指令

> ## ✅✅ 2026-07-21 再起動OK — 忠実モデル確定 ✅✅
> `foe_switch_target` は忠実度ワークフロー(22エージェント)の確定差分を全反映した**最終版**です（コミット c5a48b8）。
> モデル= 敵AI ShouldSwitch のうち当構築のダブルで関与する **#3 AbsorbMove(Volt Absorb) + gate517 + gate519 + #5/#6** を
> AI_TypeCalc準拠(powerガード無し・net判定・吸収特性は#3のみ)で忠実移植。
> 検証済: OFF byte一致(全shard)・ON無クラッシュ(4000戦)・#3/#5/#6発火・#3ユニットテスト4/4。
>
> **各班の起動手順（自分のBASE=下表）:**
> ```bash
> cd battle-tower/tools/remote-audit
> git pull --rebase origin claude/battle-tower-1000-wins-8xr0ze   # sim.py最終版 c5a48b8 を取得
> chmod +x shepherd_pivot.sh
> rm -f pivotm_ckpt_*.json          # 念のため旧ckpt掃除(あれば)
> nohup ./shepherd_pivot.sh 26000000 > shepherd_pivot_run.log 2>&1 &   # 班A=26M / 班B=27M / 班C=28M
> ```
> 本体(協調ボックス)は 25M を起動済み。~30分〜完走ごとに `git add pivotm_ckpt_*.json && git pull --rebase && git commit && git push`。



**目的**: 敵AIの「不利対面ピボット交代(#5/#6)」を有効化（`PIVOT_AI=1`）したv4チームで
同一100万シードを回し、既存の PIVOT_OFF ベースライン（`v4m_ckpt_*.json` 合計2516負け）と
**同一シードのペア比較**で net Δ を測る。Δ<0.02pp なら公式0.2516%は「ピボット未実装バイアスに対して保守的＝床」と認定できる。

## 班とブロックの割り当て（各ボックス＝4コア→4チャンク×62,500＝25万戦）

| ボックス | BASE（ブロック） | シード範囲 |
|---|---|---|
| **協調ボックス（本体）** | `25000000` | [25,000,000 , 25,250,000) |
| 班A | `26000000` | [26,000,000 , 26,250,000) |
| 班B | `27000000` | [27,000,000 , 27,250,000) |
| 班C | `28000000` | [28,000,000 , 28,250,000) |
| 班D | 予備（最遅ブロックの増援 or 落ちたボックスの引き継ぎ） | — |

- 協調ボックス（本体）が 25M を自走するので、**必要な班は A/B/C の3つだけ**（班Dは保険）。
- ベースライン v4m と完全に同じ4ブロック・同じシードなので、ペアは厳密に一致する。
- 協調ボックスは集約（`aggregate_pivot.py`）も担当。

## 各班の実行手順（自分の BASE を上表から選ぶ）

```bash
cd battle-tower/tools/remote-audit
git pull --rebase origin claude/battle-tower-1000-wins-8xr0ze
chmod +x shepherd_pivot.sh

# 例: 班A なら BASE=25000000。自分の割り当てに置き換える。
nohup ./shepherd_pivot.sh 25000000 > shepherd_pivot_run.log 2>&1 &

# 進捗確認（数分後）:
tail -f marathon_pivot_W25000000_0.log        # 1チャンクのログ。負け率/連勝中/戦数/分が出る
ls -la pivotm_ckpt_25000000_*.json            # 4チャンク分のckptができる

# ckptは ~1000戦ごとに自動保存。定期的に（30分〜1時間ごと、または完走時に）push:
git add pivotm_ckpt_${BASE}_*.json
git pull --rebase origin claude/battle-tower-1000-wins-8xr0ze
git commit -m "pivot-marathon-ckpt: 班X ブロック${BASE} 中間/完走"
git push origin claude/battle-tower-1000-wins-8xr0ze
```

## 重要な注意

- **必ず `PYTHONHASHSEED=0 FIDELITY2=1`**（shepherd_pivot.sh が各ワーカーに設定済み。手動起動時は付ける）。
- **ckptファイル（`pivotm_ckpt_*.json`）は追跡・コミット対象**。ログ（`marathon_pivot_*.log` 等）は .gitignore 済みでコミット不要。
- 1ワーカー ≈ 71戦/分。1チャンク62,500戦 ≈ 14〜15時間（4コアで4チャンク並列なのでブロック全体も同じ壁時計）。
- push衝突を避けるため、**push前に必ず `git pull --rebase`**。各班のckptはファイル名が班ごとに違う（BASE違い）ので内容衝突はしない。
- 完走判定: `pivotm_ckpt_${BASE}_${START}.json` の `i` が 62500 に達したら、その START チャンク完了。4つ揃えばブロック完走。
- 協調ボックス側で全16チャンク（4班×4）が揃い次第、ベースライン2516とペア集約して net Δ・マクネマー検定を出す。

## 完了報告

各班は自分のブロックの4チャンクが `i==62500` に達したら、ckptをpushして「班X 完走」と一言。
```
