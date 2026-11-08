/* StarSeekers Mars Trackers - map + route planner. Educational estimate - uncalibrated model.
   Two zones share ONE local frame: x east, y north, file-CRS metres, SW corner of the 10 km detail zone = (0,0).
   Leaflet CRS.Simple uses [y, x]. Ground distance = x*cos(lat) (file CRS has lat_ts=0), see gd() below.
   Route grid: both clicks inside the detail zone -> 10 m grid, otherwise the wide 40 m grid. */
(async function () {
  const $ = (id) => document.getElementById(id);
  const MODES = [{ id: 'safe', name: 'Safe', color: '#3ddc84' }, { id: 'fast', name: 'Fast', color: '#4aa8ff' }, { id: 'power', name: 'Power', color: '#ffd23f' }];
  const j = (n) => fetch(`data/${n}.json`).then((r) => r.json());
  const b = (n) => fetch(`data/${n}.bin`).then((r) => r.arrayBuffer()).then((a) => new Uint8Array(a));
  const [meta, mw, classes, trav, lms, cost, slope, soft, wcost, wslope, wsoft] = await Promise.all([j('meta'), j('meta_wide'), j('classes'), j('wide/traverse_wide'), j('landmarks'),
    b('cost'), b('slope'), b('softness'), b('wide/cost'), b('wide/slope'), b('wide/softness')]);
  // grids: cx/cy = ground metres per cell (E-W is shorter than the file-CRS cell by cos(lat)); ox/oy = SW corner in local metres
  const DET = { name: 'det', label: '10 m', W: meta.width, H: meta.height, cell: meta.cell_m, cx: meta.cell_m_x, cy: meta.cell_m_y, ox: 0, oy: 0, cost, slope, soft };
  const WIDE = { name: 'wide', label: '40 m', W: mw.width, H: mw.height, cell: mw.cell_m, cx: mw.cell_m_x, cy: mw.cell_m_y, ox: mw.origin_local[0], oy: mw.origin_local[1], cost: wcost, slope: wslope, soft: wsoft };
  let G = DET;  // grid of the current route (tracker reads App.G)
  const SIZE = meta.size_m, KX = meta.cell_m_x / meta.cell_m;
  const gd = (a, c) => Math.hypot((c[0] - a[0]) * KX, c[1] - a[1]);  // ground metres between two local points
  const inside = (g, x, y) => x >= g.ox && y >= g.oy && x < g.ox + g.W * g.cell && y < g.oy + g.H * g.cell;

  // ---- map ----
  const map = L.map('map', { crs: L.CRS.Simple, minZoom: -7, maxZoom: 2, zoomSnap: 0.25, attributionControl: false });
  const DB = [[0, 0], [SIZE, SIZE]], WB = [[WIDE.oy, WIDE.ox], [WIDE.oy + WIDE.H * WIDE.cell, WIDE.ox + WIDE.W * WIDE.cell]];
  const hsW = L.imageOverlay('data/wide/hillshade.png', WB).addTo(map);
  const dfW = L.imageOverlay('data/wide/difficulty.png', WB, { opacity: 0.7 }).addTo(map);
  const hs = L.imageOverlay('data/hillshade.png', DB).addTo(map);
  const df = L.imageOverlay('data/difficulty.png', DB, { opacity: 0.7 }).addTo(map);
  map.fitBounds(WB);
  // frame around the detail zone + zone labels
  const frame = L.layerGroup().addTo(map);
  L.rectangle(DB, { color: '#fff', weight: 1.5, dashArray: '6 4', fill: false, interactive: false }).addTo(frame);
  const zlabel = (ll, txt) => L.marker(ll, { icon: L.divIcon({ className: 'zlabel', html: txt, iconSize: null }), interactive: false }).addTo(frame);
  zlabel([SIZE, 0], 'Detail 10 m'); zlabel([WB[1][0], WB[0][1]], 'Wide 40 m (coarser)');
  const trLayer = L.layerGroup().addTo(map), lmLayer = L.layerGroup().addTo(map), routeLayer = L.layerGroup().addTo(map);
  for (const s of trav.segments) {
    L.polyline(s.pts.map((p) => [p[1], p[0]]), { color: '#00c8ff', weight: 3, opacity: 0.9 }).bindTooltip('Perseverance sol ' + s.sol, { sticky: true }).addTo(trLayer);
  }
  const lw = mw.latest_waypoint;  // latest published waypoint (inside the wide zone, outside the detail zone)
  if (lw) L.circleMarker([lw.y, lw.x], { radius: 6, color: '#fff', weight: 2, fillColor: '#00c8ff', fillOpacity: 1 }).bindTooltip(`Perseverance, latest waypoint (sol ${lw.sol})`).addTo(trLayer);
  const lmMarkers = lms.landmarks.map((l) => {
    const m = L.circleMarker([l.y, l.x], { radius: 6, color: '#fff', weight: 2, fillColor: '#a64bf4', fillOpacity: 0.9, interactive: false }).addTo(lmLayer);
    return Object.assign(m, { lm: l });
  });
  lmMarkers.forEach((m) => m.bindTooltip(m.lm.name, { permanent: true, direction: 'top', offset: [0, -6] }));
  const bind = (id, ...layers) => $(id).addEventListener('change', (e) => layers.forEach((l) => (e.target.checked ? l.addTo(map) : map.removeLayer(l))));
  bind('l-hs', hs, hsW); bind('l-df', df, dfW); bind('l-tr', trLayer); bind('l-lm', lmLayer); bind('l-fr', frame);
  $('op').addEventListener('input', (e) => { df.setOpacity(e.target.value / 100); dfW.setOpacity(e.target.value / 100); });

  // legend (colours/names from classes.json) + "no data" swatch for the wide zone
  const lg = L.control({ position: 'bottomleft' });
  lg.onAdd = () => { const d = L.DomUtil.create('div', 'legend');
    d.innerHTML = '<b>Terrain difficulty</b><br>' + classes.classes.map((c) => `<i style="background:${c.color}"></i>${c.name_en} <span dir="rtl">${c.name_ar}</span>`).join('<br>')
      + '<br><i style="background:#6e6e78"></i>No data (outside DEM) <span dir="rtl">لا بيانات</span>'; return d; };
  lg.addTo(map);
  // scale bar in metres, along the N-S axis (L.Control.Scale assumes lat/lng, so a tiny custom one)
  const sb = L.control({ position: 'bottomright' });
  sb.onAdd = () => { const d = L.DomUtil.create('div', 'scalebar'); d.update = () => {
    const ppm = Math.pow(2, map.getZoom()), len = [5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000].filter((v) => v * ppm <= 140).pop() || 5000;
    d.innerHTML = `${len >= 1000 ? len / 1000 + ' km' : len + ' m'}<div style="width:${len * ppm}px"></div>`; }; return d; };
  sb.addTo(map); map.on('zoomend', () => sb.getContainer().update()); sb.getContainer().update();
  // cursor readout: longitude/latitude are linear in the equirectangular file CRS, so interpolating the wide-zone corners is exact
  const C = mw.corners_lonlat, f = (a, bb, t) => a + (bb - a) * t;
  map.on('mousemove', (e) => { const x = e.latlng.lng, y = e.latlng.lat, tx = (x - WIDE.ox) / (WIDE.W * WIDE.cell), ty = (y - WIDE.oy) / (WIDE.H * WIDE.cell);
    $('cursor').textContent = `x ${x.toFixed(0)} m, y ${y.toFixed(0)} m | lon ${f(C.SW[0], C.NE[0], tx).toFixed(4)}, lat ${f(C.SW[1], C.NE[1], ty).toFixed(4)} | ${inside(DET, x, y) ? 'detail 10 m' : inside(WIDE, x, y) ? 'wide 40 m' : 'outside'}`; });
  // where is Perseverance now, relative to the detail zone
  if (lw) { const dx = lw.x < 0 ? -lw.x : Math.max(lw.x - SIZE, 0), dy = lw.y < 0 ? -lw.y : Math.max(lw.y - SIZE, 0), dist = Math.hypot(dx * KX, dy);
    $('offmap').textContent = `Perseverance now (sol ${lw.sol}): ${(dist / 1000).toFixed(1)} km from the detail zone (inside the wide zone)`; }

  // ---- route planner (A* runs in 3 Web Workers, one per mode; each holds both grids) ----
  const workers = MODES.map(() => { const w = new Worker('worker.js');
    for (const g of [DET, WIDE]) w.postMessage({ init: g.name, W: g.W, H: g.H, cell: g.cell, cx: g.cx, cy: g.cy, cost: g.cost.slice(), slope: g.slope.slice(), soft: g.soft.slice() });
    return w; });
  let jid = 0;
  const solve = (wi, s, e, opts) => new Promise((res) => { const id = ++jid, w = workers[wi];
    const h = (ev) => { if (ev.data.id === id) { w.removeEventListener('message', h); res(ev.data.path); } };
    w.addEventListener('message', h); w.postMessage(Object.assign({ id, s, e, mode: MODES[wi].id, grid: G.name }, opts)); });
  const idx = (x, y) => Math.floor((y - G.oy) / G.cell) * G.W + Math.floor((x - G.ox) / G.cell);
  const xy = (i) => [G.ox + ((i % G.W) + 0.5) * G.cell, G.oy + (Math.floor(i / G.W) + 0.5) * G.cell];
  const ll = (i) => { const p = xy(i); return [p[1], p[0]]; };
  const state = { clicks: [], routes: [], sel: null, rec: null };
  const pins = L.layerGroup().addTo(map);

  function select(r) {
    state.sel = r;
    routeLayer.eachLayer((l) => l.setStyle({ weight: l.route === r ? 6 : 3, opacity: l.route === r ? 1 : 0.6 }));
    document.querySelectorAll('#rt tbody tr').forEach((tr) => tr.classList.toggle('sel', tr.dataset.mode === (r && r.mode.id)));
  }
  function render() {
    routeLayer.clearLayers(); const tb = $('rt').tBodies[0]; tb.innerHTML = '';
    const valid = state.routes.filter(Boolean); $('rt').hidden = !valid.length;
    state.rec = SS.recommend(valid);
    for (const r of valid) {
      const l = L.polyline(r.path.map(ll), { color: r.mode.color, weight: 3, dashArray: r.stats.unsafe ? '8 6' : null }).addTo(routeLayer); l.route = r;
      const s = r.stats, tr = tb.insertRow(); tr.dataset.mode = r.mode.id; tr.onclick = () => select(r);
      tr.innerHTML = `<td><span class="sw" style="background:${r.mode.color}"></span>${r.mode.name}${r === state.rec ? '<span class="rec">Recommended</span>' : ''}</td><td>${G.label}</td><td>${s.len.toFixed(0)}</td><td>${s.timeMin.toFixed(0)}</td><td>${s.energy.toFixed(1)}</td><td>${s.maxSlope.toFixed(1)}&deg;</td><td>${s.meanRisk.toFixed(2)}</td><td>${(s.softShare * 100).toFixed(0)}%</td>`
        + `<td class="${s.unsafe ? 'unsafe' : 'ok'}" title="${s.unsafe ? s.reason : 'within limits'}">${s.unsafe ? 'UNSAFE' : 'OK'}</td>`;
    }
    const msg = $('rmsg'); msg.className = '';
    if (state.clicks.length === 2 && !valid.length) { msg.className = 'err'; msg.textContent = 'No route: start or end is blocked / has no data, or they are disconnected by blocked terrain.'; }
    else if (valid.length && !state.rec) { msg.className = 'err'; msg.textContent = 'No safe route found between these points (all routes UNSAFE, none recommended).'; }
    else msg.textContent = valid.length && G === WIDE ? 'Wide grid (40 m, coarser): slopes are smoother than in the 10 m detail zone, so this route is less precise.' : '';
    select(state.rec || valid[0] || null);
    if (window.Tracker) window.Tracker.routesChanged();
  }
  map.on('click', async (e) => {
    const x = e.latlng.lng, y = e.latlng.lat;
    if (!inside(WIDE, x, y)) return;
    if (window.Tracker) window.Tracker.stop();
    if (state.clicks.length >= 2) { state.clicks = []; state.routes = []; pins.clearLayers(); render(); }
    state.clicks.push([x, y]);
    L.circleMarker([y, x], { radius: 6, color: '#fff', fillColor: state.clicks.length === 1 ? '#3ddc84' : '#ff5252', fillOpacity: 1 }).addTo(pins);
    if (state.clicks.length < 2) { $('rmsg').textContent = 'Start set. Click the end point.'; return; }
    G = state.clicks.every((p) => inside(DET, p[0], p[1])) ? DET : WIDE;  // both ends in the detail zone -> 10 m grid, else wide
    app.G = G;
    const s = idx(...state.clicks[0]), t = idx(...state.clicks[1]);
    $('rmsg').textContent = `Searching on the ${G.label} grid...`; const t0 = performance.now();
    const paths = await Promise.all(MODES.map((m, k) => solve(k, s, t)));
    state.routes = paths.map((p, k) => p && { mode: MODES[k], path: Array.from(p), stats: SS.stats(G, p) });
    console.log(`3 searches (${G.label} grid) in ${(performance.now() - t0).toFixed(0)} ms (parallel workers)`);
    render();
  });
  const app = { map, G, MODES, state, meta, lmMarkers, xy, ll, idx, gd, solve, select, render, $ };
  window.App = app;
})();
