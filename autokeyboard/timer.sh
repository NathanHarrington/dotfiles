#!/bin/sh
# Display a timer expired message on the screen, on top of all windows, on all desktops. 
# Designed to be run continuously - in gnome mate, bind this script to ctrl-shift-alt-t and when you see timer is up, start a new one. 
pkill osd_cat
#SECS=90 # 1.5 
#SECS=330 # 5.5 
SECS=450 # 7.5
echo "sleeping $SECS" | osd_cat --delay 3
sleep $SECS
echo "timer is up " | osd_cat  --align=center  --font="-*-*-bold-*-*-*-36-*-*-*-*-*-*-*" --delay=100000000 --shadowcolour=white --pos=middle 

