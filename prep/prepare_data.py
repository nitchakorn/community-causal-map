"""Download the public Bowling Green Polis dataset and prep it for the pipeline."""
import csv
import io
import urllib.request

URL = ("https://raw.githubusercontent.com/compdemocracy/openData/master/"
       "american-assembly.bowling-green/comments.csv")


def main() -> None:
  raw = urllib.request.urlopen(URL).read().decode("utf-8")
  rows = list(csv.DictReader(io.StringIO(raw)))
  accepted = [r for r in rows if r["moderated"] == "1"]
  with open("data/processed_full.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["participant_id", "survey_text"])
    for r in accepted:
      w.writerow([r["author-id"], r["comment-body"]])
  print(f"{len(rows)} comments downloaded; {len(accepted)} accepted "
        f"(moderated==1) written to data/processed_full.csv")


if __name__ == "__main__":
  main()
