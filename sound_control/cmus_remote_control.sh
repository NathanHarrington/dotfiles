#!/bin/sh
#
# Simple script to send forward, next, back commands across the lan to
# the cmus audio application running on a different computer (or your localhost)
#
# Assumes cmus is running on a system with:
# cmus --listen avahi_servername:port
# (The the user types set:passwd=<password>
#
# Bind this script in gnome or mate like shown below, where all the music and volume
# controls have the left side of the keyboard ctrl-alt-mod4 prefix
#
# ctrl+alt+Mod4+pagedown <full_path>/cmus_remote_control.sh seek_forward
# ctrl+alt+Mod4+pageup <full_path>/cmus_remote_control.sh seek_backward
#
# ctrl+alt+Mod4+] <full_path>/cmus_remote_control.sh next
# ctrl+alt+Mod4+[ <full_path>/cmus_remote_control.sh back

AVAHINAME=127.0.0.1
PORT=5577
PASSWORD=cmuscontrolitifyouwant

COMMAND=toggle

if [[ $# -eq 1 ]] ; then
   COMMAND=$1
fi

if [[ "$COMMAND" == "toggle" ]] ; then
    if [ -f ~/.config/cmus_playing ]; then
        rm ~/.config/cmus_playing
        COMMAND=pause
    else
        touch ~/.config/cmus_playing
        COMMAND=play
    fi
fi

if [[ "$COMMAND" == "seek_forward" ]] ; then
    COMMAND="seek +1m"
fi

if [[ "$COMMAND" == "seek_backward" ]] ; then
    COMMAND="seek -1m"
fi

cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD --$COMMAND


