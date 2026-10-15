# Статья №10 «Что посмотреть в Кольмаре» (/things-to-do-in-colmar/) — файлы для сайта, 15.10.2026

Архив повторяет корень репозитория. Перетащите папки `public/`, `build-art-things-to-do-in-colmar/`, `tools-batch/` в корень репо (Add file → Upload files) — файлы лягут по тем же путям, существующие заменятся.

В public/ (17 файлов):
- НОВЫЕ: public/things-to-do-in-colmar/index.html и public/{fr,de,es,it,pt,pl,ru}/things-to-do-in-colmar/index.html
- ЗАМЕНИТЬ: public/guides/index.html и public/{fr,de,es,it,pt,pl,ru}/guides/index.html (карточка №10 первой)
- ЗАМЕНИТЬ: public/sitemap.xml (+8 URL, всего 96)

Исходники: build-art-things-to-do-in-colmar/ (md ×8 из финальных версий, content, шаблон, render_art.py) и tools-batch/ (make_batch.py с №10, integrate_batch.py, validate_all.py).

Важно:
- Ссылки на /petite-venise-colmar/, /one-day-in-colmar/, /colmar-walking-tour/ выводятся обычным текстом, пока этих страниц нет (список PENDING в make_batch.py). После публикации — убрать путь из PENDING и пересобрать №9 и №10.
- Картинка карточки и og: tile-old-town.webp (та же, что у «Стоит ли ехать в Кольмар»). Нужна своя фотография.
- В RU-тексте абзац про Доминиканскую церковь отделён от абзаца про Унтерлинден, как в EN и остальных языках (иначе не совпадала структура страниц).
- Проверка: validate_all — только 7 известных ошибок hreflang в статье №1.
