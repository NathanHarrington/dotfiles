#!/usr/bin/bash
# Temporarily pause/disconnect the AirPods, or resume automatic connection.
set -uo pipefail
export LC_ALL=C

device='20:F4:D4:73:76:79'
timer='airpods-autoconnect.timer'
service='airpods-autoconnect.service'
autoconnect='unknown'
connected='unknown'

notify() {
    local header=$1 colour=$2
    printf '%s\n' "$header"
    command -v osd_cat >/dev/null 2>&1 || return 0

    # Match ~/projects/dotfiles/scripts/volume-notify.sh.
    {
        printf '%s\n' "$header" "Nathan's Air pro" \
            "Auto-connect: $autoconnect" "Connected: $connected" \
            "$(date '+%Y-%m-%d %H:%M:%S')"
    } | osd_cat \
        --align=center \
        --pos=bottom \
        --offset=50 \
        --delay=1 \
        --outline=1 \
        --font='-*-*-bold-*-*-*-36-*-*-*-*-*-*-*' \
        --colour="$colour" \
        --lines=5 9>&- &

    sleep 0.01
    if [ "$(pgrep -u "$UID" -c -x osd_cat)" -gt 1 ]; then
        pkill -u "$UID" -o -x osd_cat || true
    fi
}

fail() {
    printf '%s\n' "$2" >&2
    notify "AirPods: $1" red
    exit 1
}

read_connection() {
    local info
    info=$(timeout 5s bluetoothctl info "$device" 2>/dev/null) || info=''
    case "$info" in
        *'Connected: yes'*) connected='yes' ;;
        *'Connected: no'*) connected='no' ;;
        *) connected='unknown' ;;
    esac
}

# Ignore overlapping invocations, such as repeated key presses during a connect.
exec 9>"${XDG_RUNTIME_DIR:-/tmp}/airpods-toggle-${UID}.lock" || exit 1
flock -n 9 || exit 0

timer_state=$(systemctl --user is-active "$timer")
case "$timer_state" in
    active|activating|reloading)
        autoconnect='on'
        systemctl --user stop "$timer" "$service" ||
            fail 'could not pause' 'Failed to stop the AirPods auto-connect timer/service.'
        autoconnect='off'

        read_connection
        if [[ "$connected" == 'unknown' ]]; then
            adapter_info=$(timeout 5s bluetoothctl show 2>/dev/null) || adapter_info=''
            if [[ "$adapter_info" == *'Powered: no'* ]]; then
                connected='no'
            else
                fail 'paused; connection unknown' 'Auto-connect is paused, but Bluetooth connection status could not be read.'
            fi
        fi

        if [[ "$connected" == 'yes' ]]; then
            disconnect_output=$(timeout 12s bluetoothctl --timeout 10 disconnect "$device" 2>&1)
            disconnect_status=$?
            read_connection
            if [[ "$connected" != 'no' ]]; then
                fail 'paused; disconnect failed' "Auto-connect is paused. Disconnect exited $disconnect_status: $disconnect_output"
            fi
        fi
        notify 'AirPods: laptop paused' red
        ;;
    inactive|failed)
        autoconnect='off'
        # Starting the helper too makes the first connection attempt immediate.
        systemctl --user start "$timer" "$service" ||
            fail 'could not resume' 'Failed to start the AirPods auto-connect timer/service.'
        autoconnect='on'
        read_connection
        notify 'AirPods: auto-connect on' green
        ;;
    *)
        fail 'timer unavailable' "Unexpected AirPods timer state: ${timer_state:-unavailable}"
        ;;
esac
