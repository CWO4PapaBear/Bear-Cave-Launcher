# The Bear Cave Launcher

First working PTR updater for Windows and Linux/Wine. A Windows bundle is built locally; GitHub source publication and the first client release are separate steps. Run `Launch.py` or the packaged executable for the connected interface. Opening `ui/preview.html` directly remains a visual preview.

## Realm channels

| Channel | Realm | Purpose |
| --- | --- | --- |
| main | The Bear Cave | Approved stable releases |
| ptr | The Bear Cave — PTR | Current HeroFreePick / More Minions test server |

The two channels are disabled until an approved package is published. They must use separate client directories. Changing future hosting addresses must not require rebuilding the launcher: server addresses and download locations belong in channel/release configuration. No address is assumed in this foundation.

## Ready now

- `ui/preview.html`: local Bear Cave visual direction, with interactive realm selection; update/play buttons are deliberately disabled.
- `tools/package.py`: allowlisted component ZIPs, file and archive SHA-256 checksums, source-change checks and versioned release manifest. Does not modify the source client.
- `tools/inspect_update.py`: read-only local file comparison; lists changed components.
- `tools/release.py`: authenticated GitHub CLI publishing, draft review, remote asset verification, explicit release publication and local channel promotion.
- `channels/main.json` and `channels/ptr.json`: independently promoted release pointers. Never use GitHub's global `/latest` release for realm discovery.
- Python tests plus Windows/Linux GitHub Actions checks.

## Working PTR updater

`launcher/updater.py` verifies the GitHub PTR pointer and release hashes, downloads changed components, verifies archive contents, checks that WoW is closed, backs up originals, and journals each update for rollback/recovery. `Launch.py` displays the themed UI in an independent desktop window with an internal, session-protected localhost service; no browser tab or public web service is opened. Main remains disabled. See [run instructions](docs/RUN-PTR-LAUNCHER.md).

The initial release does not remove obsolete files, self-update or provide independently signed manifests. It does not implement account submission. The Linux binary/Wine launch still needs testing. Never reuse your Main client as the PTR folder; the current UI asks you to supply a separate copy.


HeroFreePick and More Minions retain independent source repositories. This repository combines reviewed client artifacts for a realm; it does not absorb their source history. Auto-Attack-Forever stays optional and PTR-specific; it is absent from the example package until its dependencies are separately reviewed. No proprietary client archives or personal configuration are committed here.

See [publishing instructions](docs/PUBLISHING.md), [repository audit](docs/REPOSITORY-STATUS.md), and [rollout plan](docs/ROLLOUT.md).

## Local checks

```powershell
python -m unittest discover -s tests -v
```

Open `ui/preview.html` in a browser for the design preview.

Automatic PTR realm configuration is applied by configured launcher builds; see [connection setup](docs/PTR-CONNECTION.md). Older launcher executables must be replaced once.


## Area 52 private alpha preparation

The Area 52 sidebar channel and separate folder settings are implemented. Its download, repair, recovery and Play actions remain disabled until its client distribution is ready. Existing PTR operations are unchanged. The compatibility UI has not yet gained Area 52 enrollment controls; use the standard Windows UI for this staged feature.

A deployment-only `access.json` (or `local/access.json`) may contain `{"channel":"area52","url":"https://YOUR_HOST"}`. Without that configuration, invitation submission stays disabled. Never place GitHub tokens or database credentials in the launcher. Enrollment credentials are protected with Windows DPAPI before network submission. Private access-service implementation is maintained separately in `CWO4PapaBear/Area52-FreePick-Client`. No public service, new launcher binary or Area 52 release assets have been activated.
