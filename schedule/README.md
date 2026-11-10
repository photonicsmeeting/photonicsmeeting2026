# Schedule importer (handbook → website)

The website's **Schedule & Sessions** section is filled from the conference handbook (`.docx`).
Replace the handbook, run one command, and the site data is rewritten.

```sh
python3 schedule/import_handbook.py            # read PM26_Conference_Handbook*.docx from the repo root, update index.html
python3 schedule/import_handbook.py --check    # parse + report only (nothing is written)
python3 schedule/import_handbook.py --docx "path/to/other.docx"
```
Then commit + push `index.html` (GitHub Pages updates in ~1 min). Running it twice is safe —
it says "No changes" when the site already matches the handbook.

## What the importer reads
Only the programme tables. Everything else in the handbook (welcome text, topics, past editions) is ignored.

| In the .docx | Becomes |
|---|---|
| Heading 1 `Programme · <day>` | a day (several days = several such headings) |
| a **one-cell** table row (e.g. "Invited Speaker Session") | a session card heading |
| a **two-cell** row `hh:mm–hh:mm` ⟶ title (+ 2nd line) | a row in that session |
| `Keynote 1 · Name` / `Invited Speaker 2 · Name` (2nd line = affiliation) | a speaker row with their photo + badge |
| titles containing break / lunch / tea | quiet break row |
| titles containing ceremony / award / certificate / photo | ceremony row |

**Keep this structure when editing the docx** (headings and tables as they are now) and the import keeps working.
It reports gaps/overlaps between consecutive times and any speaker that is not in the website's speaker list
(no photo would be shown), so typos are caught before publishing.

## Details that are not in the handbook yet — `schedule/supplement.json`
Agreed information that the .docx doesn't contain (yet) lives in `supplement.json`; the importer applies it
after reading the handbook, so a re-import never wipes it:

* `"days"` — a whole extra day (currently **Wednesday, 11 November: Laboratory Visit & Networking, 09:00–16:30**).
  It is added only if the handbook has no such day; once the handbook has it, the handbook wins and the importer
  tells you the entry can be deleted.
* `"patches"` — overwrite fields on matching entries (currently the **Opening Ceremony** officiating line, naming
  Prof. Ir. Dr. Sulaiman Wadi Harun and Prof. Madya Ir. Dr. Zool Hilmi bin Ismail). A patch that matches nothing is reported, so it cannot go stale silently.

When you add the same information to the handbook, delete the matching entry from `supplement.json`.

## Data written to `index.html`
`program` inside the `__ssr_data__` JSON — one object per row:
`day, session, time, type (keynote|invited|session|break|ceremony|registration), session_title,
 label, speaker, detail`. Speaker photos are looked up from the `speakers` list by exact name.

Other site text for this section lives in `content`: `program_sub` (subtitle) and `program_footnote`
(an optional italic note under the schedule — empty now that Day 2 is on the page).

## Presentation lists (paper titles) — `papers`
**Presentation Session I** and **II** each carry a collapsible "Presentation list" on the website. Until titles exist it
shows "Coming soon". To fill it, put the papers into the matching patch in `supplement.json` (the `"papers": []` entry):

```json
{ "match": {"type": "session", "session_title": "Presentation Session I"},
  "set": { "papers": [
      {"time": "15:10–15:30", "title": "Title of the paper", "authors": "A. Author, B. Author"},
      {"time": "15:30–15:50", "title": "Another title",      "authors": "C. Author"} ] } }
```
`time` and `authors` are optional. Then run `python3 schedule/import_handbook.py` and push. The paper that is on
(per the planned times) is highlighted while the session is live.

## Updating from the handbook FLIPBOOK (.html) — `import_flipbook.py`
The current source of truth is `PM26_Conference_Handbook_Flipbook.html`:
```sh
python3 schedule/import_flipbook.py "path/to/PM26_Conference_Handbook_Flipbook.html"          # rewrites `program` in index.html
python3 schedule/import_flipbook.py "path/to/PM26_Conference_Handbook_Flipbook.html" --check  # report only
```
It reads the **paper IDs, time slots, titles and presenters** of both presentation sessions straight from the flipbook text.
The rest of the programme (speakers, topics, MC / chairs / time keepers, breaks, Day 2) is typed in `build()` inside the script —
edit it there when the handbook changes. `supplement.json` still adds the officiating guests' photos.
(`import_handbook.py` + the `.docx` remains available, but the flipbook is now newer.)
