# tools/advisor/ — アドバイザー（凍結）

v4 構成の補助 UI。盤面を入れると、12章の条項と2手読みで推奨手を出す。
盤面入力が v4 の4体（サンダー／メタグロス／ラティオス／ラグラージ）のままなので凍結した。v6 でも使わない。

- 端末版 `advisor.py`、ブラウザ版 `advisor_web.py`、対面コンソール `playbook-console.html`、AWS Lambda 用 `lambda_handler.py`・`make_lambda_zip.sh`、Docker 用 `Dockerfile.advisor`
- 配備の手順書は非公開で、公開版には無い
- このフォルダは非公開側の配備用ワークフローが見張っている。気軽に書き換えない

条項の出どころは [12章](../../docs/history/12-playbook.md)（凍結）。
