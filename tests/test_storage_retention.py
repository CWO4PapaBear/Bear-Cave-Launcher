import errno
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from launcher import backups, selfupdate, storage, updater


class StorageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.parent = Path(temporary.name).resolve()
        self.home = self.parent / 'Bear Cave Launcher'
        self.home.mkdir()
        self.enterContext(patch.object(storage, 'launcher_home', return_value=self.home))

    def image(self, folder, version):
        folder.mkdir(exist_ok=True)
        (folder/'BearCaveLauncher.exe').write_text(version)
        (folder/'launcher-version.json').write_text(json.dumps({'version':version}))

    def job(self, number, owner=None):
        work = self.parent / f'bcu-{number:012x}'
        work.mkdir()
        (work/'job.json').write_text(json.dumps({'root':str(owner or self.home),'parent_pid':1}))
        ready = work/'worker-ready'
        ready.touch()
        os.utime(ready,(1700000000+number,1700000000+number))
        return work

    def test_upgrades_retain_two_flat_snapshots_and_preserve_state(self):
        self.image(self.home,'old')
        state=self.home/'.bear-cave-launcher'
        state.mkdir()
        (state/'pending.json').write_text('pending')
        unrelated=self.job(10,self.parent/'another launcher')
        self.image(unrelated/'previous','other')
        failed=self.job(11)
        (failed/'failed').mkdir()
        self.image(failed/'previous','failed')
        for number in range(1,5):
            work=self.job(number)
            self.image(work/'payload',str(number))
            selfupdate.swap(work,self.home,lambda p:None,lambda p:None)
            backups.collect(self.home,lambda msg:None)
            self.assertFalse(work.exists())
            self.assertEqual((state/'pending.json').read_text(),'pending')
        history=list((self.home/'Backups').iterdir())
        self.assertEqual({(p/'BearCaveLauncher.exe').read_text() for p in history},{'2','3'})
        self.assertFalse(any((p/'Backups').exists() or (p/'.bear-cave-launcher').exists() for p in history))
        self.assertTrue(unrelated.exists() and failed.exists())
        work=self.job(5)
        self.image(work/'payload','5')
        with self.assertRaises(RuntimeError):
            selfupdate.swap(work,self.home,lambda p:None,lambda p:(_ for _ in ()).throw(RuntimeError('failed restart')))
        self.assertEqual((self.home/'BearCaveLauncher.exe').read_text(),'4')
        self.assertEqual((state/'pending.json').read_text(),'pending')
        self.assertEqual(set((self.home/'Backups').iterdir()),set(history))

    def test_import_keeps_newest_legacy_backups_by_update_time(self):
        for n in (4,1,3,2):
            self.image(self.job(n)/'previous',str(n))
        backups.collect(self.home,lambda msg:None)
        backups.collect(self.home,lambda msg:None)
        self.assertFalse(list(self.parent.glob('bcu-*')))
        self.assertEqual({(p/'BearCaveLauncher.exe').read_text() for p in (self.home/'Backups').iterdir()},{'3','4'})

    def test_migrate_pending_state_across_volumes_and_isolate_clients(self):
        client=self.parent/'game'
        legacy=client/'.bear-cave-launcher'
        legacy.mkdir(parents=True)
        (legacy/'pending.json').write_text('pending')
        (legacy/'channel.json').write_text('{"channel":"area52"}')
        rename=Path.rename
        def cross_volume(source,target):
            if source.name=='.bear-cave-launcher.migrating' and target==storage.state_path(client):
                raise OSError(errno.EXDEV,'different drives')
            return rename(source,target)
        with patch.object(Path,'rename',cross_volume):
            state=updater.state_dir(client,'area52')
        self.assertTrue(state.is_relative_to(self.home/'.bear-cave-launcher'))
        self.assertFalse(legacy.exists())
        self.assertEqual((state/'pending.json').read_text(),'pending')
        with self.assertRaises(ValueError):updater.state_dir(client,'ptr')
        self.assertNotEqual(storage.state_path(self.parent/'another game'),state)
        legacy.mkdir()
        (legacy/'pending.json').write_text('different')
        with self.assertRaises(ValueError):storage.migrate(client)
        self.assertTrue(legacy.exists())
        self.assertEqual((state/'pending.json').read_text(),'pending')
