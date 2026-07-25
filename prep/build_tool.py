"""Build tool.html — the BYO-key interactive version of the causal map page.

Takes the renderer template from cld/build_view.py, makes the render re-runnable,
adds an upload/key control panel and a fully client-side extraction pipeline
(browser -> Gemini API directly; no server anywhere).

Run from repo root: python prep/build_tool.py
"""
import json
import re
import sys

sys.path.insert(0, ".")
from cld.build_view import TEMPLATE  # noqa: E402

FALLBACK_KEY = ""  # a referrer-restricted FREE-project key; never a billed key

PANEL = r"""
  <details id="toolpanel">
    <summary>Run this on your own data — no server, your browser talks to Google directly</summary>
    <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:10px 0;
                background:var(--surface-1);border:1px solid var(--border);border-radius:10px;padding:12px">
      <input type="file" id="csvfile" accept=".csv" style="font-size:12.5px;color:var(--ink-2)">
      <select id="coltext" style="display:none;font-size:12.5px"></select>
      <select id="colpid" style="display:none;font-size:12.5px"></select>
      <input type="password" id="apikey" size="34" style="font-size:12.5px;padding:5px 8px;border:1px solid var(--border);border-radius:6px;background:var(--page);color:var(--ink-1)">
      <button id="runbtn" disabled style="font-size:12.5px;padding:6px 14px;border-radius:999px;border:1px solid var(--border);background:var(--surface-1);color:var(--ink-1);cursor:pointer">Extract causal map</button>
      <span id="status" style="font-size:12.5px;color:var(--ink-2)"></span>
      <p style="flex-basis:100%;font-size:12px;color:var(--ink-3);margin:2px 0 0">
        CSV needs one column of free-text responses (a participant-id column is optional).
        Everything runs in this tab: your file and your key go only to Google's Gemini API, never to us.
        Shared free key (when configured) is community quota — it can run out; bring your own for reliability.</p>
    </div>
  </details>
"""

PIPELINE_JS = r"""
// ---------- BYO-key client-side pipeline ----------
const FALLBACK_KEY = "__FALLBACK_KEY__";
const TOOL_MODEL = "gemini-3.1-flash-lite";
const EXTRACT_HEAD = "You are auditing community comments for EXPLICIT causal claims.\n" +
  "A causal claim exists only when the text itself asserts one thing influences another " +
  "(because, causes, leads to, results in, brings, keeps, attracts, drives away, or unmistakable if-then). " +
  "Do NOT infer mechanisms behind bare suggestions or wishes ('we need X' alone = no claim).\n" +
  "Name 'cause' and 'effect' as NEUTRAL variables naming a quantity that can rise or fall " +
  "(e.g. 'Sidewalk Availability', 'Traffic Congestion', 'Driver Confusion'), NEVER a directional " +
  "phrase ('lack of sidewalks', 'less traffic'). Then set 'polarity' by how those two quantities " +
  "actually co-move in the sentence: '+' if they rise and fall together, '-' if one rises as the other falls.\n" +
  "Example: 'The lack of sidewalks discourages walking' -> cause 'Sidewalk Availability', effect " +
  "'Walking', polarity '+' (more sidewalks -> more walking). 'Bike lanes caused confusion for drivers' " +
  "-> cause 'Bike Lanes', effect 'Driver Confusion', polarity '+' (more lanes -> more confusion).\n" +
  'Return ONLY JSON: {"claims":[{"comment_index":int,"cause":str,"effect":str,' +
  '"polarity":"+ or -","span":"verbatim words asserting it"}]}\nComments:\n';

const $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
function setStatus(t) { $('status').textContent = t; }

let csvRows = null, csvHeader = null;

function parseCSV(text) {
  const rows = []; let row = [], cur = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"') { if (text[i+1] === '"') { cur += '"'; i++; } else q = false; } else cur += c; }
    else if (c === '"') q = true;
    else if (c === ',') { row.push(cur); cur = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i+1] === '\n') i++;
      row.push(cur); if (row.some(x => x !== '')) rows.push(row); row = []; cur = '';
    } else cur += c;
  }
  row.push(cur); if (row.some(x => x !== '')) rows.push(row);
  return rows;
}

$('csvfile').addEventListener('change', async evt => {
  const f = evt.target.files[0]; if (!f) return;
  const rows = parseCSV(await f.text());
  if (rows.length < 2) { setStatus('CSV appears empty.'); return; }
  csvHeader = rows[0]; csvRows = rows.slice(1);
  const mkOpts = (sel, extra) => {
    sel.innerHTML = extra;
    csvHeader.forEach((h, i) => { const o = document.createElement('option'); o.value = i; o.textContent = h; sel.appendChild(o); });
    sel.style.display = '';
  };
  mkOpts($('coltext'), '<option value="">— text column —</option>');
  mkOpts($('colpid'), '<option value="">participant col (optional)</option>');
  // guess: text col = widest average cell; pid col = header name match
  let best = 0, bestw = -1;
  csvHeader.forEach((h, i) => {
    const w = csvRows.slice(0, 40).reduce((s, r) => s + (r[i] || '').length, 0);
    if (w > bestw) { bestw = w; best = i; }
  });
  $('coltext').value = best;
  const pid = csvHeader.findIndex(h => /participant|author|user|(^|[-_ ])id($|[-_ ])/i.test(h));
  if (pid >= 0) $('colpid').value = pid;
  $('runbtn').disabled = false;
  setStatus(csvRows.length + ' rows loaded.');
});

async function llm(prompt, key) {
  for (let a = 0; a < 5; a++) {
    let r;
    try {
      r = await fetch('https://generativelanguage.googleapis.com/v1beta/models/' + TOOL_MODEL + ':generateContent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-goog-api-key': key },
        body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { responseMimeType: 'application/json', temperature: 0 } })
      });
    } catch (e) { setStatus('network hiccup — retrying'); await sleep(4000); continue; }
    if (r.status === 429) { setStatus('rate-limited — pausing 30s (attempt ' + (a+1) + '/5)'); await sleep(30000); continue; }
    if (!r.ok) throw new Error('API ' + r.status + ': ' + (await r.text()).slice(0, 160));
    const j = await r.json();
    const t = (((j.candidates || [])[0] || {}).content || {}).parts;
    const text = t ? t.map(p => p.text || '').join('') : '';
    if (!text) throw new Error('empty model response');
    return JSON.parse(text);
  }
  throw new Error('still rate-limited after 5 attempts — try your own key or wait a minute');
}

function buildGraph(claims) {
  const nodeClaims = {}, edgeMap = new Map();
  for (const c of claims) {
    if (c.cause === c.effect) continue;
    nodeClaims[c.cause] = (nodeClaims[c.cause] || 0) + 1;
    nodeClaims[c.effect] = (nodeClaims[c.effect] || 0) + 1;
    const k = JSON.stringify([c.cause, c.effect, c.polarity]);
    if (!edgeMap.has(k)) edgeMap.set(k, { u: c.cause, v: c.effect, pol: c.polarity,
                                          participants: new Set(), quotes: [] });
    const e = edgeMap.get(k);
    e.participants.add(c.participant_id);
    e.quotes.push({ participant_id: c.participant_id, span: c.span, comment: c.comment,
                    raw_cause: c.raw_cause || c.cause, raw_effect: c.raw_effect || c.effect });
  }
  const chosen = new Map();
  for (const e of edgeMap.values()) {
    const uk = JSON.stringify([e.u, e.v]);
    const cur = chosen.get(uk);
    if (cur) {
      cur.conflict = true;
      if (e.participants.size > cur.participants.size) { e.conflict = true; chosen.set(uk, e); }
    } else { e.conflict = false; chosen.set(uk, e); }
  }
  const edges = [...chosen.values()].map(e => ({ source: e.u, target: e.v, polarity: e.pol,
    support: e.participants.size, conflict: e.conflict, quotes: e.quotes }));
  const loops = findLoops(edges);
  return { nodes: Object.keys(nodeClaims).map(id => ({ id, n_claims: nodeClaims[id] })), edges, loops };
}

function findLoops(edges) {
  const adj = {}; edges.forEach(e => { (adj[e.source] = adj[e.source] || []).push(e); });
  const loops = [];
  function dfs(start, node, path, sign) {
    if (loops.length >= 50 || path.length > 6) return;
    for (const e of (adj[node] || [])) {
      const s2 = sign * (e.polarity === '+' ? 1 : -1);
      if (e.target === start && path.length >= 2) loops.push({ nodes: [...path], type: s2 > 0 ? 'R' : 'B' });
      else if (e.target > start && !path.includes(e.target)) dfs(start, e.target, [...path, e.target], s2);
    }
  }
  Object.keys(adj).forEach(s => dfs(s, s, [s], 1));
  return loops;
}

$('runbtn').addEventListener('click', async () => {
  const key = $('apikey').value.trim() || FALLBACK_KEY;
  if (!key) { setStatus('paste a Gemini API key first (aistudio.google.com/apikey — free)'); return; }
  const ti = parseInt($('coltext').value); const pi = $('colpid').value === '' ? -1 : parseInt($('colpid').value);
  if (isNaN(ti)) { setStatus('choose the text column'); return; }
  const rows = csvRows.map((r, i) => ({ pid: pi >= 0 ? (r[pi] || 'p' + i) : 'p' + i, text: (r[ti] || '').trim() }))
                      .filter(r => r.text.length > 5);
  if (!rows.length) { setStatus('no usable text rows'); return; }
  $('runbtn').disabled = true;
  try {
    const B = 38, claims = [];
    for (let s = 0; s < rows.length; s += B) {
      const chunk = rows.slice(s, s + B);
      setStatus('extracting ' + (s + 1) + '–' + Math.min(s + B, rows.length) + ' of ' + rows.length + '…');
      const listing = chunk.map((r, i) => '[' + i + '] ' + r.text).join('\n');
      const out = await llm(EXTRACT_HEAD + listing, key);
      for (const c of (out.claims || [])) {
        if (typeof c.comment_index === 'number' && chunk[c.comment_index] && (c.polarity === '+' || c.polarity === '-'))
          claims.push({ participant_id: chunk[c.comment_index].pid, comment: chunk[c.comment_index].text,
                        cause: String(c.cause).trim(), effect: String(c.effect).trim(),
                        polarity: c.polarity, span: String(c.span || '').trim() });
      }
    }
    if (!claims.length) { setStatus('no explicit causal claims found — that itself is a finding.'); $('runbtn').disabled = false; return; }
    setStatus('canonicalizing ' + claims.length + ' claims…');
    const phrases = [...new Set(claims.flatMap(c => [c.cause, c.effect]))].slice(0, 400);
    const canon = await llm(
      'These phrases are variables from causal claims in a public conversation. Merge phrases that mean the same underlying variable.\n' +
      "Rules: canonical names are short Title-Case noun phrases (2-4 words), specific enough to distinguish different variables. " +
      "PRESERVE each phrase's semantic direction — merge only true synonyms; NEVER map a phrase to a name that means its opposite " +
      "(do not turn 'Driver Confusion' into 'Intersection Navigation', or 'Sidewalk Availability' into 'Missing Sidewalks'). " +
      'Every input phrase must appear exactly once as a key.\nReturn ONLY JSON: {"mapping": {"<input phrase>": "<Canonical Name>"}}\nPhrases:\n' +
      phrases.map(p => '- ' + p).join('\n'), key);
    const map = canon.mapping || {};
    for (const c of claims) {
      c.raw_cause = c.cause; c.raw_effect = c.effect;
      c.cause = map[c.cause] || c.cause; c.effect = map[c.effect] || c.effect;
    }
    GRAPH = buildGraph(claims);
    boot();
    setStatus('done — ' + claims.length + ' claims, ' + GRAPH.nodes.length + ' variables, ' +
              GRAPH.edges.length + ' links, ' + GRAPH.loops.length + ' loops.');
  } catch (err) { setStatus('stopped: ' + err.message); }
  $('runbtn').disabled = false;
});

$('apikey').placeholder = FALLBACK_KEY
  ? 'Your Gemini API key (optional — shared free key otherwise)'
  : 'Your Gemini API key (free at aistudio.google.com/apikey)';
"""


def main() -> None:
  graph = json.load(open("data/causal_graph.json", encoding="utf-8"))
  t = TEMPLATE

  t = t.replace(
      "<title>How Bowling Green Thinks It Works — Community Causal Map</title>",
      "<title>Community Causal Map — run it on your data</title>")

  # The template header is Bowling-Green-specific; on the BYO tool the map is only a
  # demo until the visitor loads their own CSV, so make the header honest in both states.
  t = t.replace(
      "<h1>How Bowling Green Thinks It Works — Community Causal Map</h1>",
      "<h1>Community Causal Map — from your own words</h1>")
  t = re.sub(
      r"<p>Explicit causal claims extracted.*?not drawn\.</p>",
      "<p>Upload a CSV of open-ended responses and run it with your own Gemini API key — the map "
      "is built entirely in your browser, calling Google directly; nothing is uploaded to any "
      "server. It shows a demo of the 2018 Bowling Green / Warren County civic conversation "
      "(607 comments, The American Assembly / Polis) until you load your own data. Every link is "
      "backed by verbatim quotes — click any arrow to read them; suggestions without an asserted "
      "mechanism are not drawn.</p>",
      t, count=1, flags=re.S)

  t = t.replace("<main>", PANEL + "\n  <main>", 1)

  # demo graph + reassignable GRAPH
  t = t.replace('const GRAPH = "__GRAPH__";',
                'const DEMO_GRAPH = "__GRAPH__";\nlet GRAPH = DEMO_GRAPH;')

  # make loops row + table rebuildable
  t = t.replace("const loopsRow = document.getElementById('loopsrow');",
                "const loopsRow = document.getElementById('loopsrow');\nif (loopsRow) loopsRow.innerHTML = '';")
  t = t.replace("loopsRow.replaceWith(d);", "loopsRow.appendChild(d);")
  t = t.replace("const tbody = document.querySelector('#edgetable tbody');",
                "const tbody = document.querySelector('#edgetable tbody');\ntbody.innerHTML = '';")

  # wrap the whole render tail into boot()
  start = t.index("const nodes = GRAPH.nodes.map")
  kick = "if (alpha > 0.02) requestAnimationFrame(animate); else redraw();"
  end = t.index(kick) + len(kick)
  body = t[start:end]
  t = t[:start] + "function boot() {\nsvg.innerHTML = '';\n" + body + "\n}\nboot();\n" + t[end:]

  # append pipeline
  t = t.replace("</script>", PIPELINE_JS.replace("__FALLBACK_KEY__", FALLBACK_KEY) + "\n</script>", 1)

  html = t.replace('"__GRAPH__"', json.dumps(graph, ensure_ascii=False))
  open("tool.html", "w", encoding="utf-8").write(html)
  print("wrote tool.html (fallback key %s)" % ("SET" if FALLBACK_KEY else "not set"))


if __name__ == "__main__":
  main()
