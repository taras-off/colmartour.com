#!/usr/bin/env python3
"""Social-preview meta for pages NOT built by make_batch (landing, /guides/, articles №2 and №3).
Sets og:image to a 1200x630 JPEG in /img/og/, adds og:image:width/height/type and twitter:image
(+ twitter:card on /guides/). Touches only <head> meta tags; idempotent. Run from repo root.
Article №1 (colmar-christmas-market) is maintained by another editor and is not touched."""
import os, re
PUB = os.path.join(os.getcwd(), 'public'); BASE = 'https://colmartour.com'
ORDER = ['en', 'fr', 'de', 'es', 'it', 'pt', 'pl', 'ru']
PAGES = {'': 'home', 'guides/': 'guides',
         'christmas-markets-near-colmar/': 'christmas-markets-near-colmar',
         'colmar-vs-strasbourg-christmas/': 'colmar-vs-strasbourg-christmas'}
def tag(attr, key, val): return f'<meta content="{val}" {attr}="{key}"/>'
for lang in ORDER:
    pre = '' if lang == 'en' else lang + '/'
    for path, og in PAGES.items():
        p = f'{PUB}/{pre}{path}index.html'
        h = open(p, encoding='utf-8').read()
        head, rest = h.split('</head>', 1)
        url = f'{BASE}/img/og/{og}.jpg'
        # drop previous social image tags, then add one clean block after og:url (or before </head>)
        head = re.sub(r'\s*<meta[^>]*(?:property="og:image(?::[a-z]+)?"|name="twitter:image")[^>]*/?>', '', head)
        block = ''.join('\n' + t for t in [tag('property', 'og:image', url), tag('property', 'og:image:width', '1200'),
                                           tag('property', 'og:image:height', '630'), tag('property', 'og:image:type', 'image/jpeg'),
                                           tag('name', 'twitter:image', url)])
        if 'twitter:card' not in head:
            block += '\n' + tag('name', 'twitter:card', 'summary_large_image')
        m = re.search(r'<meta[^>]*property="og:url"[^>]*/?>', head)
        head = head[:m.end()] + block + head[m.end():] if m else head + block + '\n'
        open(p, 'w', encoding='utf-8').write(head + '</head>' + rest)
print('social meta patched:', len(ORDER) * len(PAGES), 'pages')
