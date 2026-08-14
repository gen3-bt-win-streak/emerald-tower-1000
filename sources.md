# 出典・検証記録

## 一次資料（最優先。data/ のCSVはここから機械抽出）

**pret/pokeemerald**（エメラルド逆コンパイル。raw.githubusercontent.com/pret/pokeemerald/master/...）
- `src/data/battle_frontier/battle_frontier_mons.h` — 敵全882セット
- `src/data/battle_frontier/battle_frontier_trainers.h` ＋ `battle_frontier_trainer_mons.h` — トレーナー300人と使用プール
- `src/battle_tower.c` — 抽選・IV・レベル・重複禁止・Lv50プールカット（FRONTIER_MONS_HIGH_TIER=849）
- `src/battle_ai_switch_items.c` — 交代AI（6トリガー）
- `data/battle_ai_scripts.s` ＋ `src/battle_ai_script_commands.c` — 技スコアリングAI・AIフラグ・AIの情報アクセス
- `src/battle_main.c` — クイッククロー20%・同速50/50・バッジ補正無効
- `src/pokemon.c` — 敵個体生成（特性＝性格値偶奇で1/2、努力値＝2ステ255/3ステ170）
- `src/data/pokemon/{species_info,level_up_learnsets,tmhm_learnsets,egg_moves,tutor_learnsets}.h` — 習得・特性・卵グループ
- `src/data/items.h` — 持ち物発動率（QC20/ハチマキ10/おうじゃ10/こな10/おこう5）
- `src/frontier_util.c` — 連勝カウント・ブレーン出現条件（シングル限定）

## 検証済み事項の要約（2026-07 ワークフロー14エージェント）

| # | 項目 | 結果 |
|---|---|---|
| 1 | 敵IVスケーリング | ✅トレーナーID基準で確定（3/6/9/12/15/18/21/31）。「セット単位」ではなくID単位 |
| 2 | 敵の二特性の決定 | ✅性格値bit0で**ちょうど1/2**（しめりけゴルダック=50%） |
| 3 | 一撃技セット | ✅23セット完全列挙（01参照） |
| 4 | 敵のほろび/じばく/爆発 | ✅3/0/24セット完全列挙 |
| 5 | ぼうおん持ち | ✅12セット（+プール外3）完全列挙 |
| 6 | トリック持ち | ✅**実在**。3セット全て@こだわりハチマキ |
| 7 | AIのまもる条件 | ✅コード確定（CV+2デフォルト、連続で−2など。03参照） |
| 8 | クイッククロー発動率 | ✅20%（13107/65536）。**ターン内で乱数共有＝場の全ツメ持ちが同時発動/同時不発（2026-08-11に`battle_main.c`原文で確定・03章§5.1）**。ハチマキは被弾ごとの独立抽選で無関係 |
| 9 | 徘徊ラティオスのシンクロ | ✅**無効**。個体はテレビ回答の瞬間に固定。エメラルドはIVバグ修正済み |
| 10 | トレーナータイプ→プール | ✅data/trainer_classes_battle50plus.csv 完成（cpp展開でパーサバグ修正済み） |
| 11 | TM30入手 | ✅おくりびやま6Fで**1個のみ**。ゲームコーナー景品に無し |
| 12 | ダブルの複数対象補正 | ✅**じしん/爆発は減衰なし**。0.5倍は相手2体対象技のみ（重大訂正） |
| 13 | 引き分け仕様 | ✅相打ち全滅=プレイヤー負け（Dans Macabreスレ明記）。※コードレベルの条件は未読 |
| 14 | ムウマ入手 | ✅**エメラルド不可**。リーフグリーン・ななしのどうくつ限定（重大訂正） |
| 15 | ほろびのうた遺伝 | ✅♂ムウマLv45×♀ゴース系（両者とも不定形グループ）。ゴース遺伝技にだいばくはつも存在 |
| 16 | メタグロスのシャドボ | ✅TM30適性あり（メタングも可、ダンバル不可）。だいばくはつはキナギ教え技1回のみ |
| 17 | AI交代仕様 | ✅6トリガー確定。ほろびのうた=唯一の100%トリガー、最終ターンに交代 |
| 18 | AIの情報アクセス | ✅ダメージ計算は実ステ実持ち物（チート）、こちらの技は使用するまで不可視、急所/命中は無視 |

## 残る未解決（実機検証キュー）

1. みちづれ状態の敵を爆発で倒した際の判定と引き分け仕様の正確な発動条件（コード：`battle_script_commands.c` の勝敗判定読解 or 実機）
2. ~~ダブル799連勝チームの一次確認~~ → **✅解決（2026-07-29・ユーザー提供のスレ原文）**：現行1位は**1,316連勝**（Jheisinho・
   ラティオス/ケンタロス/ラグラージ/フリーザー・エミュ）。799はAb2658（ラティアス/ラグラージ/カビゴン/ラティオス＝旧有力説どおり）で現2位
3. ありじごく判定バグ（飛行/ふゆうにも有効）の実害確認

## 二次資料・先行研究

### 記録（2026-07時点の調査）
- **シングルLv50世界記録: 3010連勝**（Adedede氏 IRIDESCENCE: エアームド/ハピナス/ラティオス）
  https://www.smogon.com/forums/threads/iridescence-emerald-battle-tower-2500-wins-team.3674437/
- **シングルオープン記録: 1090連勝**（同氏 Dans Macabre: ハチマキケッキング/ソーナンス/ゲンガー@ラム
  みちづれ/ほろびのうた/まもる/くろいまなざし）
  https://www.smogon.com/forums/threads/dans-macabre-a-record-breaking-gen-3-battle-tower-singles-team.3651964/
- **ダブル最高: 1,316連勝**（Jheisinho・オープンLv100・エミュ。ラティオス/ケンタロス/ラグラージ/フリーザー。
  2026-07-29にリーダーボード原文で確認）。2位: 799連勝（Ab2658。ラティアス/ラグラージ/カビゴン/ラティオス＝旧有力説が正解だった）。
  Lv50ダブルも同氏1,001連勝が1位
  https://www.smogon.com/forums/threads/gen-iii-battle-frontier-discussion-and-records.3648697/
- 日本語圏ダブル: オープン70連勝（ハチマキメタグロス/みちづれゲンガー/カビゴン/スイクン）
  https://ameblo.jp/almond-taka/entry-12079164575.html
- 日本語シングル: 2303連勝解説 https://baobaopoke.hatenadiary.com/entry/worldrecord ／ 802連勝 https://note.com/takep_r/n/n2515b4f948f4
- 本プロジェクトは**オープン・ダブル**採用 → 世界記録の更新ライン＝**1,317連勝**（1000連勝は歴代2位相当。
  2026-07-29の1,316確認で目標値を再校正。Lv50ダブルも現在は1,001連勝まで伸びており「80連勝程度」は過去の誤認）

### QC+一撃技への先行対策（記録者の実践）
1. がんじょう持ち（エアームド等）による一撃技無効化
2. ふゆう/飛行によるじわれ無効（ラティオス・ゲンガーは適合）
3. まもる/いちゃもんでのセット判別スカウト
4. ソーナンスみちづれによる1:1交換の受け入れ
5. ダブル特有：初手集中攻撃（focus fire）での2vs1化
※ IRIDESCENCE作者も「QC+こな+ぜったいれいどは完全対策不可能」と明言＝確率圧縮の思想で挑む

### 仕様の裏取りに使ったページ
- Bulbapedia: Battle Tower (Generation III) / Battle Frontier (Generation III) / Sleep / Confusion / Paralysis /
  Critical hit / Damage / Explosion / King's Rock / Synchronize / Roaming Pokémon / Lost Cave
- Serebii: emerald/tower.shtml / emerald/movetutor.shtml / ItemDex TM30 / Pokéarth
- Glitch City Wiki: Roaming Pokémon IV glitch（エメラルドで修正済みの根拠）
- Smogon: Introduction to ADV Doubles（複数対象補正）/ RS dex

※ この作業環境からは bulbapedia/serebii/smogon 等への直接アクセスがプロキシで遮断されているため、
検索経由スニペット＋pokeemeraldコードで照合した。ユーザーのリンク2件（Serebiiタワー・Bulbapediaトレーナー一覧）の
内容は、それぞれ 00-rules.md のルール表と data/trainers.csv（一次データ由来でより正確）でカバー済み。
