# dotfiles
environment configuration resources


# Cinnamon configuration instructions
Based on FC23 with cinnammon spin:

Goto themes, select esco window borders for blue edges
Background->Settings -> picture gradient of no picture, change color to
black. Turn off display of icons on desktop.

cp .bashrc ~/
Run timewaster blocks 

sudo hostnamectl set-hostname u430touch
sudo systemctl enable sshd
sudo systemctl start sshd


sudo dnf install git screen
sudo dnf install parcellite
sudo dnf install vim autossh
start parcellite, click synchronize clipboards

Run .vimrc top level instructions

Start a terminal, change to green on black color scheme, turn off
scrollbar display, no scrollbar buffer. Set menubar to not display by
default.

Change time display in bottom right panel applet to be custom format.
Add the workspace panel applet
Press alt-f1, add 6 more workspaces

Copy .gnupg from backup to ~/

Install ublock origin for firefox
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
