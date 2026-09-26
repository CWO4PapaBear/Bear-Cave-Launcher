---
name: bear-cave-login-art
description: Inspect supplied BLP artwork and build, validate, install, or roll back Bear Cave WoW 3.3.5a login-screen branding. Use when changing the pre-login background or logo, not in-game addon portraits or launcher artwork.
---

# Login artwork integration

**Observed compatibility failure, September 26:** The local client rejected this GlueXML candidate with `Logs/GlueXML.log: GlueXML is modified or corrupt`. The original locale Z archive was restored and hash-verified. The Lua-overlay implementation below is retained for diagnosis and reproducibility, not as a working solution for this executable. Do not reinstall it on this client. Investigate an asset-only logo/model replacement that leaves signed GlueXML unchanged. BLP backgrounds alone do not replace the stock 3D login scene; that route needs a compatible model/scene asset. Do not claim this first pass works or distribute it through the launcher.

Use the actual client as the baseline. Login UI is GlueXML, before addons load; an ordinary addon cannot replace it. Preserve authentication and realm configuration. Keep extracted Blizzard sources, BLPs, MPQs, executable files and personal client data out of source history. Publish original scripts and this guide only. Local installation does not publish a launcher release.

## Current route: asset-only scene (local test)

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
