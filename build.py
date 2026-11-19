"""Builds the portfolio pages from _src/ into plain static HTML.

Run:  python build.py
Output: index.html, projects/index.html, services/index.html, about/index.html, contact/index.html
Every page is complete HTML (no JavaScript needed to read it), so search engines and AI crawlers see everything.
"""
import json, re, pathlib, copy

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "_src" / "parts"
SITE = "https://ian-vincent-rebuta-portfolio.vercel.app"
BOOK = "https://calendly.com/ianrebuta/30min"
UPDATED = "2026-11-20"

part = lambda n: (SRC / n).read_text(encoding="utf-8")
LD = json.loads(part("jsonld.json"))["@graph"]
node = lambda t, **kw: next(n for n in LD if n["@type"] == t and all(n.get(k) == v for k, v in kw.items()))
videos = [n for n in LD if n["@type"] == "VideoObject"]

# ---------- icons (line icons, SF Symbols style) ----------
I = {
 "home": '<path d="M4 11l8-7 8 7v9h-5v-6H9v6H4z"/>',
 "work": '<path d="M3 7h6l2 2h10v10H3z"/>',
 "services": '<path d="M12 3l2.4 5.1 5.6.7-4.1 3.9 1 5.5L12 15.6 7.1 18.2l1-5.5L4 8.8l5.6-.7z"/>',
 "about": '<circle cx="12" cy="8" r="4"/><path d="M4 20c1.5-4 4.5-6 8-6s6.5 2 8 6"/>',
 "contact": '<path d="M4 5h16v11H9l-5 4z"/>',
 "book": '<path d="M5 5h14v15H5zM5 10h14M9 3v4M15 3v4"/>',
 "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/>',
 "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
 "moon": '<path d="M20 14.5A8 8 0 019.5 4 8 8 0 1020 14.5z"/>',
 "a11y": '<circle cx="12" cy="4.5" r="1.8"/><path d="M5 8.5l7 1.5 7-1.5M12 10v4.5M12 14.5l-3 6M12 14.5l3 6"/>',
 "chev": '<path d="M9 6l6 6-6 6"/>',
 "arrow": '<path d="M7 17L17 7M9 7h8v8"/>',
 "play": '<path d="M8 5v14l11-7z"/>',
 "close": '<path d="M6 6l12 12M18 6L6 18"/>',
 "send": '<path d="M5 12h14M13 6l6 6-6 6"/>',
}
def ico(k, cls=""): return f'<svg class="i {cls}" viewBox="0 0 24 24" aria-hidden="true">{I[k]}</svg>'
GH = '<svg class="i fill" viewBox="0 0 24 24" aria-hidden="true"><path d="' + re.search(r'd="([^"]+)"', (ROOT/"logos/github.svg").read_text(encoding="utf-8")).group(1) + '"/></svg>'
CUP = '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M7 12h15v6a6 6 0 01-6 6h-3a6 6 0 01-6-6z" fill="#FFF8EF"/><path d="M22 14h1.5a3 3 0 010 6H22" fill="none" stroke="#FFF8EF" stroke-width="2"/><path d="M11 6c0 2 2 2 2 4M15 5c0 2 2 2 2 4" fill="none" stroke="#FFF8EF" stroke-width="1.8" stroke-linecap="round"/><ellipse cx="14.5" cy="13.2" rx="5.5" ry="1.4" fill="#C89A6B"/></svg>'
import math
# smooth 8-lobe scalloped seal (like a platform "verified" badge), centred check
_SEAL = "M" + " L".join(f"{12+(10.3+.85*math.cos(8*t))*math.sin(t):.2f} {12-(10.3+.85*math.cos(8*t))*math.cos(t):.2f}"
                        for t in (2*math.pi*i/120 for i in range(120))) + "Z"
VERIFIED = ('<svg class="verified" viewBox="0 0 24 24" role="img" aria-label="Verified">'
            f'<path d="{_SEAL}" fill="#1D8CF8"/>'
            '<path d="M7.6 12.2l3 3 5.8-6" fill="none" stroke="#fff" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/></svg>')

NAV = [("home","Home","/"),("work","Projects","/projects"),("services","Services","/services"),("about","About","/about"),("contact","FAQ & Contact","/contact")]

def fix_paths(html):
    """Make asset paths absolute and turn old one-page anchors into page links."""
    html = re.sub(r'(src|href|poster)="(?!https?:|/|#|mailto:|tel:|data:)', r'\1="/', html)
    for a, b in {"#work":"/projects","#support":"/services","#experience":"/about#experience","#faq":"/contact#faq",
                 "#contact":"/contact","#intro":"/about#intro","#overview":"/","#process":"/services#process"}.items():
        html = html.replace(f'href="{a}"', f'href="{b}"')
    return html

def strip_head(section_html):
    """Remove a part's own <section> wrapper and section heading so a page can give it a new one."""
    inner = re.sub(r'^\s*<section[^>]*>\s*<div class="wrap">', '', section_html.strip())
    inner = re.sub(r'</div>\s*</section>\s*$', '', inner)
    return re.sub(r'\s*<div class="sec-head">.*?</div>', '', inner, count=1, flags=re.S).strip()

# ---------- shared chrome ----------
def sidebar(active):
    links = "".join(f'<a href="{h}"{" class=\"on\" aria-current=\"page\"" if k==active else ""}>{ico(k)}<span>{l}</span></a>' for k,l,h in NAV)
    return f'''<aside class="side" aria-label="Sidebar">
  <div class="prof">
    <a class="prof-pic" href="/" aria-label="Home"><img src="/photo.jpg" alt="Ian Vincent Rebuta" width="88" height="88"><i class="online" title="Available now"></i></a>
    <p class="prof-name">Ian Vincent Rebuta {VERIFIED}</p>
    <p class="prof-handle">@amfufy · Bohol, PH</p>
    <div class="prof-links">
      <a href="https://github.com/amfufy" target="_blank" rel="noopener me" aria-label="GitHub">{GH}</a>
      <a href="https://amfufy.github.io/pvblicly/" target="_blank" rel="noopener" aria-label="Pvblicly, my remote operations practice">{ico("globe")}</a>
      <a href="{BOOK}" target="_blank" rel="noopener" aria-label="Book a call on Calendly">{ico("book")}</a>
      <button type="button" class="theme-btn" aria-label="Switch light or dark mode">{ico("sun","sun")}{ico("moon","moon")}</button>
    </div>
  </div>
  <nav class="side-nav" aria-label="Main">{links}</nav>
  <div class="side-card">
    <p class="avail"><i aria-hidden="true"></i>Available now</p>
    <p>Free 30-minute call to see if we fit. No prep needed.</p>
    <a class="btn sun" href="{BOOK}" target="_blank" rel="noopener">Book a free call</a>
  </div>
  <div class="side-foot"><button type="button" class="a11y-btn" aria-label="Accessibility settings" aria-haspopup="dialog">{ico("a11y")}</button><small>© 2026 Ian Vincent Rebuta</small></div>
</aside>'''

def topbar():
    return f'''<header class="top">
  <div class="wrap">
    <a class="brand" href="/"><img src="/photo.jpg" alt=""><span>Ian Vincent Rebuta</span>{VERIFIED}</a>
    <div class="top-r"><button type="button" class="a11y-btn" aria-label="Accessibility settings" aria-haspopup="dialog">{ico("a11y")}</button><button type="button" class="theme-btn" aria-label="Switch light or dark mode">{ico("sun","sun")}{ico("moon","moon")}</button><a class="btn sun sm" href="{BOOK}" target="_blank" rel="noopener">Book a call</a></div>
  </div>
</header>'''

def tabbar(active):
    tabs = [t for t in NAV if t[0] != "contact"]
    items = "".join(f'<a href="{h}"{" class=\"on\" aria-current=\"page\"" if k==active else ""}>{ico(k)}<span>{l}</span></a>' for k,l,h in tabs)
    return f'<nav class="tabbar" aria-label="Quick links">{items}<a href="/contact"{" class=\"on\"" if active=="contact" else ""}>{ico("contact")}<span>Contact</span></a></nav>'

CHAT = f'''<button type="button" class="chat-fab" aria-label="Ask Latte, Ian's assistant" aria-haspopup="dialog" aria-controls="chat">{CUP}<i class="online"></i></button>
<section class="chat" id="chat" role="dialog" aria-modal="false" aria-labelledby="chat-t" hidden>
  <header class="chat-h"><span class="chat-av">{CUP}</span><span><b id="chat-t">Latte</b><small>Ian's assistant · answers from this site</small></span><button type="button" class="chat-x" aria-label="Close chat">{ico("close")}</button></header>
  <div class="chat-log" aria-live="polite"></div>
  <div class="chat-sugg"></div>
  <form class="chat-f" autocomplete="off"><label class="sr" for="chat-in">Ask a question</label><input id="chat-in" type="text" placeholder="Ask about Ian's work, hours, rates…" maxlength="200"><button type="submit" aria-label="Send">{ico("send")}</button></form>
  <p class="chat-note">Answers come from this site and can miss things. Chats aren't stored.</p>
</section>'''

A11Y = f'''<section class="a11y" id="a11y" role="dialog" aria-labelledby="a11y-t" hidden>
  <header><b id="a11y-t">Accessibility</b><button type="button" class="a11y-x" aria-label="Close">{ico("close")}</button></header>
  <p class="a11y-l">Text size</p>
  <div class="seg" role="group" aria-label="Text size"><button type="button" data-fs="0" aria-pressed="true">A</button><button type="button" data-fs="1" aria-pressed="false">A+</button><button type="button" data-fs="2" aria-pressed="false">A++</button></div>
  <label class="tog"><span><b>High contrast</b><small>Darker text, stronger edges</small></span><input type="checkbox" data-opt="hc"><i></i></label>
  <label class="tog"><span><b>Reduce motion</b><small>No animation or scrolling logos</small></span><input type="checkbox" data-opt="rm"><i></i></label>
  <label class="tog"><span><b>Underline links</b><small>Every link gets a line</small></span><input type="checkbox" data-opt="ul"><i></i></label>
  <button type="button" class="a11y-reset">Reset to default</button>
</section>'''

PREPAINT = '''<script>(function(){var d=document.documentElement;d.classList.add("js");try{var t=localStorage.getItem("theme");if(t)d.dataset.theme=t;var a=JSON.parse(localStorage.getItem("a11y")||"{}");if(a.fs)d.classList.add("fs-"+a.fs);["hc","rm","ul"].forEach(function(k){if(a[k])d.classList.add(k)})}catch(e){}})()</script>'''

def head(p):
    url = SITE + p["path"]
    ld = json.dumps({"@context":"https://schema.org","@graph":p["ld"]}, ensure_ascii=False, indent=1)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#F6EFE6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#17110D" media="(prefers-color-scheme: dark)">
<title>{p["title"]}</title>
<meta name="description" content="{p["desc"]}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<meta name="author" content="Ian Vincent Rebuta">
<link rel="canonical" href="{url}">
<link rel="alternate" type="text/plain" title="Summary for AI assistants" href="/llms.txt">
<meta name="geo.region" content="PH-BOH"><meta name="geo.placename" content="Bohol, Philippines">
<meta property="og:type" content="{"profile" if p["path"]=="/" else "website"}">
<meta property="og:site_name" content="Ian Vincent Rebuta">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{p["og"]}">
<meta property="og:description" content="{p["desc"]}">
<meta property="og:image" content="{SITE}/og.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Ian Vincent Rebuta, Operations, Social Media, Video and Web specialist">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{p["og"]}">
<meta name="twitter:description" content="{p["desc"]}">
<meta name="twitter:image" content="{SITE}/og.jpg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
{p.get("preload","")}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={UPDATED}">
{PREPAINT}
<script type="application/ld+json">
{ld}
</script>
</head>'''

def page(p):
    html = f'''{head(p)}
<body class="pg-{p["key"]}">
<a class="skip" href="#main">Skip to content</a>
{sidebar(p["key"])}
<div class="app">
{topbar()}
<main id="main">
{p["body"]}
</main>
<footer><div class="wrap"><span>© 2026 Ian Vincent Rebuta</span><span>Bohol, Philippines · Remote, US Eastern hours</span></div></footer>
</div>
{tabbar(p["key"])}
{CHAT}
{A11Y}
<script src="/assets/site.js?v={UPDATED}" defer></script>
</body>
</html>
'''
    out = ROOT / (p["path"].strip("/") or ".") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(fix_paths(html), encoding="utf-8", newline="\n")
    print("built", out.relative_to(ROOT))

def page_head(eyebrow, h1, sub, action=""):
    return f'''<header class="page-head rv"><div><p class="eyebrow">{eyebrow}</p><h1>{h1}</h1><p class="sub">{sub}</p></div>{action}</header>'''

# ---------- reusable bits from the old one-page site ----------
overview = part("overview.html")
bento = overview[overview.index('<div class="bento">') + len('<div class="bento">'):overview.rindex('</div>\n    </div>\n  </section>')]
starts = [m.start() for m in re.finditer(r'<(?:div|figure|article) class="w ', bento)] + [len(bento)]
WIDGETS = [bento[a:b].strip() for a, b in zip(starts, starts[1:])]
grab = lambda cls: [w for w in WIDGETS if w.split(">", 1)[0].count(f"w {cls} ")]
KPIS = "\n  ".join(grab("w-kpi"))
VIDEO = grab("w-video")[0].replace('<div class="w w-video rv">', '<div class="w w-video rv" id="intro">', 1)
CLOCK, CSAT, PROOF = grab("w-clock")[0], grab("w-csat")[0], grab("w-proof")[0]
marquee = part("marquee.html")
seen = set()
TOOLS = [t for t in re.findall(r'<img src="logos/([^"]+)"[^>]*></span><span class="mq-name">([^<]+)</span>', marquee) if not (t in seen or seen.add(t))]
li = "".join(f'<li><span class="appico"><img src="/logos/{f}" alt="" width="30" height="30" loading="lazy" decoding="async"></span><span class="mq-name">{n}</span></li>' for f, n in TOOLS)
one_row = f'<div class="mq-row"><ul class="mq-track">{li}</ul><ul class="mq-track" aria-hidden="true">{li}</ul></div>'

person = node("Person"); website = node("WebSite"); org = node("Organization")
ref_person = {"@id": person["@id"]}
def webpage(t, path, name, desc, extra=None):
    d = {"@type": t, "@id": f"{SITE}{path}#page", "url": SITE+path, "name": name, "description": desc,
         "isPartOf": {"@id": website["@id"]}, "about": ref_person, "dateModified": UPDATED, "inLanguage": "en",
         "breadcrumb": {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"}] +
                        ([{"@type":"ListItem","position":2,"name":name.split(" |")[0],"item":SITE+path}] if path!="/" else [])}}
    if extra: d.update(extra)
    return d

# ======================= HOME =======================
shots = ["happyhobby","etl","wedding","pvblicly","kusog"]
carousel = "".join(f'<img src="/shots/{s}.jpg" alt="" loading="{"eager" if i==0 else "lazy"}" width="1200" height="750" style="--i:{i}">' for i,s in enumerate(shots))
home_body = f'''
<div class="home">
  <header class="home-head rv">
    <div><p class="avail"><i aria-hidden="true"></i>Available now for US teams</p>
      <h1>Operations, content and systems, handled.</h1>
      <p class="sub">I help US businesses run smoother: QA, social media, video, websites and AI tools, from one person.</p></div>
    <a class="btn sun" href="{BOOK}" target="_blank" rel="noopener">Book a free 30-min call</a>
  </header>

  <section class="pillbar rv" aria-label="Tools I work with">
    <p class="pb-l"><small>Daily drivers</small><b>Tools I work with</b></p>
    {one_row}
  </section>

  <div class="home-grid">
    <div class="badge-wrap rv">
      <span class="lanyard" aria-hidden="true"></span>
      <article class="badge" id="badge" aria-label="ID card: Ian Vincent Rebuta">
        <span class="badge-clip" aria-hidden="true"></span>
        <span class="badge-shine" aria-hidden="true"></span>
        <a class="badge-play" href="/about#intro">{ico("play")}<span>1:24 intro</span></a>
        <div class="badge-photo"><img src="/portrait.jpg" alt="Ian Vincent Rebuta" width="826" height="826" fetchpriority="high">{VERIFIED}</div>
        <p class="badge-hi">Hi, I'm</p>
        <h2 class="badge-name">Ian Vincent Rebuta</h2>
        <p class="badge-role">Ops · QA · Social · Video · Web</p>
        <p class="badge-tag">Run smoother.<br><b>Every week.</b></p>
        <div class="badge-foot"><span><i class="online"></i>Available now</span><span>Bohol · GMT+8</span></div>
      </article>
    </div>

    <a class="tile t-proj rv" href="/projects">
      <span class="t-h">{ico("work","t-ico")}<span><b>Projects</b><small>12 real projects, live links and videos.</small></span>{ico("arrow","t-go")}</span>
      <span class="carousel browser"><span class="chrome"><i></i><i></i><i></i><span>live sites I built</span></span><span class="car">{carousel}</span></span>
    </a>

    <a class="tile t-reel rv" href="/projects#video">
      <span class="t-h">{ico("play","t-ico")}<span><b>Video &amp; reels</b><small>Made for the feed.</small></span>{ico("arrow","t-go")}</span>
      <span class="reel"><video autoplay muted loop playsinline preload="metadata" poster="/media/bbx-news.jpg" aria-label="Beyblade X news reel, muted preview" width="540" height="960"><source src="/media/bbx-news.mp4" type="video/mp4"></video></span>
    </a>

    <a class="tile t-serv rv" href="/services">
      <span class="t-h">{ico("services","t-ico")}<span><b>Services</b><small>Four jobs, one person.</small></span>{ico("arrow","t-go")}</span>
      <span class="list">
        <span><b>Operations &amp; QA</b><em>01</em></span><span><b>Social media</b><em>02</em></span>
        <span><b>Video &amp; animation</b><em>03</em></span><span><b>Web &amp; AI automation</b><em>04</em></span>
      </span>
    </a>

    <a class="tile t-about rv" href="/about">
      <span class="t-h">{ico("about","t-ico")}<span><b>About</b><small>Six years with US companies.</small></span>{ico("arrow","t-go")}</span>
      <span class="minis">
        <span><b>6<small>yrs</small></b><em>with US teams</em></span><span><b>23</b><em>QA analysts led</em></span>
        <span><b>10</b><em>social pages</em></span><span><b>97%</b><em>CSAT held</em></span>
      </span>
    </a>

    <div class="tile t-chat rv">
      <span class="t-h">{ico("contact","t-ico")}<span><b>Say hi</b><small id="status">Works US Eastern hours</small></span></span>
      <span class="times"><span><em>Bohol</em><b id="cbt" data-tz="Asia/Manila">GMT+8</b></span><span><em>New York</em><b id="cnt" data-tz="America/New_York">US Eastern</b></span></span>
      <span class="t-acts"><button type="button" class="btn line sm open-chat">Ask Latte</button><a class="btn ink sm" href="/contact">FAQ &amp; contact</a></span>
    </div>
  </div>
</div>'''
home_ld = [website, webpage("ProfilePage","/","Ian Vincent Rebuta | Remote Ops, QA, Social Media & Web",
           "Portfolio of Ian Vincent Rebuta, remote operations & QA, social media, video and web & AI specialist.",
           {"mainEntity": ref_person, "primaryImageOfPage": SITE+"/portrait.jpg"}), person, org]

# ======================= PROJECTS =======================
work = strip_head(part("work.html"))
proj_videos = [v for v in videos if "intro" not in v.get("@id","")]
proj_body = f'''<div class="wrap">
{page_head("Projects","Real projects you can open.","Websites, campaigns, reels and AI tools. Pick a lane, or see everything.",
  f'<a class="btn sun" href="{BOOK}" target="_blank" rel="noopener">Book a free call</a>')}
{work}
</div>'''
items = re.findall(r'<p class="kind">([^<]*)</p><h3>([^<]*)</h3>', work)
proj_ld = [webpage("CollectionPage","/projects","Projects | Ian Vincent Rebuta","Websites, campaigns, reels and AI tools built by Ian Vincent Rebuta.",
           {"mainEntity":{"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"item":{"@type":"CreativeWork","name":t.replace("&amp;","&").replace("&#x27;","'"),"genre":k.replace("&amp;","&"),"creator":ref_person}} for i,(k,t) in enumerate(items)]}}),
           person] + proj_videos

# ======================= SERVICES =======================
support = strip_head(part("support.html"))
process = strip_head(part("process.html"))
serv_body = f'''<div class="wrap">
{page_head("Services","Four jobs, one person.","Most growing businesses hire for these separately. I cover all four, and because my background is QA, each one is checked before it goes out.",
  f'<a class="btn sun" href="{BOOK}" target="_blank" rel="noopener">Book a free call</a>')}
{support}
<section id="process" class="sub-sec"><div class="sec-head"><h2 class="rv">How I work with you</h2><p class="rv">My background is quality assurance, so I check my own work before you ever see it.</p></div>
{process}</section>
<section class="cta-card rv"><div><h2>Not sure which one you need?</h2><p>Tell me what's eating your week. I'll tell you honestly what I'd take over first.</p></div><a class="btn sun" href="{BOOK}" target="_blank" rel="noopener">Book a free 30-min call</a></section>
</div>'''
serv_ld = [webpage("WebPage","/services","Services | Ian Vincent Rebuta","Operations & QA, social media management, video & animation, and web & AI automation for US businesses.",
           {"mainEntity": person["makesOffer"]}), person]

# ======================= ABOUT =======================
exp = strip_head(part("experience.html"))
toolgrid = "".join(f'<li><span class="appico"><img src="/logos/{f}" alt="" width="30" height="30" loading="lazy"></span><span class="mq-name">{n}</span></li>' for f,n in TOOLS)
about_body = f'''<div class="wrap">
{page_head("About","Hi, I'm Ian.","I keep businesses running smoother every week, from Bohol, Philippines, on US hours.")}
<div class="bento about-bento">
  <article class="w w-story rv">
    <p class="story-lead">Six years finding out exactly where work breaks for US teams. <span>Now I build the systems, content and checks that stop it from breaking again.</span></p>
    <p>I started on the phones at Ibex Global, moved into QA and business insights, and went on to lead 23 QA analysts across Jamaica, Honduras and the Philippines. At Nooro I rebuilt the knowledge base behind an AI call-audit pipeline. Today I run Pvblicly, manage ten social media pages, make their videos and build websites for clients.</p>
    <div class="roles"><span>Operations &amp; QA <em>01</em></span><span>Social media manager <em>02</em></span><span>Video &amp; animation <em>03</em></span><span>Web &amp; AI automation <em>04</em></span></div>
  </article>
  {KPIS}
  {VIDEO}
  {CLOCK}
  {CSAT}
  {PROOF}
</div>
<section id="experience" class="sub-sec"><div class="sec-head"><h2 class="rv">Experience</h2><p class="rv">From the phones to leading a multi-country QA team.</p></div>
{exp}</section>
<section id="toolkit" class="sub-sec"><div class="sec-head"><h2 class="rv">Toolkit</h2><p class="rv">{len(TOOLS)} tools I use for operations, content, web and AI.</p></div>
<ul class="toolgrid rv">{toolgrid}</ul></section>
</div>'''
intro_video = node("VideoObject", **{"@id": f"{SITE}/#intro-video"})
about_ld = [webpage("AboutPage","/about","About Ian Vincent Rebuta","Background, experience and toolkit of Ian Vincent Rebuta.",{"mainEntity": ref_person}), person, intro_video]

# ======================= CONTACT =======================
faq = strip_head(part("faq.html"))
contact_body = f'''<div class="wrap">
{page_head("FAQ &amp; Contact","Let's talk.","Short answers first. If yours isn't here, ask Latte or book a free call.")}
<div class="contact-cards">
  <a class="w cc rv" href="{BOOK}" target="_blank" rel="noopener">{ico("book","cc-i")}<b>Book a free 30-min call</b><span>Pick a time on Calendly. No prep needed.</span>{ico("arrow","t-go")}</a>
  <button type="button" class="w cc open-chat rv">{CUP}<b>Ask Latte</b><span>Instant answers about my work, hours and rates.</span>{ico("arrow","t-go")}</button>
  <a class="w cc rv" href="https://amfufy.github.io/pvblicly/" target="_blank" rel="noopener">{ico("globe","cc-i")}<b>Pvblicly</b><span>My remote operations practice.</span>{ico("arrow","t-go")}</a>
  <a class="w cc rv" href="https://github.com/amfufy" target="_blank" rel="noopener me">{GH}<b>GitHub</b><span>The code behind my sites.</span>{ico("arrow","t-go")}</a>
</div>
<section id="faq" class="sub-sec"><div class="sec-head"><h2 class="rv">Questions people ask</h2><p class="rv">Short answers about who I am, what I do and how to work with me.</p></div>
{faq}</section>
</div>
{fix_paths(part("contact.html").replace('<section id="contact" class="contact">','<section id="contact" class="contact" aria-label="Book a call">'))}'''
faq_node = node("FAQPage"); faq_node = dict(faq_node, **{"@id": f"{SITE}/contact#faq"})
contact_ld = [webpage("ContactPage","/contact","FAQ & Contact | Ian Vincent Rebuta","How to hire Ian Vincent Rebuta, plus answers to common questions.",{"mainEntity": ref_person}), person, faq_node]

PAGES = [
 dict(key="home", path="/", title="Ian Vincent Rebuta | Remote Ops, QA, Social Media & Web",
      og="Ian Vincent Rebuta | Operations, Social Media, Video & Web",
      desc="Hire Ian Vincent Rebuta for remote operations & QA, social media, video and web & AI automation. 6 years with US companies. Book a free 30-min call.",
      body=home_body, ld=home_ld, preload='<link rel="preload" as="image" href="/portrait.jpg" fetchpriority="high">'),
 dict(key="work", path="/projects", title="Projects: Websites, Reels & AI Tools | Ian Vincent Rebuta",
      og="Projects by Ian Vincent Rebuta", desc="Real projects by Ian Vincent Rebuta: websites, social media campaigns, reels, brand films, a QA pipeline fix and Claude AI skills.",
      body=proj_body, ld=proj_ld),
 dict(key="services", path="/services", title="Services: Ops & QA, Social, Video, Web | Ian Vincent Rebuta",
      og="Services by Ian Vincent Rebuta", desc="Operations & QA, social media management, video & animation, and web & AI automation for US businesses, from one remote specialist.",
      body=serv_body, ld=serv_ld),
 dict(key="about", path="/about", title="About Ian Vincent Rebuta | 6 Years with US Companies",
      og="About Ian Vincent Rebuta", desc="Ian Vincent Rebuta: 6 years with US companies, led 23 QA analysts across 3 countries, manages 10 social pages. Based in Bohol, on US hours.",
      body=about_body, ld=about_ld),
 dict(key="contact", path="/contact", title="FAQ & Contact | Hire Ian Vincent Rebuta",
      og="FAQ & Contact | Ian Vincent Rebuta", desc="How to hire Ian Vincent Rebuta: book a free 30-minute call. Answers about his services, hours, tools and availability for US teams.",
      body=contact_body, ld=contact_ld),
]
for p in PAGES: page(p)
