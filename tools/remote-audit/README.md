# リモート監査ジョブ(実行手順書)

このフォルダは自己完結の計算パッケージ。別セッション(作業係)が以下を実行し、
結果を `battle-tower/results/remote_audit_results.jsonl` に集積して随時 push する。

## 手順(作業係セッション向け)

```bash
cd /home/user/daily-tasks
git fetch origin claude/battle-tower-1000-wins-8xr0ze
git checkout claude/battle-tower-1000-wins-8xr0ze
cd battle-tower/tools/remote-audit

# 1) スモークテスト(30戦・1分弱で「smoke OK」が出ること)
PYTHONHASHSEED=0 FIDELITY2=1 python3 remote_run.py smoke

# 2) 5ジョブを並列実行(4コア前提・各1〜3時間)
for J in scarfA scarfB arm10 arm11 arm12; do
  PYTHONHASHSEED=0 FIDELITY2=1 nohup nice python3 remote_run.py $J > job_$J.log 2>&1 &
done

# 3) ジョブが1本終わるごとに結果をコミット+プッシュ(pull --rebaseを先に)
cd /home/user/daily-tasks
git pull --rebase origin claude/battle-tower-1000-wins-8xr0ze
git add battle-tower/results/remote_audit_results.jsonl
git commit -m "リモート監査: <ジョブ名> 完了"
git push origin claude/battle-tower-1000-wins-8xr0ze
```

## 作業係の責務
- プロセス死活を適宜確認し(`pgrep -f remote_run`)、死んでいたら該当ジョブのみ再実行
  (results に既に行があるジョブは再実行不要)
- 全5ジョブの結果行が揃ったら最終コミット+プッシュして終了報告
- **push先は claude/battle-tower-1000-wins-8xr0ze のみ。PRは作らない。他のファイルは触らない**
- スモークが失敗したら結果をコミットせず、job_*.log の末尾をエラー報告としてコミットする
  (`battle-tower/results/remote_audit_ERROR.txt` に貼る)

## 中身のメモ
- sim*.py / calc_matchups.py: シミュレータ一式(このフォルダ内で相対openするためcwd必須)
- losses_snapshot.json: 364,000戦時点の負けシード凍結版(1,027敗)
- 期待される結果形式: 1行JSON {job, name, n, base_losses, w2l, l2w, flips, loss_n?, loss_rescue?}
