# dotfiles
environment configuration resources


# Cinnamon configuration instructions
Based on FC23 with cinnammon spin:

    sudo dnf -y update

    (about 20 minutes later...)
    
    (system specific integrations here - scroll down)


    sudo dnf -y install git autossh screen
    git clone https://github.com/NathanHarrington/dotfiles

    # Enable the timewaster blocks crontab entry:
    crontab -e
    59 * * * * /home/nharrington/projects/dotfiles/hosts_block.sh

    Go to Themes, download the themes:
        Ambience Crunchy (OS-Crunchy-green), Faince+
        Choose esco window borders
        Choose OS-Crunhcy-green controls
        Choose Desktop Faince+
        This approach gives you full borders around entire command line
        windows to highlight current focus. Green controls in certain
        areas, and a dark taskbar. That's the goal at least. apparently
        these results are different for different installs. As of
        2016-05-13 06:53 a decent option appears to be window borders
        from ubuntu-xenial Xenus, gnome icons, adwaita controls, adwaita
        mouse pointer and Faience+ desktop.

    Backgrounds->Settings->Picture aspect of no picture, change color to
    black. Turn off display of icons on desktop.

    Start a terminal, change to green on black color scheme, turn off
    scrollbar display, no scrollbar buffer size limit. Set menubar to
    not display by default.

    Enter panel edit mode, move the "All windows" applet so the clock is
    in the bottom right.

    Change time display in bottom right panel applet to be custom format:
        %Y-%m-%d %H:%M:%S

    Add the workspace switcher panel applet, press alt-f1, create a
        total of 7 workspaces.

    Keyboard->Shortcuts->Workspaces->Direct Navigation:
        Add alt+N for direct to workspace N
  
    Windows->Behavior->Location of newly opened windows to Automatic

    Open the applets application, go online and install the network
    applet:
        Network usage monitor with alerts.
        Configure to show combined up/down, select appropriate
        interface.

    Right click icons on taskbar, remove.
    Right click the word menu, remove the text, change to custom icon.


    (in dotfiles)
    cp .bashrc ~/
    sudo systemctl enable sshd
    sudo systemctl start sshd
    
    sudo dnf -y install parcellite vim 
    
    start parcellite, check "Use Copy" and "Use Primary", then click synchronize clipboards

    Run .vimrc top level instructions

    # Basic development environment
    sudo dnf -y make automake gcc gcc-c++ kernel-devel


Lenovo U430-touch specifics:
    sudo hostnamectl set-hostname u430touch

Asus Zenbook UX305C specifics:
    sudo hostnamectl set-hostname zenbook

    As of 2016-05-12 16:44 touchpad will not work out of the box:

    FC23 Live Cinnamon change boot in grub of usb disk, append
    i915.preliminary_hw_support=1

    After installing, and running dnf -y update above, reboot
    Add the most recent mainline kernel as described here:
    https://fedoraproject.org/wiki/Kernel_Vanilla_Repositories

    Reboot, verify that secure boot is disabled in the bios

    In keyboard shortcuts, set brightness up/down to windows+F5/F6


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

### Setup the nuclear backup option:

    Download and install rclone according to: http://rclone.org/install/

    After the .gnupg copy as described above, and with a fully verified key
    management and recovery system:

    # Anything you put in the folder below will be auto-backed up to the
    # cloud, with encryption
    mkdir ~/Documents/auto_backup/
    
    Add the following to crontab -e:
    
    SCRIPTS=/home/nharrington/projects/dotfiles/backup_scripts
    13 * * * * $SCRIPTS/encrypt_directory.sh >>$SCRIPTS/backup.log 2>&1
    14 * * * * $SCRIPTS/daily >>$SCRIPTS/backup.log 2>&1


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
    Then from there it's all derivatives of vnc/nx port forwarding.


store all of these settings in dotfiles repositories to make environment
    more portable

digital imagery export from cloud hosting providers for long term backup
