#!/bin/bash
# Lambda用 function.zip を生成: ./make_lambda_zip.sh [出力先(既定:./function.zip)]
# 中身 = app.py(シム) + battle-tower/tools/remote-audit(必要ファイルのみ) + battle-tower/data(CSV)
set -e
SP="$(cd "$(dirname "$0")" && pwd)"; OUT="${1:-$SP/function.zip}"
T=$(mktemp -d)
mkdir -p "$T/battle-tower/tools/remote-audit" "$T/battle-tower/data"
cd "$SP"
cp calc_matchups.py sim.py sim_teams.py sim_z4.py sim_z11.py sim_zsearch.py sim_v4marathon.py \
   advisor.py advisor_web.py jpnames.py lambda_handler.py "$T/battle-tower/tools/remote-audit/"
cp -r pokeemerald "$T/battle-tower/tools/remote-audit/pokeemerald"
cp ../../data/frontier_sets.csv ../../data/trainers.csv "$T/battle-tower/data/"
cat > "$T/app.py" <<'PY'
import sys, os
_R=os.path.join(os.path.dirname(os.path.abspath(__file__)), "battle-tower", "tools", "remote-audit")
sys.path.insert(0,_R); os.chdir(_R)
from lambda_handler import handler
PY
cd "$T"; rm -f "$OUT"; zip -qr "$OUT" .
cd /; rm -rf "$T"
echo "作成: $OUT ($(du -h "$OUT" | cut -f1))"
