#!/bin/bash
# Update the cmus queue with the classical mps
# Bind in gnome to ctrl+alt+shift+c
AVAHINAME=127.0.0.1
PORT=5577
PASSWORD=cmuscontrolitifyouwant

/home/nharrington/projects/dotfiles/sound_control/clear_playlist.sh

FLD=/home/nharrington/projects/dotfiles/sound_control
LIST_FILE=$FLD/classical_cmus_queuelist.m3u
MUSIC_FOLDER=/home/nharrington/Downloads/refined_mp3s

ls -1 ${MUSIC_FOLDER}/bach/* > $LIST_FILE
ls -1 ${MUSIC_FOLDER}/beethoven/* >> $LIST_FILE
ls -1 ${MUSIC_FOLDER}/classical/* >> $LIST_FILE

cat $LIST_FILE | shuf > $FLD/shuf_list.m3u

cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD -q $FLD/shuf_list.m3u
cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD --next

