"""Local-only browser shell for the Bear Cave PTR updater."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, os, secrets, shutil, subprocess, sys, threading
from . import updater, connection

ROOT=Path(__file__).resolve().parents[1]

class Application:
    def __init__(self,config_dir=None):
        self.directory=config_dir or (Path(os.getenv('LOCALAPPDATA') or Path.home()/'.config')/'BearCaveLauncher')
        self.directory.mkdir(parents=True,exist_ok=True)
        self.config=self.directory/'settings.json'
        self.client=updater.read_json(self.config).get('ptr_client','') if self.config.exists() else ''
        self.manifest=None;self.busy=False;self.message='Select your dedicated PTR client folder.'
        self.error='';self.changes=[];self.mutex=threading.Lock()
        self.folder_picker=None

    def status(self):
        return dict(client=self.client,busy=self.busy,message=self.message,error=self.error,
                    changes=self.changes,version=self.manifest['version'] if self.manifest else None)

    def report(self,text): self.message=text

    def select(self,value,internal=False):
        if self.busy and not internal: raise ValueError('Wait for the current operation')
        root=updater.client_root(value)
        marker=root/'.bear-cave-launcher/channel.json'
        if marker.exists() and updater.read_json(marker).get('channel')!='ptr':
            raise ValueError('That client belongs to another realm.')
        self.client=str(root);self.manifest=None;self.changes=[]
        updater.save_json(self.config,dict(ptr_client=self.client))
        self.message='PTR client selected. Check for updates.';self.error=''

    def start(self,action):
        with self.mutex:
            if self.busy: raise ValueError('An operation is already running')
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
                    manifest=updater.latest();parts=updater.changed(root,manifest)
                    self.manifest=manifest;self.changes=[dict(id=c['id'],bytes=c['bytes']) for c in parts]
                    self.message=f'{len(parts)} component(s) need updating.' if parts else 'Your PTR files match the published version.'
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
            if route not in ('api/browse','api/select','api/check','api/update','api/recover','api/play'):
                return self.respond(403,dict(error='Invalid launcher action'))
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=4096 or self.headers.get('Content-Type')!='application/json':
                    raise ValueError('Invalid request')
                data=json.loads(self.rfile.read(size))
                if route=='api/select':app.select(data['path'])
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
        if failed.is_set():raise RuntimeError('The desktop rendering engine did not initialize. Install or repair Microsoft Edge WebView2 Runtime on Windows, then retry.')
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)

if __name__=='__main__':main()
