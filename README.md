# Community Causal Map

**What does a town believe causes what?** This project recreates Google Jigsaw's [Sensemaker](https://github.com/Jigsaw-Code/sensemaking-tools) pipeline end-to-end on real civic data, then extends it with a layer Sensemaker doesn't have: a **causal loop diagram (CLD)** extracted from residents' own words — the community's mental model of how their town works, with every causal link backed by verbatim quotes.

Built on the public 2018 Bowling Green / Warren County, KY conversation (607 comments, The American Assembly on [Polis](https://pol.is), via [compdemocracy/openData](https://github.com/compdemocracy/openData)).

## Live demos

- **[Community Causal Map](https://nitchakorn.github.io/community-causal-map/cld.html)** — the CLD extension. Click any arrow to read the quotes asserting that link.
- **[Interactive Report](https://nitchakorn.github.io/community-causal-map/report/)** — the recreated Sensemaker report: topics, opinions, quotes ranked by constructiveness.

## Findings

- **607 comments → 8 coherent topics** (transportation, urban development, downtown economy, education, parks, safety, health/social services, governance) through the Sensemaker categorization pipeline.
- **93 explicit causal claims from 84 comments (14% of the corpus)** under a strict extraction rule: the text itself must assert a mechanism ("annexation would eliminate unincorporated islands"), bare wishes extract nothing.
- Canonicalized into **77 variables and 69 signed causal links**; 4 links independently asserted by 2+ residents.
- **Zero closed feedback loops** — the headline negative result, reported as such. Individual civic comments carry single cause→effect links; feedback structure doesn't close across 84 claiming participants at this density. Loops require denser elicitation (adaptive follow-ups asking *"and what does that lead to?"*) — which is exactly what this argues for.
- Along the way: one reproducible model-behavior bug (4 of 438 scoring prompts consistently hang `gemini-3.1-flash-lite-preview` past a 10-minute client timeout; the flagship model clears all 438 in seconds).

## Method (CLD layer)

1. **Extract** (`cld/extract_claims.py`) — explicit-claims-only prompt over every comment, structured JSON out: `(cause, effect, polarity, verbatim span, participant_id)`.
2. **Canonicalize + graph** (`cld/build_graph.py`) — LLM merge of surface phrases into a controlled vocabulary (surface forms preserved as provenance), signed digraph in networkx, cycle detection with loop type = polarity product (+ → Reinforcing, − → Balancing).
3. **Render** (`cld/build_view.py`) — a self-contained interactive HTML: polarity-colored arrows (colorblind-validated palette), line width = independent corroboration, click-through to verbatim quotes, table view.

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
