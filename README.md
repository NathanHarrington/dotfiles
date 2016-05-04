# dotfiles
environment configuration resources


# Cinnamon configuration instructions
Based on FC23 with cinnammon spin:

    Goto themes, select esco window borders for blue edges
    Background->Settings -> picture gradient of no picture, change color to
    black. Turn off display of icons on desktop.

    Start a terminal, change to green on black color scheme, turn off
    scrollbar display, no scrollbar buffer. Set menubar to not display by
    default.

    Change time display in bottom right panel applet to be custom format.
    Add the workspace panel applet
    Press alt-f1, add 6 more workspaces


    sudo dnf -y install git autossh screen
    git clone https://github.com/NathanHarrington/dotfiles

    cd dotfiles
    sudo ./timewaster-blocks.sh

    cp .bashrc ~/
    sudo systemctl enable sshd
    sudo systemctl start sshd
    
    sudo dnf -y install parcellite vim 
    
    start parcellite, check "Use Copy" and "Use Primary", thne click synchronize clipboards

    Right click icons on taskbar, remove.
    Right click the word menu, remove the text, change to custom icon.

    Run .vimrc top level instructions


Lenovo U430-touch specifics:
    sudo hostnamectl set-hostname u430touch

MacBook Pro 
    sudo hostnamectl set-hostname mbp-fc23
    sudo dnf -y update
    sudo dnf install -y 
    
    Install rpm fusion libraries as described here:
        http://rpmfusion.org/Configuration/
    
    Use the onpub.com broadcom installation script described here:
        https://onpub.com/install-broadcom-linux-wi-fi-driver-on-fedora-23-s7-a192

    This will lead to "almost works" status with the built-in broadcom
    chipset. Alternatives include wired access and external dongles.
    Unfortunately there are also various standby issues at this time, so
    inhibiting the macbook pro experiment.


Integrate the shared drive where appropriate:

    sudo mkdir -p /mnt/cifs_share/share_data
    sudo mount --verbose -t cifs -o uid=1000 \
        //192.168.1.250/was-share1 /mnt/cifs_share/share_data/

    (press enter for no password)

    mkdir /home/nharrington/wasatch
    ln -s /mnt/cifs_share/share_data /home/nharrington/wasatch



Copy .gnupg from backup to ~/

Install ublock origin for firefox
Install disable ctrl-q exit plugin for firefox
Install Dropbox, spideroak

Login to spideroak, dropbox, reboot make sure the services start at
login.

Modify the encrypt_to_cloud.sh script to make a gpg encrypted tar file,
upload every hour. This is the 'warm' backup of anything on the disk
that is absolutely critical. Add entry to crontab like:
# Every hour sync with dropbox
38 * * * * $HOME/Documents/encryption/encrypt_to_cloud.sh

This is to create a series of easier to manage tar files that are stored
on a per-system basis.


TODO:
setup autossh tunneling service at system login
    tested setups monitored outside of channels

store all of these settings in dotfiles repositories to make environment
    more portable

digital imagery export from cloud hosting providers for long term backup
set timewaster blocks to auto start, iptables save
