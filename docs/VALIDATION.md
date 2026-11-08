# Validation vs real Perseverance path (educational, uncalibrated)

| metric | value |
|---|---|
| densified points (10 m), inside window | 23775 / 23775 |
| unique cells along path | 3109 |
| risk mean / median / p90 / max | 0.290 / 0.266 / 0.457 / 0.810 |
| % cells blocked (slope >= 25 deg) | 0.00% |
| % cells risk > 0.6 | 3.35% |
| % cells risk > 0.8 | 0.10% |
| slope p50 / p90 / p99 / max (deg) | 3.8 / 11.4 / 17.4 / 21.3 |
| mean softness | 0.537 |
| window-wide: risk mean, blocked % | 0.371, 1.21% |

**Verdict:** Model NOT too pessimistic by the rule (blocked <= 5% and mean risk <= 0.5).

## Latitude-scale fix (8 Nov 2026, Stage 1b)
File CRS is equirectangular with lat_ts = 0, so x file-metres are 1/cos(18.47 deg) = 1.054x ground metres. `04_terrain.py` now uses dx = 5*cos(lat) in the Horn slope; `meta.json` has `cell_m_x` (9.485 m, ground E-W) and `cell_m_y` (10 m); A*/stats/tracker use ground distances.
| metric (10 km window) | before | after |
|---|---|---|
| slope p95 (deg) | 18.6 | 19.2 |
| blocked cells (slope >= 25 deg) | 1.02% | 1.21% |
| mean risk, whole window | 0.366 | 0.371 |
| risk > 0.6 along real path | 3.18% | 3.35% |
| window ground width | 10.0 km | 9.49 km (height 10 km) |
Typical E-W route lengths shrink ~5% (N-S unchanged). Verdict unchanged: model not too pessimistic.

## Wide zone (50 km, 40 m) vs detail zone, inside the 10 km window (Stage 1)
62,500 cells of 40 m (detail risk averaged 4x4): correlation of risk = 0.816; mean risk wide 0.364 vs detail 0.366; blocked 0.50% (wide) vs 1.02% (detail, before the fix) - the 20 m DEM smooths slopes, so the wide zone under-counts steep cells. Wide zone: DEM valid 92.9%, thermal inertia available on 77.8% of valid cells (the rest uses slope+roughness only, flagged in `mask.bin`).
