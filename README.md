# dotfiles
Nathan Harrington environment configuration resources


### System configuration instructions
Based on stock Fedora Core 33 workstation MATE-compiz install.

    The procedure below expects the entire drive to be dedicated to the
    fedora install, with the 'auto' partitioning setup.


Add wifi network connection

Pretty sure this is a typo: you do want to encrypt home folder
Accept all defaults of installation process
   Do not select 'encrypt my home folder'

Reboot, at startup wizard, turn off privacy invasions.
Skip connecting online accounts.
Set username, password

Reboot

Clone this dotfiles repository
git clone https://github.com/NathanHarrington/dotfiles ~/projects/dotfiles

hostnamectl set-hostname "short computer hostname, like u430"

    Install rpmfusion libraries (dnf install command for adding repos)

    dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
    dnf update -y
    (about 20 minutes later...)
    reboot

If it says flatpak failed, run dnf update -y again

### MATE configuration (1.22.2)

<pre>
    dnf install @mate-desktop-environment
    # If you get a message like:
    #Error: 
    #Problem: problem with installed package fedora-release-workstation-31-2.noarch
    #- package fedora-release-workstation-31-2.noarch conflicts with system-release provided by fedora-release-matecompiz-31-1.noarch
    
    #Then run the command:
    dnf install @mate-desktop-environment --allow-erasing

    # Reboot, select mate for desktop environment on login

    # Why MATE? out of the box screen locking and suspend that is
    # closest to regular Gnome. Significantly faster performance in
    # other areas. Basically a usable gnome. Unfortunately it won't
    # handle plug and unplug of a monitor correctly. The work around
    # is to manually clone the displays before you unplug.

    # If you still need that fix, here's the instructions:
        # Remove screen tearing at the cost of a window compositor
        gsettings set org.mate.Marco.general compositing-manager false 

        dnf install disper
        # On Lenovo U430, map lcd/external monitor cycling to:
        # ctrl+alt+mod4+m (mod4=windows key)
        # Keyboard Shortcuts -> New Shortcut -> Name -> Cycle displays
        # Command:  disper --clone
        #
        # This will find a resolution that both monitors can do. Then unplug
        # the hdmi display, and do disper -s to select just the internal
        # display. If you get a black screen, the virtual console is still
        # available at alt+ctrl+f3. Run: 
        # export DISPLAY=:0; sleep 3; disper --clone
        # Then do ctrl-alt-f1 to get back to your black screen desktop and
        # it should mirror the display to a usable state again.
</pre> 

### After MATE setup has been verified, continue with the environment setup

    # Edit startup applications, remove:
    # clipit (use parcellite instead)
    # dnfdragora
    # Anything else that appears unecessary

    # Basic development environment
    dnf -y install make automake gcc gcc-c++ kernel-devel cmake
    dnf -y install git autossh tmux
    dnf -y install redhat-rpm-config python-devel
    dnf -y install parcellite vim ncdu cmus sox rofi
    
    start parcellite,
	Activate the parcellite config interface by pressing ctrl+alt+p
	If you can't see the preferences pop up, it may be because you are operating on wayland and not xorg.

	In parcellite config: 
        check "Use Copy" and "Use Primary", then click synchronize clipboards

    # Enable the timewaster blocks crontab entry as root:
    su -
    crontab -e
    59 * * * * /home/nharrington/projects/dotfiles/hosts_block.sh

    Follow the time-wasters.md file for more details on the leechblock and other network-level blocking.

    # MATE Keyboard shortcuts
    run a terminal  Ctrl+Alt+T
    Switch to workspace N  Alt-N

### tmux configuration:

    Install xclip to enable copying from the tmux scrollback buffer to
    the system clipboard:
    dnf install xclip urlview

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
    cd ~/projects/dotfiles
    cp custom.tmux.conf ~/.tmux.conf
    tmux source-file ~/.tmux.conf

    # Start a tmux session:
    tmux

    # Press control-a shift-I to load plugins
 
### Miscellaneous configuration:

    cd ~/projects/dotfiles
    cp .bashrc ~/
    
    git config --global core.editor "vim"
    git config --global credential.helper "cache --timeout=360000"

    systemctl enable sshd
    systemctl start sshd

    dnf -y install gimp inkscape graphviz w3m nmap thunar ImageMagick
    dnf -y install surfraw tig

    mkdir ~/.config/tig/
    cp tig-colors-neonwolf-256.tigrc  ~/.config/tig/
    echo "source ~/.config/tig/tig-colors-neonwolf-256.tigrc" \
        > ~/.config/tig/config

    # Copy .gnupg from backup to ~/
    # See notes below on 'recovering from backup' for details
    scp -r (backup-system) ~/.gnupg .

    cp .surfraw.conf ~/
    
    # Start w3m, change color of anchor to yellow

    # Install ghi from the curl setup, setup auth

### Firefox and Chrome configuration

    #Add streaming video support:
    #dnf install gstreamer1-libav gstreamer1-plugins-ugly unrar compat-ffmpeg28 ffmpeg-libs

    Google Chrome:
        Install google chrome from the google repo
        Sign in to chrome to get the settings below, or start a new profile 
	with the fundamentals:
            Set chrome to "remember where you left off"
            Install ublock origin for chrome
            Install surfingkeys for chrome

### Launcher setup

   gmrun does bash-style path completion and command history search out
   of the box.

   Clone from: https://github.com/rtyler/gmrun or one of the newer forks

   Run autogen.sh, then make, make install
   
   Create mate keyboard shortcut for Alt+F3 with:
      gmrun


### SSH Configuration:

    To connect with other systems from this new system:
    ssh-keygen 
    (accept defaults)
    cat ~/.ssh/id_rsa.pub | \
        ssh (other system) "cat >> ~/.ssh/authorized_keys"

    chmod 0700 ~/.ssh
    chmod 0600 ~/.ssh/{authorized_keys,id_rsa}

    ssh (other system) # verify passwordless connectivity

### Setup the rclone backup option:

    Download and install rclone according to: http://rclone.org/install/

    Create the references to the various cloud storage options with:

    rclone config, exit
    Copy .rclone.conf from backup system
    mkdir ~/.config/rclone/
    scp -r (backup-system):.rclone.conf .config/rclone/rclone.conf
    chown username.username .config/rclone/rclone.conf

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
    "google apps for business" hosted domain, such as mybusiness.com
     
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

    # Issue this command as root and primary userid
    echo "username@domain" > ~/.forward

    Test mail configuration:

    echo "Test mail to root" | mail -s "Test root essmtp" root
    echo "Test mail to local" | mail -s "Test local" nharrington
    echo "Test mail to gmail" | mail -s "Test gmail" username@domain


### Sound specific configurations
    
    See the notes in sound_control/README.md for details on how to
    configure a Bose QuietControl 30 headset with bluetooth, and for using
    cmus.

### Auto-keyboard configurations

    See the notes in autokeyboard/*.sh
    for details on commonly used keyboard automation scripts and how
    they should be bound in MATE.

### Install nomachine

    Download nomachine from: https://www.nomachine.com/download/linux&id=1 

    run:

    dnf install ./nomachine

    If you get a message about an selinux failure with systemd read from
    nxserver.service as describe here: https://www.nomachine.com/TR11N07360

    vi /etc/selinux/config

    change 'enforcing' to 'permissive'

    reinstall nomachine
        
### Vim configuration
   
    # Install SpaceVim!
    # Use configuration in: spacevimrc

### Task warrior configuration

    # This configuration assumes that after task warrior is used just for
    # calendar and calculator convenience, and is not actually used for task
    # recording.

    dnf install task
    task
    (accept defaults)

### Recovering from backup:

    Restoring from old system encrypted home folder:

    Plug in the old disk run:
    pvscan

    You should see something like the same volume group names listed below.
    ACTIVE /dev/fedora/home    <- this is the current operating system
    inactive /dev/fedora/home  <- this is your old disk

    Run:
    vgdisplay

    Get the VG UUID of the older disk

    Rename the volume group of the older disk:
    vgrename OLD_DISK_UUID  oldFedora

    Unplug the disk, replug.
    Mount by device name:

    mkdir /media/DISK/home
    mount /dev/oldFedora/home /media/DISK/home

    Now if you do:
    ls -la /media/DISK/home/nharrington
    You should see blinking red failures to show you need to load the encryption

    The simple mode for read only access should be the command below. Make sure to run this
    in a root shell session. It will not work with sudo!

    ecryptfs-recover-private /media/DISK/home/.ecryptfs/nharrington/.Private
    Recover directory: yes
    Do you know your login passphrase: yes
    Enter your fedora gnome login password

    Details here:
    https://askubuntu.com/questions/238047/how-do-i-mount-an-encrypted-home-directory-on-another-ubuntu-machine


