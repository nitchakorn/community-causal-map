"""Canonicalize causal claims and build the signed digraph with loops (CLD v0 stage 2)."""
import collections
import json
import os

import networkx as nx
from google import genai
from google.genai import types

MODEL = "gemini-flash-latest"
MAX_LOOP_LEN = 6


def canonicalize(client: genai.Client, phrases: list[str]) -> dict[str, str]:
  listing = "\n".join(f"- {p}" for p in sorted(set(phrases)))
  prompt = (
      "These phrases are variables from causal claims in a civic conversation about "
      "Bowling Green, Kentucky. Merge phrases that mean the same underlying variable.\n"
      "Rules: canonical names are short Title-Case noun phrases (2-4 words), neutral "
      "direction (e.g. 'Traffic Congestion' not 'less traffic'), specific enough to "
      "distinguish genuinely different variables. Every input phrase must appear exactly "
      "once as a key.\n"
      'Return ONLY JSON: {"mapping": {"<input phrase>": "<Canonical Name>", ...}}\n'
      "Phrases:\n" + listing
  )
  resp = client.models.generate_content(
      model=MODEL,
      contents=prompt,
      config=types.GenerateContentConfig(
          response_mime_type="application/json", temperature=0
      ),
  )
  return json.loads(resp.text)["mapping"]


def main() -> None:
  key = os.environ.get("GEMINI_API_KEY") or open(".gemini_key", encoding="utf-8").read().strip()
  client = genai.Client(api_key=key)
  claims = json.load(open("data/claims_raw.json", encoding="utf-8"))
  phrases = [c["cause"] for c in claims] + [c["effect"] for c in claims]
  mapping = canonicalize(client, phrases)
  missing = [p for p in set(phrases) if p not in mapping]
  for p in missing:
    mapping[p] = p.title()[:40]
  print(f"canonical vars: {len(set(mapping.values()))} from {len(set(phrases))} phrases"
        f" ({len(missing)} unmapped, kept as-is)")

  edges: dict[tuple, dict] = {}
  node_claims = collections.Counter()
  for c in claims:
    u, v = mapping[c["cause"]], mapping[c["effect"]]
    if u == v:
      continue
    node_claims[u] += 1
    node_claims[v] += 1
    e = edges.setdefault((u, v, c["polarity"]), {"participants": set(), "quotes": []})
    e["participants"].add(c["participant_id"])
    e["quotes"].append({
        "participant_id": c["participant_id"],
        "span": c["span"],
        "comment": c["comment"],
        "raw_cause": c["cause"],
        "raw_effect": c["effect"],
    })

  g = nx.DiGraph()
  for (u, v, pol), e in edges.items():
    if g.has_edge(u, v):  # keep the better-supported polarity, record conflict
      if len(e["participants"]) <= len(g[u][v]["participants"]):
        g[u][v]["conflict"] = True
        continue
      e = dict(e)
      e["conflict"] = True
      g.remove_edge(u, v)
      g.add_edge(u, v, polarity=pol, **e)
    else:
      g.add_edge(u, v, polarity=pol, **e)

  loops = []
  for cyc in nx.simple_cycles(g):
    if len(cyc) > MAX_LOOP_LEN:
      continue
    sign = 1
    for a, b in zip(cyc, cyc[1:] + cyc[:1]):
      sign *= 1 if g[a][b]["polarity"] == "+" else -1
    loops.append({"nodes": cyc, "type": "R" if sign > 0 else "B"})

  out = {
      "nodes": [
          {"id": n, "n_claims": node_claims[n]} for n in g.nodes
      ],
      "edges": [
          {
              "source": u,
              "target": v,
              "polarity": d["polarity"],
              "support": len(d["participants"]),
              "conflict": bool(d.get("conflict")),
              "quotes": d["quotes"],
          }
          for u, v, d in g.edges(data=True)
      ],
      "loops": loops,
  }
  json.dump(out, open("data/causal_graph.json", "w", encoding="utf-8"), indent=1)
  multi = sum(1 for e in out["edges"] if e["support"] >= 2)
  print(f"DONE nodes={g.number_of_nodes()} edges={g.number_of_edges()} "
        f"(support>=2: {multi}) loops={len(loops)} "
        f"R={sum(1 for l in loops if l['type']=='R')} B={sum(1 for l in loops if l['type']=='B')}")


if __name__ == "__main__":
  main()
