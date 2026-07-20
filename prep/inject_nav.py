"""Regenerate docs/ and hf_space/ pages from built artifacts, with the shared site menu.

Idempotent: strips any existing #sitenav before injecting the current one.
Run from the repo root after rebuilding cld_view.html (and optionally the reports).
"""
import os
import re

ITEMS = [
    ("Home", "index.html", "home"),
    ("Report — sample", "report/", "report"),
    ("Report — full corpus", "report-full/", "reportfull"),
    ("Causal Map", "cld.html", "cld"),
]
HF_BASE = "https://nitchakorn.github.io/community-causal-map/"

# Jigsaw is the upstream author of the pipeline these report pages ARE (near-verbatim,
# just fed our data) — a small always-present credit is non-negotiable, not cosmetic.
CREDIT_BADGE = (
    '<a href="https://github.com/Jigsaw-Code/sensemaking-tools" target="_blank" rel="noopener"'
    ' title="Independent extension by Nitchakorn Tangs — not affiliated with or endorsed by'
    ' Google or Jigsaw." style="position:fixed;top:10px;left:10px;z-index:9999;'
    'background:#fcfcfb;border:1px solid rgba(11,11,11,0.15);border-radius:999px;'
    'padding:5px 12px;text-decoration:none;color:#52514e;font:12.5px system-ui;'
    'box-shadow:0 1px 6px rgba(0,0,0,0.07)">Built on Google Jigsaw’s sensemaking-tools ↗</a>'
)


def inject_credit(path: str) -> None:
  s = open(path, encoding="utf-8").read()
  s = re.sub(r'<a[^>]*id="creditbadge"[^>]*>.*?</a>', "", s, count=1, flags=re.S)
  i = s.find("<body")
  i = s.find(">", i) + 1
  s = s[:i] + CREDIT_BADGE.replace('href=', 'id="creditbadge" href=', 1) + s[i:]
  open(path, "w", encoding="utf-8").write(s)
  print("credit ->", path)


def pills(base: str, current: str) -> str:
  links = []
  for label, href, key in ITEMS:
    target = f"{base}{href}"
    probe = f"docs/{href}"
    if not (os.path.isdir(probe) or os.path.isfile(probe)) and href != "index.html":
      continue  # skip menu items whose page doesn't exist yet
    cur = key == current
    style = (
        "background:#fcfcfb;border:1px solid rgba(11,11,11,0.15);border-radius:999px;"
        "padding:5px 12px;text-decoration:none;box-shadow:0 1px 6px rgba(0,0,0,0.07);"
        + ("color:#0b0b0b;font-weight:600;" if cur else "color:#2a78d6;")
    )
    if cur:
      # the page you're already on: a plain label, never a (possibly cross-domain,
      # possibly iframed) link back to itself
      links.append(f'<span style="{style}">{label}</span>')
      continue
    target_attr = ' target="_blank" rel="noopener"' if base else ""
    links.append(f'<a href="{target}" style="{style}"{target_attr}>{label}</a>')
  return (
      '<div id="sitenav" style="position:fixed;top:10px;right:10px;z-index:9999;'
      'display:flex;gap:6px;font:12.5px system-ui">' + "".join(links) + "</div>"
  )


def inject(path: str, current: str, base: str) -> None:
  s = open(path, encoding="utf-8").read()
  s = re.sub(r'<div id="sitenav".*?</div>', "", s, count=1, flags=re.S)
  i = s.find("<body")
  i = s.find(">", i) + 1
  s = s[:i] + pills(base, current) + s[i:]
  open(path, "w", encoding="utf-8").write(s)
  print("nav ->", path)


def main() -> None:
  if os.path.exists("cld_view.html"):
    open("docs/cld.html", "w", encoding="utf-8").write(open("cld_view.html", encoding="utf-8").read())
  if os.path.exists("tool.html"):
    t = open("tool.html", encoding="utf-8").read()
    open("docs/tool.html", "w", encoding="utf-8").write(t)
    open("hf_space/index.html", "w", encoding="utf-8").write(t)
  else:
    open("hf_space/index.html", "w", encoding="utf-8").write(open("cld_view.html", encoding="utf-8").read())
  inject("docs/index.html", "home", "")
  inject("docs/cld.html", "cld", "")
  if os.path.exists("docs/report/index.html"):
    inject("docs/report/index.html", "report", "../")
    inject_credit("docs/report/index.html")
  if os.path.exists("docs/report-full/index.html"):
    inject("docs/report-full/index.html", "reportfull", "../")
    inject_credit("docs/report-full/index.html")
  if os.path.exists("docs/tool.html"):
    inject("docs/tool.html", "", "")
  # HF mirror: absolute links back to the canonical site
  inject("hf_space/index.html", "", HF_BASE)


if __name__ == "__main__":
  main()
