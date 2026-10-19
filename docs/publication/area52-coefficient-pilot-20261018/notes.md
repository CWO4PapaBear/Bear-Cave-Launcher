# Area 52 — client-based AP/SP coefficient pilot

- Exorcism: 14% Holy spell power + 24% attack power, across nine ranks.
- Consecration: 2.64% Holy spell power + 2.2% attack power per tick, across eight ranks.
- Flash Heal: 15.8964% bonus healing + 7.2% attack power, across eleven ranks. Existing echo behavior is preserved.
- Victory Rush: 45% attack power + 45% spell power, without the legacy AP-percent term being added again. Existing 10% maximum-health heal (8% against players) is preserved.
- Cone of Cold: 10.70% Frost spell power + 6.96% attack power, across eight ranks. This is the owner's approved fallback because the untouched client lacks an explicit formula and public rank references conflict.
- Flesh Hook, Frost Lich/Bone Chill and Spell Slinger retain their existing client-supported coefficients.

Each ability uses its own formula; there is no universal AP-to-SP ratio. Existing rank base values, normal talent modifiers, mitigation and level penalties remain in the native pipeline. No client download or tooltip/status-label changes are included. Existing Certified records are preserved; this scoped coefficient qualification does not certify gameplay or award new full-ability Verification.

Offline native build/unit, extracted native coefficient/regression checks, production-schema SQL lifecycle/rollback and package preflight qualify this correction. Gameplay testing remains with realm testers. These notes are prepared for publication only after owner activation and server readiness.
