# results/ — 実測とマラソンの結果置き場

シミュレータの走行結果と、当時の運用記録を置く。**新しい研究成果はここには入らない**（数値は章と
`tools/engine/` の再実行で出す）。シミュレータのマラソンは 2026-09-05 に終了しており、ここにあるのは
その時点までの記録。

## remote_audit_results.jsonl

v3 期に `tools/sim/remote_run.py` が複数の作業係セッションから集積した監査結果。運用は終了している。

## marathon-ckpt/ — 100万戦マラソンのチェックポイント

`<接頭辞>_ckpt_<累計戦数>_<開始オフセット>.json` の形式。接頭辞は走らせた構成を表す。

| 接頭辞 | 構成 | 状態 |
|---|---|---|
| `v3m` | Z軸 v3.1 | 完走 |
| `v4m` | Z軸 v4（公式 0.2516%） | 完走（16チャンク） |
| `v5m` | v5 系 | 完走（16チャンク） |
| `pivotm` | ピボット案 | 完走（16チャンク） |
| `bfm` | BOOM_FIX | 完走（16チャンク） |
| `ffm` | FIRE_FIX | 完走（16チャンク） |
| `hrm` | HP_ROCK | **25M ぶんのみ**（4チャンク。それ以上は走らせていない） |
| `hdm` | HP_DARK | **存在しない**（走らせる前にマラソンを終了した。欠落ではない） |

`milestones_*.jsonl` は各系列の到達記録（1000連勝の達成点など）。`milestones_v3m.jsonl` は
2026-09-11 の再編で `milestones.jsonl` から改名したもの（他の系列と接頭辞を揃えるため）。
当時のコードは `milestones.jsonl` に書いていたので、`docs/history/10-z-axis.md` の本文はその名前のまま。

集計は `tools/sim/aggregate_*.py`（このディレクトリを cwd にして読む）。例：

```bash
cd battle-tower/tools/sim && python3 aggregate_v4.py | head -3
# → チャンク 16/16 … W25000000: 250000/250000戦 負け594 ✓完走
```

**注意**：`*marathon.py` と `shepherd_*.sh` は自分のディレクトリ（`tools/sim/`）に ckpt を書く。
マラソンを再開した場合、完走後にここへ移すこと。

## archive/

- `sim-era/` … 旧 `data/` に置いていたシミュ期の派生物5点（しきい値マップ、負けlift、ショーリール等）
- `worker-ops/` … 当時の作業係セッション向け指示書と生存ログ。**原文のまま**保存しており、
  本文中のパス表記は再編前（`tools/remote-audit/`）のまま。現在の配置との対応は
  [`../tools/README.md`](../tools/README.md) の対応表を見ること
