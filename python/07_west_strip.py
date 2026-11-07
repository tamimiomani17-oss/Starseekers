"""Stage 1B-2: profile the western strip + suspected seam from dem.tif."""
import numpy as np
import rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import ndimage as ndi

from common import PROC

with rasterio.open(PROC / "dem.tif") as ds:
    dem = ds.read(1).astype("float32")
bad = dem <= -9998
print("dem", dem.shape, "nodata frac", round(float(bad.mean()), 5), "nodata in x<1500:", round(float(bad[:, :1500].mean()), 5))
z = np.where(bad, np.nan, dem)
z5 = z[:z.shape[0]//5*5, :z.shape[1]//5*5].reshape(z.shape[0]//5, 5, z.shape[1]//5, 5).mean((1, 3))
gy, gx = np.gradient(np.nan_to_num(z5, nan=np.nanmean(z5)), 5)
sl = np.degrees(np.arctan(np.hypot(gx, gy)))
rough = ndi.generic_filter(z5[::2, ::2], np.std, size=3)  # ~10 m std
def bands(a, step_m, px_m, xmax=None):
    n = a.shape[1] * px_m // step_m
    return np.array([np.nanmean(a[:, int(i*step_m/px_m):int((i+1)*step_m/px_m)]) for i in range(int(n))])
bs = bands(sl, 100, 5)[:15]; br = bands(rough, 100, 10)[:15]
bz = bands(z5, 100, 5)[:15]
bnd = [np.mean(np.isnan(z5[:, int(i*20):int((i+1)*20)])) for i in range(15)]
print("band x(m) | mean slope | rough | mean elev | step ratio slope")
for i in range(15):
    ratio = bs[i] / max(bs[i-1], 1e-6) if i else float("nan")
    print(f"{i*100:5d} | {bs[i]:6.2f} | {br[i]:5.2f} | {bz[i]:8.1f} | {ratio:5.2f}")
# constant-value stripes: fraction of identical consecutive columns
cols = z[:, :1500]
const = np.mean(np.nanstd(cols, axis=0) < 1e-3)
print("constant columns frac (x<1500):", round(float(const), 4))
# east comparison and seam region
print("mean slope x 1500-4000:", round(float(np.nanmean(sl[:, 300:800])), 2), " x 4000-4500 y 500-2000:", end=" ")
seam = sl[(10000-2000)//5:(10000-500)//5, 4000//5:4500//5]
print(round(float(np.nanmean(seam)), 2))
# seam columns profile in 20 m steps
cp = [np.nanmean(sl[(10000-2000)//5:(10000-500)//5, c:c+4]) for c in range(4000//5, 4500//5, 4)]
print("seam 20m-col slope max/median:", round(max(cp), 2), round(float(np.median(cp)), 2))
dz = np.abs(np.diff(np.nanmean(z5[(10000-2000)//5:(10000-500)//5, 4000//5:4500//5], axis=0)))
print("seam max column-to-column elev jump (5m):", round(float(np.nanmax(dz)), 2))
fig, ax = plt.subplots(3, 1, figsize=(9, 8))
x = np.arange(15)*100+50
ax[0].plot(x, bs, "o-"); ax[0].set_ylabel("mean slope deg")
ax[1].plot(x, br, "o-"); ax[1].set_ylabel("roughness (10m std)")
ax[2].imshow(z5[:, :300], aspect="auto", cmap="gray", extent=[0, 1500, 0, 10000]); ax[2].set_xlabel("x (m)"); ax[2].set_ylabel("DEM y")
plt.tight_layout(); plt.savefig(PROC / "west_strip.png", dpi=80)
print("saved west_strip.png")
