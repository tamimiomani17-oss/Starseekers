/* StarSeekers Mars Trackers - map + route planner. Educational estimate - uncalibrated model.
   Coordinates: local metres, x east, y north, SW corner = (0,0). Leaflet CRS.Simple uses [y, x]. */
(async function () {
  const $ = (id) => document.getElementById(id);
  const MODES = [{ id: 'safe', name: 'Safe', color: '#3ddc84' }, { id: 'fast', name: 'Fast', color: '#4aa8ff' }, { id: 'power', name: 'Power', color: '#ffd23f' }];
  const j = (n) => fetch(`data/${n}.json`).then((r) => r.json());
  const b = (n) => fetch(`data/${n}.bin`).then((r) => r.arrayBuffer()).then((a) => new Uint8Array(a));
  const [meta, classes, trav, lms, cost, slope, soft] = await Promise.all([j('meta'), j('classes'), j('traverse'), j('landmarks'), b('cost'), b('slope'), b('softness')]);
  const G = { W: meta.width, H: meta.height, cell: meta.cell_m, cost, slope, soft };
  const SIZE = meta.size_m, C = meta.corners_lonlat;

  // ---- map ----
  const map = L.map('map', { crs: L.CRS.Simple, minZoom: -4, maxZoom: 2, zoomSnap: 0.25, attributionControl: false });
  const BND = [[0, 0], [SIZE, SIZE]];
  const hs = L.imageOverlay('data/hillshade.png', BND).addTo(map);
  const df = L.imageOverlay('data/difficulty.png', BND, { opacity: 0.7 }).addTo(map);
  map.fitBounds(BND);
  const trLayer = L.layerGroup().addTo(map), lmLayer = L.layerGroup().addTo(map), routeLayer = L.layerGroup().addTo(map);
  for (const s of trav.segments) {
    L.polyline(s.pts.map((p) => [p[1], p[0]]), { color: '#00c8ff', weight: 3, opacity: 0.9 }).bindTooltip('Perseverance sol ' + s.sol, { sticky: true }).addTo(trLayer);
  }
  const lmMarkers = lms.landmarks.map((l) => {
    const m = L.circleMarker([l.y, l.x], { radius: 6, color: '#fff', weight: 2, fillColor: '#a64bf4', fillOpacity: 0.9, interactive: false }).addTo(lmLayer);
    return Object.assign(m, { lm: l });
  });
  lmMarkers.forEach((m) => m.bindTooltip(m.lm.name, { permanent: true, direction: 'top', offset: [0, -6] }));
  const bind = (id, layer) => $(id).addEventListener('change', (e) => (e.target.checked ? layer.addTo(map) : map.removeLayer(layer)));
  bind('l-hs', hs); bind('l-df', df); bind('l-tr', trLayer); bind('l-lm', lmLayer);
  $('op').addEventListener('input', (e) => df.setOpacity(e.target.value / 100));

  // legend (colours/names from classes.json)
  const lg = L.control({ position: 'bottomleft' });
  lg.onAdd = () => { const d = L.DomUtil.create('div', 'legend');
    d.innerHTML = '<b>Terrain difficulty</b><br>' + classes.classes.map((c) => `<i style="background:${c.color}"></i>${c.name_en} <span dir="rtl">${c.name_ar}</span>`).join('<br>'); return d; };
  lg.addTo(map);
  // scale bar in metres (L.Control.Scale assumes lat/lng, so a tiny custom one)
  const sb = L.control({ position: 'bottomright' });
  sb.onAdd = () => { const d = L.DomUtil.create('div', 'scalebar'); d.update = () => {
    const ppm = Math.pow(2, map.getZoom()), len = [5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000].filter((v) => v * ppm <= 140).pop() || 5000;
    d.innerHTML = `${len >= 1000 ? len / 1000 + ' km' : len + ' m'}<div style="width:${len * ppm}px"></div>`; }; return d; };
  sb.addTo(map); map.on('zoomend', () => sb.getContainer().update()); sb.getContainer().update();
  // cursor readout (lon/lat by linear interpolation between the window corners: small-window approximation)
  map.on('mousemove', (e) => { const x = e.latlng.lng, y = e.latlng.lat, f = (a, bb, t) => a + (bb - a) * t;
    $('cursor').textContent = `x ${x.toFixed(0)} m, y ${y.toFixed(0)} m | lon ${f(C.SW[0], C.NE[0], x / SIZE).toFixed(4)}, lat ${f(C.SW[1], C.NE[1], y / SIZE).toFixed(4)}`; });
  // off-map indicator for the latest Perseverance waypoint
  const wp = meta.latest_waypoint, bb = meta.window_bbox_file_crs, wx = wp.x - bb.xmin, wy = wp.y - bb.ymin;
  if (!wp.inside_window) $('offmap').textContent = `Perseverance now (sol ${wp.sol}): ${(Math.max(-wx, wx - SIZE, 0) / 1000).toFixed(1)} km ${wx < 0 ? 'west' : 'east'} of this window`;

  // ---- route planner (A* runs in 3 Web Workers, one per mode) ----
  const workers = MODES.map(() => { const w = new Worker('worker.js'); w.postMessage({ init: 1, W: G.W, H: G.H, cell: G.cell, cost: G.cost.slice(), slope: G.slope.slice(), soft: G.soft.slice() }); return w; });
  let jid = 0;
  const solve = (wi, s, e, opts) => new Promise((res) => { const id = ++jid, w = workers[wi];
    const h = (ev) => { if (ev.data.id === id) { w.removeEventListener('message', h); res(ev.data.path); } };
    w.addEventListener('message', h); w.postMessage(Object.assign({ id, s, e, mode: MODES[wi].id }, opts)); });
  const idx = (x, y) => Math.floor(y / G.cell) * G.W + Math.floor(x / G.cell);
  const xy = (i) => [((i % G.W) + 0.5) * G.cell, (Math.floor(i / G.W) + 0.5) * G.cell];
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
      tr.innerHTML = `<td><span class="sw" style="background:${r.mode.color}"></span>${r.mode.name}${r === state.rec ? '<span class="rec">Recommended</span>' : ''}</td><td>${s.len.toFixed(0)}</td><td>${s.timeMin.toFixed(0)}</td><td>${s.energy.toFixed(1)}</td><td>${s.maxSlope.toFixed(1)}&deg;</td><td>${s.meanRisk.toFixed(2)}</td><td>${(s.softShare * 100).toFixed(0)}%</td>`
        + `<td class="${s.unsafe ? 'unsafe' : 'ok'}" title="${s.unsafe ? s.reason : 'within limits'}">${s.unsafe ? 'UNSAFE' : 'OK'}</td>`;
    }
    const msg = $('rmsg'); msg.className = '';
    if (state.clicks.length === 2 && !valid.length) { msg.className = 'err'; msg.textContent = 'No route: start or end is blocked, or they are disconnected by blocked terrain.'; }
    else if (valid.length && !state.rec) { msg.className = 'err'; msg.textContent = 'No safe route found between these points (all routes UNSAFE, none recommended).'; }
    else msg.textContent = '';
    select(state.rec || valid[0] || null);
    if (window.Tracker) window.Tracker.routesChanged();
  }
  map.on('click', async (e) => {
    const x = e.latlng.lng, y = e.latlng.lat;
    if (x < 0 || y < 0 || x >= SIZE || y >= SIZE) return;
    if (window.Tracker) window.Tracker.stop();
    if (state.clicks.length >= 2) { state.clicks = []; state.routes = []; pins.clearLayers(); render(); }
    state.clicks.push(idx(x, y));
    L.circleMarker([y, x], { radius: 6, color: '#fff', fillColor: state.clicks.length === 1 ? '#3ddc84' : '#ff5252', fillOpacity: 1 }).addTo(pins);
    if (state.clicks.length < 2) { $('rmsg').textContent = 'Start set. Click the end point.'; return; }
    $('rmsg').textContent = 'Searching...'; const t0 = performance.now();
    const paths = await Promise.all(MODES.map((m, k) => solve(k, state.clicks[0], state.clicks[1])));
    state.routes = paths.map((p, k) => p && { mode: MODES[k], path: Array.from(p), stats: SS.stats(G, p) });
    console.log(`3 searches in ${(performance.now() - t0).toFixed(0)} ms (parallel workers)`);
    render();
  });
  window.App = { map, G, MODES, state, meta, lmMarkers, xy, ll, idx, solve, select, render, $ };
})();
