"""Local-only browser shell for the Bear Cave PTR updater."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, os, secrets, shutil, subprocess, sys, threading
from . import updater, connection, access

ROOT=Path(__file__).resolve().parents[1]

class Application:
    def __init__(self,config_dir=None):
        self.directory=config_dir or (Path(os.getenv('LOCALAPPDATA') or Path.home()/'.config')/'BearCaveLauncher')
        self.directory.mkdir(parents=True,exist_ok=True)
        self.config=self.directory/'settings.json'
        settings=updater.read_json(self.config) if self.config.exists() else {}
        self.channel=settings.get('channel','ptr')
        if self.channel not in ('ptr','area52'):self.channel='ptr'
        self.clients={key:settings.get(key+'_client','') for key in ('ptr','area52')}
        self.client=self.clients[self.channel]
        self.manifest=None;self.busy=False;self.message='Select your dedicated PTR client folder.'
        self.error='';self.changes=[];self.mutex=threading.Lock()
        self.folder_picker=None

    def status(self):
        from .selfupdate import VERSION
        return dict(channel=self.channel,channel_ready=self.channel=='ptr',client=self.client,busy=self.busy,message=self.message,error=self.error,
                    changes=self.changes,version=self.manifest['version'] if self.manifest else None,
                    launcher_version=VERSION,access_ready=bool(access.service_url(ROOT)))

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
            self.manifest=None;self.changes=[];self.error=''
            self.message=('Select your dedicated PTR client folder.' if channel=='ptr' else
                          'Area 52 private alpha distribution is being prepared. Downloads and play are not enabled yet.')
            self.save_settings()

    def save_settings(self):
        self.clients[self.channel]=self.client
        updater.save_json(self.config,dict(channel=self.channel,**{key+'_client':value for key,value in self.clients.items()}))

    def report(self,text): self.message=text

    def select(self,value,internal=False):
        if self.busy and not internal: raise ValueError('Wait for the current operation')
        root=updater.client_root(value) if self.channel=='ptr' else Path(value).expanduser().resolve(strict=True)
        if self.channel=='area52' and (not root.is_dir() or not (root/'Ascension.exe').is_file()):
            raise ValueError('Select the dedicated Area 52 folder containing Ascension.exe')
        for channel,folder in self.clients.items():
            if channel!=self.channel and folder and root==Path(folder).resolve():
                raise ValueError('Each realm must use a separate client folder')
        marker=root/'.bear-cave-launcher/channel.json'
        if marker.exists() and updater.read_json(marker).get('channel')!=self.channel:
            raise ValueError('That client belongs to another realm.')
        self.client=str(root);self.manifest=None;self.changes=[]
        self.save_settings()
        self.message='Client folder saved for '+self.channel+'.';self.error=''

    def start(self,action):
        with self.mutex:
            if self.busy: raise ValueError('An operation is already running')
            if self.channel!='ptr' and action!='browse':raise ValueError('Area 52 private alpha distribution is not enabled yet')
            if action not in ('browse','check','update','recover','play'): raise ValueError('Unknown action')
            root=updater.client_root(self.client) if action!='browse' else None
            self.busy=True;self.error='';self.message='Working…'
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
                    with updater.locked(root) as state:
                        connection.configure(root,state,connection.load(ROOT),updater.ensure_closed)
                    manifest=updater.latest();changes=updater.pending_changes(root,manifest)
                    self.manifest=manifest;self.changes=changes
                    self.message=f'{len(changes)} component(s) need updating.' if changes else 'Your PTR files match the published version.'
                    self.message+=' PTR connection configured.'
                elif action=='update':
                    if not self.manifest: raise ValueError('Check for updates first')
                    realm=connection.load(ROOT)
                    self.message=updater.install(root,self.manifest,report=self.report);self.changes=[]
                    with updater.locked(root) as state:
                        connection.configure(root,state,realm,updater.ensure_closed)
                    self.message+=' PTR connection configured.'
                elif action=='recover': self.message=updater.recover(root,report=self.report)
                else:
                    with updater.locked(root) as state:
                        if (state/'pending.json').exists(): raise ValueError('Recover interrupted changes before playing')
                        updater.ensure_closed()
                        connection.configure(root,state,connection.load(ROOT),updater.ensure_closed)
                        exe=root/'Wow.exe'
                        command=[str(exe)] if os.name=='nt' else [shutil.which('wine') or 'wine',str(exe)]
                        subprocess.Popen(command,cwd=root)
                        self.message='WoW launched with the PTR connection configured.'
            except Exception as error:
                self.error=str(error);self.message='Operation stopped. See the message below.'
            finally: self.busy=False
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
            if route not in ('api/enroll','api/account-status','api/channel','api/browse','api/select','api/check','api/update','api/recover','api/play'):
                return self.respond(403,dict(error='Invalid launcher action'))
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=4096 or self.headers.get('Content-Type')!='application/json':
                    raise ValueError('Invalid request')
                data=json.loads(self.rfile.read(size))
                if route in ('api/enroll','api/account-status'):
                    action='enroll' if route=='api/enroll' else 'status'
                    return self.respond(200,app.account(action,data))
                if route=='api/channel':app.change_channel(data['channel'])
                elif route=='api/select':app.select(data['path'])
                else:app.start(route.split('/')[-1])
                self.respond(200,app.status())
            except Exception as error:self.respond(400,dict(error=str(error)))
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    return server,f'http://127.0.0.1:{server.server_port}/{token}/'

def main(smoke_dir=None):
    import webview
    app=Application(smoke_dir);server,url=create_server(app)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        class WindowControls:
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
                result=window.evaluate_js("({title:document.title,browse:!!document.getElementById('client-browse'),update:!!document.querySelector('[data-action=update]')})")
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
