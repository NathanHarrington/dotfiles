#!/bin/bash
# Stop cmus current playing, play the classical folders, then restart
/home/nharrington/projects/dotfiles/sound_control/cmus_remote_control.sh pause
mplayer /home/nharrington/Downloads/refined_mp3s/classical/*
mplayer /home/nharrington/Downloads/refined_mp3s/bach/*
mplayer /home/nharrington/Downloads/refined_mp3s/beethoven/*
/home/nharrington/projects/dotfiles/sound_control/cmus_remote_control.sh pause
