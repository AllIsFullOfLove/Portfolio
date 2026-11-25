# patlau.com — deploy notes

Static site on GitHub Pages (branch `main`, root `/`, `.nojekyll`), custom domain in `CNAME`, proxied by Cloudflare.

## Every publish
1. Bump the red version tag (bottom-left) in `index.html` (`.site-version` + `<!-- build … -->`) and `VERSION` in `tools/build_pages.py`. Current: **v034** (next: v035).
2. Cache-bust: `/assets/site.js?v=NNN` in `index.html` (preload + script tag); sub-pages get it from the build script.
3. Run `python3 tools/build_pages.py` — regenerates `assets/site.css`, the specialty pages, `/work/…` pages and the sub-page block of `sitemap.xml`.
4. Commit to `main` and push. Pages rebuilds in ~1 minute.

## SEO pages (v034)
- Specialty landing pages: `/matte-painter-toronto/`, `/concept-artist-toronto/`, `/vfx-supervisor-toronto/`, `/storyboard-artist-toronto/`
- Project pages: `/work/` index + `/work/<project>/` (galleries copied verbatim from the matching `<article>` in `index.html`)
- Copy uses only facts already on the site (slates + résumé). Edit the text in `tools/build_pages.py`, never the generated HTML.
- `assets/site.css` = verbatim copy of the inline `<style>` in `index.html` + a sub-page block. The home page keeps its inline CSS.

## Google Search Console / Bing — waiting on the owner (nothing faked)
Search Console → Add property → **URL prefix** `https://patlau.com/` (or a **Domain** property, verified by a TXT record in Cloudflare DNS).
- HTML-tag method: paste `<meta name="google-site-verification" content="CODE">` into `index.html` `<head>` right after the `<meta name="color-scheme">` line.
- HTML-file method: commit the downloaded `googleXXXXXXXX.html` file unchanged to the repo root (served at `https://patlau.com/googleXXXXXXXX.html`).
- Then submit `https://patlau.com/sitemap.xml`. Bing Webmaster Tools can import from Search Console (or uses `BingSiteAuth.xml` in the root / `<meta name="msvalidate.01">`).

## Analytics
None active. The placeholder Cloudflare beacon was removed in v034; see the comment at the end of `index.html` for where a real Cloudflare Web Analytics token or Plausible snippet goes (or enable Cloudflare's automatic setup — no code).
