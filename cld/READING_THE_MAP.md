# Reading — and Trusting — This Causal Map

A plain-language guide to what this map is, how it's built, and why you can (and can't)
believe it. Written for two readers at once: someone who has never heard the phrase
"causal loop diagram," and someone who builds them for a living and wants to know we did
it honestly.

---

## Part 1 — For the newcomer: what is this thing?

A **causal loop diagram (CLD)** is a picture of how the parts of a situation push on each
other. It has just two ingredients:

- **Variables** — things that can go *up or down*: `Traffic Congestion`, `Public Safety`,
  `Local Government Revenue`. (Notice they're named as quantities, not as opinions. Not
  "bad traffic" — just `Traffic Congestion`, which can rise or fall.)
- **Arrows** — "this affects that," with a sign:
  - **`+`** the two move **together** — more streetlights, more safety.
  - **`−`** they move **opposite** — higher parking fees, less traffic.

That's the whole alphabet. Everything on the map is variables joined by `+` and `−` arrows.

**Why not just list what people want?** Because a list of opinions tells you *what* people
want changed. A causal map tells you *how they think their town actually works* — the
mental model underneath the opinions. "Add more police" is an opinion. "More enforcement →
more compliance → fewer accidents" is a piece of a worldview. The second is far more useful
if you're trying to actually help.

### Loops (the "loop" in causal loop diagram)

When arrows form a **circle**, you get **feedback** — the thing that makes systems behave in
surprising ways. There are exactly two flavors:

- **Reinforcing (marked `R`)** — a snowball. More of A → more of B → even more of A.
  (Savings → interest → more savings.)
- **Balancing (marked `B`)** — a thermostat. It pushes back toward a set point.
  (Room too warm → AC kicks on → room cools → AC stops.)

The rule practitioners use: **count the `−` arrows in the loop. Even number → reinforcing.
Odd number → balancing.** (This map computes that automatically; it doesn't eyeball it.)

> **On this particular map, there are _no_ closed loops** — and that's a genuine finding,
> not a gap. See Part 4.

---

## Part 2 — For the skeptic: where this sits in the field

If you know system dynamics, here's the honest placement. This is a machine-scaled cousin
of **Group Model Building (GMB)** and **Community-Based System Dynamics (CBSD)** — the
participatory tradition where a facilitator sits a room of stakeholders down and helps them
draw their *shared mental model* as a signed causal graph. (See Sterman, *Business
Dynamics*, ch. 5 for CLD conventions; Hovmand, *Community-Based System Dynamics* for the
participatory method.)

We're after the **same object** — a shared mental model as a signed digraph — by a
**different elicitation**. Instead of a workshop with a dozen people, we read the *perceived
causal claims* already sitting in hundreds of written public comments. The upside is scale
and that nobody is put on the spot; the cost is that we can't ask a follow-up question, so
we only ever see what people wrote down unprompted.

We keep the field's conventions on purpose so the output is legible to a practitioner:
variables are neutral quantities, links carry `+`/`−` polarity, loop polarity is the product
of the link signs, reinforcing/balancing are marked `R`/`B`.

---

## Part 3 — The one rule to hold in your head

**Every arrow means "at least one person asserted this influence" — not "this influence is
real."**

This is a map of **beliefs**, not a validated causal model. If a resident writes "harsher
sentences create more victims," an arrow appears — whether or not criminology agrees. That's
the point: we are mapping how the community *reasons*, faithfully, including where it may be
wrong. It is not econometrics, and it does not claim to be. An expert should read this map as
*elicited perceived causality*, full stop.

---

## Part 4 — How it's built, and why each choice is defensible

Four steps. For each, what we do and why a careful reader should accept it.

**1. Extract only _explicit_ causal claims.**
We pull an arrow only when the text itself asserts a mechanism — "because," "leads to,"
"reduces," "causes confusion." A bare wish ("we need more parks") produces *nothing*. *Why:*
the fastest way to make a CLD lie is to let the model infer mechanisms nobody stated. Staying
literal is the difference between mapping the community's reasoning and mapping our own.

**2. Name variables neutrally; set the sign from the sentence.**
"The lack of sidewalks discourages walking" becomes `Sidewalk Availability —(+)→ Walking`
(more sidewalks, more walking) — not `lack of sidewalks`. *Why:* it's the core CLD
convention (a variable must be able to go up *or* down), and — learned the hard way — naming
a variable by its *absence* is exactly how arrow signs get flipped backwards. The war story
is in [`METHOD_NOTES.md`](METHOD_NOTES.md).

**3. Keep the verbatim quote on every arrow.**
Click any link and you see the exact sentences behind it, with the participant IDs. *Why:*
in a workshop, the facilitator is the guarantee that the diagram reflects what people said.
Here, the quotes are that guarantee. A causal map nobody can audit is just a drawing.

**4. Merge synonyms, weight by corroboration, find loops mechanically.**
"gridlock," "traffic," "congestion" collapse into one `Traffic Congestion` node — but we
*never* merge a variable into its opposite. A link asserted by several independent people is
drawn heavier than a one-off. Loops are detected by walking the graph and multiplying signs,
not by hand. *Why:* a map of 200 one-off variables isn't a system; sensible grouping is what
lets structure appear — as long as the grouping never changes what someone meant.

---

## Part 5 — Two views, and what the map is telling us (honestly)

The map comes at two altitudes. The **theme overview** groups the 97 fine-grained variables
into ~10 hand-curated themes and draws only the theme-to-theme links that *multiple*
residents independently made — a legible executive summary. The **detailed view** (zoom in)
shows every variable. The grouping is a human judgment call, stated as such; it's in
`build_themes.py` so anyone can audit or redo it.

- **At the variable level: no closed loops.** On single-round written comments, people assert
  *open chains* ("A causes B"), not *circuits* ("…and B feeds back to A"). Closing loops is
  precisely what a facilitated GMB session does across several rounds of "and what does *that*
  lead to?" So the absence of loops isn't a failure of the method — it's a true statement
  about what one-shot public comment can reveal, and an argument for iterative elicitation.
- **At the theme level: one _candidate_ loop.** Aggregation surfaces a possible reinforcing
  loop between `Local Economy` and `Community & Governance`. Treat it as a **hypothesis to
  test, not a finding** — click it and you'll see it rests on only a couple of participants,
  with one contested arm. Flagging that honestly is the point: aggregation can *suggest*
  feedback the raw claims don't yet support, and a careful reader should always drop down to
  the quotes before believing a loop.
- **Sparse corroboration.** Most links come from a single person; genuine agreement is rare.
  A real shared hub does emerge (several residents independently tie different causes to
  `Local Government Revenue`), but the headline is that this community reasons in many
  private, idiosyncratic causal stories rather than one common one.

## Part 6 — What it is *not*

- Not validated or quantitative causality — no data proves any arrow; they're claims.
- Not a simulation model — there are no stocks, flows, or equations, so it can't be "run."
- Not a replacement for a facilitated session — it's a fast, transparent *starting point*
  that a real Group Model Building process could refine.

---

### Further reading
- J. Sterman, *Business Dynamics: Systems Thinking and Modeling for a Complex World* — the
  standard reference for CLD notation and loop polarity.
- P. Hovmand, *Community-Based System Dynamics* — the participatory, community-voice tradition
  this project scales.
- The System Dynamics Society (systemdynamics.org) for primers on reinforcing/balancing feedback.
