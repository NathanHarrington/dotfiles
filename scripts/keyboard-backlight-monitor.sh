#!/usr/bin/env bash
set -euo pipefail

# Monitor X11 for keyboard backlight key presses (Fn+Space on many laptops).
# Usage: scripts/keyboard-backlight-monitor.sh [command...]
# Environment:
#   KEYSYMS="XF86KbdBrightnessToggle XF86KbdBrightnessUp XF86KbdBrightnessDown"
#   KEYCODES="123 124"  # override if keysyms are not mapped
#   ONESHOT=1           # exit after the first match

if ! command -v xinput >/dev/null 2>&1; then
    echo "xinput not found; install it to monitor X11 key events." >&2
    exit 1
fi

if ! command -v xmodmap >/dev/null 2>&1; then
    echo "xmodmap not found; install it to resolve keysyms to keycodes." >&2
    exit 1
fi

keysyms_default="XF86KbdBrightnessToggle XF86KbdBrightnessUp XF86KbdBrightnessDown"
read -r -a keysyms <<< "${KEYSYMS:-$keysyms_default}"

keycodes=()
if [[ -n "${KEYCODES:-}" ]]; then
    read -r -a keycodes <<< "$KEYCODES"
else
    keysym_re=$(printf '%s|' "${keysyms[@]}")
    keysym_re=${keysym_re%|}
    mapfile -t keycodes < <(
        xmodmap -pke | awk -v re="$keysym_re" '$0 ~ re {print $2}' | sort -u
    )
fi

if [[ ${#keycodes[@]} -eq 0 ]]; then
    echo "No keycodes found for keysyms: ${keysyms[*]}" >&2
    echo "Set KEYCODES=\"<code> ...\" to override." >&2
    exit 1
fi

declare -A watch=()
for code in "${keycodes[@]}"; do
    watch["$code"]=1
done

press=0
while IFS= read -r line; do
    if [[ $line == "EVENT type 3"* ]]; then
        press=1
        continue
    fi
    if [[ $press -eq 1 && $line =~ detail:\ ([0-9]+) ]]; then
        code=${BASH_REMATCH[1]}
        press=0
        if [[ -n "${watch[$code]:-}" ]]; then
            ts=$(date '+%Y-%m-%d %H:%M:%S')
            if [[ $# -gt 0 ]]; then
                "$@"
            else
                echo "$ts keyboard backlight key pressed (keycode $code)"
            fi
            if [[ ${ONESHOT:-0} -eq 1 ]]; then
                exit 0
            fi
        fi
    fi
done < <(xinput test-xi2 --root)
