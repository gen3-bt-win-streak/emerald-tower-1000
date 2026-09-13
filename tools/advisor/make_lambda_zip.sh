#!/bin/bash
# Lambda用 function.zip を生成: ./make_lambda_zip.sh [出力先(既定:./function.zip)]
# 中身 = app.py + battle-tower/tools/{engine,sim,advisor}(必要ファイルのみ・リポジトリと同じ相対配置) + battle-tower/data(CSV)
set -e
SP="$(cd "$(dirname "$0")" && pwd)"; TOOLS="$(cd "$SP/.." && pwd)"; OUT="${1:-$SP/function.zip}"
T=$(mktemp -d)
mkdir -p "$T/battle-tower/tools/engine" "$T/battle-tower/tools/sim" "$T/battle-tower/tools/advisor" "$T/battle-tower/data"
cp "$TOOLS/engine/calc_matchups.py" "$TOOLS/engine/jpnames.py" "$T/battle-tower/tools/engine/"
cp -r "$TOOLS/engine/pokeemerald" "$T/battle-tower/tools/engine/pokeemerald"
cp "$TOOLS/sim/sim.py" "$TOOLS/sim/sim_teams.py" "$TOOLS/sim/sim_z4.py" "$TOOLS/sim/sim_z11.py" \
   "$TOOLS/sim/sim_zsearch.py" "$TOOLS/sim/sim_v4marathon.py" "$T/battle-tower/tools/sim/"
cp "$SP/advisor.py" "$SP/advisor_web.py" "$SP/lambda_handler.py" "$T/battle-tower/tools/advisor/"
cp "$TOOLS/../data/frontier_sets.csv" "$TOOLS/../data/trainers.csv" "$T/battle-tower/data/"
cat > "$T/app.py" <<'PY'
import sys, os
_R=os.path.join(os.path.dirname(os.path.abspath(__file__)), "battle-tower", "tools", "advisor")
sys.path.insert(0,_R); os.chdir(_R)
from lambda_handler import handler
PY
cd "$T"; rm -f "$OUT"; zip -qr "$OUT" .
cd /; rm -rf "$T"
echo "作成: $OUT ($(du -h "$OUT" | cut -f1))"
