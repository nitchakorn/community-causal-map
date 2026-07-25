"""Aggregate the fine-grained variable graph up to ~10 themes (CLD v0 — "small map" view).

The variable->theme mapping below is curated by hand (not an LLM call), so it is fully
auditable and costs nothing to run. Every one of the 97 variables is assigned to exactly
one theme; edges are re-aggregated between themes (intra-theme links dropped), polarity and
verbatim-quote provenance preserved. Output schema matches causal_graph.json so build_view.py
can render it unchanged.

Run from repo root:  python cld/build_themes.py
"""
import collections
import json

THEME = {
    # Traffic & Mobility
    "Access Road Infrastructure": "Traffic & Mobility",
    "Highway Exit Infrastructure": "Traffic & Mobility",
    "Parking Infrastructure": "Traffic & Mobility",
    "Roadway Flooding": "Traffic & Mobility",
    "Traffic Congestion": "Traffic & Mobility",
    "Traffic Disruptions": "Traffic & Mobility",
    "Traffic Flow": "Traffic & Mobility",
    "Traffic Signal Infrastructure": "Traffic & Mobility",
    "Travel Activity": "Traffic & Mobility",
    "Travel Time": "Traffic & Mobility",
    "Commercial Signage Infrastructure": "Traffic & Mobility",
    # Road Safety & Enforcement
    "Driver Distraction": "Road Safety & Enforcement",
    "Driving Safety": "Road Safety & Enforcement",
    "DUI Offenses": "Road Safety & Enforcement",
    "Pedestrian Safety": "Road Safety & Enforcement",
    "Traffic Accidents": "Road Safety & Enforcement",
    "Traffic Law Compliance": "Road Safety & Enforcement",
    "Traffic Law Enforcement": "Road Safety & Enforcement",
    "Traffic Regulations": "Road Safety & Enforcement",
    # Public Space & Environment
    "Pedestrian and Bike Infrastructure": "Public Space & Environment",
    "Public Parks and Greenery": "Public Space & Environment",
    "Street Lighting Infrastructure": "Public Space & Environment",
    "Lighting and Glare": "Public Space & Environment",
    "City Aesthetics": "Public Space & Environment",
    "Visual Landscape Quality": "Public Space & Environment",
    "Environmental Litter": "Public Space & Environment",
    "Building Preservation Codes": "Public Space & Environment",
    "Waste Management Infrastructure": "Public Space & Environment",
    "Arts and Culture Presence": "Public Space & Environment",
    # Crime, Drugs & Justice
    "Community Crime Rate": "Crime, Drugs & Justice",
    "Correctional System Strain": "Crime, Drugs & Justice",
    "Crime Victimization": "Crime, Drugs & Justice",
    "Criminal Sentence Severity": "Crime, Drugs & Justice",
    "Illicit Drug Availability": "Crime, Drugs & Justice",
    "Opioid Epidemic": "Crime, Drugs & Justice",
    "Pain Management Efforts": "Crime, Drugs & Justice",
    "Prescription Access": "Crime, Drugs & Justice",
    "Property Theft Rate": "Crime, Drugs & Justice",
    "Substance Abuse": "Crime, Drugs & Justice",
    "Cannabis Legalization": "Crime, Drugs & Justice",
    "Recreational Cannabis Availability": "Crime, Drugs & Justice",
    # Local Economy & Jobs
    "Commercial Customer Traffic": "Local Economy & Jobs",
    "Commercial Tenant Turnover": "Local Economy & Jobs",
    "Employment Availability": "Local Economy & Jobs",
    "Employment Regulations": "Local Economy & Jobs",
    "Local Business Activity": "Local Economy & Jobs",
    "Local Business Growth": "Local Economy & Jobs",
    "Local Market Competition": "Local Economy & Jobs",
    "Regional Economic Growth": "Local Economy & Jobs",
    "Retail Infrastructure": "Local Economy & Jobs",
    "Tourism Activity": "Local Economy & Jobs",
    "Workforce Business Skills": "Local Economy & Jobs",
    "Workforce Mobilization": "Local Economy & Jobs",
    "College Graduate Retention": "Local Economy & Jobs",
    # Government Finance
    "Government Financial Auditing": "Government Finance",
    "Government Financial Burden": "Government Finance",
    "Local Government Revenue": "Government Finance",
    "Local Tax Base": "Government Finance",
    "Local Tax Rates": "Government Finance",
    "Public Financial Expenditure": "Government Finance",
    "Municipal Energy Consumption": "Government Finance",
    # Housing & Land Use
    "Affordable Housing Programs": "Housing & Land Use",
    "Campus Student Housing": "Housing & Land Use",
    "Land Usability": "Housing & Land Use",
    "Urban Land Development": "Housing & Land Use",
    "Urban Sprawl": "Housing & Land Use",
    # Education & Youth
    "Educational Opportunities": "Education & Youth",
    "K-12 School Access": "Education & Youth",
    "K-12 School Quality": "Education & Youth",
    "School District Policy": "Education & Youth",
    "School Funding Policy": "Education & Youth",
    "Youth Enrichment": "Education & Youth",
    "Youth Programs": "Education & Youth",
    "Higher Education Cost": "Education & Youth",
    "College Student Population": "Education & Youth",
    "University Financial Resources": "Education & Youth",
    "University Governance": "Education & Youth",
    # Health & Social Services
    "Healthcare Staffing": "Health & Social Services",
    "Healthcare Education Capacity": "Health & Social Services",
    "Patient Suffering Level": "Health & Social Services",
    "Community Resource Provision": "Health & Social Services",
    "Community Well-Being Outcomes": "Health & Social Services",
    "Senior Community Services": "Health & Social Services",
    "Public Assistance Abuse": "Health & Social Services",
    "Public Assistance Eligibility": "Health & Social Services",
    # Community & Governance
    "Community Cohesion": "Community & Governance",
    "Community Identity": "Community & Governance",
    "Community Poverty Level": "Community & Governance",
    "Community Quality of Life": "Community & Governance",
    "Civil Rights Ordinances": "Community & Governance",
    "Refugee Population": "Community & Governance",
    "Municipal Civic Issues": "Community & Governance",
    "Municipal Civic Programs": "Community & Governance",
    "Municipal Ordinances": "Community & Governance",
    "Representative Municipal Governance": "Community & Governance",
    "Media Anonymity": "Community & Governance",
    "Media Bias Perception": "Community & Governance",
}


def main() -> None:
  g = json.load(open("data/causal_graph.json", encoding="utf-8"))

  missing = [n["id"] for n in g["nodes"] if n["id"] not in THEME]
  if missing:
    raise SystemExit(f"Unmapped variables (fix THEME): {missing}")

  # claims per theme (for node size)
  theme_claims = collections.Counter()
  for n in g["nodes"]:
    theme_claims[THEME[n["id"]]] += n["n_claims"]

  # aggregate edges between themes, keeping per-(theme,theme,polarity) provenance
  agg = {}
  for e in g["edges"]:
    ts, tt = THEME[e["source"]], THEME[e["target"]]
    if ts == tt:
      continue  # drop intra-theme links
    key = (ts, tt, e["polarity"])
    a = agg.setdefault(key, {"participants": set(), "quotes": []})
    for q in e["quotes"]:
      a["participants"].add(q["participant_id"])
      a["quotes"].append({**q, "raw_cause": e["source"], "raw_effect": e["target"]})

  # collapse to one directed edge per (theme,theme): dominant polarity wins, conflict flagged
  best = {}
  for (ts, tt, pol), a in agg.items():
    k = (ts, tt)
    cur = best.get(k)
    if cur is None:
      best[k] = {"polarity": pol, **a, "conflict": False}
    else:
      cur["conflict"] = True
      if len(a["participants"]) > len(cur["participants"]):
        best[k] = {"polarity": pol, **a, "conflict": True}

  # At the theme level, only elevate a link that multiple INDEPENDENT residents drew —
  # a single cross-theme claim is noise once you aggregate 97 variables into 10 themes.
  MIN_SUPPORT = 2
  used = set()
  edges = []
  for (ts, tt), d in best.items():
    if len(d["participants"]) < MIN_SUPPORT:
      continue
    used.update([ts, tt])
    edges.append({
        "source": ts, "target": tt, "polarity": d["polarity"],
        "support": len(d["participants"]), "conflict": d["conflict"], "quotes": d["quotes"],
    })

  # loops via polarity product
  import networkx as nx
  G = nx.DiGraph()
  for e in edges:
    G.add_edge(e["source"], e["target"], polarity=e["polarity"])
  loops = []
  for cyc in nx.simple_cycles(G):
    if len(cyc) > 6:
      continue
    sign = 1
    for a, b in zip(cyc, cyc[1:] + cyc[:1]):
      sign *= 1 if G[a][b]["polarity"] == "+" else -1
    loops.append({"nodes": cyc, "type": "R" if sign > 0 else "B"})

  nodes = [{"id": t, "n_claims": theme_claims[t]} for t in sorted(used)]
  out = {"nodes": nodes, "edges": edges, "loops": loops}
  json.dump(out, open("data/theme_graph.json", "w", encoding="utf-8"), indent=1)
  multi = sum(1 for e in edges if e["support"] >= 2)
  print(f"themes={len(nodes)} edges={len(edges)} (support>=2: {multi}) "
        f"loops={len(loops)} R={sum(1 for l in loops if l['type']=='R')} "
        f"B={sum(1 for l in loops if l['type']=='B')}")


if __name__ == "__main__":
  main()
