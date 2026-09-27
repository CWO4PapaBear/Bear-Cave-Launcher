# Battle Pass spin client integration

Source for the tested production animation and minimal addon integration patches.
Interface 30300 / Lua 5.1. Asset hashes identify the reviewed release payload;
extracted textures and audio are not committed to source history.

Requires the active server Battle Pass spin integration and durable claim tables.
It uses CSMH responses 6 (saved result) and 7 (Claim All continuation), and request
4 for delivery after the reveal/hold/flight. Requests 2/3 include `spin-v1` so the
server can refuse claims from an older addon. No GM test commands are included.

The animation sends one delivery request after 12.35 seconds. Claim All waits
until animation completion before requesting the next spin. Reward selection,
eligibility and duplicate protection are server-authoritative.

Release: PTR 0.2.16-test.1. Owner gameplay test complete; full server build,
isolated SQL apply/rollback and Lua animation/claim fixtures passed. Server
integration sources and maintenance helpers are retained in the separate local
BattlePass_Spin_Integration workspace, not in this launcher source repository.
