# Area 52 — Charge consumption and recharge

- Charge ranks 2 and 3 now spend their charges instead of allowing unlimited chaining.
- These ranks have two charges, with one charge recovering every 16 seconds. An empty pool prevents another cast until a charge returns.
- Both ranks share the same pool, so changing ranks does not reset the available charges.
- Rank 1 keeps its normal cooldown. The deployed Warrior stance Rage-retention fix is preserved.
- Existing Verified and Certified labels are unchanged; this is a scoped engineering repair.

Native build/unit and source checks passed. Offline native consumption/recharge checks and 13,244 metadata/isolation cases passed. Live tester certification remains separate.
