# tools/rng-oracle/ — 乱数オラクル（保留）

観測（トレーナー名・先発2体など）から敵生成の乱数を同定する試み。棚上げで、走行では使っていない。
説明と残作業は [21章](../../docs/shelved/21-rng-oracle.md)。

- `towergen.py`：タワーの敵生成を、乱数の消費単位まで再現する
- `identify.py`：観測から乱数の状態を同定する
- `extract_trainers.py`：`../engine/pokeemerald/` から `frontier_trainers.json`（トレーナーID→名前・クラス・使う型）を作る
