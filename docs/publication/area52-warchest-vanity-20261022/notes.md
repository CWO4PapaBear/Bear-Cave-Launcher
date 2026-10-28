# Area 52 Warchest and vanity ownership corrections

- Refreshes the Fel Enchanted Warchest item definition at Area 52 login, including accounts that already received it. Clients caching the previous non-openable definition can use the existing chest; no duplicate account gift is sent.
- The chest retains its six guaranteed rewards, including four non-Unique 22-slot Pit Lord's Satchels. The previous database transaction crash repair is preserved.
- Claiming mailed vanity items now immediately registers ownership through the existing collection path. Repeated claims do not duplicate ownership records.
- Item tooltips recognize an individually owned vanity item even when its containing bundle is not owned. An appearance unlock alone does not grant ownership of a bundle or its other rewards.
- Removes malformed unsolicited custom-store packets, incorporating the relevant correction from upstream PR #6446 while preserving our other realm changes.

Close the game and update through the launcher after deployment. No DLL, verification labels, tester certifications, gift receipts or reward quantities are changed. Offline engineering checks cover the stale cached item definition, native mail acquisition, transaction connection compatibility and tooltip ownership combinations. Live gameplay acceptance remains with testers.

Upstream #5052 fixes a different Warchest (2977351), not Fel Enchanted Warchest657112. Upstream #7220 changes binding requirements and is not imported as a blanket ownership policy change here. Area52 account distribution remains excluded from the future upstream reward PR.
