#!/bin/bash
#
# Create new line mode and force a P2350 to an unsupported
# resolution of 1600x900
#
# This is only tested on a 2013-era lenovo U430 touch with hdmi output
# and a P2350 from about 2009?  The modeline below was generated with
# the cvt command: cvt 1600 900
#
# Usage:
# 1. Login to gnome.
# 2. Use the hardware video display keys to mirror the desktop.
#    You should see black bars on the sides of a 1024x768 resolution
#    display on both the laptop and the external monitor
#
# 3. Run this script
# 4. The external display should now turn into the primary at what looks
#    like full HD, and the laptop display is blank.
# 5. Use the hardware video display keys again to mirror the desktop.
# 6. You should now see a slightly blurry 1600x900 overscanned full
#     screen usage on the external and native 1600x900 on the laptop
xrandr --newmode "1600x900_60.00"  118.25  1600 1696 1856 2112  900 903 908 934 -hsync +vsync
xrandr --addmode HDMI-1 1600x900_60.00
