// node web/test_astar.js  -- synthetic grids; no deps
const assert = require('assert'), fs = require('fs'), path = require('path');
const SS = require('./astar.js');
const params = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'config', 'params.json'), 'utf8'));
for (const sec of ['routing', 'tracker']) for (const k of Object.keys(SS.PARAMS[sec])) assert.strictEqual(SS.PARAMS[sec][k], params[sec][k], `PARAMS drift: ${sec}.${k}`);
const grid = (W, H, f) => { const cost = new Uint8Array(W * H); for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) cost[y * W + x] = f(x, y);
  return { W, H, cell: 10, cost, slope: new Uint8Array(W * H), soft: new Uint8Array(W * H) }; };
const id = (G, x, y) => y * G.W + x;
let n = 0; const ok = (m) => console.log('PASS', ++n, m);
const run = (G, m) => { const p = SS.astar(G, id(G, 0, 40), id(G, 79, 40), m); return { mode: m, path: p, stats: SS.stats(G, p) }; };

// 1. wall with a gap: route goes around, never touches a wall cell
let G = grid(40, 40, (x, y) => (x === 20 && y !== 35 ? 255 : 10));
for (const m of ['safe', 'fast', 'power']) {
  const p = SS.astar(G, id(G, 2, 5), id(G, 37, 5), m);
  assert(p && p.every(i => G.cost[i] !== 255), m + ' crosses wall'); assert(SS.stats(G, p).len > 350, m + ' not detouring');
}
ok('route detours around a wall (3 modes)');
// 2. fully walled -> no route; blocked end -> no route
G = grid(40, 40, (x) => (x === 20 ? 255 : 10));
assert.strictEqual(SS.astar(G, id(G, 2, 5), id(G, 37, 5), 'safe'), null); ok('fully walled -> null');
G = grid(40, 40, (x, y) => (x === 37 && y === 5 ? 255 : 10));
assert.strictEqual(SS.astar(G, id(G, 2, 5), id(G, 37, 5), 'fast'), null); ok('blocked end -> null');
// 3. high-risk band (not blocked) with a clean corridor in row 0: fast/power go through -> UNSAFE; Recommended skips it
const band = (gap) => grid(80, 80, (x, y) => (x >= 30 && x < 50 && (!gap || y > 0) ? 230 : 10));
G = band(true);
const routes = ['safe', 'fast', 'power'].map(m => run(G, m));
const by = Object.fromEntries(routes.map(r => [r.mode, r]));
assert(by.fast.stats.unsafe && /risk/.test(by.fast.stats.reason), 'fast should be UNSAFE: ' + by.fast.stats.reason);
assert(!by.safe.stats.unsafe, 'safe route should be OK');
assert(by.fast.stats.len < by.safe.stats.len, 'fast route should be shorter (it cuts through the band)');
assert.strictEqual(SS.recommend(routes).mode, 'safe'); ok('band route flagged UNSAFE, Recommended skips it (' + by.fast.stats.reason + ')');
// 4. no alternative: every route UNSAFE -> no recommendation
G = band(false);
const all = ['safe', 'fast', 'power'].map(m => run(G, m));
assert(all.every(r => r.stats.unsafe)); assert.strictEqual(SS.recommend(all), null); ok('all routes UNSAFE -> no recommendation');
// 5. real WIDE grid (1318x1250, 40 m): far-apart valid cells in the SW and NE corners; all 3 modes find a route that avoids blocked/no-data cells,
//    and the slowest search stays under the 3 s target (limit 6 s here so a slow CI machine does not flake)
const wd = path.join(__dirname, 'data', 'wide'), mw = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', 'meta_wide.json'), 'utf8'));
const rb = (n) => new Uint8Array(fs.readFileSync(path.join(wd, n + '.bin')));
const GW = { W: mw.width, H: mw.height, cell: mw.cell_m, cx: mw.cell_m_x, cy: mw.cell_m_y, cost: rb('cost'), slope: rb('slope'), soft: rb('softness') };
assert.strictEqual(GW.cost.length, GW.W * GW.H);
const nearest = (x0, y0, dx, dy) => { for (let k = 0; k < 400; k++) for (let a = 0; a <= k; a++) { const i = (y0 + dy * (k - a)) * GW.W + x0 + dx * a; if (GW.cost[i] !== 255) return i; } };
const wS = nearest(10, 10, 1, 1), wE = nearest(GW.W - 11, GW.H - 11, -1, -1);
let worst = 0;
for (const m of ['safe', 'fast', 'power']) {
  const t0 = Date.now(), p = SS.astar(GW, wS, wE, m), dt = Date.now() - t0; worst = Math.max(worst, dt);
  assert(p && p.every(i => GW.cost[i] !== 255), 'wide ' + m + ' failed'); assert(SS.stats(GW, p).len > 40000, 'wide route too short');
}
assert(worst < 6000, 'wide A* too slow: ' + worst + ' ms'); ok(`wide 40 m grid corner-to-corner: 3 modes OK, slowest ${worst} ms`);
console.log('all tests passed');
