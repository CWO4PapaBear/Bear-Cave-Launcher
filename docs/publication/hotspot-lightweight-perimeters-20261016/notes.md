# XP Hotspot single-perimeter correction

Combined hotspots now use one clean polygon perimeter per saved entry instead of retaining their original component shapes. The 1,415 prior replacement entries become 1,349 plain polygons. Disconnected areas are separate entries; each perimeter stays within the native 256-point limit. Names no longer include a combined-count suffix.

The new perimeter follows the union's outer boundary, fills enclosed holes, and smooths redundant points within half a yard of the tessellated boundary. This selects the existing fast polygon-rendering path instead of repeatedly checking every component shape. Offline Lua rendering checks showed a substantial CPU reduction; testers will confirm in-game performance.

Inherited quest IDs, objective and POI metadata, geometry provenance and historical source-reference metadata are removed from all affected records. The 4,464 retired records are permanently deleted from the working database, with no separate archive. Another 905 usable records receive metadata-only cleanup; their geometry and enabled state remain intact. The 414 whole-zone hotspots remain unchanged.

New polygon entries use default +150% XP, 60-minute duration/cooldown and weight 1, and start inactive in the normal rotation. The server now avoids copying hotspot geometry during routine timer scans, catalog paging and rotation selection. Retired records are excluded from runtime loading. This is a server update; no client download or DLL change is required. Verification and Certified totals are unchanged.
