#!/bin/bash
# Update the cmus queue with the 'full spectrum' music which is usually
# metal. Anything that is low and high frequency, without words,
# suitable for drownning out the sounds of a house with 9 people in it.
AVAHINAME=192.168.0.70
PORT=5577
PASSWORD=cmuscontrolitifyouwant
QLIST=/home/nharrington/projects/dotfiles/sound_control/full_spectrum_music_queuelist.m3u
cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD -q $QLIST
cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD --next

