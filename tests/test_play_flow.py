import copy
import unittest
from unittest.mock import patch
from test_connection import test_directory
from test_fullclient import fixture
from launcher import baseline, updater
from launcher.app import Application

class ImmediateThread:
    def __init__(self,target,**kwargs):self.target=target
    def start(self):self.target()

class PlayFlowTests(unittest.TestCase):
    def client(self,root,m,payload,damaged=False):
        for component in m['components']:
            target=root/component['files'][0]['path'];target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(b'old' if damaged else b''.join(payload[c['url']] for c in component['chunks']))

    def test_check_update_play_hashes_baseline_once(self):
        with test_directory() as root:
            m,payload=fixture();self.client(root,m,payload,True)
            app=Application(root/'settings');app.channel='area52';app.client=str(root);app.manifest=m
            with patch('launcher.baseline.compare',wraps=baseline.compare) as compare:
                app.verify_baseline(root)
                with patch('launcher.baseline.compare',side_effect=AssertionError('Repeated baseline hash')):
                    updater.install(root,m,channel='area52',scan=app.scan,verified=app.accept_scan,
                        download=lambda url,target,**kw:target.write_bytes(payload[url]),guard=lambda:None)
                    self.assertTrue(app.valid_scan(root));self.assertFalse(app.scan.mismatches)
                    with patch('launcher.app.threading.Thread',ImmediateThread),patch.object(app,'area52_ready',return_value=True),patch.object(app,'configure_realm'),patch('launcher.app.updater.latest',return_value=m),patch('launcher.app.updater.ensure_closed'),patch('launcher.app.subprocess.Popen') as launch:
                        app.start('play')
                        self.assertEqual(app.error,'');launch.assert_called_once()
                self.assertEqual(compare.call_count,1)

    def test_cache_invalidates_for_file_manifest_folder_and_extra_archive(self):
        with test_directory() as root:
            m,payload=fixture();self.client(root,m,payload)
            mismatches,stamp=baseline.compare(root,m['baseline']);scan=baseline.Scan(root,m,mismatches,stamp)
            self.assertTrue(scan.valid(root,m))
            changed=copy.deepcopy(m);changed['baseline'][0]['sha256']='a'*64
            self.assertFalse(scan.valid(root,changed))
            self.assertFalse(scan.valid(root/'other',m))
            extra=root/'Data/extra.MPQ';extra.write_bytes(b'extra');self.assertFalse(scan.valid(root,m));extra.unlink()
            (root/'Extensions.dll').write_bytes(b'modified');self.assertFalse(scan.valid(root,m))

    def test_play_without_scan_checks_and_repairs_before_launch(self):
        with test_directory() as root:
            m,payload=fixture();self.client(root,m,payload,True)
            app=Application(root/'settings');app.channel='area52';app.client=str(root)
            real_install=updater.install
            def install(*args,**kwargs):
                kwargs.update(download=lambda url,target,**kw:target.write_bytes(payload[url]),guard=lambda:None)
                return real_install(*args,**kwargs)
            with patch('launcher.app.threading.Thread',ImmediateThread),patch.object(app,'area52_ready',return_value=True),patch.object(app,'configure_realm'),patch('launcher.app.updater.latest',return_value=m),patch('launcher.app.updater.ensure_closed'),patch('launcher.app.updater.install',side_effect=install),patch('launcher.app.subprocess.Popen') as launch,patch('launcher.baseline.compare',wraps=baseline.compare) as compare:
                app.start('play')
                self.assertEqual(app.error,'');launch.assert_called_once();self.assertEqual(compare.call_count,1)
                self.assertIsNone(app.scan)

    def test_visible_launcher_update_locks_actions_and_hands_off(self):
        with test_directory() as root:
            app=Application(root);app.prepare_launcher_update()
            self.assertTrue(app.status()['launcher_updating']);self.assertTrue(app.busy)
            with self.assertRaises(ValueError):app.start('play')
            closed=[]
            def update(report,progress):
                self.assertTrue(app.busy);report('Downloading launcher');progress('Downloading launcher',50,100)
                self.assertEqual(app.progress,40);return True
            with patch('launcher.app.threading.Thread',ImmediateThread),patch('launcher.selfupdate.startup',side_effect=update):
                app.run_launcher_update(lambda:closed.append(True))
            self.assertEqual(closed,[True]);self.assertFalse(app.busy)

    def test_failed_repair_never_launches(self):
        with test_directory() as root:
            m,payload=fixture();self.client(root,m,payload,True)
            app=Application(root/'settings');app.channel='area52';app.client=str(root)
            with patch('launcher.app.threading.Thread',ImmediateThread),patch.object(app,'area52_ready',return_value=True),patch('launcher.app.updater.latest',return_value=m),patch('launcher.app.updater.ensure_closed'),patch('launcher.app.updater.install',side_effect=OSError('interrupted')),patch('launcher.app.subprocess.Popen') as launch:
                app.start('play');launch.assert_not_called()
                self.assertIn('interrupted',app.error);self.assertIsNone(app.scan)

    def test_launcher_update_failure_unlocks_existing_launcher(self):
        with test_directory() as root:
            app=Application(root);app.prepare_launcher_update();closed=[]
            with patch('launcher.app.threading.Thread',ImmediateThread),patch('launcher.selfupdate.startup',return_value=False):
                app.run_launcher_update(lambda:closed.append(True))
            self.assertFalse(app.busy);self.assertFalse(app.launcher_updating);self.assertFalse(closed)

    def test_restart_reuses_cache_but_check_hashes_all(self):
        import hashlib
        with test_directory() as root:
            m,payload=fixture();self.client(root,m,payload)
            first=Application(root/'settings');first.channel='area52';first.manifest=m
            first.verify_baseline(root)
            app=Application(root/'settings');app.channel='area52';app.client=str(root)
            with patch('launcher.app.threading.Thread',ImmediateThread),patch.object(app,'area52_ready',return_value=True),patch.object(app,'configure_realm'),patch('launcher.app.updater.latest',return_value=m),patch('launcher.app.updater.ensure_closed'),patch('launcher.app.subprocess.Popen'),patch('launcher.baseline.hashlib.file_digest',side_effect=AssertionError('Repeated hash')):
                app.start('play');self.assertEqual(app.error,'')
            with patch('launcher.baseline.hashlib.file_digest',wraps=hashlib.file_digest) as digest:
                app.verify_baseline(root);self.assertEqual(digest.call_count,len(m['baseline']))

    def test_play_checks_launcher_before_client_and_stops_for_update_or_failure(self):
        for result in (True, RuntimeError('version unavailable')):
            with test_directory() as root:
                m,payload=fixture();self.client(root,m,payload)
                app=Application(root/'settings');app.channel='area52';app.client=str(root)
                closed=[];app.close_for_update=lambda:closed.append(True)
                with patch('launcher.app.threading.Thread',ImmediateThread),patch.object(app,'area52_ready',return_value=True),patch('launcher.selfupdate.startup',side_effect=result if isinstance(result,Exception) else None,return_value=result) as check,patch('launcher.app.updater.latest') as client,patch('launcher.app.subprocess.Popen') as launch:
                    app.start('play')
                    check.assert_called_once_with(app.report,app.report_progress,force=True)
                    client.assert_not_called();launch.assert_not_called()
                    self.assertEqual(bool(closed),result is True)
                    self.assertFalse(app.busy);self.assertFalse(app.launcher_updating)
