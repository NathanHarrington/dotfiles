#!/bin/bash
#
# X-windows only. As of 2018-01-01 wayland does not support xdotool
# sending of keystrokes.
#
# Create a shortcut in gnome mapped to ctrl-shift-5, then make sure the
# tmux window is focused.
#
INTRA_KEY_DELAY=0.05
sleep 0.8

# Do the command mode, buffer scroll, search backwards, look for python
# error, then press enter
xdotool key ctrl+a
sleep $INTRA_KEY_DELAY

xdotool type :
sleep $INTRA_KEY_DELAY

xdotool type r
sleep $INTRA_KEY_DELAY

xdotool type e
sleep $INTRA_KEY_DELAY

xdotool type s
sleep $INTRA_KEY_DELAY

xdotool type i
sleep $INTRA_KEY_DELAY

xdotool type z
sleep $INTRA_KEY_DELAY

xdotool type e
sleep $INTRA_KEY_DELAY

xdotool type -
sleep $INTRA_KEY_DELAY

xdotool type p
sleep $INTRA_KEY_DELAY

xdotool type a
sleep $INTRA_KEY_DELAY

xdotool type n
sleep $INTRA_KEY_DELAY

xdotool type e
sleep $INTRA_KEY_DELAY

xdotool key space
sleep $INTRA_KEY_DELAY

xdotool type -
sleep $INTRA_KEY_DELAY

xdotool type L
sleep $INTRA_KEY_DELAY

xdotool key space
sleep $INTRA_KEY_DELAY

xdotool type 3
sleep $INTRA_KEY_DELAY

xdotool type 0
sleep $INTRA_KEY_DELAY


xdotool key Return

