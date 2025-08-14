#!/usr/bin/env bash
set -euo pipefail

TITLE="Pomotron"
TERM_CMD="lxterminal --title=$TITLE --working-directory=$HOME/pomotron --command=\"/bin/bash -lc 'screen -dmS myserver && screen -X stuff '$HOME/pomotron/run_loop.sh\\\\\\\\\\\\\\\\n' && screen -r myserver'\""

# Launch terminal
bash -lc "$TERM_CMD"
