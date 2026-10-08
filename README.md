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


## Area 52 alpha channel

Area 52 has independent client-folder settings and a separate public update feed in CWO4PapaBear/Area52-FreePick-Client. Launcher 0.3.7 supports schema-4 full baseline repair: every listed file must have complete, hash-verified chunk downloads. Runtime files, large game archives, required UI and content data can be repaired. Extra MPQs are quarantined in verified transaction backups. Personal settings, caches and optional addons are excluded. Existing PTR ZIP manifests retain their original restrictions. Release assets and channel promotion are separate from source publication.

The footer progress bar tracks download bytes, installation and final verification; errors retain the incomplete state. Large repairs require free space for downloads, staged files and backups, checked before download. Verified download chunks are retained for retry; incomplete or corrupt chunks are downloaded again. The existing Recover action rolls back interrupted installation, including quarantined files. Source baseline changes require a separately reviewed client release; the launcher never follows the upstream PTR feed automatically.

Local builds can include local/connection-area52.json using tools/build_launcher.py --area52-local. This deployment configuration is excluded from source and public update bundles. The local test endpoint is not a tester deployment address. PTR and Area 52 cannot share a client folder. Area 52 launches Ascension.exe and does not apply PTR executable repairs or renderer settings. Use the standard Windows UI for Area 52.
## Current account-request flow

The active launcher UI opens the Discord invitation in `config/account-discord.json` for account requests. PTR and Area 52 currently share the same community. Account enrollment/password entry is not exposed by the launcher HTTP API. The invitation-service implementation is retained for future deployment; Discord is the current account workflow. The invite configuration is included in packaged launcher builds.

Area 52 defaults to the existing PTR connection host on port 3725 when no explicit Area 52 configuration exists. This allows automatic launcher updates to enable the realm without redistributing deployment settings. Explicit local overrides take priority.


## Launcher 0.3.8 flow

Choose the realm and client folder, then press **Play**. It retrieves the current channel, checks/repairs the client and launches. Check/Repair and Recover remain under Troubleshooting in the WebView launcher. Area 52 full-baseline verification is reused within the session only while the root, manifest and file metadata match; launching, recovery, failures and folder/channel changes invalidate it. Installed files remain hash-verified. PTR retains its component-level checks.

Self-update checks now start after the window opens. Controls stay disabled during the update, the existing bar displays download/verification progress, and the replacement launcher opens automatically. Versions older than 0.3.8 still use their old silent updater for the transition to 0.3.8.

Verification: 91 automated tests passed (one platform-specific skip); packaged executable self-test passed; desktop smoke verified Play, stable content height with no panel overflow, disabled controls during self-update and 40% displayed progress for the test download. Public update archive extraction/identity checks passed. A real tester upgrade remains user acceptance.
