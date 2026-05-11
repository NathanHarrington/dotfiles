#!/usr/bin/env bash

LOW_BATTERY_THRESHOLD="${LOW_BATTERY_THRESHOLD:-25}"
CHECK_INTERVAL_SECONDS="${CHECK_INTERVAL_SECONDS:-60}"
OSD_DELAY_SECONDS="${OSD_DELAY_SECONDS:-5}"
OSD_FONT="${OSD_FONT:--*-*-bold-*-*-*-36-*-*-*-*-*-*-*}"

if [[ ! "$LOW_BATTERY_THRESHOLD" =~ ^[0-9]+$ ]]; then
    LOW_BATTERY_THRESHOLD=25
elif (( LOW_BATTERY_THRESHOLD > 100 )); then
    LOW_BATTERY_THRESHOLD=100
fi

if [[ ! "$CHECK_INTERVAL_SECONDS" =~ ^[1-9][0-9]*$ ]]; then
    CHECK_INTERVAL_SECONDS=60
fi

if [[ ! "$OSD_DELAY_SECONDS" =~ ^[1-9][0-9]*$ ]]; then
    OSD_DELAY_SECONDS=5
fi

if [[ -z "${DISPLAY:-}" && -S /tmp/.X11-unix/X0 ]]; then
    export DISPLAY=:0
fi

if command -v flock >/dev/null 2>&1; then
    LOCK_DISPLAY="${DISPLAY:-no-display}"
    LOCK_DISPLAY="${LOCK_DISPLAY//[^[:alnum:]_.-]/_}"
    LOCK_FILE="/tmp/battery_monitor-${UID}-${LOCK_DISPLAY}.lock"
    exec 9>"$LOCK_FILE"
    if ! flock -n 9; then
        exit 0
    fi
fi

read_sysfs_battery() {
    local supply=""
    local supply_type=""
    local present=""
    local capacity=""
    local status=""
    local lowest=101
    local lowest_name=""
    local lowest_status="Unknown"
    local found=0

    for supply in /sys/class/power_supply/*; do
        [[ -e "$supply" ]] || continue
        [[ -r "$supply/type" && -r "$supply/capacity" ]] || continue

        supply_type="$(<"$supply/type")"
        [[ "$supply_type" == "Battery" ]] || continue

        if [[ -r "$supply/present" ]]; then
            present="$(<"$supply/present")"
            [[ "$present" == "1" ]] || continue
        fi

        capacity="$(<"$supply/capacity")"
        [[ "$capacity" =~ ^[0-9]+$ ]] || continue

        status="Unknown"
        if [[ -r "$supply/status" ]]; then
            status="$(<"$supply/status")"
        fi

        found=1
        if (( capacity < lowest )); then
            lowest="$capacity"
            lowest_name="${supply##*/}"
            lowest_status="$status"
        fi
    done

    (( found )) || return 1
    printf '%s\t%s\t%s\n' "$lowest" "$lowest_status" "$lowest_name"
}

read_acpi_battery() {
    local line=""
    local name=""
    local status=""
    local capacity=""
    local lowest=101
    local lowest_name=""
    local lowest_status="Unknown"
    local found=0

    command -v acpi >/dev/null 2>&1 || return 1

    while IFS= read -r line; do
        if [[ "$line" =~ ^Battery[[:space:]]+([^:]+):[[:space:]]+([^,]+),[[:space:]]+([0-9]+)% ]]; then
            name="Battery ${BASH_REMATCH[1]}"
            status="${BASH_REMATCH[2]}"
            capacity="${BASH_REMATCH[3]}"
            found=1

            if (( capacity < lowest )); then
                lowest="$capacity"
                lowest_name="$name"
                lowest_status="$status"
            fi
        fi
    done < <(acpi -b 2>/dev/null)

    (( found )) || return 1
    printf '%s\t%s\t%s\n' "$lowest" "$lowest_status" "$lowest_name"
}

read_battery() {
    read_sysfs_battery || read_acpi_battery
}

show_low_battery_warning() {
    local level="$1"
    local status="$2"
    local name="$3"
    local message="Battery low: ${level}%"

    if [[ -n "$status" && "$status" != "Unknown" ]]; then
        message+=" (${status})"
    fi
    if [[ -n "$name" ]]; then
        message+=" [$name]"
    fi

    if ! command -v osd_cat >/dev/null 2>&1; then
        printf '%s\n' "$message" >&2
        return 1
    fi

    printf '%s\n' "$message" | osd_cat \
        --align=center \
        --pos=bottom \
        --color=red \
        --delay="$OSD_DELAY_SECONDS" \
        --outline=2 \
        --font="$OSD_FONT"
}

while true; do
    battery_info=""
    if battery_info="$(read_battery)"; then
        IFS=$'\t' read -r battery_level battery_status battery_name <<<"$battery_info"
        if (( battery_level <= LOW_BATTERY_THRESHOLD )); then
            show_low_battery_warning "$battery_level" "$battery_status" "$battery_name"
        fi
    else
        printf 'battery_monitor: no battery data found\n' >&2
    fi

    sleep "$CHECK_INTERVAL_SECONDS"
done
