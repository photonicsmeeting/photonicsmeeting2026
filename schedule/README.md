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

## Data written to `index.html`
`program` inside the `__ssr_data__` JSON — one object per row:
`day, session, time, type (keynote|invited|session|break|ceremony|registration), session_title,
 label, speaker, detail`. Speaker photos are looked up from the `speakers` list by exact name.

Other site text for this section lives in `content`: `program_sub` (subtitle) and `program_footnote`
(the "Wednesday, 11 November — program to be announced" line; clear it once Day 2 is in the handbook).
