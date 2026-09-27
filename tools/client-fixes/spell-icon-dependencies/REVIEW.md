# Missing spell icon dependencies

The 0.2.18-test.1 cumulative patches contain spell/icon mappings referencing
`HeroAdvancement\Interface\Icons`, but omit their textures. The working development
client obtains these from an older locale patch that launcher-only installations
do not receive. Repair reinstalls the same incomplete payload.

Confirmed undead controls: Dominate Undead (891/899), Raise Undead (885), Dismiss
Undead (893), and Revive Undead (889). Undead Lore uses a stock-client icon.
Demon and dragonkin controls share the dependency issue.

`Build.py` adds every missing texture in that namespace referenced by SpellIconID
or ActiveIconID in the supplied Spell.dbc. Both reviewed cumulative archives
required 83 textures. It preserves all spell and icon mappings and every existing
archive entry, validates image decoding, checks archive readback, and rejects
conflicting existing texture content. No server change is required.

Use Python with Pillow and the existing `lib.mpq` reader/writer package available
through `--mpq-library`. Supply the reviewed source archive containing the exact
paths; do not substitute by filename or distribute the entire old patch.

```powershell
python Build.py --input current/patch-Z.MPQ --source reference/patch-enUS-4.MPQ --output staged/patch-Z.MPQ --mpq-library path/to/tools --report root-report.json
```

Repeat for `patch-enUS-Z.MPQ`. Use new output paths; this tool stages files only.
Generated archives and extracted artwork must remain outside source history.
The staged repair passed image decoding and complete archive-entry preservation.
In-game acceptance on the affected tester's client remains outstanding.
