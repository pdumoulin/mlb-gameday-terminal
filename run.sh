#!/bin/bash

set -e

clear && printf '\e[3J'

python run.py "$@"
if [ -n "$WATCH_MLB" ]; then
    watch -t -d -n $WATCH_MLB python run.py "$@"
fi
