Setup instructions for Bose QuietControl 30 on Fedora Core 24

Lenovo u430 Touch 20270

start a tmux window
in one window, execute command:
mkfifo /tmp/srv-input
watch 'echo  "connect 04:52:C7:1B:D7:F7" > /tmp/srv-input'
watch 'pactl set-default-sink bluez_sink.04_52_C7_1B_D7_F7'


In another window execute:
tail -f /tmp/srv-input

