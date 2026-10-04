from pathlib import Path
import unittest,sys,uuid,shutil
from contextlib import contextmanager
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from launcher import connection

@contextmanager
def test_directory():
    base=Path(__file__).resolve().parents[1]/'local/test-runs';base.mkdir(parents=True,exist_ok=True)
    root=base/uuid.uuid4().hex;root.mkdir()
    try:yield root
    finally:
        assert root.resolve().parent==base.resolve()
        shutil.rmtree(root)

class ConnectionTests(unittest.TestCase):
    def test_existing_launcher_gains_area52_without_replacing_override(self):
        import json
        with test_directory() as root:
            (root/'connection.json').write_text(json.dumps(dict(schema=1,channel='ptr',address='ptr.example.com:3724')))
            self.assertEqual(connection.load(root,'area52'),'ptr.example.com:3725')
            (root/'connection-area52.json').write_text(json.dumps(dict(schema=1,channel='area52',address='127.0.0.1:3725')))
            self.assertEqual(connection.load(root,'area52'),'127.0.0.1:3725')

    def test_direct3d_preserves_settings_and_backs_up(self):
        with test_directory() as root:
            (root/'WTF').mkdir();config=root/'WTF/Config.wtf'
            original=b'SET gxApi "OpenGL"\r\nSET gxResolution "2560x1440"\r\n# \xfc\r\n'
            config.write_bytes(original);state=root/'state'
            with patch.object(connection,'native_windows',return_value=True):
                connection.configure(root,state,'ptr.example.com',lambda:None)
                self.assertIn(b'SET gxApi "D3D9"',config.read_bytes())
                self.assertIn(b'SET gxResolution "2560x1440"\r\n# \xfc',config.read_bytes())
                self.assertEqual(next((state/'realm-backups').glob('*/WTF/Config.wtf')).read_bytes(),original)
                count=len(list((state/'realm-backups').iterdir()))
                connection.configure(root,state,'ptr.example.com',lambda:None)
                self.assertEqual(count,len(list((state/'realm-backups').iterdir())))
    def test_fresh_windows_config_and_wine_preservation(self):
        with test_directory() as root:
            with patch.object(connection,'native_windows',return_value=True):
                connection.configure(root,root/'state','ptr.example.com',lambda:None)
            config=root/'WTF/Config.wtf'
            self.assertIn(b'SET gxApi "D3D9"',config.read_bytes())
            config.write_bytes(b'SET gxApi "OpenGL"\n')
            with patch.object(connection,'native_windows',return_value=False):
                connection.configure(root,root/'state','ptr.example.com',lambda:None)
            self.assertIn(b'SET gxApi "OpenGL"',config.read_bytes())

    def test_check_repairs_connection_when_no_update_is_needed(self):
        from launcher import app
        class ImmediateThread:
            def __init__(self,target,**kwargs):self.target=target
            def start(self):self.target()
        with test_directory() as folder:
            client=folder/'client';(client/'Data/enUS').mkdir(parents=True)
            (client/'Wow.exe').write_bytes(b'fixture only')
            realm=client/'Data/enUS/realmlist.wtf';realm.write_text('set realmlist old.example\n')
            application=app.Application(folder/'settings');application.select(str(client))
            with patch.object(app.threading,'Thread',ImmediateThread),patch.object(app.connection,'load',return_value='ptr.example.com'),patch.object(app.updater,'ensure_closed'),patch.object(app.updater,'latest',return_value={'version':'test'}),patch.object(app.updater,'changed',return_value=[]):
                application.start('check')
            self.assertEqual(application.error,'')
            self.assertEqual(application.changes,[])
            self.assertIn('ptr.example.com',realm.read_text())
            self.assertIn('PTR connection configured',application.message)
    def test_stock_and_existing_settings(self):
        with test_directory() as folder:
            root=Path(folder);(root/'Data/enUS').mkdir(parents=True);(root/'WTF').mkdir()
            settings=root/'WTF/Config.wtf';settings.write_bytes(b'SET gxResolution "1920x1080"\r\nSET realmList "old.example"\r\n')
            state=root/'.bear-cave-launcher';state.mkdir()
            before=settings.read_bytes()
            connection.configure(root,state,'ptr.example.com',lambda:None)
            self.assertIn(b'ptr.example.com',(root/'Data/enUS/realmlist.wtf').read_bytes())
            self.assertIn(b'SET gxResolution "1920x1080"',settings.read_bytes())
            self.assertEqual(next((state/'realm-backups').glob('*/WTF/Config.wtf')).read_bytes(),before)
            count=len(list((state/'realm-backups').iterdir()))
            connection.configure(root,state,'ptr.example.com',lambda:None)
            self.assertEqual(count,len(list((state/'realm-backups').iterdir())))
    def test_bad_address_and_running_game(self):
        for value in ('x\nSET foo bar','https://example.com','../file','bad..host','-bad.example',''):
            with self.assertRaises(ValueError):connection.address(value)
        with test_directory() as folder:
            root=Path(folder)
            def blocked():raise RuntimeError('running')
            with self.assertRaises(RuntimeError):connection.configure(root,root/'state','ptr.example.com',blocked)
            self.assertEqual(list(root.iterdir()),[])
    def test_nonenglish_root_and_failure_rollback(self):
        with test_directory() as folder:
            root=Path(folder);(root/'Data/deDE').mkdir(parents=True)
            original=b'set realmlist old.example\n# \xfc\n'
            (root/'realmlist.wtf').write_bytes(original)
            state=root/'state';state.mkdir();calls=0
            def guard():
                nonlocal calls
                calls+=1
                if calls==3:raise RuntimeError('interrupted')
            with self.assertRaises(RuntimeError):connection.configure(root,state,'ptr.example.com',guard)
            self.assertEqual((root/'realmlist.wtf').read_bytes(),original)
            self.assertFalse((root/'Data/deDE/realmlist.wtf').exists())
            connection.configure(root,state,'ptr.example.com',lambda:None)
            self.assertIn(b'# \xfc',(root/'realmlist.wtf').read_bytes())

if __name__=='__main__':unittest.main()
