#!/usr/bin/env bash

set -euo pipefail

lxterminal --title=Pomotron --working-directory=/home/trosos/pomotron --command='screen -dmS myserver && screen -X stuff "xdotool search --name Pomotron windowactivate; /home/trosos/pomotron/run_loop.sh\n" && screen -r myserver'
