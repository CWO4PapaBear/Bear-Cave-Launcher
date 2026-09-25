# PTR 0.2.8-test.1 — Bear Cave merger

- Adds the client data and addons for the now-active Bear Cave-to-PTR merger: custom heirlooms and vendor items, Return/Retreat travel, transmogrification, Custom Login controls, and Battle Pass integration.
- Includes the Return/Retreat trainer interface and remapped travel spells, preserving existing PTR abilities.
- Preserves the previously released Hero Advancement, portraits, hybrid spellbook, pet improvements, Auto-Attack-Forever, bag sorting, and stock-client creature display crash fix.
- Local testing verified login, heirloom grants, and bag grants. Please report issues with travel trainers, vendors, transmogrification, loot pets, and other newly imported features.
- Generated AzerothChatter messages have been disabled on PTR. Normal player chat remains available.
- Battle Pass item/reward revisions are planned separately; this update does not claim that work is complete.

Close WoW, select PTR in the launcher, and choose **Check for updates**, then **Update**. This is a cumulative client update; no replacement launcher executable is required. Main is unchanged.

If existing item or NPC descriptions still show old values, close WoW and remove only these files from `Cache/WDB/enUS` in your PTR client: `itemcache.wdb`, `itemnamecache.wdb`, `creaturecache.wdb`, `gameobjectcache.wdb`, and `npccache.wdb`. They are rebuilt by the game. Keep your `WTF` settings and realmlist.

This release contains patches and addons, not a full game client. Private full-client distribution remains a separate planned feature.
