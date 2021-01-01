# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions

alias l='ls -la'
alias vi='vim'
alias vim='vimx'
alias gg='sr google'

# visual differentiator for core computer
#PS1="# \W # "
export GITAWAREPROMPT=~/projects/dotfiles/.bash/git-aware-prompt
source "${GITAWAREPROMPT}/main.sh"

export PS1="\${debian_chroot:+(\$debian_chroot)}\u@\h:\w \[$txtcyn\]\$git_branch\[$txtred\]\$git_dirty\[$txtrst\]\$ "
export PS1="# \W \[$txtcyn\]\$git_branch\[$txtred\]\$git_dirty\[$txtrst\] # "
export PS1="\u@\h \W\[$txtcyn\]\$git_branch\[$txtred\]\$git_dirty\[$txtrst\] "


# No more .pyc files cluttering the directory.
export PYTHONDONTWRITEBYTECODE=1

# For resetting the stored git credential cache in order to use multiple
# git user id's on the same machine
alias credkill='killall git-credential-cache--daemon'
alias noise='play -c 2 -n synth brownnoise'

# Make the screen entirelyblank
alias cleanclear='export PS1="";clear'

eval "$BASH_POST_RC"


function pybadge() {
    echo "![pylint Score](https://mperlet.github.io/pybadge/badges/$(pylint ( 2> /dev/null | tail -n2 | awk '{print $7}' | cut -d"/" -f1).svg)"
}

# Use less for the bat pager with no line wrapping, display colors, case
# insensitive searches, don't erase the screen, and don't require q to exit
alias bat='bat --plain --pager "less -SRIXE"'


# Tmux sessions
alias workflowstmux=~/projects/dotfiles/tmux_generators/workflows_tmux
alias tunnelstmux=~/projects/dotfiles/tmux_generators/tunnels_tmux
alias w3mtmux=~/projects/dotfiles/tmux_generators/w3m_tmux
alias nathanharringtoninfotmux=~/projects/dotfiles/tmux_generators/nathanharringtoninfo_tmux
alias musictmux=~/projects/dotfiles/tmux_generators/music_tmux
alias rndban=~/projects/dotfiles/tmux_generators/rndban

# Stack overflow caclculator!
calc () { local in="$(echo " $*" | sed -e 's/\[/(/g' -e 's/\]/)/g')";
  gawk -M -v PREC=201 -M 'BEGIN {printf("%.60g\n",'"${in-0}"')}' < /dev/null
}

