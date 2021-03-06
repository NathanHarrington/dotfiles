#!/bin/bash
# Update the cmus queue with haendel only
# Bind in gnome to ctrl+alt+shift+f
AVAHINAME=127.0.0.1
PORT=5577
PASSWORD=cmuscontrolitifyouwant

/home/nharrington/projects/dotfiles/sound_control/clear_playlist.sh

FLD=/home/nharrington/projects/dotfiles/sound_control
DIRNAME="/home/nharrington/raw_data/pre2020_u430_reload/refined_mp3s/classical/"
echo "$DIRNAME/G._F._Haendel_-_Organ_Concertos.mp3"  \
    > $FLD/shuf_list.m3u

cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD -q $FLD/shuf_list.m3u
cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD --next

