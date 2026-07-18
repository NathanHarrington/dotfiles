#!/usr/bin/env bash
set -u

SCREEN_OFF_SECONDS="${SUSPEND_ON_BATTERY_SCREEN_OFF_SECONDS:-300}"
SUSPEND_SECONDS="${SUSPEND_ON_BATTERY_IDLE_SECONDS:-600}"
SLEEP_ACTION="${SUSPEND_ON_BATTERY_SLEEP_ACTION:-hibernate}"
DEBUG="${SUSPEND_ON_BATTERY_DEBUG:-0}"
XIDLEHOOK="${XIDLEHOOK:-xidlehook}"
XAUTOLOCK="${XAUTOLOCK:-xautolock}"
XSET="${XSET:-xset}"
SYSTEMCTL="${SYSTEMCTL:-systemctl}"
LOCK_FILE="${SUSPEND_ON_BATTERY_IDLE_LOCK:-${XDG_RUNTIME_DIR:-/tmp}/suspend-on-battery-idle.lock}"
DPMS_POLL_SECONDS="${SUSPEND_ON_BATTERY_DPMS_POLL_SECONDS:-15}"
DPMS_PID=

log() {
    if command -v logger >/dev/null 2>&1; then
        logger -t suspend-on-battery-idle -- "$*" 2>/dev/null || true
    fi
    printf '%s\n' "$*" >&2
}

read_first_line() {
    local file=$1
    local value=

    if [ -r "$file" ]; then
        IFS= read -r value <"$file" || true
    fi

    printf '%s\n' "$value"
}

on_battery_power() {
    local supply type online
    local battery_found=0
    local external_power_online=0

    for supply in /sys/class/power_supply/*; do
        [ -e "$supply" ] || continue

        type=$(read_first_line "$supply/type")
        case "$type" in
            Battery)
                battery_found=1
                ;;
            Mains|USB|USB_C|USB_PD)
                online=$(read_first_line "$supply/online")
                [ "$online" = "1" ] && external_power_online=1
                ;;
        esac
    done

    [ "$battery_found" -eq 1 ] && [ "$external_power_online" -eq 0 ]
}

screen_off_if_on_battery() {
    if ! on_battery_power; then
        return 0
    fi

    if fullscreen_active; then
        log "screen-off threshold reached on battery power, but a fullscreen window is active; not turning screen off"
        return 0
    fi

    if ! command -v "$XSET" >/dev/null 2>&1; then
        log "xset not found; cannot turn screen off"
        return 1
    fi

    log "screen-off threshold reached on battery power; activating screensaver and turning screen off"
    "$XSET" s activate
    "$XSET" dpms force off
}

set_screen_off_timeout() {
    local seconds=$1

    command -v "$XSET" >/dev/null 2>&1 || return 1
    "$XSET" s "$seconds" "$seconds"
    "$XSET" +dpms
    "$XSET" dpms "$seconds" "$seconds" "$seconds"
}

disable_screen_off_timeout() {
    command -v "$XSET" >/dev/null 2>&1 || return 1
    "$XSET" s off
    "$XSET" dpms 0 0 0
}

dpms_manager() {
    local applied=unknown
    local wanted

    if ! command -v "$XSET" >/dev/null 2>&1; then
        log "xset not found; cannot manage screen-off timeout"
        return 1
    fi

    while true; do
        if on_battery_power && ! fullscreen_active; then
            wanted=battery
        else
            wanted=disabled
        fi

        if [ "$wanted" != "$applied" ]; then
            case "$wanted" in
                battery)
                    log "setting battery screen-off/lock timeout to ${SCREEN_OFF_SECONDS}s"
                    set_screen_off_timeout "$SCREEN_OFF_SECONDS" || true
                    ;;
                disabled)
                    log "disabling helper-managed screen-off/lock timeout"
                    disable_screen_off_timeout || true
                    ;;
            esac
            applied=$wanted
        fi

        sleep "$DPMS_POLL_SECONDS"
    done
}

suspend_if_on_battery() {
    local status

    case "$SLEEP_ACTION" in
        suspend|hibernate|hybrid-sleep|suspend-then-hibernate)
            ;;
        *)
            log "unsupported sleep action: $SLEEP_ACTION"
            return 2
            ;;
    esac

    if ! on_battery_power; then
        log "idle threshold reached, but external power is connected or no battery was found; not running $SLEEP_ACTION"
        return 0
    fi

    if fullscreen_active; then
        log "idle threshold reached on battery power, but a fullscreen window is active; not running $SLEEP_ACTION"
        return 0
    fi

    if audio_playing; then
        log "idle threshold reached on battery power, but audio is playing; not running $SLEEP_ACTION"
        return 0
    fi

    log "idle threshold reached on battery power; running $SLEEP_ACTION"
    "$SYSTEMCTL" "$SLEEP_ACTION"
    status=$?
    log "$SLEEP_ACTION command exited with status $status"
    return "$status"
}

fullscreen_active() {
    command -v i3-msg >/dev/null 2>&1 || return 1
    command -v jq >/dev/null 2>&1 || return 1

    i3-msg -t get_tree 2>/dev/null |
        jq -e '.. | objects | select((.window? // null) != null and (.fullscreen_mode? // 0) > 0)' >/dev/null
}

audio_playing() {
    command -v pactl >/dev/null 2>&1 || return 1
    pactl list sink-inputs 2>/dev/null | grep -q 'State: RUNNING'
}

take_lock() {
    local lock_file=$LOCK_FILE
    local user_id

    command -v flock >/dev/null 2>&1 || return 0

    if ! { exec 9>"$lock_file"; } 2>/dev/null; then
        user_id=$(id -u 2>/dev/null || printf 'unknown')
        lock_file="/tmp/suspend-on-battery-idle.${user_id}.lock"

        if ! { exec 9>"$lock_file"; } 2>/dev/null; then
            log "could not create lock file; continuing without duplicate-process protection"
            return 0
        fi
    fi

    if ! flock -n 9; then
        log "another suspend-on-battery-idle watcher is already running"
        exit 0
    fi
}

cleanup() {
    if [ -n "${DPMS_PID:-}" ]; then
        kill "$DPMS_PID" 2>/dev/null || true
    fi
    disable_screen_off_timeout >/dev/null 2>&1 || true
}

watch_idle() {
    local script_path=$0
    local remaining_seconds suspend_minutes xautolock_status
    local xautolock_args

    take_lock

    case "$script_path" in
        /*)
            ;;
        *)
            script_path="$(pwd)/$script_path"
            ;;
    esac

    if command -v "$XIDLEHOOK" >/dev/null 2>&1; then
        remaining_seconds=$((SUSPEND_SECONDS - SCREEN_OFF_SECONDS))
        [ "$remaining_seconds" -lt 1 ] && remaining_seconds=1

        log "starting $XIDLEHOOK: screen off/lock after ${SCREEN_OFF_SECONDS}s, $SLEEP_ACTION after ${SUSPEND_SECONDS}s"
        exec "$XIDLEHOOK" \
            --detect-sleep \
            --not-when-fullscreen \
            --timer normal "$SCREEN_OFF_SECONDS" \
                "$script_path --screen-off-if-on-battery" \
                '' \
            --timer normal "$remaining_seconds" \
                "$script_path --suspend-if-on-battery" \
                ''
    fi

    if command -v "$XAUTOLOCK" >/dev/null 2>&1; then
        suspend_minutes=$(((SUSPEND_SECONDS + 59) / 60))
        [ "$suspend_minutes" -lt 1 ] && suspend_minutes=1

        xautolock_args=(
            -detectsleep
            -time "$suspend_minutes"
            -locker "$script_path --suspend-if-on-battery"
        )

        if [ "$DEBUG" = "1" ]; then
            xautolock_args=(-noclose "${xautolock_args[@]}")
        fi

        dpms_manager &
        DPMS_PID=$!
        trap cleanup EXIT TERM INT

        log "started screen-off/lock manager pid=$DPMS_PID: screen off/lock after ${SCREEN_OFF_SECONDS}s on battery"
        log "starting $XAUTOLOCK: screen off/lock after ${SCREEN_OFF_SECONDS}s, $SLEEP_ACTION after ${SUSPEND_SECONDS}s"
        "$XAUTOLOCK" "${xautolock_args[@]}"
        xautolock_status=$?
        log "$XAUTOLOCK exited with status $xautolock_status"
        return "$xautolock_status"
    fi

    log "no idle watcher found; install xautolock with: sudo dnf install xautolock"
    exit 1
}

case "${1:---watch}" in
    --watch)
        watch_idle
        ;;
    --settings)
        cat <<EOF
screen_off_seconds=$SCREEN_OFF_SECONDS
suspend_seconds=$SUSPEND_SECONDS
sleep_action=$SLEEP_ACTION
debug=$DEBUG
dpms_poll_seconds=$DPMS_POLL_SECONDS
xidlehook=$XIDLEHOOK
xautolock=$XAUTOLOCK
xset=$XSET
systemctl=$SYSTEMCTL
lock_file=$LOCK_FILE
EOF
        ;;
    --screen-off-if-on-battery)
        screen_off_if_on_battery
        ;;
    --suspend-if-on-battery)
        suspend_if_on_battery
        ;;
    --check)
        if on_battery_power; then
            echo "on battery"
        else
            echo "external power connected or no battery found"
        fi
        ;;
    -h|--help)
        cat <<EOF
Usage: $0 [--watch|--settings|--screen-off-if-on-battery|--suspend-if-on-battery|--check]

Starts xidlehook when available, otherwise xautolock. By default it activates
the X screensaver and turns the screen off after ${SCREEN_OFF_SECONDS} seconds
of X idle time, and runs ${SLEEP_ACTION} after ${SUSPEND_SECONDS} seconds, only when a
battery is present and no external power supply is online.

xautolock uses whole-minute sleep-action timers, so this script rounds
${SUSPEND_SECONDS} seconds up to the nearest minute when using xautolock.

Environment overrides:
  SUSPEND_ON_BATTERY_SCREEN_OFF_SECONDS=${SCREEN_OFF_SECONDS}
  SUSPEND_ON_BATTERY_IDLE_SECONDS=${SUSPEND_SECONDS}
  SUSPEND_ON_BATTERY_SLEEP_ACTION=${SLEEP_ACTION}
  SUSPEND_ON_BATTERY_DEBUG=${DEBUG}
  SUSPEND_ON_BATTERY_DPMS_POLL_SECONDS=${DPMS_POLL_SECONDS}
  SUSPEND_ON_BATTERY_IDLE_LOCK=${LOCK_FILE}
  XIDLEHOOK=${XIDLEHOOK}
  XAUTOLOCK=${XAUTOLOCK}
  XSET=${XSET}
  SYSTEMCTL=${SYSTEMCTL}
EOF
        ;;
    *)
        echo "unknown argument: $1" >&2
        exit 2
        ;;
esac
