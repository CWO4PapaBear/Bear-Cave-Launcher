# Area 52: rechargeable ability corrections

Area 52 now loads cast-charge metadata after its ability and Mystic Enchant catalogs are ready. Previously, a class-family filter skipped eligible abilities, leaving their casts unable to consume their intended charges.

- Purge: three charges, with one charge recovering every 12 seconds.
- Fear Ward: two charges, with one charge recovering every 20 seconds.
- The shared policy also covers eligible Shred, Crusader Strike, Angelic Feather and Oracle's Blessing ranks/dependencies. Existing Charge and Swiftmend charge behavior is preserved.
- Ranks of the same ability share their intended pool. Shred and Ironfur have independent pools and distinct client counters.
- Recharge timing, saved charges and login counter updates are covered by offline engineering checks. Existing ordinary cooldown interactions and Swiftmend's special exception remain intact.

This repair changes no Verified or Certified labels. Tester certification remains separate. After publication, close the game and use the Bear Cave Launcher to obtain the matching charge-counter data.

These notes describe the prepared payload; publication is gated on successful activation and server readiness. No DLL or new addon is included.
