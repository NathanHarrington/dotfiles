#!/bin/sh
#
# Simple script to send forward, next, back commands across the lan to
# the cmus audio application running on a different computer.
#
# Assumes cmus is running on a system with:
# cmus --listen avahi_servername:port
# (The the user types set:passwd=<password>
#
# Bind this script in gnome like:
# ctrl+alt+]  <full_path>/cmus_remote_control.sh next
# ctrl+alt+[  <full_path>/cmus_remote_control.sh previous
# ctrl+alt+l  <full_path>/cmus_remote_control.sh pause
#

AVAHINAME=127.0.0.1
PORT=5577
PASSWORD=cmuscontrolitifyouwant

COMMAND=pause

if [[ $# -eq 1 ]] ; then
    COMMAND=$1
fi

if [[ "$COMMAND" == "seek_forward" ]] ; then
    COMMAND="seek +1m"
fi

if [[ "$COMMAND" == "seek_backward" ]] ; then
    COMMAND="seek -1m"
fi

cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD --$COMMAND


