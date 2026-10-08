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


class PersistentTests(BaselineTests):
    def test_restarts_changes_and_manifest_hash(self):
        from unittest.mock import patch
        with test_directory() as root:
            rows=self.records(root);m,stamp=baseline.compare(root,rows)
            cache=root/'cache.json';baseline.save_cache(cache,baseline.Scan(root,{'schema':4,'baseline':rows},m,stamp),rows)
            saved=baseline.read_cache(cache,root)
            with patch('launcher.baseline.hashlib.file_digest',side_effect=AssertionError('Unchanged file rehashed')):
                self.assertEqual(baseline.compare(root,rows,cache=saved)[0],[])
            (root/'Extensions.dll').write_bytes(b'altered!')
            with patch('launcher.baseline.hashlib.file_digest',wraps=hashlib.file_digest) as digest:
                mismatches,_=baseline.compare(root,rows,cache=saved)
                self.assertEqual(digest.call_count,1)
                self.assertEqual(mismatches,[dict(path='Extensions.dll',reason='hash differs')])
            changed=[dict(r) for r in rows];changed[0]['sha256']='0'*64
            self.assertIn(dict(path='Ascension.exe',reason='hash differs'),baseline.compare(root,changed,cache=saved)[0])
            with patch('launcher.baseline.hashlib.file_digest',wraps=hashlib.file_digest) as digest:
                baseline.compare(root,rows);self.assertEqual(digest.call_count,3)
            (root/'Data/patch-extra.MPQ').write_bytes(b'x')
            self.assertIn('unexpected archive',{r['reason'] for r in baseline.compare(root,rows,cache=saved)[0]})
            self.assertEqual(baseline.read_cache(cache,root/'different'),{})
            for bad in ('broken','[]','null'):
                cache.write_text(bad);self.assertEqual(baseline.read_cache(cache,root),{})
