#!/usr/bin/env python3
"""October 2026 batch integration. Run from the repo root after the five render_art.py runs.
Idempotent. Touches ONLY:
  - public/[lang/]guides/index.html  — card grid and ItemList rebuilt: 5 new articles + №3 + №2 + №1
    (№1's card is kept exactly as it is on the page);
  - public/sitemap.xml               — adds missing URLs for №2, №3 and the 5 new articles (8 languages each).
Published article pages (№1–№3) and the landing page are NOT modified.
"""
import json, os, re
from bs4 import BeautifulSoup
ROOT = os.getcwd(); PUB = os.path.join(ROOT, 'public'); BASE = 'https://colmartour.com'
ORDER = ['en', 'fr', 'de', 'es', 'it', 'pt', 'pl', 'ru']
NEW = [('is-colmar-worth-visiting', 'tile-old-town'), ('best-time-to-visit-colmar', 'tile-canal-day'),
       ('how-to-get-to-colmar', 'tile-rooftops'), ('where-to-stay-in-colmar', 'tile-little-venice'),
       ('colmar-parking', 'tile-winter-street')]
OLD = [('christmas-markets-near-colmar', 'tile-christmas-market'), ('colmar-vs-strasbourg-christmas', 'tile-little-venice')]
ALT = {
 'tile-old-town': {'en': "Half-timbered houses and visitors on a square in Colmar's old town", 'fr': "Maisons à colombages et visiteurs sur une place de la vieille ville de Colmar", 'de': "Fachwerkhäuser und Besucher auf einem Platz in der Altstadt von Colmar", 'es': "Casas con entramado de madera y visitantes en una plaza del casco antiguo de Colmar", 'it': "Case a graticcio e visitatori in una piazza del centro storico di Colmar", 'pt': "Casas enxaimel e visitantes numa praça do centro histórico de Colmar", 'pl': "Domy z muru pruskiego i turyści na placu Starego Miasta w Colmarze", 'ru': "Фахверковые дома и туристы на площади Старого города Кольмара"},
 'tile-canal-day': {'en': "Half-timbered houses along a canal in Colmar on a sunny day", 'fr': "Maisons à colombages au bord d'un canal de Colmar par une journée ensoleillée", 'de': "Fachwerkhäuser an einem Kanal in Colmar an einem sonnigen Tag", 'es': "Casas con entramado de madera junto a un canal de Colmar en un día soleado", 'it': "Case a graticcio lungo un canale di Colmar in una giornata di sole", 'pt': "Casas enxaimel junto a um canal de Colmar num dia de sol", 'pl': "Domy z muru pruskiego nad kanałem w Colmarze w słoneczny dzień", 'ru': "Фахверковые дома у канала в Кольмаре в солнечный день"},
 'tile-rooftops': {'en': "A traveller looking out over the rooftops of Colmar", 'fr': "Une voyageuse face aux toits de Colmar", 'de': "Eine Reisende mit Blick über die Dächer von Colmar", 'es': "Una viajera contemplando los tejados de Colmar", 'it': "Una viaggiatrice che guarda i tetti di Colmar", 'pt': "Uma viajante a olhar para os telhados de Colmar", 'pl': "Podróżniczka patrząca na dachy Colmaru", 'ru': "Путешественница смотрит на крыши Кольмара"},
 'tile-little-venice': {'en': "Colourful houses and flowers along the canal in Colmar's Little Venice", 'fr': "Maisons colorées et fleurs au bord du canal, dans la Petite Venise de Colmar", 'de': "Bunte Häuser und Blumen am Kanal in Klein-Venedig, Colmar", 'es': "Casas de colores y flores junto al canal en la Pequeña Venecia de Colmar", 'it': "Case colorate e fiori lungo il canale nella Piccola Venezia di Colmar", 'pt': "Casas coloridas e flores junto ao canal na Pequena Veneza de Colmar", 'pl': "Kolorowe domy i kwiaty nad kanałem w Małej Wenecji w Colmarze", 'ru': "Цветные дома и цветы у канала в Маленькой Венеции, Кольмар"},
 'tile-winter-street': {'en': "A half-timbered street in Colmar decorated for Christmas", 'fr': "Une rue à colombages de Colmar décorée pour Noël", 'de': "Eine weihnachtlich geschmückte Fachwerkgasse in Colmar", 'es': "Una calle de casas con entramado de madera en Colmar, decorada para Navidad", 'it': "Una via di case a graticcio a Colmar addobbata per Natale", 'pt': "Uma rua de casas enxaimel em Colmar decorada para o Natal", 'pl': "Uliczka z domami z muru pruskiego w Colmarze w świątecznych dekoracjach", 'ru': "Улица с фахверковыми домами в Кольмаре в рождественском убранстве"},
}
def unit(slug, lang, ctx):
    b = os.path.join(ROOT, f'build-art-{slug}', 'content')
    en = json.load(open(f'{b}/en.json', encoding='utf-8'))
    k = next(k for k, v in en.items() if v['ctx'].startswith(ctx))
    v = json.load(open(f'{b}/{lang}.json', encoding='utf-8'))[k]
    return v['en'] if isinstance(v, dict) else v
def card(slug, img, lang, alt):
    pre = '' if lang == 'en' else f'/{lang}'
    h1 = unit(slug, lang, 'div.arthero > div.wrap > h1'); sub = unit(slug, lang, 'div.arthero > div.wrap > p.sub')
    return h1, (f'  <div class="card">\n   <img src="/img/{img}.webp" width="800" height="600" loading="lazy" alt="{alt}">\n'
                f'   <div class="pad">\n    <h3><a href="{pre}/{slug}/">{h1}</a></h3>\n    <p>{sub}</p>\n   </div>\n  </div>')
for lang in ORDER:
    pre = '' if lang == 'en' else f'/{lang}'
    p = f'{PUB}{pre}/guides/index.html'
    h = open(p, encoding='utf-8').read()
    s = BeautifulSoup(h, 'html.parser')
    grid = s.select_one('main div.grid')
    first = None
    for c in grid.select('div.card'):
        a = c.find('a', href=True)
        if a and a['href'].rstrip('/').endswith('colmar-christmas-market'): first = c
    assert first is not None, f'{lang}: card of article 1 not found'
    a1_name = first.find('h3').get_text(strip=True); a1_card = str(first)
    cards, items = [], []
    for slug, img in NEW + OLD:
        alt = ALT[img][lang] if img in ALT and slug != 'christmas-markets-near-colmar' else first.find('img')['alt']
        name, html = card(slug, img, lang, alt)
        cards.append(html); items.append((name, f'{BASE}{pre}/{slug}/'))
    cards.append(a1_card); items.append((a1_name, f'{BASE}{pre}/colmar-christmas-market/'))
    new_grid = BeautifulSoup(f'<div class="grid" style="{grid.get("style", "")}">\n' + '\n'.join(cards) + '\n </div>', 'html.parser')
    grid.replace_with(new_grid)
    for sc in s.find_all('script', attrs={'type': 'application/ld+json'}):
        d = json.loads(sc.string)
        for node in d.get('@graph', []):
            if node.get('@type') == 'ItemList':
                node['itemListElement'] = [{"@type": "ListItem", "position": i, "name": n, "url": u}
                                           for i, (n, u) in enumerate(items, 1)]
        sc.string = '\n' + json.dumps(d, ensure_ascii=False, indent=1) + '\n'
    open(p, 'w', encoding='utf-8').write(str(s))
    print(f'{lang}: /guides/ -> {len(cards)} cards')
sp = f'{PUB}/sitemap.xml'; sm = open(sp, encoding='utf-8').read(); added = 0
def alts(slug):
    return ''.join(f'    <xhtml:link rel="alternate" hreflang="{l}" href="{BASE}{"" if l == "en" else "/" + l}/{slug}/"/>\n' for l in ORDER) \
        + f'    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE}/{slug}/"/>\n'
for slug in [x for x, _ in OLD] + [x for x, _ in NEW]:
    for l in ORDER:
        loc = f'{BASE}{"" if l == "en" else "/" + l}/{slug}/'
        if f'<loc>{loc}</loc>' not in sm:
            sm = sm.replace('</urlset>', f'  <url>\n    <loc>{loc}</loc>\n{alts(slug)}  </url>\n</urlset>'); added += 1
open(sp, 'w', encoding='utf-8').write(sm)
print(f'sitemap.xml: +{added} URLs, total {sm.count("<loc>")}')
