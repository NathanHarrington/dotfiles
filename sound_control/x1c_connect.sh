# Automatically connect to the soundcontrol u2 

# Create an input stream for the bluetoothctrl command
mkfifo /tmp/srv-input 
tail -f /tmp/srv-input | bluetoothctl &

echo  "connect E8:07:BF:DC:99:72" > /tmp/srv-input
sleep 1

echo "set default sink"
pactl set-default-sink bluez_sink.E8_07_BF_DC_99_72

sleep 1
pkill bluetoothctl
