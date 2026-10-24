#!/usr/bin/env python3
"""Builds one page per project from projects.json into projects/<slug>/index.html.

Usage: python3 build.py
"""
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
CLD = "https://res.cloudinary.com/dsbe46noz/image/upload/"
FONTS = ("https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600"
         "&family=Cormorant+Garamond:ital,wght@0,500;1,400;1,500"
         "&family=Cormorant+SC:wght@500;600;700&family=Jost:wght@400;500;600&display=swap")
ENC = {"name": "Escuela Nacional de Cine", "url": "https://encvenezuela.org/",
       "logo": "v1776641600/enc_lblcuo.png"}


def asset_version():
    h = hashlib.sha1()
    for f in ("assets/project.css", "assets/project.js", "assets/pages.css", "assets/i18n.js", "assets/search.js"):
        h.update((ROOT / f).read_bytes())
    return h.hexdigest()[:8]


VER = asset_version()


def img(path, w):
    if path.startswith("img/"):
        return "@@BASE@@" + path   # stored in this repo; @@BASE@@ becomes the page's path back to the site root
    return f"{CLD}f_auto,q_auto,w_{w}/{path}"


def e(s):
    return html.escape(s or "", quote=True)


WA = "584221990119"  # WhatsApp number, international format without +


def wa(text):
    from urllib.parse import quote
    return f"https://wa.me/{WA}?text={quote(text)}"


def nav(base, current=""):
    items = [("Films", "#films", ""), ("Music Videos", "#work", ""), ("Commercials", "#work", ""),
             ("Services", "services/", "services"), ("About", "about/", "about"), ("Shop", "shop/", "shop")]
    lis = "".join(
        f'<li><a href="{base}{(h if h.endswith("/") else h)}"{" aria-current=\"page\"" if key and key == current else ""}>{n}</a></li>'
        for n, h, key in items)
    return f"""<header class="nav">
  <div class="wrap">
    <a class="logo" href="{base}" aria-label="X Films home"><img src="{CLD}f_auto,q_auto,h_135/logo_long_side_for_web_tpvx8y" alt="X Films"></a>
    <ul>{lis}</ul>
    <a class="book" href="{base}#book">Book us</a>
  </div>
</header>"""


def footer(base):
    return f"""<footer>
  <div class="wrap">
    <div class="fcols">
      <div><h4>Watch</h4><ul><li><a href="{base}#films">Short films</a></li><li><a href="{base}#work">Music videos</a></li><li><a href="{base}#work">Commercials</a></li></ul></div>
      <div><h4>Work with us</h4><ul><li><a href="{base}services/">Services</a></li><li><a href="{base}services/#rental">Equipment rental</a></li><li><a href="{base}#book">Book us</a></li></ul></div>
      <div><h4>X Films</h4><ul><li><a href="{base}about/">About</a></li><li><a href="{base}shop/">Shop · Night Haze</a></li><li><a href="{wa('Hello X Films')}" target="_blank" rel="noopener">WhatsApp</a></li></ul></div>
      <div><h4>Follow</h4><ul><li><a href="https://www.instagram.com/xstudios.films" target="_blank" rel="noopener">Instagram</a></li><li><a href="https://www.youtube.com/@X-STUDIOS-0" target="_blank" rel="noopener">YouTube</a></li><li><a href="https://www.facebook.com/share/1B4C5CS3aY/" target="_blank" rel="noopener">Facebook</a></li></ul></div>
    </div>
    <div class="legal"><span>© 2026 X Films · Made in Venezuela</span><span>+58 422 199 0119</span></div>
  </div>
</footer>"""


def head(title, desc, image, base, extra_css="", extra_fonts=""):
    css = f'<link rel="stylesheet" href="{base}assets/project.css?v={VER}">'
    if extra_css:
        css += f'\n<link rel="stylesheet" href="{base}assets/{extra_css}?v={VER}">'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{image}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
{extra_fonts}{css}
<script src="{base}assets/i18n.js?v={VER}" defer></script>
<script src="{base}assets/search.js?v={VER}" defer></script>
</head>"""


def page(p, nxt):
    t = e(p["title"])
    is_film = p["kind"] == "Short film"
    prod = next((n for r, n in p["credits"] if r.lower().startswith("production company")), "X Films")

    # hero
    line1 = "X Films presents" if is_film else p["kind"]
    if p["director"]:
        line2 = ("A film by " if is_film else "Directed by ") + p["director"]
        if p.get("status"):
            line2 += " · " + p["status"]
    else:
        line2 = ""
    bright = ' class="brighten"' if p.get("hero_brighten") else ""
    yt = ""
    if p["trailer"]:
        src = (f"https://www.youtube-nocookie.com/embed/{p['trailer']}?autoplay=1&amp;mute=1&amp;loop=1"
               f"&amp;playlist={p['trailer']}&amp;controls=0&amp;rel=0&amp;playsinline=1&amp;modestbranding=1"
               f"&amp;iv_load_policy=3&amp;start={p.get('bg_start', 8)}")
        yt = f'<iframe class="yt" id="yt" title="" tabindex="-1" aria-hidden="true" allow="autoplay; encrypted-media" data-src="{src}"></iframe>'
    actions = []
    if p["trailer"]:
        label = "Watch the teaser" if p.get("teaser") else "Watch the trailer" if is_film else "Watch"
        actions.append(f'<button class="play" type="button" data-trailer="{e(p["trailer"])}"><svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 1l9 5-9 5z" fill="currentColor"/></svg>{label}</button>')
    actions.append('<a class="lnk" href="#story">The story</a>')
    title_cls = ' class="cinzel"' if p["slug"] == "nothing-i-havent-dreamt-of" else ""
    es = f'<p class="es">{e(p["title_es"])}</p>' if p["title_es"] else ""

    credits = [(r, n) for r, n in p["credits"] if n and n.upper() != "N/A"]
    def credit(*roles):
        for r, n in credits:
            if r.lower() in roles:
                return n
        return ""

    # facts beside the synopsis
    facts = [("Directed by", p["director"]), ("Written by", credit("screenplay")), ("Status", p.get("status", "")), ("Genre", p["genre"]),
             ("Runtime", p["runtime"]), ("Year", p["year"]), ("Production", prod)]
    facts_html = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in facts if v)

    # poster + partner
    poster = ""
    if p["poster"]:
        poster = (f'<button class="poster" type="button" data-full="{img(p["poster"], 1600)}" data-alt="Poster for {t}">'
                  f'<img src="{img(p["poster"], 800)}" alt="Poster for {t}" loading="lazy"><span>Tap to enlarge</span></button>')
    partner = ""
    if p.get("partner") == "enc":
        partner = (f'<p class="partner"><img src="{img(ENC["logo"], 200)}" alt="" loading="lazy">'
                   f'Made with the <a href="{ENC["url"]}" target="_blank" rel="noopener">{ENC["name"]}</a></p>')

    # lead still: the first still that isn't the hero image, else the first still
    stills = p["stills"][:]
    lead_src = next((x for x in stills if x != p["hero"]), stills[0] if stills else "")
    rest = [x for x in stills if x != lead_src and x != p["hero"]]
    lead = ""
    if lead_src:
        lead = (f'<button class="lead" type="button" data-full="{img(lead_src, 2400)}" data-alt="Still from {t}">'
                f'<img src="{img(lead_src, 2400)}" alt="Still from {t}" loading="lazy"></button>')

    # cast portraits
    cast = ""
    if p["cast"]:
        cards = []
        for c in p["cast"]:
            nm = e(c["name"])
            if c.get("photo"):
                ph = f'<div class="ph"><img src="{img(c["photo"], 600)}" alt="{nm}" loading="lazy"></div>'
            else:
                initials = "".join(w[0] for w in c["name"].split()[:2]).upper()
                ph = f'<div class="ph none" aria-hidden="true"><span>{e(initials)}</span></div>'
            role = f'<span class="as">{e(c["role"])}</span>' if c.get("role") else ''
            cards.append(f'<figure class="person">{ph}<figcaption>{nm}{role}</figcaption></figure>')
        cast = (f'<section class="cast" id="cast" aria-labelledby="cast-h"><div class="wrap">'
                f'<div class="sec-h"><h2 id="cast-h">Cast</h2><p>{len(p["cast"])} {"actor" if len(p["cast"]) == 1 else "actors"}</p></div>'
                f'<div class="people" style="--cols:{min(len(cards), 5) if len(cards) != 6 else 3}">{"".join(cards)}</div></div></section>')

    # credits: key creatives up top, everything in the roll
    key_roles = [("Director", ("director", "performer")), ("Written by", ("screenplay",)),
                 ("Cinematography", ("director of photography", "directors of photography")),
                 ("Music", ("original score", "original music", "music & mix")), ("Edited by", ("edited by",))]
    keys = "".join(f"<div><dt>{k}</dt><dd>{e(credit(*rs))}</dd></div>" for k, rs in key_roles if credit(*rs))
    keys_html = f'<dl class="keys">{keys}</dl>' if keys.count("<div>") >= 2 else ""
    roll = "".join(f"<dt>{e(r)}</dt><dd>{e(n)}</dd>" for r, n in credits)

    gallery = ""
    if rest:
        btns = []
        for n, x in enumerate(rest):
            wide = " wide" if (len(rest) % 2 == 1 and n == 0) else ""
            btns.append(f'<button class="{wide.strip()}" type="button" data-full="{img(x, 2000)}" data-alt="Still from {t}"><img src="{img(x, 1400)}" alt="Still from {t}" loading="lazy"></button>')
        gallery = (f'<section class="gallery" id="stills" aria-labelledby="gal-h"><div class="wrap">'
                   f'<div class="sec-h"><h2 id="gal-h">Stills</h2><p>Tap any frame to view it full screen</p></div>'
                   f'<div class="grid">{"".join(btns)}</div></div></section>')

    game = ""
    g = p.get("game")
    if g:
        game = f"""<section class="game" id="game" aria-labelledby="game-h">
    <div class="wrap">
      <div class="sec-h"><h2 id="game-h">The official game</h2><p>Free · Plays in your browser</p></div>
      <div class="gwrap">
        <div class="screen" id="gscreen" data-url="{e(g['url'])}">
          <img src="{img(p['hero'], 1800)}" alt="" loading="lazy">
          <canvas class="embers" aria-hidden="true"></canvas>
          <div class="card">
            <p class="eyebrow">Based on the short film</p>
            <p class="gtitle">{t}</p>
            <button class="play" type="button" data-game><svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 1l9 5-9 5z" fill="currentColor"/></svg>Play here</button>
            <p class="gnote">Best with headphones</p>
          </div>
          <button class="gexit" type="button" hidden aria-label="Close the game">×</button>
        </div>
        <div class="ginfo">
          <blockquote>{e(g['lead'])}</blockquote>
        </div>
      </div>
    </div>
  </section>"""

    sub_links = ['<a href="#story">Story</a>']
    if game: sub_links.append('<a href="#game">Game</a>')
    if cast: sub_links.append('<a href="#cast">Cast</a>')
    sub_links.append('<a href="#credits">Credits</a>')
    if gallery: sub_links.append('<a href="#stills">Stills</a>')
    if p["trailer"]:
        sub_links.append(f'<button class="watch" type="button" data-trailer="{e(p["trailer"])}">Watch</button>')
    subnav = (f'<div class="subnav"><div class="wrap"><strong>{t}</strong>'
              f'<nav aria-label="On this page">{"".join(sub_links)}</nav></div></div>')

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t} · X Films</title>
<meta name="description" content="{e(p['synopsis'])}">
<meta property="og:title" content="{t} · X Films">
<meta property="og:description" content="{e(p['tagline'])}">
<meta property="og:image" content="{img(p['hero'], 1200)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="../../assets/project.css?v={VER}">
<script src="../../assets/i18n.js?v={VER}" defer></script>
<script src="../../assets/search.js?v={VER}" defer></script>
</head>
<body>
{nav("../../")}
<main>
  <section class="p-hero" aria-labelledby="title">
    <div class="bg"><img{bright} src="{img(p['hero'], 2400)}" alt="" fetchpriority="high"></div>
    {yt}
    <div class="in">
      <p class="credit">{e(line2) if is_film else e(line1) + (' · ' + e(line2) if line2 else '')}</p>
      <h1 id="title"{title_cls}>{t}</h1>
      {es}
      <p class="tag">{e(p['tagline'])}</p>
      <div class="actions">{''.join(actions)}</div>
    </div>
  </section>

  {subnav}

  <section class="story" id="story" aria-label="Synopsis">
    <div class="wrap{'' if poster else ' no-poster'}">
      {poster}
      <div class="text">
        <p class="credit">Synopsis</p>
        <blockquote>{e(p['synopsis'])}</blockquote>
        <dl class="facts">{facts_html}</dl>
        {partner}
      </div>
    </div>
  </section>

  {lead}

  {game}

  {cast}

  <section class="credits" id="credits" aria-labelledby="cred-h">
    <div class="wrap">
      <div class="sec-h"><h2 id="cred-h">Credits</h2></div>
      {keys_html}
      <p class="roll-h">Full credits</p>
      <dl class="roll">{roll}</dl>
    </div>
  </section>

  {gallery}

  <a class="next" href="../{nxt['slug']}/">
    <img src="{img(nxt['hero'], 2000)}" alt="" loading="lazy">
    <div class="wrap">
      <p class="credit">Next · {e(nxt['kind'])}</p>
      <h2>{e(nxt['title'])}</h2>
      <span class="arrow">See the project ›</span>
    </div>
  </a>
</main>
{footer("../../")}

<dialog id="player" aria-label="Trailer"><button class="x" type="button" aria-label="Close">×</button><div class="box"><div class="frame"><iframe title="Trailer for {t}" allow="autoplay; encrypted-media; fullscreen" allowfullscreen src="about:blank"></iframe></div></div></dialog>
<dialog id="viewer" aria-label="Image viewer"><button class="x" type="button" aria-label="Close">×</button><button class="arr l" type="button" aria-label="Previous image">‹</button><button class="arr r" type="button" aria-label="Next image">›</button><div class="box"><img class="shot" src="" alt=""></div></dialog>
<script src="../../assets/project.js?v={VER}"></script>
</body>
</html>
"""


def main():
    data = json.loads((ROOT / "projects.json").read_text(encoding="utf-8"))["projects"]
    for n, p in enumerate(data):
        out = ROOT / "projects" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(p, data[(n + 1) % len(data)]).replace("@@BASE@@", "../../"), encoding="utf-8")
        print("built", out.relative_to(ROOT))


if __name__ == "__main__":
    main()


# ─────────────────────────── About, Services, Shop ───────────────────────────
SITE = "https://xstudiosfilms.com/assets/"   # images that live on the current site


def close_band(base, title="Tell us the story", text="Send the date, the place and what you have in mind. We reply within two days.", wa_text="Hello X Films, I'd like to talk about a project."):
    return f"""<section class="close" aria-labelledby="close-h"><div class="wrap">
    <h2 id="close-h">{title}</h2>
    <p>{text}</p>
    <div class="actions"><a class="play" href="{base}#book">Book us</a><a class="lnk" href="{wa(wa_text)}" target="_blank" rel="noopener">Message us on WhatsApp</a></div>
    <span class="num">WhatsApp · +58 422 199 0119</span>
  </div></section>"""


def about_page(data):
    by = {p["slug"]: p for p in data}
    counts = {"Short film": 0, "Music video": 0, "Commercial": 0}
    for p in data:
        counts[p["kind"]] = counts.get(p["kind"], 0) + 1
    first = min(int(p["year"]) for p in data if p["year"])
    reel = "".join(
        f'<a href="../projects/{s}/"><img src="{img(by[s]["hero"], 900)}" alt="" loading="lazy"><span>{e(by[s]["title"])}</span></a>'
        for s in ("nothing-i-havent-dreamt-of", "in-silence", "big-band-banana"))
    return head("About us · X Films", "X Films is a collective of directors, designers and visual artists from Venezuela crafting atmospheric narratives.",
                img("v1780349969/x_films_eye_lwm5ky.jpg", 1200), "../", "pages.css") + f"""
<body>
{nav("../", "about")}
<main>
  <section class="pg-hero" aria-labelledby="title">
    <div class="bg"><img src="{img('v1780349969/x_films_eye_lwm5ky.jpg', 2400)}" alt="" fetchpriority="high"></div>
    <div class="in">
      <p class="eyebrow">Behind the lens</p>
      <h1 id="title" class="lead amber-text">Cinema should be more than entertainment. It should be an experience.</h1>
    </div>
  </section>

  <section class="band manifesto" aria-labelledby="m-h">
    <div class="wrap">
      <p class="eyebrow">Who we are</p>
      <div>
        <h2 id="m-h">Crafting atmospheric narratives.</h2>
        <p class="body">X Films was founded on the belief that cinema should be more than entertainment; it should be an experience. Our collective of directors, designers and visual artists works together to create worlds that are as visually arresting as they are emotionally resonant.</p>
      </div>
    </div>
  </section>

  <section class="band ink" aria-label="Mission and vision">
    <div class="wrap">
      <div class="mv">
        <article><h3>Mission</h3><p>To redefine the cinematic landscape by crafting deeply atmospheric and immersive narratives that transcend traditional boundaries and resonate with global audiences.</p></article>
        <article><h3>Vision</h3><p>To be a leading creative force in contemporary cinema, recognized for our commitment to artistic integrity, technical excellence and visionary storytelling.</p></article>
      </div>
    </div>
  </section>

  <section class="band" aria-labelledby="w-h">
    <div class="wrap">
      <div class="head2"><h2 id="w-h">The work</h2><p>Short films, music videos and brand films, made in Venezuela with a growing family of collaborators.</p></div>
      <div class="stats">
        <div><b>{counts["Short film"]}</b><span>Short films</span></div>
        <div><b>{counts["Music video"]}</b><span>Music videos</span></div>
        <div><b>{counts["Commercial"]}</b><span>Brand films</span></div>
        <div><b>{first}</b><span>First film</span></div>
      </div>
      <div class="reel">{reel}</div>
    </div>
  </section>

  <section class="band ink" aria-label="Partners">
    <div class="wrap partners">
      <img src="{img(ENC['logo'], 300)}" alt="Escuela Nacional de Cine" loading="lazy">
      <span>Co-productions with the <a href="{ENC['url']}" target="_blank" rel="noopener" style="border-bottom:1px solid var(--hair)">Escuela Nacional de Cine</a></span>
    </div>
  </section>

  {close_band("../")}
</main>
{footer("../")}
</body>
</html>
"""


def services_page(data):
    by = {p["slug"]: p for p in data}
    caps = [
        ("production", "PRD", "Film production", f"{SITE}film_production_1780358201299-DEZY95OT.png",
         "Full-scale production from concept development to principal photography. We bring visionary narratives to life with uncompromising quality and scale.",
         ["Concept development", "Pre-production", "Principal photography"], "Hello X Films, I'd like to talk about producing a film."),
        ("cinematography", "DOP", "Director of photography", f"{SITE}director_of_photography_1780358213266-VsCExifR.png",
         "Cinematography focused on lighting, composition and visual tone, so every frame tells your story with power and elegance.",
         ["Lighting", "Composition", "Visual tone"], "Hello X Films, I'm looking for a director of photography."),
        ("post", "PST", "Post-production", f"{SITE}post_production_1780358228084-BPQDlsOy.png",
         "Editing, color grading, visual effects and sound design to polish and finish your film.",
         ["Editing", "Color grading", "Visual effects", "Sound design"], "Hello X Films, I need help with post-production."),
        ("rental", "RNT", "Equipment rental", f"{SITE}equipment_rental_1787786778409-0HHBs3nM.jpg",
         "High-end cinema cameras, lenses, lighting and grip equipment for your next production.",
         ["Cinema cameras", "Lenses", "Lighting", "Grip"], "Hello, I am interested in renting equipment."),
    ]
    rows = "".join(f"""<article class="cap" id="{i}">
        <div class="pic"><img src="{src}" alt="{e(t)}" loading="lazy"></div>
        <div class="txt">
          <span class="code">{c}</span>
          <h3>{e(t)}</h3>
          <p>{e(d)}</p>
          <ul>{''.join(f'<li>{e(x)}</li>' for x in tags)}</ul>
          <a class="lnk" href="{wa(msg)}" target="_blank" rel="noopener">Ask on WhatsApp</a>
        </div>
      </article>""" for i, c, t, src, d, tags, msg in caps)
    kinds = [
        ("Weddings & events", "Your day or your event, shot like a film.", "big-band-banana", "Event coverage · Big Band Banana"),
        ("Music videos", "Concept, shoot and grade built around the track.", "extasis", "See Extasis"),
        ("Commercials", "Brand films with the craft of narrative cinema.", "runway-night-heroines", "See Runway Night"),
        ("Narrative", "Short films, from the script to the festival.", "the-woman-in-the-other-room", "See The Woman in the Other Room"),
    ]
    tiles = "".join(f"""<a class="kind" href="../projects/{s}/"><img src="{img(by[s]['hero'], 900)}" alt="" loading="lazy">
        <h3>{e(t)}</h3><p>{e(d)}</p><span class="see">{e(see)} ›</span></a>""" for t, d, s, see in kinds)
    return head("Services · X Films", "Film production, cinematography, post-production and equipment rental from X Films.",
                img(by["runway-night-heroines"]["hero"], 1200), "../", "pages.css") + f"""
<body>
{nav("../", "services")}
<main>
  <section class="pg-hero" aria-labelledby="title">
    <div class="bg"><img src="{img(by['runway-night-heroines']['hero'], 2400)}" alt="" fetchpriority="high"></div>
    <div class="in">
      <p class="eyebrow">Services</p>
      <h1 id="title">From idea to final cut</h1>
      <p class="lead amber-text">Everything a production needs, under one roof.</p>
      <div class="actions"><a class="play" href="#capabilities">See what we do</a><a class="lnk" href="{wa("Hello X Films, I'd like a quote.")}" target="_blank" rel="noopener">Get a quote</a></div>
    </div>
  </section>

  <section class="band" id="capabilities" aria-labelledby="cap-h">
    <div class="wrap">
      <div class="head2"><h2 id="cap-h">Capabilities</h2><p>Hire the full team, or just the part of the pipeline you need.</p></div>
      {rows}
    </div>
  </section>

  <section class="band ink" aria-labelledby="k-h">
    <div class="wrap">
      <div class="head2"><h2 id="k-h">What we shoot</h2><p>Locally, across Venezuela and abroad.</p></div>
      <div class="kinds">{tiles}</div>
    </div>
  </section>

  {close_band("../", "Let's make something", "Tell us about the shoot, the date and the place. We reply within two days with a plan and a quote.", "Hello X Films, I'd like a quote for a shoot.")}
</main>
{footer("../")}
</body>
</html>
"""


def shop_page():
    shots = [
        ("isolated_gallon_1787785853795-B8DYDhWc.jpg", "Night Haze one-gallon jug"),
        ("night_haze_left_aligned_1787790906641-I2GfI3we.jpg", "Night Haze professional fluid"),
        ("feat_diffusion_model_1787785636901-CcN-VdXk.jpg", "Haze catching a light beam on set"),
        ("feat_hangtime_1787785453635-ftuAdYIg.jpg", "Haze hanging in a studio"),
        ("feat_formats_1787785464597-Bi-oSpOd.jpg", "Night Haze bottle and jug"),
    ]
    thumbs = "".join(f'<button type="button" aria-pressed="{"true" if n == 0 else "false"}" data-src="{SITE}{f}" aria-label="Show {e(a)}"><img src="{SITE}{f}" alt="" loading="lazy"></button>' for n, (f, a) in enumerate(shots))
    feats = [
        ("feat_diffusion_model_1787785636901-CcN-VdXk.jpg", "Cinematic light diffusion", "A smooth, even haze that catches practical and studio light, lifting beams, shaping shadows and bringing out flares."),
        ("feat_premium_1787785441473-DINZKPTA.jpg", "Premium formulation", "A precise blend of high-quality vegetable glycerin and propylene glycol for a reliable, non-toxic, clean effect."),
        ("feat_hangtime_1787785453635-ftuAdYIg.jpg", "Extended hang time", "Made for the pace of real productions, so you spend less time re-hazing between takes."),
        ("feat_formats_1787785464597-Bi-oSpOd.jpg", "Production-ready formats", "A 1-liter (33.8 fl oz) bottle for nimble location work, or a gallon jug for studio builds."),
        ("feat_clean_1787785474280-BEkXEsVX.jpg", "Odorless and clean", "A neutral scent that keeps cast and crew comfortable through long indoor shooting days."),
    ]
    feat_html = "".join(f'<article class="feat"><div class="pic"><img src="{SITE}{f}" alt="" loading="lazy"></div><div class="t"><h3>{e(t)}</h3><p>{e(d)}</p></div></article>' for f, t, d in feats)
    return head("Night Haze · X Films Shop", "Night Haze: professional cinematic fog fluid from X Films. 1 liter $15, 1 gallon $50.",
                f"{SITE}{shots[0][0]}", "../", "pages.css",
                '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@800&display=swap">\n') + f"""
<body>
{nav("../", "shop")}
<main>
  <section class="product" aria-labelledby="title">
    <div class="wrap">
      <div class="gal">
        <div class="main"><img id="shot" src="{SITE}{shots[0][0]}" alt="{e(shots[0][1])}"></div>
        <div class="thumbs" role="group" aria-label="Product photos">{thumbs}</div>
      </div>
      <div class="buy">
        <p class="eyebrow">X Films Shop · Elevate your atmosphere</p>
        <h1 id="title" class="brand">Night<br>Haze</h1>
        <p class="lead amber-text">Professional cinematic fog fluid.</p>
        <p class="price"><span id="price">$15</span><small>USD</small></p>
        <div class="sizes" role="group" aria-label="Size">
          <button type="button" aria-pressed="true" data-size="1 Liter" data-price="15"><b>1 Liter</b><span>33.8 fl oz · $15</span></button>
          <button type="button" aria-pressed="false" data-size="1 Gallon" data-price="50"><b>1 Gallon</b><span>3.8 L · $50</span></button>
        </div>
        <a class="play order" id="order" href="{wa("Hello, I'm interested in ordering Night Haze (1 Liter) for $15.00.")}" target="_blank" rel="noopener"><svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 1l9 5-9 5z" fill="currentColor"/></svg>Order on WhatsApp</a>
        <p class="note">Orders, payment and delivery are arranged on WhatsApp · +58 422 199 0119</p>
        <dl class="specs">
          <div><dt>Formula</dt><dd>Vegetable glycerin and propylene glycol</dd></div>
          <div><dt>Sizes</dt><dd>1 liter · 1 gallon</dd></div>
          <div><dt>Residue</dt><dd>Clean-burning, kind to lenses and sensors</dd></div>
          <div><dt>Scent</dt><dd>Odorless</dd></div>
        </dl>
      </div>
    </div>
  </section>

  <section class="band ink" aria-labelledby="q-h">
    <div class="wrap copy2">
      <h2 id="q-h">Made for the professional set</h2>
      <div>
        <p>Night Haze delivers the volumetric light and atmospheric depth cinematographers, lighting directors and event producers chase. It gives a consistent, long-lasting mist that turns flat spaces into textured, striking environments.</p>
        <p>The fluid is a clean-burning blend of vegetable glycerin and propylene glycol. It creates a rich atmosphere without leaving heavy residue on cinema lenses, sensors or event equipment, and its dark, minimal packaging looks at home on any set.</p>
      </div>
    </div>
  </section>

  <section class="band" aria-labelledby="f-h">
    <div class="wrap">
      <div class="head2"><h2 id="f-h">The Night Haze advantage</h2><p>The haze we use on our own sets.</p></div>
      <div class="feats">{feat_html}</div>
    </div>
  </section>

  {close_band("../", "Light your next scene", "Need a quantity for a production or a venue? Message us and we'll put an order together.", "Hello, I'd like to order Night Haze for a production.")}
</main>
{footer("../")}
<script>
(() => {{
  const shot = document.getElementById("shot");
  document.querySelectorAll(".thumbs button").forEach(b => b.addEventListener("click", () => {{
    shot.src = b.dataset.src; shot.alt = b.getAttribute("aria-label").replace("Show ", "");
    document.querySelectorAll(".thumbs button").forEach(x => x.setAttribute("aria-pressed", x === b));
  }}));
  const order = document.getElementById("order"), price = document.getElementById("price");
  document.querySelectorAll(".sizes button").forEach(b => b.addEventListener("click", () => {{
    document.querySelectorAll(".sizes button").forEach(x => x.setAttribute("aria-pressed", x === b));
    price.textContent = "$" + b.dataset.price;
    const msg = "Hello, I'm interested in ordering Night Haze (" + b.dataset.size + ") for $" + b.dataset.price + ".00.";
    const en = "https://wa.me/{WA}?text=" + encodeURIComponent(msg);
    order.href = "https://wa.me/{WA}?text=" + encodeURIComponent(window.XF ? XF.t(msg) : msg);
    order.dataset.enHref = en; order.dataset.hrefSet = order.getAttribute("href");
  }}));
}})();
</script>
</body>
</html>
"""


def build_search(data):
    """assets/search.json: every project plus the main pages, for the search in the menu bar."""
    items = []
    for p in data:
        names = [c["name"] for c in p["cast"]]
        crew = sorted({n for r, n in p["credits"] if n and n.upper() != "N/A"})
        items.append({"type": "project", "t": p["title"], "es": p.get("title_es", ""), "k": p["kind"], "g": p["genre"], "y": p["year"],
                      "d": p["director"], "c": " · ".join(names), "x": " · ".join(crew), "u": f"projects/{p['slug']}/", "img": p["hero"],
                      "quick": p["slug"] == "nothing-i-havent-dreamt-of"})
    pages = [
        {"t": "Services", "sub": "Production, cinematography, post-production and rental", "u": "services/", "icon": "✦", "quick": True,
         "x": "Weddings & events · Music videos · Commercials · Narrative · Film production · Director of photography · Post-production · Editing · Color grading · Visual effects · Sound design"},
        {"t": "Equipment rental", "sub": "High-end cinema cameras, lenses, lighting and grip equipment for your next production.", "u": "services/#rental", "icon": "◎",
         "x": "Cinema cameras · Lenses · Lighting · Grip"},
        {"t": "Night Haze", "sub": "Night Haze fog fluid", "u": "shop/", "icon": "≋", "quick": True, "x": "Shop · fog · haze · humo · niebla · fluid · líquido · 1 Liter · 1 Gallon"},
        {"t": "The official game", "sub": "Play in your browser", "u": "projects/nothing-i-havent-dreamt-of/#game", "icon": "▶", "quick": True,
         "x": "game · juego · videojuego · Nothing I Haven't Dreamt Of · Nada que no haya soñado · Hollow · Luna · Damian"},
        {"t": "About", "sub": "Mission, vision and the work", "u": "about/", "icon": "✕", "quick": True, "x": "About us · Mission · Vision · Escuela Nacional de Cine · Who we are"},
        {"t": "Book us", "sub": "Book a shoot or ask for a quote", "u": "#book", "icon": "✉", "quick": True,
         "x": "Contact · quote · cotización · contacto · WhatsApp · Weddings & events · boda · Tell us the story"},
    ]
    for pg in pages:
        pg["type"] = "page"
        items.append(pg)
    (ROOT / "assets" / "search.json").write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    print("built assets/search.json")


def build_pages():
    data = json.loads((ROOT / "projects.json").read_text(encoding="utf-8"))["projects"]
    build_search(data)
    for name, html_ in (("about", about_page(data)), ("services", services_page(data)), ("shop", shop_page())):
        out = ROOT / name / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_.replace("@@BASE@@", "../"), encoding="utf-8")
        print("built", out.relative_to(ROOT))


if __name__ == "__main__":
    build_pages()
