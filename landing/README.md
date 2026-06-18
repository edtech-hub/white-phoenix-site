# Niche landing-page system

Spin up a customized, conversion-focused landing page for any campaign niche
from one shared design. Pages are **fully static HTML** (own `<title>`,
meta description and Open Graph tags) so they deploy on GitHub Pages and render
correct previews when you drop the link into an SMS / iMessage / WhatsApp blast.

```
landing/
  build.py                       # the generator (design lives here, edit rarely)
  niches/
    event-planners.json          # ← all copy for one niche
    event-planners.demo.html     # ← the product mockup ("screenshot") for that niche
  README.md
lp/
  event-planners.html            # ← GENERATED — the page you actually send
```

Live URL pattern: `https://whitephoenixconsulting.com/lp/<slug>.html`

## Build

```bash
python3 landing/build.py                 # build every niche in niches/
python3 landing/build.py event-planners  # build just one
```

Then commit & push `lp/` — GitHub Pages serves it.

## Add a new niche (≈10 minutes)

1. **Copy the config:**
   `cp landing/niches/event-planners.json landing/niches/<your-slug>.json`
2. **Edit the copy.** Change `slug`, `meta.title/description`, hero, problem
   pains, steps, why, compare, faqs, final CTA. Keep the same JSON shape — every
   field maps to a section. The `form.access_key` posts leads to the
   Web3Forms inbox (currently → aditya@edastra.in); change `form.subject` so you
   can tell which niche a lead came from.
3. **Make the demo mockup.**
   `cp landing/niches/event-planners.demo.html landing/niches/<your-slug>.demo.html`
   and edit it to show *that* niche's product. Point `demo.partial` in the JSON
   at the new file. All mockup classes are prefixed `gq-` and scoped, so you can
   restyle freely without touching page CSS.
4. **Build & preview:**
   `python3 landing/build.py <your-slug>` then open `lp/<your-slug>.html`.
5. **Ship:** commit `landing/niches/<slug>.*` + `lp/<slug>.html`, push, send the link.

## What's shared vs. per-niche

| Shared (in `build.py`) | Per-niche (in `niches/`) |
|---|---|
| Page structure & section order | All headlines & body copy |
| CSS theme (flame/ember), buttons, nav | Stats, pain points, FAQs |
| Animations, FAQ accordion, mobile nav | The product mockup / "screenshot" |
| Lead form → Web3Forms wiring | Form subject line & meta/OG tags |

Change the design once in `build.py` and **every** niche page updates on the
next build — that's the point of the system.

## Notes for US campaigns
- Copy is Americanized (customize, catalog, sales tax, gratuity, `$`, per-guest).
- The lead form is the primary CTA (the product/booking link isn't live yet).
  When you have a scheduler, swap the `#book` form for your Calendly link in
  `build.py` and rebuild all niches at once.
- OG image currently reuses the site's `og-image.png`. For best SMS previews,
  generate a per-niche 1200×630 image and point `meta.og_image` at it.
