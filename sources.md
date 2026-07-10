# 出典・今後のデータ採掘先

> 注意：この作業環境からは一部サイトへの直接アクセスが制限されていたため、検索経由で確認した。
> 【要検証】タグの解消には下記の一次資料を直接参照すること。

## 今回の裏取りで使用した情報源

### ルール・仕様
- Bulbapedia「Battle Tower (Generation III)」 https://bulbapedia.bulbagarden.net/wiki/Battle_Tower_(Generation_III)
  - ダブルは4匹編成、オープンレベル、禁止ポケモン10種
- Serebii「Pokémon Emerald - Battle Tower」 https://www.serebii.net/emerald/tower.shtml
- アイテムクローズ・禁止リスト（GameFAQs/Serebii フォーラム複数ソース一致）

### 敵トレーナー・セットデータ（Phase 1/2 の本命データ源）
- altissimo1 のトレーナー表 https://altissimo1.github.io/Main-Series/RSE/battle-tower-trainers.html
  - トレーナー番号→出現戦数帯、個体値スケーリング（3/6/9/12/15/21/31）
- Bulbapedia「List of Battle Frontier Pokémon in Generation III」 https://bulbapedia.bulbagarden.net/wiki/List_of_Battle_Frontier_Pok%C3%A9mon_in_Generation_III
  - 敵全セット（種族・技・持ち物・努力値）
- Bulbapedia「List of Battle Frontier Trainers in Generation III」 https://bulbapedia.bulbagarden.net/wiki/List_of_Battle_Frontier_Trainers_in_Generation_III
- Buried Relic「Emerald Battle Frontier Sets」 https://buriedrelic.neocities.org/pages/emerald_battle_frontier_sets
- pokeemerald 逆コンパイル（一次資料）
  - `src/data/battle_frontier/battle_frontier_trainer_mons.h`（全セット）
  - `src/data/battle_frontier/battle_frontier_trainers.h`（トレーナー→セット範囲）
  - `data/battle_ai_scripts.s`（AI行動スコアリング）
  - `src/battle_tower.c`（タワーの抽選ロジック）

### 記録・戦略（先行研究）
- Smogon「Gen III Battle Frontier Discussion and Records」 https://www.smogon.com/forums/threads/gen-iii-battle-frontier-discussion-and-records.3648697/
  - **ダブル既知最高：799連勝（Lv100・エミュ）**
  - シングル：1090連勝、2500連勝超（IRIDESCENCE）
  - ほろびのうたゲンガー（ほろび/みちづれ/まもる/くろいまなざし）で1036連勝の記録
  - **AIはほろびのうたを受けたときのみ交代（カウント1で交代）**という仕様報告
- Smogon「Dans Macabre」（タワーシングル記録チーム） https://www.smogon.com/forums/threads/dans-macabre-a-record-breaking-gen-3-battle-tower-singles-team.3651964/
- Smogon「IRIDESCENCE: Emerald Battle Tower 2500+ wins」 https://www.smogon.com/forums/threads/iridescence-emerald-battle-tower-2500-wins-team.3674437/
- Smogon「frontier & tower information pile」 https://www.smogon.com/forums/threads/frontier-tower-information-pile.60119/

### 育成・習得情報
- ほろびのうた遺伝：♂ムウマ×♀ゴース系（PokémonDB/Serebii 一致） https://pokemondb.net/pokedex/gengar/moves/3
- ムウマ Lv46 ほろびのうた習得（第3世代） https://pokemondb.net/pokedex/misdreavus/moves/3
- エメラルド教え技（だいばくはつ＝キナギタウン・1回限り） https://www.serebii.net/emerald/movetutor.shtml
- メタグロス第3世代学習セット https://bulbapedia.bulbagarden.net/wiki/Metagross_(Pok%C3%A9mon)/Generation_III_learnset

### AI解析
- Bulbapedia「Battle Frontier (Generation III)」（ダブルのターゲット選択：技×対象のスコアリング）
- PokéCommunity「Research: Emerald's Battle Frontier」 https://www.pokecommunity.com/threads/emeralds-battle-frontier.289974/

## 未解決の【要検証】一覧（次回作業キュー）

| # | 項目 | 当たる資料 |
|---|---|---|
| 1 | 中間セットの個体値（15/21のゆれ） | altissimo1 表 or pokeemerald |
| 2 | 敵の二特性個体の特性決定方法（しめりけ率） | pokeemerald `battle_tower.c` |
| 3 | 一撃技持ちの全セット洗い出し（クイッククロー併用の有無） | 敵セット一覧 |
| 4 | 敵のほろびのうた/じばく/だいばくはつ所持セット一覧 | 敵セット一覧 |
| 5 | ぼうおん持ちの出現セット | 敵セット一覧 |
| 6 | トリック持ちの有無（いなければ負け筋から削除） | 敵セット一覧 |
| 7 | AIのまもる使用条件 | `battle_ai_scripts.s`＋実機 |
| 8 | クイッククロー発動率（第3世代） | データ解析 |
| 9 | 徘徊ラティオスへのシンクロ有効性（エメラルド） | 検証記事 |
| 10 | トレーナータイプ→セット番号帯の対応表 | `battle_frontier_trainers.h` |
| 11 | シャドーボールTM30の入手場所・個数（エメラルド） | 攻略サイト |
| 12 | みちづれ状態の敵を爆発で倒した際の判定 | 実機 |
