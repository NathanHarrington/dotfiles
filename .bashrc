# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# User specific environment
if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]; then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi
export PATH

# User specific aliases and functions
if [ -d ~/.bashrc.d ]; then
    for rc in ~/.bashrc.d/*; do
        if [ -f "$rc" ]; then
            . "$rc"
        fi
    done
fi
unset rc

# .bashrc aliases and prompts
export PYENV_ROOT="$HOME/.pyenv"
if [[ -d "$PYENV_ROOT/bin" ]]; then
    export PATH="$PYENV_ROOT/bin:$PATH"
fi

if [[ $- == *i* ]]; then
    eval "$(pyenv init - --no-rehash)"
fi

# Use less for the bat pager with wrapping, display colors, case
# insensitive searches, don't erase the screen, and require q to
# exit
alias bat='bat --plain --pager "less -RIX"'

# Display all files by default
alias rg='rg --hidden'

# Use the awesome eza tool instead of ls
alias eza='eza -la'

# Use trash instead of rm 
alias tp='trash-put'

alias shutter-clip='shutter --select --output=/tmp/screenshot.png && (wl-copy < /tmp/screenshot.png 2>/dev/null || xclip -selection clipboard -target image/png -in /tmp/screenshot.png) && rm /tmp/screenshot.png'

# Stack overflow caclculator!
calc () { local in="$(echo " $*" | sed -e 's/\[/(/g' -e 's/\]/)/g')";
  gawk -M -v PREC=201 -M 'BEGIN {printf("%.60g\n",'"${in-0}"')}' < /dev/null
}

export PATH="/home/nharrington/projects/chromedriver:$PATH"
export PATH="$HOME/.cargo/bin:$PATH"

# No more .pyc files cluttering the directory.
export PYTHONDONTWRITEBYTECODE=1
export EDITOR=vim
alias vi='vimx'
alias vim='vimx'
eval "$(starship init bash)"
export PIPENV_VERBOSITY=-1

# Set console colors: bright green text on black background (for framebuffer console)
if [ "$TERM" = "linux" ] || [ -t 0 ] && [ -z "$DISPLAY" ]; then
    # Set bright green foreground, black background using console escape sequences
    printf '\033]P0000000'  # Black background
    printf ']P200ff00'  # Bright green palette slot
    printf ']P700ff00'  # Bright green default foreground
    printf ']PA00ff00'  # Bright green alternate slot
    # Alternative: use setterm if available
    if command -v setterm >/dev/null 2>&1; then
        setterm --foreground green --background black 2>/dev/null || true
    fi
fi

# Force blinking block cursor at each prompt
PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND; }printf \"\\e[1 q\""

export PATH="$HOME/.npm-global/bin:$PATH"



if [[ $- == *i* ]]; then
    TEMPO_LOGINDISPLAY="/home/nharrington/projects/Tempo/src/tempo/logindisplay.py"
    if [[ -x "$TEMPO_LOGINDISPLAY" ]]; then
        "$TEMPO_LOGINDISPLAY" --message "WELCOME MR. HARRINGTON" --green
    fi
fi

# Create or attach to a tmux session, defaulting to a tmux-safe name based on the current directory.
th() {
    local raw_name session_name
    if [[ -n "$1" ]]; then
        raw_name="$1"
    else
        raw_name="${PWD##*/}"
        [[ -n "$raw_name" && "$raw_name" != "/" ]] || raw_name="main"
    fi

    session_name="${raw_name//[^[:alnum:]_-]/-}"
    while [[ "$session_name" == *--* ]]; do
        session_name="${session_name//--/-}"
    done
    session_name="${session_name#-}"
    session_name="${session_name%-}"
    [[ -n "$session_name" ]] || session_name="main"

    tmux new-session -A -s "$session_name"
}
