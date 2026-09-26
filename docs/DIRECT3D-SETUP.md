# Windows Direct3D setup

The launcher configures native Windows clients to use `SET gxApi "D3D9"` during Check, Update and Play, even when no game component needs updating. This follows the Azuremyst crash test where switching the affected tester from OpenGL resolved the issue; it is not proof that every area crash has the same cause.

Only the renderer and existing realm settings are edited. Original configuration files are backed up under `.bear-cave-launcher/realm-backups`; unrelated settings and encoding are preserved. Missing WTF configuration is created. Running-game and linked-path guards still apply. Wine/Proton/native Linux retain their renderer settings.

Deployment requires the rebuilt launcher ZIP. Existing launcher executables do not self-update, and the managed client package deliberately excludes personal WTF settings. Distribute the new configured ZIP privately, then testers select their existing client and Check or Play with WoW closed. No new client patch or server restart is required. The ZIP includes deployment connection settings and is not committed to source.
