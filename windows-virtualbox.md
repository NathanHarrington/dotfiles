
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

