# dotfiles
environment configuration resources


# System configuration instructions
Based on Fedoara Core 24:

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

    Setup tmux with the instructions from:
    http://tony.github.io/tmux-config/
    (Make sure to run the pip and sudo commands from the powerline section in a terminal)
    
    Install tmux-resurrect with the manual instructions from:
    https://github.com/tmux-plugins/tmux-resurrect

Gnome Configuration (3.204):

    Install gnome-tweak-tool
    In workspaces, change workspace creation to static, create 7 workspaces.
    Top Bar show date, show seconds
    Extensions, Launch new instance to On
    Applications, global dark theme to On
    Extensions, Alternatetab to On
    
    Keyboard shortcuts, set Switch to workspace 1-4 to Alt-[1234]
    Add new shortcuts for workspaces 5,6,7 with the custom command type:
    wmctrl -s w(orkspace number-1)

    dnf install wmctrl

Miscellaneous configuration:

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


    Copy .gnupg from backup to ~/

    Install ublock origin for firefox
    Install disable ctrl-q exit plugin for firefox

    Sign in to chrome to get the settings below:
    Set chrome to "remember where you left off"
    Install ublock origin for chrome
    Install "fixed width text for gmail" extension for chrome


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

### Virtualbox configuration instructions
    
    Download virtualbox: http://download.virtualbox.org/virtualbox/5.0.22/VirtualBox-5.0-5.0.22_108108_fedora24-1.x86_64.rpm
    Download expansion pack: http://download.virtualbox.org/virtualbox/5.0.22/Oracle_VM_VirtualBox_Extension_Pack-5.0.22-108108.vbox-extpack
    
    After installing virtualbox, add the current user to the vboxusers group for usb access
    sudo usermod -a -G vboxusers nharrington
    

TODO:
store all of these settings in dotfiles repositories to make environment
    more portable

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

