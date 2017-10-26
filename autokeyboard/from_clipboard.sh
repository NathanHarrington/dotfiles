#!/bin/bash
# copy the contents of a file to the system clipboard, then paste then
# in using ctrl+v
#
# Use gnome keyboard shortcuts and assign to ctrl+alt+shift+v
#
export FILENAME=~/Documents/text_template.txt

cat $FILENAME | xclip -in
if [ ! -f $FILENAME ]; then
    echo "$FILENAME does not exist!" | xclip -in
fi

sleep 1.5

xdotool key ctrl+v
