"""Stage 4: export web files into web/data/ + preview PNG. Bins are row-major from the SOUTH row up."""
import datetime
import json

import numpy as np
from PIL import Image, ImageDraw
from pyproj import CRS, Transformer
from scipy import ndimage as ndi

from common import CONFIG, PROC, RAW, WEB, params

LABEL = "Educational estimate - uncalibrated"


def difficulty_rgba(risk, blocked):
    stops = np.array([0.0, 0.33, 0.66, 1.0])
    cols = np.array([[40, 180, 80], [250, 220, 50], [230, 60, 40], [110, 0, 10]], dtype=float)
    rgb = np.stack([np.interp(risk, stops, cols[:, i]) for i in range(3)], -1)
    a = np.clip((risk - 0.05) / 0.3, 0, 1) * 190 + 40 * (risk > 0.05)
    rgb[blocked] = 0
    a = np.where(blocked, 230, a)
    return np.dstack([rgb, a]).astype(np.uint8)


def main():
    P = params()
    win = json.loads((CONFIG / "window.json").read_text(encoding="utf-8"))
    T = np.load(PROC / "terrain.npz")
    risk, blocked, slope, soft, rough, elev, hs = (T[k] for k in ["risk", "blocked", "slope", "softness", "rough_norm", "elev", "hillshade"])
    H, W = risk.shape
    cell = P["grid"]["cell_m"]
    bb = win["bbox"]
    WEB.mkdir(parents=True, exist_ok=True)

    south_up = lambda a: np.ascontiguousarray(a[::-1])
    cost = np.clip(np.round(risk * 254), 0, 254).astype(np.uint8)
    cost[blocked] = 255
    south_up(cost).tofile(WEB / "cost.bin")
    south_up(np.round(np.clip(slope, 0, 45) / 45 * 255).astype(np.uint8)).tofile(WEB / "slope.bin")
    south_up(np.round(np.clip(soft, 0, 1) * 255).astype(np.uint8)).tofile(WEB / "softness.bin")

    # images (north-up, normal image orientation: top = north)
    Image.fromarray(hs, "L").save(WEB / "hillshade.png", optimize=True)
    diff = Image.fromarray(difficulty_rgba(risk, blocked), "RGBA").resize((W, H), Image.NEAREST)
    diff.save(WEB / "difficulty.png", optimize=True)

    # coordinates
    crs = CRS.from_wkt(win["crs_wkt"])
    ll = CRS.from_user_input("+proj=longlat +R=3396190 +no_defs")
    to_file = Transformer.from_crs(ll, crs, always_xy=True)
    to_ll = Transformer.from_crs(crs, ll, always_xy=True)
    corners = {n: to_ll.transform(x, y) for n, (x, y) in
               {"SW": (bb["xmin"], bb["ymin"]), "SE": (bb["xmax"], bb["ymin"]), "NW": (bb["xmin"], bb["ymax"]), "NE": (bb["xmax"], bb["ymax"])}.items()}
    X0, Y0 = bb["xmin"], bb["ymin"]
    size = W * cell

    def loc(lon, lat):
        x, y = to_file.transform(lon, lat)
        return x - X0, y - Y0

    # traverse clipped to window (runs of consecutive inside points; segments keep their sol)
    inside = lambda x, y: 0 <= x <= size and 0 <= y <= size
    runs, tlen = [], 0.0
    for f in json.loads((RAW / "M20_traverse.json").read_text(encoding="utf-8"))["features"]:
        sol = f["properties"].get("sol")
        pts = [loc(*c[:2]) for c in f["geometry"]["coordinates"]]
        cur = []
        for p in pts + [None]:
            if p is not None and inside(*p):
                cur.append([round(p[0], 1), round(p[1], 1)])
            else:
                if len(cur) >= 2:
                    runs.append({"sol": float(sol) if sol not in (None, "") else None, "pts": cur})
                    d = np.diff(np.array(cur), axis=0); tlen += float(np.sum(np.hypot(d[:, 0] * np.cos(np.radians(win["center_lat"])), d[:, 1])))
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
    (WEB / "traverse.json").write_text(json.dumps({"segments": runs, "waypoints": wps, "units": "metres, x east y north from SW corner"}), encoding="utf-8")
    print(f"traverse: {len(runs)} segments, {tlen/1000:.2f} km inside window; {len(wps)} waypoints inside")

    # landmarks: roughness + elevation prominence, >= 1.5 km apart, away from edges
    sm = lambda a, s: ndi.gaussian_filter(a, s)
    prom = elev - sm(elev, 30)  # local high relative to ~300 m neighbourhood
    z = lambda a: (a - a.mean()) / (a.std() + 1e-9)
    score = z(sm(rough, 5)) + z(sm(prom, 3)) + 0.5 * z(elev)
    margin = 30
    score[:margin], score[-margin:], score[:, :margin], score[:, -margin:] = -1e9, -1e9, -1e9, -1e9
    score[blocked] -= 3  # keep landmarks reachable-ish
    lms, mind = [], 150  # cells (1.5 km)
    s = score.copy()
    yy, xx = np.mgrid[0:H, 0:W]
    for i in range(5):
        r, c = np.unravel_index(np.argmax(s), s.shape)
        lms.append({"name": f"Landmark {i+1}", "x": round((c + 0.5) * cell, 1), "y": round((H - r - 0.5) * cell, 1),
                    "elev_m": round(float(elev[r, c]), 1)})
        s[np.hypot(yy - r, xx - c) < mind] = -1e12
    (WEB / "landmarks.json").write_text(json.dumps({"landmarks": lms, "units": "metres, x east y north from SW corner"}), encoding="utf-8")
    ds = [np.hypot(a["x"] - b["x"], a["y"] - b["y"]) for i, a in enumerate(lms) for b in lms[i + 1:]]
    print(f"landmarks: 5, min pairwise distance {min(ds):.0f} m")

    meta = {
        "label": LABEL, "width": W, "height": H, "cell_m": cell, "size_m": size,
        "cell_m_x": round(cell * float(np.cos(np.radians(win["center_lat"]))), 4), "cell_m_y": cell,
        "cell_note": "x/y local coords are file-CRS metres; GROUND metres per cell are cell_m_x (E-W, = cell*cos(lat)) and cell_m_y (N-S)",
        "origin_local": [0, 0], "origin_note": "SW corner of window = (0,0); x east, y north, metres",
        "bin_order": "row-major, first row = SOUTH row, rows go northward; index = row*width + col",
        "cost_bin": "uint8: 0..254 = risk*254, 255 = blocked",
        "slope_bin": "uint8: slope clipped 0..45 deg scaled to 0..255",
        "softness_bin": "uint8: softness 0..1 scaled to 0..255",
        "images": "hillshade.png (2000x2000, top row = north) and difficulty.png (1000x1000 RGBA, top row = north) cover the full window",
        "window_bbox_file_crs": bb, "crs": crs.to_wkt(),
        "corners_lonlat": {k: [round(v[0], 6), round(v[1], 6)] for k, v in corners.items()},
        "window_case": win["case"], "latest_waypoint": win["latest_waypoint"],
        "sources": [win["source"], "THEMIS thermal inertia of Jezero (Zenodo 4931348)", "NASA MMGIS M20 waypoints/traverse"],
        "model": {"risk": "clamp(0.5*slope/25 + 0.25*rough_norm + 0.25*softness, 0, 1); blocked if slope >= 25 deg",
                  "params_file": "config/params.json"},
        "params": P,
        "softness_filled_fraction": round(float(T["stats"][0]), 4),
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    (WEB / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")

    # preview
    hsr = Image.open(WEB / "hillshade.png").convert("RGBA")
    base = hsr.resize((1000, 1000), Image.BILINEAR)
    base = Image.alpha_composite(base, diff)
    d = ImageDraw.Draw(base)
    toimg = lambda p: (p[0] / cell, H - p[1] / cell)
    for sgm in runs:
        d.line([toimg(p) for p in sgm["pts"]], fill=(0, 200, 255, 255), width=3)
    for l in lms:
        x, y = toimg((l["x"], l["y"]))
        d.ellipse([x - 7, y - 7, x + 7, y + 7], outline=(255, 255, 255, 255), width=3)
    d.text((8, 8), LABEL, fill=(255, 255, 255, 255))
    base.convert("RGB").save(PROC / "preview.png")

    # sanity checks
    tot = 0
    for fn in ["cost.bin", "slope.bin", "softness.bin", "hillshade.png", "difficulty.png", "traverse.json", "landmarks.json", "meta.json"]:
        sz = (WEB / fn).stat().st_size
        tot += sz
        print(f"  web/data/{fn}: {sz/1e3:.0f} kB")
    print(f"  total web/data: {tot/1e6:.2f} MB")
    cb = np.fromfile(WEB / "cost.bin", np.uint8)
    nan_ok = np.isfinite(risk).all() and np.isfinite(slope).all() and cb.size == W * H
    bf = blocked.mean() * 100
    print(f"CHECK a (no NaN, size ok): {'PASS' if nan_ok else 'FAIL'}")
    print(f"CHECK b (blocked 0..40%): {'PASS' if 0 <= bf <= 40 else 'WARN'} ({bf:.2f}%)")
    print(f"CHECK c (traverse inside grid): {'PASS' if len(runs) else 'FAIL/none'} ({len(runs)} segments)")
    print(f"CHECK d (risk tracks slope, corr): {np.corrcoef(risk.ravel(), slope.ravel())[0,1]:.2f} -> inspect data/processed/preview.png")


if __name__ == "__main__":
    main()
