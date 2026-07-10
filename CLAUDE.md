# CLAUDE.md — Project Brain (auto-read by Claude Code)

This file is auto-read by Claude Code when the project folder is opened, so the
tool instantly understands the project WITHOUT you re-explaining. Keep it accurate
when things change.

**Stability note:** This file is edited ONLY when the project's workflow or conventions
change — never during routine feature/editing work (which touches `index.html` and the
data only). If a change to this file is ever needed, the AI must **ask you first**, so
you can run `git pull` on the other machine to keep its brain file in sync. (Content mirrors AGENTS.md so both tools stay in sync.)

---

## What this project is
A **single-page static website** for **Photonics Meeting 2026 (PM26)** — an annual
conference organised by the **Optical Society of Malaysia (OSM)**, held in
celebration of the **International Day of Light**.

- **Event:** 8–9 September 2026
- **Venue:** Malaysia-Japan International Institute of Technology (MJIIT),
  Universiti Teknologi Malaysia (UTM), Kuala Lumpur
- **Live site:** https://photonics-meeting.com  (custom domain via `CNAME`)
- **Published from:** GitHub repo `photonicsmeeting/photonicsmeeting2026`
  (GitHub Pages serves the site from the `main` branch root).

## How the site is built (IMPORTANT)
- Everything lives in **`index.html`** — all CSS is inline in `<style>`, all JS is
  inline in a `<script>` at the bottom. There is **no build step, no bundler, no
  framework**.
- Page data is **inlined as JSON** in a `<script type="application/json" id="__ssr_data__">`
  block near the bottom of `index.html`. The JS (`populateAll`) reads that block on
  boot and fills the DOM. **Zero network calls.**
- **⚠️ The JSON is the runtime source of truth — it OVERWRITES the static HTML.** On
  boot, `populateAll()` copies values from `__ssr_data__` into the matching elements
  (by `id`), so the text in the raw `<span>`/`<title>`/etc. markup is only a fallback
  that gets clobbered a split-second after load. Two rules follow:
  1. **To change any visible text you MUST edit the JSON value** (e.g. `nav_brand_name`,
     `page_title`), not just the HTML — otherwise your HTML edit is silently reverted at
     runtime. If you also touch the HTML, keep it in sync with the JSON.
  2. **Never delete a static element that `populateAll` still writes to**
     (`getElementById(...).textContent = ...`) — the `null` reference throws and
     silently breaks the rest of `populateAll`. Clear the JSON value (or the JS guard)
     instead. *(This is the exact trap that once left the navbar half-broken: HTML
     edited, JSON missed.)*
- A Google Apps Script backend (`Code.gs` + Google Sheets) **used to exist but has
  been removed** — the live fetch (`loadConferenceData()`) is commented out. Do NOT
  re-add backend dependencies; the site is fully static.
- **Images actually used:** `pm26.png` (logo, navbar + masthead), `banner.jpeg`
  (poster in masthead). These MUST stay.
- `speakers/` holds headshot images but they are currently **unused** — speaker
  cards render initials placeholders because `photo_url` is empty in the data.
  (Folder is gitignored; kept locally only.)

## How we work (workflow)
- Two machines, same project, **never edited at the same time** (different times of day):
  - **MacBook** → edited with **opencode**, in a **local folder** (e.g.
    `~/Documents/photonicsmeeting26`), **NOT** inside Google Drive.
  - **Office PC (Windows)** → edited with **Claude Code**, in a **local folder** (e.g.
    `C:\Users\<you>\Documents\VibeCodeProject\photonicsmeeting26`), **NOT** inside Google Drive.
- **Google Drive is NOT part of the repo workflow.** Each machine keeps its own local
  clone and the two sync through **GitHub** (push/pull). This avoids Drive's
  virtual-filesystem git failures on Windows and keeps things simple.
- **Sync is automatic and lightweight (no session boundary, no "done" keyword needed):**
  - **Pull once when returning to a machine:** the AI runs `git pull` before the *first*
    edit of a working spell (not before every micro-edit — nothing changes on the remote
    while you alone are actively working). This catches the other machine's work.
  - **Push after each logical chunk:** once a requested change (or a small batch of
    related tweaks) is complete, the AI runs `git commit -a` + `git push`. It does NOT
    pull/push on every tiny keystroke-level edit, to avoid needless git churn and token use.
  - Net effect: **pull when you arrive, push when a change is done.** You simply request
    edits; the AI keeps GitHub and the other machine in sync efficiently.
- **To publish to the live site, you MUST push to GitHub.** GitHub Pages rebuilds in
  ~1 min.
- **Before switching machines:** the other device will `git pull` automatically before
  its next edit (per the rule above), so just open the project and continue. The AI can
  verify with `git status`.
- **Editing this brain file:** only do it when workflow/conventions change, and always
  **ask the user first** so they can `git pull` on the other device to sync it. Routine
  feature work must never modify `AGENTS.md`/`CLAUDE.md`.

## Conventions / notes for the AI
- Edit `index.html` directly. Keep CSS in the `<style>` block and JS in the
  `<script>` block at the bottom. Design tokens are CSS variables in `:root`.
- When adding or changing **any** user-visible content (brand text, page/tab titles,
  speakers, dates, fees, FAQ, etc.), **update the inline `__ssr_data__` JSON block**
  (and the matching `render*` / `populateAll` JS) — the JSON overrides the HTML at
  runtime (see "How the site is built"), so a raw-HTML-only edit will not stick.
- All dynamic text inserted via JS MUST go through the `esc()` / `escAttr()`
  helpers to stay XSS-safe (already present in the script).
- The site is embedded in Google Sites via iframe on some pages — keep the
  `postMessage` height-notify logic (`notifyHeight`) intact.
- Do NOT introduce external CDN dependencies unless necessary; fonts (Sora/Inter)
  are the only external links and should stay.
- `CNAME`, `pm26.png`, `banner.jpeg`, `index.html` are the only published assets —
  never delete them.
- Keep `.claude/`, `.opencode/`, and `speakers/` gitignored.
