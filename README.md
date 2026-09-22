# The Bear Cave Launcher

Initial foundation for a Windows and Linux/Wine tester launcher. **No launcher binary or automatic client installer has been released.** The visual preview is not a connected application.

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

## Next implementation milestone

Build the actual desktop app and install engine: persisted separate client roots, Windows and Linux/Wine process checks, staged downloads, checksum verification, safe archive extraction, atomic per-file replacement with a persistent recovery journal, failed-install rollback, owned-file removal, realm configuration, and play integration. Hashes protect file integrity; launcher/manifest signing and trust-key handling remain to be designed before unattended installation. Do not treat this foundation as an operational updater.

Main and PTR must reject reuse of the same or nested client paths, including aliases and symlinks. Never overwrite WTF, SavedVariables, screenshots, accounts, unrelated addons or the game executable. Do not clear user caches wholesale. Deletions must be restricted to files recorded in a prior successful launcher install.

HeroFreePick and More Minions retain independent source repositories. This repository combines reviewed client artifacts for a realm; it does not absorb their source history. Auto-Attack-Forever stays optional and PTR-specific; it is absent from the example package until its dependencies are separately reviewed. No proprietary client archives or personal configuration are committed here.

See [publishing instructions](docs/PUBLISHING.md), [repository audit](docs/REPOSITORY-STATUS.md), and [rollout plan](docs/ROLLOUT.md).

## Local checks

```powershell
python -m unittest discover -s tests -v
```

Open `ui/preview.html` in a browser for the design preview.
