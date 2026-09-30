#!/usr/bin/env python3
"""One-time integration of article 3 (christmas-markets-near-colmar). Run from the repo root AFTER integrate_article2.py.
Idempotent. Adds menu + footer items (keys M003/M004) to build/template.html and build-art/template-art.html,
the slug to PUBLISHED in build/render.py and 8 URLs to public/sitemap.xml.
Also adds the same two links to article 2's own page (build-art-colmar-vs-strasbourg-christmas)."""
import json, os, re
ROOT = os.getcwd()
SLUG = 'christmas-markets-near-colmar'
ORDER = ['en','fr','de','es','it','pt','pl','ru']
A3 = os.path.join(ROOT, 'build-art-' + SLUG, 'content')
EN = json.load(open(f'{A3}/en.json', encoding='utf-8'))
def key(text): return next(k for k, v in EN.items() if v['en'] == text)
K_MENU, K_FOOT = key('Christmas markets near Colmar'), key('Village Christmas markets')
def lab(l, k):
    v = json.load(open(f'{A3}/{l}.json', encoding='utf-8'))[k]
    return v['en'] if isinstance(v, dict) else v
MENU = {l: lab(l, K_MENU) for l in ORDER}; FOOT = {l: lab(l, K_FOOT) for l in ORDER}
problems = []
def patch_build(bdir, tpl_name):
    tp = os.path.join(ROOT, bdir, tpl_name)
    if not os.path.exists(tp): problems.append(f'{tp} not found'); return
    t = open(tp, encoding='utf-8').read()
    if '{{M003}}' not in t:
        a2m = '<li><a href="/colmar-vs-strasbourg-christmas/">{{M001}}</a></li>'
        a2f = '<li><a href="/colmar-vs-strasbourg-christmas/">{{M002}}</a></li>'
        if a2m in t and a2f in t:
            t = t.replace(a2m, a2m + f'\n<li><a href="/{SLUG}/">{{{{M003}}}}</a></li>', 1)
            t = t.replace(a2f, a2f + f'\n<li><a href="/{SLUG}/">{{{{M004}}}}</a></li>', 1)
        else:
            problems.append(f'{tp}: article 2 items (M001/M002) not found — run integrate_article2.py first'); return
        open(tp, 'w', encoding='utf-8').write(t); print(f'{tp}: menu + footer item added')
    for l in ORDER:
        cp = os.path.join(ROOT, bdir, 'content', f'{l}.json')
        if not os.path.exists(cp): problems.append(f'{cp} not found'); continue
        d = json.load(open(cp, encoding='utf-8'))
        sample = d.get('M001', next(iter(d.values())))
        for k, labs, ctx in (('M003', MENU, 'header menu > li > a (article 3)'), ('M004', FOOT, 'footer > li > a (article 3)')):
            if l == 'en' or (isinstance(sample, dict) and 'ctx' in sample): d[k] = {'ctx': ctx, 'en': labs[l]}
            elif isinstance(sample, dict): d[k] = {'en': labs['en'], 'loc': labs[l]}
            else: d[k] = labs[l]
        json.dump(d, open(cp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{bdir}/content: M003/M004 set for 8 languages')
patch_build('build-art', 'template-art.html')
patch_build('build', 'template.html')
# article 2 page: add the same items after its own menu/footer links
A2 = os.path.join(ROOT, 'build-art-colmar-vs-strasbourg-christmas')
tp2 = os.path.join(A2, 'template-art.html')
if os.path.exists(tp2):
    t = open(tp2, encoding='utf-8').read()
    if '{{M003}}' not in t:
        pat = re.compile(r'(<li><a href="/colmar-vs-strasbourg-christmas/">\{\{T\d+\}\}</a></li>)')
        n = [0]
        def rep(m):
            n[0] += 1
            k = 'M003' if n[0] == 1 else 'M004'
            return m.group(1) + f'\n<li><a href="/{SLUG}/">{{{{{k}}}}}</a></li>' if n[0] <= 2 else m.group(1)
        t2 = pat.sub(rep, t)
        if n[0] < 2: problems.append(f'{tp2}: expected menu + footer links to article 2, found {n[0]}')
        else:
            open(tp2, 'w', encoding='utf-8').write(t2); print(f'{tp2}: menu + footer item added')
            for l in ORDER:
                cp = os.path.join(A2, 'content', f'{l}.json'); d = json.load(open(cp, encoding='utf-8'))
                if l == 'en':
                    d['M003'] = {'ctx': 'header menu > li > a (article 3)', 'en': MENU['en']}
                    d['M004'] = {'ctx': 'footer > li > a (article 3)', 'en': FOOT['en']}
                else:
                    d['M003'] = MENU[l]; d['M004'] = FOOT[l]
                json.dump(d, open(cp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('build-art-colmar-vs-strasbourg-christmas/content: M003/M004 set for 8 languages')
else: problems.append(f'{tp2} not found')
rp = os.path.join(ROOT, 'build', 'render.py')
if os.path.exists(rp):
    s = open(rp, encoding='utf-8').read()
    if SLUG not in s:
        m = re.search(r'PUBLISHED\s*=\s*([\[\{\(])', s)
        if m:
            s = s[:m.end()] + f"'{SLUG}', " + s[m.end():]; open(rp, 'w', encoding='utf-8').write(s); print('build/render.py: PUBLISHED += ' + SLUG)
        else: problems.append('build/render.py: PUBLISHED not found — add the slug by hand')
else: problems.append('build/render.py not found')
sp = os.path.join(ROOT, 'public', 'sitemap.xml')
if os.path.exists(sp):
    s = open(sp, encoding='utf-8').read()
    if SLUG not in s:
        urls = ''.join(f'<url><loc>https://colmartour.com{"" if l=="en" else "/"+l}/{SLUG}/</loc><lastmod>2026-09-30</lastmod></url>\n' for l in ORDER)
        s = s.replace('</urlset>', urls + '</urlset>'); open(sp, 'w', encoding='utf-8').write(s); print('sitemap.xml: 8 URLs added')
else: problems.append('public/sitemap.xml not found')
print('\nDONE' if not problems else '\nCHECK BY HAND:\n - ' + '\n - '.join(problems))
