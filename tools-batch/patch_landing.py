#!/usr/bin/env python3
"""Landing pages (8 languages) + llms.txt: bring product facts in line with the approved articles (23.10.2026).
- audio languages: 7 (EN, FR, DE, IT, PL, ES, RU); only Portuguese has no audio
- "narrated by a professional historian" -> "route and texts prepared by professional authors"
- Studio Ghibli: no claim that a house inspired a film -> "how the town is connected to Japanese animation"
- ES/RU: own-language intro recording (colmart1_es_intro-1.mp3, colmart1_ru_intro-1.mp3), texts that said "no Spanish/Russian audio" fixed
Idempotent: a replacement whose new text is already present is skipped. Run from the repo root.
"""
import os, sys
PUB = 'public'
R = {
'en': [
 ("which house inspired a Studio Ghibli film", "how the town is connected to Japanese animation"),
 ("27 audio stops narrated by a professional historian", "27 audio stops · route and texts prepared by professional authors"),
 ("English, French, German, Italian and Polish", "English, French, German, Italian, Polish, Spanish and Russian"),
],
'fr': [
 ("quelle maison a inspiré un film du Studio Ghibli", "quel lien unit la ville à l'animation japonaise"),
 ("27 étapes audio racontées par un historien professionnel", "27 étapes audio · itinéraire et textes préparés par des auteurs professionnels"),
 ("Français, anglais, allemand, italien et polonais", "Français, anglais, allemand, italien, polonais, espagnol et russe"),
 ("français, anglais, allemand, italien et polonais", "français, anglais, allemand, italien, polonais, espagnol et russe"),
],
'de': [
 ("welches Haus einen Studio-Ghibli-Film inspiriert hat", "was die Stadt mit japanischen Animationsfilmen verbindet"),
 ("27 Stationen, gesprochen von einem Historiker", "27 Stationen · Route und Texte von professionellen Autoren erstellt"),
 ("Deutsch, Englisch, Französisch, Italienisch und Polnisch", "Deutsch, Englisch, Französisch, Italienisch, Polnisch, Spanisch und Russisch"),
],
'es': [
 ("qué casa inspiró una película del Studio Ghibli", "qué relación tiene la ciudad con la animación japonesa"),
 ("27 paradas narradas por un historiador profesional", "27 paradas · ruta y textos preparados por autores profesionales"),
 ("Audio en inglés, francés, alemán, italiano y polaco. En español no está disponible.", "Audio en español, inglés, francés, alemán, italiano, polaco y ruso."),
 ("En inglés, francés, alemán, italiano y polaco. En español no está disponible: esta página está en español, pero el audio no, y no hay versión española prevista. Eliges el idioma al comprar.", "En español, inglés, francés, alemán, italiano, polaco y ruso. Eliges el idioma al comprar."),
 ("En inglés, francés, alemán, italiano y polaco. En español no está disponible. Eliges el idioma al comprar.", "En español, inglés, francés, alemán, italiano, polaco y ruso. Eliges el idioma al comprar."),
 ("en inglés, francés, alemán, italiano y polaco.\"", "en español, inglés, francés, alemán, italiano, polaco y ruso.\""),
 ("Un minuto de la primera pista: esta es la voz que te acompañará todo el paseo. Y está en inglés. La audioguía existe en inglés, francés, alemán, italiano y polaco; en español no hay versión, así que lo que vas a oír ahora suena en inglés.", "Un minuto de la primera pista, en español: así suena la audioguía que te acompañará todo el paseo."),
 ("sin conexión · en inglés</span>", "sin conexión · en español</span>"),
 ("colmart1_en_intro.mp3", "colmart1_es_intro-1.mp3"),
],
'it': [
 ("quale casa ha ispirato un film dello Studio Ghibli", "che legame ha la città con l'animazione giapponese"),
 ("27 tappe audio, raccontate da uno storico di mestiere", "27 tappe audio · percorso e testi curati da autori professionisti"),
 ("Italiano, inglese, francese, tedesco e polacco", "Italiano, inglese, francese, tedesco, polacco, spagnolo e russo"),
 ("italiano, inglese, francese, tedesco e polacco", "italiano, inglese, francese, tedesco, polacco, spagnolo e russo"),
],
'pt': [
 ("que casa inspirou um filme do Studio Ghibli", "que ligação tem a cidade à animação japonesa"),
 ("27 paragens áudio narradas por um historiador profissional", "27 paragens áudio · percurso e textos preparados por autores profissionais"),
 ("inglês, francês, alemão, italiano e polaco", "inglês, francês, alemão, italiano, polaco, espanhol e russo"),
],
'pl': [
 ("który dom trafił do filmu Studio Ghibli", "co łączy miasto z japońską animacją"),
 ("27 nagrań, które czyta zawodowy historyk", "27 nagrań · trasa i teksty przygotowane przez profesjonalnych autorów"),
 ("Po polsku — a także po angielsku, francusku, niemiecku i włosku", "Po polsku — a także po angielsku, francusku, niemiecku, włosku, hiszpańsku i rosyjsku"),
 ("olsku, angielsku, francusku, niemiecku i włosku", "olsku, angielsku, francusku, niemiecku, włosku, hiszpańsku i rosyjsku"),
],
'ru': [
 ("какой дом попал в мультфильм Studio Ghibli", "как город связан с японской анимацией"),
 ("27 остановок, озвучил профессиональный историк", "27 остановок · маршрут и тексты подготовлены профессиональными авторами"),
 ("Пять языков озвучки: английский, французский, немецкий, итальянский и польский. Русского среди них нет.", "Семь языков озвучки: русский, английский, французский, немецкий, итальянский, польский и испанский."),
 ("На пяти: английском, французском, немецком, итальянском и польском. Язык выбираете при покупке. Русской озвучки нет — на русском гид не выходил.", "На семи: русском, английском, французском, немецком, итальянском, польском и испанском. Язык выбираете при покупке."),
 ("На пяти: английском, французском, немецком, итальянском и польском. Язык выбираете при покупке. Русской озвучки нет.", "На семи: русском, английском, французском, немецком, итальянском, польском и испанском. Язык выбираете при покупке."),
 ("Озвучка на английском, французском, немецком, итальянском и польском; русской версии нет.", "Озвучка на русском, английском, французском, немецком, итальянском, польском и испанском."),
 ("Минута из первой дорожки — этот голос будет с вами всю прогулку. Отрывок звучит на английском: русской озвучки у гида нет.", "Минута из первой дорожки на русском — этот голос будет с вами всю прогулку."),
 ("офлайн · на английском</span>", "офлайн · на русском</span>"),
 ("colmart1_en_intro.mp3", "colmart1_ru_intro-1.mp3"),
],
}
LLMS = [("in English, French, German, Italian and Polish.", "in English, French, German, Italian, Polish, Spanish and Russian (no Portuguese audio).")]
bad = 0
def patch(path, reps):
    global bad
    s = open(path, encoding='utf-8').read(); n0 = s
    for a, b in reps:
        if a in s:
            s = s.replace(a, b)
        elif b not in s:
            print(f'{path}: NOT FOUND: {a[:70]}'); bad += 1
    if s != n0:
        open(path, 'w', encoding='utf-8').write(s); print(f'{path}: patched')
    else:
        print(f'{path}: unchanged')
for lang, reps in R.items():
    patch(os.path.join(PUB, 'index.html' if lang == 'en' else f'{lang}/index.html'), reps)
patch(os.path.join(PUB, 'llms.txt'), LLMS)
sys.exit(1 if bad else 0)
