"""Extract explicit causal claims from community comments (CLD v0 stage 1)."""
import csv
import json
import os
import sys
import time

from google import genai
from google.genai import types

MODEL = "gemini-flash-latest"
BATCH = 38
RETRIES = 3

PROMPT_HEAD = (
    "You are auditing community comments for EXPLICIT causal claims.\n"
    "A causal claim exists only when the text itself asserts one thing influences another "
    "(because, causes, leads to, results in, brings, keeps, attracts, drives away, or unmistakable if-then). "
    "Do NOT infer mechanisms behind bare suggestions or wishes ('we need X' alone = no claim).\n"
    "Name 'cause' and 'effect' as NEUTRAL variables naming a quantity that can rise or fall "
    "(e.g. 'Sidewalk Availability', 'Traffic Congestion', 'Driver Confusion'), NEVER a directional "
    "phrase ('lack of sidewalks', 'less traffic'). Then set 'polarity' by how those two quantities "
    "actually co-move in the sentence: '+' if they rise and fall together, '-' if one rises as the other falls.\n"
    "Example: 'The lack of sidewalks discourages walking' -> cause 'Sidewalk Availability', effect "
    "'Walking', polarity '+' (more sidewalks -> more walking). 'Bike lanes caused confusion for drivers' "
    "-> cause 'Bike Lanes', effect 'Driver Confusion', polarity '+' (more lanes -> more confusion).\n"
    'Return ONLY JSON: {"claims":[{"comment_index":int,"cause":str,"effect":str,'
    '"polarity":"+ or -","span":"verbatim words asserting it"}]}\n'
    "Comments:\n"
)


def main() -> None:
  key = os.environ.get("GEMINI_API_KEY") or open(".gemini_key", encoding="utf-8").read().strip()
  client = genai.Client(api_key=key)
  rows = list(csv.DictReader(open("data/processed_full.csv", encoding="utf-8")))
  out = []
  for start in range(0, len(rows), BATCH):
    chunk = rows[start : start + BATCH]
    listing = "\n".join(f"[{i}] {r['survey_text']}" for i, r in enumerate(chunk))
    for attempt in range(RETRIES):
      try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=PROMPT_HEAD + listing,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0
            ),
        )
        claims = json.loads(resp.text)["claims"]
        break
      except Exception as e:  # noqa: BLE001 - retry any API/parse failure
        print(f"batch {start}: attempt {attempt+1} failed: {e}", file=sys.stderr)
        time.sleep(5 * (attempt + 1))
    else:
      print(f"batch {start}: GAVE UP", file=sys.stderr)
      continue
    for c in claims:
      i = c.get("comment_index")
      if not isinstance(i, int) or not 0 <= i < len(chunk):
        continue
      if str(c.get("polarity")) not in ("+", "-"):
        continue
      out.append({
          "participant_id": chunk[i]["participant_id"],
          "comment": chunk[i]["survey_text"],
          "cause": str(c["cause"]).strip(),
          "effect": str(c["effect"]).strip(),
          "polarity": c["polarity"],
          "span": str(c.get("span", "")).strip(),
      })
    print(f"batch {start}: total claims so far {len(out)}", flush=True)
  json.dump(out, open("data/claims_raw.json", "w", encoding="utf-8"), indent=1)
  n_comments = len({c["comment"] for c in out})
  print(f"DONE claims={len(out)} from {n_comments} comments of {len(rows)}")


if __name__ == "__main__":
  main()
