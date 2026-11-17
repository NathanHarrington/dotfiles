"""Run with: python3 -m unittest discover -s tests -p test_wifi_saved_password_recovery.py -v"""

import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'wifi_saved_password_recovery.py'
spec = importlib.util.spec_from_file_location('wifi_saved_password_recovery', SCRIPT)
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)

PROFILE = '9561576c-0f9b-46f3-b78f-7c1ed0d90c76'


class NetworkManagerOutputTests(unittest.TestCase):
    def test_device_states_preserve_an_empty_connection_uuid(self):
        for state, profile in ((100, PROFILE), (60, PROFILE), (30, ''), (120, ''), (20, '')):
            with self.subTest(state=state):
                runner = mock.Mock()
                runner.run.side_effect = [
                    subprocess.CompletedProcess([], 0, stdout=f'wifi\n{state}\nyes\n{profile}\n'),
                    subprocess.CompletedProcess([], 0, stdout='enabled\n'),
                ]
                nm = recovery.NetworkManager(runner, 'wlo1')
                self.assertEqual(nm.snapshot(), {
                    'type': 'wifi', 'state': state, 'autoconnect': 'yes',
                    'uuid': profile or None, 'radio': 'enabled',
                })

    def test_profile_preserves_multiple_empty_trailing_fields(self):
        fields = ['802-11-wireless', '', 'yes', '', '100', 'Sugg Farm Public WiFi', '', '']
        runner = mock.Mock()
        runner.run.return_value = subprocess.CompletedProcess([], 0, stdout='\n'.join(fields) + '\n')
        nm = recovery.NetworkManager(runner, 'wlo1')
        self.assertEqual(nm.profile(PROFILE), dict(zip(recovery.PROFILE_FIELDS, fields)))

    def test_incomplete_device_output_still_fails(self):
        runner = mock.Mock()
        runner.run.return_value = subprocess.CompletedProcess([], 0, stdout='wifi\n30\n')
        nm = recovery.NetworkManager(runner, 'wlo1')
        with self.assertRaisesRegex(recovery.RecoveryError, 'Cannot determine Wi-Fi device state'):
            nm.snapshot()


if __name__ == '__main__':
    unittest.main()
