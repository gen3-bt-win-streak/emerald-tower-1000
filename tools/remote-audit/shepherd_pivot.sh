#!/bin/bash
# 関所3 PIVOT_ONマラソン シェパード: 1ブロック(BASE)を4チャンク×62500に分割し4ワーカー起動。
# 敵AIに不利対面ピボット交代(#5/#6)を有効化(sim_pivotmarathon.py が G["PIVOT_AI"]=True)。
# 同一シードのPIVOT_OFFベースライン(v4m_ckpt_*.json 合計2516負け)とペア比較してΔを測る。
# 使い方: ./shepherd_pivot.sh 25000000   (班A=25M / 班B=26M / 班C=27M / 班D=28M)
SP="$(cd "$(dirname "$0")" && pwd)"; cd "$SP"
BASE="${1:?usage: shepherd_pivot.sh BASE}"
CHUNK=62500
STARTS="0 62500 125000 187500"
while true; do
  DONE=0
  for START in $STARTS; do
    CK="pivotm_ckpt_${BASE}_${START}.json"
    if [ -f "$CK" ] && python3 -c "import json,sys; d=json.load(open('$CK')); sys.exit(0 if d['i']>=$CHUNK else 1)" 2>/dev/null; then
      DONE=$((DONE+1)); continue
    fi
    if ! pgrep -f "sim_pivotmaratho[n].py $BASE $START " >/dev/null; then
      echo "$(date -u +%H:%M) relaunch W${BASE}+${START}" >> shepherd_pivot.log
      FIDELITY2=1 PYTHONHASHSEED=0 nohup nice -n 1 python3 sim_pivotmarathon.py $BASE $START $CHUNK >> "marathon_pivot_W${BASE}_${START}.log" 2>&1 &
    fi
  done
  if [ "$DONE" -eq 4 ]; then echo "$(date -u +%H:%M) ブロック${BASE}全4チャンク完走" >> shepherd_pivot.log; break; fi
  sleep 60
done
