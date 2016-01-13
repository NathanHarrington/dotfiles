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


LOGO_BLOCK="
██╗    ██╗ █████╗ ███████╗ █████╗ ████████╗ ██████╗██╗  ██╗             
██║    ██║██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔════╝██║  ██║             
██║ █╗ ██║███████║███████╗███████║   ██║   ██║     ███████║             
██║███╗██║██╔══██║╚════██║██╔══██║   ██║   ██║     ██╔══██║             
╚███╔███╔╝██║  ██║███████║██║  ██║   ██║   ╚██████╗██║  ██║             
 ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝             
                                                                        
██████╗ ██╗  ██╗ ██████╗ ████████╗ ██████╗ ███╗   ██╗██╗ ██████╗███████╗
██╔══██╗██║  ██║██╔═══██╗╚══██╔══╝██╔═══██╗████╗  ██║██║██╔════╝██╔════╝
██████╔╝███████║██║   ██║   ██║   ██║   ██║██╔██╗ ██║██║██║     ███████╗
██╔═══╝ ██╔══██║██║   ██║   ██║   ██║   ██║██║╚██╗██║██║██║     ╚════██║
██║     ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚████║██║╚██████╗███████║
╚═╝     ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝╚══════╝
"

LOGO_CURSIVE="
WW      WW   AAA    SSSSS    AAA   TTTTTTT  CCCCC  HH   HH            
WW      WW  AAAAA  SS       AAAAA    TTT   CC    C HH   HH            
WW   W  WW AA   AA  SSSSS  AA   AA   TTT   CC      HHHHHHH            
 WW WWW WW AAAAAAA      SS AAAAAAA   TTT   CC    C HH   HH            
  WW   WW  AA   AA  SSSSS  AA   AA   TTT    CCCCC  HH   HH            
                                                                      
PPPPPP  HH   HH  OOOOO  TTTTTTT  OOOOO  NN   NN IIIII  CCCCC   SSSSS  
PP   PP HH   HH OO   OO   TTT   OO   OO NNN  NN  III  CC    C SS      
PPPPPP  HHHHHHH OO   OO   TTT   OO   OO NN N NN  III  CC       SSSSS  
PP      HH   HH OO   OO   TTT   OO   OO NN  NNN  III  CC    C      SS 
PP      HH   HH  OOOO0    TTT    OOOO0  NN   NN IIIII  CCCCC   SSSSS  
"

LOGO_BLIMP="
 _     _  _______  _______  _______  _______  _______  __   __                
| | _ | ||   _   ||       ||   _   ||       ||       ||  | |  |               
| || || ||  |_|  ||  _____||  |_|  ||_     _||       ||  |_|  |               
|       ||       || |_____ |       |  |   |  |       ||       |               
|       ||       ||_____  ||       |  |   |  |      _||       |               
|   _   ||   _   | _____| ||   _   |  |   |  |     |_ |   _   |               
|__| |__||__| |__||_______||__| |__|  |___|  |_______||__| |__|               
 _______  __   __  _______  _______  _______  __    _  ___   _______  _______ 
|       ||  | |  ||       ||       ||       ||  |  | ||   | |       ||       |
|    _  ||  |_|  ||   _   ||_     _||   _   ||   |_| ||   | |       ||  _____|
|   |_| ||       ||  | |  |  |   |  |  | |  ||       ||   | |       || |_____ 
|    ___||       ||  |_|  |  |   |  |  |_|  ||  _    ||   | |      _||_____  |
|   |    |   _   ||       |  |   |  |       || | |   ||   | |     |_  _____| |
|___|    |__| |__||_______|  |___|  |_______||_|  |__||___| |_______||_______|
"
RED='\033[0;33m'
NC='\033[0m' # No Color

# Present a wasatch photonics logo, and lock the system with no password prompt.
# You can still type in the password and it will unlock
lock() {
    NUMBER=$(( $RANDOM % 3 ))
    printf "\n"
    if [ "$NUMBER" == "0" ]; then
        echo "${LOGO_BLOCK}"
    fi
    if [ "$NUMBER" == "1" ]; then
        echo "${LOGO_CURSIVE}"
    fi
    if [ "$NUMBER" == "2" ]; then
        echo "${LOGO_BLIMP}"
    fi

    printf "\n"
    printf "${RED}"
    vlock 2>/dev/null
    printf "${NC}"
}

# 2015-10-26 07:54 No more .pyc files cluttering the directory. Are you
# sure you want to do this? Are you going to get bit later in
# productions or on a different system where it finds an old .pyc file
# and you've lost familiarity with that error pattern? It will manifest
# as importing a module or access some code that should not exist on
# disk because you deleted the file.py file, but the file.pyc file is
# still there.
export PYTHONDONTWRITEBYTECODE=1

# Avoid inadvertent global package installation
export PIP_REQUIRE_VIRTUALENV=true

