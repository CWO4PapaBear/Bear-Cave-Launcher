from pathlib import Path
import hashlib, json, shutil, sys, threading, unittest, zipfile
from unittest.mock import patch
from urllib.request import Request, urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from launcher import updater
from launcher.app import Application,create_server
import test_packages
from package import build,sha

class Updater(unittest.TestCase):
    def setUp(self):
        test_packages.Packages.setUp(self)
        (self.client/'Wow.exe').write_bytes(b'not an executable; fixture only')
        source=self.root/'source';shutil.copytree(self.client,source)
        (source/'Interface/AddOns/HeroFreePick/HeroFreePick.lua').write_text('updated')
        (source/'Interface/AddOns/HeroFreePick/New.lua').write_text('new file')
        self.package=self.root/'package';self.manifest=build(source,self.config,self.package,'Notes')
        self.guard=lambda:None
    def download(self,url,target,limit,report):shutil.copy2(self.package/Path(url).name,target)
    def install(self,**kw):return updater.install(self.client,self.manifest,download=self.download,guard=self.guard,**kw)
    def test_install_preserves_private_files_and_backs_up(self):
        original=(self.client/'Interface/AddOns/HeroFreePick/HeroFreePick.lua').read_bytes()
        self.install()
        self.assertEqual((self.client/'WTF/private.txt').read_text(),'private')
        self.assertEqual(updater.changed(self.client,self.manifest),[])
        backups=list((self.client/'.bear-cave-launcher/transactions').glob('*/backup/*'))
        self.assertEqual(backups[0].read_bytes(),original)
        self.assertIn('up to date',self.install())
    def test_active_game_blocks_all_installation(self):
        def blocked():raise RuntimeError('WoW running')
        with self.assertRaises(RuntimeError):updater.install(self.client,self.manifest,guard=blocked)
        self.assertFalse((self.client/'.bear-cave-launcher').exists())
    def test_corrupt_archive_never_touches_client(self):
        (self.package/'hero.zip').write_bytes(b'bad')
        with self.assertRaises(ValueError):self.install()
        self.assertEqual((self.client/'Interface/AddOns/HeroFreePick/HeroFreePick.lua').read_text(),'print("test")')
    def test_partial_failure_rolls_back(self):
        count=0
        def report(message):
            nonlocal count
            if message.startswith('Installing '):
                count+=1
                if count==2:raise OSError('Simulated file failure')
        with self.assertRaises(OSError):self.install(report=report)
        self.assertEqual((self.client/'Interface/AddOns/HeroFreePick/HeroFreePick.lua').read_text(),'print("test")')
        self.assertFalse((self.client/'Interface/AddOns/HeroFreePick/New.lua').exists())
        self.assertFalse((self.client/'.bear-cave-launcher/pending.json').exists())
    def test_interruption_recovery(self):
        count=0
        def stop(message):
            nonlocal count
            if message.startswith('Installing '):
                count+=1
                if count==2:raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):self.install(report=stop)
        self.assertTrue((self.client/'.bear-cave-launcher/pending.json').exists())
        updater.recover(self.client,guard=self.guard)
        self.assertEqual((self.client/'Interface/AddOns/HeroFreePick/HeroFreePick.lua').read_text(),'print("test")')
    def test_wrong_realm_and_zip_traversal_rejected(self):
        self.manifest['channel']='main'
        with self.assertRaises(ValueError):self.install()
        self.manifest['channel']='ptr';archive=self.package/'hero.zip'
        with zipfile.ZipFile(archive,'a') as z:z.writestr('../bad.lua','bad')
        c=self.manifest['components'][0];c['sha256']=sha(archive);c['bytes']=archive.stat().st_size
        with self.assertRaises(ValueError):self.install()
        self.assertFalse((self.root/'bad.lua').exists())
    def test_manifest_pin_and_origin(self):
        pointer=dict(schema=1,channel='ptr',enabled=True,manifest_sha256='0'*64,
                     manifest_url=f'https://github.com/{updater.REPOSITORY}/releases/download/ptr-0.1.0/manifest.json')
        with patch.object(updater,'fetch',side_effect=[json.dumps(pointer).encode(),json.dumps(self.manifest).encode()]):
            with self.assertRaises(ValueError):updater.latest()
        self.manifest['components'][0]['url']='https://example.com/hero.zip'
        with self.assertRaises(ValueError):updater.validate_manifest(self.manifest)
    def test_loopback_session_rejects_csrf_and_unknown_files(self):
        app=Application(self.root/'config');server,url=create_server(app)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with urlopen(url+'api/status') as response:self.assertIn('client',json.load(response))
            for request in [Request(url+'api/select',data=b'{}',headers={'Content-Type':'application/json','Origin':'https://evil.example'}),
                            Request(url+'../../README.md'),Request(url+'api/status',headers={'Host':'evil.example'})]:
                with self.assertRaises(HTTPError):urlopen(request)
            with urlopen(url) as response:self.assertIn(b'runtime.js',response.read())
        finally:server.shutdown();server.server_close();thread.join()

if __name__=='__main__':unittest.main()
