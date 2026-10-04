from pathlib import Path
from test_connection import test_directory
import unittest
from launcher.app import Application
from launcher.access import protect
import os
from unittest.mock import patch
import json


class ChannelTests(unittest.TestCase):
    def test_area52_play_uses_ascension_and_local_auth_port(self):
        class ImmediateThread:
            def __init__(self,target,**kwargs):self.target=target
            def start(self):self.target()
        with test_directory() as directory:
            root=Path(directory);client=root/'client';client.mkdir()
            (client/'Ascension.exe').write_bytes(b'fixture')
            app=Application(root/'settings');app.change_channel('area52');app.select(str(client))
            with patch('launcher.app.connection.load',return_value='127.0.0.1:3725'), \
                    patch('launcher.app.threading.Thread',ImmediateThread), \
                    patch('launcher.app.updater.ensure_closed'), \
                    patch('launcher.app.subprocess.Popen') as launch:
                app.start('play')
            self.assertEqual(app.error,'')
            self.assertEqual(launch.call_args.args[0][-1],str(client/'Ascension.exe'))
            self.assertIn('127.0.0.1:3725',(client/'realmlist.wtf').read_text())
            self.assertFalse((client/'WTF/Config.wtf').exists())
    def test_discord_opens_shared_invite_for_each_channel(self):
        with test_directory() as directory:
            app = Application(Path(directory))
            for channel in ('ptr', 'area52'):
                app.change_channel(channel)
                with patch('launcher.app.webbrowser.open', return_value=True) as browser:
                    app.open_discord()
                    browser.assert_called_once_with('https://discord.gg/ZkzWqsCqkt', new=2)

    def test_discord_rejects_untrusted_configured_url(self):
        with test_directory() as directory:
            root = Path(directory)
            (root / 'config').mkdir()
            app = Application(root / 'settings')
            for url in ('http://discord.gg/abc', 'https://discord.gg.evil.test/abc',
                        'https://discord.gg/abc?redirect=elsewhere', 'file:///test'):
                (root / 'config/account-discord.json').write_text(json.dumps({'ptr': url}))
                with patch('launcher.app.ROOT', root), self.assertRaises(ValueError):
                    app.discord_url()

    def test_separate_folders_and_persistence(self):
        with test_directory() as directory:
            root = Path(directory)
            ptr = root / 'ptr'
            alpha = root / 'alpha'
            ptr.mkdir(); alpha.mkdir()
            (ptr / 'Wow.exe').write_bytes(b'fixture')
            (ptr / 'Ascension.exe').write_bytes(b'fixture')
            (alpha / 'Ascension.exe').write_bytes(b'fixture')
            app = Application(root / 'settings')
            app.select(str(ptr))
            app.change_channel('area52')
            with self.assertRaises(ValueError):
                app.select(str(ptr))
            app.select(str(alpha))
            with patch.object(app,'area52_ready',return_value=False):
                self.assertFalse(app.status()['channel_ready'])
            for action in ('check', 'update', 'play', 'recover'):
                with patch.object(app,'area52_ready',return_value=False), self.assertRaises(ValueError):
                    app.start(action)
            restored = Application(root / 'settings')
            self.assertEqual(restored.channel, 'area52')
            restored.change_channel('ptr')
            self.assertEqual(restored.client, str(ptr.resolve()))

    def test_cannot_switch_during_update(self):
        with test_directory() as directory:
            app = Application(Path(directory))
            app.busy = True
            with self.assertRaises(ValueError):
                app.change_channel('area52')

    @unittest.skipUnless(os.name == 'nt', 'Windows DPAPI')
    def test_access_credential_roundtrip(self):
        original = b'test credential, not a real invitation'
        protected = protect(original)
        self.assertNotIn(original, protected)
        self.assertEqual(protect(protected, decrypt=True), original)
