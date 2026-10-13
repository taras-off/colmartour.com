# Статья №9 «Кольмар с детьми» (/colmar-with-kids/) — файлы для сайта, 13.10.2026

## Что загрузить на GitHub (taras-off/colmartour.com)
Архив повторяет структуру корня репозитория. Папки `public/`, `build-art-colmar-with-kids/`, `tools-batch/` перетащить в корень репо (Add file → Upload files): GitHub разложит файлы по тем же путям и заменит существующие. Новых папок в корне не появится, кроме build-art-colmar-with-kids (как у других статей).

В public/:
- НОВЫЕ: `public/colmar-with-kids/index.html` и `public/{fr,de,es,it,pt,pl,ru}/colmar-with-kids/index.html` (8 страниц)
- ЗАМЕНИТЬ: `public/guides/index.html` и `public/{fr,de,es,it,pt,pl,ru}/guides/index.html` (новая карточка первой)
- ЗАМЕНИТЬ: `public/sitemap.xml` (+8 URL с hreflang, всего 88)
Остальные файлы сайта не тронуты.

## Исходники
- `build-art-colmar-with-kids/` — md ×8 (финальные тексты без служебных блоков и тегов источников), content/*.json, шаблон, render_art.py
- `tools-batch/` — make_batch.py (+ слаг №9, отложенные ссылки, блок «Читать дальше» при сборке), integrate_batch.py, validate_all.py

Пересборка: `python3 tools-batch/make_batch.py colmar-with-kids && (cd build-art-colmar-with-kids && python3 render_art.py) && python3 tools-batch/integrate_batch.py && python3 tools-batch/validate_all.py`

## Важно
- Ссылки на «Маленькую Венецию» (/petite-venise-colmar/, №10) и «целый день» (/one-day-in-colmar/, №11) пока выводятся обычным текстом — этих страниц ещё нет. После публикации №10/№11 убрать пути из PENDING в make_batch.py и пересобрать №9.
- [LINK №22] — обычный текст, маркер не публикуется.
- Картинка карточки/og: tile-canal-day.webp (та же, что у «Когда ехать»). Нужна своя фотография — заменить в ARTS и integrate_batch.py.
- Проверка: validate_all — только 7 известных ошибок hreflang статьи №1, по №9 ошибок нет.
