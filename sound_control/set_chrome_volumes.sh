#!/bin/sh
#
# Set the noise + music mix volumes to the default watching a video on
# youtube levels.
# Set to ctrl+win+alt+c
#
#amixer set Master 50%
#amixer set Master unmute
PM=~/projects/pulsemixer/pulsemixer

$PM --list \
  | grep -i sox \
  | awk '{print $4}' \
  | tr ',' ' ' \
  | while read line; do $PM --id $line --mute; done

$PM --list \
  | grep -i music\
  | awk '{print $4}' \
  | tr ',' ' ' \
  | while read line; do $PM --id $line --mute; done


$PM --list \
  | grep -i chrome\
  | awk '{print $4}' \
  | tr ',' ' ' \
  | while read line; do $PM --id $line --unmute; done

