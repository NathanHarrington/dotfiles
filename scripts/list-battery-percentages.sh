#!/usr/bin/env bash
set -u

get_upower_field() {
    local field=$1
    local line
    local value

    while IFS= read -r line; do
        line=${line#"${line%%[![:space:]]*}"}
        case "$line" in
            "${field}:"*)
                value=${line#"${field}:"}
                value=${value#"${value%%[![:space:]]*}"}
                printf '%s\n' "$value"
                return 0
                ;;
        esac
    done

    return 1
}

list_upower_batteries() {
    local devices
    local device
    local info
    local name
    local native_path
    local percent
    local found=0

    devices=$(upower -e 2>/dev/null) || return 1

    while IFS= read -r device; do
        [ -n "$device" ] || continue
        case "$device" in
            */DisplayDevice) continue ;;
        esac

        info=$(upower -i "$device" 2>/dev/null) || continue
        percent=$(get_upower_field percentage <<< "$info") || continue
        name=$(get_upower_field model <<< "$info") || name=

        if [ -z "$name" ]; then
            native_path=$(get_upower_field native-path <<< "$info") || native_path=
            name=${native_path:-${device##*/}}
        fi

        printf '%s: %s\n' "$name" "$percent"
        found=1
    done <<< "$devices"

    [ "$found" -eq 1 ]
}

if command -v upower >/dev/null 2>&1 && list_upower_batteries; then
    exit 0
fi

found=0

for battery in /sys/class/power_supply/*; do
    [ -e "$battery" ] || continue
    [ -r "$battery/type" ] || continue
    [ "$(cat "$battery/type")" = "Battery" ] || continue
    [ -r "$battery/capacity" ] || continue

    name=${battery##*/}
    if [ -r "$battery/model_name" ]; then
        model_name=$(cat "$battery/model_name")
        if [ -n "$model_name" ]; then
            name=$model_name
        fi
    fi
    percent=$(cat "$battery/capacity")

    printf '%s: %s%%\n' "$name" "$percent"
    found=1
done

if [ "$found" -eq 0 ]; then
    echo "No batteries found" >&2
    exit 1
fi
