# GPT回答B：XD入手ルート一次資料の逐語引用（2026-09-10）

> 走者が `gpt-prompts.md` のプロンプトBをChatGPTに投げ、ChatGPTが実際にページを開いて抜き出した結果の原文。本リポジトリ側（Code）は bulbapedia／serebii／hatenablog 等を開けないため**未検証**。26章§4・§5.1の根拠として「GPT」と明記して引用。

---

# Pokémon XD / Shadow Pokémon / XD RNG 調査結果

調査日: 2026-09-10

## 引用について

指定サイトを実際に開いて確認した。原文の逐語引用を中心に記録している。

ただし、第三者サイトの長文をそのまま大量転載することはできないため、各項目では**該当する短い逐語引用**を掲載し、必要な箇所はページ内の節名とURLを示している。指定された文言が確認できなかった場合は「見つからず」と記載した。

---

# A. Bulbapedia「Shadow Pokémon」

## A-1. Pokémon XDのShadow PokémonがShinyにならない仕組み

### 見出し
**Shiny Shadow Pokémon**

URL:
https://bulbapedia.bulbagarden.net/wiki/Shadow_Pokémon

逐語引用:

> "In Pokémon XD, when the game calculates a personality value for a Shadow Pokémon, it ensures that the Pokémon will not be Shiny for the player or the NPC Trainer."

— Bulbapedia, **Shadow Pokémon / Shiny Shadow Pokémon**,  
https://bulbapedia.bulbagarden.net/wiki/Shadow_Pokémon

より詳細な現在のBulbapedia「Shiny」記事には、PID再計算について次の記述がある。

### 見出し
**Shiny / Pokémon XD**

> "In Pokémon XD, the game ensures that all Shadow Pokémon are not Shiny by recalculating the Pokémon's personality value if it would result in a Shiny Pokémon."

— Bulbapedia, **Shiny / Pokémon XD**,  
https://bulbapedia.bulbagarden.net/wiki/Shiny

### 判定に使われるID

BulbapediaのColosseum/XDのShiny説明では、XDについて、

> "the game calculates a personality value for a Shadow Pokémon, checks it against the player's and opponent's ID numbers"

と明記されている。

— Bulbapedia, **List of battle glitches in Generation III**,  
https://bulbapedia.bulbagarden.net/wiki/List_of_battle_glitches_(Generation_III)

したがって、XDでは**player側とopponent/NPC側の双方のID**をチェックする記述が確認できる。

---

## A-2. Colosseumとの違い / Shiny Shadow Pokémon glitch

### 見出し
**Shiny Shadow Pokémon**

Bulbapedia:

> "In Pokémon Colosseum, there is a roughly 1/8192 chance of a Shadow Pokémon being Shiny."

> "When a Shadow Pokémon is first encountered, it is assigned a random personality value, but the game ensures that the personality value does not cause it to be Shiny for its NPC Trainer"

> "When the player catches the Shadow Pokémon, because it retains that same personality value but now has a different Trainer ID and Secret ID, the Shadow Pokémon can be Shiny for the player."

— Bulbapedia, **Shadow Pokémon / Shiny Shadow Pokémon**,  
https://bulbapedia.bulbagarden.net/wiki/Shadow_Pokémon

つまりColosseumでは、NPC側でShinyにならないようにPIDを選び、その後playerのTID/SIDへ変わることでShinyになるケースが発生する。

---

# B. Glitch City Laboratories Wiki「Shiny Shadow Pokémon glitch」

指定URL:

https://glitchcity.wiki/wiki/Shiny_Shadow_Pok%C3%A9mon_glitch

### 結果

**見つからず（サイトが403 Forbiddenで取得不能）。**

実際のURLを開こうとしたところ403となり、ページ本文を確認できなかった。

そのため、Glitch City Laboratories Wikiについては、**TID/SIDに関する逐語引用を推測で補わない**。

なお、同じ仕組みについてはBulbapedia側で確認できる。

---

# C. Greevil / Citadark Isle / XD Walkthrough Part 8

## C-1. Greevilの6体とレベル・順番

### 見出し
**Greevil / After Shadow Lugia is dealt with**

URL:
https://bulbapedia.bulbagarden.net/wiki/Greevil

逐語引用:

> "Shadow Rhydon♂/♀ Lv.46"

> "Shadow Moltres Lv.50"

> "Shadow Exeggutor♂/♀ Lv.46"

> "Shadow Tauros♂ Lv.46"

> "Shadow Articuno Lv.50"

> "Shadow Zapdos Lv.50"

— Bulbapedia, **Greevil / After Shadow Lugia is dealt with**,  
https://bulbapedia.bulbagarden.net/wiki/Greevil

したがって、送り出し順は:

1. Rhydon Lv.46
2. Moltres Lv.50
3. Exeggutor Lv.46
4. Tauros Lv.46
5. Articuno Lv.50
6. Zapdos Lv.50

---

## C-2. Shadow Lugia戦→Greevil戦が連続し、間にセーブできないか

### Bulbapedia Walkthrough Part 8

URL:
https://bulbapedia.bulbagarden.net/wiki/Walkthrough:Pokémon_XD/Part_8

Part 8について、今回取得できた本文では**「Shadow Lugia戦直後にGreevil戦が始まり、その間にセーブできない」という明示的な一文は見つからず**。

したがって、指定されたBulbapedia Part 8については:

**見つからず**

とする。

### 補足：別の一次的攻略資料では確認可能

SerebiiのXD Walkthroughには、

> "Beat or snag it, then Verich will go berserk and fight you"

とあり、Lugia後にGreevil戦へ続くことが確認できる。

URL:
https://www.serebii.net/xd/walkthrough/06.shtml

またGameFAQsの攻略資料には、

> "Use your master ball, because you're going to have a really hard fight with a ton of shadow pokemon and no time to save right after."

とある。

URL:
https://gamefaqs.gamespot.com/gamecube/925945-pokemon-xd-gale-of-darkness/faqs/39245

ただし、これは**指定されたBulbapedia Part 8の引用ではない**。

---

## C-3. エンディング後のGreevil再戦でShadowが置き換わるポケモン

### 見出し
**Greevil / After others are snagged**

URL:
https://bulbapedia.bulbagarden.net/wiki/Greevil

逐語引用:

> "If a Shadow Pokémon was not snagged in the first battle, it will replace the corresponding Pokémon in this team."

— Bulbapedia, **Greevil / After others are snagged**,  
https://bulbapedia.bulbagarden.net/wiki/Greevil

再戦時の通常ポケモンは:

- Rhydon → Manectric
- Moltres → Swellow
- Exeggutor → Starmie
- Tauros → Granbull
- Articuno → Altaria
- Zapdos → Aerodactyl

Bulbapediaの再戦チームではManectric / Swellow / Starmie / Granbull / Altaria / Aerodactylの6体がLv.50。

別のSerebii FAQにも6体が列挙されている:

> "his team will be replaced by level 50s Swellow, Manectric, Altaria, Aerodactyl, Starmie, Granbull if you've snagged all his shadows."

URL:
https://forums.serebii.net/threads/the-xd-faq-thread.87525/post-2156789

---

# D. Purification / Purify Chamber / Articuno Generation III learnset

## D-1. リライブ方法

### 見出し
**Purification / Purifying a Pokémon**

URL:
https://bulbapedia.bulbagarden.net/wiki/Purification

逐語引用:

> "The following actions will open the door to a Pokémon's heart by varying amounts:"

> "Sending a Shadow Pokémon into battle"

> "Calling a Shadow Pokémon out of Hyper Mode or Reverse Mode in battle"

> "Walking with a Shadow Pokémon in the party"

> "Using Scents on a Shadow Pokémon"

> "Placing a Shadow Pokémon in the Purification Chamber (in Pokémon XD only)"

— Bulbapedia, **Purification / Purifying a Pokémon**,  
https://bulbapedia.bulbagarden.net/wiki/Purification

また、Heart Gaugeについて:

> "There are several ways in which to open a Pokémon's heart."

— Bulbapedia, **Heart Gauge**,  
https://bulbapedia.bulbagarden.net/wiki/Heart_Gauge

---

## D-2. Purify Chamber

### 見出し
**Purify Chamber / Mechanics**

URL:
https://bulbapedia.bulbagarden.net/wiki/Purification_Chamber

逐語引用:

> "The Purify Chambers works by slowly opening up a Shadow Pokémon's heart over time."

— Bulbapedia, **Purify Chamber / Mechanics**,  
https://bulbapedia.bulbagarden.net/wiki/Purification_Chamber

---

## D-3. Articunoのリライブ後の4技

### 見出し
**Purification / Special moves**

URL:
https://bulbapedia.bulbagarden.net/wiki/Purification

Bulbapediaの表ではArticunoについて、

> "Articuno | Haze | Heal Bell | Extrasensory"

と記載されている。

さらにArticunoのGeneration III learnsetでは、XDのPurified movesとして:

> "Haze | Ice"

> "Heal Bell | Normal"

> "Extrasensory | Psychic"

> "Ice Beam | Ice"

が記載されている。

URL:
https://bulbapedia.bulbagarden.net/wiki/Articuno_(Pokémon)/Generation_III_learnset

したがってリライブ後の4技は:

**Extrasensory / Heal Bell / Haze / Ice Beam**

---

# E. Pokémon XD → GBA交換条件

## Bulbapedia「Pokémon XD: Gale of Darkness」

### 見出し
**Connectivity**

URL:
https://bulbapedia.bulbagarden.net/wiki/XD

逐語引用:

> "In the original Nintendo GameCube release of Pokémon XD, players can transfer snagged Pokémon from Pokémon XD to any of the portable Generation III games: Ruby, Sapphire, FireRed, LeafGreen, and Emerald Version."

> "This transference functions identically to the trading function in the core series games, but can only happen in Phenac City."

> "In order to do the above, one needs to finish the main story in Pokémon XD and have entered the Hall of Fame in the corresponding Generation III game."

— Bulbapedia, **Pokémon XD / Connectivity**,  
https://bulbapedia.bulbagarden.net/wiki/XD

### 重要な修正

ユーザー指定の「リライブ済みのみ」については、今回開いたBulbapedia本文には**その条件をそのまま述べる文は見つからず**。

また「DS不可」「GC–GBAケーブル」について、Bulbapediaの概要には:

> "Connectivity: GameCube Game Boy Advance cable"

とある。

さらにBlurbには:

> "By connecting with a Game Boy Advance—using a Nintendo GameCube Game Boy Advance cable—you can import and battle with your Game Boy Advance Pokémon"

とある。

ただし、指定された「すべての条件」を一つの文章として記載した箇所は**見つからず**。

### DSについて

今回開いたBulbapediaでは、DSを直接「不可」とする逐語的な記述は**見つからず**。

ただし、XDのConnectivityはGameCube–GBA方式として記載されている。

---

# F. ニケルダーク大学（Hope_flygon）

## F-1. 「いますぐバトル」で初期Seedを特定

### 2023-12-07
記事:
**「3世代環境における対戦個体調達用の乱数調整の解説 ポケモンXD サンダー編」**

URL:
https://hope3gen.hatenablog.com/entry/2023/12/07/234846

### 見出し
**2. 初期Seedの特定**

逐語引用:

> "XDを起動し、右の「対戦モード」から「いますぐバトル」、「コンピュータとバトル」、「さいきょう」の順に進んでいきます。"

> "そうしたら、今度こそXDSearchにポケモンと数値を入力していきます。"

> "入力した情報が間違っていなければ、右側のSeed欄に8桁の現在Seedが出てきます。"

— ニケルダーク大学 / Hope_flygon, 2023-12-07, **2. 初期Seedの特定**,  
https://hope3gen.hatenablog.com/entry/2023/12/07/234846

---

## F-2. 固定消費 22 + 22 + 4 = 48

### 2023-12-07 補足資料

記事:
**「XDサンダーの乱数調整に関する補足資料」**

URL:
https://hope3gen.hatenablog.com/entry/2023/12/07/234821

### 見出し
**4. 任意消費数を確認してください。**

逐語引用:

> "恐らく48となっているはずです。"

> "この48という数字は、タイトルからデータをロードする際に発生する22消費、エレベーターを降りる際に発生する22消費、デスゴルド戦の戦闘開始エフェクトにより発生する4消費を足したものとなっています。"

— ニケルダーク大学 / Hope_flygon, 2023-12-07, **4. 任意消費数を確認してください。**,  
https://hope3gen.hatenablog.com/entry/2023/12/07/234821

### 2023-12-07 サンダー本編

逐語引用:

> "大量消費の消費速度を3850.0と入力"

— ニケルダーク大学 / Hope_flygon, 2023-12-07, **4. Seed厳選と乱数消費**,  
https://hope3gen.hatenablog.com/entry/2023/12/07/234846

### 3713.6/s

指定された「3713.6/s」は、今回確認できたHopeの記事本文では**該当する逐語記載を見つけられず**。

ただし、XDSeedSorterのGitHubには:

> "advancesPerSecond": 3713.6

という設定値があり、

> "いますぐバトルにファイヤーが1体出ている場合の消費数になっています。"

と説明されている。

URL:
https://github.com/u1f992/XDSeedSorter

### 6872〜7500/s

Hopeの記事そのものではなく、別のXD RNG資料で確認できる。

ポケ屋の根城:

> "ファイヤー(デスゴルド戦前)：6872/s"

> "ファイヤー(デスゴルド戦後未捕獲)：7500/s"

URL:
https://baobaopoke.hatenadiary.com/entry/2020/03/10/121442

また2023-10-05の別記事では:

> "GCだと7500/s、Wiiだと6872.1/s説もあればファイヤー固定前と固定後で消費数が変わる説とかいろいろあります"

URL:
https://wasou3721.hatenablog.com/entry/2023/10/05/053600

したがって、**6872〜7500/sはXD乱数界隈の消費速度資料として確認できるが、指定された2023-12-07 Hope記事の記述ではない。**

---

## F-3. デスゴルド戦で負けて「生成済み」にする / 初出場時点で個体確定

### 2023-12-07

記事:
https://hope3gen.hatenablog.com/entry/2023/12/07/234846

### 見出し
**4. Seed厳選と乱数消費**

逐語引用:

> "一旦XDをリセットして今度はルギアを討伐。デスゴルド戦で相手のフリーザーまで見たら負けてください。"

> "ここまでやったらレポートを書いて次へ進みます。"

— Hope_flygon, 2023-12-07, **4. Seed厳選と乱数消費**,  
https://hope3gen.hatenablog.com/entry/2023/12/07/234846

### 個体がエンカウント時点で固定

2023-11-27:

記事:
https://hope3gen.hatenablog.com/entry/2023/11/27/175410

本文:

> "ポケモンXDには一度エンカウントするとその時点で個体の情報が確定し、特性以外は変わらないという仕様があります。これを個体の固定と呼んでいます。"

— Hope_flygon, 2023-11-27,  
**ポケモンXDコラム / ポケモンXDの乱数調整についてもっと深く知ってみよう**,  
https://hope3gen.hatenablog.com/entry/2023/11/27/175410

2023-12-04にも同趣旨の記述:

> "ポケモンXDでは、一度ダークポケモンとエンカウントするとその時点で個体情報が確定し、以降変わる事はありません。これを個体の固定といいます。"

— Hope_flygon, 2023-12-04,  
**乱数調整に関わりがちな独自仕様まとめ / 3. 個体の固定とXD特性**,  
https://hope3gen.hatenablog.com/entry/2023/12/04/093843

---

## F-4. 3鳥の実例

### サンダー

2023-11-27の記事に明確な実例あり。

### 見出し
**ポケモンXDの乱数調整についてもっと深く知ってみよう**

逐語引用:

> "ひかえめ 31-31-31-31-31-30 (氷70)。"

— Hope_flygon, 2023-11-27,  
https://hope3gen.hatenablog.com/entry/2023/11/27/175410

同記事では、この個体について「色回避が発生するID」「デスゴルドの手持ちを丁度ナッシーまで固定した状態」で出現する個体であると説明している。

### ファイヤー

2023-12-09記事:

https://hope3gen.hatenablog.com/entry/2023/12/09/120733

対象は**サイドン / ファイヤー**。

記事には、XDファイヤーが「3世代で貴重な高速回復技の一つである『あさのひざし』」と「おにび」を持つこと、また具体的な乱数調整手順が記載されている。

今回取得した本文範囲では、指定された「性格＋6IV」の具体的なファイヤー完成個体を逐語的に確認できる箇所は**見つからず**。

### Articuno / Zapdos

指定された2023-11-27 / 12-04 / 12-07 / 12-09の記事群について、今回確認できた本文では、Articunoについての具体的な「性格＋6IV」の完成個体例は**見つからず**。

---

# G. Smogon「Pokémon Colosseum and Pokémon XD Mechanics Guide」

URL:
https://www.smogon.com/ingame/guides/colosseum_xd_mechanics_guide

## 見出し
**Shiny Pokémon**

逐語引用:

> "In XD, they implemented a shiny-lock feature whereby, if the Shadow Pokémon's generated PID is shiny with the player's IDs, it's rerolled until it is not shiny."

> "This means that Shadow Pokémon in XD can never be shiny."

— Smogon University, **Pokémon Colosseum and Pokémon XD: Gale of Darkness Mechanics Guide / Shiny Pokémon**,  
https://www.smogon.com/ingame/guides/colosseum_xd_mechanics_guide

これはXDのshiny lockについて、今回確認した中でも非常に直接的な記述。

---

# まとめ：今回確認できたこと

## XD Shiny判定

- XDではShadow PokémonのPIDがShiny判定になる場合、PIDを再抽選／再計算してShinyを回避する。
- BulbapediaではplayerとNPC/opponentのID双方をチェックすると記載。
- Smogon Mechanics Guideでは特に「player's IDs」に対するShiny判定→rerollを明記。

## Greevil

初戦後の6体:

1. Rhydon Lv.46
2. Moltres Lv.50
3. Exeggutor Lv.46
4. Tauros Lv.46
5. Articuno Lv.50
6. Zapdos Lv.50

再戦時の対応:

- Rhydon → Manectric
- Moltres → Swellow
- Exeggutor → Starmie
- Tauros → Granbull
- Articuno → Altaria
- Zapdos → Aerodactyl

## Articuno

XDでShadow Articunoをリライブすると、

**Extrasensory / Heal Bell / Haze / Ice Beam**

を得ることが、BulbapediaのPurificationおよびGeneration III learnsetで確認できる。

## XD乱数

- いますぐバトル → コンピュータとバトル → さいきょう、でSeed特定。
- 固定消費は **22 + 22 + 4 = 48**。
- デスゴルド戦で一定数のShadow Pokémonを出して負けることで、個体固定を利用した乱数調整が可能。
- Shadow Pokémonの個体は初回エンカウント時点で固定される。
- 3713.6/sはXDSeedSorter側で確認。
- 6872/s / 7500/sは別のXD乱数資料で確認。

---

# 実際に開けたURL

## Bulbapedia

- https://bulbapedia.bulbagarden.net/wiki/Shadow_Pokémon
- https://bulbapedia.bulbagarden.net/wiki/Shiny
- https://bulbapedia.bulbagarden.net/wiki/List_of_battle_glitches_(Generation_III)
- https://bulbapedia.bulbagarden.net/wiki/Greevil
- https://bulbapedia.bulbagarden.net/wiki/Nickeldark_Island
- https://bulbapedia.bulbagarden.net/wiki/Walkthrough:Pokémon_XD/Part_7
- https://bulbapedia.bulbagarden.net/wiki/Walkthrough:Pokémon_XD/Part_8
- https://bulbapedia.bulbagarden.net/wiki/Purification
- https://bulbapedia.bulbagarden.net/wiki/Purification_Chamber
- https://bulbapedia.bulbagarden.net/wiki/Articuno_(Pokémon)/Generation_III_learnset
- https://bulbapedia.bulbagarden.net/wiki/XD

## Smogon

- https://www.smogon.com/ingame/guides/colosseum_xd_mechanics_guide

## ニケルダーク大学

- https://hope3gen.hatenablog.com/entry/2023/11/27/175410
- https://hope3gen.hatenablog.com/entry/2023/12/04/093843
- https://hope3gen.hatenablog.com/entry/2023/12/07/234846
- https://hope3gen.hatenablog.com/entry/2023/12/07/234821
- https://hope3gen.hatenablog.com/entry/2023/12/09/120733

## その他

- https://github.com/u1f992/XDSeedSorter
- https://baobaopoke.hatenadiary.com/entry/2020/03/10/121442
- https://wasou3721.hatenablog.com/entry/2023/10/05/053600
- https://www.serebii.net/xd/walkthrough/06.shtml
- https://www.serebii.net/xd/walkthrough/07.shtml
- https://forums.serebii.net/threads/the-xd-faq-thread.87525/post-2156789
- https://gamefaqs.gamespot.com/gamecube/925945-pokemon-xd-gale-of-darkness/faqs/39245

# 開けなかったURL

- https://glitchcity.wiki/wiki/Shiny_Shadow_Pok%C3%A9mon_glitch
  - **403 Forbidden**
  - ページ本文を確認できず。
  - TID/SIDについて推測で補完していない。

# 注意

今回の調査では、指定されたサイト・記事について「確認できた事実」と「指定ページでは確認できなかった事実」を分けた。

特に、
- Glitch City LaboratoriesのShiny Shadow Pokémon glitch
- Bulbapedia Part 8の「Lugia→Greevil間でセーブ不可」という明示文
- 2023-12-07 Hope記事内の3713.6/s
- 2023-12-09記事内の指定された3鳥の完成個体

については、指定されたページから該当する逐語引用を確認できなかったため、別サイトの情報を補助資料として分離した。
