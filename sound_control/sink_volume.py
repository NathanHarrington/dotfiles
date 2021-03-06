#!/usr/bin/env python3
""" Control the volume of a specific pulse audio sink input from the
command line. This is designed to be used with an already running noise
generating application like:

$ play -c 2 -n synth brownnoise

The command above will create a running noise generator with the pulse
audio property of application.name set to "SoX". As your auditory
environment dictates, independently control the noise level from the
music level.  Bind the commands below to the respsective shortcut keys:

Name: Noise Level Up   Shortcut:  Ctrl+Shift+{
Command: <full_path>/sink_volume.py "--command up"

Name: Noise Level Down Shortcut:  Ctrl+Shift+}
Command: <full_path>/sink_volume.py "--command down"

If your music client is CMUS, try:

Name: Music level down shortcut Ctrl+shift+F12
Command: <full_path>/sink_volume.py "--name 'C* Music Player' --command down"

Name: Music level down shortcut Ctrl+shift+F11
Command: <full_path>/sink_volume.py "--name 'C* Music Player' --command up"

It is often easier to create an executable in /usr/bin with the full
python3 command and map that in gnome keyboard shortcuts like:

cat /usr/bin/music_down

python3 \
/home/nharrington/projects/dotfiles/sound_control/sink_volume.py \
--name 'C* Music Player' --command down


Requirements: https://github.com/mk-fg/python-pulse-control
with the get input sink by name patch.
"""

import sys
import argparse
import pulsectl

class VolumeApplication(object):
    """ Create the main application code.
    """
    def __init__(self):
        super(VolumeApplication, self).__init__()
        self.parser = self.create_parser()

    def create_parser(self):
        """ Create the parser with arguments specific to this
        application.
        """
        desc = "Noise volume control"
        parser = argparse.ArgumentParser(description=desc)

        cmd_str = "Specify a command [up|down|mute|unmute]"
        parser.add_argument("-c", "--command", type=str,
                            default="unmute", help=cmd_str)

        inc_str = "Specify an increment of volume change 0-1"
        parser.add_argument("-i", "--increment", type=float,
                            default=0.1, help=inc_str)

        nam_str = "Specify an audio sink application name"
        parser.add_argument("-n", "--name", type=str,
                            default="SoX", help=inc_str)

        nam_str = "Exact volume"
        parser.add_argument("-e", "--exact", type=float,
                            default=-1, help=inc_str)
        return parser

    def run(self, argv):
        """ Use the pulsectl library with patches to find channels by
            the specified name then change the volume. """

        self.args = self.parser.parse_args(argv)

        pulse = pulsectl.Pulse('my-client-name')

        vol = pulse.volume_get_all_chans_by_name(self.args.name)
        print('vol: %s' % vol)

        if self.args.exact > 1.0:
            print("\n SPECIFY FLOATING POINT OR YOUR EARS EXPLODE \n")
            sys.exit(1)

        if self.args.exact != -1:
            vol = self.args.exact

        elif self.args.command.upper() == "UP":
            vol += self.args.increment
        else:
            vol -= self.args.increment

        pulse.volume_set_all_chans_by_name(self.args.name, vol)


def main(argv=None):
    argv = argv[1:]

    exit_code = 0
    try:
        go_app = VolumeApplication()
        go_app.run(argv)

    except SystemExit as exc:
        exit_code = exc.code

    return exit_code

if __name__ == "__main__":
    sys.exit(main(sys.argv))
