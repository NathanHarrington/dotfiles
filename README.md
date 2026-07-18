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

Based on stock Fedora Core 43 workstation i3 live install.

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
dnf -y install git autossh tmux alacritty patch unzip
dnf -y install redhat-rpm-config python-devel
dnf -y install parcellite vim vim-X11 ncdu sox 
dnf -y install bat ripgrep shutter xss-lock trash-cli

# Install eza: 
sudo dnf install cargo
cargo install eza

# Install the ibm plex mono fonts  - also available in .fonts
dnf install ibm-plex-mono-fonts

# Install Symbols Nerd Font as fallback for Starship prompt icons.
mkdir -p ~/.local/share/fonts/NerdFonts/SymbolsOnly ~/.config/fontconfig/conf.d
curl -fL -o /tmp/NerdFontsSymbolsOnly.zip https://github.com/ryanoasis/nerd-fonts/releases/latest/download/NerdFontsSymbolsOnly.zip
unzip -o /tmp/NerdFontsSymbolsOnly.zip -d ~/.local/share/fonts/NerdFonts/SymbolsOnly
cp ~/.local/share/fonts/NerdFonts/SymbolsOnly/10-nerd-font-symbols.conf ~/.config/fontconfig/conf.d/
fc-cache -fv ~/.local/share/fonts
# Restart alacritty after changing fonts.

# start parcellite,
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

### Alacritty configuration
mkdir -p ~/.config/alacritty
cp ~/projects/dotfiles/alacritty.toml ~/.config/alacritty/alacritty.toml

## Install pyenv for managing python versions:
dnf install zlib-devel bzip2 bzip2-devel readline-devel 
dnf install sqlite sqlite-devel xz xz-devel libffi-devel findutils
curl https://pyenv.run | bash
# Ignore the install in bash steps here, you'll do it below in the .bashrc copy

# Make sure to install pipenv with pip, not with dnf 
# as main user: 
pip install pipenv

# Install starship from the guide:
dnf copr enable atim/starship 
dnf install starship

### Miscellaneous configuration:
cd ~/projects/dotfiles
cp starship.toml ~/.config/starship.toml
# On hotel-compute, use the host-specific prompt instead:
# cp hotel-compute_starship.toml ~/.config/starship.toml
cp .bashrc ~/.bashrc
cp .vimrc ~/.vimrc
cp .tmux.conf ~/.tmux.conf

git config --global core.editor "vim"
git config --global credential.helper "cache --timeout=360000"

systemctl enable sshd
systemctl start sshd

dnf -y install gimp inkscape graphviz w3m nmap thunar ImageMagick
dnf -y install gwenview feh
dnf -y install tig darktable xclip urlview

# Start w3m, change color of anchor to yellow

Start firefox, create new profiles with the following fundamentals:
    1. Open previous windows and tabs.
    2. Turn off: Use AI to suggest tags 
                 Recommend extensions as you browse 
                 Recommend features as you browse
                 Enable link previews
    3. Home -> New windows and tabs all start blank page. 
               Uncheck all firefox home content. 
    4. Search -> Uncheck show search terms in the address bar
                 Uncheck show trending search suggetssions
                 Uncheck show search suggestions ahead
                 Uncheck show trending
                 Under firefox suggest, uncheck suggest search engines, quick actions, suggestions from firefox
    5. Privacy and security 
          Uncheck send technical data, usage ping
          Check 'tell websites not to...'
    6. Settings, search 'location', check 'block websites from asking'
    Install ublock origin, vimium

Google Chrome for compatibility with various meeting tools:
    Install google chrome from google's page.
    Sign in to chrome to get the settings below, or start a new profile 
	with the fundamentals:
            Set chrome to "remember where you left off"
            Install vimium for chrome
            Don't use chrome for anything on the web as it will be overwhelmed with ads.


### Move over previous system files. 
With the previous years m.2 ssd, plug it into the adapter, start thunar, 
click the drive and enter the passphrase.

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
Base terminal for i3wm is xfce, leave that untouched. 
Use alacritty already configured above.

### Keynav configuration
Clone the repository: https://github.com/NathanHarrington/keynav
# As of fc41, the fc31 branch is still functional.
git checkout fc31_build
Install pre-requisities, make.
mkdir ~/.config/keynav/
cp ~/projects/dotfiles/keynavrc ~/.config/keynav/
# reboot to get keynav crosshairs to appear 

### Open office install 
dnf -y install libreoffice
Start oocalc, close all popups. 
Turn off sidebar, status bar, menu bar, turn off formatting bar, standard bar.

### Early LUKS Remote Unlock

Pre-requisites: known working wifi connections on all networks you want to work with. Generally speaking you want to bring this machine to the different networks, connect them to wifi at home, work and with the hotspot. Use the machine for normal activities for a week or so before doing the following to make sure there are no gotchas with the network configs. Add a calendar reminder a week out to then do this process:

1. Install the initramfs pieces:
   sudo dnf install dracut-sshd dracut-network NetworkManager-wifi wpa_supplicant

2. Add the SSH public key allowed for early unlock:
   sudo install -d -m 700 /etc/dracut-sshd
   sudoedit /etc/dracut-sshd/authorized_keys
   # Paste in the desired public key here

3. Create initramfs-only NetworkManager Wi-Fi profiles by cloning existing system profiles, run both commands separate, one for each existing ssid profile you want to use. For example MyHomeNework initrd-myhomenetwork, then two more commands for AtWorkNetowrk initrd-atworknetwork
   sudo nmcli connection clone "ExistingSSIDProfile" initrd-home
   sudo nmcli connection modify initrd-home connection.autoconnect yes connection.permissions '' connection.interface-name '' wifi.cloned-mac-address permanent
   sudo restorecon -Rv /etc/NetworkManager/system-connections
   sudo nmcli connection reload

   If retrying this step, delete old initrd-* connections by UUID first. Duplicate connection names make nmcli ambiguous, and stale files can keep the wrong SELinux context.

4. Add a small dracut module that starts wpa_supplicant before nm-initrd.service, then include it from:
   /etc/dracut.conf.d/91-early-ssh-wifi.conf

   Install the custom dracut module and generate the dracut config with the current Wi-Fi driver modules and all initrd-only NetworkManager profiles:
   cd ~/projects/dotfiles
   sudo scripts/install-early-luks-wifi-dracut.sh
   cat /etc/dracut.conf.d/91-early-ssh-wifi.conf

5. Enable early networking and rebuild initramfs:
   sudo grubby --update-kernel=ALL --args="rd.neednet=1 cfg80211.ieee80211_regdom=US"
   sudo dracut -f --regenerate-all

6. Reboot, wait for Wi-Fi/DHCP, then unlock:
   ssh -i <private-key> root@<early-boot-lan-ip>
   systemd-tty-ask-password-agent

Notes:
- This does not work over Tailscale until after root is unlocked.
- The Wi-Fi PSKs and early SSH material are embedded in /boot/initramfs-*.
- Early boot may get a different DHCP lease than the fully booted system.
- Multiple initrd-* profiles are tried in filename order; unavailable networks can add about 25-30 seconds each before an available profile connects.

### ThinkPad X1 Carbon unattended power-outage recovery

Goal: leave the laptop plugged in with the battery installed. If utility power
fails, the machine runs on battery, locks/blanks after 5 minutes, hibernates
after 10 minutes, then boots again when AC power returns. Because the disk is
LUKS encrypted, it will stop at early remote unlock; unlock from another
machine on the LAN, then the hibernated system image resumes and normal
services such as Tailscale come back.

1. Enable firmware boot on AC attach.

   Reboot into the ThinkPad BIOS/UEFI setup and enable the power option named
   something like "Power On with AC Attach", "Wake on AC", or "AC Power
   Recovery".

   Test it before continuing:

   sudo poweroff

   After the machine powers off, unplug AC, wait a few seconds, then plug AC
   back in. The laptop should boot without pressing the power button.

2. Configure early LUKS remote unlock.

   Complete the "Early LUKS Remote Unlock" section above first. This is what
   makes the machine reachable on the LAN before the root filesystem is
   unlocked. Tailscale is not available until after LUKS unlock and resume.

3. Add disk-backed swap for hibernate.

   Fedora's default zram swap cannot be used for hibernate. On the encrypted
   Btrfs root filesystem, create a real swapfile:

   sudo btrfs filesystem mkswapfile --size 24g /swapfile
   sudo swapon /swapfile
   echo '/swapfile none swap defaults,pri=10 0 0' | sudo tee -a /etc/fstab

   The 24g size is intentionally larger than the 16g RAM in the X1 Carbon
   setup. Adjust upward if the machine has more RAM.

4. Teach the kernel and initramfs where to resume from.

   ROOTDEV="$(findmnt -no SOURCE / | sed 's/\[.*\]//')"
   RESUME_UUID="$(sudo blkid -s UUID -o value "$ROOTDEV")"
   RESUME_OFFSET="$(sudo btrfs inspect-internal map-swapfile -r /swapfile)"

   sudo grubby --update-kernel=ALL --args="resume=UUID=$RESUME_UUID resume_offset=$RESUME_OFFSET"
   echo 'add_dracutmodules+=" resume "' | sudo tee /etc/dracut.conf.d/resume.conf
   sudo dracut -f --regenerate-all
   sudo reboot

5. Verify manual hibernate.

   After reboot:

   swapon --show
   sudo systemctl hibernate

   The machine should power down. Press the power button or attach AC power,
   unlock LUKS through early SSH, and confirm the previous session resumes.

6. Make lid close hibernate instead of suspend.

   If the desired behavior is "closing the lid always hibernates", configure
   systemd-logind:

   sudo mkdir -p /etc/systemd/logind.conf.d
   printf '%s\n' '[Login]' 'HandleLidSwitch=hibernate' 'HandleLidSwitchExternalPower=hibernate' 'HandleLidSwitchDocked=hibernate' | sudo tee /etc/systemd/logind.conf.d/hibernate-on-lid.conf >/dev/null
   sudo systemctl reload systemd-logind.service

   For headless outage-recovery use, leaving the lid open is simplest. If the
   machine must stay online with the lid closed while AC is connected, use
   HandleLidSwitchExternalPower=ignore instead.

7. Install the i3 idle helper from this repository.

   Copy the i3 config as described earlier:

   cp -ra ~/projects/dotfiles/i3/config ~/.config/i3/config

   The config starts:

   ~/projects/dotfiles/scripts/suspend-on-battery-idle.sh

   The helper defaults to:
   - on battery only
   - screen off / lock after 5 minutes
   - hibernate after 10 minutes
   - skip hibernate while fullscreen or while audio is playing

   To verify what it will do:

   ~/projects/dotfiles/scripts/suspend-on-battery-idle.sh --settings
   ~/projects/dotfiles/scripts/list-power-settings.sh

8. Full outage dry-run.

   Leave the laptop plugged in, then pull AC power. Wait for the helper to
   hibernate after 10 minutes. Restore AC power. The BIOS should boot the
   laptop, early LUKS remote unlock should come up on the LAN, and after
   unlocking the previous hibernated session should resume.
