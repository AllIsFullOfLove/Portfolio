#!/usr/bin/env python3
"""patlau.com — builds the SEO landing pages and per-project pages from index.html.

Run from the repo root:  python3 tools/build_pages.py
  * copies index.html's inline <style> verbatim into /assets/site.css (+ a small sub-page block),
  * generates /matte-painter-toronto/, /concept-artist-toronto/, /vfx-supervisor-toronto/,
    /storyboard-artist-toronto/, /work/ and /work/<project>/ (index.html in each folder),
  * project galleries are copied verbatim from the matching <article> blocks in index.html,
    so captions, credits and image files always match the home page.
index.html itself is never rewritten by this script.
Facts used in the copy come only from what is already on the site (slates + résumé).
"""
import html, json, os, re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://patlau.com'
VERSION = 'v034'          # bump with every publish (keep in step with index.html)
TODAY = '2026-11-25'
PERSON = SITE + '/#pat-lau'
OG = SITE + '/media/og-pat-lau-matte-painter-concept-artist-toronto.jpg'

INDEX = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()

# ---------------------------------------------------------------- shared CSS
style = re.search(r'<style>\n(.*?)</style>', INDEX, re.S).group(1)
SUB_CSS = r"""
/* =================== sub-pages (specialty + /work/ pages) — v034 =================== */
.seal-link{display:block;flex:none;line-height:0;border-radius:4px}
.sub section.page{padding-top:calc(var(--bar-h) + 40px)}
.sub .section-head{margin-bottom:40px}
.sub .section-head h1{font-family:'Cinzel',serif;font-weight:500;font-size:clamp(24px,3.4vw,42px);letter-spacing:.12em;text-transform:uppercase;line-height:1.25}
.sub .section-head .sub{margin-top:10px;font-size:13px;letter-spacing:.24em;text-transform:uppercase;color:var(--seal-text)}
/* no hover zoom anywhere on sub-pages */
.sub .shots a:hover img,.sub .shots .clip:hover img,.sub .shots .clip:hover video{transform:none}
.crumbs{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--dim);margin:0 auto 22px;text-align:center}
.crumbs ol{list-style:none;display:flex;flex-wrap:wrap;justify-content:center;gap:4px 0}
.crumbs li+li::before{content:"/";margin:0 10px;color:var(--seal-text)}
.crumbs a{border-bottom:1px solid transparent}.crumbs a:hover{border-color:var(--seal-bright)}
.prose{max-width:820px;margin:0 auto 64px;font-size:15px;line-height:1.85}
.prose p+p{margin-top:1.1em}
.prose h2{font-family:'Cinzel',serif;font-weight:500;font-size:clamp(17px,2vw,22px);letter-spacing:.12em;text-transform:uppercase;margin:2.2em 0 .8em}
.prose a,.facts a,.plink,.foot-links a{color:var(--paper);border-bottom:1px solid var(--seal-bright)}
.prose a:hover,.facts a:hover,.plink:hover,.foot-links a:hover{color:var(--seal-bright)}
.prose ul{margin:.6em 0 0 1.2em}.prose li+li{margin-top:.35em}
.facts{max-width:820px;margin:0 auto 48px;display:grid;grid-template-columns:200px 1fr;border-top:1px solid var(--line)}
.facts dt,.facts dd{padding:12px 0;border-bottom:1px solid var(--line)}
.facts dt{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--seal-text)}
.facts dd{font-size:15px}
@media(max-width:700px){.facts{grid-template-columns:1fr}.facts dt{border-bottom:0;padding-bottom:0}}
.gallery{display:grid;grid-template-columns:repeat(2,1fr);gap:18px 10px;margin-bottom:72px}
@media(max-width:700px){.gallery{grid-template-columns:1fr}}
.gallery figure{margin:0;min-width:0}
.gallery .shots a{aspect-ratio:16/9}
.gallery .shots img{width:100%;height:100%;object-fit:cover}
.gallery figcaption{margin-top:8px;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--dim)}
.gallery figcaption b{font-weight:400;color:var(--paper)}
.gallery figcaption a{border-bottom:1px solid var(--seal-bright);color:var(--paper)}
.cta{max-width:820px;margin:24px auto 72px;padding:36px 24px;border:1px solid var(--line);text-align:center}
.cta h2{font-family:'Cinzel',serif;font-weight:500;font-size:clamp(18px,2.2vw,24px);letter-spacing:.14em;text-transform:uppercase}
.cta p{margin-top:10px;font-size:14px}
.cta .resume-actions{margin-top:22px}
.linkset{max-width:820px;margin:0 auto 56px}
.linkset h2{font-family:'Cinzel',serif;font-weight:500;font-size:16px;letter-spacing:.16em;text-transform:uppercase;text-align:center;margin-bottom:16px}
.linkset ul{list-style:none;display:flex;flex-wrap:wrap;justify-content:center;gap:8px}
.linkset .btn{height:auto;min-height:40px;padding:8px 14px;white-space:normal;text-align:center;font-size:12px}
.pager{max-width:820px;margin:0 auto 40px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.pager a{flex:1 1 240px;border:1px solid var(--line);padding:14px 16px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;transition:border-color .3s ease}
.pager a:hover{border-color:var(--paper)}
.pager .dir{display:block;color:var(--seal-text);font-size:10px;margin-bottom:4px}
.pager .next{text-align:right}
.workgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:22px 12px;margin-bottom:72px}
@media(max-width:700px){.workgrid{grid-template-columns:1fr}}
.workgrid a.card{display:block;min-width:0}
.workgrid .card img{aspect-ratio:16/9;object-fit:cover;opacity:.92;transition:opacity .4s ease}
.workgrid .card:hover img{opacity:1}
.workgrid .card .t{display:block;margin-top:10px;font-family:'Cinzel',serif;font-size:17px;letter-spacing:.08em;text-transform:uppercase}
.workgrid .card .m{display:block;margin-top:2px;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--dim)}
.foot-links{margin:0 auto 14px;font-size:11px;line-height:2.2}
.foot-links a{margin:0 6px}
@media print{.crumbs,.cta,.linkset,.pager{display:none!important}}
"""
css = ('/* patlau.com shared stylesheet for sub-pages — GENERATED by tools/build_pages.py.\n'
       '   Lines up to the "sub-pages" block are a verbatim copy of the inline <style> in /index.html\n'
       '   (the home page keeps its own inline copy, so it renders exactly as before). Edit index.html, then re-run. */\n'
       + style + SUB_CSS)
open(os.path.join(ROOT, 'assets', 'site.css'), 'w', encoding='utf-8').write(css)

# ---------------------------------------------------------------- helpers
def esc(s): return html.escape(s, quote=True)

def dims(path):
    p = os.path.join(ROOT, path.lstrip('/').split('?')[0].replace('%20', ' '))
    with Image.open(p) as im: return im.size

def sections():
    out = {}
    body = INDEX[INDEX.index('<main'):]
    for sec in re.finditer(r'<section class="page" id="(\w+)".*?</section>', body, re.S):
        out[sec.group(1)] = sec.group(0)
    return out
SECS = sections()

def article(sec, title):
    for a in re.finditer(r'    <article class="project">.*?</article>', SECS[sec], re.S):
        h = re.search(r'<h3>(.*?)</h3>', a.group(0)).group(1)
        if html.unescape(h) == title:
            t = a.group(0)
            t = re.sub(r' · <a class="plink"[^>]*>.*?</a>', '', t)      # strip home-page project links
            return t
    raise KeyError((sec, title))

def meta_of(sec, title):
    a = article(sec, title)
    return html.unescape(re.search(r'<span class="meta">(.*?)</span>', a).group(1))

def full_imgs(sec, title):
    a = article(sec, title)
    hrefs = [h for h in re.findall(r'<a href="([^"]+)"', a) if re.search(r'\.(jpe?g|png)$', h)]
    srcs = re.findall(r'(?<!data-)src="(/[^"]+\.(?:jpe?g|png))(?:\?[^"]*)?"', a)
    seen, out = set(), []
    for u in hrefs + srcs + re.findall(r'data-src="(/[^"]+)"', a):
        if 'icon.jpg' in u or '-1600w' in u or u in seen: continue
        seen.add(u); out.append(u)
    return out

BANNER = '''<header class="banner">
  <div class="banner-inner">
    <a class="seal-link" href="/" aria-label="patlau.com — home"><img width="400" height="400" class="seal-img" src="/logo1.png" alt="patlau.com — Pat Lau"></a>
    <nav class="nav-row" aria-label="Sections">
      <a class="btn" href="/#matte"><span class="lbl-full">Matte Paintings</span><span class="lbl-short">MATTES</span><span class="lbl-land">Matte<br>Paintings</span></a>
      <a class="btn" href="/#vfx"><span class="lbl-full">Visual Effects</span><span class="lbl-short">EFFECTS</span><span class="lbl-land">Visual<br>Effects</span></a>
      <a class="btn" href="/#concept"><span class="lbl-full">Concept Designs</span><span class="lbl-short">Concepts</span><span class="lbl-land">Concept<br>Designs</span></a>
      <a class="btn" href="/#storyboards"><span class="lbl-full">Storyboards</span><span class="lbl-short">Boards</span><span class="lbl-land">Storyboards</span></a>
      <a class="btn" href="/#resume">Résumé</a>
      <a class="btn" href="https://www.linkedin.com/in/pat-lau-6b44574/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
      <a class="btn mail" href="#contact" data-contact="email">E-mail</a>
      <a class="btn tel-btn" href="#contact" data-contact="tel"><span class="lbl-full">Telephone</span><span class="lbl-short">Tel</span><span class="lbl-land">Telephone</span></a>
    </nav>
    <button type="button" class="player" id="player" aria-label="Play background music" aria-pressed="false">
      <canvas id="wave" width="64" height="64"></canvas>
      <audio id="audio" src="/ariella.mp3" loop preload="none"></audio>
    </button>
  </div>
</header>'''

SPECIALTY_LINKS = [
    ('/matte-painter-toronto/', 'Matte Painter · Toronto'),
    ('/concept-artist-toronto/', 'Concept Artist · Toronto'),
    ('/vfx-supervisor-toronto/', 'VFX Supervisor · Toronto'),
    ('/storyboard-artist-toronto/', 'Storyboard Artist · Toronto'),
    ('/work/', 'Selected Work'),
]

def footer():
    links = ' · '.join(f'<a href="{u}">{esc(t)}</a>' for u, t in SPECIALTY_LINKS)
    return f'''<footer id="contact">
  <p class="foot-contact"><a href="#contact" data-contact="email">E-mail</a> · <a href="#contact" data-contact="tel">Telephone</a> · <a href="https://www.linkedin.com/in/pat-lau-6b44574/" target="_blank" rel="noopener noreferrer me">LinkedIn</a> · <a href="https://vimeo.com/patlau" target="_blank" rel="noopener noreferrer me">Vimeo</a> · <a href="/pat-lau-resume.pdf" download>Résumé PDF</a></p>
  <p class="foot-links">{links}</p>
  <noscript><p>E-mail: patlau.com (at) gmail (dot) com</p></noscript>
  <p>Pat Lau · Matte Painter · Concept Artist · VFX Supervisor · Toronto, Ontario, Canada</p>
  <p>All images on this site are copyright Pat Lau or their respective owners.</p>
</footer>

<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Full image view">
  <img id="lb-img" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" alt="">
  <div class="lb-ui" id="lb-ui" hidden>
    <button type="button" class="lb-btn lb-close" id="lb-close" aria-label="Close (Esc)">×</button>
    <button type="button" class="lb-btn lb-prev" id="lb-prev" aria-label="Previous image (←)">‹</button>
    <button type="button" class="lb-btn lb-next" id="lb-next" aria-label="Next image (→)">›</button>
    <div class="lb-bar"><span class="lb-cap" id="lb-cap"></span><span class="lb-count" id="lb-count"></span><button type="button" class="lb-link" id="lb-link">Copy link</button></div>
  </div>
</div>

<script src="/assets/site.js?v={VERSION[1:]}" defer></script>
<div class="site-version" aria-hidden="true">{VERSION}</div>
<!-- build {VERSION} · {TODAY} · generated by tools/build_pages.py -->'''

def page(path, title, desc, og_title, og_desc, og_image, og_alt, jsonld, body):
    url = SITE + path
    return f'''<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="Pat Lau">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="theme-color" content="#0a0a0b">
<meta name="color-scheme" content="dark">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en-ca" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<link rel="icon" href="/favicon.ico">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:site_name" content="The Art of Pat Lau">
<meta property="og:locale" content="en_CA">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(og_title)}">
<meta property="og:description" content="{esc(og_desc)}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:alt" content="{esc(og_alt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(og_title)}">
<meta name="twitter:description" content="{esc(og_desc)}">
<meta name="twitter:image" content="{og_image}">
<meta name="twitter:image:alt" content="{esc(og_alt)}">
<link rel="preload" href="/assets/fonts/cinzel-var-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/ibm-plex-mono-300-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css?v={VERSION[1:]}">
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False, separators=(',', ':'))}</script>
</head>
<body class="sub">
<a href="#main" class="skip-link">Skip to content</a>
{BANNER}

<main id="main">
<section class="page" id="top">
  <div class="wrap">
{body}
  </div>
</section>
</main>

{footer()}
</body>
</html>
'''

def crumbs(items):
    lis = []
    for i, (name, path) in enumerate(items):
        if i == len(items) - 1:
            lis.append(f'<li aria-current="page">{esc(name)}</li>')
        else:
            lis.append(f'<li><a href="{path}">{esc(name)}</a></li>')
    return '    <nav class="crumbs" aria-label="Breadcrumb"><ol>' + ''.join(lis) + '</ol></nav>'

def crumbs_ld(items, path):
    return {'@type': 'BreadcrumbList', '@id': SITE + path + '#breadcrumb',
            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + p}
                                for i, (n, p) in enumerate(items)]}

PERSON_LD = {'@type': 'Person', '@id': PERSON, 'name': 'Pat Lau', 'url': SITE + '/',
             'jobTitle': ['Matte Painter', 'Concept Artist', 'Visual Effects Supervisor', 'Storyboard Artist', 'Compositor', 'Motion Graphic Artist'],
             'address': {'@type': 'PostalAddress', 'addressLocality': 'Toronto', 'addressRegion': 'ON', 'addressCountry': 'CA'},
             'sameAs': ['https://www.linkedin.com/in/pat-lau-6b44574/', 'https://vimeo.com/patlau', 'https://www.deviantart.com/patlau']}

AREA = [{'@type': 'City', 'name': 'Toronto', 'containedInPlace': {'@type': 'AdministrativeArea', 'name': 'Ontario'}},
        {'@type': 'City', 'name': 'Montreal'}, {'@type': 'City', 'name': 'Vancouver'},
        {'@type': 'Country', 'name': 'Canada'}]

CTA = '''    <div class="cta">
      <h2>{h}</h2>
      <p>{p}</p>
      <p class="resume-actions"><a class="btn" href="#contact" data-contact="email">E-mail Pat</a> <a class="btn" href="#contact" data-contact="tel">Telephone</a> <a class="btn" href="/pat-lau-resume.pdf" download>Résumé (PDF)</a></p>
    </div>'''

# ---------------------------------------------------------------- projects
# (slug, display name, [(section, h3 title)], work label, schema type, about-type, extra facts, description paragraphs, related specialty)
PROJECTS = [
  dict(slug='the-creator', name='The Creator', arts=[('matte', 'The Creator')], work='Digital matte painting',
       about='CreativeWork', director='Gareth Edwards', studio='MARZ VFX', spec='/matte-painter-toronto/',
       desc=['A digital matte painting of New Asia City at night for <i>The Creator</i>, directed by Gareth Edwards, painted at MARZ VFX.',
             'Click the panorama to open it at full resolution. The looping clip beneath it is a layer breakdown that shows how the night city is built up. <i>The Creator</i> is also listed among Pat’s MARZ VFX credits on his <a href="/#resume">résumé</a>.']),
  dict(slug='the-walking-dead-dead-city', name='The Walking Dead: Dead City', arts=[('matte', 'The Walking Dead: Dead City')], work='Digital matte painting',
       about='CreativeWork', studio='MARZ VFX', spec='/matte-painter-toronto/',
       desc=['A digital matte painting for <i>The Walking Dead: Dead City</i>, painted at MARZ VFX.',
             'Hover over the image (or drag across it on a phone) to wipe between the original plate and the final matte painting; click to open it at full resolution.']),
  dict(slug='garm-wars-the-last-druid', name='Garm Wars: The Last Druid', arts=[('matte', 'Garm Wars: The Last Druid'), ('concept', 'Garm Wars: The Last Druid')],
       work='Digital matte painting and concept design', about='Movie', director='Mamoru Oshii', studio='Intelligent Creatures', spec='/matte-painter-toronto/',
       desc=['Digital matte paintings and concept designs for the feature film <i>Garm Wars: The Last Druid</i>, directed by Mamoru Oshii, created at Intelligent Creatures.',
             'The first gallery is the matte painting work; the second is the concept design. Click any frame to view it full size and step through the set with the arrow keys.']),
  dict(slug='resident-evil-retribution', name='Resident Evil: Retribution 3D', arts=[('matte', 'Resident Evil: Retribution 3D')], work='Digital matte painting',
       about='Movie', director='Paul W. S. Anderson', studio='Mr. X', spec='/matte-painter-toronto/',
       desc=['Digital matte paintings for <i>Resident Evil: Retribution 3D</i>, directed by Paul W. S. Anderson, created at Mr. X (listed on the résumé as Mr. X Toronto).']),
  dict(slug='orphan-black', name='Orphan Black', arts=[('matte', 'Orphan Black')], work='Digital matte painting',
       about='TVSeries', studio='Intelligent Creatures', spec='/matte-painter-toronto/',
       desc=['Digital matte paintings for the TV series <i>Orphan Black</i>, created at Intelligent Creatures (the résumé lists Orphan Black S03).',
             'Each frame is a before/after pair: hover over it (or drag on a phone) to compare the original plate with the finished painting.']),
  dict(slug='star-wars-uprising', name='Star Wars: Uprising', arts=[('matte', 'Star Wars: Uprising')], work='Digital matte painting',
       about='CreativeWork', studio='Goldtooth Creative', spec='/matte-painter-toronto/',
       desc=['Digital matte paintings for <i>Star Wars: Uprising</i>, created at Goldtooth Creative. Pat’s résumé lists the Star Wars: Uprising Cinematic Trailers 1 &amp; 2 among his Goldtooth Creative credits.']),
  dict(slug='skrillex-the-devils-den', name='Skrillex ft. Wolfgang Gartner — The Devil’s Den', arts=[('vfx', "Skrillex ft. Wolfgang Gartner — The Devil's Den")],
       work='Visual effects — storyboard artist / digital illustrator', about='MusicVideoObject', director='Arev Manoukian', studio='Spy Films', spec='/vfx-supervisor-toronto/',
       role='Storyboard Artist / Digital Illustrator',
       desc=['Visual effects work on the Skrillex ft. Wolfgang Gartner music video <i>The Devil’s Den</i>, directed by Arev Manoukian at Spy Films. Pat’s résumé lists his role as storyboard artist and digital illustrator.',
             'Hover over each of the six stills (or tap on a phone) to switch between the final frame and its “before” version.']),
  dict(slug='erupt-art-of-beat-making', name='ERUPT — Art of Beat-Making', arts=[('vfx', 'ERUPT — Art of Beat-Making')], work='Visual effects',
       about='MusicVideoObject', director='Will Cyr', studio='Secret Level Films', spec='/vfx-supervisor-toronto/',
       desc=['Visual effects for the music video <i>ERUPT — The Art of Beat Making</i>, directed by Will Cyr at Secret Level Films.',
             'Press play to watch the video (it loads from Vimeo only when you click), then browse the 15 frames below at full size.']),
  dict(slug='aeon-flux', name='Æon Flux — City Design', arts=[('concept', 'Æon Flux — City Design')], work='Concept design — internal concept design',
       about='CreativeWork', studio='MARZ', spec='/concept-artist-toronto/',
       desc=['City design concept art for <i>Æon Flux</i>, done as internal concept design at MARZ. Æon Flux is also listed among Pat’s MARZ VFX credits on his résumé.']),
  dict(slug='colossal', name='Colossal', arts=[('concept', 'Colossal — 2016')], work='Concept design',
       about='Movie', director='Nacho Vigalondo', spec='/concept-artist-toronto/',
       desc=['Concept designs for the 2016 feature film <i>Colossal</i>, directed by Nacho Vigalondo.']),
  dict(slug='the-monkey-king', name='The Monkey King', arts=[('concept', 'The Monkey King')], work='Concept design',
       about='Movie', director='Tsui Hark', spec='/concept-artist-toronto/',
       desc=['Concept designs for the feature film <i>The Monkey King</i>, directed by Tsui Hark. Click any image to see it full size.']),
]
SPEC_NAME = {u: t for u, t in SPECIALTY_LINKS}

def project_images(p):
    imgs = []
    for sec, t in p['arts']:
        for u in full_imgs(sec, t):
            if u not in imgs: imgs.append(u)
    return imgs

def project_thumb(p):
    for sec, t in p['arts']:
        a = article(sec, t)
        m = re.search(r'src="(/[^"]+?\.jpg)(?:\?[^"]*)?"', a)
        if m: return m.group(1)

def build_project(i, p):
    path = f"/work/{p['slug']}/"
    meta = meta_of(*p['arts'][0])
    imgs = project_images(p)
    items = [('Home', '/'), ('Work', '/work/'), (p['name'], path)]
    facts = [('Project', esc(p['name'])), ('Work', esc(p['work'])), ('Details (as credited)', esc(meta))]
    if len(p['arts']) > 1:
        facts[-1] = ('Details (as credited)', '<br>'.join(esc(meta_of(*a)) for a in p['arts']))
    if p.get('director'): facts.append(('Director', esc(p['director'])))
    if p.get('studio'): facts.append(('Studio', esc(p['studio'])))
    if p.get('role'): facts.append(('Role', esc(p['role'])))
    facts.append(('Artist', 'Pat Lau · Toronto, Canada · <a href="' + p['spec'] + '">' + esc(SPEC_NAME[p['spec']]) + '</a>'))
    dl = '\n'.join(f'      <dt>{k}</dt><dd>{v}</dd>' for k, v in facts)
    arts = '\n\n'.join(article(*a) for a in p['arts'])
    prev = PROJECTS[i - 1]; nxt = PROJECTS[(i + 1) % len(PROJECTS)]
    desc_txt = re.sub('<[^>]+>', '', html.unescape(p['desc'][0]))
    title = f"{p['name']} — {p['work'].split(' — ')[0]} by Pat Lau | Toronto"
    about = {'@type': p['about'], 'name': p['name'].replace(' — City Design', '')}
    if p.get('director'): about['director'] = {'@type': 'Person', 'name': p['director']}
    art_type = 'CreativeWork' if p['work'].startswith('Visual effects') else 'VisualArtwork'
    work = {'@type': art_type, '@id': SITE + path + '#work', 'name': f"{p['name']} — {p['work'].split(' — ')[0].lower()}",
            'url': SITE + path, 'creator': {'@id': PERSON}, 'description': desc_txt,
            'image': [SITE + u for u in imgs], 'about': about, 'inLanguage': 'en-CA',
            'copyrightNotice': 'All images on this site are copyright Pat Lau or their respective owners.'}
    if art_type == 'VisualArtwork': work['artform'] = p['work'].split(' — ')[0].split(' and ')[0]
    if p.get('studio'): work['sourceOrganization'] = {'@type': 'Organization', 'name': p['studio']}
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebPage', '@id': SITE + path, 'url': SITE + path, 'name': title, 'description': desc_txt,
         'isPartOf': {'@id': SITE + '/#website'}, 'about': {'@id': SITE + path + '#work'}, 'author': {'@id': PERSON},
         'breadcrumb': {'@id': SITE + path + '#breadcrumb'}, 'inLanguage': 'en-CA', 'dateModified': TODAY,
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + imgs[0]}},
        work, PERSON_LD, crumbs_ld(items, path)]}
    body = f'''{crumbs(items)}
    <div class="section-head">
      <h1>{esc(p['name'])}</h1>
      <p class="sub">{esc(p['work'])} · Pat Lau</p>
    </div>
    <div class="prose">
      {''.join('<p>' + d + '</p>' for d in p['desc'])}
    </div>
    <dl class="facts">
{dl}
    </dl>

{arts}

    <nav class="pager" aria-label="More projects">
      <a class="prev" href="/work/{prev['slug']}/"><span class="dir">‹ Previous project</span>{esc(prev['name'])}</a>
      <a class="next" href="/work/{nxt['slug']}/"><span class="dir">Next project ›</span>{esc(nxt['name'])}</a>
    </nav>
    <div class="linkset">
      <h2>More from Pat Lau</h2>
      <ul>{''.join(f'<li><a class="btn" href="{u}">{esc(t)}</a></li>' for u, t in SPECIALTY_LINKS)}<li><a class="btn" href="/">Full portfolio</a></li></ul>
    </div>
''' + CTA.format(h='Work with Pat Lau', p='Matte painting, concept design, VFX supervision and storyboards — based in Toronto, working with productions in Toronto, Montreal and Vancouver.')
    og_img = SITE + imgs[0]
    out = page(path, title, f"{desc_txt} Images and credits on patlau.com.", title.split(' | ')[0], desc_txt, og_img,
               f"{p['name']} — {p['work']} by Pat Lau", ld, body)
    write(path, out)
    return path, imgs

def write(path, text):
    d = os.path.join(ROOT, path.strip('/'))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(text)

# ---------------------------------------------------------------- specialty pages
def figure(u, cap, link=None, alt=None):
    w, h = dims(u)
    small = u.replace('.jpg', '-1600w.jpg')
    src = small if os.path.exists(os.path.join(ROOT, small.lstrip('/'))) else u
    sw, sh = dims(src)
    alt = alt or cap
    c = f'<b>{esc(cap)}</b>' + (f' · <a href="{link}">Project page</a>' if link else '')
    return (f'      <figure><div class="shots"><a href="{u}"><img width="{sw}" height="{sh}" src="{src}" alt="{esc(alt)}" loading="lazy" decoding="async"></a></div>'
            f'<figcaption>{c}</figcaption></figure>')

def W(slug): return f'/work/{slug}/'

SPECIALTIES = [
 dict(path='/matte-painter-toronto/', h1='Matte Painter in Toronto — Pat Lau', short='Matte Painter in Toronto',
      title='Matte Painter in Toronto — Pat Lau | Digital Matte Painting for Film & TV',
      desc='Pat Lau is a Toronto digital matte painter: environments for The Creator, The Walking Dead: Dead City, Garm Wars, Resident Evil: Retribution 3D and Orphan Black. Toronto · Montreal · Vancouver.',
      home_label='All matte paintings', sub='Digital Environments for Film &amp; Television', service='Digital matte painting', home='/#matte',
      og='/matte/tl-1600w.jpg', og_alt='The Creator — New Asia City night matte painting by Pat Lau',
      prose='''<p>Pat Lau is a senior digital matte painter based in Toronto, Ontario. He paints digital environments for feature films, television series, commercials and game cinematics, and works with productions in Toronto, Montreal and Vancouver.</p>
      <h2>Feature film and television</h2>
      <p>His most recent matte painting on this site is the New Asia City night environment for Gareth Edwards’ <a href="/work/the-creator/"><i>The Creator</i></a>, painted at MARZ VFX, along with a matte painting for <a href="/work/the-walking-dead-dead-city/"><i>The Walking Dead: Dead City</i></a>, also at MARZ VFX. Earlier feature work includes <i>Crouching Tiger, Hidden Dragon: Sword of Destiny</i> (dir. Yuen Woo-ping) at Pixomondo, <a href="/work/garm-wars-the-last-druid/"><i>Garm Wars: The Last Druid</i></a> (dir. Mamoru Oshii) at Intelligent Creatures, and <a href="/work/resident-evil-retribution/"><i>Resident Evil: Retribution 3D</i></a> (dir. Paul W. S. Anderson) at Mr. X. For television he painted environments for <a href="/work/orphan-black/"><i>Orphan Black</i></a> at Intelligent Creatures and an abandoned shopping-mall interior for a TV show at Inversion Studio.</p>
      <p>His résumé also lists studio credits at WeFX (<i>John Wick: Chapter 4</i>, <i>The Fall of the House of Usher</i>, <i>Reacher</i> S2), MARZ VFX (<i>Wednesday</i>, <i>Moon Knight</i>, <i>WandaVision</i>, <i>Umbrella Academy 3</i>) and Pixomondo Toronto (<i>Star Trek: Discovery</i>, <i>Wonder Woman</i>, <i>The Fate of the Furious</i>).</p>
      <h2>Short films, commercials and games</h2>
      <p>Short-film matte paintings include <i>Azul</i> (dir. David Karlak), <i>Law Zero</i> (dir. Macgregor) and <i>Nuit Blanche</i> (dir. Arev Manoukian, Stellar Scene), where he was senior digital matte painter. Commercial work includes Hyundai Genesis (Dashing), Nissan Versa Note (The Vanity) and Maple Leaf Canadian Craft (POPBOX VFX). For games he painted environments for <a href="/work/star-wars-uprising/"><i>Star Wars: Uprising</i></a> and <i>Star Wars: Commander</i> at Goldtooth Creative.</p>
      <h2>See the before and after</h2>
      <p>Several paintings on this site come with the original plate. On the Dead City and Orphan Black pages you can wipe between plate and final, and The Creator page has a layer-by-layer breakdown of the painting.</p>
      <h2>Hiring a matte painter in Toronto</h2>
      <p>Pat works from Toronto, Ontario, Canada, with productions in Toronto, Montreal and Vancouver, and can be reached directly by e-mail or phone for studio or freelance matte painting work. A PDF résumé with the full credit list is below.</p>''',
      figs=[('/matte/tl.jpg', 'The Creator · MARZ VFX', W('the-creator')), ('/matte/dc.jpg', 'The Walking Dead: Dead City · MARZ VFX', W('the-walking-dead-dead-city')),
            ('/matte/druid_matte_11.jpg', 'Garm Wars: The Last Druid · Intelligent Creatures', W('garm-wars-the-last-druid')),
            ('/matte/re1.jpg', 'Resident Evil: Retribution 3D · Mr. X', W('resident-evil-retribution')),
            ('/matte/orphan_black_1.1.jpg', 'Orphan Black · Intelligent Creatures', W('orphan-black')),
            ('/matte/sw_hoth.jpg', 'Star Wars: Uprising · Goldtooth Creative', W('star-wars-uprising')),
            ('/matte/ct2-03.jpg', 'Crouching Tiger, Hidden Dragon: Sword of Destiny · Pixomondo', None),
            ('/matte/azul.jpg', 'Azul · Short film, dir. David Karlak', None),
            ('/matte/inversion1.jpg', 'Abandoned Shopping Mall Interior · Inversion Studio', None),
            ('/matte/nuit_blanche.jpg', 'Nuit Blanche · Stellar Scene', None)],
      work=['the-creator', 'the-walking-dead-dead-city', 'garm-wars-the-last-druid', 'resident-evil-retribution', 'orphan-black', 'star-wars-uprising']),
 dict(path='/concept-artist-toronto/', h1='Concept Artist in Toronto — Pat Lau', short='Concept Artist in Toronto',
      title='Concept Artist in Toronto — Pat Lau | Environment, Character & Prop Design',
      desc='Toronto concept artist Pat Lau: environment, character, armour and prop design for Colossal, Downsizing, Garm Wars, Æon Flux, Titans, The Monkey King and Xbox. Toronto · Montreal · Vancouver.',
      home_label='All concept designs', sub='Environments · Characters · Props for Film, TV &amp; Games', service='Concept art and design', home='/#concept',
      og='/concept/shut-in-1600w.jpg', og_alt='Shut In — cyberpunk apartment interior concept by Pat Lau',
      prose='''<p>Pat Lau is a concept artist based in Toronto, Ontario. He designs environments, characters, armour and props for feature films, television, short films and games, and works with productions in Toronto, Montreal and Vancouver.</p>
      <h2>Feature films</h2>
      <p>Feature-film concept work includes <a href="/work/colossal/"><i>Colossal</i></a> (2016, dir. Nacho Vigalondo), the <a href="/work/aeon-flux/"><i>Æon Flux</i> city design</a> (internal concept design at MARZ), <i>Downsizing</i> (2017, Alexander Payne, Paramount) and <a href="/work/garm-wars-the-last-druid/"><i>Garm Wars: The Last Druid</i></a> (dir. Mamoru Oshii, Intelligent Creatures). For Tsui Hark he designed for <a href="/work/the-monkey-king/"><i>The Monkey King</i></a>, and his armour and weapon designs for <i>Seven Swords</i> were shown at the Film Workshop 25th Anniversary Exhibition at agnès b. in Hong Kong.</p>
      <h2>Television and short films</h2>
      <p>For television he has designed for DC’s <i>Titans</i> (Starfire, DC Entertainment), <i>Heroes Reborn</i>, <i>In Contempt</i> and <i>Brain City</i>. Short-film work includes the cyberpunk apartment interior for <i>Shut In</i> (dir. Joseph Procopio, Diamond Box Entertainment), concept design for <i>Concrete City</i> (dir. Arev Manoukian) and character look development for an untitled short film at Intelligent Creatures.</p>
      <h2>Games and interactive</h2>
      <p>Game and interactive work includes <i>Project Scorpion</i> for Xbox, the “Wraith Vision” design of the Nine Nazgûl on fell beasts for <i>Middle-earth: Shadow of Mordor</i> at Goldtooth Creative, and the Horror Cam concept for Google’s Project Tango with Jam3.</p>
      <h2>What the work covers</h2>
      <p>The concept section of the portfolio spans city and environment design (<i>Æon Flux</i>, <i>Colossal</i>, <i>Brain City</i>), interior design (<i>Shut In</i>), character design and character look development, armour and weapon design (<i>Seven Swords</i>), and the Nazgûl “Wraith Vision” design for the game <i>Shadow of Mordor</i>. Most projects show several views or variations, and every image opens full size.</p>
      <h2>Concept art that goes all the way to the shot</h2>
      <p>Pat is also a matte painter, compositor and VFX supervisor, so the same artist can take an idea from concept painting through to a finished environment. See his <a href="/matte-painter-toronto/">matte painting</a> and <a href="/vfx-supervisor-toronto/">visual effects</a> pages.</p>
      <h2>Hiring a concept artist in Toronto</h2>
      <p>Pat works from Toronto, Ontario, Canada, with productions in Toronto, Montreal and Vancouver. Get in touch by e-mail or phone; the full credit list is in the PDF résumé.</p>''',
      figs=[('/concept/shut-in.jpg', 'Shut In · Diamond Box Entertainment', None), ('/concept/ae01.jpg', 'Æon Flux — City Design · MARZ', W('aeon-flux')),
            ('/concept/collosal03.jpg', 'Colossal — 2016 · dir. Nacho Vigalondo', W('colossal')),
            ('/concept/druid_concept_01.jpg', 'Garm Wars: The Last Druid · Intelligent Creatures', W('garm-wars-the-last-druid')),
            ('/concept/underwater.jpg', 'The Monkey King · dir. Tsui Hark', W('the-monkey-king')),
            ('/concept/downsizing.jpg', 'Downsizing — 2017 · Paramount', None),
            ('/concept/titan1.jpg', 'DC Titans — Starfire · DC Entertainment', None),
            ('/concept/nazgul.jpg', 'Middle-earth: Shadow of Mordor · Goldtooth Creative', None),
            ('/concept/xbox1.jpg', 'Project Scorpion · Xbox', None),
            ('/concept/horror.jpg', 'Google Project Tango — Horror Cam · Jam3', None)],
      work=['aeon-flux', 'colossal', 'garm-wars-the-last-druid', 'the-monkey-king']),
 dict(path='/vfx-supervisor-toronto/', h1='VFX Supervisor in Toronto — Pat Lau', short='VFX Supervisor in Toronto',
      title='VFX Supervisor in Toronto — Pat Lau | Visual Effects, Compositing & Matte Painting',
      desc='Toronto VFX supervisor and compositor Pat Lau: VFX supervision at Parktown Productions and Fuel Films / Karbon Arc, plus credits at WeFX, MARZ VFX, Pixomondo and Mr. X Toronto.',
      home_label='All visual effects', sub='Visual Effects · Compositing · Supervision', service='Visual effects supervision and compositing', home='/#vfx',
      og='/vfx/devilsden.jpg', og_alt='The Devil’s Den music video VFX by Pat Lau',
      prose='''<p>Pat Lau is a visual effects supervisor, compositor and matte painter based in Toronto, Ontario. His résumé lists him as VFX supervisor, senior VFX compositor and storyboard artist at Parktown Productions, and as VFX supervisor, senior VFX compositor, storyboard artist and senior matte painter at Fuel Industries / Fuel Films / Karbon Arc.</p>
      <h2>Visual effects on this site</h2>
      <p>The visual effects section of the portfolio includes the Meteor Project VFX breakdown; the Skrillex ft. Wolfgang Gartner music video <a href="/work/skrillex-the-devils-den/"><i>The Devil’s Den</i></a> (dir. Arev Manoukian, Spy Films), where he was storyboard artist and digital illustrator; and the music video <a href="/work/erupt-art-of-beat-making/"><i>ERUPT — The Art of Beat Making</i></a> (dir. Will Cyr, Secret Level Films). The Devil’s Den page lets you switch each still between the final frame and its “before” version.</p>
      <h2>Studio credits</h2>
      <p>His supervision work sits alongside studio credits across the Toronto VFX industry, including:</p>
      <ul>
        <li>WeFX — <i>John Wick: Chapter 4</i>, <i>FUBAR</i>, <i>The Fall of the House of Usher</i>, <i>Painkiller</i>, <i>Cabinet of Curiosities</i>, <i>Reacher</i> S2</li>
        <li>MARZ VFX — <a href="/work/the-creator/"><i>The Creator</i></a>, <i>Wednesday</i>, <i>Moon Knight</i>, <i>WandaVision</i>, <i>Umbrella Academy 3</i>, <i>Y: The Last Man</i></li>
        <li>Pixomondo Toronto — <i>Star Trek: Discovery</i>, <i>Star Trek Beyond</i>, <i>Wonder Woman</i>, <i>The Fate of the Furious</i></li>
        <li>Mavericks VFX — <i>American Gods</i>, <i>The Magicians</i>, <i>11/22/63</i></li>
        <li>Technicolor — <i>ARQ</i>, <i>X Company</i>; Mr. X Toronto — <a href="/work/resident-evil-retribution/"><i>Resident Evil: Retribution 3D</i></a>; Igloo VFX — <i>The Nature of Things with David Suzuki: Save My Lake</i></li>
      </ul>
      <h2>From storyboard to final composite</h2>
      <p>Because Pat also works as a <a href="/storyboard-artist-toronto/">storyboard artist</a>, <a href="/concept-artist-toronto/">concept artist</a> and <a href="/matte-painter-toronto/">matte painter</a>, he can plan a sequence on paper, design and paint its environments, and supervise and composite the shots.</p>
      <h2>Hiring a VFX supervisor in Toronto</h2>
      <p>Pat works from Toronto, Ontario, Canada, with productions in Toronto, Montreal and Vancouver. Reach him directly by e-mail or phone; the PDF résumé has the full credit list.</p>''',
      figs=[('/vfx/devilsden.jpg', 'The Devil’s Den · Spy Films', W('skrillex-the-devils-den')),
            ('/aobm/erupt.jpg', 'ERUPT — Art of Beat-Making · Secret Level Films', W('erupt-art-of-beat-making')),
            ('/vfx/meteor1.jpg', 'Meteor Project · VFX breakdown', None), ('/vfx/meteor2.jpg', 'Meteor Project · VFX breakdown', None),
            ('/vfx/skrillex1a.jpg', 'The Devil’s Den · VFX still', W('skrillex-the-devils-den')),
            ('/aobm/073.jpg', 'ERUPT — Art of Beat-Making · VFX frame', W('erupt-art-of-beat-making'))],
      work=['skrillex-the-devils-den', 'erupt-art-of-beat-making', 'the-creator']),
 dict(path='/storyboard-artist-toronto/', h1='Storyboard Artist in Toronto — Pat Lau', short='Storyboard Artist in Toronto',
      title='Storyboard Artist in Toronto — Pat Lau | Commercials, Music Videos & Film',
      desc='Toronto storyboard artist Pat Lau: boards for Sony 3D Two Worlds, Nokia The Passenger, Twins Effect 2, Skrillex’s The Devil’s Den and more. Toronto · Montreal · Vancouver.',
      home_label='All storyboards', sub='Commercials · Music Videos · Film', service='Storyboard art', home='/#storyboards',
      og='/storyboard/sony1.jpg', og_alt='Sony 3D Two Worlds storyboard by Pat Lau',
      prose='''<p>Pat Lau is a storyboard artist based in Toronto, Ontario, who draws boards for TV commercials, music videos, feature films and branded projects. He works with productions in Toronto, Montreal and Vancouver.</p>
      <h2>Commercials and branded work</h2>
      <p>Storyboards on this site include the <i>Sony 3D — Two Worlds</i> TV commercial (dir. Arev Manoukian), the Nokia commercial <i>The Passenger</i>, and storyboards for TextEd.ca and for Msheireb Properties’ Downtown Doha.</p>
      <h2>Music videos and film</h2>
      <p>Music-video boards include <i>“500”</i>, and on the Skrillex ft. Wolfgang Gartner video <a href="/work/skrillex-the-devils-den/"><i>The Devil’s Den</i></a> at Spy Films he worked as storyboard artist and digital illustrator. Film boards include the feature <i>Twins Effect 2</i> and rough internal boards for an untitled action short.</p>
      <h2>From rough boards to client presentations</h2>
      <p>The storyboards range from quick, rough internal boards used to plan an action sequence to finished frames for commercial clients. The <i>Sony 3D — Two Worlds</i> section of the portfolio shows the boards next to the finished commercial, so you can compare the drawings with the final film.</p>
      <h2>Browse the boards</h2>
      <p>Every storyboard on this site opens full size — click a frame below, or browse the <a href="/#storyboards">storyboard section</a> of the portfolio. Projects shown there: <i>Sony 3D — Two Worlds</i>, <i>Nokia — The Passenger</i>, <i>“500”</i>, <i>Twins Effect 2</i>, an untitled action short, TextEd.ca and Msheireb Properties — Downtown Doha.</p>
      <h2>Boards from someone who also does the VFX</h2>
      <p>Storyboarding has been part of Pat’s work throughout his career: his résumé lists storyboard artist alongside VFX supervisor and senior VFX compositor at Parktown Productions and at Fuel Industries / Fuel Films / Karbon Arc. He is also a <a href="/vfx-supervisor-toronto/">VFX supervisor</a>, <a href="/matte-painter-toronto/">matte painter</a> and <a href="/concept-artist-toronto/">concept artist</a>, so his boards are drawn by someone who knows how the shots will be built.</p>
      <h2>Hiring a storyboard artist in Toronto</h2>
      <p>Pat works from Toronto, Ontario, Canada. Get in touch by e-mail or phone; the PDF résumé has the full credit list.</p>''',
      figs=[('/storyboard/sony1.jpg', 'Sony 3D — Two Worlds · dir. Arev Manoukian', None), ('/storyboard/sony2.jpg', 'Sony 3D — Two Worlds', None),
            ('/storyboard/nokia.jpg', 'Nokia — The Passenger · Commercial', None), ('/storyboard/twins.jpg', 'Twins Effect 2 · Feature film', None),
            ('/storyboard/500.jpg', '“500” · Music video', None), ('/storyboard/msheireb.jpg', 'Msheireb Properties — Downtown Doha', None)],
      work=['skrillex-the-devils-den', 'erupt-art-of-beat-making']),
]

def build_specialty(s):
    path = s['path']
    items = [('Home', '/'), (s['short'], path)]
    figs = '\n'.join(figure(u, c, l) for u, c, l in s['figs'])
    PN = {p['slug']: p['name'] for p in PROJECTS}
    work_links = ''.join(f'<li><a class="btn" href="/work/{w}/">{esc(PN[w])}</a></li>' for w in s['work'])
    others = ''.join(f'<li><a class="btn" href="{u}">{esc(t)}</a></li>' for u, t in SPECIALTY_LINKS if u != path)
    words = len(re.sub('<[^>]+>', ' ', s['prose']).split())
    body = f'''{crumbs(items)}
    <div class="section-head">
      <h1>{esc(s['h1'])}</h1>
      <p class="sub">{s['sub']}</p>
    </div>
    <div class="prose">
      {s['prose']}
    </div>
    <div class="gallery">
{figs}
    </div>
    <div class="linkset">
      <h2>Project pages</h2>
      <ul>{work_links}<li><a class="btn" href="{s['home']}">{esc(s['home_label'])}</a></li></ul>
    </div>
    <div class="linkset">
      <h2>Other specialties</h2>
      <ul>{others}<li><a class="btn" href="/#resume">Résumé</a></li></ul>
    </div>
''' + CTA.format(h=f"Hire Pat Lau — {s['short']}", p='Based in Toronto, Ontario, Canada · working with productions in Toronto, Montreal and Vancouver. E-mail or call directly.')
    url = SITE + path
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebPage', '@id': url, 'url': url, 'name': s['title'], 'description': s['desc'],
         'isPartOf': {'@id': SITE + '/#website'}, 'about': {'@id': PERSON}, 'mainEntity': {'@id': url + '#service'},
         'breadcrumb': {'@id': url + '#breadcrumb'}, 'inLanguage': 'en-CA', 'dateModified': TODAY,
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + s['og']}},
        PERSON_LD,
        {'@type': 'Service', '@id': url + '#service', 'name': f"{s['service']} — Pat Lau, Toronto", 'serviceType': s['service'],
         'provider': {'@id': PERSON}, 'areaServed': AREA, 'url': url, 'description': s['desc'],
         'availableChannel': {'@type': 'ServiceChannel', 'serviceUrl': url}},
        crumbs_ld(items, path)]}
    out = page(path, s['title'], s['desc'], s['h1'], s['desc'], SITE + s['og'], s['og_alt'], ld, body)
    write(path, out)
    return path, [u for u, _, _ in s['figs']], words

# ---------------------------------------------------------------- /work/ index
def build_work_index():
    path = '/work/'
    items = [('Home', '/'), ('Work', path)]
    cards = []
    for p in PROJECTS:
        t = project_thumb(p); w, h = dims(t)
        cards.append(f'''      <a class="card" href="/work/{p['slug']}/"><img width="{w}" height="{h}" src="{t}" alt="{esc(p['name'])} — {esc(p['work'])} by Pat Lau" loading="lazy" decoding="async"><span class="t">{esc(p['name'])}</span><span class="m">{esc(meta_of(*p['arts'][0]))}</span></a>''')
    title = 'Selected Work — Pat Lau | Matte Paintings, Concept Design & VFX, Toronto'
    desc = 'Project pages for Pat Lau’s matte painting, concept design and visual effects work: The Creator, The Walking Dead: Dead City, Garm Wars, Resident Evil: Retribution 3D, Orphan Black and more.'
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'CollectionPage', '@id': SITE + path, 'url': SITE + path, 'name': title, 'description': desc,
         'isPartOf': {'@id': SITE + '/#website'}, 'about': {'@id': PERSON}, 'breadcrumb': {'@id': SITE + path + '#breadcrumb'},
         'inLanguage': 'en-CA', 'dateModified': TODAY,
         'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f"{SITE}/work/{p['slug']}/", 'name': p['name']} for i, p in enumerate(PROJECTS)]}},
        PERSON_LD, crumbs_ld(items, path)]}
    body = f'''{crumbs(items)}
    <div class="section-head">
      <h1>Selected Work</h1>
      <p class="sub">Project pages · Pat Lau · Toronto</p>
    </div>
    <div class="prose"><p>A closer look at individual projects from the portfolio, with the credits exactly as listed on the home page. The complete portfolio — every matte painting, effect, concept and storyboard — is on the <a href="/">home page</a>, and the full credit list is in the <a href="/#resume">résumé</a>.</p></div>
    <div class="workgrid">
{chr(10).join(cards)}
    </div>
    <div class="linkset">
      <h2>Specialties</h2>
      <ul>{''.join(f'<li><a class="btn" href="{u}">{esc(t)}</a></li>' for u, t in SPECIALTY_LINKS[:-1])}</ul>
    </div>
''' + CTA.format(h='Work with Pat Lau', p='Based in Toronto, Ontario, Canada · working with productions in Toronto, Montreal and Vancouver.')
    write(path, page(path, title, desc, 'Selected Work — Pat Lau', desc, OG, 'The Art of Pat Lau', ld, body))
    return path, [project_thumb(p) for p in PROJECTS]

if __name__ == '__main__':
    built = []
    for s in SPECIALTIES:
        p, imgs, words = build_specialty(s); built.append((p, imgs)); print(f'{p}  ({words} words)')
    for i, pr in enumerate(PROJECTS):
        built.append(build_project(i, pr)); print(built[-1][0])
    built.append(build_work_index()); print('/work/')

# ---------------------------------------------------------------- sitemap.xml (sub-page entries are regenerated between markers)
def update_sitemap(built):
    p = os.path.join(ROOT, 'sitemap.xml'); sm = open(p, encoding='utf-8').read()
    sm = re.sub(r'\n  <!-- generated sub-pages: begin -->.*?<!-- generated sub-pages: end -->', '', sm, flags=re.S)
    sm = re.sub(r'(<loc>https://patlau.com/</loc>\s*<lastmod>)[^<]+', r'\g<1>' + TODAY, sm, count=1)
    parts = ['\n  <!-- generated sub-pages: begin -->']
    for path, imgs in built:
        imgx = ''.join(f'\n    <image:image><image:loc>{SITE}{u}</image:loc></image:image>' for u in imgs)
        parts.append(f'  <url>\n    <loc>{SITE}{path}</loc>\n    <lastmod>{TODAY}</lastmod>{imgx}\n  </url>')
    parts.append('  <!-- generated sub-pages: end -->')
    sm = sm.replace('\n</urlset>', '\n'.join(parts) + '\n</urlset>')
    open(p, 'w', encoding='utf-8').write(sm)

if __name__ == '__main__':
    update_sitemap(built)
    print('sitemap.xml updated')
