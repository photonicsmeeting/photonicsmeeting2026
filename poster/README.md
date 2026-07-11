# PM26 Call-for-Papers Posters

Print-ready A4 posters built from the live website data. Served by GitHub
Pages, so the PNGs are publicly downloadable at:

    https://photonics-meeting.com/poster/pm26-cfp-poster.png          (CFP 1 — dark)
    https://photonics-meeting.com/poster/pm26-cfp-poster-bright.png   (CFP 2 — bright)

The website's **Call for Papers** section links to the dark one
("Download CFP Poster").

## Files

| File | What it is |
|---|---|
| `pm26-cfp-poster.png` / `.html` | **CFP 1 — dark theme.** PNG is A4 @ 300 DPI (2480×3508); HTML is its render source. |
| `pm26-cfp-poster-bright.png` / `.html` | **CFP 2 — bright theme.** Same content, light design. |
| `make_poster.py` | **The design source of truth.** Regenerates BOTH HTML files from `../index.html` — data comes from the `__ssr_data__` JSON (dates, fees, speakers + photos, topics) and the About Us section (brief). Design changes go in here so they survive regeneration. |
| `cfp-poster-prompt.txt` | AI image-generation prompts (full-info + background-only variants). |

## Workflow: website data changed (dates/fees/speakers/about)

The posters do NOT update by themselves — regenerate after editing the site:

```sh
python3 poster/make_poster.py    # rebuild both HTMLs from current index.html
```

then re-render both PNGs (macOS path shown; on Windows use `chrome.exe`):

```sh
for v in pm26-cfp-poster pm26-cfp-poster-bright; do
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --headless=new --disable-gpu --hide-scrollbars \
    --window-size=1240,1754 --force-device-scale-factor=2 \
    --virtual-time-budget=15000 \
    --screenshot="poster/$v.png" "file://$PWD/poster/$v.html"
done
```

(run from the repo root; 1240×1754 @ 2× = 2480×3508 = exact A4 @ 300 DPI)

Commit + push — the live download links update in ~1 min via GitHub Pages.

## Workflow: fine-tune the design

Edit the CSS/layout inside `make_poster.py` (NOT the generated HTML files —
they get overwritten on the next regeneration), then run the two commands
above. Theme colors live in the `THEMES` dict (dark + bright).
