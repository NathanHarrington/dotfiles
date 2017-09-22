# dotfiles
environment configuration resources


# System configuration instructions
Based on stock Fedoara Core 26 install:

    Install rpmfusion libraries (dnf install command for adding repos)

    dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
    dnf update -y
    (about 20 minutes later...)
    reboot


    Install virtualbox first, and verify, as this is the longest cycle
    testing to make sure the system has kernel configurations that are
    compatible.
    dnf install VirtualBox
    install the extension pack that exactly matches the virtualbox version number 5.2.16-r7771323 etc.

    After installing virtualbox, add the current user to the vboxusers group for usb access
    usermod -a -G vboxusers nharrington

    import the appliance for enlightendev
    import the appliance for dash3
    import the base win7 and win10 appliances for cloning



    # Basic development environment
    dnf -y install make automake gcc gcc-c++ kernel-devel cmake
    dnf -y install git autossh tmux
    dnf -y install redhat-rpm-config python-devel

    git clone https://github.com/NathanHarrington/dotfiles ~/projects/dotfiles

    dnf -y install parcellite vim 
    
    start parcellite, check "Use Copy" and "Use Primary", then click synchronize clipboards

    You may have to go to mouse and touchpad, then turn off "emulate
    middle click by clicking both left and right buttons" If using an
    external mouse.

    # Enable the timewaster blocks crontab entry as root:
    su -
    crontab -e
    59 * * * * /home/nharrington/projects/dotfiles/hosts_block.sh

Encrypt home folder:

    These are based on: 
    https://cloud-ninja.org/2014/04/05/fedora-encrypting-your-home-directory/

    After a fresh reboot, with no users logged in.
    Open a virtual console, login as root:

    dnf -y install keyutils ecryptfs-utils pam_mount
    authconfig --enableecryptfs --updateall
    usermod -aG ecryptfs nharrington
    ecryptfs-migrate-home -u nharrington

    # After perusing the messages about what to do next...

    su - nharrington

    # Write down the wrapped passphrase elsewhere...
    ecryptfs-unwrap-passphrase ~/.ecryptfs/wrapped-passphrase 

    # Include it locally...
    ecryptfs-insert-wrapped-passphrase-into-keyring ~/.ecryptfs/wrapped-passphrase

    # Reboot system, login as nharrington. Verify that the firefox history
    # is there, all the other expected files are there.

    # Remove the older, unencrypted home directory, something like:
    # rm -rf /home/nharrington.YwNG1Fho

    # Setup swap encryption, reboot
    ecryptfs-setup-swap

tmux configuration:

    Install xclip to enable copying from the tmux scrollback buffer to
    the system clipboard:
    dnf install xclip

    Setup tmux with the instructions from http://tony.github.io/tmux-config/:

    git clone https://github.com/tony/tmux-config.git ~/.tmux
    ln -s ~/.tmux/.tmux.conf ~/.tmux.conf
    cd ~/.tmux
    git submodule init
    git submodule update
    cd ~/.tmux/vendor/tmux-mem-cpu-load
    cmake .
    sudo make install

    cd ~
    tmux 
    ( press control + a then d to exit)
    tmux source-file ~/.tmux.conf

    Copy the custom tmux configuration:
    cp custom.tmux.conf ~/.tmux.conf
    tmux source-file ~/.tmux.conf

    

Gnome Configuration (3.204):

    Install and run gnome-tweak-tool

    Problems? run gnome-control-center from command line, looks for
    library fails

    In workspaces, change workspace creation to static, create 7 workspaces.
    Top Bar show date, show seconds
    Extensions, Launch new instance to On
    Extensions, Alternatetab to On
    Appearance, global dark theme to On
    
    Keyboard shortcuts, set Switch to workspace 1-4 to Alt-[1234]
    Add new shortcuts for workspaces 5,6,7 with the custom command type:
    wmctrl -s (workspace number-1)

    dnf install wmctrl

Miscellaneous configuration:

    cd ~/projects/dotfiles
    cp .bashrc ~/
    
    git config --global core.editor "vim"
    git config --global credential.helper "cache --timeout=360000"

    systemctl enable sshd
    systemctl start sshd

    dnf install w3m nmap    

Miscellaneous Configuration:

    To connect with other systems from this new system:
    ssh-keygen 
    (accept defaults)
    cat ~/.ssh/id_rsa.pub | \
        ssh (other system) "cat >> ~/.ssh/authorized_keys"

    chmod 0700 ~/.ssh
    chmod 0600 ~/.ssh/{authorized_keys,id_rsa}

    ssh (other system)

    Copy .gnupg from backup to ~/
    scp -r (backup-system) ~/.gnupg .

    hostnamectl set-hostname new_computer_hostname

Asus Zenbook UX305C specifics:

    hostnamectl set-hostname zenbook

    FC24 will not display all 16:9 options. All you really want is 1920x1080:
    Edit /etc/default/grub
    Append: video=1920x1080 to the CMDLINE_LINUX variable.
    
    Run: grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg as root
    
    This will "kick the 16:9" mode into place as described here:
    https://bugzilla.redhat.com/show_bug.cgi?id=1339930

    In keyboard shortcuts, set brightness up/down to windows+F5/F6


Lenovo w541 configuration:

    Swap Fn and Ctrl in BIOS
    Use Vertex theme for gnome here (install from source):
        https://github.com/horst3180/vertex-theme


Integrate the shared drive where appropriate:

    # These two as sudo
    mkdir -p /mnt/cifs_share/share_data

    (press enter for no remote system password)
    mount --verbose -t cifs -o uid=1000 \
        //192.168.1.250/was-share1 /mnt/cifs_share/share_data/

    # Run these as nharrington
    mkdir /home/nharrington/wasatch
    ln -s /mnt/cifs_share/share_data /home/nharrington/wasatch


### Setup the rclone backup option:

    Download and install rclone according to: http://rclone.org/install/

    Create the references to the various cloud storage options with:

    rclone config  
    Copy .rclone.conf from backup system
    scp -r (backup-system):.rclone.conf .


    After the .gnupg directory copy as described above, and with a fully verified key
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
    29 3 * * * $SCRIPTS/mail_summary >>$SCRIPTS/backup.log 2>&1


### rclone backup sends verification emails as well, so configure ssmtp:

    These are based on: http://crashmag.net/setting-up-ssmtp-with-gmail

    dnf -y install ssmtp mailx

    # Update the ssmtp.conf file as shown below, where domain is a
    "google apps for business" hosted domain, such as
    wasatchphotonics.com
     
    vi /etc/ssmtp/ssmtp.conf

    root=username@domain
    mailhub=smtp.gmail.com:587
    RewriteDomain=domain
    UseTLS=YES
    UseSTARTTLS=YES
    AuthUser=username@domain
    AuthPass=<app password created from google)

    alternatives --config mta
    (select sendmail.ssmtp)

    echo "username@domain" > ~/.forward

    Test mail configuration:

    echo "Test mail to root" | mail -s "Test root essmtp" root
    echo "Test mail to local" | mail -s "Test local" nharrington
    echo "Test mail to gmail" | mail -s "Test gmail" username@domain

### Autossh systemd service configuration instructions

    Edit the autossh.service file. Change the CUSTOM_REMOTE_PORT
    variable to a unique value for the host.  That is, make sure it's a
    port that isn't used by any other forwarding setup.  Add the correct
    reference to the private key. Change the ssh hostname and port
    numbers as required.

    First, ssh into the system in question to make sure the manual key
    agreement process is executed.

    cp autossh.service /etc/systemd/system/autossh.service
    systemctl enable NetworkManager-wait-online.service
    systemctl enable autossh

    (reboot to test)

### Hardware specific configurations

    Logitech Performance MX Mouse
    
    dnf install xdotool xbindkeys
    
    cat > ~/.xbindkeysrc
    "xdotool key Super"
    release + b:10
    
    echo "xbindkeys" > ~/.config/autostart/xbindkeys.desktop

### Install nomachine

    Download nomachine from: https://www.nomachine.com/download/linux&id=1 

    run:

    dnf install ./nomachine

    If you get a message about an selinux failure with systemd read from
    nxserver.service as describe here: https://www.nomachine.com/TR11N07360

    vi /etc/selinux/config

    change 'enforcing' to 'permissive'

    reinstall nomachine

### Mutt configuration

    mkdir -p ~/.mutt/cache

    cp /home/nharrington/projects/dotfiles/.muttrc ~/

    Edit the .muttrc configuration to include the appropriate app
    passwords, domain settings.

    cd ~/.mutt
    git clone https://github.com/altercation/mutt-colors-solarized

### Firefox and Chrome configuration
    Update to at least firefox version 54.0

    Install ublock origin for firefox
    Install disable ctrl-q exit plugin for firefox
    Install vimfx plugin for firefox
        (blacklist *mail.google.com*)
        Enable (Prevent autofocus of text inputs)
    Install Hide Caption Titlebar Plus for firefox
        Under look and feel 2, select 
            Smaller Tabs & Tab bar 
                (smaller like classic tabs, new)
            Smaller Toolbars & Buttons 
                ([Old] smaller buttons)
    
            Options for home button:
                (Transparent style/color)
                Select same icon size for both


    Under about:config
        set browser.fullscreen.autohide to False
    Preferences -> General -> "Show windows and tabs from last time"

    Install Dark Blue theme by G4Oblivion

    Install google crhome from the google repo:
	https://www.if-not-true-then-false.com/2010/install-\
		google-chrome-with-yum-on-fedora-red-hat-rhel/

    Sign in to chrome to get the settings below:
    Set chrome to "remember where you left off"
    Install ublock origin for chrome
    Install "fixed width text for gmail" extension for chrome

### Task warrior configuration

    # This configuration assumes that after task integration is
    # verified, you will import the tasks from other machines into the
    # auto backup folder

    dnf install task
    mkdir /home/nharrington/Documents/auto_backup/task_warrior
    ln -s /home/nharrington/Documents/auto_backup/task_warrior ~/.task
    task 

    (accept defaults)


### Vim configuration

    # Use vim awesome from: https://github.com/amix/vimrc
    git clone --depth=1 https://github.com/amix/vimrc.git ~/.vim_runtime
    sh ~/.vim_runtime/install_awesome_vimrc.sh

    Then copy the custom config:
    cp nharrington_vim_config ~/.vim_runtime/my_configs.vim


    # Install the DrawIt plugin
    # wget https://vim.sourceforge.io/scripts/script.php?script_id=40
     wget  \
        https://vim.sourceforge.io/scripts/download_script.php?src_id=21108
        -O DrawIt.vba.gz

    vi DrawIt.vba.gz
    :so %

    # Exit vim, restart vim

    # Apparently the \ leader character conflicts with a tmux setting,
    # so every time you want to use the DrawIt plugin, the workflow is:

    :let mapleader="-"
    :DIstart
    


