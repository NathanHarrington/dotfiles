#!/usr/bin/env bash
set -u

LOGIND_CONFIG=

section() {
    printf '\n== %s ==\n' "$1"
}

kv() {
    printf '  %-34s %s\n' "$1:" "$2"
}

have() {
    command -v "$1" >/dev/null 2>&1
}

format_seconds() {
    local seconds=$1

    case "$seconds" in
        ''|*[!0-9]*)
            printf '%s\n' "$seconds"
            return
            ;;
    esac

    if [ "$seconds" -eq 0 ]; then
        printf '0s'
    elif [ "$seconds" -lt 60 ]; then
        printf '%ss' "$seconds"
    elif [ $((seconds % 3600)) -eq 0 ]; then
        printf '%sh' $((seconds / 3600))
    elif [ $((seconds % 60)) -eq 0 ]; then
        printf '%sm' $((seconds / 60))
    else
        printf '%sm %ss' $((seconds / 60)) $((seconds % 60))
    fi
}

clean_gvariant() {
    local value=$1

    value=${value#uint32 }
    value=${value#uint64 }
    value=${value#int32 }
    value=${value#int64 }
    value=${value#\'}
    value=${value%\'}

    printf '%s\n' "$value"
}

print_time_value() {
    local value=$1

    case "$value" in
        ''|*[!0-9]*)
            printf '%s\n' "$value"
            ;;
        *)
            printf '%s (%s)\n' "$value" "$(format_seconds "$value")"
            ;;
    esac
}

format_duration() {
    local value=$1

    case "$value" in
        ''|*[!0-9]*)
            printf '%s\n' "$value"
            ;;
        *)
            format_seconds "$value"
            ;;
    esac
}

print_kernel_sleep() {
    section "Kernel Sleep"

    if [ -r /sys/power/state ]; then
        kv "Supported sleep states" "$(tr '\n' ' ' </sys/power/state)"
    else
        kv "Supported sleep states" "unavailable"
    fi

    if [ -r /sys/power/mem_sleep ]; then
        kv "Suspend mode choices" "$(tr '\n' ' ' </sys/power/mem_sleep)"
    else
        kv "Suspend mode choices" "unavailable"
    fi
}

logind_setting() {
    local key=$1

    printf '%s\n' "$LOGIND_CONFIG" | awk -v key="$key" '
        {
            line = $0
            sub(/^[[:space:]]*/, "", line)
            state = "configured"

            if (line ~ /^#/) {
                state = "default"
                sub(/^#[[:space:]]*/, "", line)
            }

            if (line ~ ("^" key "=")) {
                sub("^[^=]*=", "", line)
                value = line
                value_state = state
                found = 1
            }
        }
        END {
            if (found) {
                printf "%s (%s)\n", value, value_state
            } else {
                print "not found"
            }
        }
    '
}

ensure_logind_config() {
    if [ -n "$LOGIND_CONFIG" ]; then
        return 0
    fi

    have systemd-analyze || return 1
    LOGIND_CONFIG="$(systemd-analyze cat-config systemd/logind.conf 2>/dev/null)" || {
        LOGIND_CONFIG=
        return 1
    }
}

plain_logind_setting() {
    local value

    if ! ensure_logind_config; then
        printf 'unknown\n'
        return
    fi

    value=$(logind_setting "$1")
    value=${value% (default)}
    value=${value% (configured)}
    printf '%s\n' "$value"
}

print_logind() {
    section "systemd-logind"

    if ! ensure_logind_config; then
        kv "logind config" "unavailable"
        return
    fi

    kv "Lid close" "$(logind_setting HandleLidSwitch)"
    kv "Lid close on AC" "$(logind_setting HandleLidSwitchExternalPower)"
    kv "Lid close while docked" "$(logind_setting HandleLidSwitchDocked)"
    kv "Power button" "$(logind_setting HandlePowerKey)"
    kv "Power button long press" "$(logind_setting HandlePowerKeyLongPress)"
    kv "Suspend key" "$(logind_setting HandleSuspendKey)"
    kv "Hibernate key" "$(logind_setting HandleHibernateKey)"
    kv "Allowed sleep operation" "$(logind_setting SleepOperation)"
    kv "Idle action" "$(logind_setting IdleAction)"
    kv "Idle action delay" "$(logind_setting IdleActionSec)"
    kv "Stop idle sessions after" "$(logind_setting StopIdleSessionSec)"
    kv "Lid switch holdoff" "$(logind_setting HoldoffTimeoutSec)"
}

gsettings_schema_exists() {
    local schema=$1

    gsettings list-schemas 2>/dev/null | grep -Fxq "$schema"
}

gsettings_key_exists() {
    local schema=$1
    local key=$2

    gsettings list-keys "$schema" 2>/dev/null | grep -Fxq "$key"
}

gsettings_value() {
    local schema=$1
    local key=$2

    clean_gvariant "$(gsettings get "$schema" "$key" 2>/dev/null)"
}

print_gsetting() {
    local label=$1
    local schema=$2
    local key=$3
    local value

    if ! gsettings_key_exists "$schema" "$key"; then
        return
    fi

    value=$(gsettings_value "$schema" "$key")

    case "$key" in
        *timeout|*delay)
            kv "$label" "$(print_time_value "$value")"
            ;;
        *)
            kv "$label" "$value"
            ;;
    esac
}

print_desktop_power() {
    section "Desktop Idle and Suspend"

    if ! have gsettings; then
        kv "Desktop settings" "gsettings not found"
        return
    fi

    if gsettings_schema_exists org.gnome.desktop.session; then
        print_gsetting "Screen idle delay" org.gnome.desktop.session idle-delay
    else
        kv "GNOME session settings" "schema not found"
    fi

    if gsettings_schema_exists org.gnome.desktop.screensaver; then
        print_gsetting "Lock enabled" org.gnome.desktop.screensaver lock-enabled
        print_gsetting "Lock after blank" org.gnome.desktop.screensaver lock-delay
    fi

    if gsettings_schema_exists org.gnome.settings-daemon.plugins.power; then
        print_gsetting "AC idle action" org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type
        print_gsetting "AC idle delay" org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout
        print_gsetting "Battery idle action" org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type
        print_gsetting "Battery idle delay" org.gnome.settings-daemon.plugins.power sleep-inactive-battery-timeout
        print_gsetting "Power button action" org.gnome.settings-daemon.plugins.power power-button-action
        print_gsetting "Dim screen when idle" org.gnome.settings-daemon.plugins.power idle-dim
    else
        kv "GNOME power settings" "schema not found"
    fi
}

print_x_power() {
    local xset_output

    section "X Screen Saver and DPMS"

    if ! have xset; then
        kv "X settings" "xset not found"
        return
    fi

    if [ -z "${DISPLAY:-}" ]; then
        kv "X settings" "DISPLAY is not set"
        return
    fi

    if ! xset_output="$(xset q 2>/dev/null)"; then
        kv "X settings" "unavailable for DISPLAY=${DISPLAY}"
        return
    fi

    printf '%s\n' "$xset_output" | awk '
        /timeout:/ {
            printf "  %-34s %ss\n", "Screen saver timeout:", $2
            printf "  %-34s %ss\n", "Screen saver cycle:", $4
        }
        /Standby:/ {
            printf "  %-34s %ss\n", "DPMS standby:", $2
            printf "  %-34s %ss\n", "DPMS suspend:", $4
            printf "  %-34s %ss\n", "DPMS off:", $6
        }
        /DPMS is/ {
            printf "  %-34s %s\n", "DPMS:", $3
        }
    '
}

read_first_line() {
    local file=$1
    local value=

    if [ -r "$file" ]; then
        IFS= read -r value <"$file" || true
    fi

    printf '%s\n' "$value"
}

script_dir() {
    local source_dir

    source_dir=${BASH_SOURCE[0]%/*}
    if [ "$source_dir" = "${BASH_SOURCE[0]}" ]; then
        source_dir=.
    fi

    (cd "$source_dir" >/dev/null 2>&1 && pwd)
}

i3_idle_helper_path() {
    local helper_dir

    if [ -n "${SUSPEND_ON_BATTERY_HELPER:-}" ]; then
        printf '%s\n' "$SUSPEND_ON_BATTERY_HELPER"
        return
    fi

    helper_dir=$(script_dir)
    if [ -x "$helper_dir/suspend-on-battery-idle.sh" ]; then
        printf '%s\n' "$helper_dir/suspend-on-battery-idle.sh"
        return
    fi

    if [ -n "${HOME:-}" ] && [ -x "$HOME/projects/dotfiles/scripts/suspend-on-battery-idle.sh" ]; then
        printf '%s\n' "$HOME/projects/dotfiles/scripts/suspend-on-battery-idle.sh"
        return
    fi

    printf '%s\n' "not found"
}

i3_idle_helper_settings() {
    local helper

    helper=$(i3_idle_helper_path)
    [ -x "$helper" ] || return 1
    "$helper" --settings 2>/dev/null
}

i3_idle_setting() {
    local key=$1

    i3_idle_helper_settings | awk -F= -v key="$key" '$1 == key { print $2; found = 1 } END { exit found ? 0 : 1 }'
}

i3_idle_helper_configured() {
    local config

    for config in "${I3_CONFIG:-}" "$HOME/.config/i3/config" "$HOME/projects/dotfiles/i3/config"; do
        [ -n "$config" ] || continue
        [ -r "$config" ] || continue
        grep -q 'suspend-on-battery-idle.sh' "$config" && return 0
    done

    return 1
}

running_idle_watcher() {
    have pgrep || return 1
    pgrep -af 'xautolock|xidlehook|suspend-on-battery-idle.sh' 2>/dev/null |
        grep -v 'pgrep -af' >/dev/null
}

idle_watcher_name() {
    local xidlehook xautolock

    xidlehook=$(i3_idle_setting xidlehook 2>/dev/null || printf 'xidlehook')
    xautolock=$(i3_idle_setting xautolock 2>/dev/null || printf 'xautolock')

    if command -v "$xidlehook" >/dev/null 2>&1; then
        printf '%s\n' "$xidlehook"
    elif command -v "$xautolock" >/dev/null 2>&1; then
        printf '%s\n' "$xautolock"
    else
        printf 'not found (install xautolock)\n'
    fi
}

i3_battery_idle_policy() {
    local screen_off_seconds suspend_seconds sleep_action

    screen_off_seconds=$(i3_idle_setting screen_off_seconds 2>/dev/null || true)
    suspend_seconds=$(i3_idle_setting suspend_seconds 2>/dev/null || true)
    sleep_action=$(i3_idle_setting sleep_action 2>/dev/null || printf 'suspend')

    if [ -z "$screen_off_seconds" ] && [ -z "$suspend_seconds" ]; then
        return 1
    fi

    if [ -n "$screen_off_seconds" ] && [ -n "$suspend_seconds" ]; then
        printf 'screen off/lock after %s, %s after %s' \
            "$(format_duration "$screen_off_seconds")" \
            "$sleep_action" \
            "$(format_duration "$suspend_seconds")"
    elif [ -n "$screen_off_seconds" ]; then
        printf 'screen off/lock after %s' "$(format_duration "$screen_off_seconds")"
    else
        printf '%s after %s' "$sleep_action" "$(format_duration "$suspend_seconds")"
    fi
}

print_i3_idle_power() {
    local helper screen_off_seconds suspend_seconds sleep_action watcher status configured

    section "i3 Battery Idle Helper"

    helper=$(i3_idle_helper_path)
    if [ ! -x "$helper" ]; then
        kv "Helper" "not found"
        return
    fi

    screen_off_seconds=$(i3_idle_setting screen_off_seconds 2>/dev/null || true)
    suspend_seconds=$(i3_idle_setting suspend_seconds 2>/dev/null || true)
    sleep_action=$(i3_idle_setting sleep_action 2>/dev/null || printf 'suspend')
    watcher=$(idle_watcher_name)

    if i3_idle_helper_configured; then
        configured="yes"
    else
        configured="not found in i3 config"
    fi

    if running_idle_watcher; then
        status="running"
    else
        status="not running"
    fi

    kv "Helper" "$helper"
    kv "Started from i3" "$configured"
    kv "Idle watcher" "$watcher"
    kv "Watcher process" "$status"
    kv "Plugged in idle action" "no action from this helper"
    [ -n "$screen_off_seconds" ] && kv "Battery screen off/lock" "after $(format_duration "$screen_off_seconds")"
    [ -n "$suspend_seconds" ] && kv "Battery sleep action" "$sleep_action after $(format_duration "$suspend_seconds")"
    kv "Sleep action guards" "battery only; skips fullscreen and audio"
    kv "Screen-off/lock guards" "battery only; skips fullscreen; locks via xss-lock/X screensaver"
}

summary_action() {
    case "$1" in
        hibernate)
            printf 'hibernate'
            ;;
        hybrid-sleep)
            printf 'hybrid sleep'
            ;;
        ignore|nothing)
            printf 'ignore'
            ;;
        lock)
            printf 'lock'
            ;;
        logout)
            printf 'log out'
            ;;
        poweroff)
            printf 'power off'
            ;;
        suspend)
            printf 'suspend'
            ;;
        suspend-then-hibernate)
            printf 'suspend, then hibernate'
            ;;
        *)
            printf '%s' "$1"
            ;;
    esac
}

idle_policy_summary() {
    local action=$1
    local delay=$2

    case "$action" in
        ignore|nothing)
            printf 'never suspend'
            ;;
        unknown|not\ found|'')
            printf 'automatic suspend unknown'
            ;;
        *)
            printf '%s after %s' "$(summary_action "$action")" "$(format_duration "$delay")"
            ;;
    esac
}

idle_policy_for_power_source() {
    local source=$1
    local action delay

    case "$source" in
        ac)
            if i3_idle_helper_settings >/dev/null 2>&1; then
                printf 'never suspend'
                return
            fi
            ;;
        battery)
            if i3_battery_idle_policy; then
                return
            fi
            ;;
    esac

    if have gsettings && gsettings_schema_exists org.gnome.settings-daemon.plugins.power; then
        case "$source" in
            ac)
                if gsettings_key_exists org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type; then
                    action=$(gsettings_value org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type)
                    delay=$(gsettings_value org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout)
                    idle_policy_summary "$action" "$delay"
                    return
                fi
                ;;
            battery)
                if gsettings_key_exists org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type; then
                    action=$(gsettings_value org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type)
                    delay=$(gsettings_value org.gnome.settings-daemon.plugins.power sleep-inactive-battery-timeout)
                    idle_policy_summary "$action" "$delay"
                    return
                fi
                ;;
        esac
    fi

    action=$(plain_logind_setting IdleAction)
    delay=$(plain_logind_setting IdleActionSec)
    idle_policy_summary "$action" "$delay"
}

print_summary() {
    local lid lid_ac

    lid=$(plain_logind_setting HandleLidSwitch)
    lid_ac=$(plain_logind_setting HandleLidSwitchExternalPower)

    section "Summary"
    kv "Plugged in" "$(idle_policy_for_power_source ac)"
    kv "Plugged in, lid closed" "$(summary_action "$lid_ac")"
    kv "Battery" "$(idle_policy_for_power_source battery)"
    kv "Battery, lid closed" "$(summary_action "$lid")"
}

print_sysfs_power_supply() {
    local supply name type status capacity online start_threshold end_threshold
    local lid_state
    local found=0

    for supply in /sys/class/power_supply/*; do
        [ -e "$supply" ] || continue

        name=${supply##*/}
        type=$(read_first_line "$supply/type")
        found=1

        case "$type" in
            Battery)
                status=$(read_first_line "$supply/status")
                capacity=$(read_first_line "$supply/capacity")
                start_threshold=$(read_first_line "$supply/charge_control_start_threshold")
                end_threshold=$(read_first_line "$supply/charge_control_end_threshold")

                if [ -n "$capacity" ]; then
                    kv "$name battery" "${status:-unknown}, ${capacity}%"
                else
                    kv "$name battery" "${status:-unknown}"
                fi

                [ -n "$start_threshold" ] && kv "$name charge start" "${start_threshold}%"
                [ -n "$end_threshold" ] && kv "$name charge stop" "${end_threshold}%"
                ;;
            Mains|USB|USB_C|USB_PD)
                online=$(read_first_line "$supply/online")
                kv "$name $type" "online=${online:-unknown}"
                ;;
            *)
                kv "$name" "${type:-unknown}"
                ;;
        esac
    done

    if [ "$found" -eq 0 ]; then
        kv "Power supplies" "none found in /sys/class/power_supply"
    fi

    for supply in /proc/acpi/button/lid/*/state; do
        [ -r "$supply" ] || continue
        lid_state=$(read_first_line "$supply")
        lid_state=${lid_state#state:}
        lid_state=${lid_state#"${lid_state%%[![:space:]]*}"}
        kv "Lid state" "$lid_state"
        return
    done
}

print_upower() {
    local upower_output

    section "UPower Hardware State"

    if ! have upower; then
        kv "UPower" "not found; using /sys fallback"
        print_sysfs_power_supply
        return
    fi

    if ! upower_output="$(upower -d 2>/dev/null)"; then
        kv "UPower" "unavailable; using /sys fallback"
        print_sysfs_power_supply
        return
    fi

    printf '%s\n' "$upower_output" | awk '
        /^Device:/ {
            device = $2
            daemon = 0
            shown = 0
            next
        }
        /^Daemon:/ {
            print "  Daemon:"
            daemon = 1
            next
        }
        daemon && /^[[:space:]]+(on-battery|lid-is-closed|lid-is-present|critical-action):/ {
            line = $0
            sub(/^[[:space:]]+/, "", line)
            print "    " line
            next
        }
        !daemon && /^[[:space:]]+(native-path|model|state|percentage|time to empty|time to full|online|charge-start-threshold|charge-end-threshold):/ {
            if (!shown) {
                print "  " device ":"
                shown = 1
            }
            line = $0
            sub(/^[[:space:]]+/, "", line)
            print "    " line
        }
    '
}

print_inhibitors() {
    local inhibitors

    section "Suspend Inhibitors"

    if ! have systemd-inhibit; then
        kv "Suspend inhibitors" "systemd-inhibit not found"
        return
    fi

    if ! inhibitors="$(systemd-inhibit --list --no-pager 2>/dev/null)"; then
        kv "Suspend inhibitors" "unavailable"
        return
    fi

    if [ -z "$inhibitors" ]; then
        kv "Suspend inhibitors" "none reported"
        return
    fi

    printf '%s\n' "$inhibitors" | sed 's/^/  /'
}

main() {
    printf 'Power settings for %s at %s\n' "$(hostname)" "$(date '+%Y-%m-%d %H:%M:%S %Z')"

    print_kernel_sleep
    print_logind
    print_desktop_power
    print_i3_idle_power
    print_x_power
    print_upower
    print_inhibitors
    print_summary
}

main "$@"
