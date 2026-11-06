"""Stage 2: choose the 10x10 km window. Reads only metadata + a coarse (1/50) sample of the remote DTM
(a few tens of MB), never the whole file. Writes config/window.json (a PROPOSAL until the DTM is downloaded)."""
import json

import numpy as np
import requests
import rasterio
from pyproj import CRS, Transformer

from common import CONFIG, PROC, RAW, DTM_URL, dtm_path, params, rio_env

WIN = 10000.0  # m
DEC = 50  # decimation for the coarse validity mask (50 m cells)


def main():
    P = params()
    # --- sizes -------------------------------------------------------------
    h = requests.head(DTM_URL, timeout=60, allow_redirects=True, headers={"User-Agent": "starseekers-prototype"})
    size = int(h.headers.get("Content-Length", 0))
    print(f"HiRISE DTM JEZ_hirise_soc_006 1 m: {size/1e9:.2f} GB (single GeoTIFF, uncompressed, striped)")
    print("MSR TRN HiRISE DTM zip: ~5.3 GB (per SOURCES.md; not needed unless the window fails)")

    # --- latest waypoint ---------------------------------------------------
    wp = json.loads((RAW / "M20_waypoints.json").read_text(encoding="utf-8"))["features"]
    pts = [(float(f["properties"]["sol"]), *f["geometry"]["coordinates"][:2]) for f in wp
           if f["properties"].get("sol") not in (None, "")]
    sol, lon, lat = max(pts)
    print(f"latest waypoint: sol {sol:.0f}, lon {lon:.5f}, lat {lat:.5f}")

    with rio_env():
        with rasterio.open(dtm_path()) as ds:
            crs, b, nodata, W, H = ds.crs, ds.bounds, ds.nodata, ds.width, ds.height
            print(f"DTM CRS: {crs.to_string()[:60]}... | bounds x {b.left:.0f}..{b.right:.0f}, y {b.bottom:.0f}..{b.top:.0f} | {W}x{H} @ {ds.res}")
            oh, ow = H // DEC, W // DEC
            cache = PROC / "coarse_valid.npy"
            if cache.exists():
                valid = np.load(cache)
            else:
                coarse = ds.read(1, out_shape=(oh, ow), resampling=rasterio.enums.Resampling.nearest, masked=True)
                valid = ~np.ma.getmaskarray(coarse) & np.isfinite(coarse.filled(np.nan)) & (coarse.filled(-1e9) > -1e6)
                np.save(cache, valid)
    print(f"coarse valid fraction of DTM extent: {valid.mean():.3f}")

    # --- project traverse + waypoint into the DTM CRS -----------------------
    tr = Transformer.from_crs(CRS.from_user_input("+proj=longlat +R=3396190 +no_defs"), crs, always_xy=True)
    cx, cy = tr.transform(lon, lat)
    print(f"latest waypoint in DTM CRS: x={cx:.0f}, y={cy:.0f}")

    # dense samples along traverse (every ~10 m)
    tj = json.loads((RAW / "M20_traverse.json").read_text(encoding="utf-8"))["features"]
    samples, weights = [], []
    for f in tj:
        xy = np.array([tr.transform(*c[:2]) for c in f["geometry"]["coordinates"]])
        if len(xy) < 2:
            continue
        seg = np.hypot(*np.diff(xy, axis=0).T)
        for i, L in enumerate(seg):
            n = max(1, int(L // 10))
            t = (np.arange(n) + 0.5) / n
            samples.append(xy[i] + t[:, None] * (xy[i + 1] - xy[i]))
            weights.append(np.full(n, L / n))
        # (each sample represents ~10 m)
    S = np.vstack(samples)
    Wt = np.concatenate(weights)  # metres of path represented by each sample
    print(f"traverse total length ~{Wt.sum()/1000:.1f} km; inside DTM extent: "
          f"{Wt[(S[:,0]>b.left)&(S[:,0]<b.right)&(S[:,1]>b.bottom)&(S[:,1]<b.top)].sum()/1000:.1f} km")

    # --- candidate squares ---------------------------------------------------
    n = int(WIN / (DEC * 1.0))  # coarse cells per side (200)
    ii = np.pad(valid.astype(np.int64).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    def all_valid(r0, c0):
        return (ii[r0 + n, c0 + n] - ii[r0, c0 + n] - ii[r0 + n, c0] + ii[r0, c0]) == n * n

    def square_to_xy(r0, c0):  # row 0 is the TOP of the file
        x0 = b.left + c0 * DEC
        y1 = b.top - r0 * DEC
        return x0, y1 - WIN, x0 + WIN, y1

    def length_inside(x0, y0, x1, y1):
        return float(Wt[(S[:, 0] >= x0) & (S[:, 0] <= x1) & (S[:, 1] >= y0) & (S[:, 1] <= y1)].sum())

    # case A: centered on the latest waypoint
    c0 = int(round((cx - WIN / 2 - b.left) / DEC)); r0 = int(round((b.top - (cy + WIN / 2)) / DEC))
    caseA = 0 <= r0 <= oh - n and 0 <= c0 <= ow - n and all_valid(r0, c0)
    if caseA:
        x0, y0, x1, y1 = square_to_xy(r0, c0)
        case = "A: centered on latest waypoint"
    else:
        print("Centered square does NOT fit inside valid DTM data -> fallback (max traverse length).")
        best = None
        for r in range(0, oh - n + 1, 2):
            for c in range(0, ow - n + 1, 2):
                if not all_valid(r, c):
                    continue
                x0_, y0_, x1_, y1_ = square_to_xy(r, c)
                L = length_inside(x0_, y0_, x1_, y1_)
                d = np.hypot((x0_ + x1_) / 2 - cx, (y0_ + y1_) / 2 - cy)
                key = (round(L, -1), -d)  # tie-break: closer to latest waypoint
                if best is None or key > best[0]:
                    best = (key, (x0_, y0_, x1_, y1_))
        if best is None:
            print("NO fully valid 10 km square in the DTM. Fallback to CTX 20 m DEM needed (not done automatically).")
            return
        x0, y0, x1, y1 = best[1]
        case = "B: fallback, most Perseverance traverse length inside valid HiRISE data"
    L = length_inside(x0, y0, x1, y1)
    inv = Transformer.from_crs(crs, CRS.from_user_input("+proj=longlat +R=3396190 +no_defs"), always_xy=True)
    clon, clat = inv.transform((x0 + x1) / 2, (y0 + y1) / 2)
    latest_in = x0 <= cx <= x1 and y0 <= cy <= y1
    print(f"CASE {case}")
    print(f"window bbox (file CRS) x {x0:.0f}..{x1:.0f}, y {y0:.0f}..{y1:.0f}; center lon {clon:.5f}, lat {clat:.5f}")
    print(f"traverse inside window: {L/1000:.2f} km; latest waypoint inside window: {latest_in}")

    out = {
        "status": "proposal (DTM crop not yet done)" if not (RAW / "JEZ_hirise_soc_006_1m.tif").exists() else "final",
        "case": case, "center_lon": clon, "center_lat": clat,
        "bbox": {"xmin": x0, "ymin": y0, "xmax": x1, "ymax": y1}, "crs_wkt": crs.to_wkt(),
        "source": "USGS HiRISE DTM mosaic JEZ_hirise_soc_006 (1 m)", "resolution_m": 1.0,
        "grid": {"cell_m": 10, "width": 1000, "height": 1000},
        "latest_waypoint": {"sol": sol, "lon": lon, "lat": lat, "x": cx, "y": cy, "inside_window": latest_in},
        "traverse_length_inside_m": L, "dtm_file_bytes": size,
    }
    (CONFIG / "window.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote config/window.json")


if __name__ == "__main__":
    main()
