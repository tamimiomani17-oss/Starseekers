"""Stage 10: wide zone DEM. Downloads the USGS Mars 2020 CTX DEM (20 m, ~90 MB), warps it into the SAME
file CRS/local frame as the 10 km window (so one coordinate system for both zones) -> data/processed/dem_wide.tif.
Also writes config/window_wide.json (does NOT touch window.json)."""
import json

import numpy as np
import rasterio
import requests
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject
from pyproj import CRS, Transformer

from common import CONFIG, PROC, RAW

URL = "https://planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/ScienceInvestigationMaps_JPL/M20_JezeroCrater_CTXDEM_20m.tif"
LOCAL = RAW / "M20_JezeroCrater_CTXDEM_20m.tif"
CELL = 40            # wide routing grid, file-CRS metres per cell
DEM_CELL = 20        # warped DEM grid used for slope (aggregated to 40 m later)
GROUND_KM = 50.0


def main():
    win = json.loads((CONFIG / "window.json").read_text(encoding="utf-8"))
    bb = win["bbox"]
    lat = win["center_lat"]
    cosl = float(np.cos(np.radians(lat)))
    RAW.mkdir(parents=True, exist_ok=True)
    if not LOCAL.exists():
        head = requests.head(URL, allow_redirects=True, timeout=60, headers={"User-Agent": "starseekers-prototype"})
        size = int(head.headers.get("content-length", 0))
        print(f"CTX DEM size {size/1e6:.1f} MB")
        assert 0 < size < 500e6, "refusing download > 500 MB"
        with requests.get(URL, stream=True, timeout=120, headers={"User-Agent": "starseekers-prototype"}) as r:
            r.raise_for_status()
            with open(LOCAL, "wb") as f:
                for ch in r.iter_content(1 << 20):
                    f.write(ch)
    # wide box in file CRS: 50 km GROUND -> x extent = 50000/cos(lat) file-metres; aligned to the 10 m detail grid
    cx, cy = (bb["xmin"] + bb["xmax"]) / 2, (bb["ymin"] + bb["ymax"]) / 2
    ncol = int(round(GROUND_KM * 1000 / cosl / CELL / 2)) * 2      # even number of cells
    nrow = int(GROUND_KM * 1000 / CELL)
    x0, y0 = cx - ncol * CELL / 2, cy - nrow * CELL / 2
    assert (bb["xmin"] - x0) % CELL == 0 and (bb["ymin"] - y0) % CELL == 0, "detail window not aligned to wide grid"
    W, H = ncol * CELL // DEM_CELL, nrow * CELL // DEM_CELL
    dst_tr = from_origin(x0, y0 + nrow * CELL, DEM_CELL, DEM_CELL)
    crs = CRS.from_wkt(win["crs_wkt"])
    out = np.full((H, W), np.nan, dtype="float32")
    with rasterio.open(LOCAL) as src:
        print(f"CTX DEM crs lat_ts note: {src.crs.to_string()[:70]}..., res={src.res}, nodata={src.nodata}")
        reproject(rasterio.band(src, 1), out, dst_transform=dst_tr, dst_crs=crs.to_wkt(), dst_nodata=np.nan,
                  src_nodata=src.nodata, resampling=Resampling.bilinear)
    bad = ~np.isfinite(out) | (out < -1e5) | (out > 1e5)
    out[bad] = -9999.0
    prof = dict(driver="GTiff", width=W, height=H, count=1, dtype="float32", crs=crs.to_wkt(), transform=dst_tr,
                nodata=-9999.0, compress="deflate", predictor=3)
    PROC.mkdir(parents=True, exist_ok=True)
    with rasterio.open(PROC / "dem_wide.tif", "w", **prof) as dst:
        dst.write(out, 1)
    good = out[~bad]
    print(f"dem_wide.tif {W}x{H} @ {DEM_CELL} m, valid {100*(1-bad.mean()):.1f}%, elev {good.min():.0f}..{good.max():.0f} m")

    to_ll = Transformer.from_crs(crs, CRS.from_user_input("+proj=longlat +R=3396190 +no_defs"), always_xy=True)
    sw, ne = to_ll.transform(x0, y0), to_ll.transform(x0 + ncol * CELL, y0 + nrow * CELL)
    ww = {"status": "final", "ground_km": GROUND_KM, "cell_m_file": CELL, "grid": {"width": ncol, "height": nrow},
          "bbox": {"xmin": x0, "ymin": y0, "xmax": x0 + ncol * CELL, "ymax": y0 + nrow * CELL},
          "origin_local": [x0 - bb["xmin"], y0 - bb["ymin"]],
          "center_lon": win["center_lon"], "center_lat": lat, "crs_wkt": win["crs_wkt"],
          "corners_lonlat": {"SW": [round(sw[0], 6), round(sw[1], 6)], "NE": [round(ne[0], 6), round(ne[1], 6)]},
          "source": "USGS Mars 2020 Science CTX DEM 20 m (M20_JezeroCrater_CTXDEM_20m.tif)",
          "source_url": URL, "dem_valid_fraction": round(float(1 - bad.mean()), 4), "dem_cell_m": DEM_CELL}
    (CONFIG / "window_wide.json").write_text(json.dumps(ww, indent=2), encoding="utf-8")
    print(f"window_wide.json: {ncol}x{nrow} cells of {CELL} m; lon {sw[0]:.3f}..{ne[0]:.3f} lat {sw[1]:.3f}..{ne[1]:.3f}")


if __name__ == "__main__":
    main()
