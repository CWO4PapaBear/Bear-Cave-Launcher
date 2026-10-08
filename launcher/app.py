"""Local-only browser shell for the Bear Cave PTR updater."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, os, secrets, shutil, subprocess, sys, threading, webbrowser
from urllib.parse import urlsplit
from . import updater, connection, access, baseline

ROOT=Path(__file__).resolve().parents[1]

class Application:
    def __init__(self,config_dir=None):
        self.directory=config_dir or (Path(os.getenv('LOCALAPPDATA') or Path.home()/'.config')/'BearCaveLauncher')
        self.directory.mkdir(parents=True,exist_ok=True)
        self.baseline_stamp=None
        self.progress=0;self.progress_phase='Ready';self.operation=None
        self.config=self.directory/'settings.json'
        settings=updater.read_json(self.config) if self.config.exists() else {}
        self.channel=settings.get('channel','ptr')
        if self.channel not in ('ptr','area52'):self.channel='ptr'
        self.clients={key:settings.get(key+'_client','') for key in ('ptr','area52')}
        self.client=self.clients[self.channel]
        self.manifest=None;self.busy=False;self.message='Select a separate client folder for this realm.'
        self.error='';self.changes=[];self.mutex=threading.Lock()
        self.folder_picker=None
        self.launcher_updating=False
        self.scan=None

    def status(self):
        from .selfupdate import VERSION
        return dict(channel=self.channel,channel_ready=self.channel=='ptr' or self.area52_ready(),client=self.client,busy=self.busy,message=self.message,error=self.error,
                    launcher_updating=self.launcher_updating,changes=self.changes,version=self.manifest['version'] if self.manifest else None,
                    launcher_version=VERSION,discord_ready=bool(self.discord_url()),progress=self.progress,progress_phase=self.progress_phase)

    def prepare_launcher_update(self):
        self.launcher_updating=True;self.busy=True;self.operation='launcher-update'
        self.progress=0;self.progress_phase='Checking launcher'
        self.message='Checking for a launcher update...'

    def run_launcher_update(self, close):
        from . import selfupdate
        def worker():
            restart=False
            try:
                restart=selfupdate.startup(self.report,self.report_progress)
            finally:
                self.launcher_updating=False;self.busy=False
                if restart:
                    close()
                else:
                    self.progress=0;self.progress_phase='Ready'
                    if self.message=='Checking for a launcher update...':
                        self.message='Launcher ready.'
        threading.Thread(target=worker,daemon=True).start()

    def area52_ready(self):
        try:return bool(connection.load(ROOT,'area52'))
        except ValueError:return False

    def realm(self):
        return connection.load(ROOT) if self.channel=='ptr' else connection.load(ROOT,'area52')

    def configure_realm(self,root,state):
        if self.channel=='ptr':connection.configure(root,state,self.realm(),updater.ensure_closed)
        else:connection.configure(root,state,self.realm(),updater.ensure_closed,force_direct3d=False)

    def discord_url(self):
        path=ROOT/'config/account-discord.json'
        if not path.exists():return None
        url=updater.read_json(path).get(self.channel,'')
        if not url:return None
        parsed=urlsplit(url)
        import re
        if (parsed.scheme!='https' or parsed.username or parsed.password or parsed.port
                or parsed.query or parsed.fragment
                or not ((parsed.netloc=='discord.gg' and re.fullmatch(r'/[A-Za-z0-9-]+',parsed.path))
                        or (parsed.netloc=='discord.com' and re.fullmatch(r'/invite/[A-Za-z0-9-]+',parsed.path)))):
            raise ValueError('Invalid Discord invitation configuration')
        return url

    def open_client_download(self):
        if self.channel!='area52':raise ValueError('Base-client link is Area 52 only')
        if not webbrowser.open('https://discord.gg/RAkxswQ7Gx',new=2):raise RuntimeError('Could not open your browser')

    def open_discord(self):
        url=self.discord_url()
        if not url:raise ValueError('Discord invitation is not configured yet')
        if not webbrowser.open(url,new=2):raise RuntimeError('Could not open your browser')
        self.message='Discord opened. Contact the administrator there to request an account.'

    def account(self,action,data):
        with self.mutex:
            if self.busy:raise ValueError('Wait for the current operation')
            if self.channel!='area52':raise ValueError('Invitation enrollment is Area 52 only')
            url=access.service_url(ROOT)
            if not url:raise ValueError('Account access service is not configured yet')
            self.busy=True
        try:
            client=access.Client(self.directory,url)
            if action=='status' and not client.path.exists():raise ValueError('No enrollment has been started')
            return client.request(action,data)
        finally:
            self.busy=False

    def change_channel(self,channel):
        with self.mutex:
            if self.busy:raise ValueError('Wait for the current operation')
            if channel not in ('ptr','area52'):raise ValueError('Unknown realm channel')
            self.channel=channel;self.client=self.clients[channel]
            self.manifest=None;self.changes=[];self.error='';self.scan=None;self.baseline_stamp=None
            self.progress=0;self.progress_phase='Ready'
            self.message=('Select your dedicated PTR client folder.' if channel=='ptr' else
                          'Select your COACore client folder for Area 52.')
            self.save_settings()

    def save_settings(self):
        self.clients[self.channel]=self.client
        updater.save_json(self.config,dict(channel=self.channel,**{key+'_client':value for key,value in self.clients.items()}))

    def report(self,text): self.message=text

    def report_progress(self,phase,done,total):
        fraction=min(1,max(0,done/total)) if total else 1
        start,end=(0,99)
        if self.operation=='launcher-update':
            start,end={'Downloading launcher':(0,80),'Verifying launcher':(80,88),'Checking launcher':(88,96),'Restarting launcher':(96,100)}.get(phase,(0,0))
        if self.operation=='update':
            start,end={'Checking':(0,5),'Downloading':(0,75),'Installing':(75,90),'Verifying':(90,99)}.get(phase,(0,0))
        self.progress=max(self.progress,start+(end-start)*fraction)
        self.progress_phase=phase

    def select(self,value,internal=False):
        if self.busy and not internal: raise ValueError('Wait for the current operation')
        root=updater.client_root(value) if self.channel=='ptr' else Path(value).expanduser().resolve(strict=True)
        if self.channel=='area52' and (not root.is_dir() or not ((root/'Ascension.exe').is_file() or (root/'Data').is_dir())):
            raise ValueError('Select the dedicated Area 52 folder containing Ascension.exe')
        for channel,folder in self.clients.items():
            if channel!=self.channel and folder and root==Path(folder).resolve():
                raise ValueError('Each realm must use a separate client folder')
        marker=root/'.bear-cave-launcher/channel.json'
        if marker.exists() and updater.read_json(marker).get('channel')!=self.channel:
            raise ValueError('That client belongs to another realm.')
        self.client=str(root);self.manifest=None;self.changes=[];self.scan=None;self.baseline_stamp=None
        self.save_settings()
        self.message='Client folder saved for '+self.channel+'.';self.error=''

    def verify_baseline(self,root,fast=False):
        self.baseline_stamp=None
        if not fast:(self.directory/'area52-file-cache.json').unlink(missing_ok=True)
        cache=baseline.read_cache(self.directory/'area52-file-cache.json',root) if fast else None
        mismatches,stamp=baseline.compare(root,self.manifest['baseline'],self.report,lambda done,total:self.report_progress('Verifying',done,total),cache=cache)
        self.accept_scan(baseline.Scan(root,self.manifest,mismatches,stamp))
        updater.save_json(self.directory/'area52-verification.json',dict(version=self.manifest['version'],mismatches=mismatches))
        if mismatches:
            repaired={f['path'].lower() for c in self.manifest['components'] for f in c['files']}
            base=[m for m in mismatches if m['path'].lower() not in repaired]
            if self.manifest.get('schema')==4:base=[]
            self.message=f'{len(mismatches)} client baseline mismatch(es). '
            self.message+=('Update Area 52 to repair managed files. ' if len(base)!=len(mismatches) else '')
            self.message+=('Base-client files also differ; obtain the matching COACore client. ' if base else '')
            self.error='; '.join(m['path']+': '+m['reason'] for m in mismatches[:5])
        else:
            self.baseline_stamp=stamp
            self.message='Area 52 base client matches the tested baseline.'
            if self.changes:self.message+=' Install the pending Area 52 overlay update before playing.'
        return mismatches

    def valid_scan(self,root):
        return self.scan is not None and self.scan.valid(root,self.manifest)

    def accept_scan(self,scan):
        self.scan=scan
        if self.channel=='area52' and not scan.mismatches:
            baseline.save_cache(self.directory/'area52-file-cache.json',scan,self.manifest['baseline'])
        self.baseline_stamp=scan.stamp if not scan.mismatches else None

    def start(self,action):
        with self.mutex:
            if self.busy: raise ValueError('An operation is already running')
            if self.channel=='area52' and not self.area52_ready() and action!='browse':raise ValueError('Area 52 connection is not configured yet')
            if action not in ('browse','check','update','recover','play'): raise ValueError('Unknown action')
            root=updater.client_root(self.client,self.channel) if action!='browse' else None
            self.busy=True;self.error='';self.message='Working…'
            self.operation=action;self.progress=0;self.progress_phase='Preparing'
        def worker():
            try:
                if action=='browse':
                    self.message='Choose your PTR folder in the folder selection window…'
                    if not self.folder_picker:raise RuntimeError('Folder picker unavailable. You can still paste the folder path.')
                    chosen=self.folder_picker()
                    if chosen:self.select(chosen,internal=True)
                    else:self.message='Folder selection cancelled. Your saved folder is unchanged.'
                elif action=='check':
                    self.manifest=None;self.changes=[];self.message='Checking the published PTR channel…'
                    # Repair the connection even when no patch components need updating.
                    with updater.locked(root,self.channel) as state:
                        self.configure_realm(root,state)
                    manifest=updater.latest() if self.channel=='ptr' else updater.latest(self.channel)
                    if self.channel=='area52' and manifest.get('schema')==4:
                        self.manifest=manifest;self.changes=[]
                        mismatches=self.verify_baseline(root)
                        damaged={row['path'].lower() for row in mismatches}
                        self.changes=[dict(id=c['id'],bytes=c['bytes']) for c in manifest['components'] if any(f['path'].lower() in damaged for f in c['files'])]
                        if any(row['reason']=='unexpected archive' for row in mismatches):self.changes.append(dict(id='quarantine-extra-archives',bytes=0))
                        return
                    changes=updater.pending_changes(root,manifest) if self.channel=='ptr' else updater.pending_changes(root,manifest,self.channel)
                    self.manifest=manifest;self.changes=changes
                    self.message=f'{len(changes)} component(s) need updating.' if changes else 'Your client files match the published version.'
                    self.message+=(' PTR connection configured.' if self.channel=='ptr' else ' Area 52 connection configured.')
                    if self.channel=='area52' and self.manifest.get('schema') in (3,4):
                        self.verify_baseline(root)
                elif action=='update':
                    if not self.manifest: raise ValueError('Check for updates first')
                    realm=self.realm()
                    current=updater.latest() if self.channel=='ptr' else updater.latest(self.channel)
                    self.manifest=current
                    self.message=updater.install(root,self.manifest,report=self.report,channel=self.channel,progress=self.report_progress,scan=self.scan,verified=self.accept_scan);self.changes=[]
                    with updater.locked(root,self.channel) as state:
                        self.configure_realm(root,state)
                    self.message+=(' PTR connection configured.' if self.channel=='ptr' else ' Area 52 connection configured.')
                    if self.channel=='area52' and self.manifest.get('schema') in (3,4) and not self.valid_scan(root):
                        self.verify_baseline(root)
                elif action=='recover':
                    self.scan=None;self.baseline_stamp=None
                    (self.directory/'area52-file-cache.json').unlink(missing_ok=True)
                    self.message=updater.recover(root,report=self.report,channel=self.channel)
                else:
                    updater.ensure_closed()
                    self.manifest=updater.latest() if self.channel=='ptr' else updater.latest(self.channel)
                    if self.channel=='area52':
                        if not self.valid_scan(root):
                            self.verify_baseline(root,fast=True)
                        if self.scan.mismatches:
                            self.error='';self.operation='update';self.progress=0
                            self.message=updater.install(root,self.manifest,report=self.report,channel=self.channel,
                                progress=self.report_progress,scan=self.scan,verified=self.accept_scan)
                            self.changes=[]
                            if not self.valid_scan(root):
                                self.verify_baseline(root)
                            if self.scan.mismatches:raise ValueError('Client repair did not complete; try Check / Repair.')
                    else:
                        self.operation='update'
                        self.message=updater.install(root,self.manifest,report=self.report,channel=self.channel,progress=self.report_progress)
                        self.changes=[]
                    with updater.locked(root,self.channel) as state:
                        if (state/'pending.json').exists():raise ValueError('Recover interrupted changes before playing')
                        updater.ensure_closed()
                        self.configure_realm(root,state)
                        if self.channel=='area52' and not self.valid_scan(root):
                            raise ValueError('Client files changed after verification. Press Play to check again.')
                        self.progress_phase='Launching'
                        exe=root/('Ascension.exe' if self.channel=='area52' else 'Wow.exe')
                        command=[str(exe)] if os.name=='nt' else [shutil.which('wine') or 'wine',str(exe)]
                        subprocess.Popen(command,cwd=root)
                        self.scan=None;self.baseline_stamp=None
                        self.message='Game launched with the '+self.channel+' connection configured.'
            except updater.ChannelUnavailable as error:
                self.message=str(error)+' Realm connection configured; client verification is unavailable.'
            except Exception as error:
                self.scan=None;self.baseline_stamp=None
                self.error=str(error);self.message='Operation stopped. See the message below.'
            finally:
                if self.error:self.progress_phase='Needs attention'
                else:self.progress=100;self.progress_phase='Complete'
                self.busy=False
        threading.Thread(target=worker,daemon=True).start()

def create_server(app,port=0):
    token=secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass  # Session capability must not appear in logs.
        def respond(self,status,body,ctype='application/json'):
            if isinstance(body,dict): body=json.dumps(body).encode()
            self.send_response(status);self.send_header('Content-Type',ctype)
            self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store')
            self.send_header('Referrer-Policy','no-referrer');self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; form-action 'none'")
            self.end_headers();self.wfile.write(body)
        def route(self):
            host=f'127.0.0.1:{self.server.server_port}'
            if self.headers.get('Host')!=host: return None
            origin=self.headers.get('Origin')
            if origin and origin!='http://'+host: return None
            prefix='/'+token+'/'
            if not self.path.startswith(prefix): return None
            return self.path[len(prefix):]
        def do_GET(self):
            route=self.route()
            if route is None: return self.respond(403,dict(error='Invalid launcher session'))
            if route=='api/status': return self.respond(200,app.status())
            files={'':('preview.html','text/html; charset=utf-8'),
                   'assets/bear-cave-logo.png':('assets/bear-cave-logo.png','image/png'),
                   'runtime.js':('runtime.js','text/javascript; charset=utf-8')}
            if route not in files: return self.respond(404,dict(error='Not found'))
            name,ctype=files[route];body=(ROOT/'ui'/name).read_bytes()
            if route=='':body=body.replace(b'</html>',b'<script src="runtime.js"></script></html>')
            self.respond(200,body,ctype)
        def do_POST(self):
            route=self.route()
            if route not in ('api/base-client','api/discord','api/channel','api/browse','api/select','api/check','api/update','api/recover','api/play'):
                return self.respond(403,dict(error='Invalid launcher action'))
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=4096 or self.headers.get('Content-Type')!='application/json':
                    raise ValueError('Invalid request')
                data=json.loads(self.rfile.read(size))
                if app.launcher_updating:raise ValueError('Wait for the launcher update to finish')
                if route=='api/base-client':app.open_client_download()
                elif route=='api/discord':app.open_discord()
                elif route=='api/channel':app.change_channel(data['channel'])
                elif route=='api/select':app.select(data['path'])
                else:app.start(route.split('/')[-1])
                self.respond(200,app.status())
            except Exception as error:self.respond(400,dict(error=str(error)))
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    return server,f'http://127.0.0.1:{server.server_port}/{token}/'

def main(smoke_dir=None):
    import webview
    app=Application(smoke_dir)
    if not smoke_dir:app.prepare_launcher_update()
    server,url=create_server(app)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        class WindowControls:
            def fit_height(self, required, available, top, viewport):
                required, available, top = int(required), int(available), int(top)
                if not 200 <= available <= 10000 or not 0 < required <= 20000:
                    return
                height = min(available, max(640, required + max(0, window.height - int(viewport))))
                if height != window.height:
                    window.resize(window.width, height)
                y = max(top, min(window.y, top + available - height))
                if y != window.y:
                    window.move(window.x, y)
            def minimize(self): window.minimize()
            def close(self):
                if app.busy:
                    app.message='Please wait for the current operation to finish before closing the launcher.'
                    return False
                window.destroy()
                return True
        window=webview.create_window('The Bear Cave - PTR Launcher',url,width=1280,height=720,
                                     min_size=(1000,640),background_color='#071422',hidden=bool(smoke_dir),
                                     frameless=True,easy_drag=False,shadow=True,js_api=WindowControls())
        ready=threading.Event();failed=threading.Event();closed=threading.Event()
        window.events.loaded+=lambda:ready.set()
        if not smoke_dir:window.events.loaded+=lambda:app.run_launcher_update(window.destroy)
        window.events.closed+=lambda:closed.set()
        def startup_watch():
            if os.name == 'nt' and webview.renderer != 'edgechromium':
                failed.set();window.destroy()
                return
            if not ready.wait(30) and not closed.is_set():
                failed.set();window.destroy()
        def pick():
            selected=window.create_file_dialog(webview.FileDialog.FOLDER,directory=app.client or str(Path.home()))
            return selected[0] if selected else None
        app.folder_picker=pick
        def closing():
            if app.busy:
                app.message='Please wait for the current operation to finish before closing the launcher.'
                return False
        window.events.closing+=closing
        if smoke_dir:
            def loaded():
                result=window.evaluate_js("({title:document.title,browse:!!document.getElementById('client-browse'),play:!!document.querySelector('[data-action=play]')})")
                window.show()
                import time
                samples = []
                for _ in range(3):
                    time.sleep(1)
                    samples.append(window.evaluate_js("({height:innerHeight,available:screen.availHeight,mainOverflow:document.querySelector('main').scrollHeight-document.querySelector('main').clientHeight,navOverflow:document.querySelector('nav').scrollHeight-document.querySelector('nav').clientHeight})"))
                result['sizing'] = samples
                app.prepare_launcher_update()
                app.message='Updating launcher test';app.report_progress('Downloading launcher',50,100)
                time.sleep(1.2)
                result['launcher_update'] = window.evaluate_js("({disabled:[...document.querySelectorAll('button')].every(b=>b.disabled),title:document.getElementById('title').textContent,progress:document.getElementById('update-progress').getAttribute('aria-valuenow')})")
                app.launcher_updating=False;app.busy=False
                updater.save_json(smoke_dir/'desktop-smoke.json',result)
                window.destroy()
            window.events.loaded+=loaded
        webview.start(startup_watch,gui='edgechromium' if os.name=='nt' else None,debug=False,
                      storage_path=str(app.directory/'webview'),private_mode=True,
                      icon=str(ROOT/'ui/assets'/('bear-cave-app-icon.ico' if os.name=='nt' else 'bear-cave-app-icon.png')))
        if failed.is_set():raise RuntimeError('The required WebView2 engine did not initialize. Install or repair Microsoft Edge WebView2 on Windows. For Wine/Proton/Lutris, start BearCaveLauncher.exe with --compatibility to use native controls (experimental).')
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)

if __name__=='__main__':main()
