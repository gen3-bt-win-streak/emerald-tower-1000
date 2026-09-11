# 27. Smogon投稿（PKHeX再現個体のleaderboard eligibility）【2026-09-10 決着：質問投稿は不要】

> **結論**：本プロジェクトの個体準備方法（PokeFinderでゲーム内RNGの実在フレームを特定 → 同一データをPKHeXで作成、技は正規習得のみ）は、**現行ルールと現行運用の両方で leaderboard eligible**。管理者が2026-05-03に明示回答済みなので、当初予定していた「可否を問う質問投稿」は出さない。提出時のwrite-upに個体準備方法を1段落書けば足りる（§2）。
> **根拠**：17章§1（OP原文）・§1.8、26章§6.1、GPT回答A/C（`tools/smogon/gpt-answer-A-smogon-thread.md`, `gpt-answer-C-reverification.md`）。

## 0. 決着の経緯（時系列）

| 日付 | 誰が・どこで | 内容 | 出典 |
|---|---|---|---|
| 2024-12-22 | ZucchiniBread #1890 (p.76) | 過去のLv50ダブル378連勝（PKHeX個体使用と本人が明記）を掲載できるか質問 | 回答C |
| 2024-12-23 | Adedede #1891 (p.76) | 「The issue that makes your streak not eligible is your team using PkHex'd Pokemon」「当時のルールではgenned個体の提出は無効」「将来generated個体を認める場合でも legal IVs / in-game obtainable を要求する」 | 回答A/C |
| 2026-02-24 | sbeven #2074 (p.83) | OPに「Streaks using genned or hacked Pokemon will not be allowed」と「genned可」が併存している矛盾を指摘。Bank of HoennのPKHeXファイル、PokeFinderでコロシアム・スイクンの合法PID/advanceを示せば可か、と質問 | 回答C |
| 2026-04-06 | Jeez Louise #2107 (p.85) | チーム全員をPKHeXで生成したと明記し、PKHeX産が合法かRNG調整が必要かを質問 | 回答C |
| **2026-05-04** | **Valentino23 #2117 (p.85)** | **「2) There have been questions if genned Pokemon are allowed. The answer is yes, but they *must* have legal moves and IV combinations, etc. It is your responsibility to ensure you do not have any illegal IV spreads for a given Pokemon. I always recommend rnging your pokemon, but I understand not everyone is able to do so.」** 3) 盗みグリッチは非合法な技/IVにならなければ可。**4) 「I am planning to retire as leaderboard manager by the end of this year … By the end of the year if everything is sorted, I'll announce who is taking over.」** | **走者のスクリーンショット（原文）**＋回答C |
| 2026-05-03 | Jeez Louise #2119 (p.85) | 非合法な6Vせっかちラティオス／スイクンをやめ、**PokeFinderで合法スプレッドを探してPKHeXで作り直し、新しいストリークをやる**と宣言 | 回答C |
| 2026-05-10 | Valentino23 #2122 (p.85) | RS盗みグリッチ産も「合法IV/技のgenned個体と同じ扱い」、ルールを更新すると予告 | 回答C |
| 2026-06-16 | OP最終編集 | 現行OP：「You are allowed to use genned Pokemon so long as they have legally obtainable stats and moves.」（gennedを含む文はこの1文のみ）＋「It is your responsibility to ensure your Pokemon is possible to obtain.」（Roamer Glitching説明の末尾） | 回答A/C |

**読み方**：2024年末の「PKHeX産は不可」は、2026-05-03の管理者回答で明示的に覆り、OPも6月に整理された。#2119 は「PokeFinderで実在スプレッドを確認してからPKHeXで作る」というまさに本プロジェクトの手順が、管理者の目の前で通った実例。

**管理者が求めているもの**：合法な技と、ゲーム内で生成され得るIV／性格の組であることを、**使用者本人の責任で**確認すること。PID／seedの提出、実入手、動画は要求されていない（エミュ記録は動画・write-upが「強く推奨」、管理者は追加映像を要求できる：17章§1.4）。

**期限に関わる注意**：Valentino23 は同じ投稿で **2026年末までに管理者を退き、後任を年末に発表**すると明言している。後任の方針は未知なので、**提出は現管理者の在任中（2026年内）が安全**。提出物にOPと#2117のスクリーンショット（走者が2026-09-10に取得）を含め、後任による再審査に備える。

**本プロジェクトの水準**：全個体についてPokeFinderの実在フレーム（Method 1／孵化／XDRNG）を特定し、PKHeX Legal、フリーザーは独立ポート（`tools/remote-audit/xd_articuno_verify.py`、42/42 PASS）でも確認済み。要求水準を大幅に超える。

## 1. 提出時に残る確認（1回だけ）

- [x] p.85 #2117 は走者がスクリーンショットで原文確認済み（2026-09-10）。提出直前にOP（p.1）の文言と「Last edited」を一度目視し、スクショを保存する。
- [ ] Battle Results 画面のスクショ、実機／エミュの申告、チームのimportable、全個体のIV（16章§4の確定表）を用意（17章§9チェックリスト）。
- [x] 公開リポジトリ https://github.com/gen3-bt-win-streak/emerald-tower-1000 を2026-09-11に公開（write-up段落にリンクを入れた）。提出前に最新の研究を反映させる（ワークフロー `publish-public-mirror` を起動）。
- [ ] 提出スクショは**Battle Results画面だけ**にする。走者のセーブは所持金が上限の999,999（2026-09-10確認）で、ルール上は無関係（審査対象はポケモンの合法性とステート／セーブ復元の不使用のみ）だが、セーブ編集の痕跡に見えるのでトレーナーカード等お金が写る画面は出さない。

## 2. 提出write-upに入れる「個体準備」段落（英語・そのまま使用可）

> **How the Pokémon were prepared.** All four Pokémon were created in PKHeX, following the current rule that genned Pokémon are allowed as long as they have legally obtainable stats and moves. Before creating each one I used PokeFinder to find a PID / IV / nature combination that the in-game Gen 3 RNG actually produces, and I recorded the seed and frame: Method 1 for the Southern Island Latios, egg frames for the bred Metagross and Snorlax, and XDRNG for the Articuno, which is an XD Shadow Articuno with its purify move Haze, not a Battle Pike glitch Articuno. Its spread is Calm 31/0/31/29/31/31, PID 0x2F3C902C, XDRNG origin seed 0xECFE3E26. All moves are level-up, TM/HM, tutor or XD purify moves. PKHeX reports every Pokémon as legal, and for the Articuno I also verified the XDRNG derivation with an independent script. PIDs, seeds and PokeFinder screenshots for every Pokémon are available on request. All calculations, the simulator, the play rules and a dated verification log are public at https://github.com/gen3-bt-win-streak/emerald-tower-1000 (English entry point: README_EN.md; the Articuno provenance dossier is 26-articuno-provenance.md and the verifier is tools/remote-audit/xd_articuno_verify.py).

（来歴は16章§4の確定表のとおり：ラティオス＝みなみのことう Method 1、メタグロス＝タマゴ産、カビゴン＝タマゴ産 PID `7D72445B`（24章§11）、フリーザー＝XD `2F3C902C`。2026-09-11 訂正：前版の「カビゴンは16章に未記載」は誤り。）

## 3. 付録：出さなかった質問投稿（2026-09-10 午前版、参考）

回答Cで #2117 が見つかる前に用意した質問文。**投稿しない**が、将来ルールが再度変わった場合の雛形として残す。

> **Title**: Eligibility of PKHeX-recreated Pokémon whose PID/IVs are verified against the in-game RNG
>
> Hi everyone, first post here. English isn't my first language, so apologies if anything is unclear.
>
> I've been running Battle Tower Doubles, Open Level, on Delta Emulator (iOS, unmodified ROM, no save states). My personal best is 613 wins (not submitted). Before my next serious attempt I'd like to make sure my Pokémon are eligible.
>
> I've read the OP, which currently says: "You are allowed to use genned Pokemon so long as they have legally obtainable stats and moves." However, I also found a reply from December 2024 (page 76) saying that a team using PKHeX'd Pokémon was not eligible, and a question from February 2026 (page 83) about PKHeX Pokémon verified with PokeFinder. So I'd like to confirm whether the current OP wording supersedes that 2024 ruling.
>
> Here is exactly what I do. First I use PokeFinder to find a PID / IV / nature combination that the in-game Gen 3 RNG actually produces (Method 1 for stationary encounters, XDRNG for XD), and I identify the seed/frame. Then I create the same data in PKHeX. For example, my Articuno is an XD Shadow Articuno (Haze is a purify move) using a PID/IV pair that the XD RNG really outputs (Calm, 31/0/31/29/31/31), not a Battle Pike glitch Articuno.
>
> My questions:
> 1. Under the current genned-Pokémon rule, is a Pokémon recreated in PKHeX with a PID/IV/nature that is verifiably produced by the in-game RNG leaderboard eligible?
> 2. Is there any difference in treatment between Pokémon actually obtained by RNG abuse (like the Bank of Hoenn ones) and Pokémon recreated in PKHeX?
> 3. When submitting, besides the required importable and IVs, is there anything else you'd like to see (PID, seed, PokeFinder results)?
>
> I can also provide recordings on request. Thanks in advance.

## 4. 回答別の分岐（将来ルールが変わった場合のみ）

| 状況 | 対応 |
|---|---|
| 現行どおり（genned可、合法IV/技） | 26章§8のチェックリストどおり証拠を添付して提出 |
| 「PKHeX産は不可、実際に入手した個体のみ」に戻った | 26章§7のD段階（Dolphin＋Luaで実際に生成・録画）へ移行。フリーザーは26章§4.2の手順、目標seedは§2.3の変種のいずれか |
| 「実機入手のみ」 | 26章§7のE段階。現実的でない場合は「記録は出すが掲載申請はしない」 |
