"""Synthetic executable fixtures; never redistribute game binaries."""
import hashlib
import unittest
from unittest.mock import patch
from launcher import rune_fix, updater
from test_updater import Updater

class RuneRepair(Updater):
    def setUp(self):
        super().setUp()
        self.original = b'x'*16 + bytes.fromhex('83fb06755a8b1d8843c200') + b'z'*16
        self.fixed = self.original[:19]+b'\x90\x90'+self.original[21:]
        for key,value in dict(OFFSET=19,SIZE=len(self.original),
                              BEFORE=hashlib.sha256(self.original).hexdigest(),
                              AFTER=hashlib.sha256(self.fixed).hexdigest()).items():
            p=patch.object(rune_fix,key,value);p.start();self.addCleanup(p.stop)
        (self.client/'Wow.exe').write_bytes(self.original)
        self.manifest.update(schema=2,client_fixes=[rune_fix.FIX_ID],minimum_launcher_build=301)

    def test_repair_exact_bytes_backup_and_idempotence(self):
        self.assertIn('rune-recovery-client-fix',[x['id'] for x in updater.pending_changes(self.client,self.manifest)])
        self.install()
        self.assertEqual((self.client/'Wow.exe').read_bytes(),self.fixed)
        backups=list((self.client/'.bear-cave-launcher/transactions').glob('*/backup/*'))
        self.assertIn(self.original,[p.read_bytes() for p in backups])
        self.assertEqual(updater.pending_changes(self.client,self.manifest),[])
        self.assertIn('up to date',self.install())

    def test_unknown_executable_stops_before_any_payload_install(self):
        (self.client/'Wow.exe').write_bytes(b'unknown')
        with self.assertRaisesRegex(ValueError,'not been reviewed'):self.install()
        self.assertEqual((self.client/'Wow.exe').read_bytes(),b'unknown')
        self.assertFalse((self.client/'Interface/AddOns/HeroFreePick/New.lua').exists())

    def test_second_reviewed_build_preserves_other_modifications(self):
        original = self.original + b'second-build-modifications'
        fixed = self.fixed + b'second-build-modifications'
        with patch.multiple(rune_fix,
                            WARMANE_BEFORE=hashlib.sha256(original).hexdigest(),
                            WARMANE_AFTER=hashlib.sha256(fixed).hexdigest(),
                            WARMANE_SIZE=len(original)):
            (self.client/'Wow.exe').write_bytes(original)
            self.install()
            self.assertEqual((self.client/'Wow.exe').read_bytes(), fixed)
            self.assertIn('up to date', self.install())
            self.assertIsNone(rune_fix.patched(fixed))
            with self.assertRaisesRegex(ValueError, 'not been reviewed'):
                rune_fix.patched(original + b'changed')

    def test_second_build_output_hash_is_enforced(self):
        original = self.original + b'second-build'
        with patch.multiple(rune_fix,
                            WARMANE_BEFORE=hashlib.sha256(original).hexdigest(),
                            WARMANE_AFTER='0'*64, WARMANE_SIZE=len(original)):
            with self.assertRaisesRegex(ValueError, 'output checksum mismatch'):
                rune_fix.patched(original)

    def test_repair_when_all_archive_files_already_current(self):
        old=dict(self.manifest);old['schema']=1;old.pop('client_fixes');old.pop('minimum_launcher_build')
        updater.install(self.client,old,download=self.download,guard=self.guard)
        self.assertEqual(updater.changed(self.client,self.manifest),[])
        self.install()
        self.assertEqual((self.client/'Wow.exe').read_bytes(),self.fixed)

    def test_failure_restores_executable_and_addons_together(self):
        def fail(message):
            if message.startswith('Installing Interface/'):raise OSError('injected')
        with self.assertRaises(OSError):self.install(report=fail)
        self.assertEqual((self.client/'Wow.exe').read_bytes(),self.original)

    def test_interrupted_repair_is_recoverable(self):
        def interrupt(message):
            if message.startswith('Installing Interface/'):raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):self.install(report=interrupt)
        self.assertEqual((self.client/'Wow.exe').read_bytes(),self.fixed)
        updater.recover(self.client,guard=self.guard)
        self.assertEqual((self.client/'Wow.exe').read_bytes(),self.original)

    def test_schema_and_fix_identity_are_required(self):
        self.manifest['schema']=1
        with self.assertRaises(ValueError):self.install()
        self.manifest['schema']=2;self.manifest['client_fixes']=['unknown']
        with self.assertRaises(ValueError):self.install()

    # Parent exercises common transaction behavior on the schema-1 baseline;
    # this inherited assertion assumes exactly one original addon backup.
    def test_install_preserves_private_files_and_backs_up(self):
        self.test_repair_exact_bytes_backup_and_idempotence()
        self.assertEqual((self.client/'WTF/private.txt').read_text(),'private')

if __name__=='__main__':unittest.main()
