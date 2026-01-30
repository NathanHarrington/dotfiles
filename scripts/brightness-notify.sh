#!/bin/bash

# Get the current brightness percentage
get_brightness() {
    local current max

    current=$(brightnessctl get 2>/dev/null)
    max=$(brightnessctl max 2>/dev/null)

    if [ -z "$current" ] || [ -z "$max" ] || [ "$max" -eq 0 ]; then
        echo 0
        return
    fi

    echo $((current * 100 / max))
}

# Function to create a bar graph using ASCII characters
create_bar_graph() {
    local percentage=$1
    local width=20  # Number of characters in the bar
    local filled=$((percentage * width / 100))
    local empty=$((width - filled))
    local bar=""

    # Create the filled portion with hash characters
    for ((i=0; i<filled; i++)); do
        bar+="#"
    done

    # Create the empty portion with dash characters
    for ((i=0; i<empty; i++)); do
        bar+="-"
    done

    echo "$bar"
}

# Get the current brightness
brightness=$(get_brightness)

# Create the bar graph
bar=$(create_bar_graph "$brightness")

# Create and display the new notification
{
    echo "Brightness: ${brightness}%"
    echo "[${bar}]"
    echo "$(date '+%Y-%m-%d %H:%M:%S')"
} | osd_cat \
    --align=center \
    --pos=bottom \
    --offset=50 \
    --delay=1 \
    --outline=1 \
    --font='-*-*-bold-*-*-*-36-*-*-*-*-*-*-*' \
    --colour=yellow \
    --lines=3 &

# Give the new notification a moment to start
sleep 0.01

# Only kill older notifications if there are multiple osd_cat processes running
if [ "$(pgrep -c osd_cat)" -gt 1 ]; then
    pkill -o osd_cat
fi
