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

Based on stock Fedora Core 41 workstation i3 live install.

The procedure below expects the entire drive to be dedicated to the
fedora install, with the 'auto' partitioning setup.

On i3-live system boot to the desktop:
Accept the default i3 config setup. 
Connect to the wifi.
Start the graphical install by running: liveinst.
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
dnf -y install bat exa ripgrep shutter xss-lock

start parcellite,
Activate the parcellite config interface by pressing ctrl+alt+p
In parcellite config: 
    check "Use Copy" and "Use Primary", then click synchronize clipboards

Clone this dotfiles repository
git clone https://github.com/NathanHarrington/dotfiles ~/projects/dotfiles

hostnamectl set-hostname "short computer hostname, like u430"
reboot 


### Launcher setup

dnf install libtool gtk2-devel xosd
Clone from: https://github.com/wdlkmpx/gmrun
./configure && sudo make install
cp ~/projects/dotfiles/.gmrunrc ~/.gmrunrc

# Copy startup configurations configurations
cp -ra ~/projects/dotfiles/autostart ~/.config/
cp -ra ~/projects/dotfiles/i3/config ~/.config/i3/config

## Install pyenv for managing python versions:
dnf install zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel xz xz-devel libffi-devel findutils
curl https://pyenv.run | bash
# Ignore the install in bash steps here, you'll do it below in the .bashrc copy

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
            Install vimium for chrome

VS Code: 
    Install ms code from ms's page. 


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
AuthPass=(app password created from google)

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
# As of fc41, the fc31 branch is still functional.
git checkout fc31_build
Install pre-requisities, make.
mkdir ~/.config/keynav/
cp ~/projects/dotfiles/keynavrc ~/.config/keynav/
# reboot to get keynav crosshairs to appear 

### Pulse mixer
cd projects/
git clone https://github.com/GeorgeFilipkin/pulsemixer
(no further install necessary)

### Open office install 
sudo dnf -y install libreoffice
Start oocalc, close all popups. 
Turn off sidebar, status bar, menu bar, turn off formatting bar, standard bar.

### VSCode configuration 
The goal here is a from-scratch minimal configuration. Keep as many 
of the defaults from vs code as possible, just change what you must. 
Write the steps here so you memorize the concepts, not a brittle 
settings.json move process. 
Start VS Code. 
Install hacker dark pro theme, Dark Green theme.
Install python extension. 
Ctrl + , for settings 
    Menubar, set to none 
    Status bar workbench, uncheck.
    Activity bar location -> hidden.
    Editor -> Line Numbers -> Off
    Editor -> Word wrap -> on
    Editor auto save.
Open a bash command, right click the menu bar set the panel to the right. 
Right click in the command tab area, hide the tabs. 
Open a file for text editing, right click the tab bar, select Hide.
Right click the minimap, uncheck to hide.

# Add custom settings to settings.json 
    "editor.glyphMargin": false, 
    "editor.folding": false,

# Add custom vs code keybings to keybindings.json: 
# Copy this text and paste into ~/.config/Code/User/keybindings.json
# Note that if you are still using Cursor, you'll need to disable these as they 
# prevent the default ctrl+k from working correctly.
// Place your key bindings in this file to override the defaultsauto[]
[
    {
        "key": "ctrl+k t",
        "command": "editor.action.insertSnippet",
        "when": "editorTextFocus",
        "args": {
            "snippet": "$CURRENT_YEAR-$CURRENT_MONTH-$CURRENT_DATE $CURRENT_HOUR:$CURRENT_MINUTE "
        }
    },
    {
            "key": "ctrl+up",
            "command": "editorScroll",
            "when": "editorTextFocus",
            "args":
            {
                   "to": "up",
                    "by": "wrappedLine",
                    "revealCursor": true
           }
    },
    {
            "key": "ctrl+down",
            "command": "editorScroll",
            "when": "editorTextFocus",
            "args":
            {
                    "to": "down",
                    "by": "wrappedLine",
                    "revealCursor": true
            }
    },
    {
        "key": "ctrl+q",
        "command": "-workbench.action.quit"
    },
    // A tweak to this is to make it focus the last active editor instead of 
    // the terminal which may be better if you find you don’t hide the terminal very often:
    { "key": "ctrl+`", "command": "workbench.action.terminal.focus",
                            "when": "!terminalFocus" },
    { "key": "ctrl+`", "command": "workbench.action.focusActiveEditorGroup",
                            "when": "terminalFocus" },
    
    {
        "terminal.integrated.commandsToSkipShell": [
            "workbench.action.quickOpen",
        ]
    }                           
]

### Cursor code editor specific configuration
Theme: Hacker Dark Pro 
Turn off all the status bars, menu bars, etc. 
To get nearly full screen with no useless bars:
   have i3 in Tabbed mode
   Press F11 in cursor. 
   Press ctrl+alt+p to get cursor console. 
   Select 'hide custom title bar in full screen'
   Press $mod+f to get out of full screen in i3, while the cursor window still thinks it's in full screen.


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

Clone and install the i3lock-svg package and follow the instructions in the readme:
https://github.com/NathanHarrington/i3lock-svg

