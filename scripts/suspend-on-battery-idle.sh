#!/usr/bin/env bash
set -u

SCREEN_OFF_SECONDS="${SUSPEND_ON_BATTERY_SCREEN_OFF_SECONDS:-300}"
SUSPEND_SECONDS="${SUSPEND_ON_BATTERY_IDLE_SECONDS:-600}"
SLEEP_ACTION="${SUSPEND_ON_BATTERY_SLEEP_ACTION:-hibernate}"
SCREEN_OFF_ON_AC="${SUSPEND_ON_BATTERY_SCREEN_OFF_ON_AC:-1}"
DEBUG="${SUSPEND_ON_BATTERY_DEBUG:-0}"
XIDLEHOOK="${XIDLEHOOK:-xidlehook}"
XAUTOLOCK="${XAUTOLOCK:-xautolock}"
XSET="${XSET:-xset}"
XSS_LOCK="${XSS_LOCK:-xss-lock}"
I3LOCK="${I3LOCK:-i3lock}"
SYSTEMCTL="${SYSTEMCTL:-systemctl}"
LOCK_FILE="${SUSPEND_ON_BATTERY_IDLE_LOCK:-${XDG_RUNTIME_DIR:-/tmp}/suspend-on-battery-idle.lock}"
DPMS_POLL_SECONDS="${SUSPEND_ON_BATTERY_DPMS_POLL_SECONDS:-15}"
XSS_LOCK_POLL_SECONDS="${SUSPEND_ON_BATTERY_XSS_LOCK_POLL_SECONDS:-30}"
DPMS_PID=
XSS_LOCK_MANAGER_PID=

log() {
    if command -v logger >/dev/null 2>&1; then
        logger -t suspend-on-battery-idle -- "$*" 2>/dev/null || true
    fi
    printf '%s\n' "$*" >&2
}

close_lock_fd() {
    { exec 9>&-; } 2>/dev/null || true
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

truthy() {
    case "$1" in
        1|true|TRUE|yes|YES|on|ON)
            return 0
            ;;
    esac

    return 1
}

screen_off_allowed() {
    if truthy "$SCREEN_OFF_ON_AC"; then
        return 0
    fi

    on_battery_power
}

screen_off_scope() {
    if truthy "$SCREEN_OFF_ON_AC"; then
        printf 'all power states'
    else
        printf 'battery only'
    fi
}

screen_off_if_allowed() {
    if ! screen_off_allowed; then
        return 0
    fi

    if fullscreen_active; then
        log "screen-off threshold reached, but a fullscreen window is active; not turning screen off"
        return 0
    fi

    if ! command -v "$XSET" >/dev/null 2>&1; then
        log "xset not found; cannot turn screen off"
        return 1
    fi

    log "screen-off threshold reached; activating screensaver and turning screen off"
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

    close_lock_fd

    if ! command -v "$XSET" >/dev/null 2>&1; then
        log "xset not found; cannot manage screen-off timeout"
        return 1
    fi

    while true; do
        if screen_off_allowed && ! fullscreen_active; then
            wanted=enabled
        else
            wanted=disabled
        fi

        if [ "$wanted" != "$applied" ]; then
            case "$wanted" in
                enabled)
                    log "setting screen-off/lock timeout to ${SCREEN_OFF_SECONDS}s ($(screen_off_scope))"
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

start_xss_lock_once() {
    local user_id xss_lock_name

    if ! command -v "$XSS_LOCK" >/dev/null 2>&1; then
        log "xss-lock not found; automatic i3lock will not run"
        return 1
    fi

    if ! command -v "$I3LOCK" >/dev/null 2>&1; then
        log "i3lock not found; automatic screen locking will not run"
        return 1
    fi

    xss_lock_name=${XSS_LOCK##*/}
    if command -v pgrep >/dev/null 2>&1; then
        user_id=$(id -u 2>/dev/null || true)
        if [ -n "$user_id" ] && pgrep -xu "$user_id" "$xss_lock_name" >/dev/null 2>&1; then
            return 0
        fi
        if [ -z "$user_id" ] && pgrep -x "$xss_lock_name" >/dev/null 2>&1; then
            return 0
        fi
    fi

    log "starting $XSS_LOCK for automatic i3lock"
    (close_lock_fd; exec "$XSS_LOCK" --transfer-sleep-lock -- "$I3LOCK" --nofork) &
}

xss_lock_manager() {
    close_lock_fd

    while true; do
        start_xss_lock_once || true
        sleep "$XSS_LOCK_POLL_SECONDS"
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
        wait "$DPMS_PID" 2>/dev/null || true
    fi

    if [ -n "${XSS_LOCK_MANAGER_PID:-}" ]; then
        kill "$XSS_LOCK_MANAGER_PID" 2>/dev/null || true
        wait "$XSS_LOCK_MANAGER_PID" 2>/dev/null || true
    fi
}

terminate() {
    cleanup
    exit 0
}

watch_idle() {
    local script_path=$0
    local remaining_seconds suspend_minutes xidlehook_status xautolock_status
    local xautolock_args

    take_lock

    case "$script_path" in
        /*)
            ;;
        *)
            script_path="$(pwd)/$script_path"
            ;;
    esac

    xss_lock_manager &
    XSS_LOCK_MANAGER_PID=$!
    trap cleanup EXIT
    trap terminate TERM INT

    if command -v "$XIDLEHOOK" >/dev/null 2>&1; then
        remaining_seconds=$((SUSPEND_SECONDS - SCREEN_OFF_SECONDS))
        [ "$remaining_seconds" -lt 1 ] && remaining_seconds=1

        log "starting $XIDLEHOOK: screen off/lock after ${SCREEN_OFF_SECONDS}s, $SLEEP_ACTION after ${SUSPEND_SECONDS}s"
        while true; do
            (close_lock_fd; exec "$XIDLEHOOK" \
                --detect-sleep \
                --not-when-fullscreen \
                --timer normal "$SCREEN_OFF_SECONDS" \
                    "$script_path --screen-off-if-allowed" \
                    '' \
                --timer normal "$remaining_seconds" \
                    "$script_path --suspend-if-on-battery" \
                    '')
            xidlehook_status=$?
            log "$XIDLEHOOK exited with status $xidlehook_status; restarting"
            sleep 5
        done
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

        log "started screen-off/lock manager pid=$DPMS_PID: screen off/lock after ${SCREEN_OFF_SECONDS}s ($(screen_off_scope))"
        while true; do
            log "starting $XAUTOLOCK: screen off/lock after ${SCREEN_OFF_SECONDS}s, $SLEEP_ACTION after ${SUSPEND_SECONDS}s"
            (close_lock_fd; exec "$XAUTOLOCK" "${xautolock_args[@]}")
            xautolock_status=$?
            log "$XAUTOLOCK exited with status $xautolock_status; restarting"
            sleep 5
        done
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
screen_off_on_ac=$SCREEN_OFF_ON_AC
screen_off_scope=$(screen_off_scope)
debug=$DEBUG
dpms_poll_seconds=$DPMS_POLL_SECONDS
xss_lock_poll_seconds=$XSS_LOCK_POLL_SECONDS
xidlehook=$XIDLEHOOK
xautolock=$XAUTOLOCK
xset=$XSET
xss_lock=$XSS_LOCK
i3lock=$I3LOCK
systemctl=$SYSTEMCTL
lock_file=$LOCK_FILE
EOF
        ;;
    --screen-off-if-allowed|--screen-off-if-on-battery)
        screen_off_if_allowed
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
of X idle time in all power states, and runs ${SLEEP_ACTION} after
${SUSPEND_SECONDS} seconds only when a battery is present and no external power
supply is online.

xautolock uses whole-minute sleep-action timers, so this script rounds
${SUSPEND_SECONDS} seconds up to the nearest minute when using xautolock.

Environment overrides:
  SUSPEND_ON_BATTERY_SCREEN_OFF_SECONDS=${SCREEN_OFF_SECONDS}
  SUSPEND_ON_BATTERY_IDLE_SECONDS=${SUSPEND_SECONDS}
  SUSPEND_ON_BATTERY_SLEEP_ACTION=${SLEEP_ACTION}
  SUSPEND_ON_BATTERY_SCREEN_OFF_ON_AC=${SCREEN_OFF_ON_AC}
  SUSPEND_ON_BATTERY_DEBUG=${DEBUG}
  SUSPEND_ON_BATTERY_DPMS_POLL_SECONDS=${DPMS_POLL_SECONDS}
  SUSPEND_ON_BATTERY_XSS_LOCK_POLL_SECONDS=${XSS_LOCK_POLL_SECONDS}
  SUSPEND_ON_BATTERY_IDLE_LOCK=${LOCK_FILE}
  XIDLEHOOK=${XIDLEHOOK}
  XAUTOLOCK=${XAUTOLOCK}
  XSET=${XSET}
  XSS_LOCK=${XSS_LOCK}
  I3LOCK=${I3LOCK}
  SYSTEMCTL=${SYSTEMCTL}
EOF
        ;;
    *)
        echo "unknown argument: $1" >&2
        exit 2
        ;;
esac
