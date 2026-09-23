# Publishing the first launcher foundation and client packages

## One-time repository setup

Create an **empty** `CWO4PapaBear/Bear-Cave-Launcher` repository. A public release download channel avoids distributing GitHub credentials to testers; if downloads must remain private, implement an authenticated distribution service first. Repository creation and visibility have not been performed by these tools.

In this directory, push the local source commit after the repository exists:

```powershell
git push -u origin main
```

If Git is not on PATH, use your installed Git executable. This project does not depend on the publishing computer's particular installation path.

Install GitHub CLI and authenticate on the **publisher's** computer:

```powershell
gh auth login
```

Never put a publisher token in the launcher or the manifest.

## Package a reviewed client snapshot

Copy `config/ptr-package.example.json` into ignored `local/ptr-package.json`. Review its exact addon list, replace the server-build placeholder with the approved build image, and set the version. The example is not yet a complete audited tester distribution. Close WoW while packaging. Include only distributable assets you have permission to distribute.

```powershell
python tools/package.py --client "D:/Path/To/PTR Client" --config local/ptr-package.json --notes local/PATCH-NOTES.md --output dist/ptr-0.1.0-test.1
```

Each addon/component is separately downloadable. A modified MPQ currently requires downloading that full component, not a binary delta. Large components must remain below GitHub's 2 GiB-per-asset limit. ZIPs live in Release assets, not Git history.

## Upload a draft

Push the current launcher source commit first, so its release tag can resolve. Then:

```powershell
python tools/release.py draft --package dist/ptr-0.1.0-test.1
```

The release remains a draft. Review files, verify the exact package on a spare client, and coordinate its required server deployment before promotion.

## Publish and promote PTR

```powershell
python tools/release.py publish --package dist/ptr-0.1.0-test.1
```

This verifies downloaded GitHub assets against local checksums, publishes the release and updates **only** the local PTR pointer. Then review, commit and push:

Verified downloads are retained under ignored `local/release-review-*` folders for inspection. Publisher output is decoded as UTF-8 so emoji patch notes work on Windows.

```powershell
git add channels/ptr.json
git commit -m "Promote reviewed PTR client release"
git push
```

PTR releases are prereleases. Main requires a separately built/reviewed `main` package and an explicit main-pointer commit. Neither channel follows `/releases/latest`; the future launcher reads `channels/<channel>.json` from the configured repository branch. For rollback, restore the pointer to a previous compatible release; client-side downgrade/rollback execution remains unimplemented.

Publishing a release does not deploy the game server. Coordinate those two actions to keep server/client spell definitions compatible.

References: [GitHub releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases), [release API](https://docs.github.com/en/rest/releases/releases).
