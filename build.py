#!/usr/bin/env python3
"""YdilWoods.com static site generator.

Reads data/releases.json → writes the full site into public/.
Usage: python3 build.py   (run from the site/ directory)
No dependencies beyond the standard library.
"""
import json, os, shutil, html
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "public")
DATA = json.load(open(os.path.join(ROOT, "data", "releases.json")))
SITE = "https://ydilwoods.com"
TODAY = date.today().isoformat()

ART = DATA["artist"]
RELEASES = DATA["releases"]

# ---- status helpers ---------------------------------------------------------
def is_out(r):
    return r["status"] == "released" or (r["status"] == "presave" and r["date"] <= TODAY)

def big_cover(url):
    return url.replace("ab67616d00001e02", "ab67616d0000b273") if url else None

def esc(s): return html.escape(s, quote=True)

GRADS = ["linear-gradient(160deg,#c9d7ff,#3d4fb8 60%,#0c1030)",
         "linear-gradient(160deg,#ffd97a,#c25818 60%,#26103c)",
         "linear-gradient(160deg,#ff7ad9,#7b2ea8 60%,#160b2e)",
         "linear-gradient(160deg,#7af0ff,#2456c9 55%,#0b0f2c)",
         "linear-gradient(160deg,#b49aff,#4a2b9e 60%,#0f0a24)"]
def art_css(r, i=0):
    if r.get("cover"):
        return f"background-image:url('{r['cover']}');background-size:cover;background-position:center"
    return f"background:{GRADS[i % len(GRADS)]}"

# ---- shared shell ------------------------------------------------------------
CSS = """
:root{--bg:#07030f;--ink:#f4f1ff;--muted:#9d93c4;--violet:#8b5cf6;--magenta:#e935c1;--gold:#f5c451}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:'Inter',sans-serif;overflow-x:hidden}
a{color:inherit}
.display{font-family:'Archivo',sans-serif;font-style:italic;font-weight:900;text-transform:uppercase}
.blob{position:fixed;border-radius:50%;filter:blur(110px);opacity:.5;z-index:0;pointer-events:none}
.b1{width:60vw;height:60vw;background:#4c1d95;top:-20vw;left:-15vw}
.b2{width:45vw;height:45vw;background:#9d174d;top:20vh;right:-18vw}
.lasers{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.22;background:
 linear-gradient(115deg,transparent 49.6%,var(--violet) 49.9%,transparent 50.3%),
 linear-gradient(115deg,transparent 64.6%,var(--magenta) 64.9%,transparent 65.3%),
 linear-gradient(115deg,transparent 34.6%,#22d3ee 34.9%,transparent 35.3%)}
header{position:relative;z-index:2;display:flex;justify-content:space-between;align-items:center;padding:22px 5vw}
.logo img{height:56px;mix-blend-mode:screen;filter:drop-shadow(0 0 14px rgba(139,92,246,.8))}
nav a{color:var(--ink);text-decoration:none;margin-left:26px;font-size:13px;font-weight:600;letter-spacing:.2em;text-transform:uppercase}
nav a:hover{color:var(--magenta)}
main{position:relative;z-index:1}
.tag{display:inline-block;background:linear-gradient(90deg,var(--magenta),var(--violet));padding:8px 18px;border-radius:4px;font-size:12px;font-weight:700;letter-spacing:.3em;text-transform:uppercase;margin-bottom:26px;transform:skew(-8deg)}
.btn{display:inline-block;padding:17px 42px;text-decoration:none;font-family:'Archivo';font-style:italic;font-weight:800;font-size:15px;letter-spacing:.14em;text-transform:uppercase;transform:skew(-8deg);transition:.2s;margin:0 14px 14px 0}
.btn span{display:inline-block;transform:skew(8deg)}
.btn-hot{background:linear-gradient(90deg,var(--magenta),var(--violet));color:#fff;box-shadow:0 0 40px rgba(233,53,193,.45)}
.btn-line{border:2px solid rgba(244,241,255,.35);color:var(--ink)}
.btn:hover{transform:skew(-8deg) translateY(-3px)}
section{padding:70px 5vw}
h2.sec{font-family:'Archivo';font-style:italic;font-weight:900;text-transform:uppercase;font-size:clamp(30px,4.5vw,52px);margin-bottom:38px}
h2.sec em{-webkit-text-stroke:1.5px var(--ink);color:transparent;font-style:italic}
.rail{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:22px}
.t{position:relative;border-radius:8px;overflow:hidden;text-decoration:none;color:var(--ink);background:#0d0820}
.t .art{aspect-ratio:1;transition:.3s;background-size:cover}
.t:hover .art{transform:scale(1.06)}
.t .label{position:absolute;left:0;right:0;bottom:0;padding:40px 16px 14px;background:linear-gradient(transparent,rgba(5,3,12,.94));font-family:'Archivo';font-style:italic;font-weight:800;letter-spacing:.05em}
.t .label small{display:block;font-family:'Inter';font-style:normal;font-weight:400;color:var(--muted);font-size:11px;letter-spacing:.2em;margin-top:4px}
.hotbadge{position:absolute;top:12px;left:12px;background:var(--gold);color:#1a1203;font-size:10px;font-weight:800;letter-spacing:.2em;padding:5px 10px;border-radius:3px;transform:skew(-8deg);z-index:2}
.catlist{border-top:1px solid rgba(244,241,255,.1)}
.crow{display:grid;grid-template-columns:70px 1fr auto;gap:20px;align-items:center;padding:14px 0;border-bottom:1px solid rgba(244,241,255,.1);text-decoration:none;transition:.2s}
.crow:hover{background:rgba(139,92,246,.08)}
.crow .thumb{width:70px;aspect-ratio:1;border-radius:4px;background-size:cover}
.crow b{font-family:'Archivo';font-style:italic;font-weight:800;font-size:17px;display:block}
.crow small{color:var(--muted);font-size:12px;letter-spacing:.15em;text-transform:uppercase}
.crow .go{color:var(--gold);font-size:11px;letter-spacing:.25em;text-transform:uppercase}
.band{background:linear-gradient(90deg,rgba(139,92,246,.14),rgba(233,53,193,.10));border-top:1px solid rgba(139,92,246,.3);border-bottom:1px solid rgba(139,92,246,.3)}
.band p{max-width:700px;font-size:20px;line-height:1.65;font-weight:300}
.band b{font-weight:700;color:var(--gold)}
.band-wrap{display:flex;gap:48px;align-items:center;flex-wrap:wrap}
.artist-photo{width:200px;height:200px;border-radius:50%;object-fit:cover;flex-shrink:0;
 box-shadow:0 0 0 3px rgba(139,92,246,.55),0 0 60px rgba(233,53,193,.35)}
.about-grid{display:grid;grid-template-columns:280px 1fr;gap:44px;align-items:start}
@media(max-width:700px){.about-grid{grid-template-columns:1fr}}
.about-photo{width:100%;border-radius:10px;box-shadow:0 20px 60px rgba(0,0,0,.6),0 0 60px rgba(139,92,246,.25)}
footer{position:relative;z-index:1;padding:38px 5vw;display:flex;justify-content:space-between;flex-wrap:wrap;gap:14px;color:var(--muted);font-size:13px}
footer a{color:var(--ink);text-decoration:none;margin-left:20px;font-weight:600;font-size:12px;letter-spacing:.18em;text-transform:uppercase}
footer a:hover{color:var(--magenta)}
.embed{max-width:720px}
/* hero */
.hero{padding:7vh 5vw 9vh;display:grid;grid-template-columns:1.2fr .8fr;gap:6vw;align-items:center}
@media(max-width:820px){.hero{grid-template-columns:1fr}}
.hero h1{font-size:clamp(50px,8.5vw,112px);line-height:.92;background:linear-gradient(100deg,#fff 20%,var(--violet) 55%,var(--magenta) 90%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 30px rgba(139,92,246,.35))}
.hero p{color:var(--muted);margin:28px 0 38px;font-size:18px;max-width:420px}
.cover{aspect-ratio:1;border-radius:10px;position:relative;background-size:cover;background-position:center;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 40px 90px rgba(0,0,0,.7),0 0 90px rgba(233,53,193,.25);display:flex;align-items:center;justify-content:center}
.cover:after{content:"";position:absolute;inset:-14px;border:1px solid rgba(139,92,246,.35);border-radius:14px;transform:rotate(-2deg)}
.cover .ph{letter-spacing:.25em;font-size:12px;text-transform:uppercase;color:rgba(255,255,255,.7)}
/* release page */
.rel{padding:6vh 5vw;display:grid;grid-template-columns:.8fr 1.2fr;gap:6vw;align-items:center;max-width:1200px;margin:0 auto}
@media(max-width:820px){.rel{grid-template-columns:1fr}}
.rel h1{font-size:clamp(42px,6.5vw,84px);line-height:.94;background:linear-gradient(100deg,#fff 20%,var(--violet) 55%,var(--magenta) 90%);-webkit-background-clip:text;background-clip:text;color:transparent}
.rel .date{color:var(--muted);margin:20px 0 32px;font-size:15px;letter-spacing:.12em;text-transform:uppercase}
.note{max-width:640px;margin:0 auto;color:var(--muted);font-size:18px;line-height:1.75;font-weight:300;text-align:center}
/* links page */
.linkstack{max-width:520px;margin:0 auto;padding:5vh 5vw 8vh;position:relative;z-index:1}
.linkstack .avatar{width:96px;height:96px;border-radius:50%;background-size:cover;margin:0 auto 18px;box-shadow:0 0 40px rgba(139,92,246,.5)}
.linkstack h1{font-family:'Archivo';font-style:italic;font-weight:900;text-transform:uppercase;text-align:center;font-size:26px;margin-bottom:6px}
.linkstack .sub{text-align:center;color:var(--muted);font-size:13px;margin-bottom:34px}
.biglink{display:block;text-decoration:none;text-align:center;padding:18px;margin-bottom:14px;border:2px solid rgba(244,241,255,.25);font-family:'Archivo';font-style:italic;font-weight:800;font-size:15px;letter-spacing:.12em;text-transform:uppercase;transform:skew(-8deg);transition:.2s}
.biglink span{display:inline-block;transform:skew(8deg)}
.biglink:hover{transform:skew(-8deg) translateY(-3px);border-color:var(--magenta)}
.biglink.hot{background:linear-gradient(90deg,var(--magenta),var(--violet));border:none;box-shadow:0 0 40px rgba(233,53,193,.4)}
/* about */
.prose{max-width:680px;margin:0 auto;font-size:18px;line-height:1.8;font-weight:300;color:var(--muted)}
.prose b,.prose strong{color:var(--gold)}
.prose p+p{margin-top:22px}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,400;0,600;1,800;1,900'
         '&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">')

def shell(title, desc, body, canonical, og_image=None, depth=0, jsonld=None):
    pre = "../" * depth
    og = og_image or f"{SITE}/assets/og-default.png"
    ld = f'<script type="application/ld+json">{json.dumps(jsonld)}</script>' if jsonld else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{og}"><meta property="og:type" content="website"><meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{pre}assets/yw-logo.png">
{FONTS}
<link rel="stylesheet" href="{pre}style.css">
{ld}
</head>
<body>
<div class="blob b1"></div><div class="blob b2"></div><div class="lasers"></div>
<header>
  <a class="logo" href="{pre}"><img src="{pre}assets/yw-logo.png" alt="Ydil Woods"></a>
  <nav><a href="{pre}#music">Music</a><a href="{pre}about/">About</a><a href="{pre}links/">Links</a></nav>
</header>
<main>
{body}
</main>
<footer>
  <div>© {TODAY[:4]} Ydil Woods · @ydilwoods</div>
  <div><a href="{ART['spotify']}">Spotify</a><a href="{ART['soundcloud']}">SoundCloud</a><a href="{ART['instagram']}">Instagram</a><a href="{ART['youtube']}">YouTube</a></div>
</footer>
</body>
</html>"""

# ---- pieces ------------------------------------------------------------------
def badge(r):
    if r["status"] == "presave" and not is_out(r):
        return '<div class="hotbadge">PRE-SAVE</div>'
    if r["status"] == "announced":
        mon = date.fromisoformat(r["date"]).strftime("%b %Y").upper() if len(r["date"]) == 10 else "SOON"
        return f'<div class="hotbadge">{mon}</div>'
    return ""

def card(r, i):
    sub = r["date"][:4] + " · " + ("COMING SOON" if r["status"] == "announced" else "SINGLE")
    return (f'<a class="t" href="/{r["slug"]}/"><div class="art" style="{art_css(r,i)}"></div>{badge(r)}'
            f'<div class="label">{esc(r["title"])}<small>{sub}</small></div></a>')

def cat_row(r, i):
    action = "Soon" if r["status"] == "announced" else ("Pre-save" if not is_out(r) else "Listen →")
    artist = esc(r["artist"]) if r["artist"] != "Ydil Woods" else ""
    return (f'<a class="crow" href="/{r["slug"]}/"><div class="thumb" style="{art_css(r,i)}"></div>'
            f'<div><b>{esc(r["title"])}</b><small>{r["date"][:4]}{(" · " + artist) if artist else ""}</small></div>'
            f'<span class="go">{action}</span></a>')

def stream_buttons(r, hero=False):
    out = []
    L = r.get("links", {})
    if not is_out(r) and r["status"] == "presave":
        href = L.get("presave") or ART["spotify"]
        label = "Pre-save now" if L.get("presave") else "Follow on Spotify"
        out.append(f'<a class="btn btn-hot" href="{href}"><span>{label}</span></a>')
    elif r["status"] == "announced":
        out.append(f'<a class="btn btn-hot" href="{ART["spotify"]}"><span>Follow for release</span></a>')
    else:
        out.append(f'<a class="btn btn-hot" href="{L.get("spotify") or ART["spotify"]}"><span>Play on Spotify</span></a>')
        if L.get("apple"): out.append(f'<a class="btn btn-line" href="{L["apple"]}"><span>Apple Music</span></a>')
        if L.get("youtube"): out.append(f'<a class="btn btn-line" href="{L["youtube"]}"><span>YouTube</span></a>')
    if hero:
        out.append('<a class="btn btn-line" href="#music"><span>All music</span></a>')
    return "".join(out)

# ---- pages -------------------------------------------------------------------
def build_home():
    hero_r = next((r for r in RELEASES if r["status"] in ("presave", "announced") and r["date"] >= TODAY), RELEASES[0])
    out_now = is_out(hero_r)
    tagline = f'New single · {date.fromisoformat(hero_r["date"]).strftime("%B %d").replace(" 0"," ")}' if not out_now else "Out now"
    cover_inner = "" if hero_r.get("cover") else '<span class="ph">cover reveal soon</span>'
    hero = f"""
<div class="hero">
  <div>
    <div class="tag">{tagline}</div>
    <h1 class="display">{esc(hero_r["title"])}</h1>
    <p>Euphoric uplifting trance. Built for the drop, made to remember.</p>
    {stream_buttons(hero_r, hero=True)}
  </div>
  <a class="cover" href="/{hero_r["slug"]}/" style="{art_css(hero_r)}">{cover_inner}</a>
</div>"""
    embed = ""
    if DATA.get("embed_latest"):
        embed = f"""
<section><h2 class="sec">Latest <em>release</em></h2>
<div class="embed"><iframe style="border-radius:12px" src="{DATA["embed_latest"]}" width="100%" height="152"
 frameborder="0" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe></div>
</section>"""
    featured = [r for r in RELEASES if r.get("featured")]
    rest = [r for r in RELEASES if not r.get("featured")]
    music = f"""
<section id="music"><h2 class="sec">The <em>music</em></h2>
<div class="rail">{''.join(card(r,i) for i,r in enumerate(featured))}</div>
<h2 class="sec" style="margin-top:70px">Full <em>catalogue</em></h2>
<div class="catlist">{''.join(cat_row(r,i) for i,r in enumerate(rest))}</div>
</section>"""
    about = f"""
<section class="band"><div class="band-wrap">
<img class="artist-photo" src="{ART.get('image','')}" alt="Ydil Woods" loading="lazy">
<div><h2 class="sec">Melody <em>first</em></h2>
<p>I'm Ydil Woods. I make uplifting trance built around one thing: <b>melody</b>.
Euphoric, emotional, straight to the point — music for the moment the lights hit the crowd.
For fans of Ben Gold and Ralphie B. <a href="/about/" style="color:var(--gold)">More about me →</a></p>
</div></div></section>"""
    ld = {"@context": "https://schema.org", "@type": "MusicGroup", "name": "Ydil Woods",
          "genre": "Uplifting Trance", "url": SITE,
          "sameAs": [ART["spotify"], ART["instagram"], ART["youtube"]]}
    desc = "Official website of Ydil Woods. Euphoric, melody-first uplifting trance."
    write("index.html", shell("Ydil Woods — Uplifting Trance", desc, hero + embed + music + about, SITE + "/",
                              og_image=big_cover(hero_r.get("cover")), jsonld=ld))

def build_release(r, i):
    out_now = is_out(r)
    when = date.fromisoformat(r["date"]).strftime("%B %d, %Y") if len(r["date"]) == 10 else r["date"]
    status_line = f"Out {when}" if not out_now else f"Released {when}"
    cover_inner = "" if r.get("cover") else '<span class="ph">cover reveal soon</span>'
    note = f'<section><p class="note">{esc(r["note"])}</p></section>' if r.get("note") else ""
    others = [x for x in RELEASES if x["slug"] != r["slug"] and x.get("featured")][:3]
    more = (f'<section><h2 class="sec">More <em>music</em></h2><div class="rail">'
            f'{"".join(card(x,j) for j,x in enumerate(others))}</div></section>')
    body = f"""
<div class="rel">
  <div class="cover" style="{art_css(r,i)}">{cover_inner}</div>
  <div>
    <div class="tag">{esc(r["artist"])}</div>
    <h1 class="display">{esc(r["title"])}</h1>
    <div class="date">{status_line}</div>
    {stream_buttons(r)}
  </div>
</div>
{note}
{more}"""
    ld = {"@context": "https://schema.org", "@type": "MusicRecording", "name": r["title"],
          "byArtist": {"@type": "MusicGroup", "name": "Ydil Woods"},
          "datePublished": r["date"], "url": f"{SITE}/{r['slug']}/"}
    desc = f"{r['title']} — {r['artist']}. {'Out now.' if out_now else 'Coming ' + when + '.'} Uplifting trance."
    write(f"{r['slug']}/index.html",
          shell(f"{r['title']} — Ydil Woods", desc, body, f"{SITE}/{r['slug']}/",
                og_image=big_cover(r.get("cover")), depth=1, jsonld=ld))

def build_links():
    current = next((r for r in RELEASES if r["status"] == "presave"), RELEASES[0])
    cur_href = current.get("links", {}).get("presave") or f"/{current['slug']}/"
    cur_label = ("Pre-save" if not is_out(current) else "Stream") + f": {current['title']}"
    body = f"""
<div class="linkstack">
  <div class="avatar" style="background-image:url('{ART.get("image","")}')"></div>
  <h1>Ydil Woods</h1>
  <div class="sub">Uplifting trance · melody first</div>
  <a class="biglink hot" href="{cur_href}"><span>{esc(cur_label)}</span></a>
  <a class="biglink" href="{ART['spotify']}"><span>Listen on Spotify</span></a>
  <a class="biglink" href="{ART['youtube']}"><span>YouTube</span></a>
  <a class="biglink" href="{ART['soundcloud']}"><span>SoundCloud</span></a>
  <a class="biglink" href="/#music"><span>All music</span></a>
  <a class="biglink" href="{ART['instagram']}"><span>Instagram @ydilwoods</span></a>
</div>"""
    write("links/index.html", shell("Links — Ydil Woods", "All Ydil Woods links in one place.",
                                    body, SITE + "/links/", depth=1))

def build_about():
    body = f"""
<section><h2 class="sec">About <em>Ydil Woods</em></h2>
<div class="about-grid">
<img class="about-photo" src="{ART.get('image','')}" alt="Ydil Woods" loading="lazy">
<div class="prose" style="margin:0">
<p><strong>Uplifting trance, melody first.</strong></p>
<p>I write euphoric, emotional trance built around simple, memorable melodies —
the kind you're still humming two days later. No overcrowded breaks, no filler:
every layer is there to lift the emotion.</p>
<p>My tracks live where the energy peaks: festival mainstages, sunrise sets and
late-night drives. Recent releases include <b>Chasing Starlight</b>, <b>Pure Energy</b>
and <b>Infinite Embrace</b>, with new music on the way every few weeks.</p>
<p>For fans of Ben Gold, Ralphie B and classic uplifting energy.</p>
<p><strong>DJs &amp; labels:</strong> supporting my music in your set or show?
Reach out for WAVs and extended mixes — contact via Instagram
<a href="https://instagram.com/ydilwoods" style="color:var(--gold)">@ydilwoods</a>.</p>
</div></div></section>"""
    write("about/index.html", shell("About — Ydil Woods", "About Ydil Woods: euphoric, melody-first uplifting trance.",
                                    body, SITE + "/about/", depth=1))

def build_meta():
    urls = [f"{SITE}/", f"{SITE}/links/", f"{SITE}/about/"] + [f"{SITE}/{r['slug']}/" for r in RELEASES]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    write("sitemap.xml", sm)
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    write("404.html", shell("Not found — Ydil Woods", "Page not found.",
        '<section style="text-align:center;padding:16vh 5vw"><h1 class="display" style="font-size:64px">Lost in the <em>drop</em></h1>'
        '<p style="color:var(--muted);margin:20px 0 34px">This page doesn\'t exist.</p>'
        '<a class="btn btn-hot" href="/"><span>Back home</span></a></section>', SITE + "/404.html"))

def write(rel, content):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    if os.path.isdir(OUT):
        try:
            shutil.rmtree(OUT)
        except PermissionError:
            pass  # omgeving zonder delete-rechten: bestanden worden overschreven
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    write("style.css", CSS)
    src_logo = os.path.join(ROOT, "assets", "yw-logo.png")
    if os.path.exists(src_logo):
        shutil.copy(src_logo, os.path.join(OUT, "assets", "yw-logo.png"))
    build_home()
    for i, r in enumerate(RELEASES):
        build_release(r, i)
    build_links()
    build_about()
    build_meta()
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print(f"Built {n} files into public/ ({len(RELEASES)} release pages)")

if __name__ == "__main__":
    main()
