# AGENTS.md — Project Brain (shared by opencode + Claude Code)

This file is auto-read by opencode (and Claude Code) when the project folder is
opened, so either tool instantly understands the project WITHOUT you re-explaining.
Keep it accurate when things change.

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
    `~/Documents/VibeCodeProject/photonicsmeeting26`), **NOT** inside Google Drive.
  - **Office PC (Windows)** → edited with **Claude Code**, in a **local folder** (e.g.
    `C:\Users\<you>\Documents\photonicsmeeting26`), **NOT** inside Google Drive.
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

## Conventions / notes for the AI
- Edit `index.html` directly. Keep CSS in the `<style>` block and JS in the
  `<script>` block at the bottom. Design tokens are CSS variables in `:root`.
- When adding user-provided content (speakers, dates, fees, FAQ, etc.), prefer
  updating the inline `__ssr_data__` JSON block (and the matching `render*` JS
  functions) rather than hard-coding into HTML.
- All dynamic text inserted via JS MUST go through the `esc()` / `escAttr()`
  helpers to stay XSS-safe (already present in the script).
- The site is embedded in Google Sites via iframe on some pages — keep the
  `postMessage` height-notify logic (`notifyHeight`) intact.
- Do NOT introduce external CDN dependencies unless necessary; fonts (Sora/Inter)
  are the only external links and should stay.
- `CNAME`, `pm26.png`, `banner.jpeg`, `index.html` are the only published assets —
  never delete them.
- Keep `.claude/`, `.opencode/`, and `speakers/` gitignored.
