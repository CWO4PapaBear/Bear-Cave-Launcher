from pathlib import Path
import json,hashlib,shutil,subprocess,datetime
H=Path(__file__).resolve().parent;client=Path('D:/DML WOTLK Client Side/WoW-3.3.5a - HeroFreePick - Classic Test')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def closed():
 p=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '^wow(?:-|$)' }).Count"],capture_output=True,text=True,check=True)
 assert p.stdout.strip()=='0','Close WoW before installation'
closed();report=json.loads((H/'report.json').read_text());files=report['archives']
for r in files:assert sha(client/r['path'])==r['before'] and sha(H/'candidate'/r['path'])==r['after'],'Client/candidate changed; rebuild rather than overwrite'
backup=H/('backup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
for r in files:
 p=backup/r['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(client/r['path'],p);assert sha(p)==r['before']
closed()
try:
 for r in files:shutil.copyfile(H/'candidate'/r['path'],client/r['path']);assert sha(client/r['path'])==r['after']
except Exception:
 for r in files:shutil.copyfile(backup/r['path'],client/r['path'])
 raise
(H/'installed.json').write_text(json.dumps({'status':'installed-local-visual-test-required','backup':str(backup),'files':files},indent=2))
print('LOCAL TEXTURE TEST INSTALLED. Backups verified. No server change or launcher publication.')
