"""Stage 1: download Perseverance / Ingenuity GeoJSON from NASA MMGIS and print a short summary."""
import json
import pathlib
import requests

RAW = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"
BASE = "https://mars.nasa.gov/mmgis-maps/M20/Layers/json/"
FILES = ["M20_waypoints.json", "M20_traverse.json", "m20_heli_waypoints.json", "m20_heli_flight_path.json"]


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        path = RAW / name
        try:
            r = requests.get(BASE + name, timeout=60, headers={"User-Agent": "starseekers-prototype"})
            r.raise_for_status()
            path.write_bytes(r.content)
            print(f"{name}: downloaded {len(r.content)/1e3:.0f} kB")
        except Exception as e:  # keep going; report plainly
            print(f"{name}: FAILED ({e})")
            continue
        gj = json.loads(path.read_text(encoding="utf-8"))
        feats = gj.get("features", [])
        props = sorted({k for f in feats for k in (f.get("properties") or {})})
        gtypes = sorted({(f.get("geometry") or {}).get("type", "?") for f in feats})
        print(f"  features={len(feats)} geom={gtypes}")
        print(f"  properties={props}")

    wp = json.loads((RAW / "M20_waypoints.json").read_text(encoding="utf-8"))["features"]
    best = None
    for f in wp:
        p = f.get("properties") or {}
        sol = fnum(p.get("sol"))
        g = f.get("geometry") or {}
        if sol is None or g.get("type") != "Point":
            continue
        lon, lat = g["coordinates"][:2]
        if best is None or sol > best[0]:
            best = (sol, lon, lat, p)
    if best:
        print(f"LATEST waypoint: sol={best[0]:.0f} lon={best[1]:.6f} lat={best[2]:.6f}")
    else:
        print("could not determine latest waypoint")


if __name__ == "__main__":
    main()
