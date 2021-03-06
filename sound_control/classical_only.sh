#!/bin/bash
# Update the cmus queue with the classical mps
# Bind in gnome to ctrl+alt+shift+c
AVAHINAME=127.0.0.1
PORT=5577
PASSWORD=cmuscontrolitifyouwant

/home/nharrington/projects/dotfiles/sound_control/clear_playlist.sh

FLD=/home/nharrington/projects/dotfiles/sound_control
LIST_FILE=$FLD/classical_cmus_queuelist.m3u
MUSIC_FOLDER=/usr/share/raw_data/refined_mp3s

ls -1 ${MUSIC_FOLDER}/bach/* |grep mp3 > $LIST_FILE
ls -1 ${MUSIC_FOLDER}/beethoven/* |grep mp3 >> $LIST_FILE
ls -1 ${MUSIC_FOLDER}/classical/* |grep mp3 >> $LIST_FILE
ls -1 ${MUSIC_FOLDER}/Handel_Edition/* | grep mp3 >> $LIST_FILE

cat $LIST_FILE | shuf > $FLD/shuf_list.m3u

cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD -q $FLD/shuf_list.m3u
cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD --next
