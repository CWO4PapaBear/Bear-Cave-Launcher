import shutil, unittest
from unittest.mock import patch
from test_connection import test_directory
from package import build, managed_path
from launcher import updater

class Area52BaseRepairTests(unittest.TestCase):
    def test_repair_repeat_and_rollback(self):
        with test_directory() as root:
            source=root/'source';source.mkdir()
            paths=['Ascension.ok','Data/patch-M.MPQ','Data/patch-S.MPQ']
            for name in paths:
                p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'reviewed')
                with self.assertRaises(ValueError):managed_path(name,'ptr')
            out=root/'package'
            manifest=build(source,dict(channel='area52',version='test',repository=updater.repository('area52'),server_build='test',components=[dict(id='base',paths=paths)]),out,'Repair test')
            manifest.update(schema=3,minimum_launcher_build=306,baseline=[dict(path=n,bytes=1,sha256='0'*64) for n in ('Ascension.exe','Extensions.dll')])
            updater.validate_manifest(manifest,'area52')
            client=root/'client';client.mkdir()
            (client/'Ascension.exe').write_bytes(b'test')
            (client/'WTF').mkdir();(client/'WTF/Config.wtf').write_bytes(b'private')
            for name in paths:
                p=client/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'old')
            def download(url,target,**kwargs):shutil.copyfile(out/url.rsplit('/',1)[-1],target)
            def fail(message):
                if message.startswith('Installing Data/patch-M'):raise OSError('interrupted')
            with self.assertRaises(OSError):updater.install(client,manifest,download=download,guard=lambda:None,report=fail,channel='area52')
            for name in paths:self.assertEqual((client/name).read_bytes(),b'old')
            updater.install(client,manifest,download=download,guard=lambda:None,channel='area52')
            for name in paths:self.assertEqual((client/name).read_bytes(),b'reviewed')
            self.assertEqual(updater.changed(client,manifest,'area52'),[])
            self.assertEqual((client/'WTF/Config.wtf').read_bytes(),b'private')
            manifest['minimum_launcher_build']=305
            with self.assertRaises(ValueError):updater.validate_manifest(manifest,'area52')
