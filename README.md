# Community Causal Map

**What does a town believe causes what?** This project recreates Google Jigsaw's [Sensemaker](https://github.com/Jigsaw-Code/sensemaking-tools) pipeline end-to-end on real civic data, then extends it with a layer Sensemaker doesn't have: a **causal loop diagram (CLD)** extracted from residents' own words — the community's mental model of how their town works, with every causal link backed by verbatim quotes.

Built on the public 2018 Bowling Green / Warren County, KY conversation (607 comments, The American Assembly on [Polis](https://pol.is), via [compdemocracy/openData](https://github.com/compdemocracy/openData)).

**New to causal loop diagrams?** [`cld/READING_THE_MAP.md`](cld/READING_THE_MAP.md) explains — in plain language, and in the terms a system-dynamics practitioner would want — what this map is, how it's built, and what you can and can't conclude from it.

## Live demos

- **[Community Causal Map](https://nitchakorn.github.io/community-causal-map/cld.html)** — the CLD extension. A ~10-theme overview, with a zoom-in to all 97 variables; click any arrow to read the quotes asserting that link.
- **[Interactive Report](https://nitchakorn.github.io/community-causal-map/report/)** — the recreated Sensemaker report: topics, opinions, quotes ranked by constructiveness.

## Findings

- **607 comments → 8 coherent topics** (transportation, urban development, downtown economy, education, parks, safety, health/social services, governance) through the Sensemaker categorization pipeline.
- **74 explicit causal claims from 66 comments (~11% of the corpus)** under a strict extraction rule: the text itself must assert a mechanism ("annexation would eliminate unincorporated islands"), bare wishes extract nothing.
- Canonicalized into **97 variables and 71 signed causal links**, 1 of them independently asserted by 2+ residents. The interactive map focuses on the ~26 variables that connect to others (a genuine "Local Government Revenue" hub emerges — cannabis legalization, business activity, and traffic enforcement all feed it); the one-off mentions are listed in the table. See [`cld/METHOD_NOTES.md`](cld/METHOD_NOTES.md) for why these numbers differ from an earlier version (a polarity-inversion bug in canonicalization was fixed; the earlier map's tighter look was partly an artifact of over-merging).
- **No closed loops at the variable level; one _candidate_ loop at the theme level.** Individual comments carry single cause→effect links, not circuits — so the detailed map has zero feedback loops, a real statement about what one-shot public comment reveals. Aggregating to themes surfaces one *possible* reinforcing loop (Local Economy ⇄ Community & Governance), but it rests on only a couple of participants with one contested arm, so the map labels it a **hypothesis, not a finding**. Closing loops for real needs denser, iterative elicitation — exactly what this argues for.
- Along the way: one reproducible model-behavior bug (4 of 438 scoring prompts consistently hang `gemini-3.1-flash-lite-preview` past a 10-minute client timeout; the flagship model clears all 438 in seconds).

## Method (CLD layer)

1. **Extract** (`cld/extract_claims.py`) — explicit-claims-only prompt over every comment, structured JSON out: `(cause, effect, polarity, verbatim span, participant_id)`.
2. **Canonicalize + graph** (`cld/build_graph.py`) — LLM merge of surface phrases into a controlled vocabulary (surface forms preserved as provenance), signed digraph in networkx, cycle detection with loop type = polarity product (+ → Reinforcing, − → Balancing).
3. **Render** (`cld/build_view.py`) — a self-contained interactive HTML: polarity-colored arrows (colorblind-validated palette), line width = independent corroboration, click-through to verbatim quotes, table view.

> **Recreating this? Read [`cld/METHOD_NOTES.md`](cld/METHOD_NOTES.md) first.** It documents two non-obvious pitfalls that will bite you — a polarity-inversion bug introduced by the canonicalization step (arrows that point the opposite of what people said), and the correctness-vs-legibility trade-off — plus why you must test the pipeline end-to-end, not just syntax-check it.

## Reproduce

```bash
pip install google-genai networkx
export GEMINI_API_KEY=<your key>          # your key, your quota — nothing is collected
python prep/prepare_data.py               # downloads the public dataset, writes data/processed_full.csv
python cld/extract_claims.py              # ~16 batched calls
python cld/build_graph.py                 # 1 call + graph build
python cld/build_view.py                  # writes cld_view.html
```

Runs on any Gemini API key (paid tier recommended; the free tier's per-model daily caps make full runs painful). The upstream Sensemaker pipeline also supports any OpenAI-compatible endpoint.

## Roadmap

- **Jury-on-edges** — re-point Sensemaker's simulated-jury + proportional-approval-voting machinery at causal links, so the map shows only community-*endorsed* mechanisms, not just extracted ones.
- **Bring-your-own-key browser tool** — this pipeline is small enough to run fully client-side: upload a CSV, paste your key, get your community's causal map. No server, no key custody.
- Adaptive causal elicitation — follow-up questions designed to close loops.

## Attribution & license

- Upstream pipeline: [Jigsaw-Code/sensemaking-tools](https://github.com/Jigsaw-Code/sensemaking-tools) (Apache-2.0, © Google LLC). This repo's extension code: Apache-2.0.
- Data: [American Assembly bowling-green conversation](https://github.com/compdemocracy/openData) (public, anonymized). Comments are residents' own words, reproduced with attribution.
