"""Stage 1B-1: validate the risk model against the real Perseverance path -> docs/VALIDATION.md."""
import json

import numpy as np

from common import PROC, ROOT, WEB, params


def densify(pts, step=10.0):
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        d = float(np.hypot(b[0] - a[0], b[1] - a[1]))
        n = max(1, int(np.ceil(d / step)))
        for i in range(n):
            t = i / n
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    out.append(tuple(pts[-1]))
    return out


def main():
    P = params()
    T = np.load(PROC / "terrain.npz")
    risk, blocked, slope, soft = T["risk"], T["blocked"], T["slope"], T["softness"]
    H, W = risk.shape
    tj = json.loads((WEB / "traverse.json").read_text(encoding="utf-8"))
    pts = []
    for s in tj["segments"]:
        pts += densify(s["pts"])
    pts = np.array(pts)
    col = np.clip((pts[:, 0] // 10).astype(int), 0, W - 1)
    row = np.clip(H - 1 - (pts[:, 1] // 10).astype(int), 0, H - 1)  # arrays are north-up
    inside = (pts[:, 0] >= 0) & (pts[:, 0] < 10000) & (pts[:, 1] >= 0) & (pts[:, 1] < 10000)
    cells = np.unique(np.stack([row, col], 1)[inside], axis=0)
    r, b, s, so = (a[cells[:, 0], cells[:, 1]] for a in (risk, blocked, slope, soft))
    rows = [
        ("densified points (10 m), inside window", f"{int(inside.sum())} / {len(pts)}"),
        ("unique cells along path", f"{len(cells)}"),
        ("risk mean / median / p90 / max", f"{r.mean():.3f} / {np.median(r):.3f} / {np.percentile(r,90):.3f} / {r.max():.3f}"),
        (f"% cells blocked (slope >= {P['slope_block_deg']} deg)", f"{b.mean()*100:.2f}%"),
        ("% cells risk > 0.6", f"{(r>0.6).mean()*100:.2f}%"),
        ("% cells risk > 0.8", f"{(r>0.8).mean()*100:.2f}%"),
        ("slope p50 / p90 / p99 / max (deg)", f"{np.median(s):.1f} / {np.percentile(s,90):.1f} / {np.percentile(s,99):.1f} / {s.max():.1f}"),
        ("mean softness", f"{so.mean():.3f}"),
        ("window-wide: risk mean, blocked %", f"{risk.mean():.3f}, {blocked.mean()*100:.2f}%"),
    ]
    pess = b.mean() > 0.05 or r.mean() > 0.5
    verdict = ("Model TOO PESSIMISTIC (blocked > 5% or mean risk > 0.5): relax `slope_block_deg` and/or lower the slope weight."
               if pess else "Model NOT too pessimistic by the rule (blocked <= 5% and mean risk <= 0.5).")
    md = ["# Validation vs real Perseverance path (educational, uncalibrated)", "", "| metric | value |", "|---|---|"]
    md += [f"| {k} | {v} |" for k, v in rows]
    md += ["", f"**Verdict:** {verdict}", ""]
    (ROOT / "docs" / "VALIDATION.md").write_text("\n".join(md), encoding="utf-8")
    for k, v in rows:
        print(f"{k}: {v}")
    print(verdict)


if __name__ == "__main__":
    main()
