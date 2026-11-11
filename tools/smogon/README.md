# tools/smogon/ — Smogon 調査のメモ（記録）

Smogon 提出の下調べで使った、GPT への調査プロンプトと回答の原文、スレッドの取り込みスクリプト。

- GPT の回答は二次資料。頼りにしているのは、スレッド原文や走者のスクリーンショットで確かめた部分だけ（[26章](../../docs/history/26-articuno-provenance.md)・[27章](../../docs/evidence/27-smogon-post.md)）
- `gpt-prompts.md`：プロンプト A〜C
- `gpt-answer-A-smogon-thread.md`（スレッドの抜き出し）・`gpt-answer-B-xd-route.md`（XD の入手ルート）・`gpt-answer-C-reverification.md`（投稿前の再確認）：回答の原文
- `smogon_thread_dump.py`：スレッドを JSONL と Markdown に落とす
