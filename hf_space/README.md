---
title: Community Causal Map — Bowling Green
emoji: 🔁
colorFrom: blue
colorTo: red
sdk: static
pinned: false
license: apache-2.0
short_description: Extract a causal map from your own civic comments
---

# Community Causal Map

Upload any CSV of free-text responses, bring your own Gemini API key, and get back a causal map of what that community believes causes what — every arrow backed by verbatim quotes. Runs entirely in your browser; nothing is uploaded to any server but Google's.

Preloaded as a demo: 607 real public comments (2018 Bowling Green / Warren County civic conversation, The American Assembly on Polis) — 74 explicit causal claims, canonicalized into 97 variables and 71 signed links (the map focuses on the ~26 connected ones; all links are in the table).

Built on a full recreation of Google Jigsaw's [sensemaking-tools](https://github.com/Jigsaw-Code/sensemaking-tools) pipeline, extended with the causal layer. Code, method, findings, and the companion Sensemaker report: [github.com/nitchakorn/community-causal-map](https://github.com/nitchakorn/community-causal-map).

Data: [compdemocracy/openData](https://github.com/compdemocracy/openData) (public, anonymized). Extraction: Gemini, explicit-claims-only rule — bare wishes extract nothing.
