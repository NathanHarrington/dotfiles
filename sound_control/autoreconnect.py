''' Auto rerun the shell script to use bluetooth control to reconnect
the bluetooth headphones every 5 seconds. This is a supremely ugly hack,
but it does auto-reconnect your headphones by pure brute force.

run with:

mkfifo /tmp/sound_status

in a separate window, run:
watch 'pipenv run python -u write_status.py'

sudo pipenv run python -u ./autoreconnect.py
'''

import os, time, sys
from subprocess import PIPE, Popen as popen


while True:
    status = ''
    with open('/tmp/sound_status') as input_file:
        for line in input_file.readline():
            status += line

    print('output decode: %s' % status)
    if '04_52_C7_1B_D7_F7' not in status:
        print('Reconnect')
        conn_out = popen(['bash', 'auto_bluetooth.sh'], stdout=PIPE).communicate()[0]
        print('conn: %s' % conn_out)
    

    time.sleep(0.3)

