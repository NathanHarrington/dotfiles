#!/usr/bin/env python
""" Control the volume of a specific pulse audio sink input from the
command line. This is designed to be used with an already running noise
generating application like:

$ play -c 2 -n synth brownnoise

The will create a running noise generator with the pulse audio property
of application.name set to "SoX". As the environment dictates,
independently control the noise level from the music level. Bind the
commands below to the respsective shortcut keys:

Name: Noise Level Up   Shortcut:  Ctrl+Shift+Alt+&
Command: noise_vol.py --command up

Name: Noise Level Down Shortcut:  Ctrl+Shift+Alt+^
Command: noise_vol.py --command down

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
        return parser

    def run(self, argv):
        """ Use the pulsectl library with patches to find channels by
            the specified name then change the volume. """

        self.args = self.parser.parse_args(argv)

        pulse = pulsectl.Pulse('my-client-name')

        vol = pulse.volume_get_all_chans_by_name(self.args.name)

        if self.args.command.upper() == "UP":
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
