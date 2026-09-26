# Launcher self-updates: 0.3.0

Distribute the newly rebuilt configured `dist/BearCaveLauncher-win32.zip` once. Testers extract the entire folder, replacing their old launcher, and keep using the same client folder. Existing launchers cannot acquire this feature through the game patch channel. The new ZIP includes the Windows Direct3D setup.

On subsequent starts the Windows executable checks `channels/launcher-win32.json` before opening the main window. Only a strictly newer numeric build is eligible. HTTPS download, exact GitHub release URL, size, SHA-256, archive paths and embedded build identity are verified. The public update contains no connection settings. The updater copies those from the existing launcher and leaves the separate per-user settings/client folder untouched. Linux-native builds skip this Windows update channel; the Windows executable under Wine uses the same helper and preserves compatibility-mode startup (Wine testing remains required).

The helper runs outside both old and replacement installation folders. It waits for the old process to exit, renames the existing folder into a retained backup, installs the candidate, and runs its packaged self-test before restarting. A failed check or replacement restores the previous folder. A successful packaged self-test is not proof of every UI/game interaction. UI runtime failures after restart may require manual recovery.

Offline checks and invalid downloads leave the current version available. An existing handoff lock prevents parallel workers. Failed checks are recorded in `%LOCALAPPDATA%/BearCaveLauncher/launcher-update.log`; stages/backups are retained beside the launcher as `bcu-<id>`. If interrupted during replacement, inspect that directory: `previous` contains the old installation. With launcher processes closed, restore that folder to the original launcher path. Do not delete backup directories while a helper is active. A stale `BearCaveLauncher.update-lock` can be removed only after confirming no helper is running. `--skip-launcher-update` bypasses a faulty channel for manual recovery. No elevation is requested: install the launcher in a user-writable folder.

## Publishing the next launcher build

Increment both VERSION and BUILD in `launcher/selfupdate.py`. Run all tests, build the configured ZIP, then build the public code-only update. Keep deployment `connection.json` out of GitHub and release assets. Source and release notes must be pushed to main before creating the release tag. The personal configured ZIP stays privately distributed.

```powershell
python -m unittest discover -s tests -q
```

```powershell
python tools/build_launcher.py
```

```powershell
python tools/package_launcher_update.py
```

Create `launcher-<VERSION>` as a draft with `BearCaveLauncher-update-win32.zip` from `dist/launcher-<VERSION>`. Download the uploaded ZIP and verify its SHA-256 against `channel.json`, then publish the release. Only after successful verification copy that channel.json into `channels/launcher-win32.json`, commit, push main and verify the remote commit. The game channel `channels/ptr.json` remains unchanged. Never replace an existing published asset with different bytes; increment the version/build instead.

Rollback promotion requires a new higher build containing the corrected/previous code; lower channel builds are intentionally ignored. The original private installer ZIP and each update backup remain manual recovery options.

Validation: 35 unit tests (one existing platform skip), packaged self-test, and local Windows integration checks covering process wait, real directory replacement, candidate self-test, rollback after an invalid executable, connection-file preservation and compatibility-mode restart arguments. Final UI launch was intercepted in the integration harness; Linux/Wine execution remains unverified.
