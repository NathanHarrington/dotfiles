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
