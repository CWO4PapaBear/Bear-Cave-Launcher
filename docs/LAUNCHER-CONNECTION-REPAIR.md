# Launcher connection repair — September 25, 2026

Check / Repair now configures the PTR connection even when all client patches already match. Previously only Update and Play wrote the realmlist, while the Update button was unavailable for an already-current client.

The configured build repairs locale realmlists, an existing root realmlist, and an existing WTF/Config.wtf realm override. It keeps backups and preserves unrelated settings. WoW must be closed. Missing bundled connection settings or write failures are displayed as errors rather than reported as success.

Distribute the newly rebuilt private `dist/BearCaveLauncher-win32.zip` to testers for this launcher behavior change. Client patch releases do not replace their launcher executable. The server endpoint remains in the ignored deployment configuration and private ZIP, not in repository source or public release assets.

The build's packaged self-test now exercises Check / Repair against an already-current synthetic client and verifies all three connection locations without network access or launching WoW. Source regression tests cover the same case.

The reported failure on the earlier September 25 ZIP has not been reproduced on the tester's computer. The Check / Repair gap is confirmed in source; it does not establish whether that tester also encountered a separate issue during Update or Play.
