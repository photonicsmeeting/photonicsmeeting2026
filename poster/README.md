# PM26 Call-for-Papers Poster

Print-ready A4 poster built from the live website data. Served by GitHub Pages,
so the PNG is publicly downloadable at:

    https://photonics-meeting.com/poster/pm26-cfp-poster.png

The website's **Call for Papers** section links to it ("Download CFP Poster").

## Files

| File | What it is |
|---|---|
| `pm26-cfp-poster.png` | The poster — A4 @ 300 DPI (2480×3508). This is what visitors download. |
| `pm26-cfp-poster.html` | **Editable source of truth.** Self-contained (fonts via Google Fonts, all images embedded as base64). Open in a browser to preview. |
| `make_poster.py` | Regenerates the HTML from `../index.html`'s `__ssr_data__` JSON. ⚠️ Overwrites hand-tuned HTML — only run after website data changes (new speakers, fees, dates). |
| `cfp-poster-prompt.txt` | AI image-generation prompts (full-info + background-only variants). |

## Workflow: fine-tune the poster

1. Edit `pm26-cfp-poster.html` directly (it is plain HTML/CSS).
2. Re-render the PNG (macOS path shown; on Windows use `chrome.exe`):

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1240,1754 --force-device-scale-factor=2 \
  --virtual-time-budget=15000 \
  --screenshot="poster/pm26-cfp-poster.png" \
  "file://$PWD/poster/pm26-cfp-poster.html"
```

(run from the repo root; 1240×1754 @ 2× = 2480×3508 = exact A4 @ 300 DPI)

3. Commit **both** the HTML and the PNG, push — the live download link updates
   in ~1 min via GitHub Pages.

## Workflow: website data changed (speakers/fees/dates)

```sh
python3 poster/make_poster.py   # rebuilds HTML from index.html JSON
```

then re-render the PNG as above. Note this discards manual HTML tweaks.
