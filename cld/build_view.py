"""Render causal_graph.json into a self-contained interactive HTML view (CLD v0 stage 3)."""
import json

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>How Bowling Green Thinks It Works — Community Causal Map</title>
<style>
  .viz-root {
    color-scheme: light;
    --surface-1: #fcfcfb; --page: #f9f9f7;
    --ink-1: #0b0b0b; --ink-2: #52514e; --ink-3: #898781;
    --grid: #e1e0d9; --baseline: #c3c2b7; --border: rgba(11,11,11,0.10);
    --pos: #2a78d6; --neg: #e34948;
  }
  @media (prefers-color-scheme: dark) {
    :root:where(:not([data-theme="light"])) .viz-root {
      color-scheme: dark;
      --surface-1: #1a1a19; --page: #0d0d0d;
      --ink-1: #ffffff; --ink-2: #c3c2b7; --ink-3: #898781;
      --grid: #2c2c2a; --baseline: #383835; --border: rgba(255,255,255,0.10);
      --pos: #3987e5; --neg: #e66767;
    }
  }
  :root[data-theme="dark"] .viz-root {
    color-scheme: dark;
    --surface-1: #1a1a19; --page: #0d0d0d;
    --ink-1: #ffffff; --ink-2: #c3c2b7; --ink-3: #898781;
    --grid: #2c2c2a; --baseline: #383835; --border: rgba(255,255,255,0.10);
    --pos: #3987e5; --neg: #e66767;
  }
  * { box-sizing: border-box; margin: 0; }
  body { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
  .viz-root { background: var(--page); color: var(--ink-1); min-height: 100vh; padding: 52px 20px 20px; }
  header h1 { font-size: 20px; font-weight: 650; }
  header p { color: var(--ink-2); font-size: 13px; margin-top: 4px; max-width: 72ch; }
  .legend { display: flex; flex-wrap: wrap; gap: 18px; align-items: center;
            font-size: 12px; color: var(--ink-2); margin: 12px 0 10px; }
  .legend .key { display: inline-flex; align-items: center; gap: 6px; }
  .swatch { width: 22px; height: 0; border-top: 2.5px solid; display: inline-block; }
  main { display: flex; gap: 14px; align-items: stretch; }
  #vizwrap { flex: 1 1 66%; background: var(--surface-1); border: 1px solid var(--border);
             border-radius: 10px; overflow: hidden; position: relative; min-width: 0; }
  svg { display: block; width: 100%; height: 640px; cursor: grab; }
  aside { flex: 0 0 340px; background: var(--surface-1); border: 1px solid var(--border);
          border-radius: 10px; padding: 14px; max-height: 640px; overflow-y: auto; }
  aside h2 { font-size: 13px; font-weight: 650; color: var(--ink-1); }
  aside .hint { color: var(--ink-3); font-size: 12.5px; margin-top: 8px; }
  .qspan { font-weight: 600; font-size: 13px; }
  .qfull { color: var(--ink-2); font-size: 12.5px; margin-top: 3px; }
  .qpid  { color: var(--ink-3); font-size: 11px; margin-top: 2px; }
  .quote { padding: 9px 0; border-bottom: 1px solid var(--grid); }
  .conflictnote { color: var(--ink-2); font-size: 12px; margin-top: 8px;
                  padding: 8px; border: 1px solid var(--grid); border-radius: 6px; }
  .loops { margin-top: 14px; display: flex; flex-wrap: wrap; gap: 8px; }
  .loopchip { border: 1px solid var(--border); background: var(--surface-1); color: var(--ink-2);
              border-radius: 999px; padding: 5px 12px; font-size: 12px; cursor: pointer; }
  .loopchip b { color: var(--ink-1); }
  .loopchip.active { border-color: var(--ink-2); }
  .loops-empty { color: var(--ink-3); font-size: 12.5px; margin-top: 14px; }
  .focusnote { color: var(--ink-3); font-size: 12px; margin: 0 0 8px; }
  .focusnote:empty { display: none; }
  details { margin-top: 16px; }
  summary { cursor: pointer; font-size: 13px; color: var(--ink-2); }
  table { border-collapse: collapse; margin-top: 10px; font-size: 12.5px; width: 100%;
          background: var(--surface-1); }
  th, td { text-align: left; padding: 6px 10px; border-bottom: 1px solid var(--grid); }
  th { color: var(--ink-3); font-weight: 600; font-variant-numeric: tabular-nums; }
  td.num { font-variant-numeric: tabular-nums; }
  #tooltip { position: absolute; pointer-events: none; background: var(--surface-1);
             border: 1px solid var(--border); border-radius: 6px; padding: 7px 10px;
             font-size: 12px; color: var(--ink-1); max-width: 300px; display: none;
             box-shadow: 0 2px 10px rgba(0,0,0,0.12); }
  .edgeline { fill: none; }
  .edgehit { fill: none; stroke: transparent; stroke-width: 14px; cursor: pointer; }
  .dim { opacity: 0.12; }
  text.nlabel { fill: var(--ink-2); font-size: 10.5px; pointer-events: none; }
  text.polglyph { fill: var(--ink-2); font-size: 11px; font-weight: 700; pointer-events: none; }
  circle.node { fill: var(--surface-1); stroke: var(--baseline); stroke-width: 1.6; cursor: pointer; }
  circle.node:hover { stroke: var(--ink-2); }
</style>
</head>
<body>
<div class="viz-root">
  <header>
    <h1>How Bowling Green Thinks It Works — Community Causal Map</h1>
    <p>Explicit causal claims extracted from residents' own words in the 2018 Bowling Green / Warren
       County civic conversation (607 comments, The American Assembly / Polis). Every link is backed by
       verbatim quotes — click any arrow to read them. Suggestions without an asserted mechanism are
       not drawn.</p>
    <p style="font-size:12.5px;color:var(--ink-3);line-height:1.55;margin-top:10px">Built on <a href="https://github.com/Jigsaw-Code/sensemaking-tools" style="color:var(--pos)">Google Jigsaw&rsquo;s sensemaking-tools</a>, used under Apache 2.0. Independent extension by Nitchakorn Tangs, not affiliated with or endorsed by Google or Jigsaw.</p>
  </header>
  <div class="legend" role="list">
    <span class="key"><span class="swatch" style="border-color: var(--pos)"></span>increases / promotes (+)</span>
    <span class="key"><span class="swatch" style="border-color: var(--neg)"></span>reduces / prevents (−)</span>
    <span class="key">line width = independent participants asserting it</span>
    <span class="key">circle size = times mentioned in claims</span>
  </div>
  <p id="focusnote" class="focusnote"></p>
  <main>
    <div id="vizwrap"><svg id="viz" role="img" aria-label="Causal map of Bowling Green community claims"></svg><div id="tooltip"></div></div>
    <aside id="panel"><h2>Quotes behind a link</h2>
      <p class="hint">Click any arrow to see the verbatim resident quotes asserting that causal link.
      Drag circles to untangle. Click a loop chip below to trace a feedback loop.</p></aside>
  </main>
  <div id="loopsrow" class="loops"></div>
  <details><summary>Table view — every causal link</summary><table id="edgetable">
    <thead><tr><th>Cause</th><th>±</th><th>Effect</th><th>Participants</th></tr></thead>
    <tbody></tbody></table></details>
</div>
<script>
const GRAPH = "__GRAPH__";
const svg = document.getElementById('viz');
const wrap = document.getElementById('vizwrap');
const tooltip = document.getElementById('tooltip');
const panel = document.getElementById('panel');
const css = getComputedStyle(document.querySelector('.viz-root'));
const COL = { '+': css.getPropertyValue('--pos').trim(), '-': css.getPropertyValue('--neg').trim() };
const W = wrap.clientWidth || 900, H = 640;
svg.setAttribute('viewBox', `0 0 ${W} ${H}`);

const _deg = {};
GRAPH.edges.forEach(e => { _deg[e.source]=(_deg[e.source]||0)+1; _deg[e.target]=(_deg[e.target]||0)+1; });
const _big = GRAPH.nodes.length > 45;              // only prune when the map is big enough to clutter
const _keep = id => !_big || (_deg[id]||0) >= 2;   // small maps show every variable
const _vEdges = GRAPH.edges.filter(e => _keep(e.source) && _keep(e.target));
const _shown = new Set(); _vEdges.forEach(e => { _shown.add(e.source); _shown.add(e.target); });
const nodes = GRAPH.nodes.filter(n => _shown.has(n.id)).map(n => ({...n,
  x: W/2 + (Math.random()-0.5)*W*0.8, y: H/2 + (Math.random()-0.5)*H*0.8,
  r: Math.min(22, 7 + Math.sqrt(n.n_claims)*2.4)}));
const byId = Object.fromEntries(nodes.map(n => [n.id, n]));
const edges = _vEdges.map(e => ({...e, s: byId[e.source], t: byId[e.target]}));
const _hidden = GRAPH.nodes.length - nodes.length;
const _fn = document.getElementById('focusnote');
if (_fn) _fn.textContent = _hidden > 0
  ? `Showing the ${nodes.length} connected variables. ${_hidden} one-off mentions are hidden from the map for clarity — every link is still in the table below.`
  : '';

// live force simulation — animates on load, reheats on drag
let dragNode = null, running = false;
let alpha = matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 1;
function step(k) {
  for (const a of nodes) { a.fx = (W/2 - a.x)*0.004; a.fy = (H/2 - a.y)*0.004; }
  for (let i = 0; i < nodes.length; i++) for (let j = i+1; j < nodes.length; j++) {
    const a = nodes[i], b = nodes[j];
    let dx = a.x-b.x, dy = a.y-b.y; let d2 = dx*dx+dy*dy || 1; const d = Math.sqrt(d2);
    const rep = 2600/d2; dx/=d; dy/=d;
    a.fx += dx*rep; a.fy += dy*rep; b.fx -= dx*rep; b.fy -= dy*rep;
  }
  for (const e of edges) {
    let dx = e.t.x-e.s.x, dy = e.t.y-e.s.y; const d = Math.sqrt(dx*dx+dy*dy)||1;
    const want = 120, f = (d-want)*0.012; dx/=d; dy/=d;
    e.s.fx += dx*f; e.s.fy += dy*f; e.t.fx -= dx*f; e.t.fy -= dy*f;
  }
  for (const n of nodes) {
    if (n === dragNode) continue;
    n.x = Math.max(30, Math.min(W-30, n.x + n.fx*14*k));
    n.y = Math.max(26, Math.min(H-30, n.y + n.fy*14*k));
  }
}
if (alpha === 0) { for (let it = 0; it < 420; it++) step(1 - it/420); }
function animate() {
  running = true;
  if (alpha > 0.02) { step(alpha); alpha *= 0.99; redraw(); requestAnimationFrame(animate); }
  else running = false;
}
function reheat(a) { alpha = Math.max(alpha, a); if (!running) requestAnimationFrame(animate); }

const NS = 'http://www.w3.org/2000/svg';
function el(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  for (const [k,v] of Object.entries(attrs)) e.setAttribute(k, v);
  (parent || svg).appendChild(e); return e;
}
const defs = el('defs', {});
for (const [pol, colr] of Object.entries(COL)) {
  const m = el('marker', {id: 'arr'+(pol==='+'?'p':'n'), viewBox: '0 0 10 10', refX: 9, refY: 5,
    markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse'}, defs);
  el('path', {d: 'M 0 1 L 9 5 L 0 9 z', fill: colr}, m);
}
const edgeG = el('g', {}), nodeG = el('g', {});

function edgePath(e) {
  const dx = e.t.x-e.s.x, dy = e.t.y-e.s.y, d = Math.sqrt(dx*dx+dy*dy)||1;
  const nx = -dy/d, ny = dx/d, bend = 14;
  const mx = (e.s.x+e.t.x)/2 + nx*bend, my = (e.s.y+e.t.y)/2 + ny*bend;
  const tr = e.t.r + 3, ex = e.t.x - dx/d*tr, ey = e.t.y - dy/d*tr;
  return {d: `M ${e.s.x} ${e.s.y} Q ${mx} ${my} ${ex} ${ey}`, mx, my};
}
function showTip(html, evt) {
  tooltip.innerHTML = html; tooltip.style.display = 'block';
  const r = wrap.getBoundingClientRect();
  tooltip.style.left = Math.min(evt.clientX - r.left + 14, r.width - 310) + 'px';
  tooltip.style.top  = (evt.clientY - r.top + 12) + 'px';
}
function hideTip() { tooltip.style.display = 'none'; }
function esc(s) { return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

edges.forEach((e, i) => {
  const p = edgePath(e);
  e.line = el('path', {class: 'edgeline', d: p.d, stroke: COL[e.polarity],
    'stroke-width': Math.min(6, 1.6 + (e.support-1)*1.4),
    'marker-end': `url(#arr${e.polarity==='+'?'p':'n'})`}, edgeG);
  e.glyph = el('text', {class: 'polglyph', x: p.mx, y: p.my - 3, 'text-anchor': 'middle'}, edgeG);
  e.glyph.textContent = e.polarity === '+' ? '+' : '−';
  const hit = el('path', {class: 'edgehit', d: p.d}, edgeG);
  hit.addEventListener('mousemove', evt => showTip(
    `<b>${esc(e.source)}</b> ${e.polarity==='+'?'increases':'reduces'} <b>${esc(e.target)}</b>` +
    `<br><span style="color:var(--ink-3)">${e.support} independent participant${e.support>1?'s':''}` +
    `${e.conflict ? ' · opposite polarity also asserted' : ''} · click for quotes</span>`, evt));
  hit.addEventListener('mouseleave', hideTip);
  hit.addEventListener('click', () => showQuotes(e));
  e.hit = hit;
});

nodes.forEach(n => {
  n.c = el('circle', {class: 'node', cx: n.x, cy: n.y, r: n.r}, nodeG);
  n.label = el('text', {class: 'nlabel', x: n.x, y: n.y - n.r - 5, 'text-anchor': 'middle'}, nodeG);
  n.label.textContent = n.id;
  n.c.addEventListener('mousemove', evt => showTip(
    `<b>${esc(n.id)}</b><br><span style="color:var(--ink-3)">appears in ${n.n_claims} claim${n.n_claims>1?'s':''}</span>`, evt));
  n.c.addEventListener('mouseleave', hideTip);
  let drag = null;
  n.c.addEventListener('mousedown', evt => { drag = {dx: n.x-evt.clientX, dy: n.y-evt.clientY}; dragNode = n; reheat(0.35); evt.preventDefault(); });
  window.addEventListener('mousemove', evt => {
    if (!drag) return;
    n.x = evt.clientX + drag.dx; n.y = evt.clientY + drag.dy; reheat(0.12); redraw();
  });
  window.addEventListener('mouseup', () => { drag = null; if (dragNode === n) dragNode = null; });
});

function redraw() {
  for (const n of nodes) {
    n.c.setAttribute('cx', n.x); n.c.setAttribute('cy', n.y);
    n.label.setAttribute('x', n.x); n.label.setAttribute('y', n.y - n.r - 5);
  }
  for (const e of edges) {
    const p = edgePath(e);
    e.line.setAttribute('d', p.d); e.hit.setAttribute('d', p.d);
    e.glyph.setAttribute('x', p.mx); e.glyph.setAttribute('y', p.my - 3);
  }
}

function showQuotes(e) {
  let h = `<h2>${esc(e.source)} ${e.polarity==='+'?'→ increases →':'→ reduces →'} ${esc(e.target)}</h2>`;
  if (e.conflict) h += `<div class="conflictnote">Residents also asserted the opposite polarity for this pair — see table view.</div>`;
  for (const q of e.quotes) {
    h += `<div class="quote"><div class="qspan">“${esc(q.span)}”</div>` +
         `<div class="qfull">${esc(q.comment)}</div>` +
         `<div class="qpid">participant ${esc(q.participant_id)}</div></div>`;
  }
  panel.innerHTML = h;
}

// loops
const loopsRow = document.getElementById('loopsrow');
if (GRAPH.loops.length === 0) {
  const d = document.createElement('div'); d.className = 'loops-empty';
  d.textContent = 'No closed feedback loops at current thresholds — residents assert single links; loops would close only across more claims (finding, not failure).';
  loopsRow.replaceWith(d);
} else {
  GRAPH.loops.forEach((L, i) => {
    const chip = document.createElement('button'); chip.className = 'loopchip';
    chip.innerHTML = `<b>${L.type === 'R' ? 'R' : 'B'}${i+1}</b> ${L.nodes.map(esc).join(' → ')} ↺`;
    chip.title = L.type === 'R' ? 'Reinforcing loop' : 'Balancing loop';
    chip.addEventListener('click', () => highlightLoop(L, chip));
    loopsRow.appendChild(chip);
  });
}
let activeChip = null;
function highlightLoop(L, chip) {
  document.querySelectorAll('.loopchip').forEach(c => c.classList.remove('active'));
  if (activeChip === chip) { activeChip = null; edges.forEach(e => e.line.classList.remove('dim')); nodes.forEach(n => { n.c.classList.remove('dim'); n.label.classList.remove('dim'); }); return; }
  activeChip = chip; chip.classList.add('active');
  const inLoop = new Set();
  for (let i = 0; i < L.nodes.length; i++) inLoop.add(L.nodes[i] + '→' + L.nodes[(i+1) % L.nodes.length]);
  const nodeSet = new Set(L.nodes);
  edges.forEach(e => e.line.classList.toggle('dim', !inLoop.has(e.source + '→' + e.target)));
  nodes.forEach(n => { const on = nodeSet.has(n.id); n.c.classList.toggle('dim', !on); n.label.classList.toggle('dim', !on); });
}

// table view
const tbody = document.querySelector('#edgetable tbody');
[...GRAPH.edges].sort((a,b) => b.support - a.support).forEach(e => {
  const tr = document.createElement('tr');
  tr.innerHTML = `<td>${esc(e.source)}</td><td>${e.polarity}</td><td>${esc(e.target)}</td>` +
                 `<td class="num">${e.support}${e.conflict ? ' (conflict)' : ''}</td>`;
  tbody.appendChild(tr);
});

if (alpha > 0.02) requestAnimationFrame(animate); else redraw();
</script>
</body>
</html>
"""


def main() -> None:
  import sys
  src = sys.argv[1] if len(sys.argv) > 1 else "data/causal_graph.json"
  out = sys.argv[2] if len(sys.argv) > 2 else "cld_view.html"
  graph = json.load(open(src, encoding="utf-8"))
  html = TEMPLATE.replace('"__GRAPH__"', json.dumps(graph, ensure_ascii=False))
  with open(out, "w", encoding="utf-8") as f:
    f.write(html)
  print(f"wrote {out} nodes={len(graph['nodes'])} "
        f"edges={len(graph['edges'])} loops={len(graph['loops'])}")


if __name__ == "__main__":
  main()
