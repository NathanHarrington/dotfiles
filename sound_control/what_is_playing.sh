#!/bin/sh
#
# Display the currently playing track name in cmus using zenity
#
# Bind in gnome to ctrl+alt+mod+w
AVAHINAME=127.0.0.1
PORT=5577
PASSWORD=cmuscontrolitifyouwant


TEXT=`cmus-remote \
    --server $AVAHINAME:$PORT --passwd $PASSWORD -Q \
    | grep file`
SONG=$(echo $TEXT | awk -F/ '{print $NF}')
CMUS_TEXT="<span font='16'>$SONG</span>"

MPLAYER=$(ps -aef | grep mplayer | grep mp3 | awk '{print $9}')
MPLAYER_TEXT="\n\n<span font='16' color='red'>$MPLAYER</span>"

zenity --info --width=1000 --text="$CMUS_TEXT $MPLAYER_TEXT"

