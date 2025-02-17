#!/bin/bash

# Get the current volume and mute status
get_volume() {
    pactl get-sink-volume @DEFAULT_SINK@ | grep -Po '[0-9]{1,3}(?=%)' | head -1
}

get_mute() {
    pactl get-sink-mute @DEFAULT_SINK@ | grep -Po '(?<=Mute: )(yes|no)'
}

# Function to create a bar graph using Unicode blocks
create_bar_graph() {
    local percentage=$1
    local width=20  # Number of characters in the bar
    local filled=$((percentage * width / 100))
    local empty=$((width - filled))
    local bar=""
    
    # Create the filled portion with full blocks
    for ((i=0; i<filled; i++)); do
        bar+="█"
    done
    
    # Create the empty portion with empty blocks
    for ((i=0; i<empty; i++)); do
        bar+="░"
    done
    
    echo "$bar"
}

# Get the current volume and mute status
volume=$(get_volume)
mute=$(get_mute)

# Create the bar graph
bar=$(create_bar_graph "$volume")

# Create and display the new notification
if [ "$mute" = "yes" ]; then
    {
        echo "Volume: Muted"
        echo "[${bar}]"
        echo "$(date '+%Y-%m-%d %H:%M:%S')"
    } | osd_cat \
        --align=center \
        --pos=bottom \
        --offset=50 \
        --delay=1 \
        --outline=1 \
        --font='-*-*-bold-*-*-*-36-*-*-*-*-*-*-*' \
        --colour=red \
        --lines=3 &
else
    {
        echo "Volume: ${volume}%"
        echo "[${bar}]"
        echo "$(date '+%Y-%m-%d %H:%M:%S')"
    } | osd_cat \
        --align=center \
        --pos=bottom \
        --offset=50 \
        --delay=1 \
        --outline=1 \
        --font='-*-*-bold-*-*-*-36-*-*-*-*-*-*-*' \
        --colour=green \
        --lines=3 &
fi

# Give the new notification a moment to start
sleep 0.01

# Only kill older notifications if there are multiple osd_cat processes running
if [ "$(pgrep -c osd_cat)" -gt 1 ]; then
    pkill -o osd_cat
fi 