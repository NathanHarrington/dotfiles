#!/bin/sh
#
# Set the noise + music mix volumes to the default 'exercise' levels.
#
amixer set Master 66%

/home/nharrington/projects/dotfiles/sound_control/sink_volume.py \
--name 'C* Music Player' --exact 0.82

/home/nharrington/projects/dotfiles/sound_control/sink_volume.py \
--name 'MPlayer' --exact 0.88

/home/nharrington/projects/dotfiles/sound_control/sink_volume.py \
--name 'SoX' --exact 0.0
