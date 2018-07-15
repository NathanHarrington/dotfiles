#!/bin/bash
#
# Convenience function to send the scroll event which is mouse button 5
# click
#
# This is designed for scrolling google calendar which does not seem to
# support the keyboard scroll in any way.
#
# Map this to ctrl-alt-super-d in gnome keyboard shortcuts
sleep 1
xdotool click 5
