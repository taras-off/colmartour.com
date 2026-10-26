#!/usr/bin/env python3
"""HTML parity: every localized string must carry exactly the same tags/attributes as English."""
import json, re, sys, os
H = os.path.dirname(os.path.abspath(__file__))
en = json.load(open(f'{H}/content/en.json', encoding='utf-8'))
TAG = re.compile(r'<[^>]+>|&[a-z]+;')
bad = 0
for lang in ['fr','de','es','it','pt','pl','ru']:
    p = f'{H}/content/{lang}.json'
    if not os.path.exists(p): print(lang, 'MISSING FILE'); bad += 1; continue
    d = json.load(open(p, encoding='utf-8'))
    extra = set(d) - set(en); miss = set(en) - set(d)
    if extra or miss: print(lang, 'keys: missing', sorted(miss), 'extra', sorted(extra)); bad += 1
    for k, v in en.items():
        if k not in d: continue
        a = sorted(TAG.findall(v['en'])); b = sorted(TAG.findall(d[k]))
        if a != b: print(lang, k, 'TAGS DIFFER\n  en:', a, '\n  xx:', b); bad += 1
print('ALL UNITS OK' if not bad else f'{bad} problem(s)')
sys.exit(1 if bad else 0)
