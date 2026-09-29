#!/usr/bin/env python3
"""Turn article-en.html into template-art.html + content/en.json (copy of build-art/extract_art.py)."""
import json, re, sys
from bs4 import BeautifulSoup, NavigableString, Comment
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
SRC = _os.path.join(_HERE, 'article-en.html')
OUT_TPL = _os.path.join(_HERE, 'template-art.html')
OUT_EN = _os.path.join(_HERE, 'content', 'en.json')
INLINE = {'a', 'b', 'strong', 'em', 'i', 'small', 'span', 'br', 'sup', 'sub', 'code', 'u'}
html = open(SRC, encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')
units = {}
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
        if 'btn' in classes(node):
            return False
        par = node.parent
        if par and par.get_text(strip=True) == node.get_text(strip=True):
            sibs = [c for c in par.children if not (isinstance(c, NavigableString) and not c.strip())]
            if len(sibs) == 1:
                return False
    return True
def ctx_of(el):
    parts = []
    for anc in list(el.parents)[:4][::-1]:
        if not getattr(anc, 'name', None) or anc.name in ('html', 'body', '[document]'):
            continue
        cl = classes(anc)
        parts.append(anc.name + ('.' + cl[0] if cl else '') + ('#' + anc['id'] if anc.get('id') else ''))
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
    kids = [c for c in el.children if not (isinstance(c, NavigableString) and not c.strip()) and not isinstance(c, Comment)]
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
hero = soup.find('div', class_='arthero')
if hero:
    walk(hero)
sticky = soup.find(id='sticky')
if sticky:
    walk(sticky)
for img in soup.find_all('img'):
    if img.get('alt') and not in_skip(img):
        tid = newid()
        units[tid] = {'ctx': 'img alt (%s)' % img.get('src', ''), 'en': img['alt']}
        img['alt'] = '{{%s}}' % tid
t = soup.find('title')
tid = newid(); units[tid] = {'ctx': '<title> (SEO title, <=60 chars)', 'en': t.string}
t.string = '{{%s}}' % tid
m = soup.find('meta', attrs={'name': 'description'})
tid = newid(); units[tid] = {'ctx': 'meta description (SEO, <=155 chars)', 'en': m['content']}
m['content'] = '{{%s}}' % tid
for prop in ['og:title', 'og:description']:
    m = soup.find('meta', attrs={'property': prop})
    tid = newid(); units[tid] = {'ctx': prop, 'en': m['content']}
    m['content'] = '{{%s}}' % tid
soup.html['lang'] = '{{LANG}}'
soup.find('link', rel='canonical')['href'] = '{{CANONICAL}}'
soup.find('meta', attrs={'property': 'og:url'})['content'] = '{{CANONICAL}}'
soup.find('meta', attrs={'property': 'og:locale'})['content'] = '{{OG_LOCALE}}'
out = str(soup)
out = re.sub(r'<nav class="lang">.*?</nav>', '{{LANGNAV}}', out, flags=re.S)
open(OUT_TPL, 'w', encoding='utf-8').write(out)
json.dump(units, open(OUT_EN, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('units:', len(units))
words = sum(len(re.sub(r'<[^>]+>', ' ', v['en']).split()) for v in units.values())
print('words:', words)
missing = re.findall(r'\{\{(T\d+|S\d+)\}\}', out)
assert len(set(missing)) == len(units), (len(set(missing)), len(units))
