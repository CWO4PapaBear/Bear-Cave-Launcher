# Area 52 — talent login restoration and Power Word: Shield verification

- Assigned talents now restore their effects after logging out and back in; changing a talent is no longer required to recover them.
- Talent restoration still respects current point investment and independent grants, rejects stale higher ranks, and avoids repeatedly applying passive bonuses. This is a shared talent-system repair, not a blanket Verification award for all talents.

- All 14 ranks use the untouched Area 52 client's shield values: nominal base absorb from 44 at rank 1 to 2,230 at rank 14, a 30-second shield, and 23% base-mana cost before modifiers.
- Shield scaling is 21% spell power. Borrowed Time retains its separately defined healing-power addition; existing talent modifiers and PvP dampening remain in the native calculation.
- Grace can now trigger from Power Word: Shield, as its tooltip describes, while preserving its existing healing-spell triggers.
- Weakened Soul remains 15 seconds. Shield snapshotting, stronger-shield rejection, absorb depletion, overflow and reflection safeguards are preserved.
- Power Word: Shield's catalog entry and 14 rank tooltips become VERIFIED after activation. Existing CERTIFIED entries remain unchanged. Verification is engineering review; live tester Certification remains separate.

Close the owner's local client before activation. This package includes that client's Shield data and labels, the server correction, status reconciliation, and guarded Grace SQL with rollback. It includes no DLL changes and no tester launcher distribution. Separate selectable Mystic Enchants, including Final Shield, Dominant Word: Shield and Healing Shields, remain queued for their own reviews and receive no status promotion.

Native build/unit, focused extracted native handler checks, production-schema SQL lifecycle tests, staged client archive readback, and temporary client rollback fixtures qualify this scope. Mocked adapters do not constitute live gameplay testing. Publication is prepared for delivery only after owner activation and server readiness.
