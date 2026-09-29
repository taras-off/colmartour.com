#!/usr/bin/env python3
"""Whole-site validation: landing + ALL articles + guides, 8 languages.
v2: SLUGS is a list (article 1 + article 2). Same checks as v1.
Run with --articles-only to check just the article pages (skips pages/images that are not built)."""
import json, re, sys, os
from collections import Counter
from bs4 import BeautifulSoup
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE)
PUB = os.path.join(_ROOT, 'public')
ORDER = ['en','fr','de','es','it','pt','pl','ru']
SLUGS = ['colmar-christmas-market', 'colmar-vs-strasbourg-christmas']
BASE = 'https://colmartour.com'
BOK = 'https://widgets.bokun.io/online-sales/8342c394-d728-44fe-a74b-664ee5a2f48b/experience/950179'
LIVE_TPL = ['/', '/guides/', '/privacy-policy/', '/affiliate-disclosure/'] + [f'/{s}/' for s in SLUGS]
ONLY_ART = '--articles-only' in sys.argv
fail = []
def pages(lang):
    pre = '' if lang == 'en' else f'/{lang}'
    if not ONLY_ART:
        yield 'landing', '/', f'{PUB}{pre}/index.html', f'{BASE}{pre}/'
        yield 'guides', '/guides/', f'{PUB}{pre}/guides/index.html', f'{BASE}{pre}/guides/'
    for s in SLUGS:
        p = f'{PUB}{pre}/{s}/index.html'
        if ONLY_ART and not os.path.exists(p): continue
        yield f'art:{s}', f'/{s}/', p, f'{BASE}{pre}/{s}/'
live = set(LIVE_TPL)
for l in ORDER[1:]:
    live |= {(f'/{l}{p}' if p != '/' else f'/{l}/') for p in LIVE_TPL}
live |= {f'/{l}/' for l in ORDER} | {'/'}
ref_tags = {}
for lang in ORDER:
    for kind, want, path, url in pages(lang):
        errs = []
        if not os.path.exists(path):
            fail.append((lang, kind, 'MISSING FILE')); print(f'{lang}/{kind}: MISSING'); continue
        h = open(path, encoding='utf-8').read(); s = BeautifulSoup(h, 'html.parser')
        if s.html.get('lang') != lang: errs.append(f'html lang={s.html.get("lang")}')
        c = s.find('link', rel='canonical')
        if not c or c['href'] != url: errs.append(f'canonical {c["href"] if c else None} != {url}')
        hl = s.find_all('link', hreflang=True)
        if len(hl) != 9: errs.append(f'hreflang count {len(hl)}')
        for x in hl:
            code = x['hreflang']; exp = f'{BASE}{want}' if code in ('en','x-default') else f'{BASE}/{code}{want}' if want != '/' else f'{BASE}/{code}/'
            if x['href'] != exp: errs.append(f'hreflang {code} -> {x["href"]}')
        tags = Counter(t.name for t in s.find_all(True))
        if kind not in ref_tags: ref_tags[kind] = tags
        else:
            diff = {k: (ref_tags[kind].get(k,0), tags.get(k,0)) for k in set(ref_tags[kind])|set(tags) if ref_tags[kind].get(k,0) != tags.get(k,0)}
            if diff: errs.append(f'tag drift vs en: {diff}')
        for a in s.find_all('a', href=True):
            hh = a['href'].split('#')[0]
            if hh and hh.startswith('/') and not hh.startswith(('/img','/favicon')) and hh not in live:
                errs.append(f'dead link {hh}')
            if re.match(r'^/(fr|de|es|it|pt|pl|ru)/(fr|de|es|it|pt|pl|ru)/', hh): errs.append(f'double prefix {hh}')
        for a in s.select('a.bokunButton'):
            if a['href'] != BOK or not a.get('data-src','').startswith(BOK): errs.append('bad bokun url')
        if kind != 'guides' and 'BokunWidgetsLoader' not in h: errs.append('bokun loader missing')
        navs = s.select('nav.lang a')
        if len(navs) != 8: errs.append(f'langnav {len(navs)} links')
        else:
            for a in navs:
                l2 = a.get_text(strip=True).lower()
                exp = want if l2 == 'en' else (f'/{l2}{want}' if want != '/' else f'/{l2}/')
                if a['href'] != exp: errs.append(f'langnav {l2} -> {a["href"]} != {exp}')
            on = [a for a in navs if 'on' in (a.get('class') or [])]
            if len(on) != 1 or on[0].get_text(strip=True).lower() != lang: errs.append('langnav "on" wrong')
        for sc in s.find_all('script', attrs={'type':'application/ld+json'}):
            try: json.loads(sc.string)
            except Exception as e: errs.append(f'ld+json parse: {e}')
        if kind.startswith('art:'):
            g = json.loads(s.find_all('script', attrs={'type':'application/ld+json'})[-1].string)['@graph']
            if {n['@type'] for n in g} != {'Article','FAQPage','BreadcrumbList'}: errs.append('schema types')
            faq = [n for n in g if n['@type']=='FAQPage'][0]['mainEntity']
            if len(faq) != len(s.select('.faq details')): errs.append('FAQ schema count')
            if [n for n in g if n['@type']=='Article'][0]['inLanguage'] != lang: errs.append('Article inLanguage')
            t = s.find('title').get_text()
            if len(t) > 60: errs.append(f'title {len(t)} chars')
            d = s.find('meta', attrs={'name':'description'})['content']
            if len(d) > 160: errs.append(f'meta description {len(d)} chars')
        body = s.find('body').get_text(' ')
        if lang == 'en':
            if '9,99' in body: errs.append('comma decimal on EN')
        else:
            if '9.99' in body: errs.append('English decimal point')
            if re.search(r'€\s?\d', body): errs.append('euro symbol before amount')
        if not ONLY_ART:
            for img in s.find_all('img', src=True):
                src = img['src']
                rel = src.lstrip('/') if src.startswith('/') else os.path.normpath(os.path.join(os.path.dirname(path), src)).replace(PUB+'/','')
                if not os.path.exists(os.path.join(PUB, rel)): errs.append(f'missing image {src}')
        print(f'{lang:>3}/{kind:<40} {"OK " if not errs else "FAIL"} {len(h)//1024:>3}KB')
        for e in sorted(set(errs)): print(f'   - {e}'); fail.append((lang, kind, e))
print('\n' + ('ALL PAGES PASS' if not fail else f'{len(fail)} PROBLEMS'))
sys.exit(1 if fail else 0)
