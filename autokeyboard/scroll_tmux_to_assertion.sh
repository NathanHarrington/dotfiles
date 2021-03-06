#!/bin/bash
#
# X-windows only. As of 2018-01-01 wayland does not support xdotool
# sending of keystrokes.
#
# Create a shortcut in gnome mapped to ctrl-shift-6, then make sure the
# tmux window is focused.
#
INTRA_KEY_DELAY=0.05
sleep 0.8

# Do the command mode, buffer scroll, search backwards, look for python
# error, then press enter
xdotool key ctrl+a
sleep $INTRA_KEY_DELAY

xdotool type [
sleep $INTRA_KEY_DELAY

xdotool type ?
sleep $INTRA_KEY_DELAY

xdotool type E
sleep $INTRA_KEY_DELAY

xdotool key space
sleep $INTRA_KEY_DELAY

xdotool key space
sleep $INTRA_KEY_DELAY

xdotool key space
sleep $INTRA_KEY_DELAY

xdotool key space
sleep $INTRA_KEY_DELAY

xdotool key Return

