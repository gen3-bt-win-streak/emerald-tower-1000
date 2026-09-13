# data/ — 一次データベース

出典：pokeemerald（エメラルド逆コンパイルプロジェクト）の実データを機械抽出したもの。
抽出スクリプトの再現手順は本ファイル末尾。

## ファイル一覧

### frontier_sets.csv — 敵ポケモン全882セット
バトルフロンティア共通の敵セット定義（`battle_frontier_mons.h` 由来）。

| 列 | 意味 |
|---|---|
| `set_id` | セットID（0-881）。**849以下のみLv50モードに出現**、850-881はオープンレベル専用 |
| `species` / `type1` / `type2` | 種族・タイプ（英語名） |
| `ability1` / `ability2` | 種族が持ちうる特性（どちらになるかは個体の性格値依存） |
| `base_speed` | 種族値の素早さ（行動順の目安） |
| `item` | 持ち物（セット固定） |
| `nature` / `ev_spread` | 性格・努力値振り先フラグ（対象ステに均等振り） |
| `move1`〜`move4` | 技（セット固定） |
| `lv50_allowed` | 1=Lv50モードに出現可能 |
| `in_pool_battle50plus` | 1=**50戦目以降の定常プール**（トレーナーID200-299の誰かが使用） |
| `lategame_trainer_count` | このセットを使う定常トレーナーの人数 |

### trainers.csv — 敵トレーナー全300人
`battle_frontier_trainers.h` 由来。

| 列 | 意味 |
|---|---|
| `trainer_id` | 0-299。**出現戦数帯とIVを決めるのはこのID** |
| `facility_class` | トレーナータイプ（見た目・肩書き）。**チームプレビューがない第3世代での裏読み材料** |
| `fixed_iv` | このトレーナーのポケモンの全ステ個体値（0-99:3 / 100-119:6 / 120-139:9 / 140-159:12 / 160-179:15 / 180-199:18 / 200-219:21 / **220-299:31**） |
| `set_ids` | このトレーナーが使いうるセットID一覧（この中から重複種族・重複持ち物なしでランダム選出） |

### trainer_classes_battle50plus.csv — 定常戦のトレーナータイプ別要注意表（オープン基準）
トレーナーID200-299をタイプ別に集計。「このトレーナータイプは一撃技/催眠/爆発/ゴースト/しめりけ/カウンター/クイッククロー/カイリュー・バンギ/最強準伝を持ちうるか」の早見表。**開幕にトレーナーの見た目から裏2体の危険度を推定する**ためのデータ。

### danger_report.json — 危険カテゴリ別の全該当セット（オープン基準）
50戦目以降の**オープンレベルプール（546セット）**を対象に、一撃技・催眠・爆発・みちづれ・ほろびのうた・トリック・まもる・カウンター・回避・メロメロ・こんらん、危険持ち物（クイッククロー等）、危険特性（しめりけ・ぼうおん・がんじょう・ふしぎなまもり）該当セットを列挙したもの。各エントリの `lv50` フラグでLv50プール該当かも判別可能。

### matchups_report.json — 全対面ダメージ・素早さレポート
`../tools/engine/calc_matchups.py`（pokeemeraldのダメージ計算式を忠実移植・Lv100・敵IV31・最悪特性分岐）による
546セット全対面の計算結果。爆発カバレッジ／各候補の与ダメ確1リスト／被確1リスト（急所込み別）／素早さ関係。
候補の追加・努力値変更はスクリプトの `CANDS` を編集して再実行。

### ../tools/engine/ — 再生成スクリプト
- `calc_matchups.py`：ダメージ計算機（CalculateBaseDamage移植）。現行エンジン。`matchups_report.json` の出どころ
- `parse_frontier.py`：pokeemerald生データ → 本ディレクトリのCSV/JSON群。**抽出時のスナップショットで、
  同梱の `pokeemerald/` とヘッダ名が一致しないため再実行できない**（記録として同梱している）

## 抽選の仕組み（コードから確定した仕様）

1. 連勝数から `challengeNum`（=何周目か。7戦=1周）が決まる
2. `challengeNum` ごとのトレーナーID範囲から乱数で相手が選ばれる（各周の7戦目だけ1段上の範囲）
3. **challengeNum 7以降（50戦目〜）は常にID200-299から抽選**
4. トレーナーIDが決まると、そのトレーナーの `set_ids` から種族重複・持ち物重複なしで4匹（ダブル）が選ばれる
5. 個体値はトレーナーIDで固定、性格はセットで固定、特性は個体の性格値依存

## 再現手順

```
# 一次資料の取得（例）
curl -O https://raw.githubusercontent.com/pret/pokeemerald/master/src/data/battle_frontier/battle_frontier_mons.h
# ほか battle_frontier_trainers.h / battle_frontier_trainer_mons.h /
#      battle_tower.c / species_info.h / 各種 constants ヘッダ
# パーサ: ../tools/engine/parse_frontier.py（当時のスナップショット。上記のとおり再実行不能）
```
