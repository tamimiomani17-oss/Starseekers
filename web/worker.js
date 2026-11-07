// Web Worker: one A* search per message (a search takes ~300 ms on the 1000x1000 grid, too slow for the UI thread).
importScripts('astar.js');
let G = null;
onmessage = (e) => {
  const m = e.data;
  if (m.init) { G = { W: m.W, H: m.H, cell: m.cell, cost: m.cost, slope: m.slope, soft: m.soft }; return; }
  const g = m.cost ? Object.assign({}, G, { cost: m.cost }) : G;  // optional cost override (re-plan with blocked patch)
  const path = SS.astar(g, m.s, m.e, m.mode, { ignoreStart: !!m.ignoreStart });
  postMessage({ id: m.id, path });
};
