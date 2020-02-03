# Automatically connect to the bluetooth headset, and set as the default
# sink.
#
#
# Most of this is vestigal as of FC31 on 2020-01-06. It was such a headache I'm
# leaving it in here in case it ever comes up again. For right now, bluetooth
# in MATE desktop works exactly as expected. Simply connect to it once, and
# every subsequent power on things just work the way you'd expect.
#
#
# Bose QuietControl 30 on Fedora Core 24
# In /etc/bluetooth/main.conf, make sure to set:
# ControllerMode = bredr
# Pair with blueman-manager or bluetoothctl manually first, then run
# this on every reboot
# Use the pulsemixer from: https://github.com/GeorgeFilipkin/pulsemixer
# to control sound levels on command line like alsamixer
#
# Trouble getting headset to operate the in a2dp_sink mode? Does it
# always go to 'phone mode', no matter how you connect it? Does it do
# the beep and reset then lost thing?  Here's how you fix that:
# connect the bose headset with blueman-manager
# run the script below, after it connects open gnome sound settings
# Change the sink from headset to a2dp sink
# (it will probably have already done the beep reset thing)
# Close the sound settings
# Power off the bose headset
# Wait 3 seconds
# Power on the bose headset

sudo systemctl restart bluetooth
# Create an input stream for the bluetoothctrl command
mkfifo /tmp/srv-input
tail -f /tmp/srv-input | bluetoothctl &

# u430 touch with in-ears
echo  "disconnect" > /tmp/srv-input
sleep 3
echo  "power off" > /tmp/srv-input
sleep 3
echo  "power on" > /tmp/srv-input
sleep 3
echo  "connect 04:52:C7:1B:D7:F7" > /tmp/srv-input
sleep 5
echo  "yes" > /tmp/srv-input
sleep 5

echo "set default sink"
pactl set-default-sink bluez_sink.04_52_C7_1B_D7_F7

sleep 5
pkill bluetoothctl
echo "Did you disable the XT1526 phone connection?"

# Zenbook with bose over-ears
#echo  "connect 04:52:C7:35:09:EF" > /tmp/srv-input
#pactl set-default-sink bluez_sink.04_52_C7_35_09_EF

