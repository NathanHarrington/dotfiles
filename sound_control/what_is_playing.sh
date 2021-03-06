#!/bin/sh
#
# Display the currently playing track name in cmus using xosd
#
#  Prereqs: dnf install xosd
#
# Bind in gnome to ctrl+alt+shift+w
AVAHINAME=127.0.0.1
PORT=5577
PASSWORD=cmuscontrolitifyouwant


cmus-remote \
    --server $AVAHINAME:$PORT --passwd $PASSWORD -Q \
    | grep file \
    | osd_cat --align=center \
              --font=Variable --offset=450 \
              --outline=35 &

ps -aef | grep mplayer | grep mp3 | awk '{print $9}' \
    | osd_cat --align=center \
              --font=Variable --offset=550 \
              --color=white --outline=35 &

