# ColmarTour — localization brief (all languages)

You are localizing the ColmarTour landing page (colmartour.com) from English.

## Rule #1 — LOCALIZE, DO NOT TRANSLATE

We do not translate words. We retell the meaning and the feeling the way a real
local author-guide would say it in that language. A good localized text reads as
if it was written in that language from the start.

Test: read the sentence aloud. Bored, stumbled, yawned? Cut it and rewrite. If you
can delete a word and the meaning survives — delete it.

A literal translation is a failed deliverable. Nothing else in this brief matters
as much as this.

## Voice

- A knowledgeable guide-friend telling you this at the bar. Warm, curious, to the
  point. Not a museum label, not a brochure, not Wikipedia.
- Confident and concrete. No "perhaps", "it is generally considered", "it should
  be noted that".
- Lead the reader: "imagine", "step out onto the terrace", "don't leave without…".
- A little character and light irony is welcome. Pathos and stock phrases are not.

## Rhythm — this is what kills boring text

- Short sentences. A long sentence with 3–4 subordinate clauses → break into 2–3.
- Vary length. Long — short — medium. A short sentence lands.
- One thought per sentence.
- Paragraphs of 2–4 sentences. Give it air.
- Cut filler: "in fact", "in general", "it is", "represents", "one should note".

## Verbs, not nouns. Active, not passive.

- "tickets can be purchased online" → "book tickets online"
- "the terrace is a place from which a view opens" → "from the terrace you see the
  whole valley"

## Show, don't tell

Replace judgements ("beautiful", "impressive") with a concrete fact-picture the
reader draws their own conclusion from.

## Openings

No warm-up. Never start with "Colmar is…". Enter through a story, a detail, a
paradox, a question. The first one or two sentences decide whether the rest is read.

## Cliché ban-list

English source clichés to never reproduce: nestled, hidden gem, must-see, boasts,
in the heart of, stunning/breathtaking on every line, picture-perfect, steeped in
history, a feast for the senses.

Each language has its own tired travel clichés — see your language section below.
If you cannot say "beautiful" without a cliché, you need a concrete detail instead
of an adjective.

## SEO inside living language

- The primary keyword is NOT a literal translation of the English one. Use the
  phrase people in that market actually type. Put it in: SEO title, H1, meta
  description, first paragraph, and one H2. Naturally — no stuffing.
- H2 headings must be human and specific, never "Ticket information".
- SEO title ≤ 60 characters. Meta description ≤ 155 characters.

## Cultural adaptation

- Units, currency, dates and number formats to the target market. Metric and € stay.
- Decimal separator: every language here except English uses a COMMA — €9,99 not
  €9.99. Apply this everywhere the price appears, including button labels.
- Date format as written in that language (e.g. DE "23. November – 29. Dezember").
- Explain what your reader doesn't know, cut explanations they don't need. A French
  reader knows what a TGV is; a Polish or Portuguese reader may need a word.
- Idioms are never literal — use the target language's equivalent or drop it.
- Adapt humour and references; don't copy them.

## Names and terms

Never translate these — keep exactly as written:

TouringBee, Colmar, La Petite Venise, Musée Unterlinden, Musée Bartholdi, Maison
Pfister, Maison des Têtes, Marché Couvert, Koïfhus, Rue des Marchands, Quai de la
Poissonnerie, Parc du Champ de Mars, Bartholdi, Frédéric Auguste Bartholdi,
Johannes Roesselmann, Décapole, Isenheim Altarpiece (use the established name in
your language if one exists, e.g. Isenheimer Altar / Retable d'Issenheim),
Eguisheim, Riquewihr, Kaysersberg, Turckheim, GetYourGuide, Tiqets, Booking.com,
SNCF, Studio Ghibli, Statue of Liberty (established name in your language).

You may give a short in-language gloss on first mention, e.g. "La Petite Venise
(die Klein-Venedig-Ecke)".

City names take the established exonym in your language (Strasbourg, Paris, Basel)
— see your language section. Colmar stays Colmar everywhere.

For Russian: transliterate proper nouns on first mention with the original in
brackets, then transliteration only, declined naturally.

## Facts that must be carried across EXACTLY (do not "localize" these)

- Price: 9.99 EUR. One payment, no subscription.
- 27 audio stops. About 1.5 hours of walking and listening.
- 100% offline once downloaded.
- GPS wording, exactly this meaning: the offline map shows where you are; YOU start
  each track yourself when you reach the stop. (It does not auto-play.)
- iOS and Android. 1 year of access.
- **The audio guide exists in English, French, German, Italian and Polish.** Only
  those five. Do not add or remove languages from that list.
- Musée Unterlinden €14, Wed–Mon 9:00–18:00, closed Tuesdays, last entry 17:30.
- Musée Bartholdi Tue–Sun 10:00–12:00 and 14:00–18:00, closed Mondays.
- Christmas markets 2026: 23 November – 29 December, six markets.
- Paris Gare de l'Est → Colmar ~2h20 by TGV. Strasbourg ~30 min. Basel ~45 min.
- A full day with one museum and lunch: €40–60 per person.
- Rating 4.6/5. Over 1,000 travellers. 14 reviews shown.
- Colmar a free imperial city from 1226; besieged 1262; Bartholdi born 1834;
  Maison Pfister 1537; Maison des Têtes 105 carved faces; Marché Couvert 1865.

Numbers, prices, hours and dates are transferred precisely. Never round, never
"improve" them.

## The 14 reviews

These are real Tripadvisor and Viator reviews. Localize them into natural,
readable language — a stiff literal translation of a review reads as fake. But do
not invent, embellish, or strengthen an opinion. Keep every reservation the
reviewer expressed (battery life, GPS drift, wanting more anecdotes) exactly as
critical as it was.

Keep reviewer names, cities and dates as they are (localize the month name and the
words "Solo / Couples / Family").

In the rating-bar paragraph, add one short sentence in your language noting that
the reviews are shown translated from the original. This matters — it is the
honest framing and it is what Tripadvisor and Booking do.

## What you must NOT change

- Any HTML tag, attribute, class, id, href, target or rel inside a string. Keep
  `<a href="/alsace-wine-route/">…</a>` byte-identical except for the link text.
  Do not add the language prefix to hrefs — the build system does that.
- `&amp;` `&nbsp;` and other entities stay as they are.
- Placeholders like `{{…}}` — there are none in your input, but if you see one,
  leave it untouched.

## Output format

Write ONE file: `/home/claude/work/build/content/<LANG>.json`

A flat JSON object, every key from `en.json`, value = the localized string:

```json
{ "T001": "…", "T002": "…", "S01": "…" }
```

All 288 keys must be present. No `ctx` field, no nesting, no extra keys, no
trailing commas. UTF-8, real accented characters (not \u escapes).

Read `/home/claude/work/build/content/en.json` first — each entry has a `ctx`
field telling you where on the page it sits (`div.card > div.pad > h3`,
`schema FAQ answer`, `img alt`, `<title>`). Use it to judge length and register:
an `h3` must stay short, an `img alt` is a plain description, a `.btn` is a button
label of 2–5 words.

Verify before finishing: `python3 -c "import json;d=json.load(open('/home/claude/work/build/content/<LANG>.json'));print(len(d))"` must print 288.
