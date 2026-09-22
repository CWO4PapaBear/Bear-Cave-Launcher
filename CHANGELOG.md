# Changelog

## 0.2.0-dev — 2026-09-22

- Add working PTR download/install/check/recovery engine and browser-based local launcher.
- Add Windows executable build and Windows/Linux CI packaging workflow.
- Verify component/file hashes, reject unsafe ZIP entries, retain backups, and recover partial installs.
- Keep Main disabled and account delivery disconnected; Play uses existing realmlist.
- Replace selected-realm text glyph with a CSS diamond.
- Add a source push helper that verifies the remote commit; milestone pushes are part of the standard workflow.


## 0.1.0-dev — 2026-09-22

- Add a realm-aware account-request form for planned backend-to-Discord webhook delivery; submission remains disabled until configured. No Discord membership will be required.
- Apply the supplied Bear Cave logo and its gold/blue visual theme to the launcher preview.
- Establish Main and PTR channels with disabled initial pointers.
- Add Bear Cave launcher visual preview with separate realm selection.
- Add allowlisted component packaging, file/archive checksums, read-only update planning and GitHub draft/publish tooling.
- Add Windows/Linux CI configuration and deployment/repository reconciliation documentation.
- Local Windows validation: six tests passed; real symlink test skipped because symlink creation permission was unavailable. GitHub Actions, remote publication and automatic client installation have not run.

This is a development foundation, not a released desktop updater.
