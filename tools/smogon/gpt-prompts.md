# GPT（Web閲覧あり）への調査プロンプト集【2026-09-10】

Codeの環境からは smogon.com / bulbapedia / projectpokemon / 各ブログ が遮断されているため、Web閲覧は走者経由でGPTに依頼する。
回答は下記の形式で受け取り、`battle-tower/` 配下に貼って Code が精査する。

---

## プロンプトA：Smogon Gen III Battle Frontier スレッドの一次情報抽出

```
あなたはリサーチアシスタントです。以下のSmogonスレッドを実際に開いて（ページ番号を指定して順に閲覧して）、指定した情報を「原文の逐語引用（英語のまま）」＋「ページ番号」＋「投稿のパーマリンクURL」＋「投稿者」＋「投稿日時」の形で抜き出してください。要約や意訳ではなく逐語引用が必要です。開けなかったページ・見つからなかった項目は「見つからず」と明記し、推測で埋めないでください。

対象スレッド：
https://www.smogon.com/forums/threads/gen-iii-battle-frontier-discussion-and-records.3648697/

抽出項目：

1. OP（1ページ目の最初の投稿）
   1-1. ルール部分の全文を逐語で（proof/証拠要件、genned Pokémonの扱い、RNG manipulationの扱い、emulator（‡）の扱い、save state禁止、動画・write-up、管理者の裁量に関する文、XD／purify moves／Battle Pike glitch に関する文）。
   1-2. OPの「Last edited」の日付と編集者名。
   1-3. 現在このスレッドとリーダーボードを管理している人の名前（OPに書かれていれば）。

2. リーダーボード（OPまたは2投稿目以降にある表）
   2-1. Battle Tower **Doubles Open Level（Lv100）** の上位全員：順位・名前・連勝数・‡や*の印・チーム4体・[paste]と[video]のリンク先URL（リンクのhrefをそのまま）。
   2-2. Battle Tower **Doubles Level 50** の上位全員（同じ項目）。
   2-3. 「‡」「*」の凡例の逐語引用。

3. Jheisinho の投稿
   3-1. スレッド内の Jheisinho の投稿をすべて列挙（ページ番号・日時・パーマリンク）。
   3-2. そのうち Articuno のセット（importable）が書かれている投稿は本文を逐語引用（Level / EVs / IVs / Nature / Item / Moves の行を一字一句）。
   3-3. 2-1・2-2の [paste] リンク（pokepast.es 等）を開き、Articuno のセットを逐語引用。1316の記録と1001の記録で個体が同じか違うか。
   3-4. Jheisinho が Articuno の入手方法（XD実機／エミュ／もらった／PKHeX 等）に言及している投稿があれば逐語引用。無ければ「言及なし」。

4. ルールの変遷
   4-1. 「genned Pokémon」が禁止から「legally obtainable stats and moves なら可」に変わった時期。OPの変更告知、または管理者がその変更を説明している投稿を逐語引用（ページ番号付き）。
   4-2. "It is your responsibility to ensure your Pokemon is possible to obtain" に類する文がこのスレッドに存在するか（存在すれば逐語引用、無ければ「存在せず」）。

5. 関連トピックの投稿（各件：ページ・投稿者・日時・逐語引用）
   5-1. PKHeX で作った個体／genned 個体の可否を質問した投稿と、それへの管理者・常連の回答。
   5-2. XD産（purify moves：Haze／Heal Bell／Extrasensory）の Articuno／Zapdos／Moltres の合法性について述べた投稿。特に「XD Pokemon are Nature Locked」「cannot be flawless or even 5 IVs」を含む投稿の全文。
   5-3. 「Bank of Hoenn」に関する投稿（35ページ付近）：何を配っているか、参加者名、配布個体の由来（RNG abuse で実機取得か等）。
   5-4. 「best spreads XD RNG can generate」のような、XD の性格別最良個体リストを載せた投稿（16ページ付近）：全文と投稿者。

6. 最後に、実際に開いたページ番号の一覧と、開けなかったページを列挙してください。

出力形式：Markdown。各引用は
> "…逐語…" — 投稿者, YYYY-MM-DD, page N, URL
の形で。日本語訳は不要です。
```

---

## プロンプトB：XD入手ルートの一次資料確認（Bulbapedia／Serebii／日本語ガイド）

```
あなたはリサーチアシスタントです。以下の各項目について、指定サイトの該当ページを実際に開き、該当箇所を「逐語引用（原文のまま）」＋「URL」＋「見出し／節名」で示してください。要約ではなく逐語引用が必要です。見つからなければ「見つからず」と明記し、推測で補わないでください。

A. Bulbapedia「Shadow Pokémon」ページ：
   A-1. Pokémon XD でシャドウポケモンが色違いにならない仕組み（PIDの再計算／再抽選）を説明している文。「相手のID」「自分のID」のどちらで判定すると書いているか。
   A-2. Colosseum との違い（Shiny Shadow Pokémon glitch）に触れている文。
B. Glitch City Laboratories wiki「Shiny Shadow Pokémon glitch」：色違い判定が誰のTID/SIDで行われるかを述べている文。
C. Bulbapedia「Greevil」および「Citadark Isle」／XD Walkthrough Part 8：
   C-1. デスゴルド（Greevil）の手持ち6体とレベル、送り出し順（先発2体とその後）。
   C-2. シャドウルギア戦の直後にデスゴルド戦が連戦で始まる（間にセーブできない）という記述。
   C-3. エンディング後の再戦で、スナッチ済みのシャドウが何に置き換わるか（Rhydon→?, Moltres→?, Exeggutor→?, Tauros→?, Articuno→?, Zapdos→?）。
D. Bulbapedia「Purification」「Purify Chamber」：XDでのリライブ方法（アゲトの遺跡の石／リライブホール）と、リライブ時に技が置き換わる記述。Articuno のリライブ後の技4つ（Extrasensory / Heal Bell / Haze / Ice Beam）が書かれているページ（Articuno の Generation III learnset ページの "purification" 欄など）。
E. Serebii「Pokémon XD: Multiplayer / Trading」または Bulbapedia「Pokémon XD」：GBA版（RSE/FRLG）との交換の条件（本編クリア後、フェナスシティのポケモンセンター地下、リライブ済みのみ、GBA側は殿堂入り済み・ポケモンセンター内でセーブ、GC–GBAケーブル、DS不可 等）。
F. 日本語：ニケルダーク大学（hope3gen.hatenablog.com）の XD 乱数調整の記事（2023/11/27, 2023/12/04, 2023/12/07（2件）, 2023/12/09）：
   F-1. 「いますぐバトル」で初期seedを特定する手順の記述。
   F-2. ロード／エレベーター／戦闘開始の固定消費（例：22＋22＋4＝48）と、いますぐバトル画面での消費速度（3713.6/s や 6872〜7500/s）を述べている箇所。
   F-3. デスゴルド戦でわざと負けて「生成済み」状態にする手順や、シャドウの個体が「初めて場に出た時点で確定する」と述べている箇所。
   F-4. フリーザー／サンダー／ファイヤーで到達した個体の性格・個体値の実例。
G. Smogon「Pokémon Colosseum and Pokémon XD Mechanics Guide」（smogon.com/forums の GP 2/2 スレッド、または smogon.com/ingame/guides/xd_guide）：shiny lock（色違いの再抽選）について述べている文の逐語引用。

出力形式：Markdown。各引用は
> "…逐語…" — サイト名, ページ名／見出し, URL
の形で。最後に、実際に開けたURLと開けなかったURLを列挙してください。
```

---

## プロンプトC：投稿前の目視確認3点（2026-09-10 追加。回答Aの再検証）

```
あなたはリサーチアシスタントです。前回の調査結果（Smogon「Gen III Battle Frontier Discussion and Records」スレッド）のうち、投稿の前提になる4箇所だけを再検証してください。今回は「あるかどうか」を厳密に確認するのが目的なので、要約せず、該当箇所の前後を含めて逐語引用してください。見つからなければ「見つからず」と明記し、推測で補わないでください。前回の回答を参照して答えることは禁止し、必ず今回ページを開き直して確認してください。

対象スレッド：
https://www.smogon.com/forums/threads/gen-iii-battle-frontier-discussion-and-records.3648697/

1. 1ページ目のOP（Post #1、Valentino23）
   1-1. "genned" を含む文をすべて、前後1文ずつを含めて逐語引用。
   1-2. "It is your responsibility to ensure your Pokemon is possible to obtain." という文（またはこれに近い文）が本当にOP本文にあるか。あれば、その文が置かれている段落全体を逐語引用。無ければ「OPには存在せず」と明記し、スレッド内の別の投稿にあるなら、その投稿者・日付・ページ・URLを示す。
   1-3. OPの末尾に表示される "Last edited" の日付と、編集者名が表示されていればその名前。
   1-4. "purify" を含む文をすべて逐語引用。

2. 76ページ Post #1891（Adedede、2024-12-23 とされる投稿）
   2-1. この投稿の本文全体を逐語引用（投稿者名・日時・パーマリンクURL付き）。
   2-2. 特に "PkHex'd" と "genned" を含む文が実在するかを明記。
   2-3. この投稿が返信している元の投稿（引用元）の投稿者・日付・要旨。

3. 83ページ Post #2074（sbeven、2026-02-24 とされる投稿）
   3-1. この投稿の本文全体を逐語引用（投稿者名・日時・パーマリンクURL付き）。
   3-2. この投稿より後（83ページ以降、最終ページまで）に、この質問への返信や、PKHeX／genned／PokeFinder の可否に触れた投稿があるか。あれば全件、投稿者・日付・ページ・URL・逐語引用。無ければ「返信なし（最終ページ N まで確認）」と明記。

4. 77ページ Post #1908（Jheisinho、2025-01-28 とされる投稿）
   4-1. Articuno のセット部分（@ から技4つまで）を一字一句逐語引用。
   4-2. この投稿が「1316連勝の報告」であることが本文から読み取れるか（該当する文を逐語引用）。

5. 最後に、実際に開いたURL（ページ番号付き）と、開けなかったURLを列挙してください。

出力形式：Markdown。各引用は
> "…逐語…" — 投稿者, YYYY-MM-DD, page N, URL
の形で。日本語訳は不要です。
```
