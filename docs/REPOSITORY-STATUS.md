# Repository audit — 2026-09-22

This is a snapshot, not a claim that development is synchronized automatically.

| Repository/folder | Observed status |
| --- | --- |
| HeroFreePick-GitHub | Local HEAD `fb04b0c` (2026-09-18), two commits ahead of the freshly queried remote `ab2d7c2`. Modified and untracked files remain. |
| More-Minions | Local HEAD `12c3514` (2026-09-17), many modified and untracked client/server files. No configured upstream branch. |
| More-Minions-publish | Local HEAD and cached origin/main `4320447` (2026-09-17). Clean publish checkout. Fresh remote verification failed authentication; current GitHub tip is unknown. |
| Bear-Cave-Launcher | Newly prepared local foundation. Remote repository existence/access was not established; no upload or release performed. |

Recent development is distributed across local patch directories, including Hero_Hybrid_Spellbook, Hero_Live_Unit_Frames, Hero_Integrated_Resources, minion capture/channel fixes and upcoming-patch staging. These are not automatically copied into source repositories or published when a test server activates a build.

## Reconciliation queue

1. Establish each running server image, its source hashes, and the installed addon hashes as the reviewed baseline.
2. Move Hero Advancement, spellbook and resource/UI integrations into HeroFreePick, preserving Classic behavior and excluding unrelated tester-only modules.
3. Move minion capture, independent companions, command controls, family mappings and generic companion telemetry into More Minions. Keep the optional HeroFreePick bridge separate.
4. Preserve each deployed fix when consolidating; do not overwrite live source from older staging copies. Exclude backups, credentials, exported databases, proprietary archives and personal settings.
5. Run each repository's required tests/build and review its changelog and diff before separate commits/pushes.
6. Package an exact approved PTR client snapshot after that reconciliation. Main remains untouched.

This launcher setup does not claim to have completed that consolidation or to have pushed the existing module changes.
