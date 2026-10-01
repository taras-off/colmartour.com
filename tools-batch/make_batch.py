#!/usr/bin/env python3
"""Batch build for articles 4-8 (October 2026).
For every slug: md/<lang>.md  ->  build-art-<slug>/{article-<lang>.html, article-en.html, template-art.html,
content/<lang>.json, render_art.py, extract_art.py, check_units.py}.
Site chrome (header, footer, sticky, CSS, final CTA, disclosure, byline) is taken from article 3's kit,
so the new pages look and behave exactly like the published ones.
Run from the repo root:  python3 tools-batch/make_batch.py
"""
import json, os, re, shutil, html as H
from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = os.getcwd()
CHROME = os.path.join(ROOT, 'build-art-christmas-markets-near-colmar')
ORDER = ['en', 'fr', 'de', 'es', 'it', 'pt', 'pl', 'ru']
DATE = '2026-10-01'
BOK = 'https://widgets.bokun.io/online-sales/8342c394-d728-44fe-a74b-664ee5a2f48b/experience/950179'
BOKBTN = f'href="{BOK}" data-src="{BOK}?partialView=1"'
HOTELS = 'https://www.booking.com/searchresults.html?ss=Colmar&amp;aid=1437498'
CARS = 'https://www.booking.com/cars/index.html?aid=1437498'
SNCF = 'https://www.sncf-connect.com/'
# slug -> og/guides image, hero buttons after the audio guide (by order of [BUTTONS: ...] labels 2..n)
ARTS = {
    'how-to-get-to-colmar':      dict(img='tile-rooftops.webp',      extra=['sncf', 'cars']),
    'colmar-parking':            dict(img='tile-winter-street.webp', extra=['hotels']),
    'where-to-stay-in-colmar':   dict(img='tile-little-venice.webp', extra=['hotels']),
    'best-time-to-visit-colmar': dict(img='tile-canal-day.webp',     extra=['hotels']),
    'is-colmar-worth-visiting':  dict(img='tile-old-town.webp',      extra=['hotels']),
}
MONTH = {'en': ('September', 'October'), 'fr': ('septembre', 'octobre'), 'de': ('September', 'Oktober'),
         'es': ('septiembre', 'octubre'), 'it': ('settembre', 'ottobre'), 'pt': ('setembro', 'outubro'),
         'pl': ('wrzesień', 'październik'), 'ru': ('сентябре', 'октябре')}

# ---------- chrome from article 3 ----------
c_tpl = open(f'{CHROME}/template-art.html', encoding='utf-8').read()
c_en = json.load(open(f'{CHROME}/content/en.json', encoding='utf-8'))
def ckey(ctx_start, nth=0):
    ks = [k for k, v in c_en.items() if v['ctx'].startswith(ctx_start)]
    return ks[nth]
def cval(lang, k):
    d = json.load(open(f'{CHROME}/content/{lang}.json', encoding='utf-8'))
    v = d[k]
    return v['en'] if isinstance(v, dict) else v
K = dict(byline=ckey('div.arthero > div.wrap > p.byline'), crumb=ckey('div.arthero > div.wrap > div.crumb'),
         herobtn=ckey('div.wrap > div.btns > a.btn', 0), buy=ckey('div.product > div.pad > a.btn'),
         alt=ckey('img alt (../img/product-colmar.webp)'), fin_h=ckey('div.wrap > div.final > h2'),
         fin_p=ckey('div.wrap > div.final > p'), fin_b1=ckey('div.final > div.btns > a.btn', 0),
         fin_b2=ckey('div.final > div.btns > a.btn', 1), disc=ckey('section > div.wrap > p.disclosure'))

def shell(lang):
    """article 3 template with every unit filled in `lang` (header/footer/sticky localized)."""
    d = json.load(open(f'{CHROME}/content/{lang}.json', encoding='utf-8'))
    out = c_tpl
    for k in c_en:
        v = d.get(k); v = (v.get('loc') or v.get('en')) if isinstance(v, dict) else v
        out = out.replace('{{%s}}' % k, v or c_en[k]['en'])
    return out

# ---------- markdown -> html ----------
def inline(s):
    s = re.sub(r'\s*\[LINK:[^\]]*\]', '', s)          # unpublished articles: plain text, no link
    s = H.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\[([^\]]+)\]\((/[^)]*)\)', r'<a href="\2">\1</a>', s)
    s = s.replace('€', '&euro;') if False else s
    return s.strip()

def parse(md):
    fm, body = re.match(r'---\n(.*?)\n---\n(.*)', md, re.S).groups()
    meta = dict(re.findall(r'^(\w+): (.*)$', fm, re.M))
    blocks = [b.strip() for b in re.split(r'\n\s*\n', body.strip()) if b.strip()]
    return meta, blocks

def table(b):
    rows = [r.strip().strip('|').split('|') for r in b.split('\n') if r.strip().startswith('|')]
    rows = [[inline(c) for c in r] for r in rows if not re.match(r'^\s*-+\s*$', r[0])]
    head, rest = rows[0], rows[1:]
    th = ''.join(f'<th>{c}</th>' for c in head)
    tb = '\n'.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rest)
    return f'<table>\n<thead><tr>{th}</tr></thead>\n<tbody>\n{tb}\n</tbody>\n</table>'

def ulist(b, cls=''):
    items = [inline(l[2:]) for l in b.split('\n') if l.startswith('- ')]
    c = f' class="{cls}"' if cls else ''
    return f'<ul{c}>\n' + '\n'.join(f'<li>{i}</li>' for i in items) + '\n</ul>'

def build_page(slug, lang, md):
    meta, blocks = parse(md)
    h1 = blocks[0][2:].strip()
    sub = blocks[1].strip('*').strip()
    labels = [x.strip() for x in re.match(r'\[BUTTONS: (.*)\]', blocks[2]).group(1).split(' · ')]
    rest = blocks[3:]
    # ---- hero
    btns = [f'<a class="btn dark bokunButton" {BOKBTN}>{cval(lang, K["herobtn"])}</a>']
    for kind, lab in zip(ARTS[slug]['extra'], labels[1:]):
        lab = re.sub(r'\s*\((Booking|SNCF)\)', '', lab)
        if kind == 'sncf':
            btns.append(f'<a class="btn ghost" href="{SNCF}" target="_blank" rel="noopener">{H.escape(lab)}</a>')
        else:
            href = HOTELS if kind == 'hotels' else CARS
            btns.append(f'<a class="btn ghost" href="{href}" target="_blank" rel="noopener sponsored">{H.escape(lab)}</a>')
    home = re.search(r'>(.*?)</a>', cval(lang, K['crumb'])).group(1)
    short = re.split(r'\s*\|\s*', meta['title'])[0].split(':')[0].strip()
    a, b = MONTH[lang]
    byline = cval(lang, K['byline']).replace(a, b)
    hero = (f'<div class="arthero">\n <div class="wrap">\n <div class="crumb"><a href="/">{home}</a> › {H.escape(short)}</div>\n'
            f' <h1>{inline(h1)}</h1>\n <p class="sub">{inline(sub)}</p>\n <p class="byline">{byline}</p>\n'
            f' <div class="btns">\n ' + '\n '.join(btns) + '\n </div>\n </div>\n</div>')
    # ---- main
    out, i, first_p, in_faq = [], 0, True, False
    while i < len(rest):
        b = rest[i]
        if b.startswith('[IMAGE'):
            i += 1; continue
        if b == '[PRODUCT CARD]':
            title = rest[i + 1][4:].strip(); para = inline(rest[i + 2])
            price = rest[i + 3]; pm = re.match(r'(.*?)\s*·\s*(.*)', price)
            plist = ulist(rest[i + 4], 'plist')
            out.append('<div class="product" style="margin:26px 0">\n'
                       f' <img src="../img/product-colmar.webp" width="1200" height="800" loading="lazy" alt="{H.escape(cval(lang, K["alt"]))}">\n'
                       f' <div class="pad">\n <h3>{inline(title)}</h3>\n <p>{para}</p>\n'
                       f' <p class="price">{H.escape(pm.group(1))} <small>· {H.escape(pm.group(2))}</small></p>\n {plist}\n'
                       f' <a class="btn block bokunButton" {BOKBTN}>{cval(lang, K["buy"])}</a>\n </div>\n</div>')
            assert rest[i + 5].startswith('[BUTTON:'), (slug, lang, rest[i + 5][:40])
            i += 6; continue
        if b == '[FINAL CTA]':
            out.append('<div class="final" style="margin-top:32px">\n'
                       f' <h2>{cval(lang, K["fin_h"])}</h2>\n <p>{cval(lang, K["fin_p"])}</p>\n <div class="btns">\n'
                       f' <a class="btn dark bokunButton" {BOKBTN}>{cval(lang, K["fin_b1"])}</a>\n'
                       f' <a class="btn ghost" href="/#preview">{cval(lang, K["fin_b2"])}</a>\n </div>\n</div>')
            i += 1; continue
        if b.startswith('[AFFILIATE DISCLOSURE'):
            out.append(f'<p class="disclosure">{cval(lang, K["disc"])}</p>')
            i += 1; continue
        if b.startswith('[BUTTON:'):
            lab = re.match(r'\[BUTTON: (.*)\]', b).group(1)
            out.append(f'<p><a class="btn outline" href="{SNCF}" target="_blank" rel="noopener">{H.escape(lab)}</a></p>')
            i += 1; continue
        if b.startswith('## '):
            if in_faq: out.append('</div>'); in_faq = False
            out.append(f'<h2>{inline(b[3:])}</h2>')
            # FAQ = an h2 followed by blocks that are all "**Q?**\nA"
            j = i + 1; qa = []
            while j < len(rest) and re.match(r'^\*\*.+\*\*\n', rest[j]):
                qa.append(rest[j]); j += 1
            if len(qa) >= 2 and all(q.split('\n')[0].rstrip('*').endswith('?') for q in qa):
                out.append('<div class="faq">')
                for q in qa:
                    qq, aa = q.split('\n', 1)
                    out.append(f'<details><summary>{inline(qq.strip("*"))}</summary>\n<p>{inline(aa)}</p></details>')
                out.append('</div>')
                i = j; continue
            i += 1; continue
        if b.startswith('### '):
            out.append(f'<h3>{inline(b[4:])}</h3>'); i += 1; continue
        if b.startswith('|'):
            out.append(table(b)); i += 1; continue
        if b.startswith('- '):
            out.append(ulist(b)); i += 1; continue
        cls = ' class="lede"' if first_p else ''
        first_p = False
        out.append(f'<p{cls}>{inline(b.replace(chr(10), " "))}</p>')
        i += 1
    main = '<main>\n<section>\n <div class="wrap art">\n\n' + '\n\n'.join(out) + '\n\n </div>\n</section>\n</main>'
    # ---- assemble on article 3 shell
    page = shell(lang)
    page = re.sub(r'<div class="arthero">.*?\n</div>\n(?=\s*<main>|\s*\n<main>)', hero + '\n', page, count=1, flags=re.S)
    page = re.sub(r'<main>.*?</main>', lambda m: main, page, count=1, flags=re.S)
    head_end = page.index('</head>')
    head = page[:head_end].replace('christmas-markets-near-colmar', slug)
    def setmeta(h, pat, val):
        return re.sub(pat, lambda m: m.group(1) + H.escape(val, quote=True) + m.group(2), h, count=1)
    head = re.sub(r'<title>.*?</title>', lambda m: f'<title>{H.escape(meta["title"])}</title>', head, count=1)
    head = setmeta(head, r'(<meta name="description" content=")[^"]*(")', meta['description'])
    head = setmeta(head, r'(<meta property="og:title" content=")[^"]*(")', re.sub(r'\*', '', h1))
    head = setmeta(head, r'(<meta property="og:description" content=")[^"]*(")', meta['description'])
    head = re.sub(r'(<meta property="og:image" content="https://colmartour.com/img/)[^"]*(")',
                  lambda m: m.group(1) + ARTS[slug]['img'] + m.group(2), head, count=1)
    page = head + page[head_end:]
    return page

# ---------- extraction (same logic as extract_art.py) ----------
INLINE = {'a', 'b', 'strong', 'em', 'i', 'small', 'span', 'br', 'sup', 'sub', 'code', 'u'}
def extract(htmltext):
    soup = BeautifulSoup(htmltext, 'html.parser')
    units = []
    def classes(el): return el.get('class') or []
    def in_skip(el):
        for x in [el] + list(el.parents):
            if getattr(x, 'get', None):
                cl = x.get('class') or []
                if 'brand' in cl or 'lang' in cl: return True
        return False
    def is_inline(n):
        if isinstance(n, NavigableString): return True
        if n.name not in INLINE: return False
        if n.name == 'a':
            if 'btn' in classes(n): return False
            par = n.parent
            if par and par.get_text(strip=True) == n.get_text(strip=True):
                sibs = [c for c in par.children if not (isinstance(c, NavigableString) and not c.strip())]
                if len(sibs) == 1: return False
        return True
    def ctx_of(el):
        parts = []
        for anc in list(el.parents)[:4][::-1]:
            if not getattr(anc, 'name', None) or anc.name in ('html', 'body', '[document]'): continue
            cl = classes(anc)
            parts.append(anc.name + ('.' + cl[0] if cl else '') + ('#' + anc['id'] if anc.get('id') else ''))
        parts.append(el.name + ('.' + classes(el)[0] if classes(el) else ''))
        return ' > '.join(parts[-3:])
    def walk(el):
        if isinstance(el, (NavigableString, Comment)): return
        if el.name in ('script', 'style', 'audio', 'source', 'br', 'img'): return
        if in_skip(el): return
        kids = [c for c in el.children if not (isinstance(c, NavigableString) and not c.strip()) and not isinstance(c, Comment)]
        if not kids: return
        if all(is_inline(k) for k in kids) and el.get_text(strip=True):
            units.append([ctx_of(el), ''.join(str(c) for c in el.children).strip(), el]); return
        for k in kids: walk(k)
    for sel in ['header', 'main', 'footer']:
        for r in soup.find_all(sel): walk(r)
    hero = soup.find('div', class_='arthero')
    if hero: walk(hero)
    st = soup.find(id='sticky')
    if st: walk(st)
    imgs = [img for img in soup.find_all('img') if img.get('alt') and not in_skip(img)]
    for img in imgs: units.append(['img alt (%s)' % img.get('src', ''), img['alt'], ('alt', img)])
    t = soup.find('title'); units.append(['<title> (SEO title, <=60 chars)', t.string, ('title', t)])
    for name, ctx in (({'name': 'description'}, 'meta description (SEO, <=155 chars)'),
                      ({'property': 'og:title'}, 'og:title'), ({'property': 'og:description'}, 'og:description')):
        m = soup.find('meta', attrs=name); units.append([ctx, m['content'], ('content', m)])
    return soup, units

def to_template(soup, units):
    store = {}
    for n, (ctx, val, ref) in enumerate(units, 1):
        tid = 'T%03d' % n
        store[tid] = {'ctx': ctx, 'en': val}
        if isinstance(ref, tuple):
            kind, el = ref
            if kind == 'title': el.string = '{{%s}}' % tid
            else: el[kind] = '{{%s}}' % tid
        else:
            ref.clear(); ref.append(NavigableString('{{%s}}' % tid))
    soup.html['lang'] = '{{LANG}}'
    soup.find('link', rel='canonical')['href'] = '{{CANONICAL}}'
    soup.find('meta', attrs={'property': 'og:url'})['content'] = '{{CANONICAL}}'
    soup.find('meta', attrs={'property': 'og:locale'})['content'] = '{{OG_LOCALE}}'
    out = str(soup)
    out = re.sub(r'<nav class="lang">.*?</nav>', '{{LANGNAV}}', out, flags=re.S)
    return out, store

# ---------- main ----------
SCRIPTS = os.path.join(ROOT, 'tools-batch', 'kit')
for slug, cfg in ARTS.items():
    bdir = os.path.join(ROOT, f'build-art-{slug}')
    mdir = os.path.join(bdir, 'md')
    os.makedirs(os.path.join(bdir, 'content'), exist_ok=True)
    pages = {l: build_page(slug, l, open(f'{mdir}/{l}.md', encoding='utf-8').read()) for l in ORDER}
    open(f'{bdir}/article-en.html', 'w', encoding='utf-8').write(pages['en'])
    soup, units = extract(pages['en'])
    tpl, en_store = to_template(soup, units)
    open(f'{bdir}/template-art.html', 'w', encoding='utf-8').write(tpl)
    json.dump(en_store, open(f'{bdir}/content/en.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    keys = list(en_store)
    for l in ORDER[1:]:
        _, u = extract(pages[l])
        assert len(u) == len(units), f'{slug}/{l}: {len(u)} units vs en {len(units)}'
        for a, b in zip(u, units):
            assert a[0] == b[0], f'{slug}/{l}: structure differs at "{b[0]}" vs "{a[0]}"\n en: {b[1][:80]}\n {l}: {a[1][:80]}'
        json.dump({k: x[1] for k, x in zip(keys, u)}, open(f'{bdir}/content/{l}.json', 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    for f in ('render_art.py', 'check_units.py'):
        s = open(f'{SCRIPTS}/{f}', encoding='utf-8').read()
        s = s.replace('@@SLUG@@', slug).replace('@@DATE@@', DATE).replace('@@IMAGE@@', cfg['img'])
        open(f'{bdir}/{f}', 'w', encoding='utf-8').write(s)
    print(f'{slug}: {len(units)} units x 8 languages')
