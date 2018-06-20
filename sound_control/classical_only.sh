#!/bin/bash
# Update the cmus queue with the classical mps
AVAHINAME=192.168.0.70
PORT=5577
PASSWORD=cmuscontrolitifyouwant
QLIST=/home/nharrington/projects/dotfiles/sound_control/classical_cmus_queuelist.m3u

FLD=/home/nharrington/projects/dotfiles/sound_control
cat $FLD/classical_cmus_queuelist.m3u | shuf > $FLD/shuf_list.m3u
cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD -q $FLD/shuf_list.m3u
cmus-remote --server $AVAHINAME:$PORT --passwd $PASSWORD --next

