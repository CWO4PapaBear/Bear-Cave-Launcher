from pathlib import Path
import sys,struct,json
sys.path.insert(0,'outputs/Adaptive_Auto_Attack/mod-adaptive-autoattack/tools')
from lib.mpq import MPQArchive
s=Path('outputs/Replacement_Model_Audit/Scan.py').read_text();exec(s[s.index('base=Path'):s.index('models,ms=dbc')])
models,ms=dbc(read('DBFilesClient/CreatureModelData.dbc')[0]);models={r[0]:ms(r[2]).lower().replace('.mdx','.m2') for r in models}
rows,ds=dbc(read('DBFilesClient/CreatureDisplayInfo.dbc')[0])
refpath=Path('D:/DML WOTLK Client Side/Ascension A52 Free Pick/ascension-live/ascension-live/Data/patch-M.MPQ')
with MPQArchive(refpath) as a:
 rr,ss=dbc(a.read_file('DBFilesClient/CreatureDisplayInfo.dbc'));ref={r[0]:(r[1],[ss(r[i]) for i in (6,7,8)]) for r in rr}
 rm,rs=dbc(a.read_file('DBFilesClient/CreatureModelData.dbc'));rm={r[0]:rs(r[2]).lower().replace('.mdx','.m2') for r in rm}
targets={3250:'Hamhock',10914:'Wooly Kodo',16975:'Gnarl'}
paths={models[r[1]] for r in rows if r[0] in targets};out=[]
for r in rows:
 path=models.get(r[1],'')
 if path not in paths:continue
 b,origin=read(path);n,o=struct.unpack_from('<II',b,80);types=[]
 for i in range(n):
  t,fl,ln,off=struct.unpack_from('<4I',b,o+i*16);types.append([t,b[off:off+ln].split(b'\0',1)[0].decode(errors='replace')])
 skins=[ds(r[i]) for i in (6,7,8)];reference=ref.get(r[0]);refmodel=rm.get(reference[0]) if reference else None
 out.append(dict(display=r[0],name=targets.get(r[0]),model=path,origin=origin,skins=skins,textures=types,reference=reference,referenceModel=refmodel))
for _,a in archives:a.close()
Path('outputs/Creature_Texture_Family_Repair/audit.json').write_text(json.dumps(out,indent=2))
print('Family displays',len(out))
print(json.dumps([r for r in out if r['name']],indent=2))
