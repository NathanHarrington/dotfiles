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


# 2015-10-26 07:54 No more .pyc files cluttering the directory. Are you
# sure you want to do this? Are you going to get bit later in
# productions or on a different system where it finds an old .pyc file
# and you've lost familiarity with that error pattern? It will manifest
# as importing a module or access some code that should not exist on
# disk because you deleted the file.py file, but the file.pyc file is
# still there.
export PYTHONDONTWRITEBYTECODE=1

# Avoid inadvertent global package installation - this is good for older
# style virtual-env integrations, but will break conda
#export PIP_REQUIRE_VIRTUALENV=true

alias conda3='export PATH=/home/nharrington/miniconda3/bin:$PATH'
alias conda2='export PATH=/home/nharrington/miniconda2/bin:$PATH'

# For resetting the stored git credential cache in order to use multiple
# git user id's on the same machine
alias credkill='killall git-credential-cache--daemon'
alias noise='play -c 2 -n synth brownnoise'

# Use spyder from the full anaconda install for machine learning course
alias spyder='export PATH=/home/nharrington/anaconda3/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/home/nharrington/.local/bin:/home/nharrington/bin; spyder'

alias ml_path='export PATH=/home/nharrington/anaconda3/bin:$PATH'

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
alias rubberopticstmux=~/projects/dotfiles/tmux_generators/rubberoptics_tmux
alias nathanharringtoninfotmux=~/projects/dotfiles/tmux_generators/nathanharringtoninfo_tmux
alias universalcbtmux=~/projects/dotfiles/tmux_generators/universalcb_tmux
alias mpsyttmux=~/projects/dotfiles/tmux_generators/mpsyt_edit_tmux
