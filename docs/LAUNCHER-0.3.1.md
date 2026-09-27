# Launcher 0.3.1

Adds the PTR rune-recovery client repair required by PTR 0.2.15-test.1.
The updater patches two bytes in an exact, checksum-approved local Wow.exe;
it does not download or distribute a game executable. Unknown builds stop
with a useful checksum message before patch installation.

The executable participates in the same verified backup, interruption journal
and rollback transaction as addons and archives. Repeated updates are harmless.
Download manifests still cannot supply executables or arbitrary binary patches.
Manifest schema 2 prevents older launchers from silently omitting this repair.

Launcher 0.3.0 automatically upgrades on reopening. Earlier versions need the
new privately distributed ZIP once. Public self-update assets exclude connection
configuration and preserve the recipient's existing connection settings.

Validation: owner confirmed the two-byte repair resolves the reproduced rune
failure. Automated tests cover exact repair, unknown-build refusal, idempotence,
already-current archives, failure rollback, interruption recovery and manifest
requirements. Broader character and Wine/Proton testing remains welcome.
