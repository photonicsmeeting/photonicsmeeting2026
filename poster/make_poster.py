#!/usr/bin/env python3
"""REGENERATE the PM26 CFP posters (dark + bright) from index.html's data.

Reads the __ssr_data__ JSON block AND the About Us section of ../index.html,
then writes:
    poster/pm26-cfp-poster.html         (dark theme  — CFP 1)
    poster/pm26-cfp-poster-bright.html  (bright theme — CFP 2)

!! Running this OVERWRITES both HTML files, discarding hand-made edits in
!! them. Design lives HERE in the generator; data lives in index.html.
Render PNGs afterwards — commands in poster/README.md.
"""
import json, re, base64, random, html as H, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (parent of poster/)
src = open(os.path.join(ROOT, "index.html")).read()
data = json.loads(re.search(r'<script type="application/json" id="__ssr_data__">(.*?)</script>', src, re.S).group(1))
cfg, content = data["config"], data["content"]

# --- About brief: pulled from the website's About Us section (1st + 3rd paragraph) ---
about_html = re.search(r'<div class="about-body">(.*?)</div>', src, re.S)
about_text = ""
if about_html:
    paras = [re.sub(r"<[^>]+>", "", p).strip() for p in re.findall(r"<p>(.*?)</p>", about_html.group(1), re.S)]
    if paras:
        about_text = "PM26 is OSM's annual conference on photonics & optics — share research, exchange ideas, build collaborations."
if not about_text:  # fallback if the About section markup ever changes
    about_text = ("The OSM Photonics Meeting 2026 (PM26) is an annual event organised by the "
                  "Optical Society of Malaysia (OSM) in celebrating International Day of Light.")

logo_b64 = base64.b64encode(open(os.path.join(ROOT, "pm26.png"), "rb").read()).decode()
utm_b64 = base64.b64encode(open(os.path.join(ROOT, "utm-logo.png"), "rb").read()).decode()
osm_b64 = base64.b64encode(open(os.path.join(ROOT, "osm-logo.png"), "rb").read()).decode()
iop_b64 = base64.b64encode(open(os.path.join(ROOT, "iop-logo.png"), "rb").read()).decode()
scopus_b64 = base64.b64encode(open(os.path.join(ROOT, "scopus-logo.png"), "rb").read()).decode()
wos_b64 = base64.b64encode(open(os.path.join(ROOT, "wos-logo.png"), "rb").read()).decode()
kl_petronas_b64 = base64.b64encode(open(os.path.join(ROOT, "attractions", "petronas.jpg"), "rb").read()).decode()
kl_tower_b64    = base64.b64encode(open(os.path.join(ROOT, "attractions", "kl-tower.jpg"), "rb").read()).decode()
kl_merdeka_b64  = base64.b64encode(open(os.path.join(ROOT, "attractions", "merdeka-square.jpg"), "rb").read()).decode()

THEMES = {
    "dark": dict(
        out="pm26-cfp-poster.html",
        bg=("radial-gradient(900px 500px at 85% -5%, rgba(124,58,237,.30), transparent 60%),"
            "radial-gradient(800px 520px at -10% 8%, rgba(32,87,224,.42), transparent 60%),"
            "radial-gradient(900px 600px at 50% 108%, rgba(34,211,238,.16), transparent 55%),"
            "linear-gradient(165deg, #0A1233 0%, #060B22 55%, #071026 100%)"),
        ink="#EAF2FF", dim="#9FB0D0", dimmer="#6D7FA5",
        card="rgba(255,255,255,.07)", edge="rgba(255,255,255,.17)",
        gold="#E8C36A", gold_edge="rgba(232,195,106,.55)", gold_bg="rgba(232,195,106,.07)",
        spectrum="linear-gradient(90deg,#4E8CFF 0%,#22D3EE 45%,#A78BFA 100%)",
        cyan="#22D3EE", rowline="rgba(255,255,255,.07)",
        net_dot="#7FD8F0", net_line="#4FA8D8", net_dot_op=(0.15, 0.5), net_line_base=0.16,
        chip_shadow="0 8px 32px rgba(0,0,0,.28)", logochip_border="none",
        orbs=[("rgba(32,87,224,.50)",150,500,300),("rgba(124,58,237,.42)",1060,760,320),
              ("rgba(34,211,238,.30)",300,1280,300),("rgba(124,58,237,.28)",980,1560,260)],
        ring="rgba(232,195,106,.75)", halo="rgba(34,211,238,.14)",
        pub_bg="linear-gradient(90deg, rgba(32,87,224,.16), rgba(34,211,238,.09), rgba(124,58,237,.14))",
        pub_edge="rgba(34,211,238,.30)",
        foot_bg="rgba(3,6,18,.72)",
        submit_bg="linear-gradient(90deg,#E8C36A,#F5DFA8)", submit_ink="#241A05",
        web_accent="#22D3EE",
    ),
    "bright": dict(
        out="pm26-cfp-poster-bright.html",
        bg=("radial-gradient(900px 500px at 85% -5%, rgba(124,58,237,.16), transparent 60%),"
            "radial-gradient(800px 520px at -10% 8%, rgba(32,87,224,.18), transparent 60%),"
            "radial-gradient(900px 600px at 50% 108%, rgba(34,211,238,.15), transparent 55%),"
            "linear-gradient(165deg, #F7F9FE 0%, #FFFFFF 55%, #EFF4FF 100%)"),
        ink="#0B1230", dim="#475569", dimmer="#94A3B8",
        card="rgba(255,255,255,.52)", edge="rgba(255,255,255,.95)",
        gold="#A87818", gold_edge="rgba(168,120,24,.45)", gold_bg="rgba(232,195,106,.14)",
        spectrum="linear-gradient(90deg,#2057E0 0%,#0891B2 45%,#7C3AED 100%)",
        cyan="#0891B2", rowline="rgba(10,18,51,.08)",
        net_dot="#2057E0", net_line="#2057E0", net_dot_op=(0.08, 0.25), net_line_base=0.09,
        chip_shadow="0 8px 32px rgba(10,18,51,.12)", logochip_border="1px solid #E2E8F0",
        orbs=[("rgba(32,87,224,.26)",150,500,300),("rgba(124,58,237,.20)",1060,760,320),
              ("rgba(34,211,238,.24)",300,1280,300),("rgba(124,58,237,.16)",980,1560,260)],
        ring="rgba(168,120,24,.65)", halo="rgba(32,87,224,.10)",
        pub_bg="linear-gradient(90deg, rgba(32,87,224,.07), rgba(34,211,238,.05), rgba(124,58,237,.07))",
        pub_edge="rgba(32,87,224,.30)",
        foot_bg="rgba(10,18,51,.035)",
        submit_bg="linear-gradient(90deg,#2057E0,#0891B2)", submit_ink="#FFFFFF",
        web_accent="#2057E0",
    ),
}

# --- shared content fragments ---
def net_svg(T):
    random.seed(26)
    W, Hh = 1240, 1754
    pts = [(random.uniform(0, W), random.uniform(0, Hh)) for _ in range(70)]
    lines, dots = [], []
    lo, hi = T["net_dot_op"]
    for i, (x, y) in enumerate(pts):
        r = random.uniform(1.2, 3.2)
        dots.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{T["net_dot"]}" opacity="{random.uniform(lo,hi):.2f}"/>')
        for j in range(i + 1, len(pts)):
            x2, y2 = pts[j]
            d = ((x - x2) ** 2 + (y - y2) ** 2) ** 0.5
            if d < 170 and random.random() < .5:
                lines.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{T["net_line"]}" stroke-width="0.7" opacity="{max(.02, T["net_line_base"] - d/1400):.2f}"/>')
    return f'<svg class="net" viewBox="0 0 {W} {Hh}" xmlns="http://www.w3.org/2000/svg">{"".join(lines)}{"".join(dots)}</svg>'

def orbs_html(T):
    return "".join(
        f'<div class="orb" style="left:{x-r}px;top:{y-r}px;width:{2*r}px;height:{2*r}px;'
        f'background:radial-gradient(circle,{c} 0%,transparent 70%);"></div>'
        for c, x, y, r in T["orbs"])

sp_cards = ""
for s in data["speakers"]:
    sp_cards += f'''
    <div class="sp">
      <img src="{s["photo_url"]}" alt="">
      <div class="sp-name">{H.escape(s["name"])}</div>
      <div class="sp-aff">{H.escape(s["affiliation"])}</div>
      <div class="sp-cty">{H.escape(s["country"]).upper()}</div>
    </div>'''

topic_chips = "".join(f'<div class="chip">{H.escape(t.strip())}</div>' for t in content["cfp_topics"].split("|"))

date_rows = "".join(
    f'''<div class="row{' hot' if 'Paper' in d["milestone"] else ''}"><span class="row-l">{H.escape(d["milestone"])}</span><span class="row-r">{H.escape(d["date"])}</span></div>'''
    for d in data["dates"])

fee_rows = "".join(
    f'''<div class="row"><span class="row-l">{H.escape(f["category"])}</span><span class="row-r">{H.escape(f["fee"])}</span></div>'''
    for f in data["fees"])


def render(T):
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  :root {{
    --ink:{T["ink"]}; --dim:{T["dim"]}; --dimmer:{T["dimmer"]};
    --card:{T["card"]}; --edge:{T["edge"]}; --gold:{T["gold"]}; --cyan:{T["cyan"]};
    --spectrum:{T["spectrum"]};
  }}
  body {{ width:1240px; height:1754px; overflow:hidden; position:relative;
    font-family:'Inter',sans-serif; color:var(--ink);
    background:{T["bg"]}; }}
  .net {{ position:absolute; inset:0; width:100%; height:100%; }}
  .orb {{ position:absolute; border-radius:50%; filter:blur(60px); }}
  .pill, .sp, .chip, .panel, .pub, .foot {{ backdrop-filter:blur(16px) saturate(150%);
    -webkit-backdrop-filter:blur(16px) saturate(150%); }}
  .wrap {{ position:relative; padding:52px 64px 0; height:100%; display:flex; flex-direction:column; }}

  .toprow {{ display:flex; justify-content:space-between; align-items:center; }}
  .topright {{ display:flex; align-items:center; gap:12px; }}
  .logochip.small {{ padding:9px 14px; border-radius:13px; }}
  .logochip.small img {{ height:42px; }}
  .logochip {{ background:#fff; border-radius:16px; padding:10px 22px; border:{T["logochip_border"]};
    box-shadow:0 10px 40px rgba(0,0,0,.18); }}
  .logochip img {{ height:56px; display:block; }}
  .org {{ text-align:right; font-size:13.5px; line-height:1.65; color:var(--dim); font-weight:500; }}
  .org b {{ color:var(--ink); font-weight:600; }}
  .org .idl {{ color:var(--gold); letter-spacing:.6px; font-weight:600; }}

  .eyebrow {{ margin-top:50px; font-size:15px; font-weight:700; letter-spacing:5px; color:var(--cyan); }}
  h1 {{ font-family:'Sora'; font-weight:800; font-size:102px; letter-spacing:-2px; line-height:1.02; margin-top:10px;
    background:var(--spectrum); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }}
  .sub {{ margin-top:16px; font-size:24px; line-height:1.5; color:var(--dim); max-width:980px; }}

  .pills {{ display:flex; gap:14px; margin-top:8px; }}
  .pill {{ display:flex; align-items:center; gap:9px; border:1px solid var(--edge); background:var(--card);
    border-radius:999px; padding:12px 24px; font-size:15px; font-weight:600; letter-spacing:.3px;
    white-space:nowrap; box-shadow:{T["chip_shadow"]}; }}
  .pill.gold {{ border-color:{T["gold_edge"]}; color:var(--gold); background:{T["gold_bg"]}; }}
  .dot {{ width:8px; height:8px; border-radius:50%; background:var(--cyan); }}
  .pill.gold .dot {{ background:var(--gold); }}

  .about {{ margin-top:12px; font-size:16px; line-height:1.4; color:var(--dim);
    border-left:3px solid var(--cyan); padding-left:18px; }}

  .kl-strip {{ display:flex; gap:14px; margin-top:14px; }}
  .kl-strip img {{ flex:1; height:78px; width:100%; object-fit:cover; border-radius:14px;
    border:1px solid var(--edge); box-shadow:{T["chip_shadow"]}; }}
  .kl-cap {{ margin-top:7px; font-size:13px; font-weight:600; letter-spacing:1.5px; color:var(--cyan); text-align:center; }}

  .slab {{ font-family:'Sora'; font-size:14px; font-weight:700; letter-spacing:3.4px; color:var(--dimmer);
    margin:16px 0 10px; display:flex; align-items:center; gap:14px; }}
  .slab::after {{ content:''; flex:1; height:1px; background:linear-gradient(90deg,var(--edge),transparent); }}
  .slab b {{ color:var(--ink); font-weight:700; }}

  .sps {{ display:grid; grid-template-columns:repeat(5,1fr); gap:14px; }}
  .sp {{ background:var(--card); border:1px solid var(--edge); border-radius:16px; padding:16px 10px 12px;
    text-align:center; box-shadow:{T["chip_shadow"]}; }}
  .sp img {{ width:72px; height:72px; border-radius:50%; object-fit:cover; object-position:top;
    border:2.5px solid {T["ring"]}; box-shadow:0 0 0 5px {T["halo"]}; }}
  .sp-name {{ font-family:'Sora'; font-size:13.5px; font-weight:700; line-height:1.3; margin-top:12px; min-height:36px;
    display:flex; align-items:center; justify-content:center; }}
  .sp-aff {{ font-size:10px; color:var(--dim); line-height:1.45; margin-top:5px; min-height:48px;
    display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }}
  .sp-cty {{ font-size:10px; font-weight:700; letter-spacing:1.8px; color:var(--cyan); margin-top:6px; }}

  .chips {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }}
  .chip {{ border:1px solid var(--edge); background:var(--card); border-radius:11px; padding:16px 10px;
    font-size:18px; font-weight:600; text-align:center; color:var(--ink); line-height:1.3;
    box-shadow:{T["chip_shadow"]}; }}

  .cols {{ display:grid; grid-template-columns:1fr 1fr; gap:22px; }}
  .panel {{ background:var(--card); border:1px solid var(--edge); border-radius:18px; padding:26px 30px 18px;
    box-shadow:{T["chip_shadow"]}; }}
  .panel h3 {{ font-family:'Sora'; font-size:14.5px; font-weight:700; letter-spacing:2.6px; color:var(--cyan); margin-bottom:10px; }}
  .row {{ display:flex; justify-content:space-between; align-items:baseline; gap:12px;
    padding:6px 0; border-bottom:1px solid {T["rowline"]}; font-size:20px; }}
  .row:last-child {{ border-bottom:none; }}
  .row-l {{ color:var(--dim); font-weight:500; }}
  .row-r {{ font-weight:700; white-space:nowrap; }}
  .row.hot .row-l, .row.hot .row-r {{ color:var(--gold); }}
  .row.hot .row-l {{ font-weight:600; }}
  .fee-note {{ font-size:11.5px; color:var(--dimmer); padding-top:9px; }}

  .pub {{ margin-top:18px; display:flex; align-items:center; gap:20px; border-radius:18px; padding:20px 30px;
    background:{T["pub_bg"]}; border:1px solid {T["pub_edge"]}; }}
  .pub-t {{ flex:1; font-size:20px; line-height:1.55; color:var(--dim); }}
  .pub-logos {{ display:flex; align-items:center; gap:10px; flex:0 0 auto; }}
  .pub-chip {{ background:#fff; border-radius:11px; padding:9px 14px; display:flex; align-items:center;
    justify-content:center; box-shadow:0 3px 14px rgba(0,0,0,.15); }}
  .pub-chip img {{ display:block; }}
  .pub-t b {{ color:var(--ink); }}
  .pub-t .gold {{ color:var(--gold); font-weight:600; }}

  .foot {{ margin-top:auto; margin-left:-64px; margin-right:-64px; padding:20px 64px 22px;
    background:{T["foot_bg"]}; border-top:1px solid var(--edge);
    display:flex; justify-content:space-between; align-items:center; }}
  .foot-submit {{ font-family:'Sora'; font-size:15.5px; font-weight:700; letter-spacing:.5px;
    background:{T["submit_bg"]}; color:{T["submit_ink"]}; padding:16px 28px; border-radius:12px; }}
  .foot-info {{ text-align:right; font-size:17px; line-height:1.8; color:var(--dim); }}
  .foot-info b {{ color:var(--ink); font-weight:600; }}
  .foot-info .web {{ color:{T["web_accent"]}; font-weight:700; font-size:15px; letter-spacing:.4px; }}
</style></head>
<body>
{net_svg(T)}
{orbs_html(T)}
<div class="wrap">

  <div class="toprow">
    <div class="logochip"><img src="data:image/png;base64,{logo_b64}" alt="Photonics Meeting 2026"></div>
    <div class="topright">
      <div class="org">Organised by <b>Universiti Teknologi Malaysia (UTM)</b><br>
      &amp; the <b>Optical Society of Malaysia (OSM)</b><br>
      <span class="idl">✦ In celebration of the International Day of Light</span></div>
      <div class="logochip small"><img src="data:image/png;base64,{utm_b64}" alt="UTM"></div>
      <div class="logochip small"><img src="data:image/png;base64,{osm_b64}" alt="OSM"></div>
    </div>
  </div>

  <div class="eyebrow">{H.escape(content["hero_title_line1"]).upper()} PHOTONICS MEETING</div>
  <h1>CALL FOR PAPERS</h1>
  <div class="sub">{H.escape(content["cfp_sub"])}</div>

  <div class="pills">
    <div class="pill gold"><span class="dot"></span>8–9 September 2026</div>
    <div class="pill"><span class="dot"></span>MJIIT, UTM Kuala Lumpur, Malaysia</div>
    <div class="pill"><span class="dot"></span>Keynotes · Technical Sessions · Workshops</div>
  </div>

  <div class="about">{H.escape(about_text)}</div>

  <div class="kl-strip">
    <img src="data:image/jpeg;base64,{kl_petronas_b64}" alt="Petronas Twin Towers, Kuala Lumpur">
    <img src="data:image/jpeg;base64,{kl_tower_b64}" alt="KL Tower, Kuala Lumpur">
    <img src="data:image/jpeg;base64,{kl_merdeka_b64}" alt="Merdeka Square, Kuala Lumpur">
  </div>
  <div class="kl-cap">KUALA LUMPUR — YOUR HOST CITY</div>

  <div class="slab"><b>KEYNOTE &amp; INVITED SPEAKERS</b></div>
  <div class="sps">{sp_cards}</div>

  <div class="slab"><b>CONFERENCE TOPICS</b></div>
  <div class="chips">{topic_chips}</div>

  <div style="height:12px"></div>
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
    <div class="pub-t">Accepted papers will be published in the <b>IOP Journal of Physics: Conference Series</b> (ISSN 1742-6596)
      — peer-reviewed &amp; open access, indexed in <span class="gold">Scopus</span> and
      <span class="gold">Web of Science (CPCI)</span>.</div>
    <div class="pub-logos">
      <span class="pub-chip"><img src="data:image/png;base64,{iop_b64}" alt="IOP Publishing" style="height:38px;"></span>
      <span class="pub-chip"><img src="data:image/png;base64,{scopus_b64}" alt="Scopus" style="height:24px;"></span>
      <span class="pub-chip"><img src="data:image/png;base64,{wos_b64}" alt="Web of Science" style="height:17px;"></span>
    </div>
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


outdir = os.path.join(ROOT, "poster")
for name, T in THEMES.items():
    path = os.path.join(outdir, T["out"])
    open(path, "w").write(render(T))
    print(f"written [{name}]: {path} ({os.path.getsize(path)//1024} KB)")
