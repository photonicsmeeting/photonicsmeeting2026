#!/usr/bin/env python3
"""Update the website's Schedule & Sessions from the conference handbook FLIPBOOK (.html).

    python3 schedule/import_flipbook.py "path/to/PM26_Conference_Handbook_Flipbook.html"
    python3 schedule/import_flipbook.py "...html" --check      # parse + report, write nothing

The flipbook embeds the handbook's text page by page (`const DATA = [...]`). This script
  * reads the PAPER SESSIONS (paper ID, time slot, title, presenter) straight from that text, and
  * keeps the rest of the programme (speakers, topics, chairs, breaks, Day 2) in PROGRAMME below,
    typed from the same handbook pages — edit it here when the handbook changes.
Then schedule/supplement.json is applied (guest photos), and `program` inside index.html is rewritten.
"""
import argparse, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import import_handbook as H

ROOT = H.ROOT
D1 = "Tuesday, 10 November 2026"
D2 = "Wednesday, 11 November 2026"
KEY = "Opening & Keynote Speakers Session I"
INV = "Invited Speaker Session"
LAB = "Laboratory Visit & Networking"


def pages(path):
    s = open(path, encoding="utf-8", errors="replace").read()
    s = re.sub(r"data:[a-z/+\-]+;base64,[A-Za-z0-9+/=]+", "DATA", s)
    m = re.search(r"const DATA = (\[.*?\]);\n", s, re.S)
    if not m:
        sys.exit("Could not find the page text (const DATA = [...]) in the flipbook.")
    return [p["text"] for p in json.loads(m.group(1))]


def papers(text):
    """'Paper #ID4 15:10–15:20 <title> <Presenter> Paper #ID6 ...' -> [{id,time,title,presenter}]"""
    out = []
    for m in re.finditer(r"Paper #ID(\d+)\s+(\d{1,2}:\d{2}\s*[–-]\s*\d{1,2}:\d{2})\s+(.*?)(?=\s+Paper #ID\d+|\s+\d{1,2}:\d{2}\s*[–-]\s*\d{1,2}:\d{2}\s|\s+Dinner|\s+PM26 Conference Handbook|$)", text):
        body = m.group(3).strip()
        # the presenter is the trailing name: it starts at the LAST honorific
        hon = list(re.finditer(r"\b(Dr\.|Ms\.|Mr\.|Mrs\.|Prof\.|Assoc\.|Ts\.|Ir\.)\s", body))
        if not hon:
            sys.exit(f"Paper #ID{m.group(1)}: could not find the presenter's name in: {body!r}")
        i = hon[-1].start()
        # keep a run of honorifics together ("Assoc. Prof. Ts. Dr. ...")
        while True:
            prev = [h for h in hon if h.end() <= i and body[h.end():i].strip() == ""]
            if not prev:
                break
            i = prev[-1].start()
        out.append({"id": "ID" + m.group(1), "time": m.group(2).replace(" ", "").replace("-", "–"),
                    "title": re.sub(r"\s+", " ", body[:i]).strip().replace("Erbium- Doped", "Erbium-Doped").replace("Nanoparticle– Chitin", "Nanoparticle–Chitin"),
                    "presenter": body[i:].strip()})
    return out


def build(pg):
    t9, t10, t11 = pg[8], pg[9], pg[10]
    p1 = papers(t10)
    p2 = papers(t11)
    if not p1 or not p2:
        sys.exit("No papers found on the Presentation Session pages — has the handbook layout changed?")
    for lst in (p1, p2):
        lst.sort(key=lambda p: p["time"])
    span = lambda lst: lst[0]["time"].split("–")[0] + "–" + lst[-1]["time"].split("–")[1]
    chair1 = "Chair: Dr. Ahmad Haziq Aimal bin Rosol  ·  Time Keeper: Ms. Ilyana Amalin Zainal Roslan"
    chair2 = "Chair: Dr Aeriyn Dwierni Ahmad  ·  Time Keeper: Mr. Muhammad Izzat Zakwan bin Mohd Zabidi"
    def keynote(n, name, aff, time, topic=""):
        return {"day": D1, "session": KEY, "time": time, "type": "keynote", "label": f"Keynote {n}", "speaker": name,
                "session_title": topic, "detail": aff}
    def invited(n, name, aff, time, topic):
        return {"day": D1, "session": INV, "time": time, "type": "invited", "label": f"Invited Speaker {n}", "speaker": name,
                "session_title": topic, "detail": aff}
    items = [
        {"day": D1, "session": "", "time": "08:00–09:00", "type": "registration", "session_title": "Registration",
         "detail": "MJIIT, Universiti Teknologi Malaysia, Kuala Lumpur"},
        {"day": D1, "session": KEY, "session_note": "MC: Prof. Ir. Ts. Dr. Malathy Batumalay", "time": "09:00–09:15", "type": "ceremony",
         "session_title": "Opening Ceremony", "detail": "Officiated by"},
        keynote(1, "Prof. Ir. Ts. Dr. Tiu Zian Cheak", "School of Engineering & Computing, MILA University (Malaysia)", "09:15–10:00",
                "Shaping Darkness: Dark Pulse Engineering, Dynamics, and Measurement"),
        keynote(2, "Prof. Dr. Waleed Mohammed", "BU-CROCCS, School of Engineering, Bangkok University (Thailand)", "10:00–10:45",
                "Flexible Optical Sensors Based on Guided-Mode Resonance (Rigid-grade optics, plus bending, force and vibration)"),
        {"day": D1, "session": KEY, "time": "10:45–11:00", "type": "break", "session_title": "Tea & Networking Break"},
        keynote(3, "Prof. Dr. Ir. Retna Apsari", "Universitas Airlangga, Surabaya (Indonesia)", "11:00–11:45"),
        keynote(4, "Dr. Yu Chen", "Chongqing Vocational Institute of Engineering (China)", "11:45–12:30",
                "From a Single Fiber to a Soliton Kaleidoscope: SMS-Structure Artificial Saturable Absorbers Empowering Ultrafast Fiber Lasers"),
        keynote(5, "Peter Macaulay", "ZDSL Networks Sdn. Bhd. (Malaysia)", "12:30–13:15", "Data Center Interconnect (DCI)"),
        {"day": D1, "session": KEY, "time": "13:15–13:30", "type": "ceremony", "session_title": "Certificate Presentation & Photo Session",
         "detail": "All keynote speakers"},
        {"day": D1, "session": KEY, "time": "13:30–14:30", "type": "break", "session_title": "Lunch Break"},
        dict(invited(1, "Assoc. Prof. Ts. Dr. Wan Maryam Wan Ahmad Kamil", "Universiti Sains Malaysia (USM)", "14:30–14:50",
                     "Aluminium Zinc Oxide Composite for Random Lasing"), session_note=chair1),
        invited(2, "Dr. Ganesan Krishnan", "Department of Physics, Faculty of Science, Universiti Teknologi Malaysia", "14:50–15:10",
                "Reusable Zinc Ferrite Nanoparticles Produced Using Pulsed Laser Ablation In Liquid Technique For Dye Photodegradation Applications"),
        {"day": D1, "session": "Presentation", "time": span(p1), "type": "session", "session_title": "Presentation Session I",
         "detail": chair1, "papers": p1},
        {"day": D1, "session": "Presentation", "time": "16:10–16:30", "type": "break", "session_title": "Tea & Networking Break"},
        {"day": D1, "session": "Presentation", "time": span(p2), "type": "session", "session_title": "Presentation Session II",
         "detail": chair2, "papers": p2},
        {"day": D1, "session": "Dinner & Closing Ceremony", "time": "18:00–19:30", "type": "ceremony",
         "session_title": "Best Paper & Best Presentation Awards", "detail": "Closing Ceremony"},
        {"day": D2, "session": LAB, "time": "09:00–09:30", "type": "session", "session_title": "Laboratory Briefing",
         "detail": "Officiated by the Advisor of OSM and the Dean/Deputy Dean of MJIIT"},
        {"day": D2, "session": LAB, "time": "09:30–13:00", "type": "session", "session_title": "Lab Tour and Sharing Session I"},
        {"day": D2, "session": LAB, "time": "13:00–14:00", "type": "break", "session_title": "Lunch Break"},
        {"day": D2, "session": LAB, "time": "14:00–16:00", "type": "session", "session_title": "Lab Tour and Sharing Session II"},
        {"day": D2, "session": LAB, "time": "16:00–16:30", "type": "break", "session_title": "Tea Break and Networking Discussion"},
        {"day": D2, "session": LAB, "time": "16:30", "type": "session", "session_title": "Programme End"},
    ]
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("flipbook")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    items = build(pages(a.flipbook))
    items, notes = H.apply_supplement(items)
    path = os.path.join(ROOT, "index.html")
    src = open(path).read()
    data = json.loads(re.search(r'<script type="application/json" id="__ssr_data__">(.*?)</script>', src, re.S).group(1))
    for w in H.report(items, data.get("speakers", [])):
        print("  ! WARNING:", w)
    for n in notes:
        print("  " + n)
    for it in items:
        if it.get("papers"):
            print(f"  {it['session_title']}: {len(it['papers'])} papers ->", ", ".join(p["id"] for p in it["papers"]))
    if a.check:
        print("--check: index.html not modified."); return
    key = '  "program": '
    start = src.index(key); arr = start + len(key)
    _, end = json.JSONDecoder().raw_decode(src[arr:])
    new = src[:arr] + json.dumps(items, ensure_ascii=False, indent=2).replace("\n", "\n  ") + src[arr + end:]
    if new == src:
        print("No changes."); return
    open(path, "w").write(new); print(f"index.html updated: {len(items)} schedule entries.")


if __name__ == "__main__":
    main()
