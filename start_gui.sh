#!/usr/bin/env bash
set -euo pipefail

TERM_CMD="lxterminal --title=Pomotron --working-directory=$HOME/pomotron --command=\"screen -dmS myserver && screen -X stuff 'xdotool search --name Pomotron windowactivate; $HOME/pomotron/run_loop.sh\\\\n' && screen -r myserver\""


# Launch terminal
bash -lc "$TERM_CMD"
