# PTR 0.2.14-test.1 — Creature textures, chat and Battle Pass

- Fixed the missing armor skin and reflection textures on Great Blue Elekk and related armored Elekk. Verified in game.
- Corrected model assignments for 58 cat displays, including snow-leopard/panther and cougar/lioness skins. Eyes and facial details now align in local model previews. Please test movement and attacks in game.
- Restored source-matched secondary skins for 19 armored hawkstrider, Zuldrak golem and Lady Vashj displays, plus missing reflection textures for wild Elekk, deer and rabbits. In-game feedback requested.
- Added a compatibility fix for LFG/channel notices that otherwise trigger a ChatFrame format error.
- Battle Pass now closes with Escape.

## Launcher 0.3.0

- Supports automatic launcher updates after this version is installed.
- Applies Direct3D 9 on native Windows to address the reported Azuremyst rendering crashes; Wine/Proton renderer settings are preserved.
- Preserves the privately distributed connection configuration during launcher self-updates.
- Testers on older launcher versions need the newly distributed 0.3.0 ZIP once. Replace the entire old launcher folder; the game client folder stays separate. Users already on 0.3.0 do not need another ZIP.

Close WoW, open the launcher, select PTR and Update. The client patch is cumulative and preserves the Bear Cave login scene. Main is unchanged.

## Server maintenance — activated

The combined server activation is complete and startup checks passed. Non-DK rune readiness now receives a full server-state resynchronization; Lootbot uses supported queue storage; Battle Pass uses the supported daily-quest API. Grey auto-sale is retained. Please verify rune reuse, companion collection/grey selling, and ordinary/daily quest progression in game. These changes do not require another client download. Previous server image and source/Lua backups are retained.
