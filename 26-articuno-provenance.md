# 26. フリーザー（XD産）の来歴証明ドシエ【2026-09-09】

> **対象個体（正）**：Pokémon XD シャドウフリーザー（PKHeX "XD Shadow Encounter 76"・シトンダーク島＝Citadark Isle・Lv50・リライブ技 じんつうりき／いやしのすず／くろいきり／れいとうビーム）
> おだやか・IV **31/0/31/29/31/31**（H/A/B/C/D/S）・PID **`2F3C902C`**・XDRNG origin seed **`ECFE3E26`**（IV1直前の乱数状態）・PSV 6114・通常色。PKHeX Legal（PIDType CXD）は確認済み。
> 本章の目的は「PKHeX Legalだから」ではなく、**XDの乱数アルゴリズムから独立に生成可能であること**、**実機での入手ルート**、**Smogon記録申請時に何を証拠として出すか**を確定すること。
> 再現スクリプト：`tools/remote-audit/xd_articuno_verify.py`（自己完結・PokeFinderのテストベクタ11件110状態を内蔵・39項目 ALL PASS・実行約1秒）。
> 調査体制：ソース監査（PokeFinder／RNG Reporter／PKHeX）・Web技術資料・Smogon・色違い／Haze・理想個体出典・ローカル計算の7系統を並列で行い、主要主張2件（色違い不可／生成可能性）は各3名の反証担当が独立に検証（全員 confirmed）。Web直アクセスはsmogon／Bulbapedia／Project Pokemon／各ブログが遮断されており、それらは検索スニペット引用（本文で「スニペット」と明記）。

## 0. 結論

1. **XD RNG上で生成可能。** origin `ECFE3E26` からXDRNG（乗数0x343FD・加数0x269EC3）を5フレーム進めるとIV1／IV2／特性／PID上位／PID下位がそのまま対象個体になる。PKHeXのコードを使わず、**PokeFinderの生成ルーチンを移植してPokeFinder同梱のテストベクタ110状態を全一致**させた実装で導出し、逆算は origin `ECFE3E26` の1件に一致、PKHeX式ロック連鎖は5変種すべて有効（§2〜§3）。ただし「ハードウェアの実測」ではなく「独立した複数実装の一致」である点は§8の証明力に反映。
2. **「おだやか 31/0/31/31/31/31」はXDでは生成不可能**（直接経路にも、アンチシャイニー再抽選の全深度にも存在しない）。A0/C31を出す乱数状態は32bit空間に**4つだけ**で、性格は直接が てれい／うっかりや／しんちょう／きまぐれ、再抽選1回が ようき／ずぶとい／わんぱく／おくびょう（特定のTID/SIDが必要）、2回以上は不可。**おだやかA0の上限はC29＝対象個体**（§4）。流布する「理想個体」のうち ずぶとい／おくびょう A0 は再抽選経路（TSV 4941 のセーブ限定）、ひかえめ A4・おくびょう A6・おだやか A5 は直接経路（§4）。
3. **Smogonは「PKHeX Legal」も「XD RNG検証」も要求していない。** 現行ルールが求めるのは Battle Results のスクショ・施設／レベル／実機かエミュかの申告・チームのimportable・**全個体の実数値かIV**。genned個体は「合法的に入手可能な実数値と技」であれば明文で許可、自分の個体の乱数調整は許可、エミュ記録は‡付きで有効、動画は「強く推奨」で管理者は追加映像を要求でき、疑わしい記録は却下できる。1316勝の記録者（Jheisinho・エミュ‡）はフリーザーのPID／TID／SIDを公開しておらず、XD RNGの数学的検証も投稿されていない（§7）。**したがって本章の水準（§2〜§4）は要求水準を大きく上回る**。保存すべき証拠は§9。

## 1. XDシャドウ生成の仕組み

- **XDRNG**：`seed' = seed × 0x343FD + 0x269EC3 (mod 2^32)`、出力は上位16bit。逆行は `× 0xB9B33155 + 0xA170F641`。PokeFinder `Core/RNG/LCRNG.hpp:296-297`（`using XDRNG = LCRNG<0x269EC3, 0x343FD>`）、PKHeX `XDRNG.cs:23-26`、aldelaro5 `BaseRNGSystem.cpp` で一致。乗数≡1 (mod 4)・加数奇数なので周期2^32＝**全状態が1周期に1回ずつ現れる**（どのoriginにも到達しうる）。
- **起動時の初期seed**：GameCubeのティッククロック下位32bit（40.5 MHz・約22ns刻み）。実機では本体時計で狙えず、**2^32から乱択**（aldelaro5 gist・`Common.h`。信頼度 中）。エミュ（Dolphin）ではRTC日時から決定論的（pokemonrng.com "Initial Seed RNG"、ソースは zaksabeast/PokemonRNGGuides から取得）。
- **非ロック個体の生成順**（PokeFinder `GameCubeGenerator::generateNonLock` `:361-374`、IV展開 `:380-385`）：IV1（HP|A<<5|B<<10）→ IV2（S|C<<5|D<<10）→ 特性（1bit、特性が1つの種は0固定）→ PID上位 → PID下位 →**`(hi ^ lo ^ TSV) < 8` なら PIDペアを再抽選**（`isShiny` `:32-35`、「Shiny lock is from TSV of savefile」）。TSV＝**プレイヤーのセーブのTID^SID**。
- **シャドウ（NPC手持ち）の生成順**（`generateGalesShadow` `:215-298`）：敵トレーナーTID/SID 2フレーム → 手持ち各1体につき 仮PID2＋IV2＋特性1＝5フレーム（非シャドウは続けて性格／性別ロックと非色違いを満たすまでPIDペア再抽選）→ 仮PID 2フレーム → シャドウ本体のIV1／IV2／特性／PID（再抽選付き）。PKHeX `NPCLock.FramesConsumed`（`:14`）は未確認シャドウ7フレーム／確認済み5フレームで、構造的に一致。
- **PKHeXの判定**：`MethodFinder.GetXDRNGMatch`（`:254-300`）がPIDペアから2フレーム戻った2出力をIV1/IV2と照合（一致＝`CXD`、途中に色違いペアが挟まれば`CXDAnti`）。**XD個体のLegal判定は `EncounterShadow3XD.IsCompatible`（`:145`）で PIDType が CXD／CXDAnti かを見るだけ**で、先行シャドウの `LockFinder` は生成時（`MethodCXD.cs:37,428`）にしか呼ばれない（反証担当C2-1の指摘）。つまり**ロック連鎖の検証はPKHeXのLegal判定には含まれておらず、本章§3の移植が独自に行った検証**である。
- **フリーザーのロック**：PKHeX `Encounters3XDShadow.cs` `XArticuno` ＝ サイドン／ファイヤー／ナッシー／ケンタロス（全員シャドウ・性格指定なし。`NPCLock.MatchesLock` `:37` は `Shadow && Nature==0` で常に真）。Seen有無で5変種。**3鳥は性格ロックなし**（PokeFinder issue #105、RNG Reporter af版 `NatureLock.cs` で Articuno＝NoLock、PKHeX）。
- **PokeFinderでの位置づけ**：シャドウロック一覧（77件）に3鳥は含まれず、**フリーザーは「Non Shadow Locks」静的リスト index 67・`Shiny::Never`**（EncounterTableGenerator `Gen3/encounters.json` @fb7414de、2026-02-28 "Correct Gales encounters" 以降）。生成／検索は上記の非ロック経路。**配布バイナリ（最新 4.3.0）に含まれるかは未確認**（§10）。
- **アンチシャイニーの照合相手**：PokeFinder／aldelaro5はプレイヤーTSVのみ。PKHeX（`TeamLockResult.VerifyNPC`）はCPUトレーナーのTSVに対する非色違いも要求し、Bulbapedia／Glitch City（スニペット）は「相手か自分のID」と記す。逆アセンブル級の一次資料は開けなかった。**どちらでも結論（§6）は変わらない**（プレイヤーID照合だけでOTに対して非色違いが確定するため）。

## 2. 対象個体の導出（独立実装）

| フレーム | 状態 | 上位16bit | 意味 |
|---|---|---|---|
| origin | `ECFE3E26` | — | IV1直前の状態（PKHeXの「Origin Seed」） |
| s1 | `7C1FFC51` | `7C1F` | IV1：HP31／A0／B31 |
| s2 | `FFBF2DD0` | `FFBF`→`7FBF` | IV2：S31／C29／D31 |
| s3 | `52845553` | `5284` | 特性bit 0（プレッシャー1つなので無関係） |
| s4 | `2F3CAACA` | `2F3C` | PID上位 |
| s5 | `902C4665` | `902C` | PID下位 |

PID `2F3C902C` → mod 25 = 20 ＝ **おだやか**、PSV = (0x2F3C ^ 0x902C) >> 3 = 0xBF10 >> 3 = **6114**。プレイヤーの (TID ^ SID) >> 3 ≠ 6114 なら再抽選は起きない（もし6114なら s6/s7 から再抽選され PID `E58324BB`＝わんぱく になる。反証担当C1-2が訂正した値）。
仮PIDペアの直前の状態は `F48AA54C`。

**独立性の担保**：`xd_articuno_verify.py` は PokeFinder `generateNonLock`／`generateGalesShadow` の移植で、PokeFinder同梱テストベクタ（`Test/Gen3/gamecube.json`：generateNonLock 5件＋generateGalesShadow 6件＝110状態、Profile TID 12345／SID 54321）を**全一致**で通過する。同じ実装が origin `ECFE3E26` advance 0 で対象個体を返す。RNG Reporter（Slashmolder 9.96.6A3 の "Colosseum\XD" 法＝[IV1][IV2][未使用][PIDhi][PIDlo]）で同seedを回しても同じ個体になる（研究R2）。
**限界**：PokeFinderのベクタは同ツールの回帰データであり実機キャプチャではない。よって本節は「独立した複数実装（PokeFinder・PKHeX・RNG Reporter af版・aldelaro5の実機検証済みモデル）の一致」であって「実機RAMトレース」ではない（§8）。

## 3. 逆算とロック連鎖

- **逆算（PKHeX `GetXDRNGMatch` 移植・GetSeedsはPKHeXのラグ方式と65536総当たりの両方）**：PID `2F3C902C` × IV 31/0/31/29/31/31 → **`CXD` / origin `ECFE3E26` の1件のみ**。プレイヤーTID/SIDに依存しない。Method 1/2/4（GBA）のどれにも合致しないので、FRLG産と取り違えられる余地はない（C2-2）。
- **ロック連鎖（PKHeX `TeamLockResult` 移植）**：origin の2フレーム前 `F48AA54C` を起点に逆行し、先行4体のPIDとCPUトレーナーTID/SIDを割り当てる。5変種すべて有効。**Seen（確認済み）メンバーはゲーム内でPIDを生成しない（5フレーム消費のみ）ので、PIDは未確認メンバーにだけ意味がある**（C2-2の訂正）。

| 変種（グリーンビル戦の状態） | ケンタロス | ナッシー | ファイヤー | サイドン | CPU TID/SID | チーム生成前のseed |
|---|---|---|---|---|---|---|
| 全員未確認（初戦） | @0 `DD41F48A` | @7 `97EA6075` | @14 `82AD462B` | @21 `DB7D5915` | @28 `0300`/`8918` | **`D1D0AE06`** |
| サイドン・ファイヤー確認済 | @0 `DD41F48A` | @7 `97EA6075` | （確認済） | （確認済） | @24 `5BD9`/`766D` | `28E810AA` |
| ＋ケンタロス確認済 | （確認済） | @5 `2D531C69` | （確認済） | （確認済） | @22 `3C29`/`DB7D` | `766D3474` |
| ＋ナッシー確認済 | @0 `DD41F48A` | （確認済） | （確認済） | （確認済） | @22 `3C29`/`DB7D` | `766D3474` |
| 全員確認済 | （確認済） | （確認済） | （確認済） | （確認済） | @20 `5915`/`0602` | `DB7D868E` |

**順方向の再生成**：`D1D0AE06` から前進すると CPU TID `0300`/SID `8918` → サイドン `DB7D5915` → ファイヤー `82AD462B` → ナッシー `97EA6075` → ケンタロス `DD41F48A` → フリーザーIV1直前が `ECFE3E26` に戻る（往復一致）。
**条件**：初戦変種でこの連鎖がそのまま成立するには、プレイヤーTSVが先行シャドウのPSV {1337, 4173, 6288, 7923} に一致しないこと（一致すると当該NPCが再抽選されフレームがずれる。PKHeXは最初の候補を無条件に受理するためLegal表示は変わらない）。全変種を通したNPC PSV集合は {1337, 1575, 3787, 4173, 5209, 5215, 6288, 6622, 6627, 7923}、CPU-SVは {4419, 1462, 7402, 3042} で、いずれも6114ではない。
**評価**：先行4体は性格ロックなしなので、この連鎖は「PSVの偶然の衝突がない」以上の強い証拠ではない（C2-3）。強い証拠は§2のPID/IV相関である。

## 4. 「おだやか 31/0/31/31/31/31」の厳密判定と理想個体リストの正体

HP31・A0・B31 のIV1と S31・C31・D31 のIV2 が連続する乱数状態は**32bit空間に4つだけ**。各状態のPID列（直接→再抽選1回→…）：

| origin | 直接（再抽選なし） | 再抽選1回（要プレイヤーTSV） | 2回以上 |
|---|---|---|---|
| `2405CA1E` | てれい `7865E69D` | ようき `93EB2DCE`（TSV 5087） | 不可（PSV不一致） |
| `9243BC41` | うっかりや `1D8787EB` | **ずぶとい `6D1DDD5B`（TSV 4941）** | 不可 |
| `A405CA1E` | **しんちょう `F865669D`**（16章の予備個体） | わんぱく `13EBADCE`（TSV 5087） | 不可 |
| `1243BC41` | きまぐれ `9D8707EB` | **おくびょう `ED1D5D5B`（TSV 4941）** | 不可 |

→ **おだやか A0/C31 は、直接経路にも再抽選経路の全深度にも存在しない**（4状態とも再抽選1回目のPIDが非色違いで連鎖が止まるため、2回以上の再抽選自体が起きない）。おだやかA0で得られるCは **29／28／26／17／16／15／4／3** の8通りが全て（`2F3C902C`＝その最大C29、`55A2A319`＝C28、`C2360A0C`＝C26…）。

**流布リストの正体**（研究R5：この4行リストを載せた外部ページは英日とも見つからず、本プロジェクト内にも存在しない。以下は当方の全数計算による説明）：

| リストの個体 | 実態 | PID／origin |
|---|---|---|
| ずぶとい 31/0/31/31/31/31 | 直接経路には無い（ずぶといでC31の最小Aは12）。**再抽選1回・TSV 4941 限定** | `6D1DDD5B` @ `9243BC41` |
| おくびょう 31/0/31/31/31/31 | 同上・TSV 4941 限定（PKHeX issue #3008 の実例 TID 7／SID 39528 → 39535>>3 = 4941 がこれ） | `ED1D5D5B` @ `1243BC41` |
| おだやか 31/5/31/31/31/31 | 直接経路（おだやかでC31の最小A） | `1E98B426` @ `89491010` |
| ひかえめ 31/4/31/31/31/31 | 直接経路 | `5A134534` @ `66E00F09` |
| おくびょう 31/6/31/31/31/31 | 直接経路 | `883EC465` @ `19F0033A` |

つまりリストは「性格ごとに C31 を保ったまま A を最小にした既知個体」の寄せ集めで、**A0が不可能だという主張ではない**し、種族に依らない（3鳥どれにも同じ表が当てはまる）。PokeFinder issue #105（Sephirona、2020-06-16、開封済み）の "This pair of spreads also works for Zapdos, Moltres, and Articuno, but they are also not searchable at the moment." が、twin seed `1243BC41`/`9243BC41` の再抽選個体を指す一次証言。
**参考**：Smogon記録者のフリーザー（おくびょう・IV「6 Atk / 30 SpA」＝31/6/31/30/31/31、§7）は直接経路に存在する（PID `AEA4D752`）。

## 5. 入手ルート（ゲーム内と実機乱数調整）

**ゲーム内**（信頼度：中。Bulbapedia／Serebii／aniwota wikiはスニペットのみ、PKHeXロック定義と整合）
1. シトンダーク島の最終戦「グランドマスター・デスゴルド（Greevil）」はダブルバトルでシャドウ6体：**サイドン Lv46・ファイヤー Lv50（先発）→ ナッシー Lv46 → ケンタロス Lv46 → フリーザー Lv50 → サンダー Lv50**。PKHeXの `XArticuno` ロック順（サイドン／ファイヤー／ナッシー／ケンタロス → フリーザー）と一致。直前にシャドウルギア（XD001）戦。
2. スナッチできなかった個体は殿堂入り後にシトンダーク島で再戦可能。**再戦時は未スナッチのシャドウ＋代替の通常ポケモン**（サイドン→ライボルト、ファイヤー→オオスバメ、ナッシー→スターミー、ケンタロス→グランブル、フリーザー→チルタリス、サンダー→プテラ）。これがPKHeXの「Seen変種」の実体で、**初戦か再戦か、再戦なら誰を既に確保したかで§3の変種が決まる**。
3. リライブ：ハートゲージを0にしてアゲトビレッジのリライブの間か、ポケモンHQラボのリライブホール。リライブでシャドウ技が置き換わり、フリーザーは **じんつうりき／いやしのすず／くろいきり／れいとうビーム**（PKHeX `Encounters3XD.cs:111` Moves=(326,215,114,058)）。
4. GBAへの転送：本編クリア後、フェナスシティのポケモンセンター地下でGBAと通信交換。**リライブ済みの個体のみ**転送可。GBA側は殿堂入り済みでポケモンセンター内セーブが条件。GC–GBAケーブル使用。
5. データ上の必須フラグ：運命的な出会いON・ナショナルリボン・OT男・出会い074／Lv50・ボール（モンスターボール既定）。

**実機での乱数調整**（信頼度：中〜高。ツールのソースとREADMEは開封、日本語解説ブログはスニペットのみ）
1. デスゴルド戦直前で、§3の変種に合う状態（初戦＝先行4体未確認、または再戦で確保済みの組合せ）でレポート。目標 origin は `ECFE3E26`、初戦なら**チーム生成前のseed `D1D0AE06`** をデスゴルド戦開始時に踏むのが目標。
2. リセット→初期seedは2^32から乱択。**現在のseedを知る方法**：タイトルから「いますぐバトル→シングル→さいきょう」の確認画面に出る 自分側リーダー（ミュウツー／ミュウ／デオキシス／レックウザ／ジラーチ）・CPU側リーダー（フリーザー／サンダー／ファイヤー／ガルーラ／ラティアス）と4体のHP実数値を PokeFinder「Gen 3 Tool → GameCube → GameCube Seed Finder（Gales）」に入力し、バトルを受けずに何度か繰り返して候補を1つに絞る（PokeFinder `GalesSeedSearcher.cpp`、aldelaro5 `GaleDarknessRNGSystem.cpp`、消費は 名前1→自チーム番号→敵チーム番号→…の固定列）。
3. 目標seedまでの消費：いますぐバトルのパーティ画面待機（ファイヤー表示時 約3713.6消費/秒）、レポート＝63、「つづきをあそぶ」≈14、道具メニュー≈14、主人公の待機モーションで微調整（u1F992/XDSeedSorter README）。マップによってはNPCの瞬きやカメラで勝手に消費されるため「静かな場所」で行う。
4. 距離が遠ければリセットして2に戻る（XDSeedSorter はキャプチャボード＋Arduinoでこの厳選を自動化した実例）。
5. 戦闘開始→フリーザーをスナッチ→PKHeXか自作スクリプトでPID/IVを確認（origin `ECFE3E26`）→リライブ→転送。
**エミュ（Dolphin）の場合**：初期seedはRTC日時で決まるので RunAsDate＋Lua（Real96 `XD_RNG_Dolphin.lua`、NTSC-U 0x4E8610／JPN 0x4C5B28／PAL 0x522BF0）で現在seedと消費数を表示しながら狙う。Smogonはエミュ記録を‡付きで認める（§7）。

## 6. 色違い不可の根拠（複数独立ソース）とHaze＋色違いの不在

**A. XDのシャドウは色違いにならない**（第3世代の判定 `(TID^SID^PIDhi^PIDlo) < 8` において）
1. PokeFinder：`GameCubeGenerator.cpp:32-35` `isShiny = (high^low^tsv) < 8`、`:272-278`「Shiny lock is from TSV of savefile」でPIDペアを再抽選、`generateNonLock` `:367-374` は `Shiny::Never` の個体に同じ再抽選、フリーザーは `Shiny::Never`（encounters.json galesColo[67]）。
2. PKHeX：`EncounterShadow3XD.cs:22-24` `IsShiny => false; Shiny => Shiny.Never; // Different from Colosseum!`、`LockFinder.cs:19-21` `if (xd && pk.IsShiny) return false; // no xd shiny shadow mons`、`MethodCXD.SetRandom` の `noShiny: true`。
3. RNG Reporter（Admiral-Fish版 `GameCube.cs`／`NatureLock.cs`）：同じアンチシャイニー実装、Galesシャドウでは色違いチェックボックスを非表示。
4. aldelaro5 GC RNG assistant（実機で検証済みと明記）：`generatePokemonPID(..., WantedShininess::notShiny)`。
5. コミュニティ文書（Bulbapedia「Shadow Pokémon」、Glitch City「Shiny Shadow Pokémon glitch」、Smogon XDガイド、ニケルダーク大学「色回避」）：XDはPIDを再計算してシャドウを色違いにしない——**いずれもスニペットのみ、原文未開封**。
- 対比：コロシアムのシャドウはCPUトレーナーのTSVで判定するため「Shiny Shadow glitch」で色違いになりうる（PKHeX `Shiny.Random`）。XDでも非シャドウ（イーブイ・ポケスポット・交換・バトル山の御三家）は色違いになりうる。**「XDは色違いが出ない」ではなく「XDのシャドウは色違いにならない」**。
- スコープ：第3〜5世代の判定 xor<8。第6世代以降は xor<16 なので、第3世代産で xor が8〜15の個体は転送後に色違い表示になりうる（一般知識・中信頼度）。**第3世代のバトルフロンティア記録には無関係**。
- 前提：TID/SIDのセーブ改変をしないこと。第3世代の色違い判定はポケモンに保存されたOTのIDで行うため、交換で変わらない。

**B. くろいきり（Haze）を持つフリーザーは第3世代ではXDリライブ産のみ**
- RSE／FRLG のレベル技・全TM/HM・エメラルド教え技30／FRLG教え技15・タマゴ技（伝説なので無し）に Haze なし（pret pokeemerald／pokeruby／pokefirered 学習データ、本リポジトリ `tools/remote-audit/pokeemerald/*.h`）。XDの教え技リスト（veekun）にも無し。コロシアムにフリーザーは登場しない。
- 第3世代の配布フリーザーは 10 ANIV／10ANNIV 系（Lv70・こうそくいどう／こころのめ／れいとうビーム／リフレクター）のみで、Haze を持たず、かつ Shiny=Never（PKHeX `EncountersWC3`）。
- Pokémon Showdown の学習データはフリーザーの第3世代Hazeを イベント "3S2"（Lv50・れいB／いやしのすず／じんつうりき／くろいきり＝XDリライブ）のみとして記録し、色違いフラグなし。
- 第9世代ではHazeがTM／レベル技になるが、第3世代に戻せないので無関係。
→ **Haze ⇒ XDリライブ ⇒ 色違い不可。色違いのフリーザーはFRLG（ふたごじま）産にしかならず、それはHazeを持てない。両立する正規ルートは存在しない。**

## 7. Smogonの記録ルールと1316勝記録者のフリーザー

**現行ルール**（Gen III Battle Frontier Discussion and Records・Valentino23 が2019-03-28開始。OP原文は17章に走者が2026-07-29に貼付したものを使用、以下は原文引用）
- 証拠：*"All records require a screenshot or picture of your in-game Battle Results and all users are required to obligatory disclaim the facility that was challenged, the level it was challenged for (Lv. 50 or Open Level) and whether the streak was done on retail or emulator."*
- 個体：*"All submissions must include the exact stats or IVs of any Pokemon being used."*（Gen 3で違法なスプレッドのgenned／hacked個体を弾くための追加チェック、と説明）
- genned：*"You are allowed to use genned Pokemon so long as they have legally obtainable stats and moves. Streaks using illegal Pokemon will not be leaderboard eligible."*（過去の文言「genned or hacked Pokemon will not be allowed」から明文で緩和）
- 乱数調整：自分の個体のIV／実数値を狙う乱数調整は "fully allowed"、相手側・施設側の操作は禁止。
- エミュ：*"Records on emulators are eligible as well as any Pokemon obtained from an emulator... having concrete proof such as recorded videos or detailed write-ups is heavily encouraged. I reserve myself the right to ask for any additional recorded footage if I do not trust your streak enough..."*（‡表記。改造ROM・海賊版・セーブステート／セーブ復元による負け回避は禁止）。管理者は「十分に疑わしい記録は確証がなくても却下できる」。
- **PID／TID／SIDの提出は一切求められていない**。セーブデータの提出要件も見つからず。
- XD固有（スニペット）：リライブ技（Haze／いやしのすず／じんつうりき）はXDで実際に入手した個体にのみ合法。バトルパイクの技復元グリッチでFRLG産フリーザーにリライブ技を持たせるのは不可（「XD個体は性格ロックがあり5V以上にできないので、正規にXDを乱数した人に対して不公平」との理由——**3鳥については事実誤認**：§1・§4の通り性格ロックはなく5Vも可能）。既存のXD個体の消したリライブ技を復元するのは可。

**Battle Tower Doubles Open Level（Lv100）リーダーボード**（検索スニペット、17章と整合）
| 順位 | 名前 | 連勝 | 構築 | 備考 |
|---|---|---|---|---|
| 1 | **Jheisinho** | **1316‡**（エミュ） | ラティオス／ケンタロス／ラグラージ／フリーザー | [paste]＋[video]リンクあり。Lv50部門も1001‡で1位（同一チーム）、ドームダブル200‡ |
| 2 | An Urban Skier | 318 | ハリテヤマ／ラティオス／ギャラドス／ガラガラ | |
| 3 | waffles101 | 252* | ラティオス／ラグラージ／メタグロス／ファイヤー | |

**Jheisinhoのフリーザー**（スレッド82ページの投稿、"streamed back in September"）：
`Articuno @ Cheri Berry / Pressure / Level: 50 / EVs: 4 Def / 248 SpA / 4 SpD / 252 Spe / Timid / IVs: 6 Atk / 30 SpA / Protect / Haze / Ice Beam / Hidden Power [Grass]`
＝ IV 31/6/31/30/31/31 と読める（§4の通り直接経路に存在）。**XD産である旨の説明・PID／TID／SID・乱数検証の投稿はいずれも見つからず**（当該投稿がLv50の1001とオープンの1316のどちらの構築かも未確定＝importableが "Level: 50"）。
→ **「Smogonに掲載されている」＝「XD RNGまで数学的に検証されている」ではない。** 記録者に求められたのはIV開示と映像であり、来歴の証明ではない。

## 8. 証明力の比較（5段階）

| 段階 | 内容 | 生成可能性の証明 | 「実際に入手した」証明 | Smogon申請での強さ |
|---|---|---|---|---|
| A | PKHeX Legalのみ | ★★☆☆☆（PID/IV相関のみ。ロック連鎖は見ていない） | ★☆☆☆☆ | ★★★☆☆（ルール上はIV開示で足りる） |
| B | A＋PokeFinder（またはRNG Reporter）でXD RNGから生成可能と確認 | ★★★☆☆（独立実装で同seed到達） | ★☆☆☆☆ | ★★★☆☆ |
| C | B＋TID/SID/PID/IV/性格/出会いデータの完全記録 | ★★★★☆（再現に必要な入力が揃う。TSV≠6114等の条件を明示できる） | ★☆☆☆☆ | ★★★★☆（「exact stats or IVs」を超える） |
| **D** | C＋origin seed・フレーム表・ロック連鎖・全数証明・検証スクリプト（＝本章） | ★★★★★（第三者が1秒で再現できる） | ★★☆☆☆（入手の証明にはならない） | ★★★★★（管理者が追加証拠を求めた場合に即応できる） |
| E | D＋実機XDでの厳選〜スナッチ〜転送の録画 | ★★★★★ | ★★★★★ | ★★★★★（エミュ‡ではなく実機表記になる） |

**A〜Dは全て「生成可能性」の証明であって「入手」の証明ではない。** Smogonは後者を要求していない（genned明文許可）。Eだけが「実際に入手した」を示す。

## 9. 保存チェックリスト

**【最低限保存】**（ルール上の必須＋本章の核心）
- [ ] Battle Results 画面のスクショ／写真、施設・Lv区分・実機／エミュの申告
- [ ] チームのimportable（4体の性格・持ち物・技・EV）＋**4体全員の実数値かIV**（フリーザー：31/0/31/29/31/31・おだやか・HP380/A157/B288/C224/D331/S207）
- [ ] フリーザーの **PID `2F3C902C`・TID・SID（TSV≠6114であること）・出会い074／Lv50・運命的な出会いON・ナショナルリボン**
- [ ] PKHeX の正規判定レポート（Legal・PIDType CXD・Origin Seed `ECFE3E26`）のスクショ

**【強く推奨】**（管理者が追加証拠を求めたときに出すもの）
- [ ] 本章（26章）と `tools/remote-audit/xd_articuno_verify.py` の実行ログ（39/39 PASS）——第三者が再現できる形
- [ ] PokeFinder の Generator（Gales・Non Shadow Locks・Articuno・Profile TID/SID）で seed `ECFE3E26` advance 0 が同個体を返すスクショ、または Searcher（IV 31/0/31/29/31/31・おだやか）が seed `ECFE3E26` を返すスクショ（配布版に3鳥が無ければ master ビルドかRNG Reporter "Colosseum\XD" で代替）
- [ ] §4の全数証明（おだやかA0はC29が上限）の要約——「非標準スプレッドをなぜ選んだか」を問われたときの回答
- [ ] 連勝の動画または詳細write-up（ルールが "heavily encouraged"）

**【可能なら保存】**
- [ ] 実機XDでの初期seed厳選（いますぐバトル確認画面）からスナッチ・リライブ・GBA転送までの録画（段階E）
- [ ] グリーンビル戦の状態（初戦か再戦か・確保済みシャドウ）と対応する§3の変種、チーム生成前のseed（初戦なら `D1D0AE06`）
- [ ] Dolphin使用時のLuaログ（初期seed・消費数）
- [ ] 本ドシエで開封できなかった一次資料（Bulbapedia／Smogon XDガイド／ニケルダーク大学）の該当箇所を人手で開いて原文を確認したメモ

## 10. 未解決・要人手確認

- PokeFinder配布版（4.3.0）の静的リストに3鳥が含まれるか（masterのサブモジュール fb7414de には含まれる）。
- 実機XDの Greevil 戦のフレーム配置（未確認7／確認済5・仮PID2）は PokeFinder／PKHeX／aldelaro5 のモデル一致に基づく。逆アセンブルまたはDolphin RAMトレースで確認すればハードウェア級になる（`scratchpad/xd_lua.lua` が出発点）。
- アンチシャイニーの照合相手がプレイヤーTSVのみか、CPU TSVも含むか（§1）。
- Smogon本文（OP・82ページ・[paste]の中身）の直接閲覧。Jheisinhoの投稿がどちらの部門の構築か。
- Bulbapedia／Glitch City／Smogon XDガイド等のスニペット引用の原文確認。

## 11. 出典

**ローカル（開封・行番号付き）**
- PokeFinder（Admiral-Fish、master ecf97624 2026-09-06）：`Core/RNG/LCRNG.hpp:250-253,296-297`、`Core/Gen3/Generators/GameCubeGenerator.cpp:32-35,215-298,361-385`、`Core/Gen3/Searchers/GameCubeSearcher.cpp:372-378,389-419`、`Core/Gen3/Searchers/GalesSeedSearcher.cpp:24-235`、`Core/Gen3/ShadowLock.hpp:34-35,47-48,61`、`Core/Gen3/LockInfo.hpp:120-163`、`Test/Gen3/gamecube.json`
- EncounterTableGenerator `Gen3/encounters.json` @fb7414de（galesColo[67] Articuno Shiny::Never）
- PKHeX.Core（master e0e63bc8）：`Legality/RNG/Algorithms/XDRNG.cs:23-26`、`Legality/RNG/MethodFinder.cs:254-300`、`Legality/RNG/CXD/MethodCXD.cs:37,428`、`Legality/RNG/CXD/LockFinder.cs:17-27`、`Legality/RNG/CXD/TeamLockResult.cs:139,194,229-268`、`Legality/RNG/CXD/NPCLock.cs:14,37`、`Legality/Encounters/Data/Gen3/Encounters3XD.cs:111`、`Encounters3XDShadow.cs:825-935`、`Legality/Encounters/Templates/Gen3/XD/EncounterShadow3XD.cs:22-24,83-89,145`、`Legality/RNG/Util/ShinyUtil.cs:40`
- RNG Reporter：Slashmolder 9.96.6A3 `RNGReporter/MainForm.cs:107`、`Objects/IVtoSeed.cs:33-96`、`Objects/FrameGenerator.cs:1102-1180`、`TimeFinder3rd.cs:954-959`；Admiral-Fish版 `GameCube.cs:206-330,1295-1330`、`NatureLock.cs:64,219-243`
- pokeemerald：`tools/remote-audit/pokeemerald/test_level_up_learnsets.h`、`tmhm_learnsets.h`、`tutor_learnsets.h`
- 本リポジトリ：`tools/remote-audit/xd_articuno_verify.py`、16章、17章（Smogon OP原文貼付）、25章§8

**Web（開封済み）**
- https://github.com/Admiral-Fish/PokeFinder/issues/105 （Sephirona 2020-06-16：3鳥は検索不可・twin seed 1243BC41/9243BC41）
- https://github.com/Admiral-Fish/PokeFinder/issues/130 、https://github.com/Admiral-Fish/PokeFinder/releases?q=Gales （2.4.0 Seed Finder／2.5.4 生成精度／4.3.0）
- https://github.com/Admiral-Fish/EncounterTableGenerator/commits/master/Gen3/encounters.json
- https://github.com/aldelaro5/GC-pokemon-RNG-manipulation-assistant （README・`Source/PokemonRNGSystem/XD/GaleDarknessRNGSystem.cpp/.h`・`BaseRNGSystem.cpp`・`Common/Common.h`・SeedFinder wizard）、https://gist.github.com/aldelaro5/05abc560c550a18e609584b974b686dc
- https://github.com/zaksabeast/PokemonRNGGuides （`guides/Gamecube/Initial Seed RNG.mdx` ほか；公開先 pokemonrng.com は遮断）
- https://github.com/u1F992/XDSeedSorter （README・PokemonXDRNGLibrary README）、https://github.com/FishamanP/PokeGC-TIDTool
- https://github.com/Real96/PokeLua （`Gen 3/Dolphin/XD_RNG_Dolphin.lua`）
- https://github.com/TuxSH/PkmGCTools/wiki/A-guide-on-how-to-make-legal-Colosseum-or-XD-Pokémon
- https://github.com/kwsch/PKHeX/issues/3008 （アンチシャイニー実例 TID 7／SID 39528）
- Pokémon Showdown 学習データ（フリーザー "3S2"）

**Web（スニペットのみ・原文未開封）**
- https://www.smogon.com/forums/threads/gen-iii-battle-frontier-discussion-and-records.3648697/ （OP・p.82）、https://www.smogon.com/ingame/guides/xd_guide 、https://www.smogon.com/forums/threads/past-gen-rng-research.61090/page-33
- https://bulbapedia.bulbagarden.net/wiki/Shadow_Pokémon 、…/Purification 、…/Purify_Chamber 、…/Walkthrough:Pokémon_XD/Part_8 、…/Articuno_(Pokémon)/Generation_III_learnset
- https://glitchcity.wiki/wiki/Shiny_Shadow_Pokémon_glitch 、https://www.serebii.net/xd/multiplayer.shtml 、https://w.atwiki.jp/aniwotawiki/pages/24249.html 、https://hope3gen.hatenablog.com/entry/2023/12/07/234846 ほか
