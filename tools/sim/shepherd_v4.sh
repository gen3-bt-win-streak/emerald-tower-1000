#!/bin/bash
# v4ネイティブ100万戦シェパード: 1ブロック(BASE)を4チャンク×62500に分割し4ワーカー起動。
# 使い方: ./shepherd_v4.sh 28000000   (この箱=28M / 班A=25M / 班B=26M / 班C=27M)
SP="$(cd "$(dirname "$0")" && pwd)"; cd "$SP"
BASE="${1:?usage: shepherd_v4.sh BASE}"
CHUNK=62500
STARTS="0 62500 125000 187500"
while true; do
  DONE=0
  for START in $STARTS; do
    CK="v4m_ckpt_${BASE}_${START}.json"
    if [ -f "$CK" ] && python3 -c "import json,sys; d=json.load(open('$CK')); sys.exit(0 if d['i']>=$CHUNK else 1)" 2>/dev/null; then
      DONE=$((DONE+1)); continue
    fi
    if ! pgrep -f "sim_v4maratho[n].py $BASE $START " >/dev/null; then
      echo "$(date -u +%H:%M) relaunch W${BASE}+${START}" >> shepherd_v4.log
      FIDELITY2=1 PYTHONHASHSEED=0 nohup nice -n 1 python3 sim_v4marathon.py $BASE $START $CHUNK >> "marathon_v4_W${BASE}_${START}.log" 2>&1 &
    fi
  done
  if [ "$DONE" -eq 4 ]; then echo "$(date -u +%H:%M) ブロック${BASE}全4チャンク完走" >> shepherd_v4.log; break; fi
  sleep 60
done
