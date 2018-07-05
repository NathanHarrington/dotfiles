#!/bin/bash
#
# Convenience function to move the pointer in defined increments from
# the command line.
#
# This is designed for movign the mouse with the keyboard so you can
# then issue a click command for websites that have broken keyboard
# navigation.
#
# Create files in /usr/bin:
# pointer_down|up|left|right
#
# With contents:
# /home/nharrington/projects/\
#    dotfiles/autokeyboard/move_pointer.sh # down|up|left|right
#
# Map those scripts to ctrl-up|down|left|right in gnome keyboard shortcuts

COMMAND="left"

if [[ $# -eq 1 ]] ; then
    COMMAND=$1
fi

if [[ "$COMMAND" == "left" ]] ; then
    COMMAND="-- -20 0"
fi

if [[ "$COMMAND" == "right" ]] ; then
    COMMAND="-- 20 0"
fi

if [[ "$COMMAND" == "up" ]] ; then
    COMMAND="-- 0 -20"
fi

if [[ "$COMMAND" == "down" ]] ; then
    COMMAND="-- 0 20"
fi


xdotool mousemove_relative $COMMAND
