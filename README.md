# dotfiles
Nathan Harrington environment configuration resources


<pre>
### Run this every year at the end of December
  There is no good time to do this, but when everyone else is on break
  is probably the best time. 

  Buy a new disk every year and replace it in the laptop. This will
  prevent manufacturer developed bit rot. You'll also get a snapshot
  non-cloud backup of all your files at that moment.

### System configuration instructions

Based on stock Fedora Core 39 workstation i3 live install.

The procedure below expects the entire drive to be dedicated to the
fedora install, with the 'auto' partitioning setup.

On i3-live system boot to the desktop:
Start the graphical install.
System -> Installation Destination
	Check the 'encrypt my data' box, set a passphrase.

Add a root user -> set password. 

Create User -> set password, and check 'Make administrator'

Accept all defaults, after the install has complete, reboot the system.

    Install rpmfusion libraries (dnf install command for adding repos)

    dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
    dnf update -y
    (about 20 minutes later...)
    reboot

# Basic development environment
dnf -y install make automake gcc gcc-c++ kernel-devel cmake
dnf -y install git autossh tmux
dnf -y install redhat-rpm-config python-devel
dnf -y install parcellite vim vim-X11 ncdu cmus sox rofi
dnf -y install bat ripgrep shutter

start parcellite,
Activate the parcellite config interface by pressing ctrl+alt+p
In parcellite config: 
    check "Use Copy" and "Use Primary", then click synchronize clipboards

Clone this dotfiles repository
git clone https://github.com/NathanHarrington/dotfiles ~/projects/dotfiles

hostnamectl set-hostname "short computer hostname, like u430"
reboot 


### Launcher setup

 dnf install libtool gtk2-devel
 Clone from: https://github.com/wdlkmpx/gmrun

 ./configure && sudo make install
 
 Create mate keyboard shortcut for Alt+F3 with:
  cp ~/projects/dotfiles/.gmrunrc ~/.gmrunrc


# Copy startup configurations configurations
cp -ra ~/projects/dotfiles/autostart ~/.config/
cp -ra ~/projects/dotfiles/i3/config ~/.config/i3/config

## Install pyenv for managing python versions:
dnf install zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel xz xz-devel libffi-devel findutils
curl https://pyenv.run | bash

# Make sure to install pipenv with pip, not with dnf 
# as main user: 
pip install pipenv


### Miscellaneous configuration:
cd ~/projects/dotfiles
cat bashrc_custom >> ~/.bashrc

git config --global core.editor "vim"
git config --global credential.helper "cache --timeout=360000"

systemctl enable sshd
systemctl start sshd

dnf -y install gimp inkscape graphviz w3m nmap thunar ImageMagick
dnf -y install tig darktable xclip urlview

# Start w3m, change color of anchor to yellow

Google Chrome:
    Install google chrome from google's page.
    Sign in to chrome to get the settings below, or start a new profile 
	with the fundamentals:
            Set chrome to "remember where you left off"
            Install ublock origin for chrome
            Install surfingkeys for chrome


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

Anything you put in the folder below will be auto-backed up to the cloud, with
encryption from the ~/Documents/auto_backup/ folder. Make sure you create the
working encrypted foloder:
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

Update the ssmtp.conf file as shown below, where domain is a "google apps for
business" hosted domain, such as mybusiness.com or just plain ol gmail.com

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
google-chrome --profile-directory=custom_profile_name@gmail.com
google-chrome --profile-directory=business.user1@company.com
google-chrome --profile-directory=business.user2@another_company.com

If you keep getting login popup/keyring type isues after a few reboots,
the workaround is to move the keyring popup exec (rename it to
back.keyring), and run chrome with:
google-chrome --password-store=basic --profile-directory=Default

       
### Terminal configuration
Base terminal for i3wm is xfce. Edit -> Preferences
Scroll bar is dsiabled 
Scrollback is 999
Cursor block, blinks

Set colorscheme green on black.
Turn off scrollbar.
Turn off show menubar by default.
Palette - choose xterm.

Uncheck display new menubar, uncheck borders.
colors -> green on black

### Keynav configuration

Clone the repository: https://github.com/NathanHarrington/keynav
git checkout fc31_build
Install pre-requisities, make.
mkdir ~/.config/keynav/
cp ~/projects/dotfiles/keynavrc ~/.config/keynav/
# reboot to get keynav crosshairs to appear 

### Pulse mixer
cd projects/
git clone https://github.com/GeorgeFilipkin/pulsemixer
(no further install necessary)

### Auto-keyboard configurations

  See the notes in autokeyboard/*.sh
  for details on commonly used keyboard automation scripts and how
  they should be bound.

### Sound specific configurations
    
See the notes in sound_control/README.md for details on how to
configure a Bose QuietControl 30 headset with bluetooth, and for using
cmus.

### Cordince branding instructions 
Clone the CordinceMarketing repo
cp ~/projects/CordinceMarketing/backgrounds/Cordince_Organ_Engineering_Background_1920x1080.png /usr/share/backgrounds/

Edit the file 
/usr/share/pixmaps/system-logo-white.png to be just a blank overlay, no logo displayed, just a transparent image.

Create the file if it does not exist:
/etc/lightdm/slick-greeter.conf 

With the contents:
[Greeter]
background=/usr/share/backgrounds/Cordince_Organ_Engineering_Background_1920x1080.png

dnf -y install slick-greeter
test with: slick-greeter --test-mode 

Hide fedora logos on boot up with: 
plymouth-set-default-theme details -R

--------------------------------------------------------------
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


