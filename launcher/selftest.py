"""Packaged connection smoke test using synthetic files only; no network/game launch."""
from pathlib import Path
import shutil,tempfile,time,uuid
from . import app,connection,updater

def connection_check():
    base=Path(tempfile.gettempdir()).resolve()
    work=base/('bear-launcher-selftest-'+uuid.uuid4().hex);work.mkdir()
    original=(updater.latest,updater.changed,updater.ensure_closed)
    try:
        client=work/'client';(client/'Data/enUS').mkdir(parents=True);(client/'WTF').mkdir()
        (client/'Wow.exe').write_bytes(b'not executable; launcher test fixture')
        paths=[client/'realmlist.wtf',client/'Data/enUS/realmlist.wtf',client/'WTF/Config.wtf']
        for path in paths:path.write_text('set realmlist old.invalid\n')
        (client/'WTF/private.txt').write_text('preserved')
        # Model an already-current client: connection repair must not require downloads.
        updater.latest=lambda:{'version':'self-test'}
        updater.changed=lambda root,manifest,channel='ptr':[]
        updater.ensure_closed=lambda:None # Only our non-executable fixture is accessed.
        application=app.Application(work/'settings');application.select(str(client));application.start('check')
        deadline=time.monotonic()+15
        while application.busy and time.monotonic()<deadline:time.sleep(.05)
        assert not application.busy and not application.error,application.error
        host=connection.load(app.ROOT)
        assert all(('SET realmList "'+host+'"') in path.read_text() for path in paths)
        assert (client/'WTF/private.txt').read_text()=='preserved'
        if connection.native_windows():assert 'SET gxApi "D3D9"' in paths[-1].read_text()
        assert application.changes==[] and 'PTR connection configured.' in application.message
    finally:
        updater.latest,updater.changed,updater.ensure_closed=original
        assert work.resolve().parent==base and work.name.startswith('bear-launcher-selftest-')
        shutil.rmtree(work)


def cache_check():
    """Exercise the bundled repair only on disposable synthetic cache data."""
    import struct
    from . import cache_repair
    def row(entry, flags, kind):
        body=b'name\0\0\0\0\0\0'+struct.pack('<II',flags,kind)
        return struct.pack('<II',entry,len(body))+body
    header=b'BOMW'+struct.pack('<I',12340)+bytes(16)
    keep=row(17157,512,4);bad=row(22313,0,8)
    before=header+bad+keep+bytes(8)
    with tempfile.TemporaryDirectory(prefix='bear-cache-selftest-') as directory:
        root=Path(directory);cache=root/'Cache/WDB/enUS/Area 52 - Free-Pick/creaturecache.wdb'
        cache.parent.mkdir(parents=True);cache.write_bytes(before)
        # The guard is replaced only for this non-game fixture and restored below.
        guard=updater.ensure_closed
        try:
            updater.ensure_closed=lambda:None
            assert cache_repair.repair(root,'ptr')==0
            assert cache.read_bytes()==before
            assert cache_repair.repair(root,'area52')==1
            assert cache.read_bytes()==header+keep+bytes(8)
            assert next(cache.parent.glob('*.backup-*')).read_bytes()==before
            assert cache_repair.repair(root,'area52')==0
        finally:
            updater.ensure_closed=guard
