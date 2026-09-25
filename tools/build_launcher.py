"""Build on the target OS; requires pip install pyinstaller==6.22.3."""
from pathlib import Path
import subprocess,sys,shutil
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from launcher import connection
# Deployment-only file: never commit the real address to source history.
connection_file=root/'connection.json'
if not connection_file.exists():connection_file=root/'local/connection.json'
connection_args=[]
if '--unconfigured' not in sys.argv:
    connection.load(root)
    connection_args=['--add-data',str(connection_file)+':.']
subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onedir','--windowed',
                '--icon',str(root/'ui/assets/bear-cave-app-icon.ico'),'--name','BearCaveLauncher','--paths',str(root/'tools'),
                '--add-data',str(root/'ui')+':ui',*connection_args,'--distpath',str(root/'dist/launcher'),
                '--workpath',str(root/'local/build'),'--specpath',str(root/'local'),str(root/'Launch.py')],cwd=root,check=True)
folder=root/'dist/launcher/BearCaveLauncher'
exe=folder/('BearCaveLauncher.exe'if sys.platform=='win32'else'BearCaveLauncher')
subprocess.run([str(exe),'--self-test'],check=True)
if sys.platform=='win32':
    (folder/'Start Compatibility Mode.cmd').write_text('@echo off\nstart "" "%~dp0BearCaveLauncher.exe" --compatibility\n',encoding='ascii')
archive=shutil.make_archive(str(root/'dist'/('BearCaveLauncher-'+sys.platform)),'zip',root_dir=folder.parent,base_dir=folder.name)
print('Built launcher bundle:',archive)
