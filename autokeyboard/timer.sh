#!/bin/sh
#
pkill osd_cat
SECS=330
echo "sleeping $SECS" | osd_cat --delay 3
sleep $SECS
echo "timer is up " | osd_cat  --align=center  --font="-*-lucida-medium-r-*-*-34-240-*-*-*-*-*-*" --delay=100000000 --shadowcolour=white --pos=middle 

