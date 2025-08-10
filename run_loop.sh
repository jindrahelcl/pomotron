#!/usr/bin/env bash
source venv/bin/activate
cd raspitron
export STORYTRON_URL="https://pomotron.cz"
export RASPITRON_TTS_LANG=cs
export RASPITRON_TTS_ENGINE=festival

while true; do
	./run.sh
	echo "Pomotron exited with code $? — restarting in 2 seconds."
	sleep 2
done
