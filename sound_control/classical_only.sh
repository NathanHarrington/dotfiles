#!/bin/bash
# Update the cmus queue with the classical mps
AVAHINAME=127.0.0.1
PORT=5577
PASSWORD=cmuscontrolitifyouwant

FLD=/home/nharrington/projects/dotfiles/sound_control
cat $FLD/classical_cmus_queuelist.m3u | shuf > $FLD/shuf_list.m3u

cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD -q $FLD/shuf_list.m3u
cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD --next

