# Selective Area 52 creature-cache correction (prepared, unpublished)

The next launcher source candidate repairs the known Rumbling Earth-Heart (22313)
cache defect before Play. Only records whose cached flags/type are exactly 0/8
are invalidated, allowing the server to supply the correct creature information.
All other records, the WDB header and terminator are preserved byte-for-byte.

Scope: Area 52 channel only, Cache/WDB/<locale>/Area 52 - Free-Pick and Area-52.
Other realms and shared top-level caches are untouched. Missing, correct or
unrecognized target metadata is left alone. No DLL or server change is required.

Runs under the existing client update lock and closed-client guard. Each changed
file gets a verified, uniquely named adjacent creaturecache.wdb.backup-* copy.
Concurrent edits, unsafe linked paths, corrupt caches and write/readback failures
stop Play instead of clearing the cache. Retry is idempotent. Backups are private
local recovery files, never uploaded or included in the launcher release.

Offline qualification: synthetic cache fixtures and actual Play-flow tests;
full launcher unittest discovery with PYTHONPATH=tools;tests. This does not prove
in-game targeting after the server refresh. No installed client was modified by
this launcher preparation and no game was launched.

Launcher 0.3.10 / build 310 is prepared separately; see LAUNCHER-0.3.10.md.
Publication remains pending owner authorization. This source change does not itself deliver fixes to testers.
The independent upstream cache utility remains in PR #9857.
