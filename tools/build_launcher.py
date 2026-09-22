"""Build on the target OS; requires pip install pyinstaller==6.22.3."""
from pathlib import Path
import subprocess,sys,shutil
root=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onedir','--windowed',
                '--name','BearCaveLauncher','--paths',str(root/'tools'),
                '--add-data',str(root/'ui')+':ui','--distpath',str(root/'dist/launcher'),
                '--workpath',str(root/'local/build'),'--specpath',str(root/'local'),str(root/'Launch.py')],cwd=root,check=True)
folder=root/'dist/launcher/BearCaveLauncher'
exe=folder/('BearCaveLauncher.exe'if sys.platform=='win32'else'BearCaveLauncher')
subprocess.run([str(exe),'--self-test'],check=True)
archive=shutil.make_archive(str(root/'dist'/('BearCaveLauncher-'+sys.platform)),'zip',root_dir=folder.parent,base_dir=folder.name)
print('Built launcher bundle:',archive)
