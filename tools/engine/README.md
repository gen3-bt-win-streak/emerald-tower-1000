# tools/engine/ — 全数計算エンジン

v6 の数値はここから出す。pokeemerald のダメージ計算を移植し、50戦目以降の546型と総当たりする。

- 本体：`calc_matchups.py`（ダメージ計算）・`evlib.py`（その場の疑問を全数で確かめる道具）・`jpnames.py`（日本語名）
- v6 の4体を `evlib` で作る定義は下の折りたたみ（`battle-tower/` から実行。公開版ではリポジトリの一番上）
- 注意：`evlib` は威力1の技と一撃技を数えない（詳しくは下の「注意の詳細」）
- そのほかの `.py`：一回きりの監査スクリプト。多くは v4・v5 期のもの（`pivot_articuno*.py` は v5）。`parse_frontier.py` は再実行できない記録
- `pokeemerald/`：pokeemerald 原文の抜粋。計算はここを読む
- 本体と `pokeemerald/` は `sim/`・`advisor/`・`rng-oracle/` からも読まれる。気軽に書き換えない

<details>
<summary>v6 の4体の定義（28章§0と一致）</summary>

```python
import sys; sys.path.insert(0, 'tools/engine')
from evlib import *
import evlib
IV = lambda **k: {**evlib._G['IV31'], **k}
GROSS = make("Metagross","Adamant",dict(hp=208,atk=252,spd=44,spe=4),"Choice Band",["MOVE_METEOR_MASH","MOVE_EARTHQUAKE","MOVE_EXPLOSION","MOVE_SHADOW_BALL"],ability="ABILITY_CLEAR_BODY")
LATI  = make("Latios","Timid",dict(hp=40,spa=252,spe=216),"Leftovers",["MOVE_PSYCHIC","MOVE_ICE_BEAM","MOVE_SUBSTITUTE","MOVE_PROTECT"],ability="ABILITY_LEVITATE",ivs=IV(atk=7))
TONO  = make("Politoed","Calm",dict(hp=240,df=154,spd=108,spe=8),"Lum Berry",["MOVE_PERISH_SONG","MOVE_PROTECT","MOVE_WATERFALL","MOVE_HYPNOSIS"],ability="ABILITY_DAMP",ivs=IV(atk=0))
KABI  = make("Snorlax","Adamant",dict(hp=80,atk=176,df=248,spe=4),"Chesto Berry",["MOVE_YAWN","MOVE_REST","MOVE_DOUBLE_EDGE","MOVE_PROTECT"],ability="ABILITY_THICK_FAT")
```

実数値は 353/405/296/203/227/177、311/172/196/359/256/341、381/139/224/216/289/178、481/330/228/149/256/97（HP/A/B/C/D/S）。
`ko_fixed(GROSS,["MOVE_METEOR_MASH","MOVE_EARTHQUAKE","MOVE_SHADOW_BALL"],n)` は n=1〜3 で 255/508/542（28章§6）。

</details>

実行のしかたと依存の向きは [`../README.md`](../README.md)。

<details>
<summary>注意の詳細</summary>

注意：`evlib` の被弾集計（`incoming`・`defense`・`risk_n`）は、威力1の技（きしかいせい・じたばた16型、カウンター34・ミラーコート13、ちきゅうなげ・ナイトヘッド）と一撃技を数えない。これらは別に見る（[2026-10-23 の敗戦ログ](../../logs/losses/2026-10-23-190.md)の「エンジンの穴」、[28章](../../docs/current/28-perish-build.md#4-運用条項)§4-10・§4-11・§4-20）

</details>
