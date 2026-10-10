from pathlib import Path
import unittest,json,zipfile,hashlib,sys
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from launcher import selfupdate as s
from test_connection import test_directory

class SelfUpdateTests(unittest.TestCase):
    def archive(self,root,extra=None):
        path=root/'update.zip'
        with zipfile.ZipFile(path,'w')as z:
            z.writestr('BearCaveLauncher.exe',b'fixture')
            z.writestr('launcher-version.json',json.dumps({'version':'0.3.1','build':301}))
            z.writestr('_internal/ui/preview.html','test')
            if extra:z.writestr(*extra)
        return path,dict(schema=1,platform='win32',version='0.3.1',build=301,url=f'https://github.com/{s.REPOSITORY}/releases/download/launcher-0.3.1/BearCaveLauncher-update-win32.zip',bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    def test_valid_bundle_and_preserved_private_connection(self):
        with test_directory()as root:
            path,info=self.archive(root);s.validate(info);s.extract(path,root/'payload',info)
            old=root/'old';(old/'_internal').mkdir(parents=True);(old/'_internal/connection.json').write_text('private deployment')
            s.preserve_connection(old,root/'payload')
            self.assertEqual((root/'payload/_internal/connection.json').read_text(),'private deployment')
    def test_traversal_private_file_duplicates_and_corruption_rejected(self):
        for name in ['../evil','C:/evil','_internal/../evil','_internal/NUL','_internal/connection.json','BEARCAVELAUNCHER.EXE','_internal/a.']:
            with test_directory()as root:
                path,info=self.archive(root,(name,'bad'))
                with self.assertRaises(ValueError):s.extract(path,root/'payload',info)
                self.assertFalse((root/'payload').exists())
        with test_directory()as root:
            path,info=self.archive(root);path.write_bytes(path.read_bytes()+b'corrupt')
            with self.assertRaises(ValueError):s.extract(path,root/'payload',info)
    def test_identity_and_remote_url_rejected(self):
        with test_directory()as root:
            path,info=self.archive(root);info['version']='0.3.2'
            with self.assertRaises(ValueError):s.extract(path,root/'payload',info)
            info['url']='https://other.example/evil.zip'
            with self.assertRaises(ValueError):s.validate(info)
    def test_swap_retains_backup_and_rolls_back_failed_check(self):
        for fail in [False,True]:
            with test_directory()as base:
                root=base/'launcher';root.mkdir();(root/'BearCaveLauncher.exe').write_text('old')
                work=base/'work';(work/'payload').mkdir(parents=True);(work/'payload/BearCaveLauncher.exe').write_text('new')
                calls=[]
                def check(p):
                    if fail:raise RuntimeError('bad executable')
                if fail:
                    with self.assertRaises(RuntimeError):s.swap(work,root,check,lambda p:calls.append(p))
                    self.assertEqual((root/'BearCaveLauncher.exe').read_text(),'old');self.assertEqual(calls,[])
                else:
                    s.swap(work,root,check,lambda p:calls.append(p))
                    self.assertEqual((root/'BearCaveLauncher.exe').read_text(),'new')
                    self.assertEqual((work/'previous/BearCaveLauncher.exe').read_text(),'old');self.assertEqual(calls,[root])
    def test_offline_continues_and_downgrade_does_not_install(self):
        with patch.object(s.sys,'frozen',True,create=True),patch.object(s.sys,'platform','win32'),patch.object(s,'log'):
            with patch.object(s,'urlopen',side_effect=OSError('offline')):self.assertFalse(s.startup())
    def test_current_build_does_not_download(self):
        import io
        with test_directory()as root:
            _,info=self.archive(root);info['build']=s.BUILD;info['enabled']=True
            with patch.object(s.sys,'frozen',True,create=True),patch.object(s.sys,'platform','win32'),patch.object(s,'urlopen',return_value=io.BytesIO(json.dumps(info).encode())),patch.object(s,'fetch')as download:
                self.assertFalse(s.startup());download.assert_not_called()

    def test_job_rejects_unrelated_paths(self):
        with test_directory()as root:
            p=root/'job.json';p.write_text(json.dumps({'root':str(root/'other'),'parent_pid':123}))
            with self.assertRaises(ValueError):s.validate_job(p)

    def test_forced_check_ignores_restart_skip_and_blocks_offline(self):
        with patch.object(s.sys,'frozen',True,create=True),patch.object(s.sys,'platform','win32'),patch.object(s.sys,'argv',['launcher','--skip-launcher-update']),patch.object(s,'log'),patch.object(s,'urlopen',side_effect=OSError('offline')) as request:
            self.assertFalse(s.startup());request.assert_not_called()
            with self.assertRaisesRegex(RuntimeError,'could not be verified'):
                s.startup(force=True)
            request.assert_called_once()

if __name__=='__main__':unittest.main()
