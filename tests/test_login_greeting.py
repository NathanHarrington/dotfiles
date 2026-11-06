"""Run with: python3 -m unittest discover -s tests -v"""

import importlib.util
import json
import os
from pathlib import Path
import pty
import re
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'login-greeting.py'
ANSI = re.compile(r'\x1b\[[0-9;?]*[ -/]*[@-~]')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


greeting = load('unified_login_greeting', SCRIPT)


class GreetingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.home = Path(self.directory.name)
        self.env = dict(os.environ, HOME=str(self.home), XDG_CONFIG_HOME=str(self.home / 'config'),
                        XDG_STATE_HOME=str(self.home / 'state'), TERM='xterm-256color',
                        COLUMNS='87', LINES='24', PYTHONPATH='', SHELL='/bin/bash')

    def run_cli(self, *args, script=SCRIPT, check=True, **kwargs):
        return subprocess.run([sys.executable, str(script), *args], cwd=self.home, env=self.env,
                              capture_output=True, timeout=15, check=check, **kwargs)

    def test_catalog_and_random_groups(self):
        self.assertEqual(len(greeting.DESIGNS), 70)
        for group, count in [('arrival', 9), ('krypton', 8), ('compact', 4), ('thinkpad', 24), ('cordince', 3)]:
            self.assertEqual(len(greeting.GROUPS[group]), count)
            with mock.patch.object(greeting.random, 'choice', side_effect=lambda options: options[-1]) as choose:
                picked = greeting.choose('random:' + group)
                self.assertIn(picked.name, greeting.GROUPS[group])
                choose.assert_called_once_with(greeting.GROUPS[group])
        self.assertIsNone(greeting.choose('off'))
        for removed in ('ares-cubes', 'ares-volumes', 'silo', 'cyber-city', 'encom', 'romulus', 'andor', 'helix'):
            self.assertNotIn(removed, greeting.DESIGNS)
            self.assertNotIn(removed + '-compact', greeting.DESIGNS)

    def test_all_designs_fit_narrow_short_and_wide_terminals(self):
        for width, height in ((22, 8), (50, 20), (86, 20), (140, 20)):
            for design in greeting.DESIGNS.values():
                final, factory, duration = greeting.prepare(design, width, height)
                self.assertGreater(duration, 0)
                self.assertLessEqual(len(final), height, design.name)
                self.assertTrue(all(len(ANSI.sub('', line)) <= width for line in final), design.name)
                first, _ = next(factory())
                self.assertEqual(len(first), len(final), design.name)

    def test_standalone_copy_needs_no_sibling_files_or_external_tools(self):
        copied = self.home / 'portable.py'
        shutil.copy2(SCRIPT, copied)
        self.env['PATH'] = '/nonexistent'
        for group in ('cinematic', 'lima', 'thinkpad', 'text', 'cordince'):
            result = self.run_cli('--group', group, '--gallery', script=copied)
            self.assertEqual(result.stderr, b'')
            self.assertGreater(len(result.stdout), 100)
        quiet = self.run_cli('--login', script=copied)
        self.assertEqual(quiet.stdout, b'')
        self.assertEqual(quiet.stderr, b'')


    def test_random_group_sources_stay_in_that_group(self):
        output = self.run_cli('--theme', 'random:arrival', '--sources').stdout.decode()
        names = [line.split(':', 1)[0] for line in output.splitlines() if line and not line.startswith(' ')]
        self.assertEqual(names, list(greeting.GROUPS['arrival']))


    def test_cli_selection_and_validation(self):
        self.assertEqual(self.run_cli('lima-purple', '--once').stdout,
                         self.run_cli('--theme', 'lima-purple', '--once').stdout)
        self.assertEqual(self.run_cli('off').stdout, b'')
        for args in (('',), ('--theme', ''), ('not-a-design',),
                     ('lima-purple', '--theme', 'arrival'), ('--duration', 'nan'),
                     ('--duration', '0')):
            with self.subTest(args=args):
                self.assertEqual(self.run_cli(*args, check=False).returncode, 2)

    def test_removed_settings_commands_are_rejected(self):
        for option in ('--set', '--settings', '--config', '--install', '--shell'):
            with self.subTest(option=option):
                self.assertEqual(self.run_cli(option, check=False).returncode, 2)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_greetings_ignore_old_settings_and_do_not_write_files(self):
        config = self.home / 'config' / 'login-greeting'
        config.mkdir(parents=True)
        (config / (greeting.socket.gethostname().lower() + '.json')).write_text('{broken')
        before = {p.relative_to(self.home): p.read_bytes() for p in self.home.rglob('*') if p.is_file()}
        for args in (('--once',), ('lima-purple', '--once'), ('random', '--once'),
                     ('random:arrival', '--once'), ('--random', 'krypton', '--once')):
            self.run_cli(*args)
        after = {p.relative_to(self.home): p.read_bytes() for p in self.home.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_bashrc_passes_its_manual_selection(self):
        program = self.home / '.local' / 'bin' / 'login-greeting'
        program.parent.mkdir(parents=True)
        program.write_text("import json, sys\nprint('GREETING_ARGS=' + json.dumps(sys.argv[1:]))\n")
        source = (ROOT / '.bashrc').read_text()
        start = source.index('# >>> login-greeting >>>')
        end = source.index('# <<< login-greeting <<<', start) + len('# <<< login-greeting <<<')
        hook = source[start:end]
        rc = self.home / '.bashrc'
        for host, expected in (('lima', 'lima-purple'), ('slippy', 'cordince-green')):
            rc.write_text(hook)
            output = self.terminal(['/bin/bash', '--noprofile', '--norc', '-ic',
                                    f'HOSTNAME={host}; . "$HOME/.bashrc"'])
            self.assertIn('GREETING_ARGS=' + json.dumps([expected, '--login']), output)
        rc.write_text(hook.replace('LOGIN_GREETING="cordince-green"', 'LOGIN_GREETING="random:arrival"'))
        output = self.terminal(['/bin/bash', '--noprofile', '--norc', '-ic',
                                'HOSTNAME=slippy; . "$HOME/.bashrc"'])
        self.assertIn('GREETING_ARGS=' + json.dumps(['random:arrival', '--login']), output)
        quiet = subprocess.run(['/bin/bash', '--noprofile', '--norc', '-c',
                                '. "$HOME/.bashrc"; printf READY'], env=self.env,
                               capture_output=True, timeout=10, check=True)
        self.assertEqual(quiet.stdout, b'READY')
        self.assertEqual(quiet.stderr, b'')

    def terminal(self, command, interrupt=False):
        master, slave = pty.openpty()
        proc = subprocess.Popen(command,
                                stdout=slave, stderr=slave, stdin=subprocess.DEVNULL, env=self.env)
        os.close(slave)
        output = bytearray()
        sent = False
        started = time.monotonic()
        try:
            while time.monotonic() - started < 10:
                if select.select([master], [], [], .1)[0]:
                    try:
                        chunk = os.read(master, 65536)
                    except OSError:
                        break
                    if not chunk:
                        break
                    output.extend(chunk)
                    if interrupt and not sent and b'\x1b[?25l' in output:
                        proc.send_signal(signal.SIGINT)
                        sent = True
                elif proc.poll() is not None:
                    break
            self.assertEqual(proc.wait(timeout=2), 0, output.decode(errors='replace'))
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
            os.close(master)
        decoded = output.decode()
        self.assertNotIn('Traceback', decoded)
        return decoded

    def test_animation_families_and_interrupt_restore_cursor(self):
        for name in ('arrival-contact', 'ares-compact', 'lima-purple', 'thinkpad-24', 'teletype', 'cordince-green', 'cordince-console'):
            output = self.terminal([sys.executable, str(SCRIPT), name, '--duration', '.08'])
            self.assertIn('\x1b[0m\x1b[?25h', output)
            self.assertTrue(all(len(line) < 87 for line in ANSI.sub('', output).splitlines()), name)
        output = self.terminal([sys.executable, str(SCRIPT), 'cordince-green', '--duration', '1'], interrupt=True)
        self.assertIn('\x1b[0m\x1b[?25h', output)


if __name__ == '__main__':
    unittest.main()
