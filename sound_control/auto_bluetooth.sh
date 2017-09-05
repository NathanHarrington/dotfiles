# Automatically connect to the bluetooth headset, and set as the default
# sink.
# Bose QuietControl 30 on Fedora Core 24
# In /etc/bluetooth/main.conf, make sure to set:
# ControllerMode = bredr
# Pair with blueman-manager or bluetoothctl manually first, then run
# this on every reboot
# Use the pulsemixer from: https://github.com/GeorgeFilipkin/pulsemixer
# to control sound levels on command line like alsamixer

# Create an input stream for the bluetoothctrl command
mkfifo /tmp/srv-input 
tail -f /tmp/srv-input | bluetoothctl &

# Loop forever, attempt to connect every 2 seconds and set the sink
while [ true ]
do
# u430 touch with in-ears
#echo  "connect 04:52:C7:1B:D7:F7" > /tmp/srv-input
#pactl set-default-sink bluez_sink.04_52_C7_1B_D7_F7

# Zenbook with bose over-ears
echo  "connect 04:52:C7:35:09:EF" > /tmp/srv-input
pactl set-default-sink bluez_sink.04_52_C7_35_09_EF

sleep 2
done
