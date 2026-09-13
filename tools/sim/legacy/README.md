# tools/sim/legacy/ — v0〜v3期のスナップショット（実行不能）

2026-07-10〜15 にリポジトリのルート直下 `tools/` へ置かれていたシミュレータと学習JSON 17本。
**当時から単体では実行できない。** 依存していた `tools/pokeemerald/` と `sim_w2.py` が
リポジトリの履歴に一度も入っていないため。

記録として残しているだけで、内容は1バイトも変更していない。現行のシミュレータは1つ上の
[`../`](../README.md)、現行の数値は [`../../engine/`](../../README.md)。

当時の経緯は次の2章にある。

- [`../../../docs/history/08-simulation.md`](../../../docs/history/08-simulation.md) —
  シミュレータv0の実装、2万戦、100万戦レース、構築トーナメント、情報パリティ化
- [`../../../docs/history/10-z-axis.md`](../../../docs/history/10-z-axis.md) —
  Z軸への移行と探索ボット、sticky不変条件

`sim_teams.py` は1つ上の `../sim_teams.py` と**同一内容**（再編時に rename 検出が交差しないよう、
こちらを先に別コミットで動かしてある）。
