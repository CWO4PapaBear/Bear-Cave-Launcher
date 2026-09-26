"""Stage Battle Pass Escape registration without changing the client."""
from pathlib import Path
import argparse,hashlib,json

def patch(source):
    if b'local function BattlePass_RegisterEscape()' in source:return source
    if b'UISpecialFrames' in source:raise ValueError('Review existing Escape handling first')
    needle=b'            InitializeAddon()'
    if source.count(needle)!=1:raise ValueError('Unexpected Battle Pass initialization')
    updated=source.replace(needle,needle+b'\n            BattlePass_RegisterEscape()')
    block=b'''\n-- Register the main menu with the stock Escape handler after XML loads.\nlocal function BattlePass_RegisterEscape()\n    for _, name in ipairs(UISpecialFrames) do\n        if name == "BattlePassFrame" then return end\n    end\n    table.insert(UISpecialFrames, "BattlePassFrame")\nend\n\n'''
    pos=updated.index(b'local eventFrame = CreateFrame("Frame")')
    return updated[:pos]+block+updated[pos:]

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a fresh output directory')
    before=a.source.read_bytes();after=patch(before);a.output.mkdir(parents=True)
    (a.output/'before.lua').write_bytes(before);(a.output/'BattlePass.lua').write_bytes(after)
    (a.output/'manifest.json').write_text(json.dumps({'before':hashlib.sha256(before).hexdigest(),'after':hashlib.sha256(after).hexdigest()},indent=2))
    print('Staged only. Validate and install with client closed and original hash checked.')
