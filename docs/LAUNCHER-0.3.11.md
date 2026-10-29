# Launcher 0.3.11 — Area 52 connection recovery

Corrects the old Area 52 public login endpoint following the network outage.
Close and reopen the launcher, allow its update, then select Area 52 and Play.
Existing client files, cache repair, TLS handling, custom endpoints and local
connections are preserved. No server restart is involved.

The update retains private connection files and resolves only an exact old
Area 52 endpoint through release-bundled endpoint-migrations.json. Real addresses
remain outside source history. PTR and nonmatching overrides are unchanged.
Build with --unconfigured --endpoint-migrations local/endpoint-migrations.json.
The signed-by-hash release inventory covers the migration file with the executable.
