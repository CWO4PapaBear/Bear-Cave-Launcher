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
        updater.changed=lambda root,manifest:[]
        updater.ensure_closed=lambda:None # Only our non-executable fixture is accessed.
        application=app.Application(work/'settings');application.select(str(client));application.start('check')
        deadline=time.monotonic()+15
        while application.busy and time.monotonic()<deadline:time.sleep(.05)
        assert not application.busy and not application.error,application.error
        host=connection.load(app.ROOT)
        assert all(('SET realmList "'+host+'"') in path.read_text() for path in paths)
        assert (client/'WTF/private.txt').read_text()=='preserved'
        assert application.changes==[] and 'PTR connection configured.' in application.message
    finally:
        updater.latest,updater.changed,updater.ensure_closed=original
        assert work.resolve().parent==base and work.name.startswith('bear-launcher-selftest-')
        shutil.rmtree(work)
