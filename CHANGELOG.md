## 0.3.3 local candidate (not promoted)

- Added independent Area 52 updates, client selection and Ascension.exe launch, with a COACore base-client Discord link.
- Account requests open Bear Cave Discord. Enrollment endpoints are inactive.
- Local desktop smoke test passed; 68 tests passed with one skipped. Tester channel remains unchanged.

## Unreleased � Discord account requests

- Request Account on Discord opens the shared community invite in the default browser for both PTR and Area 52.
- Removed the account form from the active launcher UI and disconnected enrollment endpoints. Invitation-service code remains inactive for future use.

## Unreleased � Area 52 private alpha preparation

- Added a separate Area 52 - Free Pick Alpha Dev channel with independent folder settings; distribution actions remain disabled until its release feed is prepared.
- Added invitation enrollment and account status integration, enabled only when the Area 52 HTTPS access service is configured. Windows protects the retained request credential with DPAPI. No email is required.
- PTR updates retain their existing feed and behavior. No launcher binary or client assets are published by this source change.

## Pending release � automatic PTR connection

- Configure realm files and saved realm overrides automatically after Update and before Play.
- Back up originals and preserve unrelated settings.
- Supply the deployment address outside Git history; configured package still exposes it to recipients.
- Requires a new launcher download; client-only updates cannot update old launcher executables.

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

- Launcher height automatically grows to fit channel content and messages, bounded by available screen height; scrolling remains available when the screen cannot fit the content.

- Correct content-height measurement and native window-frame allowance so automatic sizing stops at content rather than filling the screen.

- Replace the broken Area 52 sidebar separator with a plain dash.
