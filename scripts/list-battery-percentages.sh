#!/usr/bin/env bash
set -u

found=0

for battery in /sys/class/power_supply/*; do
    [ -e "$battery" ] || continue
    [ -r "$battery/type" ] || continue
    [ "$(cat "$battery/type")" = "Battery" ] || continue
    [ -r "$battery/capacity" ] || continue

    name=${battery##*/}
    percent=$(cat "$battery/capacity")

    printf '%s: %s%%\n' "$name" "$percent"
    found=1
done

if [ "$found" -eq 0 ]; then
    echo "No batteries found" >&2
    exit 1
fi
