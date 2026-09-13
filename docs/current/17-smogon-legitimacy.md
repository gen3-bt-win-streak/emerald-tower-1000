# 17. Smogon世界記録提出：正規性・入手方法の調査レポート（2026-07-30）

> **調査目的**：エメラルド バトルタワー（ダブル・Lv100オープン）のSmogon Battle Frontier Records提出に向け、
> ①公式ルール ②記録保持者の実態 ③個体正規性の証明水準 ④PokeFinder+PKHeX運用の位置づけ を一次情報基準で整理し、
> 本プロジェクトのケース（Delta・ステート不使用・実在スプレッドのPKHeX再現）の掲載可能性を評価する。

## 0. 情報源の等級（本レポートの読み方）

この環境からは smogon.com / projectpokemon.org / pokepast.es への直接アクセスが遮断されていたため（プロキシ403）、
情報源を4等級に分けて全項目にラベルを付けた。**ページ番号・投稿番号は検索経由のものを含み、最終確認はブラウザで行うこと。**

| ラベル | 意味 | 信頼度 |
|---|---|---|
| 【原文】 | スレッド原文の直接コピー（2026-07-29にユーザーがスレから取得・貼付した一次資料） | **高** |
| 【ソース確認】 | GitHub等で実ソースコード/文書を直接取得して確認 | **高** |
| 【検索抽出】 | 検索エンジンのスニペット経由（複数クエリで一致を確認したもの） | **中** |
| 【推測】 | 上記から導いた推論（事実と明確に区別する） | **低** |

---

## 1. Smogon公式ルール（Gen III Battle Frontier Discussion and Records スレッドOP）

スレッド：https://www.smogon.com/forums/threads/gen-iii-battle-frontier-discussion-and-records.3648697/

### 1.1 genned（生成）個体 —【原文】信頼度：高

> *"Don't cheat (this includes save stating or restoring save files to avoid losses). Streaks using illegal Pokemon will not be leaderboard eligible. **You are allowed to use genned Pokemon so long as they have legally obtainable stats and moves.**"*
>
> 訳：チートは禁止（負けを回避するためのセーブステートやセーブ復元を含む）。違法なポケモンを使った連勝はリーダーボード掲載資格なし。**合法的に入手可能なステータスと技である限り、生成（genned）ポケモンの使用は許可される。**

- 補足【検索抽出】：この方針は「従来のBattle Tower/Maison/Treeスレの伝統（genned不許可）からの意図的な逸脱」と説明されている。

### 1.2 乱数調整（RNG） —【原文】信頼度：高

> *"You cannot perform rng manipulation to manipulate the trainers you face, the layouts of facilities, or your drafts in the Battle Factory. Runs that use these methods will not be accepted on the leaderboard."*
>
> 訳：対面トレーナー・施設配置・ファクトリーのドラフトを操作する乱数調整は不可。

- 【検索抽出】：**自分のポケモンのIV・ステータスを狙う乱数調整は完全に許可**（"RNG manipulation to get Pokemon with desirable IVs and stats are fully allowed"）。禁止は「相手側の操作」のみ。

### 1.3 提出要件 —【原文】信頼度：高

> *"All records require a screenshot or picture of your in-game Battle Results and all users are required to obligatory disclaim the facility that was challenged, the level it was challenged for (Lv. 50 or Open Level) and whether the streak was done on retail or emulator."*
>
> 訳：全記録に**ゲーム内バトル記録画面のスクショ/写真**が必須。施設・レベル帯（Lv50/オープン）・実機orエミュの申告が義務。

> *"All submissions must include the exact stats or IVs of any Pokemon being used."*
>
> 訳：**使用個体の正確な実数値またはIVの開示が義務**（ファクトリーを除く）。
> 【検索抽出】これは「Gen 3では違法なスプレッドを持つgenned/hackedポケモンが使われていないか確認する追加チェック」と説明されている。

### 1.4 エミュレータ —【原文】信頼度：高

> *"Records on emulators are eligible as well as any Pokemon obtained from an emulator. Records on retail and emulator will be marked differently... Due to how easy it is to cheat streaks on emulator, having concrete proof such as recorded videos or detailed write-ups is heavily encouraged. I reserve myself the right to ask for any additional recorded footage if I do not trust your streak enough..."*
>
> 訳：エミュ記録も掲載資格あり（エミュ入手個体も可）。実機とエミュは別表記（リーダーボード凡例：`*`=継続中、`‡`=エミュ【原文】）。
> エミュはチートが容易なため**動画・詳細write-upを強く推奨**。信頼できない場合は**追加映像を要求する権利を管理者が留保**。

> *"Streaks must be done on legitimate copies of the game. Emulator streaks must be done on unedited ROMs without any patches. Bootlegs, ROM-hacks or fan-translations will not be allowed."*
>
> 訳：正規のゲームコピーであること。エミュは**無改造ROM**限定（パッチ・ROMハック・ブートレグ・非公式翻訳は不可）。

### 1.5 管理者の裁量条項 —【原文】信頼度：高

> *"This is not a court of law. I reserve myself the right to reject sufficiently dubious streaks even without absolute proof of cheating. The various facility threads rely on a system of trust."*
>
> 訳：ここは法廷ではない。**チートの絶対的証拠がなくても、十分に疑わしい連勝は却下する権利を留保する。** 各施設スレは信頼のシステムで成り立っている。

### 1.6 スレ管理者 —【検索抽出・矛盾あり】信頼度：低〜中

- 調査Aは「OP著者は **Valentino23**（2019-03-28開始）、検証チームとして Adedede / Wildcat Formation / Actaeon / wtset が提出を検証」と抽出。
- 調査Bは「**Kommo-o** がスレッドを引き継いだ（"adopted the thread"）」と抽出。
- **両立可能な解釈**【推測】：管理者は時期により交代しており、現行管理者はどちらか（要ブラウザ確認）。ルール原文が一人称なのは歴代管理者が引き継いだOPのため。
- 前身スレ：https://www.smogon.com/forums/threads/gen-3-battle-frontier-record-thread.3478612/【検索抽出】

### 1.7 グリッチ方針（post-8765280）—【検索抽出】信頼度：中

許可される主なもの：**タワーのクローン技（自由に使用可）**・ことう/イベント地点への到達・ポメグ系は「孵化親としてのみ」等。
リンク：https://www.smogon.com/forums/threads/gen-iii-battle-frontier-discussion-and-records.3648697/post-8765280（本文は未取得）

---

### 1.8 2026-09-10 追記：OPの最終編集日・追加文言・管理者回答の時系列 —【GPT逐語引用・要目視確認】信頼度：中

走者経由でChatGPTにスレッドを実際に開かせた結果（原文 `tools/smogon/gpt-answer-A-smogon-thread.md`。本環境は smogon.com を開けないので未検証）。

- **OP（Valentino23, 2019-03-28, Post #1）の最終編集は 2026-06-16**（編集者名は表示されず）。§1.1〜1.5 の原文は現行OPと一致。
- OPに **"It is your responsibility to ensure your Pokemon is possible to obtain."** が存在すると報告（§1.1の走者コピー（2026-07）には無い行。コピー漏れか後の追加か不明→**投稿前に目視確認**）。
- OPのXD条項: "Recover a deleted purify move. Your Pokemon must be a legal Pokemon obtained from Pokemon XD Gale of Darkness."（Pikeグリッチの許可範囲）。
- **管理者回答との矛盾**: Adedede（2024-12-23, p.76, Post #1891）「The issue that makes your streak not eligible is your team using PkHex'd Pokemon」「At the moment, the rules are the same: no submission with genned Pokemon is valid for the board.」→ **2024年末時点ではPKHeX産は不可と運用**。その後 sbeven（2026-02-24, p.83, Post #2074）が「PokeFinderで合法PID/advanceを示せるPKHeX個体は使えるか」と質問し、**回答はGPTの閲覧範囲で見つからず**。現行OP（2026-06-16編集）はgenned可。
- **同日の再検証（GPT回答C、`tools/smogon/gpt-answer-C-reverification.md`）で決着**: sbeven #2074 は「OPに『Streaks using genned or hacked Pokemon will not be allowed』と『genned可』が併存している矛盾」の指摘。その後 p.85 で Jeez Louise（#2107, 2026-04-06）が「チーム全員PKHeX産」と明記して可否を質問し、**Valentino23（リーダーボード管理者, #2117, 表示日付 2026-05-04）が明示回答。走者がスクリーンショットで原文確認済み【原文・信頼度：高】**：「There have been questions if genned Pokemon are allowed. The answer is yes, but they *must* have legal moves and IV combinations, etc. It is your responsibility to ensure you do not have any illegal IV spreads for a given Pokemon. I always recommend rnging your pokemon, but I understand not everyone is able to do so.」同投稿で「steal from battle tower glitch」は「非合法な技/IVにならないなら構わない」、そして**「I am planning to retire as leaderboard manager by the end of this year … By the end of the year if everything is sorted, I'll announce who is taking over.」**（2026年末に管理者交代）。Jeez Louise（#2119）は非合法6Vをやめて**PokeFinderで合法スプレッドを探し直しPKHeXで作り直す**と宣言、Valentino23（#2122, 2026-05-10）はRS盗みグリッチ産も「合法IV/技のgenned個体と同じ扱い」としてルール更新を予告。OPの2026-06-16編集はこの整理。
- **§8の評価への影響**: 「掲載可能性：高い」は**OP文言ベース・運用ベースの両方で確定**。管理者が求めるのは「合法な技とIVの組であることの本人責任での確認」で、本プロジェクトのPokeFinder実在フレーム特定＋PKHeX Legalはそれを大幅に超える。質問投稿は不要（27章）。Bank of Hoenn の配布個体は「All these Pokemon have been RNG abused on emulators」（Kommo-o, 2021-01-29, p.35 #851）＝実際にエミュで乱数調整して入手した.pkであり、本プロジェクトの「PKHeXで再現」とは一段違う。この差を投稿で正面から問う。
- リーダーボード上位10（Open／Lv50）とJheisinhoのフリーザー2個体（おくびょう 31/6/31/30/31/31 と 31/26/31/30/31/31、いずれもXD直接経路に実在）は 26章§6.2–6.3。

## 2. 記録保持者の個体入手方法

### 2.1 総括表

| プレイヤー | 記録 | 実機/エミュ | 個体準備 | 証明 | 信頼度 |
|---|---|---|---|---|---|
| **Jheisinho** | タワーダブル両部門1位（Lv50 1001‡／オープン 1316‡・ラティオス/ケンタロス/ラグラージ/フリーザー） | **エミュ（‡）**【原文】 | **本人言明は発見できず**。XD限定わるあがき…改めXD限定くろいきりフリーザー＋めざ岩ラグラージ＝genned or 高度な準備が自然な解釈【推測】 | リーダーボードに[paste]＋動画あり・配信実績（9月にstream）【検索抽出】 | 中 |
| **Adedede** | シングルLv50 3010（IRIDESCENCE）／オープン1090（Dans Macabre） | Dans Macabre=**実機**（テストカートで100勝→クローン技で公式カートへ移送）【検索抽出】IRIDESCENCE=抽出が矛盾し**未確定** | 明示言明なし。色違いニックネーム個体3体をタワークローン技で複製 | **YouTubeに節目動画多数**（1001/2205/2303/2415/2457/3010等・チャンネル: https://www.youtube.com/channel/UCYmHbDlHzLnoWkd-kz-0HAw ）＋詳細write-up | 中〜高 |
| Kommo-o | タワー108・ファクトリー56（Lv50） | **実機と明記**【検索抽出・page-53】 | 不明 | — | 中 |
| An Urban Skier / waffles101 / Ab2658 / Ghost14196 / GOSCIZOR | ダブル上位勢 | 表記どおり（‡有無） | **一切の言明を発見できず** | [paste]リンクのみ | 中 |
| Helta / wtset | Heltaは情報発見できず。wtsetは**検証チーム側**として名前が出る【検索抽出】 | — | — | — | 低 |

### 2.2 重要な観察（事実と推測の区別）

- **事実**【検索抽出の範囲】：上位勢の誰一人として「genned」「RNG捕獲」を明示した投稿は発見できなかった。IV開示はルール上の義務なので[paste]内にあるはずだが、pasteの中身は未取得。
- **事実**【原文】：ルールがgennedを明文許可しているため、**入手方法を申告する義務そのものが存在しない**（開示義務はIV/実数値のみ）。
- **推測**：エミュ勢（現1位・2位を含む）にとってgennedは合理的選択であり、コミュニティもそれを前提に運用している。「どう用意したか」は文化的に問われていない。

---

## 3. サンダー（FRLG産・めざ氷）

- **めざ氷サンダーの採用例**：Adededeの旧シングル編成（Dans Macabre系譜のZapdos @ラム・ひかえめ・10万/めざ氷/どくどく/みがわり）【検索抽出】。ダブル上位のサンダー採用（Golden Blissey・Albus・Burning Justice）は**めざ草**採用が目立つ（雨パ/対水文脈）。
- **IV・PID・出自（FRLG産）を開示/証明した例：発見できず**【検索抽出の範囲で0件】。
- **出自証明の文化は存在しない**：出自が話題になった唯一の例は「FRLGでフラグをリセットしてサンダーを再出現させるのは合法か」という質問で、証明要求ではない【検索抽出】。
- 【推測】genned許可の下では「FRLG産であることの証明」は誰にも求められない。**本プロジェクトの水準（Method-1実在フレームまで特定・PKHeX Full Reportで機械的認定）は、コミュニティの実運用を大幅に上回る過剰品質**。

## 4. ラティオス（みなみのことう産・おくびょう）

- **Jheisinhoのラティオス**：@ラム・サイキネ/冷B/10万/まもる（技構成は本プロジェクトと同一）。**IVは[paste]未取得のため不明**【検索抽出】。
- **コミュニティの「完璧」個体の実態**：
  - Project Pokemon配布ファイル「**PERFECT 5IV 31/7/31/31/31/31**」（おくびょう・色違い・RNG産）：https://projectpokemon.org/home/files/file/5648-pokemon-emerald-shiny-timid-latios-perfect-5iv-31731313131-rng-manipulation/【検索抽出】
  - Team Azure（Smogonのタワー構築記事）のラティオス：おくびょう **31/4/31/31/31/31**：https://www.smogon.com/forums/threads/team-azure-a-gen-3-battle-tower-team.3642308/【検索抽出】
- **おくびょうA0理想（31/0/31/31/31/31）がMethod-1に存在しないことを明言する一次ソース：発見できず**。ただし：
  - 一般原理として「Gen3のLCRNGはPIDとIVの組み合わせが有限で、特定の性格×IV組は存在しないことがある」はPKHeX issue #3894等で確認【検索抽出】
  - **本プロジェクトの独立検証（一次計算）**：LCRNG全32bit状態の逆算列挙により、おくびょうMethod-1の該当スプレッドを全数探索済み。採用個体 `E955D07C`（**31/7/31/31/31/31**）はその最良解であり、**コミュニティが「PERFECT」と呼ぶ配布個体と攻IV=7まで完全に同型**。外部証拠と独立計算が一致した。信頼度：**高**（自前計算＋外部一致）
- Emerald静的乱数の方法論（シード0起動・ペインティングリシード等）の標準ガイド群：
  https://www.pokemonrng.com/emerald-static/ ／ https://www.pokemonrng.com/emerald-painting-reseeding/ ／ https://retailrng.com/emerald/advanced/perfectstatic/【ソース確認（GitHubリポジトリ経由で本文一致確認）】

## 5. PokeFinder＋PKHeX運用の位置づけ

### 5.1 これは「コミュニティ公認の標準手順」である —【ソース確認＋検索抽出】信頼度：高

- **Project Pokemon公式チュートリアル**「PID Mismatch - Origin Game RSEFRLG (Pokefinder)」：
  https://projectpokemon.org/home/tutorials/save-editing/using-pkhex/pid-mismatch-origin-game-rsefrlg-pokefinder-r94/
  > *"All Stationary/Gift Pokémon in RSEFRLG use Method 1."* ／ *"When an entry shows up, copy the relevant information into PKHeX. When all information is inputted correctly, it'll be legal."*
  >
  > 訳：RSEFRLGの固定/贈呈ポケモンは全てMethod 1。「（PokeFinderで）ヒットした情報をPKHeXへ転記すれば合法になる」
  **＝本プロジェクトのやり方（実在スプレッド探索→PKHeX転記）は公式チュートリアルそのもの。**
- **Searcher/Generatorの定義**【ソース確認・pokemonrng.comのソースripo原文】：
  > *"For most RNG processes, you will begin with the 'Searcher' tab to find an initial seed, and then use the 'Generator' tab with the initial seed found to RNG the Pokemon."*
  >
  > 訳：Searcher＝条件から全シードを逆検索、Generator＝特定シードからフレームを順生成。
- **Method 1の一次定義**【ソース確認】：https://www.pokemonrng.com/gba-methods/
  > *"The Pokémon is generated using the value of the RNG of advances 1,2,3,4"*（PID下位→PID上位→HP/攻/防IV→素/特攻/特防IV）

### 5.2 PKHeXが実際に検証している内容 —【ソース確認（実コード）】信頼度：高

`kwsch/PKHeX` masterの実装を直接確認：

- `EncounterStatic3.cs` の `IsCompatible()`：**エメラルド産固定は `PIDType.Method_1` のみ合格**。FRLG固定も原則Method 1（実コード取得済み）。
- `MethodFinder.cs`：個体のPID/IVからLCRNGシードを逆算してMethod分類。
- 判定文言：`"PID+ correlation does not match what was expected for the Encounter's type."`＝「エンカウントタイプと性格値が一致しません」の実体。
- **含意**：本プロジェクトの4体がFull Reportで「Method_1・実在シード/フレーム」まで認定されたことは、**PKHeXのソースコード水準で「ゲームが生成し得る個体」であることの機械的証明**になっている。

## 6. Smogonが証明として認めるもの（まとめ）

| 証明手段 | 位置づけ | 根拠 |
|---|---|---|
| 記録画面のスクショ/写真 | **必須** | 【原文】 |
| IV/実数値の開示 | **必須** | 【原文】 |
| 施設・レベル帯・実機orエミュの申告 | **必須** | 【原文】 |
| 動画・詳細write-up | エミュでは**強く推奨**（義務ではない） | 【原文】 |
| 追加映像 | 管理者が**裁量で要求し得る** | 【原文】 |
| セーブデータ提出 | **要求された事例を発見できず** | 【検索抽出】 |
| バトルビデオ | Gen3に機能が存在せず、証明手段として言及なし | 【検索抽出】 |
| PokeFinder検索結果・Seed・PID・Frame | 要求事例なし（開示は任意の上乗せ） | 【検索抽出】 |
| 配信アーカイブ | 上位勢が任意で公開（Adededeの節目動画・Jheisinhoの配信）＝信頼形成の実例 | 【検索抽出】 |

## 7. 却下・疑義事例

- **Just_Peaches（却下確定例）**【検索抽出・page-55】：バトルアリーナ109連勝の申請が「**証拠の整合性不足**」＋「この構成でこの勝数は信じがたい（一般的な敵アーキタイプに不利）」を理由に却下され、**同氏の全記録がリーダーボードから除外**された。
  - 教訓【推測】：裁量条項は実際に行使される。**構築の説得力（なぜ勝てるかの説明）と証拠の厚みが防御線**になる。
- green_typhlosion【検索抽出・詳細不明】：ファクトリー64連勝が「なぜか掲載されなかった」との言及（却下か見落としか不明）。
- PKHeX生成個体を理由とする却下例：**発見できず**（そもそも明文許可のため理屈上あり得ない。違法ステータス/技なら1.1により却下対象）。

---

## 8. 本プロジェクトのケース評価

**条件**：Delta（iOS）／無改造ROM（自己カートから吸い出し・チェックサム照合済み）／ステート・巻き戻し不使用／
PokeFinder＋独自全数探索で**実在確認済みのスプレッド**（サンダー/ラティオス=Method-1・グロス/ラグラージ=孵化フレーム、2026-08-25来歴変更）をPKHeXで再現（実機capture無し）／イベントフラグ整合済み。

### 現行ルールでの掲載可能性：**高い**【原文ベース＋2026-05-03 管理者回答（§1.8）で運用も確認】

1. 「合法的に入手可能なステータスと技」——全個体がPKHeXソースコード水準の生成方式認定（固定=Method-1／孵化=Egg）＋正規習得技のみ。**ルールが要求する水準を大幅に超過**。
2. エミュ記録は明文で掲載資格あり（現1位・2位もエミュ‡）。
3. 「実際に捕獲していない」ことは問題にならない——gennedの明文許可がまさにこれを許すルール（1.1）。
4. IV開示義務は16章§4の確定表がそのまま満たす。

### 却下リスク：**低いが、ゼロではない**

- 唯一の実リスクは**裁量条項**（1.5）×**記録の高さ**。1,317+は現1位超え＝最大限の注目を浴びる申請になる。
- Just_Peaches事例の含意：疑念は「証拠の薄さ×構成の説得力不足」で発動する。
  → 対策：**(a) 全戦画面録画**（推奨を最大限実施）**(b) 7連勝毎の記録画面スクショ (c) IV/PID/シードまで開示 (d) 構築の勝率根拠（100万戦シミュ・確率計算）をwrite-upに添付**。本プロジェクトはここが世界最強レベルに厚い。
- アドバイザー（外部助言ツール）使用は改造・乱数操作のどちらでもないが、**write-upに明記して透明性を確保**するのが安全side【推測・方針】。

### 将来ルール変更時：**不確実**【推測】

- genned許可は「伝統からの逸脱」と自認されており、管理者交代等で厳格化される可能性は理論上ある。**【原文・2026-09-10】Valentino23 は #2117 で「2026年末までに管理者を退き、後任を年末に発表」と明言。交代は確定事項なので、提出は現管理者の在任中（2026年内）に行い、OPと#2117のスクリーンショットを提出物に含めて後任の再審査に備える。**
- 既掲載記録が遡及削除された事例は発見できず。厳格化されても遡及適用されない可能性が高いが、保証はない。
- ヘッジ：**提出時点の証拠を最大化**（録画・スクショ・開示）しておけば、後年の基準でも再審査に耐える。

---

## 8.5 手法の全面公開（提出の説得力を最大化する手段）

Just_Peaches事例（§7）が示すとおり、却下は「証拠の薄さ×構成の説得力不足」で発動する。
本プロジェクトは**シミュレータ・100万戦の生データ（全負けシード）・条項の設計過程・全ドキュメント**を
公開リポジトリとして提示できる＝**第三者が同一シードで負け率を再現検証できる**状態にある。
これはこのコミュニティで前例がなく、「信じがたい」という疑念に対する構造的な回答になる。

**公開用エクスポートは自動化済み**：`tools/make_public_export.sh`
- `battle-tower/` 単体の履歴を `git subtree split` で抽出
- 個人メールのauthor書き換え／コミットのセッションURL除去／AWS個人インフラ文書（13・14章）を全履歴から除去
- LICENSE（MIT＋第三者素材の注記）・英語README（`README_EN.md`、再現手順つき）・.gitignore は **2026-09-11 に `battle-tower/` 直下へコミット済み**。スクリプトは bundle 生成まで自動化され、同日この環境で通し実行して検証済み：1352コミット・author は公開用の仮名（2026-09-11 に Organization 名 `Gen3-bt-win-streak <Gen3-bt-win-streak@users.noreply.github.com>` へ変更。どのアカウントにも紐づかない）のみ・`Claude-Session` 行 0・個人識別子（メール／AWSアカウントID）は全履歴の全ツリーに残存なし・13／14章と本スクリプト自体は履歴から除去。`Co-Authored-By: Claude …` のトレーラーは残る（AI補助の開示として整合。消すなら `--msg-filter` に1行追加）。
- 公開手順：`bash tools/make_public_export.sh emerald-tower-1000.bundle` → `git clone emerald-tower-1000.bundle emerald-tower-1000` → `git remote set-url origin https://github.com/gen3-bt-win-streak/emerald-tower-1000.git` → `git push -u origin pub-split:main`。公開先 https://github.com/gen3-bt-win-streak/emerald-tower-1000 （2026-09-11 作成、空）。
- **更新の運用（2026-09-11 確認）**：エクスポートは**決定的**（同じ履歴・同じ書き換え規則なら再実行しても全コミットのハッシュが一致することを2回実行で確認）。よって研究は従来どおり `daily-tasks` の作業ブランチで続け、節目にスクリプトを再実行して bundle から `git push origin pub-split:main` すれば**fast-forward で追随**する（`--force` 不要）。公開側に直接コミットはしない。書き換え規則（除去ファイル・author）を変えた場合だけ履歴が変わり `--force` が要る。
- **公開完了（2026-09-11）**：https://github.com/gen3-bt-win-streak/emerald-tower-1000 の `main` に 1357 コミットを公開。公開後にクローンして再検証：author は `Gen3-bt-win-streak` のみ、セッション行 0、個人識別子 0、`xd_articuno_verify.py` は公開ツリーから ALL PASS。
- **以後の公開は GitHub Actions が行う**（`.github/workflows/publish-public-mirror.yml`、`daily-tasks` 側）。作業ブランチを checkout → エクスポート → 検証（失敗なら push しない）→ fine-grained PAT（Secret `PUBLIC_MIRROR_TOKEN`、Resource owner = gen3-bt-win-streak、対象 emerald-tower-1000 のみ、Contents: Read and write、**有効期限 2027-09-12**。切れたら同じ設定で作り直して Secret を更新）で公開リポジトリの `main` へ push。起動は Code が API から `workflow_dispatch` を叩く（既定ブランチに無いワークフローを登録するため、ワークフローファイル自身の変更 push でも起動する設定）。checkout の `persist-credentials: false` が必須（無いと Actions の標準トークンが優先されて 403）。
- この作業環境（Claude Code）は `Yuki670926` 配下のリポジトリしか扱えないため、公開リポジトリへ直接 push はできない。Actions 経由が正規の経路。
- 公開先は Yuki670926 が所有する Organization **`Gen3-bt-win-streak`**（2026-09-11 作成、メンバー表示は Private）。第2の個人アカウントはGitHub規約（無料個人アカウントは1人1つ）に抵触するため使わない。
  リポジトリ本体に秘密情報は無いが、コミットのauthorメールが唯一の実リーク経路だったため書き換え対象にしている。

## 9. 世界記録提出チェックリスト

**準備（完了済みのものはチェック）**
- [x] 無改造ROM（自己カートリッジから吸い出し・No-Intro checksum照合）
- [x] 正規セーブ（実プレイ由来・イベントフラグ整合済み＝16章§5）
- [x] 4体すべて実在フレームのスプレッド（サンダー/ラティ=Method_1認定・グロス/ラグ=孵化フレーム。16章§4・2026-08-25更新）
- [x] IV/実数値開示表（16章§4がそのまま提出資料）
- [ ] （任意・推奨）各個体のPokeFinder検索条件・シード/フレームのスクショ保存

**走行中の規律**
- [ ] セーブステート・巻き戻し・早送り以外の機能を使わない（Deltaの早送りは対戦結果に影響しないが、write-upで使用有無を明記）
- [ ] 中断は必ず「休憩」→再開はRestart→セーブロード（ステート復元をしない）
- [ ] **画面録画を回す**（最低でも節目と記録更新帯。理想は全戦・セグメント録画の頭と尾で記録画面を映す）
- [ ] 7連勝セットごとに記録画面スクショ

**提出物**
- [ ] ゲーム内バトル記録画面のスクショ（必須）
- [ ] 申告：Battle Tower／Open Level（Lv100）／**Emulator（Delta, iOS）**
- [ ] 全個体のIV・実数値・持ち物・技（＋任意でPID/シード）
- [ ] write-up：構築解説・勝率根拠（シミュ統計）・個体準備方法（genned・実在スプレッド・ツール名を正直に記載）・アドバイザー使用の明記
- [ ] 録画リンク（YouTube等・限定公開でも可）
- [ ] 管理者から追加映像要求が来た場合に備え、生録画データを保全

**最終確認**
- [ ] リーダーボード原文の再確認（現1位の数値が変わっていないか）
- [ ] ルールOPの再読（提出直前に原文をブラウザで再確認——本レポートの引用の最終検証を兼ねる）
