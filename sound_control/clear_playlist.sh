# Issue 100 cmus next commands to make sure it gets through any existing
# playlists, then on to the rock list

#!/bin/bash
for i in {1..100}
do
   /home/nharrington/projects/dotfiles/sound_control/cmus_remote_control.sh next
   sleep 0.01
done
