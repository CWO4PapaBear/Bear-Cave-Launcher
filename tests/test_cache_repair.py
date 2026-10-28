import struct
import unittest
from unittest.mock import patch
from test_connection import test_directory
from launcher import cache_repair as repair


def row(entry, flags=0, kind=8):
    body=b'name\0\0\0\0\0\0'+struct.pack('<II',flags,kind)+b'other fields'
    return struct.pack('<II',entry,len(body))+body


def data(*rows):
    return b'BOMW'+struct.pack('<I',12340)+bytes(16)+b''.join(rows)+bytes(8)


class CacheRepairTests(unittest.TestCase):
    def cache(self, root, content, realm='Area 52 - Free-Pick'):
        path=root/'Cache/WDB/enUS'/realm/'creaturecache.wdb'
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
        return path

    def test_selective_preservation_backup_and_retry(self):
        with test_directory() as root, patch.object(repair.updater,'ensure_closed'):
            before=data(row(12),row(22313),row(1002),row(17157,512,4))
            cache=self.cache(root,before)
            other=self.cache(root,before,'Other Realm')
            self.assertEqual(repair.repair(root,'area52'),1)
            self.assertEqual(cache.read_bytes(),data(row(12),row(1002),row(17157,512,4)))
            backups=list(cache.parent.glob('*.backup-*'))
            self.assertEqual(len(backups),1);self.assertEqual(backups[0].read_bytes(),before)
            self.assertEqual(other.read_bytes(),before)
            self.assertEqual(repair.repair(root,'area52'),0)
            self.assertEqual(list(cache.parent.glob('*.backup-*')),backups)

    def test_missing_correct_unknown_and_ptr_untouched(self):
        with test_directory() as root:
            self.assertEqual(repair.repair(root,'area52'),0)
            for content in (data(),data(row(22313,512,4)),data(row(22313,1,8))):
                cache=self.cache(root,content)
                self.assertEqual(repair.repair(root,'area52'),0)
                self.assertEqual(cache.read_bytes(),content)
            cache=self.cache(root,data(row(22313)))
            self.assertEqual(repair.repair(root,'ptr'),0)
            self.assertEqual(cache.read_bytes(),data(row(22313)))

    def test_corrupt_and_duplicate_cache_not_changed(self):
        for content in (b'',data(row(22313))[:-1],data(row(22313),row(22313))):
            with test_directory() as root:
                cache=self.cache(root,content)
                with self.assertRaises(ValueError):repair.repair(root,'area52')
                self.assertEqual(cache.read_bytes(),content)

    def test_active_client_refused(self):
        with test_directory() as root, patch.object(repair.updater,'ensure_closed',side_effect=RuntimeError('Close client')):
            before=data(row(22313));cache=self.cache(root,before)
            with self.assertRaises(RuntimeError):repair.repair(root,'area52')
            self.assertEqual(cache.read_bytes(),before)

    def test_concurrent_write_refused(self):
        with test_directory() as root:
            before=data(row(22313));cache=self.cache(root,before);changed=data(row(42))
            calls=[]
            def guard():
                calls.append(1)
                if len(calls)==2:cache.write_bytes(changed)
            with patch.object(repair.updater,'ensure_closed',side_effect=guard):
                with self.assertRaises(RuntimeError):repair.repair(root,'area52')
            self.assertEqual(cache.read_bytes(),changed)
            self.assertEqual(next(cache.parent.glob('*.backup-*')).read_bytes(),before)

    def test_replace_failure_keeps_original_and_backup(self):
        with test_directory() as root, patch.object(repair.updater,'ensure_closed'), patch.object(repair.os,'replace',side_effect=OSError('locked')):
            before=data(row(22313));cache=self.cache(root,before)
            with self.assertRaises(OSError):repair.repair(root,'area52')
            self.assertEqual(cache.read_bytes(),before)
            self.assertEqual(next(cache.parent.glob('*.backup-*')).read_bytes(),before)
            self.assertFalse(list(cache.parent.glob('*.repair-*')))

    def test_link_guard_and_escape(self):
        with test_directory() as root:
            with patch.object(type(root),'is_symlink',return_value=True):
                with self.assertRaises(ValueError):repair.repair(root,'area52')
            with self.assertRaises(ValueError):repair.safe_path(root,root.parent/'outside')

    def test_alias_and_additional_locale(self):
        with test_directory() as root, patch.object(repair.updater,'ensure_closed'):
            cache=self.cache(root,data(row(22313)),'Area-52')
            second=root/'Cache/WDB/deDE/Area 52 - Free-Pick/creaturecache.wdb'
            second.parent.mkdir(parents=True);second.write_bytes(data(row(22313),row(7)))
            self.assertEqual(repair.repair(root,'area52'),2)
            self.assertEqual(cache.read_bytes(),data())
            self.assertEqual(second.read_bytes(),data(row(7)))

    def test_readback_failure_retains_backup(self):
        with test_directory() as root, patch.object(repair.updater,'ensure_closed'), patch.object(repair.os,'replace'):
            before=data(row(22313));cache=self.cache(root,before)
            with self.assertRaisesRegex(RuntimeError,'Readback failed'):repair.repair(root,'area52')
            self.assertEqual(cache.read_bytes(),before)
            self.assertEqual(next(cache.parent.glob('*.backup-*')).read_bytes(),before)
