# Launcher 0.3.10 — selective targeting-cache repair

Prepared for tester distribution; not published or installed.

- Before Area 52 Play, repair the confirmed stale Rumbling Earth-Heart creature
  record that can prevent Tab targeting. Other creatures and realm caches remain
  unchanged; there is no full-cache clear.
- Preserve a verified local backup before a change. Correct or missing records
  need no repair. Repeated runs are safe.
- Preserve existing launcher certificate handling, efficient client verification,
  connection settings and compatibility mode.

Candidate identity: 0.3.10 / build 310. Source branch:
`fix/area52-selective-creature-cache`.

Build independently with:

```powershell
python tools/build_launcher.py --unconfigured --output dist/candidate-0.3.10
python tools/package_launcher_update.py --source dist/candidate-0.3.10/launcher/BearCaveLauncher --output dist/launcher-0.3.10
```

Use the existing pinned build dependencies. The public update contains code/UI
and runtime only; private connection/access files are excluded. The updater
preserves testers' existing connection configuration. Candidate channel.json is
staged beside the update archive; the repository's live channel pointer is not
changed during preparation.

Offline checks cover source regressions, packaged runtime startup, selective
repair on synthetic caches, archive integrity and the actual updater's extraction
contract. They do not establish live in-game targeting acceptance or delivery.
Publication still requires approval, source push, release upload/readback and
launcher-feed promotion. No Discord announcement has been sent.
