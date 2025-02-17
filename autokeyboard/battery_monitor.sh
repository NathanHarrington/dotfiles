#!/bin/bash

while true; do
    # Get battery percentage
    BATTERY_LEVEL=$(acpi -b | grep -P -o '[0-9]+(?=%)')

    # Check if battery level is below 15%
    if [ "$BATTERY_LEVEL" -lt 25 ]; then
        # Display warning message using osd_cat
        echo "Battery Low: ${BATTERY_LEVEL}%" | osd_cat --align=center \
            --pos=bottom \
            --color=red \
            --delay=5 \
            --outline=2 \
            --font='-*-*-bold-*-*-*-36-*-*-*-*-*-*-*'
    fi

    # Sleep for 1 minute before next check
    sleep 60
done 
