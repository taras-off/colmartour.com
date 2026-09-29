#!/usr/bin/env python3
"""One-time integration of article 2 (colmar-vs-strasbourg-christmas) into the existing site sources.
Run ONCE from the repo root (the folder with build/, build-art/, public/). Idempotent: safe to re-run.

What it does:
 1. Adds a menu item and a footer item for article 2 to build-art/template-art.html (article 1)
    and build/template.html (landing), as new keys M001 (menu) / M002 (footer) — existing T-keys untouched.
 2. Adds M001/M002 to every content/<lang>.json of both builds, with the localized labels.
 3. Adds the slug to PUBLISHED in build/render.py.
 4. Adds the 8 new URLs to public/sitemap.xml.
Then run: build/render.py, build-art/render_art.py, build-art-colmar-vs-strasbourg-christmas/render_art.py,
          build-art/build_guides.py (v2), build-art/validate_all.py (v2) -> must print ALL PAGES PASS.
"""
import json, os, re, sys
ROOT = os.getcwd()
SLUG = 'colmar-vs-strasbourg-christmas'
ORDER = ['en','fr','de','es','it','pt','pl','ru']
A2 = os.path.join(ROOT, 'build-art-' + SLUG, 'content')
def a2(lang, key):
    v = json.load(open(f'{A2}/{lang}.json', encoding='utf-8'))[key]
    return v['en'] if isinstance(v, dict) else v
_EN = json.load(open(f'{A2}/en.json', encoding='utf-8'))
K_MENU = next(k for k, v in _EN.items() if v['en'] == 'Colmar or Strasbourg for Christmas')
K_FOOT = next(k for k, v in _EN.items() if v['en'] == 'Colmar or Strasbourg')
MENU = {l: a2(l, K_MENU) for l in ORDER}
FOOT = {l: a2(l, K_FOOT) for l in ORDER}
problems = []
def patch_build(bdir, tpl_name):
    tp = os.path.join(ROOT, bdir, tpl_name)
    if not os.path.exists(tp): problems.append(f'{tp} not found'); return
    t = open(tp, encoding='utf-8').read()
    if '{{M001}}' not in t:
        pat = re.compile(r'(<li><a href="/colmar-christmas-market/">\{\{T\d+\}\}</a></li>)')
        hits = pat.findall(t)
        if len(hits) < 2:
            problems.append(f'{tp}: expected 2 links to article 1 (menu + footer), found {len(hits)} — add M001/M002 by hand')
            return
        n = [0]
        def rep(m):
            n[0] += 1
            key = 'M001' if n[0] == 1 else 'M002'
            return m.group(1) + f'\n<li><a href="/{SLUG}/">{{{{{key}}}}}</a></li>' if n[0] <= 2 else m.group(1)
        t = pat.sub(rep, t)
        open(tp, 'w', encoding='utf-8').write(t)
        print(f'{tp}: menu + footer item added')
    for l in ORDER:
        cp = os.path.join(ROOT, bdir, 'content', f'{l}.json')
        if not os.path.exists(cp): problems.append(f'{cp} not found'); continue
        d = json.load(open(cp, encoding='utf-8'))
        sample = next(iter(d.values()))
        for key, lab, ctx in (('M001', MENU, 'header menu > li > a (article 2)'), ('M002', FOOT, 'footer > li > a (article 2)')):
            if l == 'en' or (isinstance(sample, dict) and 'ctx' in sample):
                d[key] = {'ctx': ctx, 'en': lab[l]}
            elif isinstance(sample, dict):
                d[key] = {'en': lab['en'], 'loc': lab[l]}
            else:
                d[key] = lab[l]
        json.dump(d, open(cp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{bdir}/content: M001/M002 set for 8 languages')
patch_build('build-art', 'template-art.html')
patch_build('build', 'template.html')
# 3. PUBLISHED
rp = os.path.join(ROOT, 'build', 'render.py')
if os.path.exists(rp):
    s = open(rp, encoding='utf-8').read()
    if SLUG not in s:
        m = re.search(r'PUBLISHED\s*=\s*([\[\{\(])', s)
        if m:
            i = m.end()
            s = s[:i] + f"'{SLUG}', " + s[i:]
            open(rp, 'w', encoding='utf-8').write(s); print('build/render.py: PUBLISHED += ' + SLUG)
        else: problems.append('build/render.py: PUBLISHED not found — add the slug by hand')
else: problems.append('build/render.py not found')
# 4. sitemap
sp = os.path.join(ROOT, 'public', 'sitemap.xml')
if os.path.exists(sp):
    s = open(sp, encoding='utf-8').read()
    if SLUG not in s:
        urls = ''.join(f'<url><loc>https://colmartour.com{"" if l=="en" else "/"+l}/{SLUG}/</loc><lastmod>2026-09-29</lastmod></url>\n' for l in ORDER)
        s = s.replace('</urlset>', urls + '</urlset>')
        open(sp, 'w', encoding='utf-8').write(s); print('sitemap.xml: 8 URLs added (check format against existing entries, e.g. xhtml:link alternates)')
else: problems.append('public/sitemap.xml not found')
print('\nDONE' if not problems else '\nCHECK BY HAND:\n - ' + '\n - '.join(problems))
