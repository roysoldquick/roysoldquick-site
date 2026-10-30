# Weekly Market Update: how to write and publish one

Roy Quick (Realtor®, LUXRE Realty, CA DRE #02417080) publishes one Market Update every
Monday at 12:00 noon Pacific. This guide is the brief for whoever writes it, human or Claude.

## Schedule and approval

1. **Draft** (Friday): research, write the post in `content/posts/`, keep `"draft": true`,
   run `python3 scripts/build.py --drafts` to check it renders, push to a `draft/<slug>`
   branch, and email the full draft (`python3 scripts/draft_email.py <post file>` prints the email HTML) to roy@roysoldquick.com with the subject
   `Market Update draft for <Monday date>: reply "post it" to approve`.
2. **Approval**: Roy replies "post it" (or sends edits). Apply any edits he asks for.
3. **Publish** (Monday 12:00 PT): only if Roy approved, set `"draft": false`, run
   `python3 scripts/build.py`, merge to `main`. Netlify publishes automatically.
   No approval means no post; email Roy that it is waiting.

## Research checklist (always cite every number)

- San Clemente and Dana Point: Redfin city housing-market pages (median sale price, YoY,
  homes sold, days on market, sale-to-list). Note Redfin's time window as stated on the page.
- Single-family detail: California Regional MLS (CRMLS) data via InfoSparks when available.
- Orange County: C.A.R. monthly sales and price report (released mid-month), and the weekly
  Orange County Housing Report (ocrealestateinc.com) for inventory and pending sales.
- Rates: Freddie Mac PMMS (freddiemac.com/pmms), published Thursdays.
- Local news: City of San Clemente news flash, Dana Point Times, San Clemente Times, OC Register,
  OCFA. Anything that affects homeowners: fires, zoning/housing element, coastal rail and beach
  sand projects, new developments, school news, events.
- Never invent a number. If a source is unclear, leave the number out. Put every source in
  the `sources` list, and say "my own math" for any calculation.

## Voice

First person, friendly, local, honest. Roy specializes in sellers (selling or leasing their
home), loves working with investors, and is good with numbers: show the math in real dollars.
Never mention a finance or lending background. No hype, no guarantees, no fear-mongering.
Sign off "Talk soon, Roy". Keep it 900 to 1,400 words.

## SEO rules

- Title pattern: `<Town> Housing Market Update: <Month Year>` or a sharper news angle, always
  with "San Clemente", "Dana Point" or "South OC" in it. `seo_title` can be longer (under 70 chars).
- `description`: 140 to 160 characters, includes a number and "Roy Quick".
- `keywords`: 8 to 12, always including "San Clemente real estate", "Roy Quick Realtor",
  and the towns covered. Rotate in: Capistrano Beach, San Juan Capistrano, Laguna Niguel,
  Rancho Mission Viejo, Talega, Forster Ranch, Monarch Beach, Dana Point Harbor.
- Use the town names naturally in H2 headings. Link to `/#expired` or `/#contact` once.
- 3 to 5 FAQ entries phrased the way people search ("Is now a good time to sell in ...?").
  These feed Google and AI answers.
- Slug: lowercase words with hyphens, include the town and month.

## Photos

Free stock photos only, from Unsplash (free Unsplash License, not Unsplash+). Hotlink
`images.unsplash.com/photo-...` URLs, and always credit the photographer with a link to the
photo page. Prefer photos tagged San Clemente, Dana Point, Capistrano Beach or Orange County.
Hero photo plus one or two in-body `<figure>`s. Write real alt text describing the photo.

## Post file format

`content/posts/YYYY-MM-DD-slug.html`: a JSON header inside `<!-- -->`, then the body HTML.
See the October 26, 2026 post for every field. Body helpers:

- `<div class="tldr">` short-version box at the top
- `<div class="stats">` three stat tiles (`<b>`, `<span>`, `<em>` for the source)
- `<table class="tbl">` inside `<div class="tblwrap">` for comparisons
- `<!-- CTA -->` drops in the "Want these numbers for your street?" call box
- FAQ, sources, author box, contact form and related posts are added automatically.
