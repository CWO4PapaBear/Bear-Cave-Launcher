from pathlib import Path
import copy, json, sys, shutil, uuid, unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from package import build, managed_path
from release import validate
from inspect_update import plan

class Packages(unittest.TestCase):
    def test_publisher_reads_utf8_release_notes(self):
        from release import run
        self.assertEqual(run(sys.executable, '-c', 'import sys; sys.stdout.buffer.write(bytes([240,159,144,190]))'), '\U0001f43e')
    def setUp(self):
        base=Path(__file__).resolve().parents[1]/'local/test-runs';base.mkdir(parents=True,exist_ok=True)
        self.root=base/uuid.uuid4().hex;self.root.mkdir()
        def cleanup():
            assert self.root.resolve().parent==base.resolve()
            shutil.rmtree(self.root)
        self.addCleanup(cleanup);self.client=self.root/'client'
        addon=self.client/'Interface/AddOns/HeroFreePick';addon.mkdir(parents=True)
        (addon/'HeroFreePick.lua').write_text('print("test")')
        (self.client/'WTF').mkdir();(self.client/'WTF/private.txt').write_text('private')
        self.config=dict(channel='ptr',version='0.1.0',repository='CWO4PapaBear/Bear-Cave-Launcher',server_build='test-image',
                         components=[dict(id='hero',paths=['Interface/AddOns/HeroFreePick'])])
    def test_round_trip_and_only_changed_component(self):
        output=self.root/'package';m=build(self.client,self.config,output,'Test notes')
        self.assertEqual(len(validate(output,self.config['repository'])[1]),4)
        self.assertEqual(plan(self.client,m,'ptr'),[])
        (self.client/'Interface/AddOns/HeroFreePick/HeroFreePick.lua').write_text('changed')
        self.assertEqual(plan(self.client,m,'ptr')[0]['component'],'hero')
        self.assertNotIn('WTF',json.dumps(m))
    def test_channel_isolation(self):
        m=build(self.client,self.config,self.root/'package','Notes')
        with self.assertRaises(ValueError):plan(self.client,m,'main')
    def test_tampered_package_rejected(self):
        output=self.root/'package';build(self.client,self.config,output,'Notes')
        (output/'hero.zip').write_bytes(b'tampered')
        with self.assertRaises(ValueError):validate(output,self.config['repository'])
    def test_paths(self):
        for path in ['../Wow.exe','/Data/patch-Z.MPQ','WTF/config.wtf','Interface/AddOns/../secret',
                     'Interface/AddOns/X/CON.lua','Interface/AddOns/X/foo:bar','Interface/AddOns/X/a.',
                     'Interface\\AddOns\\X','Interface/AddOns/X/backups/a.lua']:
            with self.subTest(path=path),self.assertRaises(ValueError):managed_path(path)
    def test_duplicate_and_unknown_file_fail_cleanly(self):
        self.config['components'].append(copy.deepcopy(self.config['components'][0]))
        with self.assertRaises(ValueError):build(self.client,self.config,self.root/'package','Notes')
        self.assertFalse((self.root/'package').exists())
        self.config['components'].pop()
        (self.client/'Interface/AddOns/HeroFreePick/private.json').write_text('{}')
        with self.assertRaises(ValueError):build(self.client,self.config,self.root/'package','Notes')
    def test_output_not_inside_client(self):
        with self.assertRaises(ValueError):build(self.client,self.config,self.client/'package','Notes')
    def test_source_symlink_rejected(self):
        link=self.client/'Interface/AddOns/HeroFreePick/link.lua'
        try:link.symlink_to(self.client/'WTF/private.txt')
        except OSError:self.skipTest('Symlink permission unavailable')
        with self.assertRaises(ValueError):build(self.client,self.config,self.root/'package','Notes')

if __name__=='__main__':unittest.main()
