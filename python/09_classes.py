"""Stage 1B-4: 5-class difficulty palette (from Canva legend) -> difficulty.png + classes.json."""
import json
import numpy as np
from PIL import Image
from common import PROC, WEB

TH = [0.25, 0.35, 0.50, 0.65]  # chosen from the risk histogram (risk rarely < 0.15 because softness adds a baseline)
CLASSES = [
    ("صخر صلب", "Solid rock", "#F4F1EA"),
    ("سهل", "Easy", "#F2D544"),
    ("متوسط", "Moderate", "#F5A55A"),
    ("صعب", "Difficult", "#E0662A"),
    ("ممنوع", "Prohibited", "#7A0E12"),
]
T = np.load(PROC / "terrain.npz")
risk, blocked = T["risk"], T["blocked"]
cls = np.digitize(risk, TH)           # 0..4
cls[blocked] = 4
cls[(cls == 4) & ~blocked] = 4        # risk >= 0.65 is also "prohibited-class" visually
rgb = np.array([[int(h[i:i+2], 16) for i in (1, 3, 5)] for _, _, h in CLASSES], np.uint8)
alpha = np.array([150, 170, 175, 185, 215], np.uint8)
img = np.dstack([rgb[cls], alpha[cls]])
Image.fromarray(img, "RGBA").save(WEB / "difficulty.png", optimize=True)
edges = [0] + TH + [1]
out = {"thresholds": TH, "note": "blocked (slope >= 25 deg) is always Prohibited; route UNSAFE cap = mean risk 0.6",
       "classes": [{"id": i, "name_ar": a, "name_en": e, "color": c,
                    "risk_min": edges[i], "risk_max": edges[i+1], "share_pct": round(float((cls == i).mean()*100), 1)}
                   for i, (a, e, c) in enumerate(CLASSES)]}
(WEB / "classes.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("class shares %:", [c["share_pct"] for c in out["classes"]])
tot = sum(p.stat().st_size for p in WEB.iterdir())
print(f"web/data total {tot/1e6:.2f} MB")
