#!/usr/bin/env python3
"""REGENERATE the PM26 CFP poster HTML from index.html's __ssr_data__ JSON.

!! WARNING: running this OVERWRITES poster/pm26-cfp-poster.html, discarding any
!! hand-made fine-tuning in that file. Use it only when the WEBSITE DATA changed
!! (new speaker, new fees/dates) and you want a fresh poster rebuilt from it.
!! For small tweaks, edit pm26-cfp-poster.html directly, then re-render the PNG
!! (command in poster/README.md).
"""
import json, re, base64, random, html as H, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (parent of poster/)
src = open(os.path.join(ROOT, "index.html")).read()
data = json.loads(re.search(r'<script type="application/json" id="__ssr_data__">(.*?)</script>', src, re.S).group(1))
cfg, content = data["config"], data["content"]

logo_b64 = base64.b64encode(open(os.path.join(ROOT, "pm26.png"), "rb").read()).decode()

# --- background network-node SVG (deterministic) ---
random.seed(26)
W, Hh = 1240, 1754
pts = [(random.uniform(0, W), random.uniform(0, Hh)) for _ in range(70)]
lines, dots = [], []
for i, (x, y) in enumerate(pts):
    r = random.uniform(1.2, 3.2)
    dots.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#7FD8F0" opacity="{random.uniform(.15,.5):.2f}"/>')
    for j in range(i + 1, len(pts)):
        x2, y2 = pts[j]
        d = ((x - x2) ** 2 + (y - y2) ** 2) ** 0.5
        if d < 170 and random.random() < .5:
            lines.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#4FA8D8" stroke-width="0.7" opacity="{max(.03, .16 - d/1400):.2f}"/>')
net_svg = f'<svg class="net" viewBox="0 0 {W} {Hh}" xmlns="http://www.w3.org/2000/svg">{"".join(lines)}{"".join(dots)}</svg>'

# --- speakers ---
sp_cards = ""
for s in data["speakers"]:
    aff = H.escape(s["affiliation"])
    sp_cards += f'''
    <div class="sp">
      <img src="{s["photo_url"]}" alt="">
      <div class="sp-name">{H.escape(s["name"])}</div>
      <div class="sp-aff">{aff}</div>
      <div class="sp-cty">{H.escape(s["country"]).upper()}</div>
    </div>'''

# --- topics ---
topics = [t.strip() for t in content["cfp_topics"].split("|")]
topic_chips = "".join(f'<div class="chip">{H.escape(t)}</div>' for t in topics)

# --- dates ---
date_rows = ""
for d in data["dates"]:
    hot = ' hot' if 'Paper' in d["milestone"] else ''
    date_rows += f'''<div class="row{hot}"><span class="row-l">{H.escape(d["milestone"])}</span><span class="row-r">{H.escape(d["date"])}</span></div>'''

# --- fees ---
fee_rows = ""
for f in data["fees"]:
    fee_rows += f'''<div class="row"><span class="row-l">{H.escape(f["category"])}</span><span class="row-r">{H.escape(f["fee"])}</span></div>'''

poster = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  :root {{
    --navy:#060B22; --navy2:#0B1233; --cyan:#22D3EE; --blue:#2057E0; --violet:#7C3AED;
    --gold:#E8C36A; --gold-dim:#C9A44C;
    --ink:#EAF2FF; --dim:#9FB0D0; --dimmer:#6D7FA5;
    --card:rgba(255,255,255,.045); --edge:rgba(255,255,255,.13);
    --spectrum:linear-gradient(90deg,#4E8CFF 0%,#22D3EE 45%,#A78BFA 100%);
  }}
  body {{ width:1240px; height:1754px; overflow:hidden; position:relative;
    font-family:'Inter',sans-serif; color:var(--ink);
    background:
      radial-gradient(900px 500px at 85% -5%, rgba(124,58,237,.30), transparent 60%),
      radial-gradient(800px 520px at -10% 8%, rgba(32,87,224,.42), transparent 60%),
      radial-gradient(900px 600px at 50% 108%, rgba(34,211,238,.16), transparent 55%),
      linear-gradient(165deg, #0A1233 0%, #060B22 55%, #071026 100%); }}
  .net {{ position:absolute; inset:0; width:100%; height:100%; }}
  .wrap {{ position:relative; padding:56px 64px 0; height:100%; display:flex; flex-direction:column; }}

  .toprow {{ display:flex; justify-content:space-between; align-items:center; }}
  .logochip {{ background:#fff; border-radius:16px; padding:10px 22px; box-shadow:0 10px 40px rgba(0,0,0,.45); }}
  .logochip img {{ height:58px; display:block; }}
  .org {{ text-align:right; font-size:13.5px; line-height:1.65; color:var(--dim); font-weight:500; }}
  .org b {{ color:var(--ink); font-weight:600; }}
  .org .idl {{ color:var(--gold); letter-spacing:.6px; font-weight:600; }}

  .eyebrow {{ margin-top:52px; font-size:16px; font-weight:700; letter-spacing:5px; color:var(--cyan); }}
  h1 {{ font-family:'Sora'; font-weight:800; font-size:108px; letter-spacing:-2px; line-height:1.02; margin-top:10px;
    background:var(--spectrum); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }}
  .sub {{ margin-top:20px; font-size:18px; line-height:1.6; color:var(--dim); max-width:940px; }}

  .pills {{ display:flex; gap:14px; margin-top:30px; }}
  .pill {{ display:flex; align-items:center; gap:9px; border:1px solid var(--edge); background:var(--card);
    border-radius:999px; padding:13px 24px; font-size:15.5px; font-weight:600; letter-spacing:.3px; white-space:nowrap; }}
  .pill.gold {{ border-color:rgba(232,195,106,.55); color:var(--gold); background:rgba(232,195,106,.07); }}
  .dot {{ width:8px; height:8px; border-radius:50%; background:var(--cyan); }}
  .pill.gold .dot {{ background:var(--gold); }}

  .slab {{ font-family:'Sora'; font-size:14px; font-weight:700; letter-spacing:3.4px; color:var(--dimmer);
    margin:44px 0 18px; display:flex; align-items:center; gap:14px; }}
  .slab::after {{ content:''; flex:1; height:1px; background:linear-gradient(90deg,var(--edge),transparent); }}
  .slab b {{ color:var(--ink); font-weight:700; }}

  .sps {{ display:grid; grid-template-columns:repeat(5,1fr); gap:14px; }}
  .sp {{ background:var(--card); border:1px solid var(--edge); border-radius:16px; padding:22px 12px 17px; text-align:center; }}
  .sp img {{ width:118px; height:118px; border-radius:50%; object-fit:cover; object-position:top;
    border:2.5px solid rgba(232,195,106,.75); box-shadow:0 0 0 5px rgba(34,211,238,.14); }}
  .sp-name {{ font-family:'Sora'; font-size:13.5px; font-weight:700; line-height:1.3; margin-top:12px; min-height:36px;
    display:flex; align-items:center; justify-content:center; }}
  .sp-aff {{ font-size:11.5px; color:var(--dim); line-height:1.45; margin-top:6px; min-height:50px;
    display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }}
  .sp-cty {{ font-size:10.5px; font-weight:700; letter-spacing:1.8px; color:var(--cyan); margin-top:8px; }}

  .chips {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }}
  .chip {{ border:1px solid var(--edge); background:var(--card); border-radius:11px; padding:16px 10px;
    font-size:13.5px; font-weight:600; text-align:center; color:var(--ink); line-height:1.3; }}

  .cols {{ display:grid; grid-template-columns:1fr 1fr; gap:22px; }}
  .panel {{ background:var(--card); border:1px solid var(--edge); border-radius:18px; padding:26px 30px 18px; }}
  .panel h3 {{ font-family:'Sora'; font-size:15px; font-weight:700; letter-spacing:2.6px; color:var(--cyan); margin-bottom:12px; }}
  .row {{ display:flex; justify-content:space-between; align-items:baseline; gap:12px;
    padding:12.5px 0; border-bottom:1px solid rgba(255,255,255,.07); font-size:15px; }}
  .row:last-child {{ border-bottom:none; }}
  .row-l {{ color:var(--dim); font-weight:500; }}
  .row-r {{ font-weight:700; white-space:nowrap; }}
  .row.hot .row-l, .row.hot .row-r {{ color:var(--gold); }}
  .row.hot .row-l {{ font-weight:600; }}
  .fee-note {{ font-size:12px; color:var(--dimmer); padding-top:11px; }}

  .pub {{ margin-top:26px; display:flex; align-items:center; gap:20px; border-radius:18px; padding:24px 30px;
    background:linear-gradient(90deg, rgba(32,87,224,.16), rgba(34,211,238,.09), rgba(124,58,237,.14));
    border:1px solid rgba(34,211,238,.30); }}
  .pub-mark {{ flex:0 0 auto; width:58px; height:58px; border-radius:14px; background:var(--spectrum);
    display:grid; place-items:center; }}
  .pub-mark svg {{ width:30px; height:30px; }}
  .pub-t {{ font-size:15px; line-height:1.6; color:var(--dim); }}
  .pub-t b {{ color:var(--ink); }}
  .pub-t .gold {{ color:var(--gold); font-weight:600; }}

  .foot {{ margin-top:auto; margin-left:-64px; margin-right:-64px; padding:28px 64px 30px;
    background:rgba(3,6,18,.72); border-top:1px solid var(--edge);
    display:flex; justify-content:space-between; align-items:center; }}
  .foot-submit {{ font-family:'Sora'; font-size:16px; font-weight:700; letter-spacing:.5px;
    background:linear-gradient(90deg,#E8C36A,#F5DFA8); color:#241A05; padding:17px 30px; border-radius:12px; }}
  .foot-info {{ text-align:right; font-size:14px; line-height:1.8; color:var(--dim); }}
  .foot-info b {{ color:var(--ink); font-weight:600; }}
  .foot-info .web {{ color:var(--cyan); font-weight:700; font-size:15px; letter-spacing:.4px; }}
</style></head>
<body>
{net_svg}
<div class="wrap">

  <div class="toprow">
    <div class="logochip"><img src="data:image/png;base64,{logo_b64}" alt="Photonics Meeting 2026"></div>
    <div class="org">Organised by the <b>Optical Society of Malaysia (OSM)</b><br>
    <span class="idl">✦ In celebration of the International Day of Light</span></div>
  </div>

  <div class="eyebrow">{H.escape(content["hero_title_line1"]).upper()} PHOTONICS MEETING</div>
  <h1>CALL FOR PAPERS</h1>
  <div class="sub">{H.escape(content["cfp_sub"])}</div>

  <div class="pills">
    <div class="pill gold"><span class="dot"></span>8–9 September 2026</div>
    <div class="pill"><span class="dot"></span>MJIIT, UTM Kuala Lumpur, Malaysia</div>
    <div class="pill"><span class="dot"></span>Keynotes · Technical Sessions · Workshops</div>
  </div>

  <div class="slab"><b>KEYNOTE &amp; INVITED SPEAKERS</b></div>
  <div class="sps">{sp_cards}</div>

  <div class="slab"><b>CONFERENCE TOPICS</b></div>
  <div class="chips">{topic_chips}</div>

  <div style="height:34px"></div>
  <div class="cols">
    <div class="panel">
      <h3>IMPORTANT DATES</h3>
      {date_rows}
    </div>
    <div class="panel">
      <h3>REGISTRATION FEES</h3>
      {fee_rows}
      <div class="fee-note">Early bird rates apply before 31 July 2026 · Fees include conference materials, proceedings &amp; meals</div>
    </div>
  </div>

  <div class="pub">
    <div class="pub-mark"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.6">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5v14z"/>
      <path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/></svg></div>
    <div class="pub-t">Accepted papers will be published in the <b>IOP Journal of Physics: Conference Series</b> (ISSN 1742-6596)
      — peer-reviewed &amp; open access, indexed in <span class="gold">Scopus</span> and
      <span class="gold">Web of Science (CPCI)</span>.</div>
  </div>

  <div class="foot">
    <div class="foot-submit">SUBMIT YOUR PAPER → morressier.com</div>
    <div class="foot-info">
      <span class="web">photonics-meeting.com</span><br>
      <b>{H.escape(cfg["contact_email"])}</b> · {H.escape(content["footer_copy"])}
    </div>
  </div>

</div>
</body></html>'''

out = os.path.join(ROOT, "poster")
os.makedirs(out, exist_ok=True)
path = os.path.join(out, "pm26-cfp-poster.html")
open(path, "w").write(poster)
print("written:", path, f"({os.path.getsize(path)//1024} KB)")
