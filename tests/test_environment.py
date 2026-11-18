from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from launcher.app import Application


class EnvironmentTests(unittest.TestCase):
    def test_default_persistence_and_busy_guard(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            app = Application(root)
            app.channel = 'area52'
            self.assertEqual(app.realm(), '129.121.172.245:3727')
            app.change_environment('development')
            restored = Application(root)
            self.assertEqual(restored.realm(), '127.0.0.1:3727')
            restored.busy = True
            with self.assertRaises(ValueError):restored.change_environment('cloud')
            self.assertEqual(restored.environment, 'development')
            restored.busy = False
            with self.assertRaises(ValueError):restored.change_environment('bad')
            with patch('launcher.app.updater.save_json', side_effect=OSError('disk')):
                with self.assertRaises(OSError):restored.change_environment('cloud')
            self.assertEqual(restored.environment, 'development')

    def test_client_connection_switch_and_guard(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            client = root/'client'
            paths = [client/'Data/enUS/realmlist.wtf', client/'realmlist.wtf', client/'WTF/Config.wtf']
            for path in paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'SET realmList "old"\r\nSET gxApi "D3D9"\r\n')
            app = Application(root/'settings')
            app.channel = 'area52'
            state = root/'state'
            with patch('launcher.app.updater.ensure_closed'):
                for environment, endpoint in [('development', b'127.0.0.1:3727'), ('cloud', b'129.121.172.245:3727')]:
                    app.change_environment(environment)
                    app.configure_realm(client, state)
                    for path in paths:
                        self.assertIn(endpoint, path.read_bytes())
                        self.assertIn(b'SET gxApi "D3D9"\r\n', path.read_bytes())
            before = [path.read_bytes() for path in paths]
            with patch('launcher.app.updater.ensure_closed', side_effect=ValueError('running')):
                with self.assertRaises(ValueError):app.configure_realm(client, state)
            self.assertEqual(before, [path.read_bytes() for path in paths])
            self.assertTrue(list((state/'realm-backups').iterdir()))

    def test_old_or_invalid_settings_default_cloud(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for settings in ({'channel':'area52'}, {'channel':'area52','environment':'unknown'}):
                (root/'settings.json').write_text(json.dumps(settings))
                self.assertEqual(Application(root).realm(), '129.121.172.245:3727')
