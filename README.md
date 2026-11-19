# Ian Vincent Rebuta — Portfolio

Operations & QA, social media, video & animation, and web & AI automation.
Live at https://ian-vincent-rebuta-portfolio.vercel.app/ (if the Vercel domain differs, change `SITE` in `build.py`, plus robots.txt, sitemap.xml and llms.txt).

## Pages
`/` home (one-screen tiles + ID badge) · `/projects` · `/services` · `/about` · `/contact` (FAQ).
Every page is complete static HTML, so Google, Bing and AI crawlers can read it without JavaScript.

## Editing
1. Edit the content in `_src/parts/` (sections, projects, FAQ, structured data in `jsonld.json`) or the page layouts in `build.py`.
2. Run `python build.py`. It writes `index.html` and `projects/`, `services/`, `about/`, `contact/` `index.html`.
3. Commit and push. Vercel redeploys automatically.

Notes:
- **Projects:** each `<article class="case" data-cats="...">` in `_src/parts/work.html`. `data-cats` takes `ops`, `social`, `video` or `web`, and the filter counts are written by hand. Linking to `/projects#video` (or `#ops`, `#social`, `#web`) opens that filter.
- **FAQ:** each `<details>` in `_src/parts/faq.html` must match the `FAQPage` entry in `_src/parts/jsonld.json` word for word.
- **Latte, the FAQ assistant:** its answers live in the `KB` list in `assets/site.js`. It runs in the browser, with no API and no cost.
- **Styles and behaviour:** `assets/site.css` and `assets/site.js` are shared by every page.
- **Logos:** in `logos/`. Most come from Simple Icons (CC0) and svgl; Monday.com, GoHighLevel, Gorgias, CapCut, Real Geeks and GoKaizn come from each company's own site icon.
- **Media:** screenshots go in `shots/` (16:10), videos in `media/` (H.264, under 7 MB, with a `.jpg` cover). Captions: `media/intro.vtt`.

## Search & AI files
`robots.txt` (all crawlers, including AI bots), `sitemap.xml` (5 pages, plus images and videos), `llms.txt` (summary for AI assistants), `og.jpg` (share image). Each page has its own title, description, canonical URL and JSON-LD.

## Hosting
Vercel, imported from this repo. Static site, no build step on Vercel: run `build.py` locally before pushing. `.vercelignore` keeps `_src/` and `build.py` off the live site. Headers and caching are in `vercel.json`.
