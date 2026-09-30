# Статья №3 «Рождественские рынки рядом с Кольмаром» — сборка на 8 языках

Слаг: `christmas-markets-near-colmar`. Тексты: RU v6, EN/FR/DE/ES/IT/PL v2, PT v2 без «11:00 em Lisboa».

## Что в архиве

```
build-art-christmas-markets-near-colmar/   сборка статьи (article-en.html, template-art.html, content/*.json, скрипты)
public/                 8 готовых страниц /christmas-markets-near-colmar/ и /<lang>/christmas-markets-near-colmar/
patch/
  integrate_article3.py  разовая интеграция: пункт меню и подвала на лендинге, в №1 и в №2 (ключи M003/M004),
                         слаг в PUBLISHED, 8 URL в sitemap.xml. Можно запускать повторно.
  build_guides.py        /guides/ с карточками №3, №2, №1 (заменяет build-art/build_guides.py)
  validate_all.py        проверка всех трёх статей (заменяет build-art/validate_all.py)
```

## Как встроить (из корня репозитория)

1. Скопировать `build-art-christmas-markets-near-colmar/` в корень, рядом с `build/`, `build-art/` и папкой №2.
2. Заменить `build-art/build_guides.py` и `build-art/validate_all.py` файлами из `patch/`.
3. `python3 patch/integrate_article3.py`
4. Пересобрать:
   ```
   python3 build/render.py
   python3 build-art/render_art.py
   python3 build-art-colmar-vs-strasbourg-christmas/render_art.py
   python3 build-art-christmas-markets-near-colmar/render_art.py
   python3 build-art/build_guides.py
   python3 build-art/validate_all.py      # должно быть ALL PAGES PASS
   ```

Статья проверена: `validate_all.py --articles-only` → ALL PAGES PASS.

## Что проверить перед деплоем

- Фото деревень нет; в статье только карточка продукта. Карточка на /guides/ временно использует `/img/tile-christmas-market.webp`.
- В hero вместо GYG стоит кнопка на официальную страницу шаттлов (партнёрской ссылки GYG нет).
- sitemap.xml — скрипт добавляет простые `<url><loc>`; если в файле есть `xhtml:link`, дописать по образцу.

## Изменение в validate_all.py

Проверка «euro symbol before amount» идёт по отдельным текстовым узлам: соседние ячейки таблицы («8 €» | «17 €») раньше склеивались и давали ложную ошибку.
