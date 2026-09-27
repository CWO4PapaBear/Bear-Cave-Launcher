from pathlib import Path
import sys,json,hashlib,io
from PIL import Image
sys.path.insert(0,'outputs/Adaptive_Auto_Attack/mod-adaptive-autoattack/tools')
from lib.mpq import MPQArchive
H=Path(__file__).resolve().parent;r=json.loads((H/'sweep.json').read_text());missing={m['texture'].lower():m['texture'] for row in r['issues'] for m in row['missing'] if m.get('texture','').lower().endswith('.blp')};found={}
root=Path('D:/DML WOTLK Client Side/Ascension A52 Free Pick/ascension-live/ascension-live/Data')
# Discovery only: multiple different source bytes are ambiguous and remain excluded.
for p in root.rglob('*.MPQ'):
 try:
  with MPQArchive(p) as a:
   names=a.read_file('(listfile)').decode(errors='replace').splitlines()
   for n in names:
    if n.lower() not in missing:continue
    b=a.read_file(n);Image.open(io.BytesIO(b)).load();sha=hashlib.sha256(b).hexdigest();found.setdefault(n.lower(),{})[sha]={'path':missing[n.lower()],'source':str(p),'sourcePath':n,'sha256':sha,'bytes':len(b)}
 except Exception:continue
safe=[next(iter(v.values())) for v in found.values() if len(v)==1];ambiguous=[k for k,v in found.items() if len(v)>1]
(H/'broad-dependencies.json').write_text(json.dumps({'exactUnique':safe,'ambiguous':ambiguous,'missingPathsSearched':len(missing),'unresolvedPaths':sorted(set(missing)-set(found))},indent=2));print('Searched',len(missing),'unique exact source files',len(safe),'bytes',sum(x['bytes'] for x in safe),'ambiguous',len(ambiguous));print([v['path'] for v in safe][:30])
