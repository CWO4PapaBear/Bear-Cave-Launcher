# Wine / Proton / Lutris compatibility test

The Windows package now includes an experimental native-control window. It uses
the same update validation, backups, realmlist configuration, recovery and game
launch backend as the main window. It needs no WebView2 or Python installation.
It is a simpler independent application window, not a browser page.

Replace the complete launcher folder using the privately distributed new ZIP.
Do not copy only the executable: the package now includes Tcl/Tk dependencies.
Keep the launcher and game in the same Wine prefix.

In Lutris or Steam launch options, pass `--compatibility` to
`BearCaveLauncher.exe`. For Wine, run:

```sh
wine BearCaveLauncher.exe --compatibility
```

Windows also has `Start Compatibility Mode.cmd` for testing. Existing Windows
launches retain the branded WebView2 interface. An unavailable WebView2 runtime
now stops with a useful error instead of displaying a nonfunctional preview.

Linux acceptance test: browse and save the folder containing Wow.exe; check and
apply the PTR update; confirm the configured realm; launch and log in; repeat
Check / Repair when already current. Check an interrupted-update recovery on a
disposable client copy. Report the Wine/Proton version and any error text.

Windows local tests and package checks do not establish Linux compatibility.
Real Wine/Proton testing is still required. No client patch channel or Discord
patch notes promotion is needed for this launcher-only package change. The
configured ZIP remains private; source publication does not distribute it.
