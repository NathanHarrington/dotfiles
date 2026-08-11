#!/usr/bin/env bash

set -euo pipefail

usage() {
    printf 'Usage: %s [--shell]\n' "$0"
    printf '\n'
    printf 'Prints a preview of starship_prompts/kilo_starship.toml with the hostname shown as kilo.\n'
    printf 'Use --shell to launch an interactive bash with this Starship config.\n'
}

toml_escape() {
    local value

    value="${1//\\/\\\\}"
    value="${value//\"/\\\"}"
    printf '%s' "$value"
}

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_DIR="$(cd -- "$SCRIPT_DIR/.." >/dev/null 2>&1 && pwd)"
CONFIG="$REPO_DIR/starship_prompts/kilo_starship.toml"
PREVIEW_HOST="kilo"
MODE="preview"

while [ "$#" -gt 0 ]; do
    case "$1" in
        --shell)
            MODE="shell"
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            printf 'Unknown option: %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
    esac
    shift
done

if ! command -v starship >/dev/null 2>&1; then
    printf 'starship is not installed or not on PATH\n' >&2
    exit 1
fi

if [ ! -f "$CONFIG" ]; then
    printf 'Missing config: %s\n' "$CONFIG" >&2
    exit 1
fi

CURRENT_HOST="$(hostname -s 2>/dev/null || hostname)"
PREVIEW_CONFIG="$(mktemp "${TMPDIR:-/tmp}/kilo-starship.XXXXXX.toml")"
trap 'rm -f "$PREVIEW_CONFIG" "${RCFILE:-}"' EXIT

cp "$CONFIG" "$PREVIEW_CONFIG"
{
    printf '\n[hostname.aliases]\n'
    printf '"%s" = "%s"\n' "$(toml_escape "$CURRENT_HOST")" "$(toml_escape "$PREVIEW_HOST")"
} >>"$PREVIEW_CONFIG"

export STARSHIP_CONFIG="$PREVIEW_CONFIG"

if [ "$MODE" = "shell" ]; then
    RCFILE="$(mktemp "${TMPDIR:-/tmp}/kilo-starship-bashrc.XXXXXX")"
    {
        printf 'export STARSHIP_CONFIG=%q\n' "$STARSHIP_CONFIG"
        printf 'eval "$(starship init bash)"\n'
        printf 'printf "\\nUsing Starship config: %s\\n"\n' "$CONFIG"
        printf 'printf "Preview hostname: %s\\n"\n' "$PREVIEW_HOST"
        printf 'printf "Exit this preview shell with: exit\\n\\n"\n'
    } >"$RCFILE"
    bash --rcfile "$RCFILE" -i
    exit
fi

print_prompt() {
    local status prompt

    status="$1"
    prompt="$(starship prompt --path "$PWD" --status "$status")"
    prompt="${prompt//\\[/}"
    prompt="${prompt//\\]/}"
    printf '%s\n' "$prompt"
}

printf 'Config: %s\n' "$CONFIG"
printf 'Preview hostname: %s\n\n' "$PREVIEW_HOST"
printf 'Success prompt:\n'
print_prompt 0
printf '\n'
printf 'Error prompt:\n'
print_prompt 1
printf '\n'
printf 'Interactive preview:\n'
printf '  %s --shell\n' "$0"
