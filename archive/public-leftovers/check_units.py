#!/usr/bin/env python3
"""Per-unit HTML parity: every localized string must carry the same inline tags,
with the same attributes, as the English source. Repairs the common failure
(dropped closing quote in an attribute) and reports anything else."""
import json, re, sys
from bs4 import BeautifulSoup

BUILD = '/home/claude/work/build'
LANGS = ['fr', 'de', 'es', 'it', 'pt', 'pl', 'ru']
en = json.load(open(f'{BUILD}/content/en.json', encoding='utf-8'))

QUOTE_FIX = re.compile(r'(<[a-z]+ [^>]*?=")([^"]*?)>')


def sig(s):
    soup = BeautifulSoup(s, 'html.parser')
    out = []
    for t in soup.find_all(True):
        attrs = {k: (' '.join(v) if isinstance(v, list) else v)
                 for k, v in t.attrs.items()}
        out.append((t.name, tuple(sorted(attrs.items()))))
    return out


problems = 0
for l in LANGS:
    p = f'{BUILD}/content/{l}.json'
    d = json.load(open(p, encoding='utf-8'))
    fixed, bad = [], []
    for k, ref in en.items():
        want = sig(ref['en'])
        got = sig(d[k])
        if got == want:
            continue
        # attempt repair: restore a dropped closing quote
        cand = QUOTE_FIX.sub(r'\1\2">', d[k])
        if sig(cand) == want:
            d[k] = cand
            fixed.append(k)
            continue
        # attempt repair: same tag names, wrong/lost attributes -> take EN's
        if [t for t, _ in got] == [t for t, _ in want]:
            soup = BeautifulSoup(d[k], 'html.parser')
            for tag, (_, attrs) in zip(soup.find_all(True), want):
                tag.attrs = {kk: vv for kk, vv in attrs}
            cand = ''.join(str(c) for c in soup.children)
            if sig(cand) == want:
                d[k] = cand
                fixed.append(k)
                continue
        bad.append((k, ref['en'][:70], d[k][:70]))
    if fixed:
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{l}: repaired={len(fixed)} {fixed if fixed else ""} unresolved={len(bad)}')
    for k, a, b in bad:
        problems += 1
        print(f'    {k}\n      EN : {a}\n      {l.upper()} : {b}')

sys.exit(1 if problems else 0)
