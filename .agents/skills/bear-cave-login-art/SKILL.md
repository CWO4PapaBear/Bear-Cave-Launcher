---
name: bear-cave-login-art
description: Inspect supplied BLP artwork and build, validate, install, or roll back Bear Cave WoW 3.3.5a login-screen branding. Use when changing the pre-login background or logo, not in-game addon portraits or launcher artwork.
---

# Login artwork integration

**Observed compatibility failure, September 26:** The local client rejected this GlueXML candidate with `Logs/GlueXML.log: GlueXML is modified or corrupt`. The original locale Z archive was restored and hash-verified. The Lua-overlay implementation below is retained for diagnosis and reproducibility, not as a working solution for this executable. Do not reinstall it on this client. Investigate an asset-only logo/model replacement that leaves signed GlueXML unchanged. BLP backgrounds alone do not replace the stock 3D login scene; that route needs a compatible model/scene asset. Do not claim this first pass works or distribute it through the launcher.

Use the actual client as the baseline. Login UI is GlueXML, before addons load; an ordinary addon cannot replace it. Preserve authentication and realm configuration. Keep extracted Blizzard sources, BLPs, MPQs, executable files and personal client data out of source history. Publish original scripts and this guide only. Local installation does not publish a launcher release.

## Current route: asset-only scene (local test)

### Original animation route (September 26 local test)

`animated_scene.py` generates original geometry and bone translation tracks from the working static scene. It uses no stock animation arrays or particles: 56 soft textured snow quads in two 28-bone sections loop over 12 seconds. The optional banner uses a 6-by-5 cloth grid with the upper slanted attachment line pinned and a separate fixed wood/rope layer. Each section has its own bone palette, capped at 53 entries. The original soft snow sprite is a generated 16x16 TGA; the supplied BLP cloth/frame remain local.

Exact build commands, after defining `$py` and `$argsList` in step 1:

```powershell
$assetScript='outputs/Bear-Cave-Launcher/.agents/skills/bear-cave-login-art/scripts/asset_patch.py'
$customArgs=$argsList.Clone()
$customArgs[5]='outputs/Bear_Cave_Login_Art/custom-snow'
& $py outputs/Bear-Cave-Launcher/.agents/skills/bear-cave-login-art/scripts/animated_scene.py
& $py $assetScript build @customArgs --previous-build outputs/Bear_Cave_Login_Art/camera-fit/manifest.json --animation snow
Get-Process Wow -ErrorAction SilentlyContinue
& $py $assetScript install @customArgs
# Recovery only, with WoW closed:
& $py $assetScript rollback @customArgs
```

The snow candidate was installed locally with a verified backup. In-client animation acceptance is pending. No launcher channel was promoted. A separate `custom-banner` candidate was built against camera-fit using `--animation banner` before snow installation; it is NOT installed. After snow acceptance, build a fresh banner work directory against the actually installed `custom-snow/manifest.json`; do not install the older candidate over changed archive bytes. Example:

```powershell
$bannerArgs=$argsList.Clone()
$bannerArgs[5]='outputs/Bear_Cave_Login_Art/custom-banner-after-snow'
& $py $assetScript build @bannerArgs --previous-build outputs/Bear_Cave_Login_Art/custom-snow/manifest.json --animation banner
# Only after snow acceptance and client closure:
& $py $assetScript install @bannerArgs
```

Validate track array bounds, timestamp ordering, vertex weights, skin indices, section palettes and every archive entry. Installation additionally regenerates the original animated model and requires exact model/skin equality. This does not establish renderer compatibility: test opening login, snow motion, looping, aspect/framing, control usability, then cloth alignment and waving. The previous donor-snow route remains blocked. Keep local art testing separate from launcher Update/Repair, which restores the published archive.

### Banner and doubled snowfall test

The owner accepted the initial snow in-game. The next locally installed candidate doubles the count from 28 to 56 while preserving flake size and speed. Two independent snow sections keep each bone palette below the renderer limit. It also enables the fixed stick/rope frame and waving cloth. Exact commands used, with the step-1 variables:

```powershell
$bannerArgs=$argsList.Clone()
$bannerArgs[5]='outputs/Bear_Cave_Login_Art/banner-double-snow'
& $py $assetScript build @bannerArgs --previous-build outputs/Bear_Cave_Login_Art/custom-snow/manifest.json --animation banner
& $py $assetScript install @bannerArgs
# Recovery only, with WoW closed:
& $py $assetScript rollback @bannerArgs
```

Model validation and complete MPQ read-back passed; installation preserved the accepted snow archive as `banner-double-snow/original.MPQ`. Banner framing, attachments and motion await in-game review. No tester release was published. After banner acceptance, the requested final layer is localized warm flickering light on the cave wall, suggesting a fire inside the cave. Keep this localized rather than changing the whole background brightness; preserve the validated snow and banner. This firelight layer is not implemented yet.

### Grounded banner and wind revision

The next local review requested 112 flakes, varied speed and swirling movement. The generator now uses 12-, 6- and 4-second fall periods; every fourth flake has a wider sinusoidal path. Tracks sample at 125ms with explicit offscreen wrap keys. Four 28-bone snow sections preserve palette limits. Cloth waves twice per 12-second loop with greater amplitude. The assembly is lowered 3.15 model units, and supplied `foreground_snowbank_512x256.blp` covers the base. Cloth depth remains in front of the post throughout its motion; render sections are frame, cloth, snowbank, then snow.

Installed locally with complete archive read-back and backup; visual acceptance pending. Commands:

```powershell
$windArgs=$argsList.Clone()
$windArgs[5]='outputs/Bear_Cave_Login_Art/grounded-banner-snow'
& $py outputs/Bear-Cave-Launcher/.agents/skills/bear-cave-login-art/scripts/animated_scene.py
& $py $assetScript build @windArgs --previous-build outputs/Bear_Cave_Login_Art/banner-double-snow/manifest.json --animation banner
& $py $assetScript install @windArgs
# Recovery only:
& $py $assetScript rollback @windArgs
```

Check post/snowbank grounding at the actual resolution, cloth overlap, snowfall density and smooth motion before adding the final cave firelight. Firelight remains pending. No launcher client channel promotion.

### Camera correction and original snowfall revision

**Failed in-client test:** The original-snow revision caused ERROR #132 / ACCESS_VIOLATION at 0x006844E8 on build 12340. It was rolled back to camera-fit and its build/install paths are blocked. The commands below are historical reproduction notes, not approval to reinstall it. Retained-array and index checks did not prove renderer compatibility. The exact defective relationship is not yet diagnosed. Do not use this prototype in a launcher release or imply that original snow is working. Static camera-fit remains installed pending confirmation of reopening/framing.

The first static scene was reported severely zoomed in. Its ten-unit camera distance was replaced with a diagonal-FOV-derived fit for the owner's 1920x1080 viewport. The subsequent snowfall request uses `snow_scene.py`: retain the stock camera, bone/sequence animation and the single skin batch referencing SNOWFLAKE01B.BLP; append a static textured background plane sized for that camera. Only two batches render (background and snow). Dragon/scenery batches, particle emitters, sound events, lights and attachments are disabled. Original model bytes remain local and are not committed. In-game snow and framing acceptance remains required.

Revision commands, after defining `$py` and `$argsList` below:

```powershell
$assetScript='outputs/Bear-Cave-Launcher/.agents/skills/bear-cave-login-art/scripts/asset_patch.py'
$snowArgs=$argsList.Clone()
$snowArgs[5]='outputs/Bear_Cave_Login_Art/original-snow'
& $py $assetScript build @snowArgs --previous-build outputs/Bear_Cave_Login_Art/camera-fit/manifest.json --original-snow
& $py $assetScript install @snowArgs
# Restore the preceding camera-fit revision (only when recovery is needed):
& $py $assetScript rollback @snowArgs
```

`--previous-build` must identify the manifest whose `after` hash matches the currently installed archive, not merely the newest folder name. The recorded sequence was asset-only -> camera-fit -> original-snow; each revision has its own original.MPQ. After a rollback, reassess installed hashes before proceeding. For a clean baseline without existing Bear Cave assets, omit `--previous-build`. The snowfall donor is the local patch-enUS-2.MPQ Northrend model/skin. If its layout or snow batch differs, reconcile rather than weakening the assertions.

Use `asset_patch.py` for the successor, not the blocked GlueXML installer described in the historical procedure below. It writes an original MD20 version 264 textured quad with one camera, bone and Stand sequence plus matching external SKIN geometry. This replaces both native login model paths and the WotLK logo texture. No script or executable changes are made. Geometry is unlit/unfogged and two-sided; background UVs trim the prepared edge padding. Model framing is static and still requires in-client aspect/camera review; unlike the rejected Lua layout, it does not dynamically recalculate crop on resize.

After setting `$py` and `$argsList` as in step 1:

```powershell
$assetScript='outputs/Bear-Cave-Launcher/.agents/skills/bear-cave-login-art/scripts/asset_patch.py'
$assetArgs=$argsList.Clone()
$assetArgs[5]='outputs/Bear_Cave_Login_Art/asset-only'
& $py outputs/Bear-Cave-Launcher/.agents/skills/bear-cave-login-art/scripts/build_scene.py
& $py $assetScript build @assetArgs
Get-Process Wow -ErrorAction SilentlyContinue
& $py $assetScript install @assetArgs
# Roll back this asset-only revision, with WoW closed:
& $py $assetScript rollback @assetArgs
```

Do not run install and rollback together; rollback is the recovery command. Build checks array strides/bounds and skin indices, confirms no signed AccountLogin.lua entry, and reads back every old and new MPQ entry. Installation verifies hashes and saves `asset-only/original.MPQ`. The `asset-only/payload/Interface` hierarchy is ready for Ladik's MPQ Editor: add this hierarchy preserving its internal paths into a **copy** of the existing managed locale Z archive, not a blank replacement that discards other patches. Do not import the payload parent directory itself as part of the virtual path. Inspect the resulting six asset entries and verify all previous records. Preserve the loose source-art folder.

Format references used: [wowdev/pywowlib M2 definitions](https://github.com/wowdev/pywowlib/blob/master/file_formats/m2_format.py) and [SKIN definitions](https://github.com/wowdev/pywowlib/blob/master/file_formats/skin_format.py). These informed the original writer; no third-party model files are committed. A successful binary validator does not establish renderer compatibility. Check the actual login screen before distributing; retain the previous patch for recovery.

## 1. Set exact paths and inspect

The following PowerShell commands were used for the September 26, 2026 Bear Cave client. Set the working directory first. For another installation, change these values deliberately.

```powershell
Set-Location 'C:/Users/danie/Documents/Codex/2026-09-12/can'
$env:PYTHONUTF8='1'
$py='C:/Users/danie/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$script='outputs/Bear-Cave-Launcher/.agents/skills/bear-cave-login-art/scripts/login_art.py'
$argsList=@('--client','D:/DML WOTLK Client Side/WoW-3.3.5a - HeroFreePick - Classic Test','--art','D:/DML WOTLK Client Side/WoW-3.3.5a - HeroFreePick - Classic Test/Data/enUS/Patch-enUS-bc.mpq','--work','outputs/Bear_Cave_Login_Art','--mpq-tools','outputs/Adaptive_Auto_Attack/mod-adaptive-autoattack/tools')
Get-Item $argsList[3]
& $py $script inspect @argsList
```

Dependencies: Python standard library, Pillow for BLP previews, and the existing `lib/mpq.py` plus `lib/pkware.py` at the supplied tools path. This guide does not install a different MPQ library silently. Inspection writes `inspection.json`, extracted AccountLogin Lua by archive, and preview PNGs. Open the preview PNGs with `view_image`; this is format conversion for inspection, not image generation.

The original `Patch-enUS-bc.mpq` is a **directory**, not an MPQ. Its BLP filenames are not client virtual paths. Never overwrite or rename that source directory. Inventory both global Data and locale archives. Check for loose overrides as well. Inspect AccountLogin.lua/XML from the winning client archive before building. In the reviewed client, locale `patch-enUS-3.MPQ` supplies AccountLogin.lua; the current locale `patch-enUS-Z.MPQ` has no GlueXML override. Do not assume this on a different client.

## 2. Choose composition

Reviewed artwork: `background_full_2048x1024.blp` and transparent `logo_SEPARATE_1024x512.blp`. Other supplied cloth/frame/snowbank assets are not required for this static first pass; filenames alone do not make animated cloth.

`scripts/login-art.lua` creates a noninteractive BACKGROUND texture on AccountLoginUI and replaces AccountLoginLogo. It crops the supplied horizontal edge padding (U=.0625 through .9375), then uses aspect-preserving cover coordinates. The logo is 320x160 at top-left (20,-20). Review 4:3, 16:9 and ultrawide framing. Adjust UV crop rather than stretching images. Existing stock login controls retain their anchors and handlers.

## 3. Build and verify archive preservation

```powershell
& $py $script build @argsList
& $py outputs/Bear-Cave-Launcher/.agents/skills/bear-cave-login-art/scripts/test_login_art.py
```

Build extracts stock AccountLogin.lua, removes only its two old model-loading calls, then appends original branding wrappers around OnLoad/OnShow. It retains all remaining login logic. It merges three entries into a candidate copy of the locale Z patch: AccountLogin.lua, BearCave/Background.blp and BearCave/Logo.blp. All existing named archive entries are read back and byte-verified. `build.json` records before/after archive hashes. Verify listfile completeness against occupied hash entries before rebuilding unfamiliar archives; missing names must not be silently dropped. Inspect the generated Lua diff before installation. The test uses `lupa.lua51` from workspace `work/regalia/libs` and verifies syntax, stock callbacks, aspect ratios and reuse of the background texture.

## 4. Install a local test

Confirm WoW is completely closed and obtain filesystem access to the exact target archive if required. No server restart or SQL changes are involved.

```powershell
Get-Process Wow -ErrorAction SilentlyContinue
& $py $script install @argsList
```

Installer rejects a running WoW process or changed archive hashes, saves `patch-enUS-Z.before.MPQ`, and verifies installed bytes. Keep that backup outside the client. Never overwrite an existing backup from a previous test. Open WoW through the usual launcher Play action without running Update/Repair: the published channel does not yet contain this local test.

Acceptance: logo transparency and proportions; no old dragon behind the artwork; readable account/password fields; typing/tab navigation; login/cancel/options; resolution changes; return to login after logout. Do not claim functional acceptance from mocked tests. Some client executables reject modified GlueXML integrity; if startup rejects the patch, roll back and investigate the client's supported customization path. Do not patch the executable or disable checks as an unrequested workaround.

## 5. Roll back

Close WoW, then run:

```powershell
& $py $script rollback @argsList
```

Rollback refuses unrelated archive changes and restores the verified original bytes. If the launcher updated the archive in between, reconcile rather than overwrite newer work.

## 6. Publish only after the requested local review

Source scripts/skill go to Bear-Cave-Launcher main under normal milestone rules. Read AGENTS.md, fetch/reconcile origin/main, run relevant checks, commit explicit paths, push without force, verify remote SHA. Art changes stay local until release authorization. To distribute, copy the approved archive into a fresh cumulative launcher candidate, retaining every prior component and excluding personal data. Use `tools/package.py` with a new version/config and patch notes, then `tools/release.py draft`, then `publish` (which downloads and hash-verifies remote assets). Commit/push channels/ptr.json only after verification; check the PTR Discord patch-notes workflow. Treat source push, release assets, channel promotion and server activation as distinct statuses.
