# Статья №2 «Кольмар или Страсбург на Рождество» — сборка на 8 языках

Слаг: `colmar-vs-strasbourg-christmas`. Основа — утверждённый RU-черновик v4 (с двумя правками фактчека).
EN-мастер написан заново на американском английском, остальные языки локализованы с EN по BRIEF-ART.

## Что в архиве

```
build-art-colmar-vs-strasbourg-christmas/   сборка статьи №2 (копия build-art, SLUG заменён)
  article-en.html      английский мастер
  template-art.html    шаблон (собран extract_art.py)
  content/*.json       строки на 8 языках, 155 ключей, check_units: ALL UNITS OK
  extract_art.py  render_art.py  check_units.py  validate_all.py (v2)
public/                 8 готовых страниц: /colmar-vs-strasbourg-christmas/ и /<lang>/colmar-vs-strasbourg-christmas/
patch/
  integrate_article2.py  разовая интеграция в существующие исходники
  build_guides.py        v2: карточка на каждую статью (заменяет build-art/build_guides.py)
  validate_all.py        v2: проверяет обе статьи (заменяет build-art/validate_all.py)
```

## Как встроить (из корня репозитория)

1. Скопировать `build-art-colmar-vs-strasbourg-christmas/` в корень, рядом с `build/` и `build-art/`.
2. Заменить `build-art/build_guides.py` и `build-art/validate_all.py` файлами из `patch/`.
3. `python3 patch/integrate_article2.py` (подписи меню и подвала берёт из статьи №2 по тексту, не по номерам ключей) — добавит пункт меню и подвала в шаблоны лендинга и статьи №1
   (новые ключи M001/M002, старые T-ключи не трогаются), слаг в PUBLISHED, 8 URL в sitemap.xml.
4. Пересобрать:
   ```
   python3 build/render.py
   python3 build-art/render_art.py
   python3 build-art-colmar-vs-strasbourg-christmas/render_art.py
   python3 build-art/build_guides.py
   python3 build-art/validate_all.py      # должно быть ALL PAGES PASS
   ```

Статья №2 сама по себе проверена: `validate_all.py --articles-only` → ALL PAGES PASS (8 страниц).
Полный прогон по всему сайту я сделать не мог — у меня нет лендинга, статьи №1 и картинок.

## Что проверить перед деплоем

- **Ссылка на страсбургский аудиогид** `https://touringbee.com/product/city-tour-of-strasbourg/` — не сверена, поправить в article-en.html (callout) и пересобрать.
- **sitemap.xml** — скрипт добавляет простые `<url><loc>`; если в файле есть `xhtml:link`-альтернативы, дописать по образцу.
- **Шаблон лендинга**: скрипт ищет две ссылки на `/colmar-christmas-market/` с `{{T…}}` (меню и подвал). Если не найдёт — скажет, что добавить руками.
- **Подписи меню/подвала** на 7 языках написаны заново; в статье №1 они могли быть переведены иначе («Guides ▾» → «Ratgeber ▾» и т.п.). Для единообразия можно взять строки из build-art/content.
- **Карточка на /guides/** использует `/img/tile-little-venice.webp` — своей картинки у статьи нет.
- Ссылки на статью №3 нет — добавить, когда её опубликуем.
- Часы шале Страсбурга (21:00) даны со ссылкой на официальный сайт (FAQ без года), в T056.

## Решения, которые стоит знать

- EN: американская орфография и формат дат (November 23); время — 24-часовое, как на всём сайте.
- Цены вне EN: «9,99 €» — так требует validate_all.py («euro symbol before amount» = ошибка). В BRIEF-ART пример «€9,99» с этим расходится.
- PT: в карточке продукта прямо сказано, что португальской озвучки нет; в липкой плашке — «áudio em 7 línguas».
- Статья не зависит от дат Страсбурга: даты и часы есть только у Кольмара-2026 (раздел «Christmas 2026 in Colmar», таблица + абзац «Between Christmas and New Year», пункт «Traveling between Christmas and New Year», FAQ про 25 декабря). Для Страсбурга — отсылка к noel.strasbourg.eu. На следующий сезон обновлять только кольмарские строки.
- Блок аудиогидов — две одинаковые карточки (Кольмар / Страсбург): остановки · время · цена, одна строка о маршруте, кнопка.
- Локализации не вычитаны носителями.
