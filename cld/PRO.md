# PRO — Community Causal Loop Diagram on Sensemaker (v0)

**Problem.** The recreated Sensemaker pipeline answers *what residents want* (topics → opinions → quotes). It cannot answer *how residents believe their town works* — the causal mental model behind the asks. That model is what CLD/system-dynamics practice (group model building, community-based system dynamics) produces manually at high cost.

**Smallest thing that works (v0, this session).**
1. `extract_claims.py` — explicit-claims-only extraction over all 607 Bowling Green comments (`bg_data/processed_full.csv`) via `gemini-flash-latest`, strict JSON: `(cause, effect, polarity, verbatim span, participant_id)`. No implied mechanisms — bare suggestions yield nothing. Measured substrate: 20% of comments carry ≥1 explicit claim (probe, n=40, seed 42) → ~120 edges expected.
2. `build_graph.py` — LLM canonicalization of variable phrases into a controlled vocabulary (surface forms preserved as provenance) → signed digraph in `networkx` → `simple_cycles` (length ≤ 6), loop type = polarity product (+ → Reinforcing, − → Balancing) → `causal_graph.json`.
3. `cld_view.html` — self-contained interactive diagram (no CDN): force layout, S/O edge notation, R/B loop list, **click any edge → the verbatim quotes and participant IDs asserting it**. Provenance is the credibility feature.

**Deliberate scope cuts (v1+):** jury-on-edges validation (simulated jury + PAV over edges — the community-endorsement layer), `report_ui` `config.json` toggle integration, implied-mechanism extraction as a labeled dashed-edge class, vote-weighting edges from Polis agrees/disagrees.

**Known risks.** Loop scarcity (finding, not failure — report it); polarity errors and over-extraction (both binary-judgeable per triple → first eval set falls out of error analysis); canonicalization over-merge (keep surface forms visible).

**Done when:** `cld_view.html` opens in her browser showing the full-corpus graph with ≥1 correct quote-backed edge chain she can audit end-to-end.
