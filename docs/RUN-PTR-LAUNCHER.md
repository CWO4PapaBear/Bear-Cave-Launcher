# Run the first PTR launcher

## Windows

Extract `BearCaveLauncher-win32.zip` into a launcher folder. Keep `BearCaveLauncher.exe` together with its `_internal` directory; do not distribute the EXE by itself. Run the EXE. It opens an independent Bear Cave desktop window with no browser tab or console. Windows requires Microsoft Edge WebView2 Runtime. Closing the window stops its local service; closing is blocked while an operation is running. The desktop renderer still needs user acceptance testing: the agent session could compile/import it but returned a WebView2 initialization error during its hidden render test.

Click **Browse…** and select a dedicated PTR client folder containing `Wow.exe`, or paste its full path and click Save Folder. A saved folder triggers an update check on subsequent launches. A new selection triggers a check immediately. Check / Repair rechecks all managed file hashes; Update PTR downloads and installs changed components. Updates require a button click in this first version. Main is disabled.

Until the first PTR package and channel pointer are published, a check reports that updates are unavailable. That is expected; it does not modify the client. Configured builds set the PTR realmlist automatically on Update and Play; see PTR-CONNECTION.md.

Close every running WoW process before updating. Original files remain in `.bear-cave-launcher/transactions/<id>/backup` inside the PTR client. Interrupted installs retain a journal; Recover restores original files. Do not delete that folder while recovery is pending. Backups are not automatically pruned yet.

Backup filenames are shortened hashes to support long Windows addon paths. Each transaction's `files.json` records the original paths. Use Recover for interrupted updates rather than copying hashed backup filenames into the game folder.

## Linux/Wine

Install `requirements.txt` and a supported Linux WebView backend (for example `pip install PySide6`), then run `python3 Launch.py` from the source checkout (Python 3.12+), or use the Linux bundle after the GitHub build workflow has completed. Select the Linux path to the PTR client. Play uses `wine` from PATH and the existing Wine environment. A custom Wine prefix can be set with `WINEPREFIX` when launching. The Windows build has been packaged locally; the Linux binary and live Wine launch have not been verified here.

## First-release limitations

- Pulls updates from the configured GitHub PTR pointer on launch/check; it is not a remote push daemon.
- Downloads complete changed components, not binary MPQ deltas.
- Does not delete retired addon files, migrate a full client, clear caches or self-update the launcher.
- Does not authenticate private GitHub downloads. The tester channel must be public or backed by a future authenticated download service.
- Release trust is HTTPS plus hashes pinned in the GitHub channel; independent signed manifests are not implemented.
- Account request UI is present but disconnected; no webhook secret is in the launcher.
- No updates have been published solely by building the launcher.

## Wide desktop window and app icon

The launcher opens at 1280 by 720 with a custom gold edge and no operating-system title bar. Drag the top Bear Cave strip to move it; use the top-right minimize and close buttons. Closing is blocked while an operation is running. The main content pane can scroll on smaller windows or for long error messages; the overall window does not scroll.

The circular bear-paw medallion is embedded as the Windows executable icon and window icon. Close the previous launcher and extract the complete new ZIP to use this version. Existing client folder preferences are retained.
