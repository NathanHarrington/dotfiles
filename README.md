# dotfiles
Nathan Harrington environment configuration resources


### Run this every year at the end of December
<pre>
  There is no good time to do this, but when everyone else is on break
  is probably the best time. 

  Buy a new disk every year and replace it in the laptop. This will
  prevent manufactured developed bit rot. You'll also get a snapshot
  non-cloud backup of all your files at that moment.
</pre>

### System configuration instructions
<pre>
Based on stock Fedora Core 37 workstation MATE-compiz install.
  Why MATE? out of the box screen locking and suspend that is
  closest to regular Gnome. 

The procedure below expects the entire drive to be dedicated to the
fedora install, with the 'auto' partitioning setup.

On MATE-live system boot to the desktop:
Start the graphical install.
System -> Installation Destination
	Check the 'encrypt my data' box, set a passphrase.

Network -> set the hostname.

Create User -> set password, and check 'Make administrator'

Accept all defaults, after the install has complete, reboot the system.

Clone this dotfiles repository
git clone https://github.com/NathanHarrington/dotfiles ~/projects/dotfiles

hostnamectl set-hostname "short computer hostname, like u430"

    Install rpmfusion libraries (dnf install command for adding repos)

    dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
    dnf update -y
    (about 20 minutes later...)
    reboot

</pre>


<pre>
Edit startup applications, remove:
dnfdragora
Anything else that appears unecessary

Right click the workspace panel in the lower right, make sure there are 9 total workspaces.

Control Center -> Keyboard shortcuts, manually set:
run a terminal  Ctrl+Alt+T
Switch to workspace N  Alt-N  (for workspaces 1-9)
Tile N,S,W,E with windows key + up,down,left,right

Control Center -> Keyboard Preferences -> Layout -> Options
  Set CAPS LOCK as another control

# Basic development environment
dnf -y install make automake gcc gcc-c++ kernel-devel cmake
dnf -y install git autossh tmux
dnf -y install redhat-rpm-config python-devel
dnf -y install parcellite vim vim-X11 ncdu cmus sox rofi
dnf -y install bat ripgrep exa

start parcellite,
Activate the parcellite config interface by pressing ctrl+alt+p
In parcellite config: 
    check "Use Copy" and "Use Primary", then click synchronize clipboards

## Install pyenv for managing python versions:
dnf install zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel xz xz-devel libffi-devel findutils
curl https://pyenv.run | bash

</pre>


### Miscellaneous configuration:
<pre>
cd ~/projects/dotfiles
cat bashrc_custom >> ~/.bashrc

git config --global core.editor "vim"
git config --global credential.helper "cache --timeout=360000"

systemctl enable sshd
systemctl start sshd

dnf -y install gimp inkscape graphviz w3m nmap thunar ImageMagick
dnf -y install surfraw tig darktable

mkdir ~/.config/tig/
cp tig-colors-neonwolf-256.tigrc  ~/.config/tig/
echo "source ~/.config/tig/tig-colors-neonwolf-256.tigrc" \
    > ~/.config/tig/config

cp .surfraw.conf ~/
</pre>

# Start w3m, change color of anchor to yellow

### Firefox and Chrome configuration

Add streaming video support:
dnf -y install gstreamer1-libav gstreamer1-plugins-ugly unrar compat-ffmpeg4 ffmpeg-libs

Google Chrome:
    Install google chrome from google's page.
    Sign in to chrome to get the settings below, or start a new profile 
	with the fundamentals:
            Set chrome to "remember where you left off"
            Install ublock origin for chrome
            Install surfingkeys for chrome


### tmux configuration:

dnf -y install xclip urlview

Setup tmux with the instructions from http://tony.github.io/tmux-config/:

cd ~
tmux 
( Ignore configuration error )
( press control + a then d to exit)
tmux source-file ~/.tmux.conf
( Ignore configuration error )


# Install tmux plugin manager
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

Copy the custom tmux configuration:
cd ~/projects/dotfiles
cp custom.tmux.conf ~/.tmux.conf
tmux source-file ~/.tmux.conf

Start a tmux session:
tmux

Press control-a shift-I to load plugins

### Launcher setup

 dnf install libtool gtk2-devel
 Clone from: https://github.com/wdlkmpx/gmrun

 ./configure && sudo make install
 
 Create mate keyboard shortcut for Alt+F3 with:
    gmrun
  cp dotfiles/.gmrunrc ~/.gmrunrc

### Move over previous system files. 

More recent versions of fedora allow you to connect the disk and it will
ask for a passphrase and mount your old encrypted home directory
automatically. If that doesn't work or you need access to the root
partition, try the process at the end of this file.

Copy the auto_backup folder from the old system:
cp -ra old_system_mount_location/home/nharrington/Documents/auto_backup ~/Documents/auto_backup

Important! - after you run the command above, disconnect the external
original drive. This is because it has the links below which will point
to your current /home/directory. If you leave the disk plugged in you
will also be editing the backup files apparently.

Make links from the encrypted folder location to the ~ location:
cd ~
ln -s ~/Documents/auto_backup/home.config_files/.ssh
ln -s ~/Documents/auto_backup/home.config_files/.gnupg

cd ~/.config/
ln -s ~/Documents/auto_backup/home.config_files/cmus
(You may have to re-add all the mp3s to the playlist)

cd ~/.config/
mkdir rclone
cd rclone
ln -s ~/Documents/auto_backup/home.config_files/rclone.conf

### Setup the rclone backup option:

Download and install rclone according to: http://rclone.org/install/

Verify rclone config is setup by running: rclone config and looking at the remotes.

After the .gnupg directory copy as described above, and with a fully verified key
management and recovery system:

Anything you put in the folder below will be auto-backed up to the
cloud, with encryption from the ~/Documents/auto_backup/ folder. Make sure you create the working encrypted foloder:
mkdir ~/Documents/working_encrypted/

Add the following to crontab -e:

# Nightly tar backup build and upload
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

Update the ssmtp.conf file as shown below, where domain is a
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

Now that the backup script is in place and the email is in place,
temporarily change the crontab times to verify everything backs up
correctly.

### Chrome profile setups:
google-chrome --profile-directory=Default
google-chrome --profile-directory=custom_profile_name

If you keep getting login popup/keyring type isues after a few reboots,
the workaround is to move the keyring popup exec (rename it to
back.keyring), and run chrome with:
google-chrome --password-store=basic --profile-directory=Default

       
### Mate Terminal configuration

Set colorscheme green on black.
Turn off scrollbar.
Turn off show menubar by default.
Palette - choose xterm.

### Vim configuration
   
Install SpaceVim!
Start vim, wait, choose 2 dark powered mode.
Exit vim, restart vim. Wait for PluginManager to complete.
Follow the configuration instructions in: spacevimrc

### Keynav configuration

Clone the repository: https://github.com/NathanHarrington/keynav
git checkout fc31_build
Install pre-requisities, make.
mkdir ~/.config/keynav/
cp ~/projects/dotfiles/keynavrc ~/.config/keynav
cp ~/projects/dotfiles/keynav.desktop ~/.config/autostart/

### Pulse mixer

cd projects/
git clone https://github.com/GeorgeFilipkin/pulsemixer
(no further install necessary)

### MATE Config

Right click the top menu bar, add 'select workspace switcher' panel.
Right click bottom panel, select delete panel, confirm.
Right click panel, set to bottom, height 20.
Right click panel, add compact menu.
Right click panel, add window list using buttons.
Remove 'System, Application, etc' panel applet.
Remove the individual files, firefox etc. icons. 
Right click and move different panel items
Right click background, choose that first option that looks like a
picture but is a gradient, set to solid black color.

Remove everything but folders from desktop:
dconf-editor
Click  org -> mate -> caja -> desktop 
Un-check all trash, volumes icons, etc. on desktop.
Appearance -> BlackMATE
As root, replace the lock screen bitmap with your desired image in:
/usr/share/backgrounds/default.png
      
</pre>

### Auto-keyboard configurations

  See the notes in autokeyboard/*.sh
  for details on commonly used keyboard automation scripts and how
  they should be bound in MATE.

### Sound specific configurations
    
See the notes in sound_control/README.md for details on how to
configure a Bose QuietControl 30 headset with bluetooth, and for using
cmus.

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


