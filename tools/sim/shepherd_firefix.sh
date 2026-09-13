#!/bin/bash
# 炎条項レバー ON マラソン シェパード: 1ブロックを4チャンク×62500で4ワーカー起動。
# sim_firefixmarathon.py が os.environ["FIRE_FIX"]=1 を設定(探索の炎条項レバーON)。
# 同一シードのOFFベースライン(v4m_ckpt_*.json 合計2516敗)とペア比較(aggregate_firefix.py)。
# 使い方: ./shepherd_firefix.sh 25000000   (班A=25M / 班B=26M / 班C=27M / 班D=28M)
SP="$(cd "$(dirname "$0")" && pwd)"; cd "$SP"
BASE="${1:?usage: shepherd_firefix.sh BASE}"
CHUNK=62500; STARTS="0 62500 125000 187500"
while true; do
  DONE=0
  for START in $STARTS; do
    CK="ffm_ckpt_${BASE}_${START}.json"
    if [ -f "$CK" ] && python3 -c "import json,sys; d=json.load(open('$CK')); sys.exit(0 if d['i']>=$CHUNK else 1)" 2>/dev/null; then
      DONE=$((DONE+1)); continue
    fi
    if ! pgrep -f "sim_firefixmaratho[n].py $BASE $START " >/dev/null; then
      echo "$(date -u +%H:%M) relaunch W${BASE}+${START}" >> shepherd_firefix.log
      FIDELITY2=1 PYTHONHASHSEED=0 nohup nice -n 1 python3 sim_firefixmarathon.py $BASE $START $CHUNK >> "marathon_ffm_W${BASE}_${START}.log" 2>&1 &
    fi
  done
  if [ "$DONE" -eq 4 ]; then echo "$(date -u +%H:%M) ブロック${BASE}全4チャンク完走" >> shepherd_firefix.log; break; fi
  sleep 60
done
