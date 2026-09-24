## PTR 0.2.6-test.1

Combat-preserved Hero Advancement drafts, tested Auto-Attack Forever melee fallback/form/indicator fixes, ranged preference and minimap settings, and cumulative healing-tooltip corrections. Broader bear animation testing remains open.

## PTR client 0.2.2-test.1

Publish the reviewed current PTR managed client: portrait/pet controls, tap-Shift and resolved blue-value tooltips, Hybrid equipment tooltip correction, and updated Patch-Z archives. Record current activated server image including equipment access, Auto Attack and repeated-login fixes. Exclude personal layouts and provenance JSON. See docs/PTR-0.2.2-test.1.md.

# Changelog

## 0.2.0-dev — 2026-09-22

- Switch to a standalone desktop window with native folder selection and no browser tab/console. Windows requires WebView2. Build and non-visual checks passed; desktop rendering failed to initialize in the agent session and needs user verification.
- Add Browse with a native folder picker; validates the selected PTR folder and preserves the saved selection on cancellation.
- Add working PTR download/install/check/recovery engine and browser-based local launcher.
- Add Windows executable build and Windows/Linux CI packaging workflow.
- Verify component/file hashes, reject unsafe ZIP entries, retain backups, and recover partial installs.
- Keep Main disabled and account delivery disconnected; Play uses existing realmlist.
- Replace selected-realm text glyph with a CSS diamond.
- Add a source push helper that verifies the remote commit; milestone pushes are part of the standard workflow.
- Validation: 14 local tests passed, one symlink test skipped; full seven-component candidate installed and verified in a disposable fixture. Windows bundle self-test passed. GitHub publication and live-client acceptance remain separate.


## 0.1.0-dev — 2026-09-22

- Add a realm-aware account-request form for planned backend-to-Discord webhook delivery; submission remains disabled until configured. No Discord membership will be required.
- Apply the supplied Bear Cave logo and its gold/blue visual theme to the launcher preview.
- Establish Main and PTR channels with disabled initial pointers.
- Add Bear Cave launcher visual preview with separate realm selection.
- Add allowlisted component packaging, file/archive checksums, read-only update planning and GitHub draft/publish tooling.
- Add Windows/Linux CI configuration and deployment/repository reconciliation documentation.
- Local Windows validation: six tests passed; real symlink test skipped because symlink creation permission was unavailable. GitHub Actions, remote publication and automatic client installation have not run.

This is a development foundation, not a released desktop updater.
# PTR 0.2.3-test.1

Publish the tested More Minions stable bridge with the original classic controls, family-specific stable icons, and Beast-only happiness displays. Undead and Demon stabling confirmed by the owner. Cumulative package contains 916 managed files matching the tested owner client; no Main or launcher executable changes. Prior-release upgrade, repeat-install and private-file preservation checks passed. See docs/PTR-0.2.3-test.1.md for tester instructions and remaining validation.
