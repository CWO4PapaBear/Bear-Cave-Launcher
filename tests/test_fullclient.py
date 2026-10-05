import copy,hashlib,json,shutil,unittest
from unittest.mock import patch
from test_connection import test_directory
from launcher import updater,fullclient
from launcher.app import Application

def digest(data):return hashlib.sha256(data).hexdigest()

def fixture():
    version='full-test';prefix='https://github.com/CWO4PapaBear/Area52-FreePick-Client/releases/download/area52-'+version+'/'
    manifest=dict(schema=4,channel='area52',minimum_launcher_build=307,version=version,tag='area52-'+version,notes_url=prefix+'PATCH-NOTES.md',baseline=[],components=[])
    payload={}
    for index,name in enumerate(('Ascension.exe','Extensions.dll','Data/common.MPQ','Data/Content/SpellRankData.json')):
        data=(name+'-tested-payload').encode();record=dict(path=name,bytes=len(data),sha256=digest(data));chunks=[];cid='file-'+str(index)
        for n,block in enumerate((data[:8],data[8:])):
            asset=f'{cid}-{n:03d}.bin';payload[prefix+asset]=block
            chunks.append(dict(asset=asset,url=prefix+asset,bytes=len(block),sha256=digest(block)))
        manifest['baseline'].append(record);manifest['components'].append(dict(id=cid,bytes=len(data),files=[record],chunks=chunks))
    return manifest,payload

class FullClientTests(unittest.TestCase):
    def client(self,root,m):
        for row in m['baseline']:
            p=root/row['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'old')
        (root/'WTF').mkdir();(root/'WTF/Config.wtf').write_bytes(b'personal')

    def test_resume_corruption_and_runtime_install(self):
        with test_directory() as root:
            m,payload=fixture();self.client(root,m);calls=[]
            def interrupted(url,target,**kw):
                calls.append(url)
                if len(calls)==2:target.write_bytes(b'partial');raise OSError('connection interrupted')
                target.write_bytes(payload[url])
            with self.assertRaises(OSError):updater.install(root,m,channel='area52',download=interrupted,guard=lambda:None)
            self.assertEqual((root/'Ascension.exe').read_bytes(),b'old')
            self.assertFalse((root/'.bear-cave-launcher/pending.json').exists())
            resumed=[];progress=[]
            def download(url,target,**kw):resumed.append(url);target.write_bytes(payload[url])
            updater.install(root,m,channel='area52',download=download,guard=lambda:None,progress=lambda *args:progress.append(args))
            self.assertNotIn(calls[0],resumed)
            self.assertEqual(updater.changed(root,m,'area52'),[])
            self.assertFalse((root/'.bear-cave-launcher/downloads').exists())
            self.assertEqual((root/'WTF/Config.wtf').read_bytes(),b'personal')
            self.assertEqual(progress[-1],('Installing',4,4))
            self.assertEqual(progress[-5][1],sum(c['bytes'] for c in m['components']))
            updater.install(root,m,channel='area52',download=lambda *a,**k:self.fail('Repeat should not download'),guard=lambda:None)

    def test_bad_chunk_does_not_modify_client(self):
        with test_directory() as root:
            m,_=fixture();self.client(root,m)
            with self.assertRaises(ValueError):updater.install(root,m,channel='area52',download=lambda url,target,**kw:target.write_bytes(b'wrong'),guard=lambda:None)
            self.assertEqual((root/'Ascension.exe').read_bytes(),b'old')

    def test_install_failure_restores_runtime(self):
        with test_directory() as root:
            m,payload=fixture();self.client(root,m)
            def report(message):
                if message=='Installing Extensions.dll':raise OSError('locked file')
            with self.assertRaises(OSError):updater.install(root,m,channel='area52',download=lambda url,target,**kw:target.write_bytes(payload[url]),guard=lambda:None,report=report)
            for f in m['baseline']:self.assertEqual((root/f['path']).read_bytes(),b'old')
            self.assertFalse((root/'.bear-cave-launcher/pending.json').exists())

    def test_incomplete_unsafe_and_cross_realm_manifests(self):
        m,_=fixture()
        with self.assertRaises(ValueError):updater.validate_manifest(m,'ptr')
        for change in ('coverage','url','private','size','duplicate'):
            bad=copy.deepcopy(m)
            if change=='coverage':bad['components'].pop()
            if change=='url':bad['components'][0]['chunks'][0]['url']='https://other.example/file'
            if change=='private':bad['baseline'][0]['path']='WTF/Config.wtf';bad['components'][0]['files'][0]['path']='WTF/Config.wtf'
            if change=='size':bad['components'][0]['chunks'][0]['bytes']+=1
            if change=='duplicate':bad['components'][1]=copy.deepcopy(bad['components'][0])
            with self.subTest(change=change),self.assertRaises(ValueError):updater.validate_manifest(bad,'area52')

    def test_low_space_prevents_download(self):
        with test_directory() as root:
            m,_=fixture();self.client(root,m)
            with patch.object(updater.shutil,'disk_usage',return_value=shutil._ntuple_diskusage(1,1,0)),self.assertRaises(RuntimeError):
                updater.install(root,m,channel='area52',download=lambda *a,**k:self.fail('No download with insufficient space'),guard=lambda:None)

    def test_extra_archives_are_quarantined_and_recoverable(self):
        with test_directory() as root:
            m,payload=fixture();self.client(root,m)
            for name in ('extra-a.MPQ','extra-b.MPQ'):(root/'Data'/name).write_bytes(b'custom')
            def stop(message):
                if message=='Quarantining extra archive Data/extra-b.MPQ':raise KeyboardInterrupt()
            with self.assertRaises(KeyboardInterrupt):updater.install(root,m,channel='area52',download=lambda url,target,**kw:target.write_bytes(payload[url]),guard=lambda:None,report=stop)
            self.assertFalse((root/'Data/extra-a.MPQ').exists())
            updater.recover(root,guard=lambda:None,channel='area52')
            for name in ('extra-a.MPQ','extra-b.MPQ'):self.assertEqual((root/'Data'/name).read_bytes(),b'custom')
            self.assertEqual((root/'Ascension.exe').read_bytes(),b'old')
            updater.install(root,m,channel='area52',download=lambda url,target,**kw:target.write_bytes(payload[url]),guard=lambda:None)
            self.assertFalse((root/'Data/extra-a.MPQ').exists())
            backups=list((root/'.bear-cave-launcher/transactions').glob('*/backup/*'))
            self.assertTrue(any(p.read_bytes()==b'custom' for p in backups))

    def test_files_above_four_gib_are_representable(self):
        m,_=fixture();c=m['components'][2];size=4*1024**3+1
        c['bytes']=size;c['files'][0]['bytes']=size
        c['chunks']=[dict(asset=f'{c["id"]}-{n:03d}.bin',url=m['notes_url'].replace('PATCH-NOTES.md',f'{c["id"]}-{n:03d}.bin'),bytes=min(fullclient.CHUNK_LIMIT,size-n*fullclient.CHUNK_LIMIT),sha256='a'*64) for n in range(17)]
        updater.validate_manifest(m,'area52')

    def test_progress_does_not_finish_before_verification(self):
        with test_directory() as root:
            app=Application(root);app.operation='update'
            app.report_progress('Downloading',10,20);self.assertEqual(app.progress,37.5)
            app.report_progress('Downloading',20,20);self.assertEqual(app.progress,75)
            app.report_progress('Installing',4,4);self.assertEqual(app.progress,90)
            app.report_progress('Verifying',10,10);self.assertEqual(app.progress,99)

    def test_retry_space_counts_cached_chunks_and_preserves_backups(self):
        with test_directory() as root:
            m,payload=fixture();state=root/'state';cache=state/'downloads';cache.mkdir(parents=True)
            first=m['components'][0]['chunks'][0];(cache/first['sha256']).write_bytes(payload[first['url']])
            abandoned=state/'transactions'/('a'*32);(abandoned/'stage').mkdir(parents=True);(abandoned/'stage/temporary').write_bytes(b'data')
            committed=state/'transactions'/('b'*32);(committed/'backup').mkdir(parents=True);(committed/'backup/original').write_bytes(b'keep')
            (committed/'files.json').write_text('[]');(committed/'stage').mkdir()
            self.assertEqual(fullclient.prepare_retry(state,m['components']),first['bytes'])
            self.assertFalse(abandoned.exists());self.assertFalse((committed/'stage').exists())
            self.assertEqual((committed/'backup/original').read_bytes(),b'keep')
