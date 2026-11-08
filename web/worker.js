// Web Worker: one A* search per message (too slow for the UI thread). Holds both grids: 'det' (10 m) and 'wide' (40 m).
importScripts('astar.js');
const Gs = {};
onmessage = (e) => {
  const m = e.data;
  if (m.init) { Gs[m.init] = { W: m.W, H: m.H, cell: m.cell, cx: m.cx, cy: m.cy, cost: m.cost, slope: m.slope, soft: m.soft }; return; }
  const G = Gs[m.grid];
  const g = m.cost ? Object.assign({}, G, { cost: m.cost }) : G;  // optional cost override (re-plan with blocked patch)
  const path = SS.astar(g, m.s, m.e, m.mode, { ignoreStart: !!m.ignoreStart });
  postMessage({ id: m.id, path });
};
