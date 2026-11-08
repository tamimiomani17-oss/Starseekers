"""Stage 11: wide-zone terrain (40 m cells). Same risk formula as the 10 m zone, but slope comes from a 20 m DEM
(Horn, 3x3 = 40 m span, aggregated to 40 m with max) so values are smoother and NOT directly comparable.
Latitude fix built in: ground dx = cell*cos(lat), dy = cell. No invented data: a mask marks cells without DEM
(bit 1) or without thermal inertia (bit 2). Output: data/processed/terrain_wide.npz (row 0 = north)."""
import json

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject
from scipy import ndimage as ndi

from common import CONFIG, PROC, TI_LOCAL, params

DEM_CELL = 20


def horn(z, dx, dy):
    k = np.pad(z, 1, mode="edge")
    dzdx = ((k[:-2, 2:] + 2 * k[1:-1, 2:] + k[2:, 2:]) - (k[:-2, :-2] + 2 * k[1:-1, :-2] + k[2:, :-2])) / (8 * dx)
    dzdy = ((k[2:, :-2] + 2 * k[2:, 1:-1] + k[2:, 2:]) - (k[:-2, :-2] + 2 * k[:-2, 1:-1] + k[:-2, 2:])) / (8 * dy)
    return np.degrees(np.arctan(np.hypot(dzdx, dzdy))), dzdx, dzdy


def block(a, f, fn):
    h, w = a.shape
    return fn(a.reshape(h // f, f, w // f, f), axis=(1, 3))


def main():
    P = params()
    ww = json.loads((CONFIG / "window_wide.json").read_text(encoding="utf-8"))
    cell = ww["cell_m_file"]
    cosl = float(np.cos(np.radians(ww["center_lat"])))
    with rasterio.open(PROC / "dem_wide.tif") as ds:
        dem = ds.read(1)
        crs, tr = ds.crs, ds.transform
    bad = dem <= -9998
    idx = ndi.distance_transform_edt(bad, return_distances=False, return_indices=True)
    demf = dem[tuple(idx)]                      # nearest fill only so derivatives stay finite; masked afterwards
    f = cell // DEM_CELL
    s20, dzdx, dzdy = horn(demf, DEM_CELL * cosl, DEM_CELL)
    slope = block(s20, f, np.max)
    rough = block(demf, f, np.std)
    # nodata at 40 m: any bad 20 m sample in the block, or within 1 cell of it (derivative edge)
    nodem = block(ndi.binary_dilation(bad, iterations=1), f, np.max).astype(bool)
    valid = ~nodem
    rough_norm = np.clip(rough / np.percentile(rough[valid], P["grid"]["roughness_clip_percentile"]), 0, 1)
    elev = block(demf, f, np.mean)

    az, alt = np.radians(315), np.radians(45)   # hillshade at 20 m (display only), row 0 = north
    sl = np.arctan(np.hypot(dzdx, dzdy)); asp = np.arctan2(-dzdx, dzdy)
    hs = np.clip(np.sin(alt) * np.cos(sl) + np.cos(alt) * np.sin(sl) * np.cos(az - asp), 0, 1)
    hs8 = (hs * 255).astype(np.uint8)
    hs8[bad] = 0

    gh, gw = slope.shape
    ti = np.full((gh, gw), np.nan, dtype="float32")
    with rasterio.open(TI_LOCAL) as src:
        raw = src.read(1).astype("float32")
        raw[(raw == 0) | ~np.isfinite(raw)] = np.nan   # 0 = nodata
        reproject(raw, ti, src_transform=src.transform, src_crs=src.crs, src_nodata=np.nan,
                  dst_transform=from_origin(tr.c, tr.f, cell, cell), dst_crs=crs, dst_nodata=np.nan, resampling=Resampling.bilinear)
    tivalid = np.isfinite(ti)
    lo, hi = np.percentile(ti[tivalid & valid], [2, 98])
    soft = np.where(tivalid, 1 - np.clip((ti - lo) / (hi - lo), 0, 1), 0.0).astype("float32")
    wt = P["risk_weights"]
    full = wt["slope"] * slope / P["slope_block_deg"] + wt["rough"] * rough_norm + wt["softness"] * soft
    # no TI: use slope+rough terms only, renormalised to the same 0..1 scale (flagged in mask bit 2, not invented)
    part = (wt["slope"] * slope / P["slope_block_deg"] + wt["rough"] * rough_norm) / (wt["slope"] + wt["rough"])
    risk = np.clip(np.where(tivalid, full, part), 0, 1)
    blocked = (slope >= P["slope_block_deg"]) & valid
    mask = (nodem.astype(np.uint8) * 1) | ((~tivalid & valid).astype(np.uint8) * 2)
    print(f"grid {gw}x{gh}; DEM valid {valid.mean()*100:.1f}%; TI valid (of valid DEM) {(tivalid&valid).sum()/valid.sum()*100:.1f}%; TI range used {lo:.0f}..{hi:.0f}")
    print(f"slope p50 {np.median(slope[valid]):.1f} p95 {np.percentile(slope[valid],95):.1f} max {slope[valid].max():.1f} deg; "
          f"risk mean {risk[valid].mean():.3f}; blocked {blocked[valid].mean()*100:.2f}% of valid")
    np.savez_compressed(PROC / "terrain_wide.npz", slope=slope.astype("float32"), rough_norm=rough_norm.astype("float32"),
                        softness=soft, risk=risk.astype("float32"), blocked=blocked, mask=mask, elev=elev.astype("float32"),
                        hillshade=hs8, ti_lohi=np.array([lo, hi]))
    print("saved data/processed/terrain_wide.npz")


if __name__ == "__main__":
    main()
