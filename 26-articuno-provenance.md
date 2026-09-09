# 26. フリーザー（XD産）の来歴証明ドシエ【2026-09-09】

> **目的**：走者が本リポジトリで生成した個体（下記・A0/C29）を**そのまま正として**、①XDの乱数から独立に生成可能であること、②実機での入手ルート、③Smogon記録申請時に何を証拠として出すか、を確定する。**理想個体の探索は目的ではない**（§2.4の「他スプレッド」は「なぜC29なのか」を問われたときの回答として置いてあるだけ）。
> **再現**：`tools/remote-audit/xd_articuno_verify.py`（自己完結・PokeFinderテストベクタ11件110状態を内蔵・39項目 ALL PASS・約1秒）。
> **調査体制**：ソース監査（PokeFinder／RNG Reporter／PKHeX）・Web技術資料・Smogon・色違い／Haze・理想個体リスト出典・ローカル計算の7系統を並列で行い、主要主張5件（色違い不可／生成可能性／PokeFinderの守備範囲／入手ルート／Smogonルール）を各3名の反証担当が独立に検証、その訂正を反映済み（C1・C2は全員confirmed、C3〜C5は部分訂正あり）。

対象個体（本書ではGROUND TRUTHとして扱う）: ポケモンXD シャドウ・フリーザー（PKHeX "XD Shadow Encounter 76"、デスゴルド@シタダーク島=Location 074、Lv50、リライブ技 じんつうりき/いやしのすず/くろいきり/れいとうビーム）、性格 おだやか、個体値 H31/A0/B31/C29/D31/S31、PID 0x2F3C902C、XDRNG origin seed 0xECFE3E26（IV1フレーム直前の状態）、PSV=(0x2F3C^0x902C)>>3=0xBF10>>3=6114、色違いではない。PKHeX判定 Legal（PIDType CXD）。

凡例: 【高】【中】【低】= 確信度。「SNIPPET」= ページ本体は閲覧不能（プロキシ遮断）で、検索結果の抜粋のみで確認した情報。

---

## 0. 結論（3行）

1. **XD RNGで生成可能か**: 可能【高】。origin 0xECFE3E26 から XDRNG（乗数 0x343FD／加算 0x269EC3）を5回進めると 0x7C1F→0xFFBF→0x5284→0x2F3C→0x902C となり、IV 31/0/31/29/31/31・PID 0x2F3C902C・おだやか・PSV 6114 が「直接経路（アンチシャイニー再抽選なし）」で一意に再現される。PKHeXとは独立の自作ポート（PokeFinderの11個のテストベクタ110状態を完全再現）で確認済み。デスゴルド先行4体のロック連鎖もPKHeX TeamLockResult移植で5変種すべて通過（ただし全員シャドウのため「通過」は自明で弱い証拠）。
2. **PokeFinder等の確認をSmogonに示せば十分か**: Smogonの現行ルール（2026-07-29時点の原文）は「正規に入手可能なステータス・技であればgenned個体も可」「IVまたは実数値の開示必須」であり、PID/TID/SID/seedの提出は求められない【高】。従って PokeFinder（Non Shadow Locks カテゴリ）＋PKHeX Legal の提示で規定上は十分。ただし PokeFinder は先行パーティ・CPUのTSV・偽PIDフレームを一切モデル化しない**部分検証**であり、「実機で入手した」ことの証明にはならない。
3. **保存すべき証拠**: (a) PKHeX Legality レポート全文（PIDType CXD, origin 0xECFE3E26 表示）、(b) PokeFinder GameCube Searcher（Non Shadow Locks／Articuno／プロフィールTID・SID）の検索結果とGenerator再生成のスクリーンショット、(c) 本リポジトリの `tools/remote-audit/xd_articuno_verify.py` の実行ログ（39/39 PASS）、(d) セーブのTID/SIDと (TID^SID)>>3≠6114 の記録、(e) 可能なら Dolphin RAMトレースまたは実機録画。詳細は§8。

---

## 1. XDシャドウ生成の仕組み（RNG・生成順・ロック連鎖・アンチシャイニー）

### 1.1 XDRNG
- 32bit LCG: `seed' = seed*0x343FD + 0x269EC3 (mod 2^32)`。逆方向は `seed*0xB9B33155 + 0xA170F641`（乗法逆元として検証済み）。各「コール」は上位16bit（`seed>>16`）を返す【高】。
  - PokeFinder `Core/RNG/LCRNG.hpp:296-297` `using XDRNG = LCRNG<0x269EC3, 0x343FD>; using XDRNGR = LCRNG<0xA170F641, 0xB9B33155>;`、`:250-253` nextUShort = next()>>16
  - PKHeX `Legality/RNG/Algorithms/XDRNG.cs:23-26`（Mult 0x000343FD / Add 0x00269EC3 / rMult 0xB9B33155 / rAdd 0xA170F641）
  - RNG Reporter `Objects/LCRNG.cs:90-104`、aldelaro5 `BaseRNGSystem.h:119-125`、Real96 `XD_RNG_Dolphin.lua` JUMP_DATA も同一定数
- 実機の初期seedは起動時に読むハードウェアtickカウンタ下位32bit（2^32全域、本体時計で設定不可）【中】。クロック周波数は資料間で矛盾（aldelaro5: 40.5 MHz/≈22ns tick、RNG Reporter `IFrameCaptureXD.cs:24-34` Seed/6,000,000、Smogon旧投稿 "~6 MHz"）— 本書では「起動時tickの下位32bit」とだけ述べる。

### 1.2 敵パーティ生成順（XD/Gales）
PokeFinder `Core/Gen3/Generators/GameCubeGenerator.cpp:215-298` generateGalesShadow、PKHeX `MethodCXD.cs:408`（"fakePID x2, IVs x2, ability, pid1*, pid2"）、`NPCLock.cs:14`（`FramesConsumed => Seen ? 5 : 7`）、aldelaro5 `GaleDarknessRNGSystem.cpp` が一致【高】:

1. 戦闘開始時 CPUトレーナーの TID/SID = 2コール（`:226 go.advance(2); // Enemy TID/SID`）
2. パーティ各メンバーについて順に:
   - 仮PID 2コール、IV1 1コール、IV2 1コール、特性 1コール（`:232-235 go.advance(5)`）
   - PID = 上位16bit + 下位16bit の2コール。**既に生成済み（"seen"）のシャドウはPIDを生成せず5コールのみ消費**（`:237-239` "We will assume it is already set and skip the PID process"）。未生成なら7コール＋再抽選分。
   - 非シャドウNPCは性格（PID%25）・性別ロックを満たすまでペアで再抽選（`:239-254`）
3. 対象シャドウ自身: 仮PID 2コール（`:265 // Fake PID`）→ IV1 → IV2 → 特性（`nextUShort(2) & (ab0!=ab1)`）→ PID上位 → PID下位（`:267-278`）
4. IV展開: HP=iv1&31, Atk=(iv1>>5)&31, Def=(iv1>>10)&31, Spe=iv2&31, SpA=(iv2>>5)&31, SpD=(iv2>>10)&31（`:380-385`、PKHeX `MethodCXD.cs:559-569` SetIVs と同一）。IVコールは15bitのみ使用。

### 1.3 アンチシャイニー（色回避）
- 判定 `isShiny(high, low, tsv) = (high ^ low ^ tsv) < 8`（`GameCubeGenerator.cpp:32-35`）。TSV = **セーブデータ（プレイヤー）の TID^SID**（`:248, :273 // Shiny lock is from TSV of savefile`、`Generator.hpp:53`）。色違いになる場合はPIDペアを丸ごと捨てて新たに2コール引き直す（XORビット反転ではない。`^0x8000` はChannelジラーチ専用 `:100-104`）【高】。
- PKHeX側: `EncounterShadow3XD.cs:24 Shiny.Never; // Different from Colosseum!`、`LockFinder.cs:19-21 if (xd && pk.IsShiny) return false; // no xd shiny shadow mons`、`MethodCXD.cs:489-508` GetPIDReuse（`while` 色違い再抽選）、`TeamLockResult.cs:15`「XDではシャドウにも非色違いを強制」。さらにPKHeXは `TeamLockResult.cs:234-255 VerifyNPC` で先行メンバーの PSV が **CPUトレーナーのTSV** と一致することも拒否する（PokeFinderはCPU TSVを一切見ない）【高】。
- 実ゲームがCPU側IDも見るかは逆アセンブルレベルで未確認。Bulbapedia/Glitch City/ポケモンWiki（SNIPPET）は「相手と自分の両方のIDで判定」と述べる。本書は「プレイヤーTSVで再抽選（全ツール一致）、PKHeX/Wiki類はNPC側TSVも」と表現する。
- コロシアムとの対比: コロシアムは**敵トレーナーのTSV**のみで判定（`:137, :159 // Shiny lock is from enemy TSV`）ためスナッチ後に色違いになり得る（Shiny Shadow glitch）。XDはこれを修正した。

### 1.4 ロック連鎖（PokeFinder / PKHeX）
- PokeFinder: `ShadowTemplate`（最大5 LockInfo + ShadowType {SingleLock, FirstShadow, Salamence, SecondShadow, EReader}）。`LockInfo(0,0,0)` は「この枠はシャドウ自身」の番兵（`LockInfo.hpp:42-43, :66`）。サーチャは `ShadowLock::{singleNL, firstShadowNormal, firstShadowSet/Unset, salamenceSet/Unset}` で逆算し、簡略化を明記: 「色違いロックは前向きにしか検査しない」（`ShadowLock.hpp:61-62`）、コロシアム/E-Reader の敵TSVは「重要でないと仮定」（`:34-35, :47-48`）、Gales EReader は未対応（`GameCubeSearcher.cpp:417 default: break;`）【高】。
- PKHeX: `Encounters3XDShadow.cs:825-832` `XArticuno = [NPCLock(112) サイドン, NPCLock(146) ファイヤー, NPCLock(103) ナッシー, NPCLock(128) ケンタロス]` + Seen変種4種（`:870-908`; `Encounters3XDTeams.cs:82`）。`NPCLock.cs:37` `if (Shadow && Nature == 0) return true;` — 全員シャドウのため性格・性別ロックは存在しない（RNG Reporter Admiral-Fish版 `NatureLock.cs:64,219` Articuno = NoLock、PokeFinder issue #105、Smogon "Greevil uses a party of 6 Shadow Pokémon, nothing is locked"(SNIPPET) と一致）【高】。
- 注意: PKHeX master (e0e63bc8) で `LockFinder.IsAllShadowLockValid` が呼ばれるのは**生成時**（`MethodCXD.cs:37, :428`）のみ。合法性判定側（`EncounterShadow3XD.cs:145`）は PIDType が CXD/CXDAnti かのみを見る。従って「PKHeX Legal」はロック連鎖の証明ではない【高】。

---

## 2. 対象個体の導出

### 2.1 前進導出（origin 0xECFE3E26）【高】
| コール | 状態 | 出力(上位16bit) | 意味 |
|---|---|---|---|
| s1 | 7C1FFC51 | 7C1F | IV1: HP31 / Atk0 / Def31 |
| s2 | FFBF2DD0 | FFBF (15bit 7FBF) | IV2: Spe31 / SpA29 / SpD31 |
| s3 | 52845553 | 5284 | 特性bit 0（フリーザーはプレッシャーのみ、マスクで0） |
| s4 | 2F3CAACA | 2F3C | PID上位 |
| s5 | 902C4665 | 902C | PID下位 |

PID 0x2F3C902C（792498220）、PID%25=20=おだやか、PSV 6114。仮PIDペア開始状態（origin の2コール前）= 0xF48AA54C。**プレイヤーの (TID^SID)>>3 が 6114 の場合のみ**再抽選が起き、次ペア s6/s7（0xE583/0x24BB）から PID 0xE58324BB（わんぱく, nature 8）になる（研究段階で挙がった 0x24BB724C（てれい）はコール7-8を取った誤り）。

### 2.2 逆算一致【高】
- PKHeX `MethodFinder.GetXDRNGMatch`（`MethodFinder.cs:254-302`）移植: `XDRNG.GetSeeds(0x2F3C0000, 0x902C0000)` → 候補は s3=52845553 の1つ（PKHeXのlag法と65536総当たりで一致）。B=Prev(s3)=FFBF2DD0（&0x7FFF=7FBF=IV2）、A=Prev(B)=7C1FFC51（=IV1）→ `PIDIV(CXD, Prev(A)=ECFE3E26)`。結果はプレイヤーTID/SIDに依存せず `[('CXD', ECFE3E26)]` のみ。CXDAnti ではない直接経路個体。
- PokeRNG（0x41C64E6D/0x6073）の Method 1/2/4 とは一致しない（PID整合状態 0x902CBA99 のIVは不一致）→ FRLGふたご島産と混同され得ない。
- RNG Reporter 9.96.6A3 の "Colosseum\XD" 法（[IV][IV][xxx][PID][PID]）で seed 0xECFE3E26 フレーム1に同一個体が出る（`FrameGenerator.cs:3797-3827` のPythonエミュレート）。

### 2.3 ロック連鎖（PKHeX TeamLockResult 移植）【高（モデル内）／中（実機一致）】
FrameCache 起点 = Prev2(ECFE3E26) = F48AA54C。未生成シャドウ7フレーム、生成済み5フレーム。

| 変種 | 先行メンバーPID（未生成のみ有意味） | CPU TID/SID | CPU-SV | チーム生成前seed |
|---|---|---|---|---|
| 全員未生成（初戦） | ケンタロス DD41F48A(PSV1337)@f0, ナッシー 97EA6075(7923)@f7, ファイヤー 82AD462B(6288)@f14, サイドン DB7D5915(4173)@f21 | 0300/8918 @f28 | 4419 | **D1D0AE06**（originの32コール前） |
| サイドン+ファイヤー生成済 | ナッシー・ケンタロス未生成 | 5BD9/766D | 1462 | **28E810AA**（28コール前） |
| +ケンタロス or +ナッシー生成済 | — | 3C29/DB7D | 7402 | **766D3474**（26コール前） |
| 4体とも生成済 | — | 5915/0602 | 3042 | **DB7D868E**（24コール前） |

D1D0AE06 から前進再生成（TID/SID 2 → 各NPC 5＋PIDペア → 偽PID 2）するとサイドン DB7D5915 / ファイヤー 82AD462B / ナッシー 97EA6075 / ケンタロス DD41F48A を再現し、ちょうど ECFE3E26 に着地する。CPU-SV はいずれも 6114 でも先行PSVでもないため、PKHeXのCPU-TSV規則でもすべて有効。
- 制約: プレイヤーTSV ≠ 6114（必須）。初戦変種を狙う場合はさらに TSV ∉ {1337, 4173, 6288, 7923}（該当NPCが再抽選され着地seedがずれる）。全8192 TSVを走査して「どの変種も無効」となるのは 6114 のみ。
- 「生成済み」変種で表示される生成済みメンバーのPIDは無意味（ゲームは生成しない）。
- 実機の偽PID/先行フレーム配置は逆アセンブル・RAMトレースでは未確認（PokeFinder・PKHeX・aldelaro5 の3実装一致に基づく）。

### 2.4 直接経路の全数証明【高】
IV1出力が HP=Def=31（Atk・bit15自由）かつ IV2出力が SpD=Spe=31 の全状態を列挙（`tools/remote-audit/xd_articuno_verify.py` §5、独立に3名が再計算し一致）:
- 総数 4692。性格別: おだやか 194、しんちょう 199、ずぶとい 195、おくびょう 174、ひかえめ 177 など。
- **おだやか A0 は8状態のみ**、SpA ∈ {29, 28, 26, 17, 16, 15, 4, 3}: C29 2F3C902C@ECFE3E26 / C28 55A2A319@1A7ABB3A / C26 C2360A0C@06F74AFC / C17 652F7B63@42E1EB5E / C16 8B958E50@705E6872 / C15 571D428A@0C18D7A9 / C4 66AA1AD4@348007CD / C3 8D102DC1@61FC84E1。
- **おだやか 31/0/31/31/31/31 は存在しない**（直接経路で0件、アンチシャイニー1回・2回でも0件、さらに全深度で不可能: 31/0/31/31/31/31 の直接4状態（てれい 2405CA1E／うっかりや 9243BC41／しんちょう A405CA1E／きまぐれ 1243BC41）の再抽選連鎖はすべて1回で非色違いに終わり、得られるのは ようき/ずぶとい/わんぱく/おくびょう のみ）。
- おだやか SpA31 は Atk ∈ {5, 11, 11, 11, 24, 29} のみ。最良: おだやか 31/5/31/31/31/31 = PID 1E98B426 @ 89491010、ひかえめ 31/4 = 5A134534 @ 66E00F09、おくびょう 31/6 = 883EC465 @ 19F0033A。ずぶとい 31/0/31/31/31/31 は直接経路に無く（ずぶとい SpA31 最小Atk=12）、アンチシャイニー1回（PID 6D1DDD5B、origin 9243BC41、**プレイヤーTSV 4941 必須** = Sephirona の TID 00007/SID 39528）でのみ存在。おくびょう 6V（908EC1FF, PID C351DEF2）は直接経路に存在する。
- 対象IV 31/0/31/29/31/31 のおだやかは直接経路1件（2F3C902C）、アンチシャイニー経路0件。

### 2.5 アンチシャイニー経路の扱い
PKHeX `MethodFinder.cs:271-301`: 最終PIDが非色違いで、直前ペアがプレイヤーTSVに対して色違いなら CXDAnti。対象個体はk=0（直接）なので CXDAnti 判定は不要。記録用には「この個体は再抽選を要さない直接CXD個体で、セーブTSV≠6114 であること」を明記する。

---

## 3. ツールで検証できる範囲と限界

| ツール | できること | できないこと |
|---|---|---|
| **PKHeX** (master e0e63bc8) | PIDType CXD/CXDAnti 判定、origin seed 表示、Shiny.Never、FatefulEncounter/ナショナルリボン、技 326/215/114/058 の照合。生成時のみ LockFinder（先行パーティ＋CPU TSV）を走らせる | 合法性判定側はロック連鎖を検査しない；記録者が使ったPKHeXビルドが master と同一かは未確認 |
| **PokeFinder** (v4.1.0以降; master ecf97624, EncounterTableGenerator fb7414de; リリース v4.3.0 はサブモジュール aae86b0 で同内容) | GameCube RNG → **Searcher カテゴリ「Non Shadow Locks」→ Articuno**（galesColo[67], Shiny::Never, Lv50）で IV→seed 検索、Generator で再生成、プロフィールTID/SID によるアンチシャイニー再抽選、Tools→GameCube Seed Finder（Gales）で実機の現在seed特定 | 「Shadow Locks」には未収録（77エントリに種144無し；全員シャドウのパーティは ShadowTemplate で表現不能）。先行4体・CPU TID/SID・偽PID・CPU TSV を一切モデル化しない**部分検証**。v4.0.1 以前はフリーザー項目自体が無い（72種ハードコード）。テストベクタは自己生成回帰データで実機採取無し |
| **RNG Reporter** 9.96.6A3 (Slashmolder) | "Colosseum\XD" 法で seed 0xECFE3E26 フレーム1に個体表示、"IVs to PID/SEED" で MonsterSeed 0xECFE3E26 | ロック・アンチシャイニー・XD/コロ区別なし；初期フレームスキップに off-by-one（`FrameGenerator.cs:3801`）；XD Capture タブは「パーティ先頭生成」前提（375,451フレーム固定）でフリーザーには不適用 |
| RNG Reporter Admiral-Fish 版 (v10.x, 2019アーカイブ) | GameCubeRNG でフリーザー（NoLock）＋anti-PID 検索 | 先行ロック未検証；未実行（C#未稼働） |
| **自作スクリプト** `tools/remote-audit/xd_articuno_verify.py`（659行, md5 b95b7db4bf2e49c19dc7104bb17adc4e） | XDRNG定数検証、PokeFinder 11ベクタ110状態完全一致、前進導出、GetXDRNGMatch 移植、TeamLockResult 移植（5変種＋前進再生成）、直接経路全数列挙、アンチシャイニー列挙 — 39/39 PASS, exit 0, 約1秒 | 実機・逆アセンブルとの照合は含まない |

テストベクタ照合結果（`Test/Gen3/gamecube.json`, Profile TID 12345/SID 54321, TSV 58376）: generateGalesShadow 6件（Ledyba SingleLock / Spheal FirstShadow / Growlithe unset・set / Salamence unset・set）＋ generateNonLock 5件（Colo Umbreon / Colo Espeon / Ageto Celebi / Gales Eevee / Gales Chikorita）を全advance一致で再現。例: Ledyba adv0 PID 2569274063 IVs [28,12,31,14,19,7]、Gales Chikorita adv0 PID 159752855 IVs [6,1,0,17,7,7]。鳥3種のベクタは存在しない。

---

## 4. 入手ルート

### 4.1 ゲーム内【高（PKHeX）／中（Wiki類はSNIPPET）】
1. シタダーク島でシャドウルギア（XD001）戦 → **直後に連戦でデスゴルド戦**（セーブ・回復不可）。デスゴルドは6体全員シャドウのダブルバトル: 先発 サイドンLv46・ファイヤーLv50、後続 ナッシーLv46・ケンタロスLv46・フリーザーLv50・サンダーLv50（PKHeX `Encounters3XD.cs:109-114`、JP wiki/Serebii SNIPPET）。
2. スナッチ（モンスターボール等）。シャドウの個体（IV/PID/性格）は**初めて場に出た時点で確定**し、負けても再戦しても変わらない（特性のみ毎回再決定）（Bulbapedia/ニケルダーク大学 SNIPPET）。戦闘後に「セーブしますか？」→「はい」でないとスナッチが成立しない（SNIPPET）。
3. リライブ: ハートゲージを0にし、アゲトの遺跡の石 または HQラボのリライブホールで浄化（XDにタイムフルートは無い）。技は じんつうりき/いやしのすず/くろいきり/れいとうビーム に置換（PKHeX 326/215/114/058、`moves_en.txt` で照合）。Fateful Encounter=true、ナショナルリボン付与（`EncounterShadow3XD.cs:26, :64-65`）。
4. GBAへ転送: エンディング後、フェナスシティ ポケモンセンター B1F でのみ通信交換。リライブ済みのみ可。GBA側は殿堂入り済み＋ポケモンセンター内でレポート、GC–GBAケーブル（GBA/GBA SP、DS不可）、対応ソフト RSE/FRLG（Serebii/Bulbapedia/任天堂 SNIPPET、複数一致だが一次ページは未閲覧）。
5. 再戦: エンディング後シタダーク島で再挑戦可。未スナッチのシャドウはそのまま、スナッチ済みは通常ポケモンに置換（サイドン→ライボルト、ファイヤー→オオスバメ、ナッシー→スターミー、ケンタロス→グランブル、フリーザー→チルタリス、サンダー→プテラ; SNIPPET）。**再戦では既に確定済みのフリーザーを狙い直せない**。

### 4.2 実機乱数調整の手順（訂正済み）【中】
研究段階の「デスゴルド戦直前でレポートし初戦（先行4体未生成）を狙う」は誤り。ルギア戦からの連戦のため直前セーブは不可能で、初戦変種（D1D0AE06）を狙うにはルギア戦を跨いで乱数を制御する必要がある（技エフェクトで大量消費、JP勢は2024年に「進化後瞬き＋カメラアングル」でファイヤー/サイドン用に達成; SNIPPET）。標準ルート:

1. ルギアをスナッチ → デスゴルド戦でサイドン・ファイヤー（必要ならナッシー・ケンタロスも）を場に出させ、**フリーザーが出る前にわざと負ける**（負けはメモリ内リスポーン＝HQラボで目覚め、「生成済み」状態が保持される; SNIPPET）→ レポート。PKHeXの "Seen" 変種はこの状態に対応し、スナッチ済み置換とは別物。サンダー用にPKHeXが "SeenRhydonMoltresArticuno" を持つことから、AIがフリーザーを早めに出す可能性に注意。
2. リセット → 初期seedは2^32一様乱数（設定不可）。
3. 現在seed特定: 英語版 VS Mode → Quick Battle → Single Battle → Ultimate（日本語版 対戦モード → いますぐバトル → コンピュータとバトル → さいきょう）。確認画面の自軍リーダー（ミュウツー/ミュウ/デオキシス/レックウザ/ジラーチ）・敵リーダー（フリーザー/サンダー/ファイヤー/ガルーラ/ラティアス）・HP4値を PokeFinder「GameCube Seed Finder → Gales」に入力（決してバトルを受けない）。複数ラウンドで1候補に絞る（`GalesSeedSearcher.cpp:24-235`、`GameCubeSeedFinder.cpp:49-54`）。JP勢は XDsearch/XDDatabase（yatsuna827）、XDSeedSorter（u1F992, キャプチャ＋Arduino自動化）。
4. 初期seed厳選: 目標（§2.3 の変種に応じた D1D0AE06 / 28E810AA / 766D3474 / DB7D868E）までの距離が許容内になるまでリセット。期待距離は2^31（3713.6/s で約6.7日）、1時間窓なら1リセットあたり約1/321、30分窓で約1/643。
5. 消費: いますぐバトル画面（ファイヤー1体表示時 3713.6/s; SNIPPETでは表示チームにより6872–7500/s）、レポート63、持ち物メニュー≈12–14（場所依存）、主人公の腰振り（微調整）。ロードからデスゴルド戦までの固定消費 = タイトルロード22 + エレベーター22 + 戦闘開始エフェクト4 = **48**（サンダー/ルギア用JPガイドの値, SNIPPET; XDSeedSorter README の 14 はプレースホルダ）。
6. 戦闘突入 → フリーザーの実数値・（ゲージ40%で判明する）性格で確認 → リライブ後 PKHeX/PokeFinder で PID/IV 確認。**1セーブにつき1回きり**。
7. セーブ側制約: (TID^SID)>>3 ≠ 6114（＝色違い回避で性格が変わるため）、選んだ変種の未生成先行メンバーPSVとも不一致。

エミュレータ（Dolphin）: RunAsDate で 2000-01-01 00:00 起動時の Origin Seed を測り、PokeFinder Gen 3 Tool → GameCube → GameCube RTC で目標seedの日時を求める（pokemonrng.com ガイド原稿, GitHub 経由で閲覧）。RAM 直読: Real96 `XD_RNG_Dolphin.lua`（NTSC-U 0x4E8610 / JPN 0x4C5B28 / PAL 0x522BF0）。

---

## 5. 色違い不可の根拠と、くろいきり＋色違いの正規ルート不在

### 5.1 XDシャドウは（第3世代判定 xor<8 で）色違いにならない【高】
独立した4系統の根拠:
1. PokeFinder: `GameCubeGenerator.cpp:32-35, :273-278, :367-374`（プレイヤーTSVで再抽選）、`GameCubeSearcher.cpp:372-378, :548-553`、`ShadowLock.cpp` 17箇所の isShiny 拒否、encounters.json galesColo[67] Articuno `Shiny::Never`。
2. PKHeX: `EncounterShadow3XD.cs:22-24`（IsShiny=>false, Shiny.Never）、`LockFinder.cs:19-26`、`TeamLockResult.cs:15, :139, :250-255`、`MethodCXD.cs:489-508`、`ShinyUtil.cs:40 GetIsShiny3 => xor < 8`。
3. RNG Reporter Admiral-Fish版 `GameCube.cs:160, :210, :455-466`（Shiny skip / Anti-Shiny、Galesシャドウで Shiny チェックボックス非表示）、aldelaro5 の `WantedShininess::notShiny`。
4. コミュニティ文書（すべてSNIPPET）: Bulbapedia「XDは色違いになる性格値を再計算する」、Glitch City「相手・自分どちらのIDでも色違いなら再生成」、Smogon Colosseum/XD Mechanics Guide「shiny-lock … rerolled until it is not shiny」、ポケモンWiki/ニケルダーク大学「色回避」。
- 自作ポート: seed 0xECFE3E26 で全65536 TSV を走査 → 再抽選は TSV 0xBF10–0xBF17 のみ、色違い出力は0件；ランダム20万試行で色違い出力0、再抽選27回（期待24.4）。
- 反証候補は成立しない: PKHeX issue #3062（PokeFinder/RNG Reporterで「色違いXDカイリュー」を計算→PKHeX Illegal）、Project Pokémon 57014/52673（回答「XDシャドウは色違い不可」）、色違いXDは shiny lock 除去ROMのみ。
- 補足: 第6世代以降は判定が xor<16 に拡大したため、xor 8–15 の個体は転送後に色違い表示され得る（一般知識【中】）。本書の主張は「第3世代（Battle Frontier記録の文脈）」に限定する。XDの非シャドウ（イーブイ、ポケスポット、ホーデル/ダッキング交換、バトル山ジョウト御三家）は色違い可だが、フリーザーは該当しない。

### 5.2 くろいきりの第3世代唯一の入手源はXDリライブ【高】
- pret pokeruby/pokeemerald/pokefirered `level_up_learnsets.h`: フリーザー = かぜおこし/こなゆき/しろいきり13/こうそくいどう25/こころのめ37/れいとうビーム49/リフレクター61/ふぶき73/ぜったいれいど85（くろいきり無し）。`tmhm_learnsets.h`・`tutor_learnsets.h` に MOVE_HAZE 0件。`egg_moves.h` にフリーザー無し。veekun XD tutor 行はダブルエッジ/ものまね/ゴッドバード/みがわり/こごえるかぜ/いばる のみ。
- Pokémon Showdown `learnsets.ts` articuno: `haze: ["9M","9L60","9S10","3S2"]`、`healbell/extrasensory: ["3S2"]`；3S2 = {gen3, Lv50, icebeam/healbell/extrasensory/haze}, shiny フラグ無し（= never shiny）。FRLG 3S0 は shiny:1 だがくろいきり無し。
- 第3世代イベントフリーザー（10 ANIV/10ANNIV/10JAHRE/10ANNI/JAA, Lv70, こうそくいどう/こころのめ/れいとうビーム/リフレクター）は PKHeX `EncountersWC3.cs:63-156` で Shiny=Never / BACD_R_A、くろいきり無し。コロシアムにフリーザーは存在しない。
- 結論: くろいきり ⇒ XDリライブ ⇒ 色回避済み。唯一色違い可能なFRLGふたご島産にはくろいきり源が無い。
- 例外（非正規／禁止）: エメラルド バトルピケの毒瀕死グリッチで スケッチ を経由すれば非XD個体に技を付け得る（Bulbapedia/Glitch City SNIPPET）。Smogonスレは「FR/LGフリーザーにXDリライブ技を真似させるPikeグリッチ」を明示禁止、PKHeXは非XDフリーザーのくろいきりをフラグする。よって表現は「非グリッチの正規ルートは存在せず、グリッチ経路も記録規定で禁止」。

---

## 6. Smogon記録ルールと1316勝記録者のフリーザー

### 6.1 現行ルール（Gen III Battle Frontier Discussion and Records, thread 3648697; 2026-07-29 のOP原文コピー `17-smogon-legitimacy.md` ＋ 2026-06 索引の検索抜粋で確認）【高（文言）／中（現在性）】
- 「Streaks using illegal Pokemon will not be leaderboard eligible. You are allowed to use genned Pokemon so long as they have legally obtainable stats and moves.」（旧文言「Streaks using hacked or genned Pokemon will not be leaderboard eligible」がスレ中盤の引用に残存、変更日は不明 → 提出時にOPを再読すること）
- 証拠: ゲーム内バトル成績画面のスクリーンショット/写真必須、施設・Lv50/Open・実機/エミュの申告必須、チームのインポータブル必須、「All submissions must include the exact stats or IVs of any Pokemon being used」（ファクトリー除く）。**PID/TID/SID/seed/セーブデータは要求されない**。
- 乱数: 自分のポケモンのIV/実数値の乱数調整は "fully allowed"。対戦相手・施設配置・ファクトリードラフトの乱数操作は禁止。
- エミュ: 記録可（‡印）、エミュで入手したポケモンも可、未改変ROMのみ、セーブステート/セーブ復元は不正。「having concrete proof such as recorded videos or detailed write-ups is heavily encouraged」「I reserve myself the right to ask for any additional recorded footage」「This is not a court of law. I reserve myself the right to reject sufficiently dubious streaks even without absolute proof of cheating.」
- ゴールドシンボル相当以上の記録には短い説明・終了経緯・写真/スクショが必要（SNIPPET）。
- XD関連: Pikeグリッチは「Recover a deleted purify move. Your Pokemon must be a legal Pokemon obtained from Pokemon XD Gale of Darkness.」に限り可、FR/LGフリーザーにリライブ技を真似させる用途は不可（SNIPPET）。スレの根拠文「Pokemon from XD are Nature Locked … most cannot be flawless or even 5 IVs」は**デスゴルドの3鳥には機構的に誤り**（性格ロック無し、おくびょう6Vが直接経路に存在）— 引用する場合は「スレの述べる理由」として扱う。
- Bank of Hoenn（p.35）: 信頼ユーザーが乱数調整したFR/LG/E/コロ/XD個体の .pk を貸与（Lego, Thomaz, Valentino23, Captain Santana, Regiultima115; SNIPPET）→ 注入済みの正規XD個体は通常の慣行。
- 運営: スレ開始 Valentino23（2019-03-28）、検証補助 Adedede/Wildcat Formation/Actaeon/wtset（SNIPPET）。Kommo-o が Valentino23 に引き継いだとの抜粋あり【中】。
- Gen IV スレ（3663294）は2022-12に「PKHeX等で作った個体も合法セットなら可」「It is ultimately your responsibility to ensure that your Pokemon have legal PID/IV combos」（SNIPPET）。Gen III OP の "It is your responsibility to ensure your Pokemon is possible to obtain" は検索で再現できず**未検証**。

### 6.2 バトルタワー ダブル リーダーボード（訂正版）【中】
- **Open Level (Lv100)**: #1 Jheisinho 1316‡（ラティオス/ケンタロス/ラグラージ/フリーザー、[paste]+[video]）、#2 Ab2658 799‡（ラティアス/ラグラージ/カビゴン/ラティオス）。研究段階の「#2 An Urban Skier 318 / #3 waffles101 252*」は**Lv50 の #2/#3**（3件の抜粋で一致; 1名は未解決扱い）。「799‡ トゲチック/ニョロボン/ラティオス/プテラ」は誤り（別チーム）。
- **Lv50**: #1 Jheisinho 1001‡（同4種、ongoing表記あり）、#2 An Urban Skier 318（ハリテヤマ/ラティオス/ギャラドス/ガラガラ）、#3 waffles101 252*（ラティオス/ラグラージ/メタグロス/ファイヤー）。バトルドーム ダブル Lv50 #1 Jheisinho 200‡（ラプラス/ガルーラ/ラティオス）。

### 6.3 Jheisinho のフリーザー公開状況【中／一部低】
- p.82 の投稿（「9月に配信した Tower Doubles ストリーク」を年末に共有）に「Articuno @ Cheri Berry / Ability: Pressure / **Level: 50** / EVs: 4 Def / 248 SpA / 4 SpD / 252 Spe / Timid / IVs: 6 Atk / 30 SpA / Protect / Haze / Ice Beam / Hidden Power [Grass]」。持ち物・性格・技は複数抜粋で確認【中】、EV/IV行は単一抜粋のみで再現不能【低】（ブラウザで要確認）。Level 50 表記のため Lv50 1001 記録の構成である可能性が高く、**1316（Open）のフリーザーIVは未確認**（[paste] は pokepast.es 遮断で未読）。
- 出自（実機XD / Dolphin / Bank of Hoenn注入）、PID/TID/SID/seed、乱数証明は**一切公開されておらず**、正当性を問う投稿も見つからない。掲載＝運営が数学的に検証した、という意味ではない（IV/実数値の開示と信頼ベースの運用）。
- 機構検証: 公開スプレッド おくびょう 31/6/31/30/31/31（めざ草70）は XD 直接経路の実在フレーム（origin 476C804E、PID AEA4D752、PSV 3902、5変種ロック連鎖有効、TSV 3902 のみ除外）。正規XD出自と**矛盾しない**が証明ではない。
- p.16 の「XD RNG が生成できる最良特殊スプレッド（ずぶとい 31/0/31/31/31/31 / おだやか 31/5 / ひかえめ 31/4 / おくびょう 31/6）」は検索で再現できず出典帰属**未検証**。ただし内容自体は§2.4の全数列挙と一致（ずぶとい31/0のみアンチシャイニー、TSV 4941）。対象のおだやか 31/0/31/29/31/31 はこのリストに無いため、「なぜ非標準スプレッドか」を問われる前提で§2の到達可能性証明を添える。

---

## 7. 証明力の比較（5段階）

| 段階 | 内容 | 証明できること | 限界 |
|---|---|---|---|
| **A** PKHeX Legal のみ | PIDType CXD、origin ECFE3E26 | IV/PID がXD相関に乗る | ロック連鎖は判定側で未検査；改造で同じ値を書ける；ビルド差 |
| **B** A + 独立ツール再現 | PokeFinder Non Shadow Locks 検索/Generator、RNG Reporter ColoXD、自作ポート（PokeFinderベクタ11件一致） | 5連続XDRNG出力であることをPKHeX非依存で確認 | 先行パーティ・CPU TSV・偽PID未検証；やはり「計算上存在する」以上ではない |
| **C** B + 連鎖・全数・セーブ整合 | TeamLockResult移植で5変種有効、直接経路全数（おだやかA0はC≤29）、セーブTID/SIDで (TID^SID)>>3≠6114 かつ先行PSV不一致、Fateful/ナショナルリボン/Met 074/OT性別・ボール整合 | 「この個体はゲームのRNGモデルで到達可能で、このセーブで生成し得た」 | モデルは3実装一致だが実機逆アセンブル未照合；入手事実の証明ではない |
| **D** C + エミュレータ実測 | Dolphin＋Lua で初期seed・消費数・デスゴルド戦突入時seed（例 28E810AA）・生成直後のRAMを記録、動画/スクショ | 実際にゲームコードが当該個体を生成した事実 | Smogon上は‡扱い；RAM値は改変可能との反論余地 |
| **E** 実機録画 | いますぐバトルでのseed特定ラウンド、消費、戦闘、リライブ、フェナスB1Fでの通信交換、GBA側での確認を通し録画（TID/SID表示含む） | 最高位。実機での入手を第三者が追跡可能 | 期待所要（2^31消費相当の厳選）が大きい；録画自体の真正性は信頼ベース |

---

## 8. 保存チェックリスト

**【最低限保存】**
- [ ] PKHeX Legality レポート全文（バージョン番号、"PIDType CXD"、origin seed ECFE3E26、Encounter "Shadow Articuno @ Citadark Isle"）とPK3ファイルのハッシュ
- [ ] 個体のインポータブル（性格・IV 31/0/31/29/31/31・技・持ち物・EV）と実数値、PID 0x2F3C902C、PSV 6114、Met 074、Fateful Encounter、ナショナルリボン
- [ ] セーブ（GBA側・XD側）の TID/SID と (TID^SID)>>3≠6114 の計算メモ
- [ ] PokeFinder バージョン（v4.1.0 以降）・プロフィール（Gales, TID/SID）・Searcher「Non Shadow Locks / Articuno / IV 31,0,31,29,31,31 / Calm」の結果画面、Generator seed ECFE3E26 advance 0 の再生成画面
- [ ] `tools/remote-audit/xd_articuno_verify.py` と実行ログ（39/39 PASS）、参照した PokeFinder/PKHeX/EncounterTableGenerator のコミットID（ecf97624 / e0e63bc8 / fb7414de）

**【強く推奨】**
- [ ] §2.3 の変種表（どの "seen" 状態で入手したか、チーム生成前seed D1D0AE06/28E810AA/766D3474/DB7D868E のいずれか）を記録
- [ ] 直接経路全数列挙の出力（おだやかA0 8件、おだやか31/0/31/31/31/31 不在）と「なぜC29か」の説明
- [ ] Smogon OP の提出時点スクリーンショット（ルール文言の日付固定）と、Jheisinho p.82 投稿の原文確認結果
- [ ] エミュ入手なら Dolphin バージョン・ROM ハッシュ・Lua ログ（Initial/Current Seed, Advances）・戦闘突入〜スナッチ〜リライブの動画
- [ ] GBA転送の記録（フェナスB1F、殿堂入り済み、GC–GBAケーブル）

**【可能なら保存】**
- [ ] 実機録画（いますぐバトル確認画面の各ラウンド、Seed Finder 入力、消費、戦闘、リライブ、交換、GBA側ステータス）
- [ ] 実機での固定消費（22+22+4）と消費速度の実測ログ、使用ツール（XDsearch/XDSeedSorter 等）の設定
- [ ] デスゴルド先行メンバーのPID（サイドン DB7D5915 等、初戦変種の場合）を後日スナッチ個体から採取して連鎖を実証
- [ ] 逆アセンブル/RAMトレースによる偽PID・先行フレーム配置の実機確認（未解決事項の解消）

---

## 9. 出典一覧

### ローカル（scratchpad = /tmp/claude-0/-home-user-daily-tasks/0c60a1ea-69b6-5e7d-8e92-741ad7c88242/scratchpad）
- PokeFinder (Admiral-Fish, ecf97624791aec147960c4f48b92ad492945b05c, 2026-09-06): `src/pokefinder/Core/RNG/LCRNG.hpp:237-253,296-297`; `Core/RNG/LCRNGReverse.cpp:296-352`; `Core/Gen3/Generators/GameCubeGenerator.cpp:32-35,100-104,126-213,215-298,300-396`; `Core/Gen3/Searchers/GameCubeSearcher.cpp:293-356,358-437,439-573`; `Core/Gen3/Searchers/GalesSeedSearcher.cpp:24-270`; `Core/Gen3/ShadowLock.cpp:25-436`; `Core/Gen3/ShadowLock.hpp:34-35,47-48,61-62`; `Core/Gen3/LockInfo.hpp:42-43,55-66`; `Core/Enum/ShadowType.hpp:30-34`; `Core/Gen3/Encounters3.cpp:229-236,310-316`; `Core/Resources/Embed/embed_gen3.py:11-31`; `Core/Resources/i18n/en/gales_en.txt`（ポケスポット名3件のみ）; `Core/Resources/i18n/en/moves_en.txt`; `Test/Gen3/gamecube.json`; `Test/Gen3/GameCubeGeneratorTest.cpp:120-238`; `Test/Gen3/GameCubeSearcherTest.cpp:160-282`; `git show HEAD:Form/Gen3/GameCube.cpp:117-323`, `GameCube.ui:84,115-125,201,246-256`, `Form/Gen3/Tools/GameCubeSeedFinder.cpp:32-153`
- EncounterTableGenerator Gen3/encounters.json @fb7414deb8412011570951731caeb0a5c834e20b: `scratchpad/et/encounters_fb7414de.json`（galesColoShadow 77件、galesColo[62-68]）; v4.3.0 のサブモジュール aae86b0 も同内容
- PKHeX (master e0e63bc87837ad2d9c8f8fda4efdbf5f2933db08): `scratchpad/pkhex_src/XDRNG.cs:23-31,130-134,300-347`; `MethodCXD.cs:15-49,396-477,489-569`; `MethodFinder.cs:254-302`; `LockFinder.cs:17-45`; `NPCLock.cs:14-15,29-38`; `TeamLock.cs:21-58`; `TeamLockResult.cs:15,51,61-66,118-124,139,176,194,229-268`; `Encounters3XD.cs:7-25,108-114`; `Encounters3XDShadow.cs:825-935`; `Encounters3XDTeams.cs:82-83`; `EncounterShadow3XD.cs:13-35,48-66,81-90,140-147`; `scratchpad/pkhex_sparse/PKHeX/PKHeX.Core/Legality/RNG/Frame/FrameCache.cs:20-46`; `.../RNG/Util/ShinyUtil.cs:40,55`; `.../RNG/PIDType.cs:81-86`; `.../Encounters/Data/Gen3/EncountersWC3.cs:63-156`; `Encounters3FRLG.cs:55`; `Templates/Gen3/EncounterStatic3.cs:20`; `Templates/Gen3/Colo/EncounterShadow3Colo.cs:24`, `EncounterGift3Colo.cs:18`, `EncounterStarter3Colo.cs:17`; `Templates/Gen3/XD/EncounterStatic3XD.cs:17`, `EncounterTrade3XD.cs:19`, `EncounterSlot3XD.cs:17`; `LearnSource/Sources/LearnSource3RS.cs:77-85`; `LearnSource/Verify/LearnVerifierHistory.cs:225-229`（注: `scratchpad/pkhex_more/ShinyUtil.cs`, `LearnSource3XD.cs` 等は0バイトの404プレースホルダ）
- RNG Reporter 9.96.6A3 (Slashmolder e9128b1, 2015-09-26): `src/rngreporter/RNGReporter/Objects/LCRNG.cs:61-104`; `Objects/FrameGenerator.cs:1096-1194,3797-3836`; `Objects/Frame.cs:175-231,813-842`; `Objects/IVtoSeed.cs:33-104,140-266`; `Objects/FrameType.cs:22-57`; `MainForm.cs:107,538-555,1316-1336`; `TimeFinder3rd.cs:835-1021`; `TimeFinder3rd.Designer.cs:3028-3173,3710,4344`; `Objects/IFrameCaptureXD.cs:24-34`; `IVtoPID_SID_SEED.resx:145`; `DonationBox.resx:121-140`。Admiral-Fish版: `scratchpad/af/GameCube.cs:160,206-300,439-468,1636-1638,2015-2034,2152-2200`; `scratchpad/af/NatureLock.cs:32-70,158-247,328-345,491-515,619-652,719-727`
- 学習データ: `scratchpad/learn/pokeemerald_level_up_learnsets.h:1994-2005`, `pokefirered_level_up_learnsets.h:2038-2049`, `pokeruby_level_up.h:2002-2013`, `*_tmhm_learnsets.h`, `*_tutor_learnsets.h`, `*_egg_moves.h`; `veekun_pokemon_moves.csv`, `veekun_version_groups.csv`; `ps_learnsets.ts`, `ps_global_types.ts:48-69`; `/home/user/daily-tasks/battle-tower/tools/remote-audit/pokeemerald/species_info.h:4353`, `pokemon.c:6740-6744`, `test_level_up_learnsets.h:1994-2005`
- 自作検証: `/home/user/daily-tasks/battle-tower/tools/remote-audit/xd_articuno_verify.py`（39/39 PASS）; `scratchpad/verify/xd_verify.py`（8 XD/Galesベクタ PASS）; `scratchpad/r5/spreads.py`; `scratchpad/c2_indep.py`, `c2_lock.py`, `c2_m1.py`, `adv_c2.py`, `adv_c4.py`, `c5/jheis.py`, `c5/sixv.py`; `scratchpad/verify_run.txt`; `scratchpad/ald_xd.cpp`, `ald_wizard.cpp`, `xdss_main.md`, `prg_Initial20Seed20RNG.m.mdx`
- リポジトリ文書: `/home/user/daily-tasks/battle-tower/17-smogon-legitimacy.md:27-74,89,115,168-173`（2026-07-29 OP原文コピー）; `18-verification-ledger.md:204`; `25-v5-articuno-build.md:845-882`; `16-pkhex-setup.md:93-141`; `sources.md:43-44,69-70`; `README.md:9-10`; `07-hardware-proof.md:40`; `10-z-axis.md:8`（旧 `26-articuno-provenance.md:90,136-138` は本書で訂正）

### Web（閲覧できたもの）
- https://github.com/Admiral-Fish/PokeFinder/issues/105 , /issues/115 , /issues/130 , /releases?q=Gales&expanded=true , /releases/tag/v4.3.0 , /tree/v4.3.0/Core/Resources , /wiki
- https://raw.githubusercontent.com/Admiral-Fish/PokeFinder/v4.0.0/Source/Forms/Gen3/GameCube.cpp , /v4.1.0/.gitmodules
- https://raw.githubusercontent.com/Admiral-Fish/EncounterTableGenerator/fb7414deb8412011570951731caeb0a5c834e20b/Gen3/encounters.json ; https://github.com/Admiral-Fish/EncounterTableGenerator/commits/master/Gen3/encounters.json
- https://github.com/Admiral-Fish/RNGReporter （README, releases, tags v10.3.1/v10.3.4）; https://raw.githubusercontent.com/Admiral-Fish/RNGReporter/master/RNGReporter/GameCube.cs , /Objects/NatureLock.cs
- https://github.com/Slashmolder/RNGReporter , /wiki
- https://github.com/kwsch/PKHeX/issues/3008 , /issues/2952 , /issues/2832 , /issues/3062 , /issues/1252 ; raw.githubusercontent.com/kwsch/PKHeX/master/PKHeX.Core/... （上記各ファイル）
- https://github.com/aldelaro5/GC-pokemon-RNG-manipulation-assistant （README, releases, Source/PokemonRNGSystem/XD/GaleDarknessRNGSystem.cpp/.h, BaseRNGSystem.h, Common/Common.h, GUI/SeedFinder/SeedFinderWizard.cpp）; https://gist.github.com/aldelaro5/05abc560c550a18e609584b974b686dc
- https://github.com/zaksabeast/PokemonRNGGuides/tree/main/guides/Gamecube （Initial Seed RNG.mdx 他）
- https://github.com/TuxSH/PkmGCTools/wiki/A-guide-on-how-to-make-legal-Colosseum-or-XD-Pok%C3%A9mon
- https://raw.githubusercontent.com/Real96/PokeLua/main/Gen%203/Dolphin/XD_RNG_Dolphin.lua
- https://github.com/u1F992/XDSeedSorter （README, PokemonXDRNGLibrary/README）; https://raw.githubusercontent.com/FishamanP/PokeGC-TIDTool/master/README.md
- https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/learnsets.ts , sim/global-types.ts ; https://raw.githubusercontent.com/veekun/pokedex/master/pokedex/data/csv/pokemon_moves.csv ; pret pokeemerald/pokefirered/pokeruby `src/data/pokemon/*.h`

### Web（SNIPPETのみ、本体は遮断: smogon.com, bulbapedia, serebii, glitchcity.wiki, projectpokemon.org, gamefaqs, hatenablog, note.com, hackmd.io, atwiki, yakkun, appmedia, nintendo.co.jp, youtube, web.archive.org, archive.ph 等）
- https://www.smogon.com/forums/threads/gen-iii-battle-frontier-discussion-and-records.3648697/ （OP, page-16, 35, 37, 52, 55, 58, 61, 64, 67, 68, 69, 73, 82）; /threads/gen-3-battle-frontier-record-thread.3478612/ ; /threads/4th-generation-battle-facilities-discussion-and-records.3663294/ ; /threads/past-gen-rng-research.61090/page-33 ; /threads/gc-research-thread-colosseum-xd.49699/ ; /threads/gp-2-2-pokemon-colosseum-and-pokemon-xd-gale-of-darkness-mechanics-guide.3638608/ ; /threads/usable-xd-pokemon.35454/ ; /threads/special-moves-in-pokemon-xd-gale-of-darkness-gp-2-2.85233/ ; /ingame/guides/xd_guide
- https://bulbapedia.bulbagarden.net/wiki/Shadow_Pok%C3%A9mon , /Purification , /Purify_Chamber , /Greevil , /Citadark_Isle , /Articuno_(Pok%C3%A9mon)/Generation_III_learnset , /Walkthrough:Pok%C3%A9mon_XD/Part_8 , /Black_out , /List_of_battle_glitches_in_Generation_III ; https://glitchcity.wiki/wiki/Shiny_Shadow_Pok%C3%A9mon_glitch , /Battle_Pike_poison_knockout_glitch
- https://www.serebii.net/xd/multiplayer.shtml ; https://forums.serebii.net/threads/official-greevil-shadow-lugia-strategy-thread.90586/ ; https://projectpokemon.org/home/forums/topic/48206-… , 57014, 52673, 62172 ; https://gamefaqs.gamespot.com/gamecube/925945-pokemon-xd-gale-of-darkness/answers/564080-… , 547451, 576665 ; https://buriedrelic.neocities.org/pages/GoD_shiny_guide
- https://aldelaro5.wordpress.com/2018/09/09/… ; https://www.pokemonrng.com/gc-initial/ ; https://www.youtube.com/watch?v=usCjKtV7Q7w , /watch?v=g2l8ooVlxwI（Gen4の可能性、無関係）
- 日本語: https://hope3gen.hatenablog.com/entry/2023/11/27/175410 , /2023/12/04/093843 , /2023/12/07/234821 , /2023/12/07/234846 , /2023/12/09/120733 ; https://note.com/sub_827/n/n001292955de8 ; https://note.com/famous_auk630/n/nf68b7c545e3a ; https://hackmd.io/@meilleur-pkmn/XDSeedSorter , /xd-initial-seed-sorter , /SkUJjU-e5 ; https://hackmd.io/@yatsuna827/H1kOxpRdI ; https://w.atwiki.jp/aniwotawiki/pages/24249.html ; https://w.atwiki.jp/p649493386251151/pages/183.html , /431.html ; https://wiki.pokemonwiki.com/wiki/ダークポケモン ; https://yakkun.com/gc/xdmemo.htm , /bbs/brain/q13523 ; https://appmedia.jp/pokemon_xd/79853744 , /79855703 ; https://ja.wikipedia.org/wiki/ポケモンXD_闇の旋風ダーク・ルギア ; https://ameblo.jp/nowtreeclimb/entry-11788640497.html ; https://otona-pokemon.blog.jp/archives/1026243272.html ; https://x.com/_3z8/status/1664679079432564741 ; https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q12191224832

---

## 10. 未解決・要人手確認（本書の限界）

- 実ゲーム（逆アセンブル／RAMトレース）での仮PID2フレーム・先行シャドウ7/5フレーム配置と、CPUトレーナーTSVによる色回避判定の有無。PokeFinder／PKHeX／aldelaro5の3実装一致に依拠。Dolphin＋Luaでデスゴルド戦のRAMを採取すれば解消できる。
- Jheisinhoの1316‡（Open Level）記録で使われたフリーザーのIV/EV。p.82の「Level: 50／IVs 6 Atk／30 SpA」は単一の検索抜粋で、Lv50 1001記録の構成である可能性が高い。[paste]とp.82本文をブラウザで要確認。出自（実機XD／Dolphin／Bank of Hoenn）は非公開。
- Smogon Gen III OPの「genned可（合法ステータス・技なら）」への変更日、現在の運営（Valentino23／Kommo-o）。2026-07-29のOP原文コピー以降の変更は提出時に再読が必要。
- p.16の「XD RNGが生成できる最良スプレッド」4行リストの出典帰属。内容は§2.4の全数列挙と一致するが投稿者・根拠ツールは未確認。
- Open Levelダブル#2/#3（An Urban Skier 318／waffles101 252）はLv50側との抜粋が3件あるが、1名の検証者は未解決扱い。
- 実機ルートの固定消費（ロード22＋エレベーター22＋戦闘開始4＝48）と消費速度（3713.6 vs 6872–7500/s）は日本語ガイドの抜粋値。対象セーブ・地域版での実測が必要。JPツール（XDsearch／XDSeedSorter）は日本語版前提。
- 初期seedのクロック周波数（40.5 MHz vs 約6 MHz）が資料間で矛盾。「起動時tickの下位32bit」以上は述べない。
- PKHeXの「サイドン＋ファイヤー＋ケンタロス生成済（ナッシー未生成）」変種が実機で到達可能か不明（送出順からナッシーが先に出る可能性が高く、PKHeXの過剰近似と推定）。
- 記録者がLegal判定に用いたPKHeXビルドが本書で監査したmaster e0e63bc8と同一かは未確認。
- Bulbapedia／Serebii／Smogon／Glitch City／日本語ブログ等の引用はすべて検索抜粋。引用前に人手でページ本文の文言を確認すること。
- 第6世代以降の色違い判定（xor<16）拡大の注記は一般知識に基づく。第3世代の記録には無関係。
