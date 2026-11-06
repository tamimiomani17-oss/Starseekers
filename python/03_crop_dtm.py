"""Stage 3a: crop the DTM to the chosen window -> data/processed/dem.tif (windowed read, local or remote)."""
import json
import time

import numpy as np
import rasterio
from rasterio.windows import Window, from_bounds

from common import CONFIG, PROC, dtm_path, rio_env


def main():
    w = json.loads((CONFIG / "window.json").read_text(encoding="utf-8"))
    bb = w["bbox"]
    PROC.mkdir(parents=True, exist_ok=True)
    with rio_env():
        with rasterio.open(dtm_path()) as ds:
            win = from_bounds(bb["xmin"], bb["ymin"], bb["xmax"], bb["ymax"], ds.transform).round_offsets().round_lengths()
            print(f"source: {dtm_path()[:60]}... window px: {win}")
            prof = ds.profile.copy()
            tr = ds.window_transform(win)
            H, W = int(win.height), int(win.width)
            prof.update(width=W, height=H, transform=tr, compress="deflate", tiled=True, blockxsize=256, blockysize=256,
                        predictor=3, nodata=-9999.0, dtype="float32")
            nod = ds.nodata
            n_nod = 0
            vmin, vmax = np.inf, -np.inf
            with rasterio.open(PROC / "dem.tif", "w", **prof) as dst:
                step = 1000  # rows per chunk keeps memory small
                for r in range(0, H, step):
                    rows = min(step, H - r)
                    sub = Window(win.col_off, win.row_off + r, W, rows)
                    a = None
                    for attempt in range(8):  # remote reads can fail transiently; reopen and retry
                        try:
                            a = ds.read(1, window=sub).astype("float32")
                            break
                        except rasterio.errors.RasterioIOError as e:
                            print(f"\n  retry {attempt+1} at row {r} ({str(e)[:40]})")
                            time.sleep(5 * (attempt + 1))
                            ds.close()
                            ds = rasterio.open(dtm_path())
                    if a is None:
                        raise SystemExit(f"giving up at row {r}")
                    bad = ~np.isfinite(a) | (a < -1e6) | (a > 1e6)
                    if nod is not None:
                        bad |= (a == nod)
                    a[bad] = -9999.0
                    n_nod += int(bad.sum())
                    good = a[~bad]
                    if good.size:
                        vmin, vmax = min(vmin, float(good.min())), max(vmax, float(good.max()))
                    dst.write(a, 1, window=Window(0, r, W, rows))
                    print(f"  rows {r+rows}/{H}", end="\r")
    print(f"\ndem.tif {W}x{H}, nodata fraction {n_nod/(W*H):.5f}, elevation range {vmin:.1f}..{vmax:.1f} m")
    w["status"] = "final"
    w["crop_px"] = [W, H]
    (CONFIG / "window.json").write_text(json.dumps(w, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
