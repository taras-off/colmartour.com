#!/usr/bin/env python3
"""Turn public/index.html into template.html + content/en.json.

Every translatable text unit becomes {{Tn}}. A "unit" is a block element whose
children are only text / inline markup, so a sentence with an inline <a> or
<strong> stays whole (word order differs between languages — fragments are
untranslatable).
"""
import json, re, sys
from bs4 import BeautifulSoup, NavigableString, Comment

SRC = '/home/claude/work/public/index.html'
OUT_TPL = '/home/claude/work/build/template.html'
OUT_EN = '/home/claude/work/build/content/en.json'

INLINE = {'a', 'b', 'strong', 'em', 'i', 'small', 'span', 'br', 'sup', 'sub', 'code', 'u'}
SKIP_TREES = [
    {'class': 'brand'}, {'class': 'lang'},
]

html = open(SRC, encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')

units = {}          # id -> {'ctx':..., 'en':...}
counter = [0]


def newid():
    counter[0] += 1
    return 'T%03d' % counter[0]


def classes(el):
    return el.get('class') or []


def in_skip(el):
    cl = getattr(el, 'get', lambda k, d=None: None)('class') or []
    if 'brand' in cl or 'lang' in cl:
        return True
    for anc in el.parents:
        if getattr(anc, 'get', None):
            cl = anc.get('class') or []
            if 'brand' in cl or 'lang' in cl:
                return True
    return False


def is_inline(node):
    if isinstance(node, NavigableString):
        return True
    if node.name not in INLINE:
        return False
    if node.name == 'a':
        cl = classes(node)
        if 'btn' in cl:
            return False          # buttons are their own unit
        # a link that is the entire content of its parent is its own unit
        par = node.parent
        if par and par.get_text(strip=True) == node.get_text(strip=True):
            sibs = [c for c in par.children
                    if not (isinstance(c, NavigableString) and not c.strip())]
            if len(sibs) == 1:
                return False
    return True


def ctx_of(el):
    parts = []
    for anc in list(el.parents)[:4][::-1]:
        if not getattr(anc, 'name', None) or anc.name in ('html', 'body', '[document]'):
            continue
        cl = classes(anc)
        parts.append(anc.name + ('.' + cl[0] if cl else '')
                     + ('#' + anc['id'] if anc.get('id') else ''))
    parts.append(el.name + ('.' + classes(el)[0] if classes(el) else ''))
    return ' > '.join(parts[-3:])


def inner_html(el):
    return ''.join(str(c) for c in el.children).strip()


def walk(el):
    if isinstance(el, (NavigableString, Comment)):
        return
    if el.name in ('script', 'style', 'audio', 'source', 'br', 'img'):
        return
    if in_skip(el):
        return
    kids = [c for c in el.children
            if not (isinstance(c, NavigableString) and not c.strip())
            and not isinstance(c, Comment)]
    if not kids:
        return
    if all(is_inline(k) for k in kids) and el.get_text(strip=True):
        tid = newid()
        units[tid] = {'ctx': ctx_of(el), 'en': inner_html(el)}
        el.clear()
        el.append(NavigableString('{{%s}}' % tid))
        return
    for k in list(kids):
        walk(k)


for root_sel in ['header', 'main', 'footer']:
    for root in soup.find_all(root_sel):
        walk(root)
sticky = soup.find(id='sticky')
if sticky:
    walk(sticky)

# ---- attributes -------------------------------------------------------
for img in soup.find_all('img'):
    if img.get('alt') and not in_skip(img):
        tid = newid()
        units[tid] = {'ctx': 'img alt (%s)' % img.get('src', ''), 'en': img['alt']}
        img['alt'] = '{{%s}}' % tid

t = soup.find('title')
tid = newid(); units[tid] = {'ctx': '<title> (SEO title, <=60 chars)', 'en': t.string}
t.string = '{{%s}}' % tid

for name, ctx in [('description', 'meta description (SEO, <=155 chars)')]:
    m = soup.find('meta', attrs={'name': name})
    tid = newid(); units[tid] = {'ctx': ctx, 'en': m['content']}
    m['content'] = '{{%s}}' % tid

for prop, ctx in [('og:title', 'og:title'), ('og:description', 'og:description')]:
    m = soup.find('meta', attrs={'property': prop})
    tid = newid(); units[tid] = {'ctx': ctx, 'en': m['content']}
    m['content'] = '{{%s}}' % tid

# ---- structural placeholders -----------------------------------------
soup.html['lang'] = '{{LANG}}'
soup.find('link', rel='canonical')['href'] = '{{CANONICAL}}'
soup.find('meta', attrs={'property': 'og:url'})['content'] = '{{CANONICAL}}'
soup.find('meta', attrs={'property': 'og:locale'})['content'] = '{{OG_LOCALE}}'

aud = soup.find('source', attrs={'type': 'audio/mpeg'})
aud['src'] = '{{AUDIO_SRC}}'

out = str(soup)

# language nav: rebuild at render time
out = re.sub(r'<nav class="lang">.*?</nav>', '{{LANGNAV}}', out, flags=re.S)

# ---- JSON-LD ----------------------------------------------------------
m = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', out, re.S)
ld = json.loads(m.group(2))
sch = {}
sc = [0]


def snew():
    sc[0] += 1
    return 'S%02d' % sc[0]


for node in ld['@graph']:
    ty = node.get('@type')
    if ty == 'WebSite':
        node['inLanguage'] = '{{LANG}}'
    if ty in ('Product', 'TouristAttraction', 'Person'):
        for f in ('name', 'description'):
            if ty != 'Product' and f == 'name':
                continue
            if node.get(f):
                k = snew(); sch[k] = {'ctx': 'schema %s.%s' % (ty, f), 'en': node[f]}
                node[f] = '{{%s}}' % k
    if ty == 'FAQPage':
        for q in node['mainEntity']:
            k = snew(); sch[k] = {'ctx': 'schema FAQ question', 'en': q['name']}
            q['name'] = '{{%s}}' % k
            k = snew(); sch[k] = {'ctx': 'schema FAQ answer', 'en': q['acceptedAnswer']['text']}
            q['acceptedAnswer']['text'] = '{{%s}}' % k

units.update(sch)
out = out[:m.start(2)] + json.dumps(ld, ensure_ascii=False, indent=1) + out[m.end(2):]

open(OUT_TPL, 'w', encoding='utf-8').write(out)
json.dump(units, open(OUT_EN, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('units:', len(units))
words = sum(len(re.sub(r'<[^>]+>', ' ', v['en']).split()) for v in units.values())
print('words:', words)
missing = re.findall(r'\{\{(T\d+|S\d+)\}\}', out)
print('placeholders in template:', len(missing), 'unique:', len(set(missing)))
assert len(set(missing)) == len(units), (len(set(missing)), len(units))
