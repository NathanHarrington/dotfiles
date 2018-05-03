#!/bin/bash
# Stop cmus current playing, play the handel organ concerto
/home/nharrington/projects/dotfiles/sound_control/cmus_remote_control.sh pause
mplayer "/home/nharrington/Downloads/refined_mp3s/classical/G._F._Haendel_-_Organ_Concertos.mp3"
/home/nharrington/projects/dotfiles/sound_control/cmus_remote_control.sh pause

