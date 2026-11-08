"""Stage 12: export the wide zone to web/data/wide/ (same bin format as the detail zone: uint8, FIRST ROW = SOUTH),
plus mask.bin, hillshade/difficulty PNGs (top row = north), traverse_wide.json, meta_wide.json.
Also prints the overlap check: wide risk vs detail risk inside the 10 km window."""
import datetime
import json

import numpy as np
from PIL import Image
from pyproj import CRS, Transformer

from common import CONFIG, PROC, RAW, WEB, params

OUT = WEB / "wide"
LABEL = "Educational estimate - uncalibrated"


def difficulty_rgba(risk, blocked, mask):
    stops = np.array([0.0, 0.33, 0.66, 1.0])
    cols = np.array([[40, 180, 80], [250, 220, 50], [230, 60, 40], [110, 0, 10]], dtype=float)
    rgb = np.stack([np.interp(risk, stops, cols[:, i]) for i in range(3)], -1)
    a = np.clip((risk - 0.05) / 0.3, 0, 1) * 190 + 40 * (risk > 0.05)
    rgb[blocked] = 0
    a = np.where(blocked, 230, a)
    nodem = (mask & 1) > 0                      # no DEM data: neutral grey, clearly "no data" (not a hazard colour)
    rgb[nodem] = [110, 110, 120]
    a = np.where(nodem, 150, a)
    return np.dstack([rgb, a]).astype(np.uint8)


def overlap(T, ww, win):
    """Wide vs detail risk in the 10 km window: detail risk averaged to 40 m cells."""
    D = np.load(PROC / "terrain.npz")["risk"]                      # 1000x1000, row 0 = north
    d40 = D.reshape(250, 4, 250, 4).mean(axis=(1, 3))
    c0 = int(round((win["bbox"]["xmin"] - ww["bbox"]["xmin"]) / 40))
    r0 = int(round((ww["bbox"]["ymax"] - win["bbox"]["ymax"]) / 40))
    w = T["risk"][r0:r0 + 250, c0:c0 + 250]
    ok = (T["mask"][r0:r0 + 250, c0:c0 + 250] & 1) == 0
    a, b = w[ok], d40[ok]
    corr = float(np.corrcoef(a, b)[0, 1])
    print(f"OVERLAP (10 km window, {ok.sum()} cells of 40 m): corr(risk wide, risk detail) = {corr:.3f}; "
          f"mean wide {a.mean():.3f} vs detail {b.mean():.3f} (diff {a.mean()-b.mean():+.3f}); "
          f"blocked wide {T['blocked'][r0:r0+250, c0:c0+250][ok].mean()*100:.2f}% vs detail {np.load(PROC/'terrain.npz')['blocked'].mean()*100:.2f}%")
    return corr, float(a.mean() - b.mean())


def main():
    P = params()
    ww = json.loads((CONFIG / "window_wide.json").read_text(encoding="utf-8"))
    win = json.loads((CONFIG / "window.json").read_text(encoding="utf-8"))
    T = np.load(PROC / "terrain_wide.npz")
    risk, blocked, slope, soft, mask, hs = (T[k] for k in ["risk", "blocked", "slope", "softness", "mask", "hillshade"])
    H, W = risk.shape
    OUT.mkdir(parents=True, exist_ok=True)
    south_up = lambda a: np.ascontiguousarray(a[::-1])
    cost = np.clip(np.round(risk * 254), 0, 254).astype(np.uint8)
    cost[blocked | ((mask & 1) > 0)] = 255                         # slope-blocked OR no DEM -> impassable
    south_up(cost).tofile(OUT / "cost.bin")
    south_up(np.round(np.clip(slope, 0, 45) / 45 * 255).astype(np.uint8)).tofile(OUT / "slope.bin")
    south_up(np.round(np.clip(soft, 0, 1) * 255).astype(np.uint8)).tofile(OUT / "softness.bin")
    south_up(mask.astype(np.uint8)).tofile(PROC / "mask_wide.bin")  # not shipped to web (no-data is already in cost.bin 255 + difficulty.png)
    Image.fromarray(hs, "L").save(OUT / "hillshade.png", optimize=True)
    Image.fromarray(difficulty_rgba(risk, blocked, mask), "RGBA").save(OUT / "difficulty.png", optimize=True)

    # traverse + waypoints in the shared local frame (origin = SW corner of the 10 km window)
    crs = CRS.from_wkt(win["crs_wkt"])
    to_file = Transformer.from_crs(CRS.from_user_input("+proj=longlat +R=3396190 +no_defs"), crs, always_xy=True)
    X0, Y0 = win["bbox"]["xmin"], win["bbox"]["ymin"]
    ox, oy = ww["origin_local"]
    sx, sy = W * ww["cell_m_file"], H * ww["cell_m_file"]
    loc = lambda lon, lat: (to_file.transform(lon, lat)[0] - X0, to_file.transform(lon, lat)[1] - Y0)
    inside = lambda x, y: ox <= x <= ox + sx and oy <= y <= oy + sy
    cosl = np.cos(np.radians(ww["center_lat"]))
    runs, tlen = [], 0.0
    for f in json.loads((RAW / "M20_traverse.json").read_text(encoding="utf-8"))["features"]:
        sol = f["properties"].get("sol")
        cur = []
        for p in [loc(*c[:2]) for c in f["geometry"]["coordinates"]] + [None]:
            if p is not None and inside(*p):
                cur.append([round(p[0], 1), round(p[1], 1)])
            else:
                if len(cur) >= 2:
                    runs.append({"sol": float(sol) if sol not in (None, "") else None, "pts": cur})
                    d = np.diff(np.array(cur), axis=0)
                    tlen += float(np.sum(np.hypot(d[:, 0] * cosl, d[:, 1])))
                cur = []
    wps = []
    for f in json.loads((RAW / "M20_waypoints.json").read_text(encoding="utf-8"))["features"]:
        x, y = loc(*f["geometry"]["coordinates"][:2])
        if inside(x, y):
            try:
                sol = float(f["properties"].get("sol"))
            except (TypeError, ValueError):
                sol = None
            wps.append({"sol": sol, "x": round(x, 1), "y": round(y, 1)})
    (OUT / "traverse_wide.json").write_text(json.dumps({"segments": runs, "waypoints": wps, "units": "file-CRS metres, x east y north from SW corner of the 10 km window"}), encoding="utf-8")
    last = max((w for w in wps if w["sol"] is not None), key=lambda w: w["sol"], default=None)

    meta = {"label": LABEL, "zone": "wide", "width": W, "height": H, "cell_m": ww["cell_m_file"],
            "cell_m_x": round(ww["cell_m_file"] * float(cosl), 4), "cell_m_y": ww["cell_m_file"],
            "cell_note": "x/y are file-CRS metres; ground metres: x*cos(lat). cell_m_x/cell_m_y are GROUND metres per cell.",
            "size_m": [sx, sy], "origin_local": [ox, oy],
            "origin_note": "same local frame as the detail zone: SW corner of the 10 km window = (0,0); x east, y north",
            "bin_order": "row-major, first row = SOUTH row; index = row*width + col",
            "cost_bin": "uint8: 0..254 = risk*254, 255 = blocked or no DEM",
            "slope_bin": "uint8: slope clipped 0..45 deg -> 0..255 (20 m DEM; smoother than the 10 m zone)",
            "softness_bin": "uint8: 0..1 -> 0..255; value 0 where mask bit 2 is set (no thermal inertia) - NOT a real zero",
            "mask_bin": "NOT shipped (data/processed/mask_wide.bin); uint8 bit flags: 1 = no DEM data, 2 = no thermal-inertia data (risk uses slope+roughness only there)",
            "images": "hillshade.png (2x cells, top row = north), difficulty.png (1 px per cell, RGBA, grey = no DEM)",
            "corners_lonlat": ww["corners_lonlat"], "source": ww["source"], "dem_valid_fraction": ww["dem_valid_fraction"],
            "mask_fractions": {"no_dem": round(float(((mask & 1) > 0).mean()), 4), "no_ti": round(float(((mask & 2) > 0).mean()), 4)},
            "latest_waypoint": last, "traverse_length_m": round(tlen), "params": P,
            "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    (OUT.parent / "meta_wide.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    sizes = {p.name: round(p.stat().st_size / 1e6, 2) for p in OUT.iterdir()}
    print(f"wide export {W}x{H}: files MB {sizes}; traverse {len(runs)} segs {tlen/1000:.1f} km, {len(wps)} waypoints; latest sol {last and last['sol']}")
    overlap(T, ww, win)


if __name__ == "__main__":
    main()
