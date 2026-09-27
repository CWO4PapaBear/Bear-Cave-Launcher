# PTR maintenance complete — client 0.2.14 and Launcher 0.3.0

The server activation is now complete. This supersedes the earlier activation-pending notice.

**Server changes installed**
- Full rune-state synchronization for characters that did not start as Death Knights, addressing client runes remaining spent after server recovery.
- Lootbot collection queue repaired to use supported Lua storage. Existing grey auto-sale integration is retained.
- Battle Pass daily-quest API error corrected.

Startup validation passed. Please test repeated rune use on Hero/Hybrid non-DK characters, Lootbot collection and grey selling, and Battle Pass quest XP. Gameplay confirmation is still needed.

**Client update 0.2.14-test.1 is available**
- Elekk texture repair, confirmed in game.
- Cat model/skin corrections and additional creature skin/reflection repairs. Please report remaining visual or animation problems.
- LFG/channel-notice Lua compatibility fix.
- Battle Pass closes with Escape.

**Launcher 0.3.0**
Automatic launcher updates are supported after installing 0.3.0. Native Windows uses Direct3D 9; Wine/Proton renderer settings are preserved. Older launcher users need the privately distributed 0.3.0 ZIP once; replace the entire launcher folder. Users already on 0.3.0 need no new ZIP.

Close WoW, open the launcher, select PTR, and Update. Players already on client 0.2.14 need no additional client update for this server activation. Main is unchanged.
