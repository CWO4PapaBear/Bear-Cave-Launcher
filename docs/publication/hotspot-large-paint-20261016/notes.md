# XP Hotspot larger brush strokes

GM painting now accepts up to 192 local drawing samples instead of 96. When a painted perimeter becomes too detailed, the server tries adaptive smoothing of 2, 5, 10 and up to 20 yards, using the smallest successful tolerance while keeping the 256-point rendering limit.

The client stops additions at its sample, coordinate and segment-length limits and turns the preview red. Accepted points remain available to save or undo. If server validation finds disconnected areas, enclosed holes or an excessively complex boundary, it explains the problem and marks the retained local preview red; nothing is saved on failure. Geometry validation happens when saving, while client input limits are enforced during drawing.

There is no separate maximum polygon area. Brush radius remains 5–1000 yards, with individual segments limited to 5000 yards and world-coordinate bounds enforced. Use connected strokes; separate islands need separate hotspots. Undo the problem stroke or simplify it if a red warning appears.

Use the launcher to receive the updated GM UI after publication. Existing lightweight perimeters, deleted retired rows, GM controls, XP settings and Certified statuses are preserved. No DLL change or new addon.
