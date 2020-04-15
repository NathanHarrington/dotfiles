from subprocess import PIPE, Popen as popen

with open('/tmp/sound_status', 'w') as output_file:
    conn_out = popen(['pactl', 'info'], stdout=PIPE).communicate()[0]
    conn_out = conn_out.decode().replace('\n', '__')
    output_file.write(conn_out)

