#!/usr/bin/env bash

cd "$( dirname "${BASH_SOURCE[0]}" )"

sleep 2
cli/selection.py -f /tmp/perdyselection.png
xclip -i -sel clip -t image/png < /tmp/perdyselection.png
