#!/usr/bin/env python3
"""Structural validation of every rendered language page against EN."""
import json, re, sys
from collections import Counter
from bs4 import BeautifulSoup

PUB = '/home/claude/work/public'
LANGS = ['en', 'fr', 'de', 'es', 'it', 'pt', 'pl', 'ru']
BOKUN = 'https://widgets.bokun.io/online-sales/8342c394-d728-44fe-a74b-664ee5a2f48b/experience/950179'
UUID = '8342c394-d728-44fe-a74b-664ee5a2f48b'
AFFIL = ['tiqets.com', 'getyourguide.com', 'booking.com', 'track.effiliation.com',
         'touringbee.com/product/city-tour-of-strasbourg', 'touringbee.com/shop-tbee']
AUDIO = {'en': 'en', 'fr': 'fr', 'de': 'de', 'es': 'en', 'it': 'it', 'pt': 'en', 'pl': 'pl', 'ru': 'en'}

fail = []


def path(l):
    return f'{PUB}/index.html' if l == 'en' else f'{PUB}/{l}/index.html'


ref = None
for l in LANGS:
    h = open(path(l), encoding='utf-8').read()
    soup = BeautifulSoup(h, 'html.parser')
    errs = []

    # 1. tag structure parity
    tags = Counter(t.name for t in soup.find_all(True))
    if ref is None:
        ref = tags
    else:
        diff = {k: (ref.get(k, 0), tags.get(k, 0)) for k in set(ref) | set(tags)
                if ref.get(k, 0) != tags.get(k, 0)}
        if diff:
            errs.append(f'tag-count drift vs en: {diff}')

    # 2. bokun
    n_btn = len(soup.select('a.bokunButton'))
    if n_btn != 5:
        errs.append(f'bokunButton count {n_btn} != 5')
    for a in soup.select('a.bokunButton'):
        if a['href'] != BOKUN or not a.get('data-src', '').startswith(BOKUN):
            errs.append(f'bad bokun url: {a.get("href")}')
    if h.count(UUID) != 11:
        errs.append(f'channel uuid occurrences {h.count(UUID)} != 11')

    # 3. affiliate links intact & not prefixed
    for a in AFFIL:
        if a not in h:
            errs.append(f'missing affiliate link: {a}')
    for m in re.findall(r'href="/[a-z]{2}/https?:', h):
        errs.append('prefixed an external url')

    # 4. internal links language-prefixed
    internal = set(re.findall(r'href="(/[^"#]*)"', h))
    for u in internal:
        if re.match(r'^/(img/|favicon)', u):
            continue
        if u in ('/', '/fr/', '/de/', '/es/', '/it/', '/pt/', '/pl/', '/ru/'):
            continue
        if l == 'en':
            if re.match(r'^/(fr|de|es|it|pt|pl|ru)/', u):
                errs.append(f'en page links into {u}')
        else:
            if not u.startswith(f'/{l}/'):
                errs.append(f'unprefixed internal link: {u}')

    # 5. head
    if soup.html.get('lang') != l:
        errs.append(f'html lang={soup.html.get("lang")}')
    canon = soup.find('link', rel='canonical')['href']
    want = 'https://colmartour.com/' + ('' if l == 'en' else f'{l}/')
    if canon != want:
        errs.append(f'canonical {canon} != {want}')
    if len(soup.find_all('link', hreflang=True)) != 9:
        errs.append('hreflang block incomplete')

    # 6. audio
    src = soup.find('source', attrs={'type': 'audio/mpeg'})['src']
    if f'colmart1_{AUDIO[l]}_intro.mp3' not in src:
        errs.append(f'audio src {src}')

    # 7. json-ld
    for s in soup.find_all('script', attrs={'type': 'application/ld+json'}):
        try:
            d = json.loads(s.string)
        except Exception as e:
            errs.append(f'ld+json parse: {e}')
            continue
        prod = [n for n in d['@graph'] if n.get('@type') == 'Product'][0]
        if prod['offers']['price'] != '9.99':
            errs.append('schema price changed')
        if prod['aggregateRating']['ratingValue'] != '4.6':
            errs.append('schema rating changed')
        site = [n for n in d['@graph'] if n.get('@type') == 'WebSite'][0]
        if site['inLanguage'] != l:
            errs.append(f'schema inLanguage {site["inLanguage"]}')
        if len([n for n in d['@graph'] if n.get('@type') == 'FAQPage'][0]['mainEntity']) != 8:
            errs.append('FAQ schema not 8 questions')

    # 8. visible price format
    body = soup.find('body').get_text(' ')
    if l != 'en' and '9.99' in body:
        errs.append('English decimal point in price')
    if l == 'en' and '9,99' in body:
        errs.append('comma decimal on EN page')
    for must in ['4,6' if l != 'en' else '4.6']:
        if must not in body:
            errs.append(f'rating {must} not visible')

    # 9. reviews present
    if len(soup.select('.rev')) != 14:
        errs.append(f'{len(soup.select(".rev"))} review cards != 14')

    # 10. no leftover English in headings (rough tell)
    if l not in ('en',):
        h1 = soup.find('h1').get_text()
        if h1 == 'Colmar: the old town, Little Venice and the Christmas markets':
            errs.append('H1 untranslated')

    status = 'OK  ' if not errs else 'FAIL'
    print(f'{l}: {status} {len(h)//1024}KB  h1="{soup.find("h1").get_text()[:58]}"')
    for e in errs:
        print(f'      - {e}')
        fail.append((l, e))

print('\n' + ('ALL PAGES PASS' if not fail else f'{len(fail)} PROBLEMS'))
sys.exit(1 if fail else 0)
