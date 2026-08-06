#!/usr/bin/env python3
"""Render template.html + content/<lang>.json -> public/[lang/]index.html"""
import json, os, re, sys

BUILD = '/home/claude/work/build'
PUB = '/home/claude/work/public'

LANGS = {
    'en': dict(locale='en_US', name='English',    audio='en'),
    'fr': dict(locale='fr_FR', name='Français',   audio='fr'),
    'de': dict(locale='de_DE', name='Deutsch',    audio='de'),
    'es': dict(locale='es_ES', name='Español',    audio='en'),
    'it': dict(locale='it_IT', name='Italiano',   audio='it'),
    'pt': dict(locale='pt_PT', name='Português',  audio='en'),
    'pl': dict(locale='pl_PL', name='Polski',     audio='pl'),
    'ru': dict(locale='ru_RU', name='Русский',    audio='en'),
}
ORDER = ['en', 'fr', 'de', 'es', 'it', 'pt', 'pl', 'ru']
BASE = 'https://colmartour.com'
# internal paths that must NOT be language-prefixed
KEEP = re.compile(r'^/(img/|favicon|robots|sitemap|llms|' + '|'.join(ORDER) + r')(/|\.|$)')

tpl = open(f'{BUILD}/template.html', encoding='utf-8').read()


def langnav(cur):
    out = []
    for l in ORDER:
        href = '/' if l == 'en' else f'/{l}/'
        on = ' class="on"' if l == cur else ''
        out.append(f'<a{on} href="{href}">{l.upper()}</a>')
    return '<nav class="lang">' + ''.join(out) + '</nav>'


def prefix_links(html, lang):
    if lang == 'en':
        return html
    def rep(m):
        q, path = m.group(1), m.group(2)
        if path == '/':
            return f'href={q}/{lang}/{q}'
        if KEEP.match(path):
            return m.group(0)
        return f'href={q}/{lang}{path}{q}'
    return re.sub(r'href=(["\'])(/[^"\']*)\1', lambda m: rep(m), html)


def render(lang):
    data = json.load(open(f'{BUILD}/content/{lang}.json', encoding='utf-8'))
    en = json.load(open(f'{BUILD}/content/en.json', encoding='utf-8'))
    cfg = LANGS[lang]
    out = tpl
    missing = []
    for k in en:
        v = data.get(k)
        if isinstance(v, dict):
            v = v.get('loc') or v.get('en')
        if not v:
            missing.append(k)
            v = en[k]['en']
        out = out.replace('{{%s}}' % k, v)
    out = (out.replace('{{LANG}}', lang)
              .replace('{{OG_LOCALE}}', cfg['locale'])
              .replace('{{CANONICAL}}', BASE + ('/' if lang == 'en' else f'/{lang}/'))
              .replace('{{LANGNAV}}', langnav(lang))
              .replace('{{AUDIO_SRC}}',
                       f"https://touringbee.com/wp-content/uploads/colmart1_{cfg['audio']}_intro.mp3"))
    out = prefix_links(out, lang)
    d = PUB if lang == 'en' else f'{PUB}/{lang}'
    os.makedirs(d, exist_ok=True)
    open(f'{d}/index.html', 'w', encoding='utf-8').write(out)
    left = re.findall(r'\{\{[A-Z0-9_]+\}\}', out)
    return len(missing), missing[:5], set(left)


if __name__ == '__main__':
    targets = sys.argv[1:] or ORDER
    for l in targets:
        if not os.path.exists(f'{BUILD}/content/{l}.json'):
            print(f'{l}: NO CONTENT FILE — skipped')
            continue
        n, sample, left = render(l)
        flag = 'OK' if not n and not left else 'CHECK'
        print(f'{l}: {flag}  missing={n} {sample if sample else ""} unresolved={left if left else "-"}')
