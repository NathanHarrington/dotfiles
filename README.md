# dotfiles
environment configuration resources


# Cinnamon configuration instructions
Based on FC23 with cinnammon spin:

    sudo dnf -y update

    (about 20 minutes later...)

    After the dnf update, go to Themes, download the themes:
        Ambience Crunchy (OS-Crunchy-green), Faince+
        Choose esco window borders
        Choose OS-Crunhcy-green controls
        Choose Desktop Faince+
        This approach gives you full borders around entire command line
        windows to highlight current focus. Green controls in certain
        areas, and a dark taskbar.

    Backgrounds->Settings->Picture aspect of no picture, change color to
    black. Turn off display of icons on desktop.

    Start a terminal, change to green on black color scheme, turn off
    scrollbar display, no scrollbar buffer. Set menubar to not display by
    default.

    Enter panel edit mode, move the "All windows" applet so the clock is
    in the bottom right.

    Change time display in bottom right panel applet to be custom format:
        %Y-%m-%d %H:%M:%S

    Add the workspace switcher panel applet, press alt-f1, create a
        total of 7 workspaces.

    Keyboard->Shortcuts->Workspaces->Direct Navigation:
        Add alt+N for direct to workspace N
   
    Open the applets application, go online and install the network
    applet:
        Network usage monitor with alerts.
        Configure to show combined up/down, select appropriate
        interface.

    Right click icons on taskbar, remove.
    Right click the word menu, remove the text, change to custom icon.

    sudo dnf -y install git autossh screen
    git clone https://github.com/NathanHarrington/dotfiles

    # Enable the timewaster blocks crontab entry:
    sudo su -
    crontab -e
    59 * * * * /home/nharrington/projects/dotfiles/hosts_block.sh


    cp .bashrc ~/
    sudo systemctl enable sshd
    sudo systemctl start sshd
    
    sudo dnf -y install parcellite vim 
    
    start parcellite, check "Use Copy" and "Use Primary", then click synchronize clipboards

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
Install Dropbox rpm from their website
Install spideroak rpm from their website
Install nomachine rpm from their website

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
    autossh -M 28767 -o port=<public port> -L 8190:<internal network ip>:22
        username@public facing ip

    Lets say you forget and leave your computer at a network location
    without port forwarding. The autossh command will survive standby's
    power cycles, unlocks, etc. It connects a tunnel from the laptop to
    the shared server (cloud droplet). You then connect to the cloud
    droplet from a different computer, then tunnel the connection back
    through the ssh connections like:

    laptop->server (public port) -R 9000:localhost:22
    other->server (public port) -L 9022:localhost:9000
    other ssh -L 9022 localhost
        (which forwards to port 9000 on server, which goes to port 22 on
        laptop)
    Then from there it's all derivates of vnc/nx port forwarding.


store all of these settings in dotfiles repositories to make environment
    more portable

digital imagery export from cloud hosting providers for long term backup
