"""Stage 1B-3: pick 5 crater-like landmarks (closed depressions / rims), away from edges, >=1.5 km apart, spread out."""
import json
import numpy as np
from scipy import ndimage as ndi
from common import PROC, WEB

T = np.load(PROC / "terrain.npz")
elev, blocked, slope = T["elev"], T["blocked"], T["slope"]
H, W = elev.shape
e = ndi.gaussian_filter(elev, 1.5)
depth = ndi.grey_closing(e, size=(31, 31)) - e          # bowl depth vs ~300 m closing (closed depression)
rimh = e - ndi.grey_opening(e, size=(31, 31))           # rim/bump height vs ~300 m opening
score = np.maximum(depth, rimh)
margin, mind = 60, 150                                  # 600 m, 1.5 km (cells)
score[:margin], score[-margin:], score[:, :margin], score[:, -margin:] = -1, -1, -1, -1
ok = ndi.binary_erosion(~blocked, iterations=3)         # centre not on a cliff
score[~ok] = -1
# local maxima only, then greedy with spacing, spread via farthest-point bonus
mx = (score == ndi.maximum_filter(score, size=41)) & (score > 2)
cand = np.argwhere(mx)
vals = score[mx]
order = np.argsort(-vals)
cand, vals = cand[order], vals[order]
print("candidates:", len(cand), "top depth/rim (m):", np.round(vals[:5], 1))
chosen = [cand[0]]
while len(chosen) < 5:
    best, bs = None, -1
    for p, v in zip(cand, vals):
        d = min(np.hypot(*(p - q)) for q in chosen)
        if d < mind:
            continue
        s = v * min(d / 400, 1.0)  # prefer strong features that are far from already chosen ones
        if s > bs:
            best, bs = p, s
    if best is None:
        break
    chosen.append(best)
out = []
for i, (r, c) in enumerate(chosen):
    kind = "depression" if depth[r, c] >= rimh[r, c] else "rim"
    out.append({"name": f"Landmark {'ABCDE'[i]}", "x": round((c + 0.5) * 10, 1), "y": round((H - r - 0.5) * 10, 1),
                "elev_m": round(float(elev[r, c]), 1), "kind": kind, "relief_m": round(float(score[r, c]), 1)})
(WEB / "landmarks.json").write_text(json.dumps({"landmarks": out, "units": "metres, x east y north from SW corner"}), encoding="utf-8")
print("name | x | y | elev | kind | relief")
for l in out:
    print(l["name"], l["x"], l["y"], l["elev_m"], l["kind"], l["relief_m"])
ds = [np.hypot(a["x"]-b["x"], a["y"]-b["y"]) for i, a in enumerate(out) for b in out[i+1:]]
print("n", len(out), "min dist", round(min(ds)), "min edge dist", round(min(min(l["x"], l["y"], 10000-l["x"], 10000-l["y"]) for l in out)))
