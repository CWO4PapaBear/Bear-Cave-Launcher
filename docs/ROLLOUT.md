# Rollout checkpoints

1. **Foundation (current):** separate Main/PTR channels, package tooling, read-only comparison, GitHub draft/promotion scripts and Bear Cave visual preview.
2. **Desktop updater:** Windows and Linux/Wine builds; select existing client folders; download staging, checksum verification, process locks, persistent rollback journal, managed-file ownership, interrupted-update recovery and repair. Design manifest signing and launcher self-update trust before automatic installation.
3. **Private test:** two disposable client copies; exercise corrupt downloads, wrong channel, linked directories, unknown files, active WoW, permission failure, interrupted installs, stale version and compatible rollback. Verify WTF and unrelated addons unchanged.
4. **PTR release:** reconcile current client modules, create initial release, deploy compatible server version, distribute launcher once. Testers thereafter receive published PTR updates through the launcher.
5. **Main:** publish a separate approved baseline. Main and PTR never share their client root or follow the same release pointer.
6. **Hosting move:** use independent configurable Main and PTR realm addresses plus download endpoints. Confirm future hosting's connectivity before changing the selected channel configuration. GitHub hosts packages; it does not host world/auth servers.

No background updater, periodic job, game launch, server restart or GitHub publication has been enabled by the foundation.
