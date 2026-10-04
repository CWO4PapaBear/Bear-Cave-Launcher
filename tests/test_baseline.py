import hashlib,unittest
from pathlib import Path
from test_connection import test_directory
from launcher import baseline,updater
class BaselineTests(unittest.TestCase):
    def records(self,root):
        rows=[]
        for name in ('Ascension.exe','Extensions.dll','Data/area-52/patch-D.MPQ'):
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'expected')
            rows.append(dict(path=name,bytes=8,sha256=hashlib.sha256(b'expected').hexdigest()))
        return rows
    def test_hash_mismatch_missing_and_change_after_success(self):
        with test_directory() as root:
            rows=self.records(root);m,stamp=baseline.compare(root,rows);self.assertEqual(m,[])
            (root/'Extensions.dll').write_bytes(b'altered!')
            self.assertNotEqual(baseline.signature(root,rows),stamp)
            (root/'Ascension.exe').unlink();m,_=baseline.compare(root,rows)
            self.assertEqual({x['reason'] for x in m},{'missing','hash differs'})
            (root/'Data/patch-extra.MPQ').write_bytes(b'extra')
            m,_=baseline.compare(root,rows)
            self.assertIn('unexpected archive',{x['reason'] for x in m})
    def test_private_and_traversal_paths_rejected(self):
        with test_directory() as root:
            rows=self.records(root)
            for name in ('../Ascension.exe','WTF/Config.wtf','Data/../secret.mpq'):
                bad=[dict(x) for x in rows];bad[-1]['path']=name
                with self.assertRaises(ValueError):baseline.validate(bad)
    def test_ptr_cannot_manage_area52_overlay(self):
        from package import managed_path
        with self.assertRaises(ValueError):managed_path('Data/area-52/patch-D.MPQ','ptr')
        managed_path('Data/area-52/patch-D.MPQ','area52')
        with self.assertRaises(ValueError):managed_path('Extensions.dll','area52')
