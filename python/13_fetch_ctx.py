"""Stage 13 (optional): CTX imagery backdrop for the wide zone. Fetches the Murray Lab CTX mosaic tiles served by Esri
(OnMars/CTX1, level 11 = ~10 m/px, 512 px JPEG tiles, geographic degrees, origin lon -180 / lat 90), ~110 tiles (~6 MB),
politely throttled. Mosaics + crops them to the wide box and saves a reduced-resolution JPEG -> web/data/wide/ctx.jpg.
Display only (NOT used for slope). Credit: NASA/JPL/MSSS/The Murray Lab; Dickson et al. 2024, doi:10.1029/2024EA003555."""
import io
import json
import time

import requests
from PIL import Image

from common import CONFIG, RAW, WEB

BASE = "https://astro.arcgis.com/arcgis/rest/services/OnMars/CTX1/MapServer/tile"
LEVEL, TILE_PX = 11, 512
OUT_W = 2636           # output = 20 m per pixel over the 52.7 km wide box (reduced from the ~10 m source)


def main():
    ww = json.loads((CONFIG / "window_wide.json").read_text(encoding="utf-8"))
    (lon0, lat0), (lon1, lat1) = ww["corners_lonlat"]["SW"], ww["corners_lonlat"]["NE"]
    deg = 360 / 2 ** (LEVEL + 1)                      # degrees per tile (0.0879 at level 11)
    c0, c1 = int((lon0 + 180) // deg), int((lon1 + 180) // deg)
    r0, r1 = int((90 - lat1) // deg), int((90 - lat0) // deg)
    cache = RAW / "ctx_tiles"
    cache.mkdir(parents=True, exist_ok=True)
    n = (c1 - c0 + 1) * (r1 - r0 + 1)
    print(f"level {LEVEL}: cols {c0}..{c1}, rows {r0}..{r1} = {n} tiles")
    mosaic = Image.new("RGB", ((c1 - c0 + 1) * TILE_PX, (r1 - r0 + 1) * TILE_PX))
    got = 0
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            f = cache / f"{LEVEL}_{r}_{c}.img"
            if not f.exists():
                status = "no response"
                for attempt in range(5):
                    try:
                        resp = requests.get(f"{BASE}/{LEVEL}/{r}/{c}", timeout=(10, 30), headers={"User-Agent": "starseekers-prototype (education)"})
                        status = f"HTTP {resp.status_code}"
                        if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):  # JPEG, or PNG where coverage is partial
                            f.write_bytes(resp.content)
                            break
                    except requests.exceptions.RequestException as e:   # transient network error: wait and retry
                        status = type(e).__name__
                    time.sleep(3 * (attempt + 1))
                else:
                    raise SystemExit(f"tile {LEVEL}/{r}/{c} failed ({status})")
                time.sleep(0.3)                        # be polite to the service
            mosaic.paste(Image.open(f).convert("RGB"), ((c - c0) * TILE_PX, (r - r0) * TILE_PX))
            got += 1
    # crop to the wide box: pixels per degree is the same in x and y (plate carree)
    ppd = TILE_PX / deg
    x0, x1 = (lon0 + 180 - c0 * deg) * ppd, (lon1 + 180 - c0 * deg) * ppd
    y0, y1 = (90 - lat1 - r0 * deg) * ppd, (90 - lat0 - r0 * deg) * ppd
    crop = mosaic.crop((round(x0), round(y0), round(x1), round(y1)))
    out_h = round(OUT_W * crop.height / crop.width)
    crop = crop.resize((OUT_W, out_h), Image.LANCZOS).convert("L")   # grey: CTX is panchromatic
    crop.save(WEB / "wide" / "ctx.jpg", quality=62, optimize=True)
    print(f"tiles {got}/{n}, mosaic {mosaic.size}, crop -> {crop.size}, ctx.jpg {(WEB/'wide'/'ctx.jpg').stat().st_size/1e6:.2f} MB")


if __name__ == "__main__":
    main()
