#!/usr/bin/env python3
"""Import the conference schedule from the PM26 handbook (.docx) into index.html.

The handbook is the source of truth for the "Schedule & Sessions" section. Replace the .docx,
run this script, and the site data (`program` inside the __ssr_data__ JSON) is rewritten.

    python3 schedule/import_handbook.py            # auto-finds PM26_Conference_Handbook*.docx in the repo root
    python3 schedule/import_handbook.py --check    # parse + report only, do not touch index.html
    python3 schedule/import_handbook.py --docx "path/to/handbook.docx"

What it reads (the structure of the handbook):
  * a Heading 1 paragraph  "Programme · <day>"   starts a day (several days are fine — one heading each)
  * every table after it, until the next Heading 1, is a block of the schedule:
      - a ONE-cell row            = a session heading (e.g. "Opening & Keynote Speakers Session I")
      - a TWO-cell row            = "hh:mm–hh:mm"  |  title (+ detail lines)
      - "Keynote 1 · Name" / "Invited Speaker 2 · Name" rows are speaker rows; the 2nd line is the affiliation
Anything else in the document (welcome text, topics, past editions) is ignored.

schedule/supplement.json holds agreed details that are NOT in the handbook yet (an extra day, a corrected line).
It is applied after the handbook is read:
  * "days":    a day is added only if the handbook does not already contain that day (handbook wins once it does)
  * "patches": {"match": {...fields...}, "set": {...fields...}} overwrite fields on matching entries;
               a patch that matches nothing is reported, so a stale patch cannot hide silently
Delete an entry from supplement.json once the handbook says the same thing.
"""
import argparse, glob, json, os, re, sys, zipfile
from xml.etree import ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TIME = re.compile(r"^(\d{1,2})[:.](\d{2})\s*[–—-]\s*(\d{1,2})[:.](\d{2})$")


def clean(t):
    return re.sub(r"\s+", " ", (t or "").replace(" ", " ")).strip()


def para_text(p):
    return clean("".join(t.text or "" for t in p.iter(W + "t")))


def para_style(p):
    s = p.find(f"{W}pPr/{W}pStyle")
    return s.get(W + "val") if s is not None else ""


def table_rows(tbl):
    """-> list of rows; each row is a list of cells; each cell is a list of non-empty paragraph strings."""
    rows = []
    for tr in tbl.findall(W + "tr"):
        cells = []
        for tc in tr.findall(W + "tc"):
            cells.append([t for t in (para_text(p) for p in tc.iter(W + "p")) if t])
        rows.append([c for c in cells if c] or [])
    return [r for r in rows if r]


def classify(title):
    t = title.lower()
    if re.search(r"\b(break|lunch|tea|coffee)\b", t):
        return "break"
    if "registration" in t:
        return "registration"
    if re.search(r"ceremony|award|certificate|photo", t):
        return "ceremony"
    return "session"


def parse(docx):
    root = ET.fromstring(zipfile.ZipFile(docx).read("word/document.xml"))
    body = root.find(W + "body")
    items, day = [], None
    for el in body:
        if el.tag == W + "p" and para_style(el) == "Heading1":
            m = re.match(r"^Programme\s*[·\-–—:]\s*(.+)$", para_text(el), re.I)
            day = m.group(1).strip() if m else None
        elif el.tag == W + "tbl" and day:
            session = ""
            for row in table_rows(el):
                if len(row) == 1:                                   # one-cell row -> session heading
                    session = " ".join(row[0])
                    continue
                time_raw, content = clean(row[0][0]), row[1]
                time = re.sub(r"\s*[–—-]\s*", "–", time_raw)
                first = content[0]
                m = re.match(r"^(Keynote(?:\s*\d+)?|Invited\s+Speaker(?:\s*\d+)?)\s*·\s*(.+)$", first, re.I)
                item = {"day": day, "session": session, "time": time}
                if m:
                    item["type"] = "keynote" if m.group(1).lower().startswith("keynote") else "invited"
                    item["label"] = clean(m.group(1))
                    item["speaker"] = clean(m.group(2))
                    item["session_title"] = ""                      # talk title — none in the handbook yet
                    if len(content) > 1:
                        item["detail"] = " · ".join(content[1:])
                else:
                    item["type"] = classify(first)
                    item["session_title"] = first
                    if len(content) > 1:
                        item["detail"] = " · ".join(content[1:])
                items.append(item)
    return items


def apply_supplement(items):
    """Merge schedule/supplement.json into the parsed handbook items. Returns (items, notes)."""
    path = os.path.join(ROOT, "schedule", "supplement.json")
    notes = []
    if not os.path.exists(path):
        return items, notes
    sup = json.load(open(path))
    for patch in sup.get("patches", []):
        hits = [i for i in items if all(i.get(k) == v for k, v in patch["match"].items())]
        if not hits:
            notes.append(f"! supplement patch matched nothing (handbook changed?): {patch['match']}")
        for i in hits:
            i.update(patch["set"])
            notes.append(f"supplement: patched {i['day']} {i['time']} {i.get('session_title') or i.get('speaker')}: {', '.join(patch['set'])}")
    have = {i["day"] for i in items}
    for d in sup.get("days", []):
        if d["day"] in have:
            notes.append(f"supplement: day '{d['day']}' ignored — the handbook now contains it (you can delete it from supplement.json)")
            continue
        for e in d["items"]:
            item = {"day": d["day"], "session": e.get("session", ""), "time": e["time"], "type": e.get("type", "session")}
            item["session_title"] = e.get("session_title", "")
            for k in ("label", "speaker", "detail"):
                if e.get(k):
                    item[k] = e[k]
            items.append(item)
        notes.append(f"supplement: added day '{d['day']}' ({len(d['items'])} entries) — not in the handbook")
    return items, notes


def minutes(t):
    m = TIME.match(t)
    if not m:
        return None
    return int(m.group(1)) * 60 + int(m.group(2)), int(m.group(3)) * 60 + int(m.group(4))


def report(items, speakers):
    warnings = []
    days = []
    for it in items:
        if it["day"] not in days:
            days.append(it["day"])
    print(f"days: {len(days)}   items: {len(items)}")
    for d in days:
        di = [i for i in items if i["day"] == d]
        sessions = []
        for i in di:
            if i["session"] not in sessions:
                sessions.append(i["session"])
        print(f"\n  {d}  —  {len(di)} entries, {len(sessions)} blocks")
        prev_end = None
        for i in di:
            span = minutes(i["time"])
            if span is None:
                warnings.append(f"unreadable time {i['time']!r}")
                continue
            if prev_end is not None and span[0] != prev_end:
                kind = "gap" if span[0] > prev_end else "overlap"
                warnings.append(f"{d}: {kind} before {i['time']} (previous entry ended {prev_end // 60:02d}:{prev_end % 60:02d})")
            prev_end = span[1]
            who = i.get("speaker") or i["session_title"]
            print(f"    {i['time']:12s} [{i['type']:12s}] {(i.get('label') + ' · ') if i.get('label') else ''}{who}")
    names = {s["name"].strip().lower() for s in speakers}
    for i in items:
        if i.get("speaker") and i["speaker"].strip().lower() not in names:
            warnings.append(f"speaker not found in the site's speaker list (no photo will show): {i['speaker']}")
    k = sum(1 for i in items if i["type"] == "keynote")
    v = sum(1 for i in items if i["type"] == "invited")
    print(f"\n  keynotes: {k}   invited: {v}")
    return warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docx", help="handbook path (default: newest PM26_Conference_Handbook*.docx in the repo root)")
    ap.add_argument("--check", action="store_true", help="parse and report only; do not modify index.html")
    a = ap.parse_args()

    docx = a.docx
    if not docx:
        found = sorted(glob.glob(os.path.join(ROOT, "PM26_Conference_Handbook*.docx")), key=os.path.getmtime)
        if not found:
            sys.exit("No PM26_Conference_Handbook*.docx found in the repo root (or pass --docx).")
        docx = found[-1]
    print("handbook:", os.path.basename(docx))

    items = parse(docx)
    items, notes = (apply_supplement(items) if items else (items, []))
    if not items:
        sys.exit('No schedule found. Expected a Heading 1 "Programme · <day>" followed by schedule tables. index.html NOT changed.')

    path = os.path.join(ROOT, "index.html")
    src = open(path).read()
    data = json.loads(re.search(r'<script type="application/json" id="__ssr_data__">(.*?)</script>', src, re.S).group(1))
    warnings = report(items, data.get("speakers", []))
    for w in warnings:
        print("  ! WARNING:", w)
    for n in notes:
        print("  " + n)

    if a.check:
        print("\n--check: index.html not modified.")
        return

    key = '  "program": '
    start = src.index(key)
    arr_start = start + len(key)
    _, arr_end = json.JSONDecoder().raw_decode(src[arr_start:])
    block = json.dumps(items, ensure_ascii=False, indent=2).replace("\n", "\n  ")
    new = src[:arr_start] + block + src[arr_start + arr_end:]
    if new == src:
        print("\nNo changes — index.html already matches the handbook.")
        return
    open(path, "w").write(new)
    print(f"\nindex.html updated: {len(items)} schedule entries written to the site data.")


if __name__ == "__main__":
    main()
