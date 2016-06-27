# dotfiles
environment configuration resources


# Cinnamon configuration instructions
Based on FC23 with cinnammon spin:

    sudo dnf -y update

    (about 20 minutes later...)
    
    (system specific integrations here - scroll down)



    # Basic development environment
    sudo dnf -y install make automake gcc gcc-c++ kernel-devel cmake
    sudo dnf -y install git autossh tmux
    sudo dnf -y install redhat-rpm-config python-devel

    git clone https://github.com/NathanHarrington/dotfiles ~/projects/dotfiles

    sudo dnf -y install parcellite vim 
    
    start parcellite, check "Use Copy" and "Use Primary", then click synchronize clipboards

    You may have to go to mouse and touchpad, then turn off "emulate
    middle click by clicking both left and right buttons" If using an
    external mouse.

    # Enable the timewaster blocks crontab entry as root:
    sudo su -
    crontab -e
    59 * * * * /home/nharrington/projects/dotfiles/hosts_block.sh


    # Create tmux configuration following:
    http://tony.github.io/tmux-config/

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
        2016-06-27 FC24 ships out of the box with themes. Combining:
        Window Borders: Esco
        Controls: BlueMenta
        Desktop: Blue-submarine 
        Looks good, and has the fully colored edge window borders

    Backgrounds->Settings->Picture aspect of no picture, change color to
    black. Turn off display of icons on desktop.

    Start a terminal, change to green on black color scheme, turn off
    scrollbar display, no scrollbar buffer size limit. Set menubar to
    not display by default. Set initial startup size to 100x30 (for tmux
    to look good at startup font size)

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

    Go to accessibility, make sure "Enable Zoom" is on. Make sure mouse
    wheel modifier is disabled - use keyboard shortcut instead.

    (in dotfiles)
    cp .bashrc ~/
    
    git config --global core.editor "vim"
    git config --global credential.helper "cache --timeout=360000"

    sudo systemctl enable sshd
    sudo systemctl start sshd
    

    # Pre-20160525 vim instructions are in wasatch.vimrc
    You probably don't want those. You want:
    https://github.com/amix/vimrc

    Then copy the custom config:
    cp nharrington_vim_config ~/.vim_runtime/my_configs.vim


    To connect with other systems from this new system:
    ssh-keygen 
    (accept defaults)
    cat ~/.ssh/id_rsa.pub | \
        ssh (other system) "cat >> ~/.ssh/authorized_keys"

    chmod 0700 ~/.ssh
    chmod 0600 ~/.ssh/{authorized_keys,id_rsa}

    ssh (other system)


Lenovo U430-touch specifics:

    sudo hostnamectl set-hostname u430touch

Asus Zenbook UX305C specifics:

    sudo hostnamectl set-hostname zenbook

    FC24 will not display all 16:9 options. All you really want is 1920x1080:
    Edit /etc/default/grub
    Append: video=1920x1080 to the CMDLINE_LINUX variable.
    
    Run: grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg as root
    
    This will "kick the 16:9" mode into place as described here:
    https://bugzilla.redhat.com/show_bug.cgi?id=1339930

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

Install ublock origin for chrome
Install "fixed width text for gmail" extension for chrome
Set chrome to "remember where you left off"

### Setup the rclone backup option:

    Download and install rclone according to: http://rclone.org/install/

    Create the references to the various cloud storage options with:

    rclone config  

    (google drive, onedrive, dropbox, etc.)

    After the .gnupg copy as described above, and with a fully verified key
    management and recovery system:

    # Anything you put in the folder below will be auto-backed up to the
    # cloud, with encryption
    mkdir ~/Documents/auto_backup/
    
    Add the following to crontab -e:
    
    SCRIPTS=/home/nharrington/projects/dotfiles/backup_scripts
    BACKUP_PREFIX=nh  (change this to the correct prefix! )
    13 * * * * $SCRIPTS/encrypt_directory.sh >>$SCRIPTS/backup.log 2>&1
    44 * * * * $SCRIPTS/rclone_hourly >>$SCRIPTS/backup.log 2>&1
    
    # Email a summary of the backup directories for hand verification
    MAIL_DEST="nharrington@wasatchphotonics.com" 
    28 3 * * * $SCRIPTS/mail_summary >>$SCRIPTS/backup.log 2>&1


### rclone backup sends verification emails as well, so configure ssmtp:

    These are based on: http://crashmag.net/setting-up-ssmtp-with-gmail

    sudo dnf -y install ssmtp mailx

    # Update the ssmtp.conf file as shown below, where domain is a
    "google apps for business" hosted domain, such as
    wasatchphotonics.com
    
    sudo vi /etc/ssmtp/ssmtp.conf

    root=username@domain
    mailhub=smtp.gmail.com:587
    RewriteDomain=domain
    UseTLS=YES
    UseSTARTTLS=YES
    AuthUser=username@domain
    AuthPass=<app password created from google)

    sudo alternatives --config mta
    (select sendmail.ssmtp)

    echo "username@domain" > ~/.forward

    Test mail configuration:

    echo "Test mail to root" | mail -s "Test root essmtp" root
    echo "Test mail to local" | mail -s "Test local" nharrington
    echo "Test mail to gmail" | mail -s "Test gmail" username@domain


TODO:
store all of these settings in dotfiles repositories to make environment
    more portable

