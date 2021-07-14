# Automatically connect to the toyota camry audio device.

#sudo systemctl restart bluetooth
# Create an input stream for the bluetoothctrl command
mkfifo /tmp/srv-input 
tail -f /tmp/srv-input | bluetoothctl &

#echo  "disconnect E8:07:BF:DC:99:72" > /tmp/srv-input
#sleep 3
#echo  "power off" > /tmp/srv-input
#sleep 3
#echo  "power on" > /tmp/srv-input
#sleep 3
echo  "connect E8:07:BF:DC:99:72" > /tmp/srv-input
sleep 1

echo "set default sink"
pactl set-default-sink bluez_sink.E8_07_BF_DC_99_72

sleep 1
pkill bluetoothctl
