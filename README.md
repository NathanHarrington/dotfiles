# dotfiles
environment configuration resources


# System configuration instructions
Based on stock Fedoara Core 26 install:

    During the installation process, set the hostname:
    The procedure below expects the entire drive to be dedicated to the
    fedora install, with the 'auto' partitioning setup.

    Install rpmfusion libraries (dnf install command for adding repos)

    dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
    dnf update -y
    (about 20 minutes later...)
    reboot


    Install virtualbox first, and verify, as this is the longest cycle
    testing to make sure the system has kernel configurations that are
    compatible.

    dnf install VirtualBox

    # Install the extension pack that exactly matches the virtualbox
    #    version: 5.2.16-r7771323 etc.

    After installing virtualbox, add the current user to the vboxusers 
    group for usb access:

    usermod -a -G vboxusers nharrington

    This can't be stressed enough: test virtualbox first on the machine
    before you go full config. There are many ways (especially on bleeding
    edge hardware) that this can fail, and you want to know at the
    beginning, not at the end.

    After VirtualBox is functional, skip to the VirtualBox section below
    for more details.

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

    # Execute the unwrapped passphrase command and write down the
    # unwrapped passphrase elsewhere if you're paranoid
    # ecryptfs-unwrap-passphrase 

    # Include it locally...
    ecryptfs-insert-wrapped-passphrase-into-keyring ~/.ecryptfs/wrapped-passphrase

    # Reboot system, login as nharrington. Verify that the firefox history
    # is there, all the other expected files are there.

    # Remove the older, unencrypted home directory, something like:
    # rm -rf /home/nharrington.YwNG1Fho

    # Setup swap encryption, reboot
    ecryptfs-setup-swap

    # On the Lenovo u430 touch from 2013, an encrypted swap will lead to system
    # wide lock ups. If this failure repeats on other systems, the workaround is to
    # have a secondary swap file created according to:
    #  https://www.linux.com/learn/ \
          increase-your-available-swap-space-swap-file 

    # dd if=/dev/zero of=/extraswap bs=1M count=4096 
    # chmod 0600 /extraswap 
    # mkswap /extraswap 
    # cp /etc/fstab /etc/fstab.mybackup 

    # Add the line to fstab: 
    # /extraswap   none swap   sw   0   0

    # Reboot - Now when you run `swapon -s` you'll see the /extraswap 4GB file
    # be used under heavy load, and the existing encrypted swap as a backup.

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

    # Install tmux plugin manager
    git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

    Copy the custom tmux configuration:
    cp custom.tmux.conf ~/.tmux.conf
    tmux source-file ~/.tmux.conf

    # Start a tmux session:
    tmux

    # Press control-a shift-I to load plugins

   
    > You must remember to open a tty and vlock the session before
    > logout/login on gnome. This is because apparently the encrypted
    > filesystem is unmounted for a full logout, then that kills all
    > processes, period. All tmux sessions included. If you want the goodness
    > of gnome session reset without loosing your tmux sessions, you must
    > remember to do this.
 

Gnome Configuration (3.204):

    Install and run gnome-tweak-tool

    In workspaces, change workspace creation to static, create 7 workspaces.
    Top Bar show date, show seconds
    Extensions, Launch new instance to On
    Extensions, Alternatetab to On
    Appearance, global dark theme to On
    
    dnf install wmctrl

    Keyboard shortcuts, set Switch to workspace 1-4 to Alt-[1234]
    Add new shortcuts for workspaces 5,6,7 with the custom command type:
    wmctrl -s (workspace number-1)

    Use Vertex theme for gnome here (install from source):
        https://github.com/horst3180/vertex-theme

    Open gnome-tweak-tool select GTK+ theme vertex-dark

    Turn off all search options (no shop, no docs, etc.)

    Set to lock after 1 minute

    Change gnome-terminal settings:
        green on black colors -> Palettes -> Built in schemes: Xterm 
        No scrollbars shown
        Change profile name to green
        Turn off show menubar by default
        

Miscellaneous configuration:

    cd ~/projects/dotfiles
    cp .bashrc ~/
    
    git config --global core.editor "vim"
    git config --global credential.helper "cache --timeout=360000"

    systemctl enable sshd
    systemctl start sshd

    dnf -y install gimp inkscape graphviz w3m nmap thunar ImageMagick
    dnf -y install surfraw

    Copy .gnupg from backup to ~/
    scp -r (backup-system) ~/.gnupg .

    cp .surfraw.conf ~/
    
    # Start w3m, change color of anchor to yellow

    # Add autossh configuration to any remote systems on network
    # availability with the instructions in the file: autossh.service

SSH Configuration:

    To connect with other systems from this new system:
    ssh-keygen 
    (accept defaults)
    cat ~/.ssh/id_rsa.pub | \
        ssh (other system) "cat >> ~/.ssh/authorized_keys"

    chmod 0700 ~/.ssh
    chmod 0600 ~/.ssh/{authorized_keys,id_rsa}

    ssh (other system) # verify passwordless connectivity

    


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
    MAIL_DEST="username@domain.com"  (change this to the correct email!)
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


### Sound specific configurations
    
    See the notes in sound_control/README.md for details on how to
    configure a Bose QuietControl 30 headset with bluetooth, and for using
    cmus.

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
    
    Firefox 57 (Quantum) on Fedora:
        about:config -> dom.webnotifications.enabled set to false
        about:config -> geo.enabled set to false

        Install Firefox Extensions:
        uBlock Origin
        LeechBlock NG
        ForceFull 
        Open in Browser
        Surfingkeys
        After surfing keys is installed:
            cp .surfingkeys.js ~

        You may have to edit the surfing keys extension advanced
        settings and point it to the .surfingkeys.js file. This is solely to get
        the benefit of turning emoji completion off with iunmap(":")

        Under about:config
            set browser.fullscreen.autohide to False
            set geo.enabled to false
            set dom.webnotifications.enabled to false
        
        Preferences -> General -> "Show windows and tabs from last time"
        
        Customize -> Themes button on bottom -> Dark

    Google Chrome:
        Install google crhome from the google repo:
	    https://www.if-not-true-then-false.com/2010/install-\
		    google-chrome-with-yum-on-fedora-red-hat-rhel/

        Sign in to chrome to get the settings below:
        Set chrome to "remember where you left off"
        Install ublock origin for chrome
        

### Task warrior configuration

    # This configuration assumes that after task integration is
    # verified, you will import the tasks from other machines into the
    # auto backup folder

    dnf install task
    mkdir /home/nharrington/Documents/auto_backup/task_warrior
    ln -s /home/nharrington/Documents/auto_backup/task_warrior ~/.task
    task 

    (accept defaults)

### Watson time tracker configuration
    
    # Like task warrior above, this configuration assumes that you will
    # restore the contents of the watson folder from a backup

    mkdir /home/nharrington/Documents/auto_backup/watson
    ln -s /home/nharrington/Documents/auto_backup/watson ~/.config/watson

    # conda3, python3
    conda create --name watson
    source activate watson
    pip install td-watson


### Vim configuration

    # Use vim awesome from: https://github.com/amix/vimrc
    git clone --depth=1 https://github.com/amix/vimrc.git ~/.vim_runtime
    sh ~/.vim_runtime/install_awesome_vimrc.sh

    Then copy the custom config:
    cp nharrington_vim_config ~/.vim_runtime/my_configs.vim

    # Install the flake8 package at the fedora system level
    dnf install pyflakes

### Windows VM in VirtualBox

Instructions for creating a bare-bones vm that can be used for cloning
purposes. Based on what I could find online, any windows 10 installation
can be used for free for 90 days without licensing issues. After 90
days, you must completely destroy the instance. Use these instructions
every 90 days to create a new windows virtual machine snapshot to then
use for different dev builds.


Install VirtualBox 5.2.6

Create a virtualbox session with 2TB disk, 4GB RAM and the iso image:

Win10_1709_English_x64.iso 2017-10-01 4,587,268KB

Accept defaults until it gets to operating system selection, choose:
Windows 10 Home

Choose customer install
Accept defaults

At Sign in with microsoft -> Offline Account -> No

Name: Win10 Development
password: "password"
password hint: the password

Make Cortana Personal Assistant -> No
Set all privacy invasions to "Off"

After system boots for the first time:

Open services, Right cick windows update, set to disabled
Stop windows update service.

Privacy: Turn off everything. Literally, all access to anything under
privacy settings should be set to off.

Go through apps & features, remove anything that looks like bloatware
   This should be nothing - as it's a pure windows install

Reboot

Disable cortana on taskbar
Install chrome
Install ublock origin

Install classic shell from classicshell.net
Reboot

Install virtualbox extension pack on Host OS
Shutdown VM

On the host system
VBoxManage setextradata "VM-Name" CustomVideoMode1 1920x1080x32

Reboot virtual machine, set desktop resolution to 1920x1080

Reboot
Shutdown system

1. Create a snapshot
2. Clone the system
Create a full clone, name it: XGUT_Windows10_development

Further clones will all be linked back to this primary clone. Which in
turn is a full clone of the windows 10 install.

Export this virtual machine.  This is the 'base' on which to make
further interations. Don't ever boot this snapshot again, always make a
clone of it or re-import the exported virtual machine.

