import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('announcement', Path(__file__).resolve().parents[1] / 'tools/announce_launcher_notes.py')
announcement = importlib.util.module_from_spec(spec)
spec.loader.exec_module(announcement)


class AnnouncementGateTests(unittest.TestCase):
    def test_old_launcher_blocks_announcement(self):
        with patch.object(announcement.updater, 'fetch', return_value=b'{"enabled":true,"version":"0.3.6"}'):
            with self.assertRaisesRegex(RuntimeError, 'Launcher'):
                announcement.verify_live()

    def test_unpromoted_client_blocks_announcement(self):
        responses = [b'{"enabled":true,"version":"0.3.7"}', b'{"enabled":true,"manifest_url":"old"}']
        with patch.object(announcement.updater, 'fetch', side_effect=responses):
            with self.assertRaisesRegex(RuntimeError, 'not publicly promoted'):
                announcement.verify_live()

    def test_bad_manifest_hash_blocks_announcement(self):
        pointer = dict(enabled=True, manifest_url='https://github.com/CWO4PapaBear/Area52-FreePick-Client/releases/download/area52-0.1.0-alpha.4/manifest.json', manifest_sha256='0' * 64)
        responses = [b'{"enabled":true,"version":"0.3.7"}', json.dumps(pointer).encode(), b'{}']
        with patch.object(announcement.updater, 'fetch', side_effect=responses):
            with self.assertRaisesRegex(RuntimeError, 'hash differs'):
                announcement.verify_live()
