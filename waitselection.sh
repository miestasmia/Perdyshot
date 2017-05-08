#!/usr/bin/env bash

cd /home/mia/Documents/Code/Perdyshot
sleep 2
cli/selection.py -f /tmp/perdyselection.png
xclip -i -sel clip -t image/png < /tmp/perdyselection.png
