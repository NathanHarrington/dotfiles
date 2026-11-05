#!/usr/bin/env python3
"""Preview purple login greetings: dotted text, a typewriter panel, or block letters."""

import argparse
import os
import shutil
import sys
import textwrap
import time

MESSAGE = "WELCOME MR. HARRINGTON"
BLOCK_MESSAGE = "WELCOME MR. HARRINGTON"
BLOCK_FADE_SECONDS = 1.0
BLOCK_FADE_FRAMES = 50
# Embedded terminus_dots render from Tempo's logindisplay.py; no figlet needed.
BANNER = (
    "⡄⠀⡄⡤⠤⠄⡄⠀⠀⡠⠤⡀⡠⠤⡀⣄⢀⡄⡤⠤⠄⠀⠀⠀ ⣄⢀⡄⡤⠤⡀⠀⠀⠀⠀⠀⠀ ⡄⠀⡄⡠⠤⡀⡤⠤⡀⡤⠤⡀⠠⡤⠀⡄⠀⡄⡠⠤⡀⠤⡤⠄⡠⠤⡀⡄⠀⡄",
    "⡇⡄⡇⡗⠒⠀⡇⠀⠀⡇⠀⠀⡇⠀⡇⡇⠃⡇⡗⠒⠀⠀⠀⠀ ⡇⠃⡇⡧⡤⠃⠀⠀⠀⠀⠀⠀ ⡗⠒⡇⡧⠤⡇⡧⡤⠃⡧⡤⠃⠀⡇⠀⡏⠢⡇⡇⠤⡄⠀⡇⠀⡇⠀⡇⡏⠢⡇",
    "⠋⠈⠃⠓⠒⠂⠓⠒⠂⠑⠒⠁⠑⠒⠁⠃⠀⠃⠓⠒⠂⠀⠀⠀ ⠃⠀⠃⠃⠈⠂⠀⠃⠀⠀⠀⠀ ⠃⠀⠃⠃⠀⠃⠃⠈⠂⠃⠈⠂⠐⠓⠀⠃⠀⠃⠑⠒⠁⠀⠃⠀⠑⠒⠁⠃⠀⠃",
)
PURPLE = "\x1b[38;2;192;132;252m"
SOFT_PURPLE = "\x1b[38;2;126;87;166m"
WHITE = "\x1b[38;2;245;245;245m"
RESET = "\x1b[0m"
STYLES = {
    "dots": "Original dotted lettering with a white and purple sweep",
    "typewriter": "Compact purple panel with text typed into place",
    "blocks": "WELCOME MR. HARRINGTON in one row of blocks, with a violet fade",
}
BLOCK_FONT = {
    "W": ("█   █", "█   █", "█ █ █", "██ ██", "█   █"),
    "E": ("█████", "█    ", "████ ", "█    ", "█████"),
    "L": ("█    ", "█    ", "█    ", "█    ", "█████"),
    "C": (" ████", "█    ", "█    ", "█    ", " ████"),
    "O": (" ███ ", "█   █", "█   █", "█   █", " ███ "),
    "M": ("█   █", "██ ██", "█ █ █", "█   █", "█   █"),
    "R": ("████ ", "█   █", "████ ", "█  █ ", "█   █"),
    "H": ("█   █", "█   █", "█████", "█   █", "█   █"),
    "A": (" ███ ", "█   █", "█████", "█   █", "█   █"),
    "I": ("█████", "  █  ", "  █  ", "  █  ", "█████"),
    "N": ("█   █", "██  █", "█ █ █", "█  ██", "█   █"),
    "G": (" ████", "█    ", "█ ███", "█   █", " ███ "),
    "T": ("█████", "  █  ", "  █  ", "  █  ", "  █  "),
    ".": (" ", " ", " ", " ", "█"),
}
BLOCK_COLORS = ((216, 180, 254), (208, 164, 253), (192, 132, 252),
                (180, 110, 250), (168, 85, 247))


def block_lines(width, height):
    lines = [
        "    ".join(
            "  ".join(BLOCK_FONT[letter][row] for letter in word)
            for word in BLOCK_MESSAGE.split()
        )
        for row in range(5)
    ]
    if len(lines[0]) <= width and len(lines) <= height:
        return lines

    # Pack each 2x2 group of pixels into a quadrant block. This keeps the
    # complete lettering on a single baseline in narrower terminal panes.
    quadrants = " ▘▝▀▖▌▞▛▗▚▐▜▄▙▟█"
    packed = []
    for y in range(0, len(lines), 2):
        row = []
        for x in range(0, len(lines[0]), 2):
            mask = 0
            for dx, dy, bit in ((0, 0, 1), (1, 0, 2), (0, 1, 4), (1, 1, 8)):
                if y + dy < len(lines) and x + dx < len(lines[0]):
                    if lines[y + dy][x + dx] == "█":
                        mask |= bit
            row.append(quadrants[mask])
        packed.append("".join(row))
    if len(packed[0]) <= width and len(packed) <= height:
        return packed

    # Below the readable block size, preserve the full message on one line.
    return [BLOCK_MESSAGE] if len(BLOCK_MESSAGE) <= width else []


def greeting_lines(style, width, plain_terminal, height=24):
    if style == "blocks":
        if plain_terminal:
            return [BLOCK_MESSAGE] if len(BLOCK_MESSAGE) <= width else []
        return block_lines(width, height)
    if not plain_terminal:
        if style == "dots" and width >= 68:
            return list(BANNER)
        if style == "typewriter" and width >= 30:
            inner = 28
            return [
                "┌" + "─ L I M A ".ljust(inner, "─") + "┐",
                "│" + " " * inner + "│",
                "│ " + MESSAGE.ljust(inner - 2) + " │",
                "│" + " " * inner + "│",
                "└" + "─" * inner + "┘",
            ]
    return textwrap.wrap(MESSAGE, width)


def colored_lines(style, lines, brightness=1.0):
    result = []
    for row, line in enumerate(lines):
        if style == "blocks":
            shade = row * (len(BLOCK_COLORS) - 1) // max(1, len(lines) - 1)
            rgb = BLOCK_COLORS[shade]
            color = "\x1b[38;2;{};{};{}m".format(*(int(c * brightness) for c in rgb))
        elif style == "typewriter" and line.startswith(("┌", "│", "└")):
            color = PURPLE if row == 2 else SOFT_PURPLE
        else:
            color = PURPLE
        result.append(color + line + RESET)
    return result


def write_lines(lines):
    if os.environ.get("TERM", "dumb") != "dumb":
        # Reset the background and clear the entire row, including the unused
        # columns to the right, before drawing each animation frame.
        lines = ["\r" + RESET + "\x1b[2K" + line + RESET for line in lines]
    sys.stdout.write("\r\n".join(lines) + "\r\n")
    sys.stdout.flush()


def reveal_line(line, step):
    parts = []
    for column, char in enumerate(line):
        if column >= step:
            parts.append(" ")
        elif column >= step - 2:
            parts.append(WHITE + char)
        elif column >= step - 7:
            parts.append(SOFT_PURPLE + char)
        else:
            parts.append(PURPLE + char)
    return "".join(parts) + RESET


def animation_frames(style, lines):
    if style == "dots":
        for step in range(1, max(map(len, lines)) + 8):
            yield [reveal_line(line, step) for line in lines], 0.01
    elif style == "typewriter":
        boxed = lines[0].startswith("┌")
        length = len(MESSAGE) if boxed else sum(map(len, lines))
        for step in range(length + 1):
            cursor = "▌" if step < len(MESSAGE) else ""
            if boxed:
                frame = lines.copy()
                frame[2] = "│ " + (MESSAGE[:step] + cursor).ljust(26) + " │"
            else:
                frame = []
                remaining = step
                for line in lines:
                    count = min(len(line), max(0, remaining))
                    frame.append(line[:count].ljust(len(line)))
                    remaining -= len(line)
            yield colored_lines(style, frame), 0.035
    else:
        for step in range(1, BLOCK_FADE_FRAMES + 1):
            brightness = (step / BLOCK_FADE_FRAMES) ** 1.5
            yield colored_lines(style, lines, brightness), BLOCK_FADE_SECONDS / BLOCK_FADE_FRAMES


def show_greeting(style, width, plain_terminal, once, height=24):
    lines = greeting_lines(style, width, plain_terminal, height)
    if not lines:
        return
    write_lines([""])
    if os.environ.get("TERM", "dumb") == "dumb":
        write_lines(lines)
        return
    if once or not sys.stdout.isatty():
        write_lines(colored_lines(style, lines))
        return

    try:
        sys.stdout.write("\x1b[?25l")
        for index, (frame, delay) in enumerate(animation_frames(style, lines)):
            if index:
                sys.stdout.write(f"\x1b[{len(lines)}F")
            write_lines(frame)
            time.sleep(delay)
    finally:
        sys.stdout.write(RESET + "\x1b[?25h")
        sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--style", choices=STYLES, default="dots", help="Greeting style (default: dots).")
    choice.add_argument("--preview", action="store_true", help="Compare all three styles in this terminal.")
    parser.add_argument("--once", action="store_true", help="Print without animating.")
    args = parser.parse_args()

    # Leave a spare column so terminals never wrap while a frame is redrawn.
    terminal = shutil.get_terminal_size((80, 24))
    width = max(1, terminal.columns - 1)
    height = max(1, terminal.lines - 1)
    plain_terminal = os.environ.get("TERM", "dumb") in ("dumb", "linux")
    try:
        for style in STYLES if args.preview else (args.style,):
            if args.preview:
                # Wrap labels too, so the comparison works in a narrow pane.
                write_lines([""] + textwrap.wrap(f"{style}: {STYLES[style]}", width))
            show_greeting(style, width, plain_terminal, args.once, height)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
