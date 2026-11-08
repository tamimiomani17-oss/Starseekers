/* Rover tracker simulation (Stage C). Educational estimate - uncalibrated model.
   Uncertainty sigma grows per metre, shrinks at landmarks; a hidden slip patch triggers an alert + re-plan. */
(function () {
  'use strict';
  const P = SS.PARAMS.tracker, R = SS.PARAMS.routing;
  const $ = (id) => document.getElementById(id);
  const SIM_MS = 30;  // simulated driving speed at x1 (m/s of animation; the real rover speed assumption is only used for "time remaining")
  let T = null, raf = 0, last = 0, rover, circle, patchLine, driveLine;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const slipPred = (so, sl) => clamp(P.slip_base + P.slip_softness_coef * so + P.slip_slope_coef * sl / 25, 0, 0.9);

  function log(t) { const li = document.createElement('li'); li.textContent = `[${T ? (T.driven / 1000).toFixed(2) : '0.00'} km] ${t}`; $('log').prepend(li); }
  function cum(path) { const c = [0], A = window.App;
    for (let k = 1; k < path.length; k++) { c.push(c[k - 1] + A.gd(A.xy(path[k - 1]), A.xy(path[k]))); }  // ground metres (x is stretched 1/cos(lat) in the file CRS)
    return c; }
  function pos() { const A = window.App, a = A.xy(T.path[T.i]), b = A.xy(T.path[Math.min(T.i + 1, T.path.length - 1)]);
    return [a[0] + (b[0] - a[0]) * T.frac, a[1] + (b[1] - a[1]) * T.frac]; }
  function clear() { clearTimeout(raf); raf = 0;
    for (const l of [rover, circle, patchLine, driveLine]) if (l) window.App.map.removeLayer(l);
    rover = circle = patchLine = driveLine = null; $('banner').hidden = true; }

  function start() {
    const A = window.App, sel = A && A.state.sel; if (!sel) { alert('Pick two points on the map first.'); return; }
    clear(); $('log').innerHTML = '';
    const path = sel.path.slice(), n = path.length;
    let patch = new Set(), patchPts = [];
    if (n >= 40) { const s = Math.floor(n * (0.35 + 0.4 * Math.random())); const cells = path.slice(s, s + P.slip_patch_cells); patch = new Set(cells); patchPts = cells; }
    const c0 = path[0], sl0 = A.G.slope[c0] / 255 * 45, so0 = A.G.soft[c0] / 255, p0 = slipPred(so0, sl0);
    T = { mode: sel.mode, path, i: 0, frac: 0, cum: cum(path), driven: 0, sigma: P.sigma_start_m, energy: 0, estM: p0, estP: p0,
      alerted: false, patch, patchPts, pts: [{ d: 0, s: P.sigma_start_m }], marks: [], inLm: {}, lastPush: 0, cost: A.G.cost.slice(), done: false };
    const q = pos();
    circle = L.circle([q[1], q[0]], { radius: T.sigma, color: '#ff9f43', weight: 1, fillColor: '#ff9f43', fillOpacity: 0.3, interactive: false }).addTo(A.map);
    rover = L.circleMarker([q[1], q[0]], { radius: 6, color: '#fff', weight: 2, fillColor: '#ff5252', fillOpacity: 1, interactive: false }).addTo(A.map);
    driveLine = L.polyline(path.map(A.ll), { color: '#fff', weight: 2, dashArray: '2 6', interactive: false }).addTo(A.map);
    if ($('follow').checked) A.map.setView([q[1], q[0]], 0, { animate: false });
    log(`Drive started (${sel.mode.name} route, ${(T.cum[n - 1] / 1000).toFixed(2)} km)`);
    last = performance.now(); raf = setTimeout(() => frame(performance.now()), 30);
  }

  // consume `budget` metres of driving in <=5 m chunks; returns true if an alert paused the run
  function advance(budget) {
    const A = window.App, G = A.G;
    while (budget > 0 && T.i < T.path.length - 1) {
      const seg = T.cum[T.i + 1] - T.cum[T.i], ds = Math.min(budget, seg * (1 - T.frac), 5);
      budget -= ds; T.frac += ds / seg; if (T.frac >= 0.9999) { T.i++; T.frac = 0; }
      const c = T.path[Math.min(T.i, T.path.length - 1)], sl = G.slope[c] / 255 * 45, so = G.soft[c] / 255;
      T.sigma += P.g_base * (1 + P.g_softness_coef * so + P.g_slope_coef * sl / 25) * ds;
      T.energy += ds * SS.energy(sl, so); T.driven += ds;
      const pred = slipPred(so, sl), meas = pred * (T.patch.has(c) ? P.slip_patch_factor : 1) * (1 + (Math.random() - 0.5) * 0.1), al = 1 - Math.exp(-ds / P.slip_ema_m);
      T.estP += al * (pred - T.estP); T.estM += al * (meas - T.estM); T.sl = sl; T.so = so;
      const q = pos();
      A.lmMarkers.forEach((m, k) => { const d = A.gd([m.lm.x, m.lm.y], q);
        if (d < P.landmark_radius_m && !T.inLm[k]) { T.inLm[k] = true; flash(m);
          if (T.sigma > P.landmark_reset_sigma_m) log(`${m.lm.name} pass: sigma ${T.sigma.toFixed(1)} -> ${P.landmark_reset_sigma_m} m`);
          T.sigma = Math.min(T.sigma, P.landmark_reset_sigma_m); T.marks.push({ d: T.driven, label: m.lm.name.slice(-1), color: '#a64bf4' }); }
        else if (d > 2 * P.landmark_radius_m) T.inLm[k] = false; });
      if (T.driven - T.lastPush >= 5 || T.marks.length && T.marks[T.marks.length - 1].d === T.driven) { T.pts.push({ d: T.driven, s: T.sigma }); T.lastPush = T.driven; }
      if (!T.alerted && T.estM / T.estP > P.slip_alert_ratio) { alertStop(); return true; }
    }
    return false;
  }
  function flash(m) { m.setStyle({ radius: 14, fillColor: '#fff' }); setTimeout(() => m.setStyle({ radius: 6, fillColor: '#a64bf4' }), 900); }
  function alertStop() {
    T.alerted = true; clearTimeout(raf); raf = 0;
    T.marks.push({ d: T.driven, label: '!', color: '#ff5252' });
    patchLine = L.polyline(T.patchPts.map(window.App.ll), { color: '#ff5252', weight: 8, opacity: 0.8, interactive: false }).addTo(window.App.map);
    $('btext').textContent = `Slip ${(T.estM * 100).toFixed(0)}% vs ${(T.estP * 100).toFixed(0)}% predicted (+${((T.estM / T.estP - 1) * 100).toFixed(0)}%).`;
    $('banner').hidden = false; log('ALERT: measured slip exceeds prediction by > 50% - paused'); ui();
  }
  async function replan() {
    const A = window.App; $('banner').hidden = true;
    for (const c of T.patchPts) T.cost[c] = 255;  // mark the slip patch as blocked
    const end = T.path[T.path.length - 1], k = A.MODES.findIndex((m) => m.id === T.mode.id);
    const p = await A.solve(k, T.path[T.i], end, { cost: T.cost.slice(), ignoreStart: true });
    if (!p) { log('Re-plan: no alternative route; continuing through the patch'); }
    else { T.path = Array.from(p); T.i = 0; T.frac = 0; T.cum = cum(T.path); T.patch = new Set();
      A.map.removeLayer(driveLine); driveLine = L.polyline(T.path.map(A.ll), { color: '#fff', weight: 2, dashArray: '2 6', interactive: false }).addTo(A.map);
      log(`Re-planned around the slip patch: ${(T.cum[T.cum.length - 1] / 1000).toFixed(2)} km remaining`); }
    last = performance.now(); raf = setTimeout(() => frame(performance.now()), 30);
  }
  function cont() { $('banner').hidden = true; log('Continuing through the slip patch'); last = performance.now(); raf = setTimeout(() => frame(performance.now()), 30); }

  function frame(ts) {
    const dt = Math.min((ts - last) / 1000, 0.5); last = ts;
    const paused = advance(SIM_MS * $('sp').value * dt);
    const q = pos(); rover.setLatLng([q[1], q[0]]); circle.setLatLng([q[1], q[0]]); circle.setRadius(T.sigma);
    if ($('follow').checked) window.App.map.setView([q[1], q[0]], window.App.map.getZoom(), { animate: false });
    ui();
    if (paused) return;
    if (T.i >= T.path.length - 1) { T.done = true; log(`Arrived. Final sigma ${T.sigma.toFixed(1)} m`); return; }
    raf = setTimeout(() => frame(performance.now()), 30);
  }
  function ui() {
    const remain = T.cum[T.cum.length - 1] - (T.cum[T.i] + T.frac * ((T.cum[T.i + 1] || T.cum[T.i]) - T.cum[T.i]));
    $('m-dist').textContent = (T.driven / 1000).toFixed(2);
    $('m-time').textContent = (remain / R.base_speed_mps / 3600).toFixed(1);
    $('m-en').textContent = (T.energy / 1000).toFixed(1);
    $('m-slip').textContent = (T.estM * 100).toFixed(0); $('m-slip').style.color = T.estM / T.estP > P.slip_alert_ratio ? '#ff5252' : '';
    $('m-pred').textContent = (T.estP * 100).toFixed(0);
    $('m-sig').textContent = T.sigma.toFixed(1);
    $('m-sl').textContent = `${(T.sl || 0).toFixed(1)} / ${(T.so || 0).toFixed(2)}`;
    chart();
  }
  function chart() {
    const cv = $('chart'), g = cv.getContext('2d'), W = cv.width, H = cv.height, m = { l: 36, r: 8, t: 8, b: 22 };
    const xmax = T.driven + T.cum[T.cum.length - 1] - (T.cum[T.i] + 0), ymax = Math.max(5, ...T.pts.map((p) => p.s)) * 1.1;
    const X = (d) => m.l + d / xmax * (W - m.l - m.r), Y = (s) => H - m.b - s / ymax * (H - m.t - m.b);
    g.clearRect(0, 0, W, H); g.strokeStyle = '#27355e'; g.fillStyle = '#93a0c4'; g.font = '10px sans-serif';
    g.beginPath(); g.moveTo(m.l, m.t); g.lineTo(m.l, H - m.b); g.lineTo(W - m.r, H - m.b); g.stroke();
    g.fillText('sigma (m)', 2, 10); g.fillText(ymax.toFixed(0), 8, m.t + 8); g.fillText('0', 24, H - m.b); g.fillText('distance (km): ' + (xmax / 1000).toFixed(1), W / 2 - 40, H - 6);
    for (const k of T.marks) { g.strokeStyle = k.color; g.setLineDash([3, 3]); g.beginPath(); g.moveTo(X(k.d), m.t); g.lineTo(X(k.d), H - m.b); g.stroke(); g.fillStyle = k.color; g.fillText(k.label, X(k.d) + 2, m.t + 9); }
    g.setLineDash([]); g.strokeStyle = '#ff9f43'; g.lineWidth = 2; g.beginPath();
    T.pts.forEach((p, k) => (k ? g.lineTo(X(p.d), Y(p.s)) : g.moveTo(X(p.d), Y(p.s)))); g.stroke(); g.lineWidth = 1;
  }
  window.Tracker = { stop() { clear(); T = null; }, routesChanged() {}, state: () => T };
  $('drive').onclick = start; $('stop').onclick = () => { clearTimeout(raf); raf = 0; if (T) log('Stopped'); };
  $('replan').onclick = replan; $('cont').onclick = cont;
  $('sp').oninput = (e) => ($('spv').textContent = e.target.value);
})();
