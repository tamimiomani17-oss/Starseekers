/* Routing core (shared by browser and Node test). PARAMS mirrors config/params.json (test_astar.js checks they match).
   Grid G = {W,H,cell,cost,slope,soft}: uint8 arrays, row-major, first row = SOUTH. cost 255 = blocked.
   Educational estimate - uncalibrated model. */
(function (root) {
  'use strict';
  const PARAMS = {
    routing: { safe_risk_multiplier: 8, speed_min: 0.15, speed_softness_coef: 0.6, speed_slope_coef: 0.4,
      energy_base: 1.0, energy_softness_coef: 1.5, energy_slope_coef: 2.0, base_speed_mps: 0.04,
      unsafe_mean_risk: 0.6, risk_high: 0.8, unsafe_high_risk_share: 0.15 },
    tracker: { g_base: 0.005, g_softness_coef: 4, g_slope_coef: 2, landmark_reset_sigma_m: 3, sigma_start_m: 2,
      landmark_radius_m: 30, slip_base: 0.05, slip_softness_coef: 0.3, slip_slope_coef: 0.4, slip_patch_cells: 10,
      slip_patch_factor: 2, slip_alert_ratio: 1.5, slip_ema_m: 30 },
  };
  const R = PARAMS.routing, S2 = Math.SQRT2;
  const slopeDeg = (G, i) => G.slope[i] / 255 * 45;
  const soft = (G, i) => G.soft[i] / 255;
  const risk = (G, i) => Math.min(G.cost[i], 254) / 254;
  const speed = (sl, so) => Math.max(R.speed_min, 1 - R.speed_softness_coef * so - R.speed_slope_coef * sl / 25);
  const energy = (sl, so) => R.energy_base + R.energy_softness_coef * so + R.energy_slope_coef * sl / 25;
  function mult(G, i, mode) {
    if (mode === 'safe') return 1 + R.safe_risk_multiplier * risk(G, i);
    const sl = slopeDeg(G, i), so = soft(G, i);
    return mode === 'fast' ? 1 / speed(sl, so) : energy(sl, so);
  }
  const DX = [1, -1, 0, 0, 1, 1, -1, -1], DY = [0, 0, 1, -1, 1, -1, 1, -1];
  let buf = null;
  function astar(G, s, e, mode, opts) {
    opts = opts || {};
    const W = G.W, N = W * G.H, cell = G.cell || 10;
    if (s === e) return [s];
    if ((!opts.ignoreStart && G.cost[s] === 255) || G.cost[e] === 255) return null;
    if (!buf || buf.g.length !== N) buf = { g: new Float64Array(N), from: new Int32Array(N), done: new Uint8Array(N) };
    const { g, from, done } = buf;
    g.fill(Infinity); from.fill(-1); done.fill(0);
    const ex = e % W, ey = (e / W) | 0;
    const h = (i) => { const dx = Math.abs(i % W - ex), dy = Math.abs(((i / W) | 0) - ey);
      return cell * (Math.max(dx, dy) + (S2 - 1) * Math.min(dx, dy)); };  // octile; admissible since mult >= 1
    const hi = [], hf = [];  // binary min-heap (parallel arrays)
    const push = (i, f) => { let k = hi.length; hi.push(i); hf.push(f);
      while (k > 0) { const p = (k - 1) >> 1; if (hf[p] <= f) break; hi[k] = hi[p]; hf[k] = hf[p]; k = p; }
      hi[k] = i; hf[k] = f; };
    const pop = () => { const top = hi[0], li = hi.pop(), lf = hf.pop(), n = hi.length;
      if (n > 0) { let k = 0; for (;;) { let c = 2 * k + 1; if (c >= n) break;
          if (c + 1 < n && hf[c + 1] < hf[c]) c++; if (hf[c] >= lf) break; hi[k] = hi[c]; hf[k] = hf[c]; k = c; }
        hi[k] = li; hf[k] = lf; }
      return top; };
    g[s] = 0; push(s, h(s));
    while (hi.length) {
      const i = pop();
      if (done[i]) continue;
      done[i] = 1;
      if (i === e) { const path = []; for (let k = e; k !== -1; k = from[k]) path.push(k); return path.reverse(); }
      const cx = i % W, cy = (i / W) | 0, mi = mult(G, i, mode);
      for (let k = 0; k < 8; k++) {
        const nx = cx + DX[k], ny = cy + DY[k];
        if (nx < 0 || ny < 0 || nx >= W || ny >= G.H) continue;
        const j = ny * W + nx;
        if (done[j] || G.cost[j] === 255) continue;
        const ng = g[i] + cell * (k >= 4 ? S2 : 1) * 0.5 * (mi + mult(G, j, mode));
        if (ng < g[j]) { g[j] = ng; from[j] = i; push(j, ng + h(j)); }
      }
    }
    return null;
  }
  function stats(G, path) {
    const W = G.W, cell = G.cell || 10;
    let len = 0, time = 0, en = 0, safeCost = 0, maxSlope = 0, rs = 0, soft6 = 0, high = 0;
    for (let k = 0; k < path.length; k++) {
      const i = path[k], r = risk(G, i), so = soft(G, i), sl = slopeDeg(G, i);
      rs += r; if (so > 0.6) soft6++; if (r > R.risk_high) high++; if (sl > maxSlope) maxSlope = sl;
      if (k) { const p = path[k - 1], diag = (p % W !== i % W) && (((p / W) | 0) !== ((i / W) | 0)), d = diag ? cell * S2 : cell;
        const sl2 = (sl + slopeDeg(G, p)) / 2, so2 = (so + soft(G, p)) / 2, r2 = (r + risk(G, p)) / 2;
        len += d; time += d / (R.base_speed_mps * speed(sl2, so2)); en += d * energy(sl2, so2); safeCost += d * (1 + R.safe_risk_multiplier * r2); }
    }
    const n = path.length, st = { len, timeMin: time / 60, energy: en / 1000, safeCost, maxSlope, meanRisk: rs / n, softShare: soft6 / n, highShare: high / n };
    const reasons = [];
    if (st.meanRisk > R.unsafe_mean_risk) reasons.push(`mean risk ${st.meanRisk.toFixed(2)} > ${R.unsafe_mean_risk}`);
    if (st.highShare > R.unsafe_high_risk_share) reasons.push(`${(st.highShare * 100).toFixed(0)}% of cells have risk > ${R.risk_high} (limit ${R.unsafe_high_risk_share * 100}%)`);
    st.unsafe = reasons.length > 0; st.reason = reasons.join('; ');
    return st;
  }
  // Recommended = lowest risk-weighted cost (safe-mode cost, the common yardstick) among routes that are NOT unsafe.
  function recommend(routes) {
    let best = null;
    for (const r of routes) if (r && !r.stats.unsafe && (!best || r.stats.safeCost < best.stats.safeCost)) best = r;
    return best;
  }
  const api = { PARAMS, astar, stats, recommend, mult, speed, energy };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.SS = api;
})(typeof window !== 'undefined' ? window : globalThis);
