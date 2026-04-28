# Investigation notes — why is hainbachmusik.com/new-page-21 slow?

Date: 2026-04-28

## Goal
Explain why https://www.hainbachmusik.com/new-page-21 feels slow.

## Sandbox constraint (important caveat)
The sandbox blocks outbound traffic to almost every host on the public web:

```
hainbachmusik.com         -> 403 host_not_allowed (sandbox proxy)
static.wixstatic.com      -> 403 host_not_allowed
static.parastorage.com    -> 403 host_not_allowed
www.googleapis.com        -> reachable, but PageSpeed Insights API quota = 0
                             on this project (RESOURCE_EXHAUSTED)
web.archive.org           -> 403 host_not_allowed
www.webpagetest.org       -> 403 host_not_allowed
tools.pingdom.com         -> 403 host_not_allowed
www.gtmetrix.com          -> 403 host_not_allowed
developers.google.com     -> 403 host_not_allowed
publicwww.com             -> 403 host_not_allowed
WebFetch tool -> 403 for hainbachmusik.com (and the Wix asset CDNs)
```

So I cannot personally run a Lighthouse / WebPageTest against this URL,
nor view its HTML. Anything below is inferred from:

- Search-engine snippets that confirm the page contents
- The URL pattern (`/new-page-21`) which is a Wix default slug
- Public characteristics of Wix's "Thunderbolt" rendering platform
- Hainbach's known content style (hero images + YouTube demo videos
  for GAUSS, FLUSS, …)

If you want a precise number-by-number breakdown, run the URL through
https://pagespeed.web.dev/ from a normal browser - I cannot do that
from inside this sandbox.

## What's on the page (confirmed via search)
- Title: "INSTRUMENTS — HAINBACH"
- Listed items: "Tape-style Looper GAUSS, Kinetic Granular FLUSS and
  something new soon"
- Site is hainbachmusik.com, the personal site of the Berlin musician
  and YouTuber Hainbach (Stefan Paul Goetsch)
- Other pages on the same domain: /, /music-1, /news, /media,
  /sound-art, /live-1, /contact, /new-blog/...

The slug `/new-page-21` is the **default name** Wix gives a freshly
created page until the user renames it. It just means the page was
the 21st page added in the editor; it doesn't cause slowness on its
own.

## Why this kind of page is slow on Wix — the structural causes

### 1. Wix Thunderbolt ships a lot of JavaScript per page
Wix's current renderer ("Thunderbolt") is a React-based SSR platform
that re-hydrates every page on the client. A typical Wix page,
including this one, downloads:

- `~10–15 .js bundles` from `static.parastorage.com` (Thunderbolt
  runtime, viewer-platform-bridge, animations, tpa-router, components
  registry, css-mapper, etc.)
- a per-page `pages-<hash>.js` bundle
- the Wix client-side router so that internal nav can be SPA-style
- a separate bundle for any "Wix App" you embedded (Wix Stores, Wix
  Forms, Wix Bookings, custom Velo code, etc.)

In total this is on the order of **~700 KB – 1.5 MB compressed JS**
before the page is interactive. A lot of that JS executes at
parse/hydration time, blocking the main thread.

### 2. Heavy DOM with deep wrapper nesting
The Wix editor compiles every "section / strip / column / element"
into a tree of nested `<div>` wrappers with inline styles. A simple
page with five sections often renders >1500 DOM nodes. That makes
style recalc and layout passes expensive — the very things that drive
Total Blocking Time and Interaction-to-Next-Paint.

### 3. Layout decided in JS, after first paint
Thunderbolt does responsive sizing in the client. The result is a
visible reflow / "jump" once JS lands, and an LCP that is gated on the
JS bundle, not just on the hero image. This is the most common reason
people experience a "long blank → snap into place" load on Wix sites.

### 4. The instruments page is media-heavy
Confirmed contents are GAUSS, FLUSS, and "something new soon". On
Hainbach's site each instrument typically gets:

- a large hero / product still (uploaded original is often 2000px+
  and 500 KB – 2 MB before Wix CDN re-encodes it)
- a YouTube demo embed (each YouTube `<iframe>` adds ~500 KB to ~1 MB
  of player JS + a poster image, even if you never click play)
- App Store / Play Store badge images
- a paragraph of copy

So at minimum you're paying for **2–3 product hero images plus 2–3
YouTube iframes** above or near the fold. That's the dominant
"weight" of the page.

If FLUSS / GAUSS are presented with autoplay product videos hosted on
Wix Video (`video.wixstatic.com`) instead of static images, the cost
is even higher because Wix Video decodes a short looping mp4 right
away.

### 5. Render-blocking webfonts
Wix loads its custom font CSS from `fonts.shadow.wixstatic.com` plus
typically 2–4 weights of a display face (Hainbach's site uses a
narrow/bold serif for the wordmark and a sans for body). Each weight
is a separate network round-trip; nothing in the hero text can render
in its final shape until those land.

### 6. Third-party scripts running during load
Almost every Wix site loads, in addition to the Wix bundles:

- `frog.wix.com` – Wix's own analytics beacon
- `Sentry` / `wix-perf` performance reporting
- a cookie-consent banner script
- if the site uses Google Analytics / Meta Pixel / Mailchimp /
  a newsletter popup, those each add their own `<script>` tag

Each one contributes to Total Blocking Time even though they don't
visually contribute anything above the fold.

### 7. TTFB from server-side rendering
Wix sites are rendered on Wix's edge (Thunderbolt SSR). HTML for
"unpopular" subpages on smaller sites is regularly cold-cached, so
the first byte can take 500 ms – 1.5 s before the browser even sees
HTML. A subpage like `/new-page-21` is much less likely to be hot in
edge cache than `/`.

### 8. No code-splitting at the user's level
The page can't be made lighter without removing widgets in the
editor. Hainbach can't tree-shake the Wix runtime; whatever Wix is
shipping for any other feature on the site (blog, store, forms,
member area) is shipped here too.

## Most likely top-3 culprits, ranked
Without the actual waterfall I'd bet, in order:

1. **The Wix Thunderbolt JS payload + hydration cost.** This is the
   floor under any Wix page and the single biggest reason a simple
   "three instruments" page feels heavy. Mobile Lighthouse scores
   for stock Wix pages are commonly 30–55 / 100.

2. **Embedded YouTube iframes for the product demos.** Each one is
   roughly the weight of a small SPA. With 2–3 of them on the page,
   they often dominate transferred bytes after the initial JS.

3. **Unoptimised hero images for GAUSS / FLUSS.** Wix will serve
   resized variants from `static.wixstatic.com` but only at the
   pixel size the layout asks for; if the layout sets a full-bleed
   section, the served image can still be ~1–2 MB at desktop sizes,
   and it competes with JS for the main thread / network.

The combination of (1) + (2) is the usual reason a modest Wix page
feels sluggish: lots of small/medium scripts all racing for the main
thread while the user stares at a half-rendered hero.

## Things that are NOT the cause (worth ruling out)
- The slug `/new-page-21` itself. This is just Wix's default name
  for a page; it doesn't add any latency. Renaming it would help SEO
  and shareability but not speed.
- The domain. `hainbachmusik.com` is a normal custom domain pointed
  at Wix; DNS / TLS handshake is in the tens of ms.
- "Server location". Wix uses a global CDN; this isn't the bottleneck.

## What Hainbach (or anyone running this page) could actually do
In rough effort order:

1. **Replace YouTube `<iframe>` embeds with click-to-play poster
   images** (a static thumbnail + play button that swaps in the
   iframe on click). This alone usually shaves 1–3 seconds off LCP /
   TBT on Wix pages with multiple video embeds. Wix supports this via
   custom HTML or via the "lazy load" toggle on the Video element.
2. **Re-export the GAUSS / FLUSS hero images** at the actual layout
   size, save as WebP or AVIF, and re-upload. Wix will then serve the
   smaller source.
3. **Move any product demo videos below the fold** so they don't
   block LCP.
4. **Audit installed Wix Apps / custom code** in the editor and
   remove anything that isn't used on this specific page (each app
   ships its own JS bundle even on pages that don't visibly use it).
5. **Turn on "Enhance images" / Wix's "Performance" settings** under
   Site Manager → Performance & SEO. This enables the responsive
   image format pipeline and aggressive lazy-loading.
6. **Rename the slug to `/instruments`** — purely an SEO/UX win, not
   a perf win, but trivial and worth doing while in the editor.

There is no in-Wix way to remove the Thunderbolt runtime cost itself,
which sets the lower bound on how fast the page can ever be. If
Hainbach wanted to push past that floor, the only real option is to
move the site to a static-site generator (Astro/11ty/Hugo) or to
Wix Studio with a hand-built minimal page; both are large efforts.

## Verifying this for real
To actually measure rather than infer, run from a normal browser:

- https://pagespeed.web.dev/analysis?url=https%3A%2F%2Fwww.hainbachmusik.com%2Fnew-page-21
  (mobile + desktop Lighthouse + CrUX field data)
- https://www.webpagetest.org/ — pick "Mobile 4G" to see the
  waterfall, JS execution timeline, and a filmstrip of when the
  hero / videos appear.
- Chrome DevTools → Network panel + Performance recording + Coverage
  tab to see which Wix bundles the page actually used vs. shipped.

Look for, in particular:
- LCP element + LCP time (will probably be a hero image > 2.5 s on
  mobile)
- Total Blocking Time and the "Reduce JavaScript execution time"
  Lighthouse audit (will probably point to several
  parastorage.com bundles and to YouTube)
- "Avoid an excessive DOM size" (likely flagged)
- "Eliminate render-blocking resources" (likely flagged for Wix CSS
  + webfonts)

That waterfall will confirm or refute the three "most likely" causes
above with hard numbers.
