#!/bin/bash
# Update the cmus queue with the 'full spectrum' music which is usually
# metal. Anything that is low and high frequency, without words,
# suitable for drownning out the sounds of a house with 9 people in it.
AVAHINAME=u430.local
PORT=5577
PASSWORD=cmuscontrolitifyouwant

FLD=/home/nharrington/projects/dotfiles/sound_control
cat $FLD/full_spectrum_music_queuelist.m3u | shuf > $FLD/shuf_list.m3u

cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD -q $FLD/shuf_list.m3u
cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD --next

