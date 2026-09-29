#!/usr/bin/env python3
"""Build /guides/ (and /<lang>/guides/) — v2: one card per published article.
Replaces build-art/build_guides.py. Header/footer still come from article 1's template."""
import json, os, re
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE)
B = _HERE
PUB = os.path.join(_ROOT, 'public')
BASE = 'https://colmartour.com'
ORDER = ['en', 'fr', 'de', 'es', 'it', 'pt', 'pl', 'ru']
LOC = {'en': 'en_US', 'fr': 'fr_FR', 'de': 'de_DE', 'es': 'es_ES', 'it': 'it_IT', 'pt': 'pt_PT', 'pl': 'pl_PL', 'ru': 'ru_RU'}
# (slug, build dir, h1 key, subtitle key, alt key, card image, w, h) — newest first
ARTICLES = [
 ('colmar-vs-strasbourg-christmas', os.path.join(_ROOT, 'build-art-colmar-vs-strasbourg-christmas'),
  'ctx:h1', 'ctx:sub', 'ctx:alt', '/img/tile-little-venice.webp', 800, 600),
 ('colmar-christmas-market', B, 'T200', 'T201', 'T208', '/img/tile-christmas-market-600.webp', 600, 450),
]
css = open(f'{B}/site.css', encoding='utf-8').read()
art_tpl = open(f'{B}/template-art.html', encoding='utf-8').read()
hdr_raw = re.search(r'<header class="hdr">.*?</header>', art_tpl, re.S).group(0)
ftr_raw = re.search(r'<footer>.*?</footer>', art_tpl, re.S).group(0)
def strip_arrow(s): return re.sub(r'\s*(&rarr;|→)\s*$', '', s).strip()
def langnav(cur):
    return '<nav class="lang">' + ''.join(
        f'<a{" class=\"on\"" if l == cur else ""} href="{"/guides/" if l == "en" else f"/{l}/guides/"}">{l.upper()}</a>' for l in ORDER) + '</nav>'
KEEPRE = re.compile(r'^/(img/|favicon|robots|sitemap|llms|en|fr|de|es|it|pt|pl|ru)(/|\.|$)')
def prefix_links(html, lang):
    if lang == 'en': return html
    def rep(m):
        q, path = m.group(1), m.group(2)
        if KEEPRE.match(path): return m.group(0)
        return f'href={q}/{lang}/{q}' if path == '/' else f'href={q}/{lang}{path}{q}'
    return re.sub(r'href=(["\'])(/[^"\']*)\1', rep, html)
def load(d, lang):
    x = json.load(open(f'{d}/content/{lang}.json', encoding='utf-8'))
    return {k: (v['en'] if isinstance(v, dict) else v) for k, v in x.items()}
CTX = {'ctx:h1': 'div.arthero > div.wrap > h1', 'ctx:sub': 'div.arthero > div.wrap > p.sub', 'ctx:alt': 'img alt'}
def resolve(bdir, key):
    # article 2 keys are looked up by position in the page, not by number (numbers change on re-extract)
    if not key.startswith('ctx:'): return key
    en = json.load(open(f'{bdir}/content/en.json', encoding='utf-8'))
    return next(k for k, v in en.items() if v['ctx'].startswith(CTX[key]))
def fill(tpl, data):
    for k, v in data.items(): tpl = tpl.replace('{{%s}}' % k, v)
    return tpl
for lang in ORDER:
    d = load(B, lang)
    pre = '' if lang == 'en' else f'/{lang}'
    url = f'{BASE}{pre}/guides/'
    heading = strip_arrow(d['T004'])
    hdr = prefix_links(fill(hdr_raw, d), lang).replace('{{LANGNAV}}', langnav(lang))
    ftr = prefix_links(fill(ftr_raw, d), lang)
    cards, items = [], []
    for i, (slug, bdir, kh, ks, ka, img, w, h) in enumerate(ARTICLES, 1):
        a = load(bdir, lang)
        kh, ks, ka = resolve(bdir, kh), resolve(bdir, ks), resolve(bdir, ka)
        cards.append(f'''  <div class="card">
   <img src="{img}" width="{w}" height="{h}" loading="lazy" alt="{a[ka]}">
   <div class="pad">
    <h3><a href="{pre}/{slug}/">{a[kh]}</a></h3>
    <p>{a[ks]}</p>
   </div>
  </div>''')
        items.append({"@type": "ListItem", "position": i, "name": a[kh], "url": f'{BASE}{pre}/{slug}/'})
    alts = '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{BASE}{"" if l=="en" else "/"+l}/guides/">' for l in ORDER) \
        + f'\n<link rel="alternate" hreflang="x-default" href="{BASE}/guides/">'
    ld = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": url + "#page", "name": heading, "url": url, "inLanguage": lang,
         "isPartOf": {"@type": "WebSite", "url": BASE + (pre or '') + '/'}},
        {"@type": "ItemList", "@id": url + "#list", "itemListElement": items}]}, ensure_ascii=False, indent=1)
    first_h1 = load(ARTICLES[-1][1], lang)[resolve(ARTICLES[-1][1], ARTICLES[-1][2])]
    html = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{heading} | TouringBee</title>
<meta name="description" content="{first_h1}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/favicon-180.png">
{alts}
<meta property="og:type" content="website">
<meta property="og:site_name" content="ColmarTour">
<meta property="og:locale" content="{LOC[lang]}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{heading}">
<style>
{css}
</style>
</head>
<body>
{hdr}
<main>
<section>
 <div class="wrap">
 <h1>{heading}</h1>
 <div class="grid" style="margin-top:26px;grid-template-columns:repeat(auto-fill,minmax(280px,370px))">
{chr(10).join(cards)}
 </div>
 </div>
</section>
</main>
{ftr}
<script type="application/ld+json">
{ld}
</script>
</body>
</html>'''
    outdir = f'{PUB}/guides' if lang == 'en' else f'{PUB}/{lang}/guides'
    os.makedirs(outdir, exist_ok=True)
    open(f'{outdir}/index.html', 'w', encoding='utf-8').write(html)
    print(f'{lang}: /guides/ -> "{heading}" | {len(cards)} cards')
