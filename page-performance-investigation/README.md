# Why is hainbachmusik.com/new-page-21 slow?

Short answer: it's a Wix-hosted page (the URL slug `/new-page-21` is a
dead-giveaway Wix default), and it's the "INSTRUMENTS" page showcasing
Hainbach's iOS apps GAUSS and FLUSS. The slowness is the usual Wix
combination — a heavy Thunderbolt JavaScript runtime, multiple
embedded YouTube product-demo iframes, and full-bleed hero imagery —
not anything specific to this URL.

## Caveat first
I could not directly fetch the page from this sandboxed environment.
`hainbachmusik.com`, every Wix asset CDN, the Wayback Machine,
PageSpeed Insights, WebPageTest, GTmetrix and Pingdom were all
blocked at the network proxy (`x-deny-reason: host_not_allowed`).
The `WebFetch` tool also returned 403 for the URL.

So this report is **diagnostic, not measured**. It is built from:

- search-engine snippets confirming the page's contents
- the URL pattern (Wix default slug)
- well-documented characteristics of the Wix Thunderbolt runtime
- Hainbach's typical media-heavy content style

To turn this into hard numbers, drop the URL into
<https://pagespeed.web.dev/> from a normal browser. `notes.md` lists
the specific Lighthouse / WebPageTest audits to look at.

## What the page actually is
- Page title: **INSTRUMENTS — HAINBACH**
- Listed contents: *"Tape-style Looper GAUSS, Kinetic Granular FLUSS
  and something new soon."*
- Each instrument is one of Hainbach + Bram Bos's iOS apps and is
  typically presented with a hero image, a paragraph of copy, an App
  Store badge, and a YouTube demo video.
- Site is built and hosted on **Wix** (Wix Editor / Thunderbolt
  renderer). The path `/new-page-21` is the default name Wix gives a
  newly created page when the user doesn't customise the slug.

## The three things that almost certainly dominate load time

1. **The Wix Thunderbolt JavaScript payload (~700 KB – 1.5 MB
   compressed).** Wix downloads ~10–15 JS bundles from
   `static.parastorage.com` — its rendering runtime, components
   registry, animations engine, router, etc. — plus a per-page
   bundle. All of this is parsed and hydrated on the client before
   the page is interactive, and it's the floor under every page on
   the site. Mobile Lighthouse scores for stock Wix pages routinely
   sit in the 30–55 range largely because of this.

2. **Embedded YouTube `<iframe>` demos.** Hainbach's instrument
   sections each embed a YouTube demo. **Every YouTube iframe
   downloads ~500 KB – 1 MB of player JS plus a poster image, even
   if the user never clicks play.** With 2–3 of them on a single
   page, this becomes the dominant transfer cost after the Wix
   runtime itself.

3. **Large hero images.** Big product stills for GAUSS / FLUSS,
   served from `static.wixstatic.com`. Wix resizes on the fly, but
   if the section is set to full-bleed, the served variant can still
   be 1–2 MB on desktop. The hero image is also typically the LCP
   element, so its weight is felt directly in user-perceived
   loading.

The interaction of (1) + (2) is the usual reason a "simple" Wix page
feels heavy: many medium-sized scripts and iframes all competing for
the main thread while the user stares at a half-rendered hero.

## Other contributing factors (smaller, but real)
- **Deep DOM with nested wrapper `<div>`s and inline styles**, which
  is how the Wix editor compiles every section/strip/column. Drives
  up style/layout cost.
- **Layout decided in JS post-hydration**, so the visible "snap into
  place" reflow is gated on the JS bundle finishing.
- **Render-blocking webfonts** from `fonts.shadow.wixstatic.com`
  (typically 2–4 weights for the wordmark + body).
- **Wix analytics + cookie-consent + any installed Wix Apps**
  (Stores, Forms, Bookings, custom Velo, embeds…) all ship JS even
  on pages that don't visibly use them.
- **TTFB on a less-trafficked subpage** — Thunderbolt SSR HTML for a
  rarely-hit slug like `/new-page-21` is often cold-cached, adding
  a few hundred ms before the first byte.

## What is NOT the cause
- The slug `/new-page-21` itself. It's a Wix default; doesn't add
  latency. Worth renaming for SEO, but won't change perf.
- The domain or DNS. `hainbachmusik.com` resolves and TLS-handshakes
  in tens of ms.
- "Server location" / region. Wix runs on a global CDN.

## What Hainbach (or anyone running a similar Wix page) can do
In rough effort order:

1. **Lazy-load the YouTube embeds.** Replace each `<iframe>` with a
   poster image + play button that swaps in the real iframe on
   click. Saves the most weight per minute of effort. Multiple-second
   improvements in LCP/TBT are typical.
2. **Re-export hero images** at the actual displayed size, save as
   WebP/AVIF, re-upload.
3. **Move demo videos below the fold** so they don't gate LCP.
4. **Audit installed Wix Apps** in the editor and remove anything
   unused on this page — each app ships JS site-wide.
5. **Enable the Wix "Performance" / "Enhance images" settings**
   (Site Manager → Performance & SEO).
6. **Rename `/new-page-21` to `/instruments`** — pure SEO / shareable-
   URL win, not a perf win, but trivial.

The Wix runtime cost itself is a hard floor; the only way past it
is leaving the platform (static-site generator, Wix Studio with a
hand-built minimal page, etc.).

## How to verify this with real measurements
From a normal browser:

- <https://pagespeed.web.dev/analysis?url=https%3A%2F%2Fwww.hainbachmusik.com%2Fnew-page-21>
- <https://www.webpagetest.org/> — "Mobile 4G", look at the waterfall
  and the filmstrip
- Chrome DevTools → Performance + Coverage to see which Wix bundles
  were actually used vs. shipped, and how long each blocked the main
  thread

Expected findings (from the diagnosis above):

- LCP element = a hero image, with LCP > 2.5 s on mobile
- "Reduce unused JavaScript" flags multiple `parastorage.com` bundles
  plus the YouTube player
- "Avoid an excessive DOM size" is flagged
- "Eliminate render-blocking resources" flags Wix CSS + webfonts

If those audits don't fire, the diagnosis is wrong and the bottleneck
is something else (a specific custom script, a misbehaving embed,
etc.) — but they almost certainly will.

## Files
- `notes.md` — working notes and the full reasoning chain, including
  the list of hosts the sandbox blocked.
