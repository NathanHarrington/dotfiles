#!/usr/bin/env bash
set -u

IDLE_MINUTES="${AUTO_STOP_IDLE_MINUTES:-60}"
POLL_SECONDS="${AUTO_STOP_POLL_SECONDS:-300}"
XAUTHORITY_VALUE="${AUTO_STOP_XAUTHORITY:-/home/fedora/.Xauthority}"
LOG_FILE="${AUTO_STOP_LOG:-/var/log/auto-stop-idle.log}"
LOCK_FILE="${AUTO_STOP_LOCK:-/run/auto-stop-idle-x11.lock}"
XSSSTATE="${XSSSTATE:-/usr/bin/xssstate}"
SYSTEMCTL="${SYSTEMCTL:-/usr/bin/systemctl}"

log() {
    printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "$*" >&2
}

usage() {
    cat <<EOF
Usage: $0 [--start|--stop|--check]

Polls all discovered X displays. When every queryable display has been idle for
at least ${IDLE_MINUTES} minutes, powers off the system.

Environment overrides:
  AUTO_STOP_IDLE_MINUTES=${IDLE_MINUTES}
  AUTO_STOP_POLL_SECONDS=${POLL_SECONDS}
  AUTO_STOP_XAUTHORITY=${XAUTHORITY_VALUE}
  AUTO_STOP_DISPLAYS=":0 :99 :100"
  AUTO_STOP_LOG=${LOG_FILE}
  AUTO_STOP_LOCK=${LOCK_FILE}
EOF
}

require_root() {
    if [ "$(id -u)" -ne 0 ]; then
        log "ERROR: run as root"
        exit 2
    fi
}

setup_logging() {
    local log_dir

    log_dir="$(dirname "$LOG_FILE")"
    mkdir -p "$log_dir"
    touch "$LOG_FILE"
    chmod 0644 "$LOG_FILE"
    exec >>"$LOG_FILE" 2>&1
}

check_requirements() {
    if [ ! -x "$XSSSTATE" ]; then
        log "ERROR: xssstate not found at $XSSSTATE"
        log "Install it with: sudo dnf install xssstate"
        exit 2
    fi

    if [ ! -r "$XAUTHORITY_VALUE" ]; then
        log "ERROR: XAUTHORITY is not readable: $XAUTHORITY_VALUE"
        exit 2
    fi
}

discover_socket_displays() {
    local socket display_number

    for socket in /tmp/.X11-unix/X*; do
        [ -S "$socket" ] || continue
        display_number="${socket##*/X}"
        case "$display_number" in
            ''|*[!0-9]*)
                continue
                ;;
        esac
        printf ':%s\n' "$display_number"
    done
}

discover_process_displays() {
    local line token display

    ps -eo args= | while IFS= read -r line; do
        case "$line" in
            *Xorg*|*Xvnc*|*Xvfb*|*Xwayland*|*Xephyr*|*xpra*)
                ;;
            *)
                continue
                ;;
        esac

        for token in $line; do
            case "$token" in
                :[0-9]*)
                    display="${token%%,*}"
                    case "$display" in
                        :*[!0-9.]*|*:|*.*.*)
                            continue
                            ;;
                    esac
                    printf '%s\n' "$display"
                    ;;
            esac
        done
    done
}

discover_displays() {
    if [ -n "${AUTO_STOP_DISPLAYS:-}" ]; then
        printf '%s\n' $AUTO_STOP_DISPLAYS | sort -u
        return
    fi

    {
        discover_socket_displays
        discover_process_displays
    } | sort -u
}

query_idle_ms() {
    local display output status

    display="$1"
    output="$(DISPLAY="$display" XAUTHORITY="$XAUTHORITY_VALUE" "$XSSSTATE" -i 2>&1)"
    status=$?
    if [ "$status" -ne 0 ]; then
        log "display $display: xssstate failed: $output"
        return 1
    fi

    case "$output" in
        ''|*[!0-9]*)
            log "display $display: xssstate returned invalid output: $output"
            return 1
            ;;
    esac

    printf '%s\n' "$output"
}

all_queryable_displays_are_idle() {
    local threshold_ms display idle_ms idle_minutes
    local queryable_count active_count displays

    threshold_ms=$((IDLE_MINUTES * 60 * 1000))
    queryable_count=0
    active_count=0
    displays="$(discover_displays)"

    if [ -z "$displays" ]; then
        log "no X displays discovered; not powering off"
        return 1
    fi

    log "checking X displays: $(printf '%s' "$displays" | tr '\n' ' ')"

    while IFS= read -r display; do
        [ -n "$display" ] || continue

        idle_ms="$(query_idle_ms "$display")" || continue
        idle_minutes=$((idle_ms / 1000 / 60))
        queryable_count=$((queryable_count + 1))

        if [ "$idle_ms" -lt "$threshold_ms" ]; then
            log "display $display is active: idle=${idle_minutes}m"
            active_count=$((active_count + 1))
        else
            log "display $display is idle: idle=${idle_minutes}m"
        fi
    done <<EOF
$displays
EOF

    if [ "$queryable_count" -eq 0 ]; then
        log "no queryable X displays; not powering off"
        return 1
    fi

    if [ "$active_count" -eq 0 ]; then
        log "all queryable X displays are idle"
        return 0
    fi

    log "$active_count of $queryable_count queryable X displays are active"
    return 1
}

take_lock() {
    exec 9>"$LOCK_FILE"
    if ! flock -n 9; then
        log "another auto-stop idle watcher is already running; exiting"
        exit 0
    fi
    printf '%s\n' "$$" 1>&9
}

poweroff_system() {
    log "idle threshold reached on all queryable X displays; powering off"
    exec "$SYSTEMCTL" poweroff
}

start_watcher() {
    require_root
    setup_logging
    check_requirements
    take_lock

    log "starting auto-stop X idle watcher: idle=${IDLE_MINUTES}m poll=${POLL_SECONDS}s xauthority=$XAUTHORITY_VALUE"

    trap 'log "auto-stop X idle watcher exiting"; exit 0' TERM INT

    while true; do
        if all_queryable_displays_are_idle; then
            poweroff_system
        fi

        log "activity is recent or displays are unavailable; sleeping ${POLL_SECONDS} seconds"
        sleep "$POLL_SECONDS"
    done
}

stop_watcher() {
    require_root
    setup_logging

    if [ ! -s "$LOCK_FILE" ]; then
        log "no lock file found at $LOCK_FILE"
        exit 0
    fi

    pid="$(head -n 1 "$LOCK_FILE")"
    case "$pid" in
        ''|*[!0-9]*)
            log "lock file does not contain a pid: $LOCK_FILE"
            exit 0
            ;;
    esac

    if kill -0 "$pid" 2>/dev/null; then
        log "stopping auto-stop X idle watcher pid=$pid"
        kill "$pid"
    else
        log "auto-stop X idle watcher pid is not running: $pid"
    fi
}

check_once() {
    check_requirements
    all_queryable_displays_are_idle
}

case "${1:---start}" in
    --start)
        start_watcher
        ;;
    --stop)
        stop_watcher
        ;;
    --check)
        check_once
        ;;
    -h|--help)
        usage
        ;;
    *)
        usage >&2
        exit 2
        ;;
esac
