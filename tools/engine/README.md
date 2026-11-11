# tools/engine/ — 全数計算エンジン

v6 の数値はここから出す。pokeemerald のダメージ計算を移植し、50戦目以降の546型と総当たりする。

- 本体：`calc_matchups.py`（ダメージ計算）・`evlib.py`（その場の疑問を全数で確かめる道具）・`jpnames.py`（日本語名）
- そのほかの `.py`：一回きりの監査スクリプト。多くは v4・v5 期のもの（`pivot_articuno*.py` は v5）。`parse_frontier.py` は再実行できない記録
- `pokeemerald/`：pokeemerald 原文の抜粋。計算はここを読む
- 本体と `pokeemerald/` は `sim/`・`advisor/`・`rng-oracle/` からも読まれる。気軽に書き換えない

実行のしかたと依存の向きは [`../README.md`](../README.md)。
