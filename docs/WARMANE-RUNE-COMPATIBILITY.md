# Additional executable supported by rune recovery repair

The owner supplied a tester executable reported as originating from Warmane.
Support applies only to this exact file, not every Warmane distribution.

- Original size: 7,699,456 bytes.
- Original SHA-256: `bf644876709c591acc17c0da8cdf1814edcc9f1e6bc109a8c0d5c38c79dc953c`.
- Patched SHA-256: `0d1cce504f8ee236719897bf7433a27cba9e275e6d26ef57367bec4f455128d9`.
- File offset: `0x327EA4`; replace `75 5A` with `90 90`.
- Required instruction context: `83 FB 06 75 5A 8B 1D 88 43 C2 00`.

Static comparison found the same PE section layout and the same 8 KiB code window
around this check, except for the two repair bytes in the already-patched local
reference. Other executable differences remain untouched. The original and final
whole-file hashes are checked; unknown builds remain rejected.

Validation includes a read-only, in-memory patch comparison of the supplied file,
exact two-byte diff, repeat-call idempotence, synthetic updater backup/install tests,
and output-hash rejection tests. The supplied executable was not launched. This
review establishes compatibility with this repair, not the provenance or safety of
the whole executable. In-game testing on the tester's client remains required.

No game executable is included in source or launcher release assets. Existing
installed launcher builds require a launcher executable update to gain this support;
a client-content channel update alone does not change the repair code.
