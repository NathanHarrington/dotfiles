#!/usr/bin/env bash

set -u

MODE="all"
HOSTNAME_PREVIEW=""
COLOR_PREVIEW_GLYPH="󰻀"

usage() {
    printf 'Usage: %s [--all|--icons|--colors] [hostname]\n' "$0"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --all)
            MODE="all"
            ;;
        --icons)
            MODE="icons"
            ;;
        --colors)
            MODE="colors"
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            printf 'Unknown option: %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
        *)
            if [ -n "$HOSTNAME_PREVIEW" ]; then
                printf 'Unexpected extra hostname: %s\n' "$1" >&2
                usage >&2
                exit 2
            fi
            HOSTNAME_PREVIEW="$1"
            ;;
    esac
    shift
done

if [ -z "$HOSTNAME_PREVIEW" ]; then
    HOSTNAME_PREVIEW="$(hostname -s 2>/dev/null || hostname)"
fi

if [ -t 1 ]; then
    USE_COLOR=1
    GREEN=$'\033[1;32m'
    HOSTNAME_COLOR=$'\033[31m'
    RESET=$'\033[0m'
else
    USE_COLOR=0
    GREEN=""
    HOSTNAME_COLOR=""
    RESET=""
fi

print_header() {
    printf 'Starship prompt chooser for host: %s\n\n' "$HOSTNAME_PREVIEW"
}

print_icon_header() {
    printf 'Each preview uses the prompt shape: icon  hostname #\n'
    printf 'This list favors Nerd Font private glyphs because standard emoji animals\n'
    printf 'do not render reliably in this alacritty/font fallback path.\n'
    printf 'Copy the chosen glyph into hotel-compute_starship.toml:\n'
    printf '  format = "$directory$git_branch$git_status\\n[GLYPH](bold green)  $hostname$character$python$custom"\n\n'
}

print_row() {
    local label glyph

    label="$1"
    glyph="$2"

    printf '%-22s %s%s%s  %s%s%s %s#%s\n' \
        "$label" \
        "$GREEN" "$glyph" "$RESET" \
        "$HOSTNAME_COLOR" "$HOSTNAME_PREVIEW" "$RESET" \
        "$GREEN" "$RESET"
}

glyph_from_codepoint() {
    local codepoint padded

    codepoint="$1"
    printf -v padded '%08X' "$((16#$codepoint))"
    printf '%b' "\\U$padded"
}

print_nf_row() {
    local label codepoint glyph

    label="$1"
    codepoint="$2"
    glyph="$(glyph_from_codepoint "$codepoint")"

    printf '%-28s U+%-6s %s%s%s  %s%s%s %s#%s\n' \
        "$label" \
        "$codepoint" \
        "$GREEN" "$glyph" "$RESET" \
        "$HOSTNAME_COLOR" "$HOSTNAME_PREVIEW" "$RESET" \
        "$GREEN" "$RESET"
}

print_group() {
    printf '\n%s\n' "$1"
}

ansi_for_starship_style() {
    local style hex red green blue

    style="$1"

    if [ "$USE_COLOR" -eq 0 ]; then
        return
    fi

    case "$style" in
        red)
            printf '\033[31m'
            ;;
        bright-red)
            printf '\033[91m'
            ;;
        "bold red")
            printf '\033[1;31m'
            ;;
        fg:#??????)
            hex="${style#fg:#}"
            red=$((16#${hex:0:2}))
            green=$((16#${hex:2:2}))
            blue=$((16#${hex:4:2}))
            printf '\033[38;2;%d;%d;%dm' "$red" "$green" "$blue"
            ;;
        *)
            printf '\033[31m'
            ;;
    esac
}

print_color_header() {
    printf 'Hostname color candidates use the same prompt shape: icon  hostname #\n'
    printf 'Copy the chosen style value into hotel-compute_starship.toml:\n'
    printf '  [hostname]\n'
    printf '  style = "STYLE_VALUE"\n\n'
    printf 'If red and bright-red look identical, prefer one of the fg:# truecolor rows.\n\n'
}

print_color_row() {
    local label style color

    label="$1"
    style="$2"
    color="$(ansi_for_starship_style "$style")"

    printf '%-18s %-14s %s%s%s  %s%s%s %s#%s\n' \
        "$label" \
        "$style" \
        "$GREEN" "$COLOR_PREVIEW_GLYPH" "$RESET" \
        "$color" "$HOSTNAME_PREVIEW" "$RESET" \
        "$GREEN" "$RESET"
}

print_colors() {
    print_color_header

    print_group "ANSI Reds"
    print_color_row "normal red" "red"
    print_color_row "bright red" "bright-red"
    print_color_row "bold red" "bold red"

    print_group "Truecolor Reds"
    print_color_row "pure red" "fg:#ff0000"
    print_color_row "signal red" "fg:#ff3030"
    print_color_row "clear red" "fg:#ff4040"
    print_color_row "soft bright" "fg:#ff5555"
    print_color_row "coral red" "fg:#ff6b6b"
    print_color_row "light red" "fg:#ff8080"
    print_color_row "rose red" "fg:#ff3366"
    print_color_row "orange red" "fg:#ff3b1f"
    print_color_row "tomato" "fg:#ff6347"
}

print_icons() {
    print_icon_header

    print_group "Star Fox-ish / Good Candidates"
    print_nf_row "slippy / frog" "EDF8"
    print_nf_row "rabbit" "F0907"
    print_nf_row "rabbit variant" "F1A61"
    print_nf_row "rabbit outline" "F1A62"
    print_nf_row "wolf pack" "EDDE"
    print_nf_row "bird" "F15C6"
    print_nf_row "crow" "EDEA"
    print_nf_row "dove" "ED99"
    print_nf_row "kiwi bird" "EDFF"
    print_nf_row "dog" "EEF7"
    print_nf_row "dog side" "F0A44"
    print_nf_row "cat" "EEED"
    print_nf_row "cat md" "F011B"

    print_group "Mammals"
    print_nf_row "cow" "EEF1"
    print_nf_row "cow md" "F019A"
    print_nf_row "cow off" "F18FC"
    print_nf_row "dog md" "F0A43"
    print_nf_row "dog service" "F0AAD"
    print_nf_row "dog side off" "F16EE"
    print_nf_row "horse" "EF04"
    print_nf_row "horse head" "EF51"
    print_nf_row "horse md" "F15BF"
    print_nf_row "horse human" "F15C0"
    print_nf_row "horse variant" "F15C1"
    print_nf_row "horse fast" "F186E"
    print_nf_row "chess horse" "E25F"
    print_nf_row "hippo" "EF03"
    print_nf_row "otter" "EF0A"
    print_nf_row "elephant" "F07C6"
    print_nf_row "kangaroo" "F1558"
    print_nf_row "koala" "F173F"
    print_nf_row "panda" "F03DA"
    print_nf_row "pandas dev" "E85D"
    print_nf_row "pig" "F0401"
    print_nf_row "pig variant" "F1006"
    print_nf_row "pig variant outline" "F1678"
    print_nf_row "piggy bank" "EDA3"
    print_nf_row "piggy bank md" "F1007"
    print_nf_row "piggy bank outline" "F1679"
    print_nf_row "seal" "F047A"
    print_nf_row "seal variant" "F0FD9"
    print_nf_row "sheep" "F0CC6"
    print_nf_row "teddy bear" "F18FB"

    print_group "Birds"
    print_nf_row "duck" "F01E5"
    print_nf_row "owl" "F03D2"
    print_nf_row "parrot linux" "F329"
    print_nf_row "penguin" "F0EC0"
    print_nf_row "turkey" "F171B"
    print_nf_row "food turkey" "F171C"

    print_group "Reptiles / Fantasy"
    print_nf_row "dragon" "EEF8"
    print_nf_row "snake" "F150E"
    print_nf_row "turtle" "F0CD7"
    print_nf_row "unicorn" "F15C2"
    print_nf_row "unicorn variant" "F15C3"

    print_group "Aquatic"
    print_nf_row "fish" "EE41"
    print_nf_row "fish md" "F023A"
    print_nf_row "fish off" "F13F3"
    print_nf_row "fishbowl" "F0EF3"
    print_nf_row "fishbowl outline" "F0EF4"
    print_nf_row "cuttlefish" "F1AF"
    print_nf_row "dolphin" "F18B4"
    print_nf_row "jellyfish" "F0F01"
    print_nf_row "jellyfish outline" "F0F02"
    print_nf_row "shark" "F18BA"
    print_nf_row "shark off" "F18BB"
    print_nf_row "shark fin" "F1673"
    print_nf_row "shark fin outline" "F1674"

    print_group "Bugs / Small Things"
    print_nf_row "bug" "F188"
    print_nf_row "bug cod" "EAAF"
    print_nf_row "bug oct" "F46F"
    print_nf_row "bug md" "F00E4"
    print_nf_row "bug check" "F0A2E"
    print_nf_row "bug check outline" "F0A2F"
    print_nf_row "bug outline" "F0A30"
    print_nf_row "butterfly" "F1589"
    print_nf_row "butterfly outline" "F158A"
    print_nf_row "butterfly fae" "E28E"
    print_nf_row "bee" "F0FA1"
    print_nf_row "bee flower" "F0FA2"
    print_nf_row "beehive outline" "F10CE"
    print_nf_row "beehive off outline" "F13ED"
    print_nf_row "beekeeper" "F14E2"
    print_nf_row "forumbee" "F211"
    print_nf_row "ladybug" "F082D"
    print_nf_row "snail" "F1677"
    print_nf_row "spider" "EF10"
    print_nf_row "spider md" "F11EA"
    print_nf_row "spider thread" "F11EB"
    print_nf_row "spider web" "F0BCA"

    print_group "Paws / Mascot-ish / Animal-adjacent"
    print_nf_row "paw" "F1B0"
    print_nf_row "paw md" "F03E9"
    print_nf_row "paw outline" "F1675"
    print_nf_row "paw off" "F0657"
    print_nf_row "paw off outline" "F1676"
    print_nf_row "deploydog" "F1CF"
    print_nf_row "rabbitmq dev" "E882"
    print_nf_row "tomcat dev" "E8C3"
    print_nf_row "hotdog" "EF87"
    print_nf_row "hotdog fae" "E251"
    print_nf_row "food hot dog" "F184B"
    print_nf_row "chicken thigh" "E29F"
    print_nf_row "baseball bat ball" "ED5B"
    print_nf_row "bat" "F0B5F"
    print_nf_row "mouse" "F037D"
    print_nf_row "mouse bluetooth" "F098B"
    print_nf_row "mouse pointer" "F245"

    print_group "Symbols / Nerd Font Fallbacks"
    print_row "star" "★"
    print_row "sparkle" "✦"
    print_row "diamond" "❖"
    print_row "bolt" "⚡"
    print_row "arrow" "➜"
    print_row "triangle" "▶"
    print_row "circle" "●"
    print_row "square" "■"
    print_row "lambda" "λ"
    print_row "ship" "⛴"
    print_row "satellite" "🛰"
    print_row "comet" "☄"

    printf '\nFull-width scan line:\n'
    for codepoint in \
        EDF8 F0907 F1A61 F1A62 EDDE F15C6 EDEA ED99 EDFF EEF7 F0A44 EEED F011B \
        EEF1 F019A F18FC F0A43 F0AAD F16EE EF04 EF51 F15BF F15C0 F15C1 F186E E25F EF03 EF0A F07C6 F1558 F173F F03DA E85D F0401 F1006 F1678 EDA3 F1007 F1679 F047A F0FD9 F0CC6 F18FB \
        F01E5 F03D2 F329 F0EC0 F171B F171C \
        EEF8 F150E F0CD7 F15C2 F15C3 \
        EE41 F023A F13F3 F0EF3 F0EF4 F1AF F18B4 F0F01 F0F02 F18BA F18BB F1673 F1674 \
        F188 EAAF F46F F00E4 F0A2E F0A2F F0A30 F1589 F158A E28E F0FA1 F0FA2 F10CE F13ED F14E2 F211 F082D F1677 EF10 F11EA F11EB F0BCA \
        F1B0 F03E9 F1675 F0657 F1676 F1CF E882 E8C3 EF87 E251 F184B E29F ED5B F0B5F F037D F098B F245
    do
        printf '%s ' "$(glyph_from_codepoint "$codepoint")"
    done
    printf '\n'
}

print_header

case "$MODE" in
    all)
        print_icons
        printf '\n'
        print_colors
        ;;
    icons)
        print_icons
        ;;
    colors)
        print_colors
        ;;
esac
