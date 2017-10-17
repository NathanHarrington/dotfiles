#!/bin/bash
#
# Create a shortcut in gnome mapped to ctrl-shift-g, then make sure the
# w3m window is focused.
#
# TODO: Verify that the w3m application has the input
#
INTRA_KEY_DELAY=0.05
# Open new tab
sleep 0.3
xdotool key "T"

# Goto url
sleep INTRA_KEY_DELAY
xdotool key "U"

# Clear URL bar, type google, press enter
sleep INTRA_KEY_DELAY
xdotool key ctrl+u
sleep INTRA_KEY_DELAY
xdotool key g
sleep INTRA_KEY_DELAY
xdotool key o
sleep INTRA_KEY_DELAY
xdotool key o
sleep INTRA_KEY_DELAY
xdotool key g
sleep INTRA_KEY_DELAY
xdotool key l
sleep INTRA_KEY_DELAY
xdotool key e
sleep INTRA_KEY_DELAY
xdotool key period
sleep INTRA_KEY_DELAY
xdotool key c
sleep INTRA_KEY_DELAY
xdotool key o
sleep INTRA_KEY_DELAY
xdotool key m
sleep INTRA_KEY_DELAY
xdotool key Return

# 13 tabs', then press enter
sleep 0.5
xdotool key Tab
xdotool key Tab
xdotool key Tab
xdotool key Tab
xdotool key Tab
xdotool key Tab
xdotool key Tab
xdotool key Tab
xdotool key Tab
xdotool key Tab
xdotool key Tab
xdotool key Tab
xdotool key Tab
xdotool key Return
