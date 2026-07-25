# Method notes & pitfalls — for anyone recreating this

The CLD layer is small (extract → canonicalize → graph → render), but two non-obvious
things will bite you. Both were *predicted* as risks in [`PRO.md`](PRO.md) ("polarity
errors + over-extraction") and both really happened. Here is what they look like in
practice and how they were resolved, so you don't rediscover them the hard way.

## 1. The polarity-inversion pitfall (the important one)

**Symptom.** An arrow asserts the *opposite* of what the person actually said. e.g. a
resident writes *"the lack of sidewalks discourages walking"* and the map draws
**Sidewalk Availability → (−) → Walking** — i.e. "more sidewalks, less walking," which
is backwards.

**Root cause.** It is introduced by the **canonicalization** step, not extraction. The
raw extraction was faithful (`cause = "lack of sidewalks"`, `polarity = −`). But when
canonicalization normalized the variable *name* to a neutral form — `"lack of sidewalks"`
→ `"Sidewalk Availability"` — it flipped the variable's semantic direction **without
flipping the edge's sign**. Same thing turned `"confusion for drivers"` into
`"Intersection Navigation"` (a good thing) while keeping a `+`, so "bike lanes improve
navigation" when the person said they *caused confusion*.

On a real 5-row test this produced a **50% polarity error rate** (2 of 4 edges inverted).
It is invisible to a JS syntax check or a unit test — the code runs fine and produces a
graph; the graph is just *wrong*. See pitfall #3.

**The fix (two parts, must do both):**
1. **Move variable-naming into the extraction prompt**, where the model has the full
   sentence and can pick both a neutral variable name *and* the correct polarity together.
   Instruct it: name `cause`/`effect` as a neutral quantity that can rise or fall
   (`"Sidewalk Availability"`, `"Driver Confusion"`), never a directional phrase
   (`"lack of sidewalks"`), then set polarity by how those two quantities co-move in the
   sentence. Give it the sidewalk example explicitly.
2. **Forbid canonicalization from reversing direction.** Tell the merge step to preserve
   each phrase's semantic direction and merge only same-direction concepts — never map a
   phrase to a name meaning its opposite.

After the fix the same test went to **4/4 correct**. The two prompts live in two places
and **must stay in sync**: `cld/extract_claims.py` (`PROMPT_HEAD`) for the Python batch
pipeline, and `prep/build_tool.py` (`EXTRACT_HEAD` / the canonicalization prompt) for the
in-browser tool.

## 2. The correctness ↔ aggregation trade-off

Fixing polarity has a side effect worth understanding before you panic at the numbers.
Pushing neutral naming into extraction makes each variable **more specific and unique**,
so the canonicalizer merges *less*, and the map gets **more fragmented** (more one-off
"leaf" nodes, fewer multi-participant edges).

Do not over-correct by merging aggressively to win back a tight-looking map — that is
exactly what produced the inversions in the first place. When we inspected the *old*
(pre-fix) map, **2 of its 4 "corroborated" edges were merge artifacts**: one was a
near-tautology (`Public Transit → Public Transit Access`) and one was mislabeled
(residents said immigrants *"enrich our landscape"*; it had been merged into
`Immigrant Population → Local Government Jurisdiction`, which no one said). So the old
map's apparent connectivity was partly an illusion of over-merging.

**Resolution used here:** (a) canonicalize at the *concept* level (bold but
direction-preserving), and (b) make the **renderer** carry the legibility load instead of
the merge step — default to showing the connected "core" (variables appearing in ≥2
links) with a toggle to reveal every one-off mention. Correctness lives in the data;
legibility lives in the view. Don't force the merge step to do both jobs.

## 3. Why you must test end-to-end, not just syntax-check

The polarity bug shipped a *valid* program that produced a *wrong* graph. Nothing short
of running the real pipeline on real text and **reading the resulting arrows** would have
caught it. The check that found it: drive the actual page in a headless browser
(`puppeteer-core` against system Chrome), upload a small CSV with known causal claims,
run it with a real key, and assert each edge's direction against the sentence. A tiny
hand-built test CSV where you already know the right answer (a few explicit "X reduces Y"
/ "lack of X discourages Y" claims) is enough to expose it.

## 4. Sanity checks worth keeping

- Grep the final variable names for directional words (`lack`, `less`, `lower`, `missing`,
  `reduced`, `fewer`) — after the fix there should be **none**; their presence means
  extraction is still emitting directional phrases.
- Spot-check the highest-degree hub and the multi-participant edges by hand against their
  verbatim quotes. Corroborated edges are where merge artifacts hide.
- Expect **few or zero closed loops** on single-round civic comment data — residents
  assert isolated links, not circuits. That is a finding about the data, not a bug (see
  the "no loops" note rendered in the map).
