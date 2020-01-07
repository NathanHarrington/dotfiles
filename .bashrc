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

# Tmux sessions
alias deimostmux=~/projects/dotfiles/tmux_generators/deimos_tmux 
alias titantmux=~/projects/dotfiles/tmux_generators/titan_tmux 
alias llstmux=~/projects/dotfiles/tmux_generators/lls_tmux 
alias workflowstmux=~/projects/dotfiles/tmux_generators/workflows_tmux
alias tunnelstmux=~/projects/dotfiles/tmux_generators/tunnels_tmux
alias w3mtmux=~/projects/dotfiles/tmux_generators/w3m_tmux
alias nathanharringtoninfotmux=~/projects/dotfiles/tmux_generators/nathanharringtoninfo_tmux
alias universalcbtmux=~/projects/dotfiles/tmux_generators/universalcb_tmux
alias mpsyttmux=~/projects/dotfiles/tmux_generators/mpsyt_edit_tmux
alias mpsyt='conda3; source activate mpsyt_py37; mpsyt'
alias ucbfirmwaretmux=~/projects/dotfiles/tmux_generators/ucbfirmware_tmux
alias labdiscoverytmux=~/projects/dotfiles/tmux_generators/labdiscovery_tmux
