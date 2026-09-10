# 27. Smogon投稿文（PKHeX再現個体のleaderboard eligibility確認）【2026-09-10】

> **目的**：Gen III Battle Frontier Discussion and Records（thread 3648697）に、本プロジェクトの個体準備方法（PokeFinderでゲーム内RNGの実在フレームを特定 → 同一データをPKHeXで作成）が現行ルールで leaderboard eligible かを確認する投稿を出す。日本語版でレビュー → 英語版をそのまま投稿。
> **前提の根拠**：17章§1（OP原文）・§1.8（2026-09-10 GPT抽出）・26章§6。**投稿前に走者が下記「目視確認3点」を済ませること**。

## 0. 前提（2026-09-10 時点で分かっていること）

| 事実 | 出典 | 確度 |
|---|---|---|
| OP（最終編集 2026-06-16）は「You are allowed to use genned Pokemon so long as they have legally obtainable stats and moves.」 | 17章§1.1（走者コピー）＋GPT | 高 |
| OPに「It is your responsibility to ensure your Pokemon is possible to obtain.」がある | GPTのみ（走者コピーには無い） | 中・**要目視** |
| 2024-12-23 Adedede（p.76 #1891）「The issue that makes your streak not eligible is your team using PkHex'd Pokemon」「At the moment, the rules are the same: no submission with genned Pokemon is valid for the board.」 | GPT | 中・**要目視** |
| 2026-02-24 sbeven（p.83 #2074）がPokeFinder検証済みPKHeX個体の可否を質問、回答は見つからず | GPT | 中・**要目視** |
| Bank of Hoenn の配布個体は「All these Pokemon have been RNG abused on emulators」 | GPT（Kommo-o p.35 #851） | 中 |
| XD条項「Recover a deleted purify move. Your Pokemon must be a legal Pokemon obtained from Pokemon XD Gale of Darkness.」 | GPT（OP） | 中 |

**投稿の設計**：
1. OPを読んだことを示す（gennedの文言を引用）。
2. 2024-12の管理者回答と2026-02の未回答質問に触れ、**「現行OPの文言が2024年回答を上書きしているか」**を直接問う。これが本当の争点で、これを避けると「OPを読め」か「PKHeXは不可」のどちらかで終わる。
3. 自分の方法を1段落で正確に説明する（PKHeXのLegal判定に頼っているのではなく、RNGの実在フレームを先に特定していること。フリーザーはXDシャドウ産のPID/IVで、Pikeグリッチではないこと）。
4. Bank of Hoenn（エミュで実際に乱数調整した.pk）との差を自分から明示し、その差が扱いを分けるかを問う。
5. 提出できる情報（PID／seed／方式／PokeFinder結果／録画）を列挙する。
6. 短く、質問は3つまで。

## 1. 目視確認3点（投稿前・走者がブラウザで）

- [ ] **p.1 OP**：gennedの文言が上表どおりか。「It is your responsibility to ensure your Pokemon is possible to obtain.」があるか。「Last edited」の日付。
- [ ] **p.76 #1891（Adedede, 2024-12-23）**：引用2文が本当にあるか。**無ければ投稿文の第3段落を削る**。
- [ ] **p.83 #2074（sbeven, 2026-02-24）**：質問の内容と、その後に管理者回答が付いていないか（付いていれば**その回答が答えそのもの**なので、投稿の必要性を再検討）。

## 2. 日本語版（レビュー用）

> **タイトル案**：Eligibility of PKHeX-recreated Pokémon whose PID/IVs are verified against the in-game RNG
>
> こんにちは。初めて投稿します。英語が母語ではないので、分かりにくい部分があればすみません。
>
> Delta Emulator（iOS、無改変ROM、セーブステート不使用）でBattle Tower Doubles Open Levelに挑戦しています。自己ベストは613勝（未提出）で、次の本格的な挑戦の前に、使用個体の扱いを確認させてください。
>
> OPは「You are allowed to use genned Pokemon so long as they have legally obtainable stats and moves.」と書いていると読みました。一方で、2024年12月の回答（p.76）に「PKHeX'd Pokemonを使ったチームはeligibleでない／genned個体の提出は無効」とあり、2026年2月（p.83）にはPokeFinderで検証したPKHeX個体について同じ趣旨の質問があって、回答が見つけられませんでした。現行OPの文言がこの2024年の回答を上書きしているのか、それとも今も「PKHeXで作った個体は不可」なのかを確認したいです。
>
> 私の方法は次のとおりです。まずPokeFinderで、Gen 3のゲーム内RNG（固定シンボルはMethod 1、XDはXDRNG）が実際に出力する PID／IV／性格 の組を探し、そのseed（フレーム）を特定します。そのうえで、同じデータをPKHeXで作成しています。PKHeXのLegal判定だけを根拠にしているのではなく、各個体について「どのゲームの、どのseedから生成されるか」を示せます。例えばフリーザーはXDのシャドウフリーザー（くろいきりはリライブ技）として、XDRNGが実際に出力するPID/IVの組（おだやか、31/0/31/29/31/31）を使っており、Pikeグリッチによるものではありません。
>
> Bank of Hoennの個体は「エミュ上で実際にRNG abuseして入手した.pk」と理解しています。私の個体は「RNGで生成されることを確認したうえでPKHeXで再現したもの」なので、実際にゲーム内で入手したかどうかだけが違います。
>
> 確認したいこと：
> 1. 現行OPのgenned条項に照らして、「ゲーム内RNGで生成されることを示せる個体をPKHeXで再現したもの」はleaderboard eligibleという理解で合っていますか。それとも2024年12月の回答のとおり、PKHeXで作った個体は今も不可ですか。
> 2. eligibleの場合、Bank of Hoennのように実際にRNG abuseで入手した個体と、PKHeXで再現した個体で扱いに差はありますか（実際にゲーム内で入手したことまで求められますか）。
> 3. 提出時には、必須のimportableとIVに加えて、各個体のPID・seed・生成方式・PokeFinderの検索結果を添えられます。ほかにあった方がよい情報があれば教えてください。
>
> 要請があれば録画も提出します。よろしくお願いします。

## 3. 英語版（投稿用）

> **Title**: Eligibility of PKHeX-recreated Pokémon whose PID/IVs are verified against the in-game RNG
>
> Hi everyone, first post here. English isn't my first language, so apologies if anything is unclear.
>
> I've been running Battle Tower Doubles, Open Level, on Delta Emulator (iOS, unmodified ROM, no save states). My personal best is 613 wins (not submitted). Before my next serious attempt I'd like to make sure my Pokémon are eligible.
>
> I've read the OP, which currently says: "You are allowed to use genned Pokemon so long as they have legally obtainable stats and moves." However, I also found a reply from December 2024 (page 76) saying that a team using PKHeX'd Pokémon was not eligible and that no submission with genned Pokémon was valid for the board, and a question from February 2026 (page 83) about PKHeX Pokémon verified with PokeFinder that I couldn't find an answer to. So I'd like to confirm whether the current OP wording supersedes that 2024 ruling, or whether PKHeX-made Pokémon are still not allowed.
>
> Here is exactly what I do. First I use PokeFinder to find a PID / IV / nature combination that the in-game Gen 3 RNG actually produces (Method 1 for stationary encounters, XDRNG for XD), and I identify the seed/frame. Then I create the same data in PKHeX. I'm not relying on PKHeX's legality check alone: for every Pokémon I can show which game and which seed generates it. For example, my Articuno is an XD Shadow Articuno (Haze is a purify move) using a PID/IV pair that the XD RNG really outputs (Calm, 31/0/31/29/31/31), not a Battle Pike glitch Articuno.
>
> My understanding is that the Bank of Hoenn Pokémon were actually RNG abused on emulators and then shared as .pk files. Mine are recreated in PKHeX after confirming the RNG produces them, so the only difference is whether the Pokémon was actually obtained in-game.
>
> My questions:
> 1. Under the current genned-Pokémon rule, is a Pokémon recreated in PKHeX with a PID/IV/nature that is verifiably produced by the in-game RNG leaderboard eligible? Or, as in the December 2024 reply, are PKHeX-made Pokémon still not allowed?
> 2. If they are eligible, is there any difference in treatment between Pokémon actually obtained by RNG abuse (like the Bank of Hoenn ones) and Pokémon recreated in PKHeX? In other words, is actually obtaining them in-game required?
> 3. When submitting, besides the required importable and IVs, I can include each Pokémon's PID, seed, generation method and the PokeFinder search results. Is there anything else you'd like to see?
>
> I can also provide recordings on request. Thanks in advance.

## 4. 投稿後の分岐

| 回答 | 対応 |
|---|---|
| 「現行OPのとおりgenned可、RNG検証は不要」 | 17章§8「掲載可能性：高い」を運用ベースでも確定。提出時は26章§8のチェックリストどおり証拠を添付 |
| 「PKHeX産は不可、実際に入手した個体のみ」 | 26章§7のD段階（Dolphin＋Luaで実際に生成・録画）へ移行。フリーザーは26章§4.2の手順、目標seedは§2.3の変種のいずれか。他3体も同様にエミュ上で実入手する |
| 「実機入手のみ」 | 26章§7のE段階。現実的でない場合は「記録は出すが掲載申請はしない」を選択肢として残す |
| 回答なし（2週間） | 走者がスレの常連（Adedede／Kommo-o）に直接メンションして再質問 |
