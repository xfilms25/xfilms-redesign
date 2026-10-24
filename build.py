#!/usr/bin/env python3
"""Builds one page per project from projects.json into projects/<slug>/index.html.

Usage: python3 build.py
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
CLD = "https://res.cloudinary.com/dsbe46noz/image/upload/"
FONTS = ("https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600"
         "&family=Cormorant+Garamond:ital,wght@0,500;1,400;1,500"
         "&family=Cormorant+SC:wght@500;600;700&family=Inter+Tight:wght@400;500;600&display=swap")
ENC = {"name": "Escuela Nacional de Cine", "url": "https://encvenezuela.org/",
       "logo": "v1776641600/enc_lblcuo.png"}


def img(path, w):
    return f"{CLD}f_auto,q_auto,w_{w}/{path}"


def e(s):
    return html.escape(s or "", quote=True)


NAV = """<header class="nav">
  <div class="wrap">
    <a class="logo" href="../../" aria-label="X Films home"><img src="{logo}" alt="X Films"></a>
    <ul>
      <li><a href="../../#films">Films</a></li>
      <li><a href="../../#work">Music Videos</a></li>
      <li><a href="../../#work">Commercials</a></li>
      <li><a href="../../#services">Services</a></li>
    </ul>
    <a class="book" href="../../#book">Book a shoot</a>
  </div>
</header>""".format(logo=f"{CLD}f_auto,q_auto,h_90/logo_long_side_for_web_tpvx8y")

FOOTER = """<footer>
  <div class="wrap">
    <div class="fcols">
      <div><h4>Watch</h4><ul><li><a href="../../#films">Short films</a></li><li><a href="../../#work">Music videos</a></li><li><a href="../../#work">Commercials</a></li></ul></div>
      <div><h4>Work with us</h4><ul><li><a href="../../#services">Weddings &amp; events</a></li><li><a href="../../#services">Services</a></li><li><a href="../../#book">Book a shoot</a></li></ul></div>
      <div><h4>X Films</h4><ul><li><a href="https://xstudiosfilms.com/about">About</a></li><li><a href="https://xstudiosfilms.com/contact">Contact</a></li></ul></div>
      <div><h4>Follow</h4><ul><li><a href="https://www.instagram.com/xstudios.films" target="_blank" rel="noopener">Instagram</a></li><li><a href="https://www.youtube.com/@X-STUDIOS-0" target="_blank" rel="noopener">YouTube</a></li><li><a href="https://www.facebook.com/share/1B4C5CS3aY/" target="_blank" rel="noopener">Facebook</a></li></ul></div>
    </div>
    <div class="legal"><span>© 2026 X Films · Made in Venezuela</span><span>All images are stills from the productions.</span></div>
  </div>
</footer>"""


def page(p, nxt):
    t = e(p["title"])
    is_film = p["kind"] == "Short film"
    prod = next((n for r, n in p["credits"] if r.lower().startswith("production company")), "X Films")

    # hero
    line1 = "X Films presents" if is_film else p["kind"]
    if p["director"]:
        line2 = ("A film by " if is_film else "Directed by ") + p["director"]
    else:
        line2 = ""
    bright = ' class="brighten"' if p.get("hero_brighten") else ""
    yt = ""
    if p["trailer"]:
        src = (f"https://www.youtube-nocookie.com/embed/{p['trailer']}?autoplay=1&amp;mute=1&amp;loop=1"
               f"&amp;playlist={p['trailer']}&amp;controls=0&amp;rel=0&amp;playsinline=1&amp;modestbranding=1"
               f"&amp;iv_load_policy=3&amp;start=8")
        yt = f'<iframe class="yt" id="yt" title="" tabindex="-1" aria-hidden="true" allow="autoplay; encrypted-media" data-src="{src}"></iframe>'
    actions = []
    if p["trailer"]:
        label = "Watch the trailer" if is_film else "Watch"
        actions.append(f'<button class="play" type="button" data-trailer="{e(p["trailer"])}"><svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 1l9 5-9 5z" fill="currentColor"/></svg>{label}</button>')
    actions.append('<a class="lnk" href="#story">The story</a>')
    title_cls = ' class="cinzel"' if p["slug"] == "nothing-i-havent-dreamt-of" else ""
    es = f'<p class="es">{e(p["title_es"])}</p>' if p["title_es"] else ""

    # facts
    facts = [("Directed by", p["director"]), ("Genre", p["genre"]), ("Runtime", p["runtime"]),
             ("Year", p["year"]), ("Production", prod)]
    facts_html = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in facts if v)

    # story
    poster = ""
    if p["poster"]:
        poster = (f'<button class="poster" type="button" data-full="{img(p["poster"], 1600)}" data-alt="Poster for {t}">'
                  f'<img src="{img(p["poster"], 800)}" alt="Poster for {t}" loading="lazy"><span>Tap to enlarge</span></button>')
    partner = ""
    if p.get("partner") == "enc":
        partner = (f'<p class="partner"><img src="{img(ENC["logo"], 200)}" alt="" loading="lazy">'
                   f'Made with the <a href="{ENC["url"]}" target="_blank" rel="noopener">{ENC["name"]}</a></p>')

    roll = "".join(f"<dt>{e(r)}</dt><dd>{e(n)}</dd>" for r, n in p["credits"] if n and n.upper() != "N/A")
    cast = ""
    if p["cast"]:
        cast = ('<section class="cast" aria-labelledby="cast-h"><div class="wrap"><h2 id="cast-h">Cast</h2><ul>'
                + "".join(f"<li>{e(c)}</li>" for c in p["cast"]) + "</ul></div></section>")
    gallery = ""
    if p["stills"]:
        gallery = ('<section class="gallery" aria-labelledby="gal-h"><div class="wrap"><h2 id="gal-h">Stills</h2><div class="grid">'
                   + "".join(f'<button type="button" data-full="{img(s, 2000)}" data-alt="Still from {t}"><img src="{img(s, 900)}" alt="Still from {t}" loading="lazy"></button>' for s in p["stills"])
                   + "</div></div></section>")

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
<link rel="stylesheet" href="../../assets/project.css">
</head>
<body>
{NAV}
<main>
  <section class="p-hero" aria-labelledby="title">
    <div class="bg"><img{bright} src="{img(p['hero'], 2400)}" alt="" fetchpriority="high"></div>
    {yt}
    <div class="in">
      <p class="credit">{e(line1)}{' · ' + e(line2) if line2 else ''}</p>
      <h1 id="title"{title_cls}>{t}</h1>
      {es}
      <p class="tag">{e(p['tagline'])}</p>
      <div class="actions">{''.join(actions)}</div>
    </div>
  </section>

  <section class="facts" aria-label="Details"><dl class="wrap">{facts_html}</dl></section>

  <section class="story" id="story" aria-label="Synopsis">
    <div class="wrap{'' if poster else ' no-poster'}">
      {poster}
      <div class="text">
        <p class="credit">Synopsis</p>
        <blockquote>{e(p['synopsis'])}</blockquote>
        {partner}
      </div>
    </div>
  </section>

  {cast}

  <section class="credits" aria-labelledby="cred-h">
    <div class="wrap"><h2 id="cred-h">Credits</h2><dl class="roll">{roll}</dl></div>
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
{FOOTER}

<dialog id="player" aria-label="Trailer"><button class="x" type="button" aria-label="Close">×</button><div class="box"><div class="frame"><iframe title="Trailer for {t}" allow="autoplay; encrypted-media; fullscreen" allowfullscreen src="about:blank"></iframe></div></div></dialog>
<dialog id="viewer" aria-label="Image viewer"><button class="x" type="button" aria-label="Close">×</button><button class="arr l" type="button" aria-label="Previous image">‹</button><button class="arr r" type="button" aria-label="Next image">›</button><div class="box"><img class="shot" src="" alt=""></div></dialog>
<script src="../../assets/project.js"></script>
</body>
</html>
"""


def main():
    data = json.loads((ROOT / "projects.json").read_text(encoding="utf-8"))["projects"]
    for n, p in enumerate(data):
        out = ROOT / "projects" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(p, data[(n + 1) % len(data)]), encoding="utf-8")
        print("built", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
