# Launcher 0.3.2

Adds rune-recovery repair support for the exact Warmane-sourced executable
reported by a tester. The launcher verifies the original file, changes only the
two reviewed rune-check bytes, verifies the resulting hash and retains a backup.
Other executable modifications are preserved. Unknown builds remain blocked.

Close WoW and reopen launcher 0.3.0 or newer to receive the launcher update, then
choose Check / Repair and Update PTR. Existing connection settings are preserved.
Older launchers without self-update require the privately distributed ZIP.

This release does not change server code, game content or the realm address.
The public self-update archive contains launcher code only, without connection
configuration or a game executable. Exact-file static verification and updater
tests passed; gameplay verification on the tester's client remains pending.
