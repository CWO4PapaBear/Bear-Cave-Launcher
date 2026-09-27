# PTR 0.2.15-test.1 — Rune recovery client fix

- Fixed Death Knight runes remaining unusable after their countdown finished on Hero characters using another active resource, such as mana. The client incorrectly skipped rune recovery unless Runic Power was active. The local gameplay retest passed after removing that gate.
- Launcher **0.3.1** applies the repair to the reviewed Wow.exe version and retains a backup. It changes only the rune-recovery gate; server ability eligibility, rune costs and cooldown calculations remain unchanged.
- Close WoW and reopen the launcher to receive its automatic update, then select **Check / Repair → Update PTR**. Launcher 0.3.0 can update itself. Older launchers without self-update need the latest privately distributed launcher ZIP.
- An unrecognized Wow.exe is left untouched. Send the displayed SHA256 to the administrator for review; do not replace it with a random executable.
- Includes the existing PTR 0.2.14 addon and texture updates. No additional server restart is required.

Please test several spend/recover cycles on Hero and Hybrid characters, plus native Death Knights. Report character, play style and ability if a problem remains. This update does not broadly remove class restrictions.
