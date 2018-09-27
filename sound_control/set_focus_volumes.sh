#!/bin/sh
#
# Set the noise + music mix volumes to the default 'focus' levels.
#
# Run this from a /usr/bin/music_focus_level script, then map to keyboard
# shortcut: Ctrl+Shift+F10 (mute)
amixer set Master 43%

/home/nharrington/projects/dotfiles/sound_control/sink_volume.py \
--name 'C* Music Player' --exact 0.8

/home/nharrington/projects/dotfiles/sound_control/sink_volume.py \
--name 'SoX' --exact 0.82

