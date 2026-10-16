#!/usr/bin/env python3
"""Regenerate the Lessons index in README.md between the LESSONS markers.

Usage: python3 scripts/build-index.py   (run from anywhere)
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
LESSONS = ROOT / "lessons"
START, END = "<!-- LESSONS:START -->", "<!-- LESSONS:END -->"


def parse(path):
    m = re.match(r"^(\d+)-(.+)\.md$", path.name)
    num, slug = int(m.group(1)), m.group(2)
    title, sent = None, ""
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if title is None and s.startswith("# "):
            title = s[2:].strip()
            # drop a leading "NN." / "NN:" / "NN -" prefix; the table has its own # column
            title = re.sub(r"^\d+\s*[.:)\-–—]\s*", "", title)
            continue
        d = re.match(r"^_?Sent\s+(\d{4}-\d{2}-\d{2})_?$", s)
        if d and not sent:
            sent = d.group(1)
        if title is not None and sent:
            break
    if not title:
        title = slug.replace("-", " ").title()
    return num, title, sent, path.name


def build():
    rows = sorted(parse(p) for p in LESSONS.glob("[0-9]*-*.md"))
    out = [START, "", "| # | Lesson | Sent |", "|---:|---|---|"]
    for num, title, sent, name in rows:
        safe = title.replace("|", "\\|")
        out.append(f"| {num:02d} | [{safe}](lessons/{name}) | {sent} |")
    out += ["", f"_{len(rows)} lessons so far._", "", END]
    block = "\n".join(out)
    text = README.read_text(encoding="utf-8")
    if START in text and END in text:
        text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    else:
        text = text.rstrip() + "\n\n## Lessons\n\n" + block + "\n"
    README.write_text(text, encoding="utf-8")
    print(f"Indexed {len(rows)} lessons")


if __name__ == "__main__":
    build()
