# Automatically connect to the toyota camry audio device.

sudo systemctl restart bluetooth
# Create an input stream for the bluetoothctrl command
mkfifo /tmp/srv-input 
tail -f /tmp/srv-input | bluetoothctl &

echo  "disconnect" > /tmp/srv-input
sleep 3
echo  "power off" > /tmp/srv-input
sleep 3
echo  "power on" > /tmp/srv-input
sleep 3
echo  "connect 20:02:AF:78:9D:8B" > /tmp/srv-input
sleep 3

echo "set default sink"
pactl set-default-sink bluez_sink.20_02_AF_78_9D_8B

sleep 5
pkill bluetoothctl
