"""Stage 3b: slope (5 m baseline -> 10 m max), roughness, softness proxy (THEMIS TI), risk + blocked.
Output: data/processed/terrain.npz (all arrays north-up, row 0 = north, shape 1000x1000) + hillshade source."""
import json

import numpy as np
import rasterio
import requests
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject
from scipy import ndimage as ndi

from common import CONFIG, PROC, RAW, TI_LOCAL, TI_URL, params


def horn_slope_deg(z, dx, dy):
    k = np.pad(z, 1, mode="edge")
    dzdx = ((k[:-2, 2:] + 2 * k[1:-1, 2:] + k[2:, 2:]) - (k[:-2, :-2] + 2 * k[1:-1, :-2] + k[2:, :-2])) / (8 * dx)
    dzdy = ((k[2:, :-2] + 2 * k[2:, 1:-1] + k[2:, 2:]) - (k[:-2, :-2] + 2 * k[:-2, 1:-1] + k[:-2, 2:])) / (8 * dy)
    return np.degrees(np.arctan(np.hypot(dzdx, dzdy))), dzdx, dzdy


def block(a, f, fn):
    h, w = a.shape
    return fn(a.reshape(h // f, f, w // f, f), axis=(1, 3))


def main():
    P = params()
    w = json.loads((CONFIG / "window.json").read_text(encoding="utf-8"))
    with rasterio.open(PROC / "dem.tif") as ds:
        dem = ds.read(1)
        crs, tr = ds.crs, ds.transform
    bad = dem <= -9998
    print(f"dem {dem.shape}, nodata frac {bad.mean():.5f}")
    if bad.any():  # fill with nearest valid so derivatives stay finite
        idx = ndi.distance_transform_edt(bad, return_distances=False, return_indices=True)
        dem = dem[tuple(idx)]
    H, W = dem.shape
    assert H % 10 == 0 and W % 10 == 0, "window must be multiple of 10 m"

    # slope at 5 m baseline (5x5 mean from 1 m), aggregate to 10 m with max
    z5 = block(dem, 5, np.mean)
    # file CRS is equirectangular with lat_ts=0: x file-metres are 1/cos(lat) longer than ground metres (fix, 8 Nov 2026)
    cosl = float(np.cos(np.radians(w["center_lat"])))
    s5, dzdx, dzdy = horn_slope_deg(z5, 5.0 * cosl, 5.0)
    slope = block(s5, 2, np.max)
    # roughness: std in 10 m block, normalized by 98th percentile
    rough = block(dem, 10, np.std)
    rough_norm = np.clip(rough / np.percentile(rough, P["grid"]["roughness_clip_percentile"]), 0, 1)
    elev10 = block(dem, 10, np.mean)

    # hillshade (5 m), azimuth 315 / altitude 45; row 0 = north. dzdy here is d/d(row) = -d/d(north)
    az, alt = np.radians(315), np.radians(45)
    sl = np.arctan(np.hypot(dzdx, dzdy))
    asp = np.arctan2(-dzdx, dzdy)  # aspect measured for rows increasing southward
    hs = np.sin(alt) * np.cos(sl) + np.cos(alt) * np.sin(sl) * np.cos(az - asp)
    hs = np.clip(hs, 0, 1)
    hs8 = (hs * 255).astype(np.uint8)

    # softness proxy from THEMIS thermal inertia
    if not TI_LOCAL.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        r = requests.get(TI_URL, timeout=120, headers={"User-Agent": "starseekers-prototype"})
        r.raise_for_status()
        TI_LOCAL.write_bytes(r.content)
        print(f"downloaded TI {len(r.content)/1e6:.2f} MB")
    gh, gw = H // 10, W // 10
    dst_tr = from_origin(tr.c, tr.f, 10.0, 10.0)
    ti = np.full((gh, gw), np.nan, dtype="float32")
    with rasterio.open(TI_LOCAL) as src:
        print(f"TI crs={src.crs.to_string()[:50]}, size={src.width}x{src.height}, res={src.res}, nodata={src.nodata}")
        raw = src.read(1).astype("float32")
        raw[(raw == 0) | ~np.isfinite(raw)] = np.nan  # 0 = nodata
        reproject(raw, ti, src_transform=src.transform, src_crs=src.crs, src_nodata=np.nan,
                  dst_transform=dst_tr, dst_crs=crs, dst_nodata=np.nan, resampling=Resampling.bilinear)
    tivalid = np.isfinite(ti)
    if tivalid.sum() > 100:
        lo, hi = np.percentile(ti[tivalid], [2, 98])
        soft = 1 - np.clip((ti - lo) / (hi - lo), 0, 1)
        med = float(np.nanmedian(soft))
        soft = np.where(tivalid, soft, med)
        filled = 1 - float(tivalid.mean())
    else:
        print("WARNING: THEMIS TI does not cover the window; softness = 0.5 everywhere")
        soft, filled, lo, hi, med = np.full((gh, gw), 0.5, "float32"), 1.0, np.nan, np.nan, 0.5
    print(f"softness filled with median: {filled:.3f}  (TI used range {lo:.0f}..{hi:.0f})")

    wt = P["risk_weights"]
    risk = np.clip(wt["slope"] * slope / P["slope_block_deg"] + wt["rough"] * rough_norm + wt["softness"] * soft, 0, 1)
    blocked = slope >= P["slope_block_deg"]
    print(f"slope {slope.min():.1f}..{slope.max():.1f} deg (p50 {np.median(slope):.1f}, p95 {np.percentile(slope,95):.1f}); "
          f"risk {risk.min():.2f}..{risk.max():.2f}; blocked {blocked.mean()*100:.2f}%")
    np.savez_compressed(PROC / "terrain.npz", slope=slope.astype("float32"), rough_norm=rough_norm.astype("float32"),
                        softness=soft.astype("float32"), risk=risk.astype("float32"), blocked=blocked,
                        elev=elev10.astype("float32"), hillshade=hs8,
                        stats=np.array([filled, float(bad.mean())]))
    print("saved data/processed/terrain.npz")


if __name__ == "__main__":
    main()
