from pathlib import Path
from test_connection import test_directory
import unittest
from launcher.app import Application
from launcher.access import protect
import os


class ChannelTests(unittest.TestCase):
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
            self.assertFalse(app.status()['channel_ready'])
            for action in ('check', 'update', 'play', 'recover'):
                with self.assertRaises(ValueError):
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
