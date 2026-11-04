# Uther's Tomb client-crash workaround

Prevents the reported client crash when approaching Uther's Tomb by disabling the additional Uther's Statue gameobject model. The statue remains spawned for Defiling Uther's Tomb; the tomb's built-in statue remains unchanged.

This is upstream PR11010's temporary database workaround, not a repair to the HD model's collision data. No client download, ability changes or verification-status changes. Offline database and package checks do not replace tester confirmation that this client crash is resolved.

Upstream: https://github.com/Conquest-of-AzerothCore/azerothcore-wotlk-coa/pull/11010
