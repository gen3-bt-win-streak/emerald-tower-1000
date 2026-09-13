# エメラルド バトルタワー（ダブル・オープンレベル）1000連勝プロジェクト

一次データ（pokeemerald逆コンパイル）と全546セットの全数計算で、構築・行動指針・個体の正当性を「感覚ではなく証拠」として積み上げる記録。
公開リポジトリ：https://github.com/gen3-bt-win-streak/emerald-tower-1000 （英語の入口は [README_EN.md](README_EN.md)）

## 現在地（2026-09-11）

| 項目 | 状態 |
|---|---|
| 構築 | **v5 確定**：メタグロス@ハチマキ／ラティオス／フリーザー（XD産・こころのめ／零度／まもる／くろいきり）／カビゴン → [25章](docs/current/25-v5-articuno-build.md) |
| 実機 | v5で走行中。42連勝停止（バクフーン#647）→ 条項化済み。ジュゴン／トドゼルガの一撃技で停止 → 条項化済み（[12章 8.6e／8.6f](docs/current/12-playbook.md)） |
| 自己ベスト | 613連勝（v4系・Delta、未提出）。v4実機の履歴は [15章](docs/history/15-v4-real-build.md) 末尾の実戦ログ |
| 世界記録 | オープン・ダブル 1316連勝（Jheisinho・エミュ）。1000連勝は歴代2位相当、更新ラインは1317 |
| Smogon | PKHeXで再現したRNG実在個体は **掲載可**（2026-05-04 管理者回答で決着）。提出は現管理者の在任中（2026年内）に → [27章](docs/current/27-smogon-post.md) |
| 公開 | `battle-tower/` の履歴をスクラブして公開。更新は `publish-public-mirror` ワークフロー（手動実行のみ。[17章§8.5](docs/current/17-smogon-legitimacy.md)）。13・14章は**旧パス・新パスとも**除去される |

## 読む順番

- **経緯を1枚で**：[TIMELINE.md](TIMELINE.md)（何を試し、何が没になり、なぜ今の形か。棄却・棚上げ・訂正も全部載せている）
- **実機で戦う**：[12章 v5クイックリファレンス](docs/current/12-playbook.md)（1ページ）→ 該当条項へ。
- **構築を理解する**：[25章§0](docs/current/25-v5-articuno-build.md)（確定表と主要指標）→ §2（フリーザーの全検討）→ §10（敵対評価）。
- **個体を用意する／正当性を説明する**：[16章](docs/current/16-pkhex-setup.md) → [26章](docs/current/26-articuno-provenance.md) → [17章](docs/current/17-smogon-legitimacy.md)・[27章](docs/current/27-smogon-post.md)。
- **数字の出どころを確かめる**：[18章 検証台帳](docs/current/18-verification-ledger.md)（日付順の全主張と訂正）→ `tools/engine/`・`tools/sim/`（各ディレクトリの役割は [tools/README.md](tools/README.md)）。

## 設計の原則（全章に共通）

1. **相手に乱数を振らせる回数を最小化する**。1000連勝は1戦あたり99.93%の勝率を要求する。
2. 攻撃側の指標は**最低乱数**（確定n発）、防御側は**最大乱数**（被乱n発圏）で数える（走者定義）。
3. だいばくはつ・じしんは第3世代ダブルで**減衰なし**。爆発が主砲で、相方のまもるとセット。
4. 引き分け＝負け。爆発・ほろびは生存者を残せる座組みでだけ撃つ。
5. 負けは全部、台帳に記録 → 全数計算 → 条項化（12章）。

## ドキュメント一覧

### 現行（v5）で使うもの — `docs/current/`

| ファイル | 内容 | 状態 |
|---|---|---|
| [**25-v5-articuno-build.md**](docs/current/25-v5-articuno-build.md) | v5構築の確定表・主要指標・フリーザーの全検討（技構成、EV、後出し枠モデル、ギャラドス比較）・敵対評価 | ✅ 確定 |
| [**12-playbook.md**](docs/current/12-playbook.md) | 実機プレイブック。先頭の **v5クイックリファレンス**、詰み系即断、名指し条項（8.6d〜8.6i）、付章B（v5差分） | ✅ 運用中 |
| [**16-pkhex-setup.md**](docs/current/16-pkhex-setup.md) | 各個体の入手経路・PokeFinder→PKHeXの手順・確定スプレッド表・Legality警告の読み方 | ✅ |
| [**26-articuno-provenance.md**](docs/current/26-articuno-provenance.md) | XD産フリーザーの来歴証明：XDRNG導出・ロック連鎖・全数証明・入手ルート・色違い不可・証拠チェックリスト | ✅ 42/42 PASS |
| [**27-smogon-post.md**](docs/current/27-smogon-post.md) | Smogon掲載資格の決着（時系列・原文）と提出write-up用の英語段落 | ✅ 決着 |
| [17-smogon-legitimacy.md](docs/current/17-smogon-legitimacy.md) | Smogonルール原文・記録保持者の実態・提出チェックリスト・公開手順 | ✅ |
| [**18-verification-ledger.md**](docs/current/18-verification-ledger.md) | 検証台帳：全主張の機械検証結果と、発見した誤り・訂正の記録 | ✅ 継続 |

### 基礎データ（コード検証済み・構築に依存しない） — `docs/base/`

| ファイル | 内容 | 状態 |
|---|---|---|
| [00-rules.md](docs/base/00-rules.md) | ルール・敵抽選／IVの仕様・オープンレベル・第3世代の対戦仕様（引き分け＝負け等） | ✅ |
| [01-danger-pokemon.md](docs/base/01-danger-pokemon.md) | 危険ポケモンDB：50連勝以降プール546セットの完全列挙（一撃技23／催眠36／爆発24／ゴースト17 等） | ✅ |
| [02-danger-moves.md](docs/base/02-danger-moves.md) | 危険技・アイテムと発動率（QC20%等） | ✅ |
| [03-ai.md](docs/base/03-ai.md) | AI完全解析：技スコアリング・ターゲット選択・交代トリガー | ✅ |
| [20-explosion-digest.md](docs/base/20-explosion-digest.md) | 敵の「だいばくはつ」使用AI（1枚もの） | ✅ |
| [data/](data/README.md) | 敵全882セット・トレーナー300人・危険レポート（CSV/JSON） | ✅ 独立監査済み |
| [sources.md](docs/base/sources.md) | 出典・検証記録 | ✅ |

### 構築の歴史（v1→v4。数値は当時の構成に対するもの） — `docs/history/`

| ファイル | 内容 | 状態 |
|---|---|---|
| [15-v4-real-build.md](docs/history/15-v4-real-build.md) | v4.2／v4.3 実機リファレンス（サンダー／メタグロス／ラティオス／ラグラージ）・実戦ログ（442→581→303→185→280） | 📁 記録 |
| [24-pick4-audit.md](docs/history/24-pick4-audit.md) | 280連勝停止後の4Pick監査。メタグロス必須・ラグラージ→カビゴン・EV指標の再定義（v5の出発点） | 📁 記録 |
| [10-z-axis.md](docs/history/10-z-axis.md) | Z軸（v3→v4）：100万戦シミュ（負け率0.2516%）・装備／EV補遺1〜20・敗因解剖 | 📁 記録 |
| [08-simulation.md](docs/history/08-simulation.md) | 対戦シミュレータの開発と大規模検証 | 📁 記録 |
| [06-no-boom-playbook.md](docs/history/06-no-boom-playbook.md) | 爆発できないパターンの頻度・対策（旧本流・ゲンガー軸） | 📁 記録 |
| [04-team.md](docs/history/04-team.md)／[05-final-team.md](docs/history/05-final-team.md)／[09-c-hedge.md](docs/history/09-c-hedge.md) | 初期構想（ゲンガー軸・ほろびのうた路線） | 📁 記録 |

### 検討して棚上げ・不採用にした軸 — `docs/shelved/`

| ファイル | 内容 | 判定 |
|---|---|---|
| [19-perish-team.md](docs/shelved/19-perish-team.md) | P軸（ほろびパ） | 負け率46%で棚上げ |
| [22-s-axis.md](docs/shelved/22-s-axis.md) | S軸（スキルスワップ＋じこあんじ） | 設営事故率が高く不採用 |
| [23-y-axis.md](docs/shelved/23-y-axis.md) | Y軸（削り軸） | 机上のみ・未投入 |
| [11-k-axis.md](docs/shelved/11-k-axis.md) | K軸（いちゃもん） | 記録のみ |
| [21-rng-oracle.md](docs/shelved/21-rng-oracle.md) | 乱数オラクル（観測からのシード同定） | 実測待ち |

### 機材・運用インフラ — `docs/infra/` と `tools/`

| ファイル | 内容 |
|---|---|
| [07-hardware-proof.md](docs/infra/07-hardware-proof.md) | 機材と記録証明の計画（録画・提出） |
| [13-deploy-advisor.md](docs/infra/13-deploy-advisor.md)／[14-apply-runbook.md](docs/infra/14-apply-runbook.md) | アドバイザーのクラウド配備手順（**非公開のみ**。公開エクスポートが旧パス・新パスの両方を全履歴から除去するため、公開側では常にリンク切れ） |
| `tools/engine/` | 全数計算エンジン（`calc_matchups.py`・`evlib.py`）と pokeemerald 抜粋。ほぼ全ての数値の出どころ |
| `tools/xd/` | XD産フリーザーの来歴検証（`xd_articuno_verify.py`・42/42 PASS） |
| `tools/sim/` | シミュレータと検証スクリプト（`legacy/` は v0期の記録・実行不能） |
| `tools/advisor/` | アドバイザー（Lambda／Docker／コンソール） |
| `tools/publish/` | 公開エクスポート |
| `tools/smogon/` | GPT向け調査プロンプトと回答原文、スレッド取り込みスクリプト |
| [tools/README.md](tools/README.md) | 各ディレクトリの役割・依存の向き・環境変数・**旧→新パス対応表** |
| `tools/publish/make_public_export.sh`／`.github/workflows/publish-public-mirror.yml` | 公開用エクスポートと自動公開 |

## 検証で判明した主な事実（抜粋）

- じしん・だいばくはつは第3世代ダブルで**減衰なし**（0.5倍は相手2体対象技のみ）。
- 敵の自爆に**HPゲートは無い**。先手を取られている側の敵は満タンでも普通に撃ってくる。
- オープンで増える脅威はカイリュー／バンギラス／三鳥三犬の32セットだけ。詰み系リストはLv50と同一。
- 相打ち全滅＝負け。しめりけ（ゴルダック／ヌオー）は特性率50%で判別不能＝見えたら爆発禁止。
- 一撃技23セット・QC75セットが常駐。一撃技は命中29%で、耐久・回避・リフレクターは無関係。
- ロック中の零度は回避・防御上昇・半無敵を無視するが、**相手のまもるでは不発**（2026-09-10 原文で確認）。
- XDのシャドウは色違いにならず、おだやか31/0/31/31/31/31は存在しない（A0の上限はC29＝現行個体）。

## ロードマップ

- [x] Phase 0〜3：ルール・危険DB・危険技・AI解析（コード検証済み）
- [x] Phase 4：構築 v3→v4（100万戦シミュ）→ v5（全数計算＋走者定義の指標に切り替え、シミュマラソンは終了）
- [x] 個体の正当性：全個体をPokeFinder実在フレーム→PKHeXで用意。XD産フリーザーの来歴証明を完成。Smogon掲載資格を決着。
- [x] 公開：スクラブ済み履歴を `gen3-bt-win-streak/emerald-tower-1000` に公開、Actionsで自動追随。
- [ ] **Phase 5（進行中）**：v5で実機走行。負けごとに条項化。録画とBattle Resultsのスクショを保存。
- [ ] Smogon提出：2026年内（現管理者の在任中）に、write-up＋公開リポジトリへのリンク付きで提出。
