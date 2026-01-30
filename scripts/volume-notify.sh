#!/bin/bash

# Get the current volume and mute status
get_volume() {
    pactl get-sink-volume @DEFAULT_SINK@ | grep -Po '[0-9]{1,3}(?=%)' | head -1
}

get_mute() {
    pactl get-sink-mute @DEFAULT_SINK@ | grep -Po '(?<=Mute: )(yes|no)'
}

# Get the current mic mute status
get_mic_mute() {
    pactl get-source-mute @DEFAULT_SOURCE@ | grep -Po '(?<=Mute: )(yes|no)'
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

# Format toggle lines using ASCII art
format_toggle() {
    local label=$1
    local state=$2
    local box="[ ]"

    if [ "$state" = "yes" ]; then
        box="[X]"
    fi

    printf "%-8s %s" "$label" "$box"
}

# Get the current volume and mute status
volume=$(get_volume)
mute=$(get_mute)
mic_mute=$(get_mic_mute)

# Create the bar graph
bar=$(create_bar_graph "$volume")

# Create and display the new notification
if [ "$mute" = "yes" ]; then
    header="Volume: Muted"
    colour="red"
else
    header="Volume: ${volume}%"
    colour="green"
fi

{
    echo "$header"
    echo "[${bar}]"
    echo "$(format_toggle "MUTE" "$mute")"
    echo "$(format_toggle "MIC MUTE" "$mic_mute")"
    echo "$(date '+%Y-%m-%d %H:%M:%S')"
} | osd_cat \
    --align=center \
    --pos=bottom \
    --offset=50 \
    --delay=1 \
    --outline=1 \
    --font='-*-*-bold-*-*-*-36-*-*-*-*-*-*-*' \
    --colour="$colour" \
    --lines=5 &

# Give the new notification a moment to start
sleep 0.01

# Only kill older notifications if there are multiple osd_cat processes running
if [ "$(pgrep -c osd_cat)" -gt 1 ]; then
    pkill -o osd_cat
fi 
