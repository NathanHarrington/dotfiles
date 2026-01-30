#!/bin/bash

# Get the keyboard backlight device name.
get_kbd_device() {
    if [ -n "${BRIGHTNESSCTL_DEVICE:-}" ]; then
        echo "$BRIGHTNESSCTL_DEVICE"
        return 0
    fi

    brightnessctl -l 2>/dev/null | awk -F"'" '
        /Device/ {
            name=$2
            class=$4
            if (class == "leds" && tolower(name) ~ /(kbd|keyboard)/) {
                print name
                exit
            }
        }
    '
}

# Get the current keyboard backlight percentage for a device.
get_brightness() {
    local device=$1
    local current max

    if [ -z "$device" ]; then
        return 1
    fi

    current=$(brightnessctl -d "$device" get 2>/dev/null) || return 1
    max=$(brightnessctl -d "$device" max 2>/dev/null) || return 1

    if [ -z "$current" ] || [ -z "$max" ] || [ "$max" -eq 0 ]; then
        return 1
    fi

    echo $((current * 100 / max))
}

# Function to create a bar graph using ASCII characters.
create_bar_graph() {
    local percentage=$1
    local width=20  # Number of characters in the bar
    local filled=$((percentage * width / 100))
    local empty=$((width - filled))
    local bar=""

    # Create the filled portion with hash characters.
    for ((i=0; i<filled; i++)); do
        bar+="#"
    done

    # Create the empty portion with dash characters.
    for ((i=0; i<empty; i++)); do
        bar+="-"
    done

    echo "$bar"
}

# Get the keyboard backlight device and brightness.
device=$(get_kbd_device)
if brightness=$(get_brightness "$device"); then
    label="Keyboard Backlight: ${brightness}%"
    bar=$(create_bar_graph "$brightness")
    colour="cyan"
else
    label="Keyboard Backlight: N/A"
    bar=$(create_bar_graph 0)
    colour="red"
fi

# Create and display the new notification.
{
    echo "$label"
    echo "[${bar}]"
    echo "$(date '+%Y-%m-%d %H:%M:%S')"
} | osd_cat \
    --align=center \
    --pos=bottom \
    --offset=50 \
    --delay=1 \
    --outline=1 \
    --font='-*-*-bold-*-*-*-36-*-*-*-*-*-*-*' \
    --colour="$colour" \
    --lines=3 &

# Give the new notification a moment to start.
sleep 0.01

# Only kill older notifications if there are multiple osd_cat processes running.
if [ "$(pgrep -c osd_cat)" -gt 1 ]; then
    pkill -o osd_cat
fi
