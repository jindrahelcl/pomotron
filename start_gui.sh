#!/usr/bin/env bash
set -euo pipefail

TITLE="Pomotron"
TERM_CMD="lxterminal --title=$TITLE --working-directory=$HOME/pomotron --command=\"/bin/bash -lc '$HOME/pomotron/run_loop.sh'\""

# Launch terminal
bash -lc "$TERM_CMD"
