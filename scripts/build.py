#!/usr/bin/env python3
"""Build the Market Updates blog for roysoldquick.com.

Each post lives in content/posts/YYYY-MM-DD-slug.html: a JSON header inside an
HTML comment, then the article body as plain HTML. This script turns those into
static pages, then refreshes the blog index, the homepage's latest-posts block,
sitemap.xml, feed.xml, robots.txt and llms.txt. Standard library only.

    python3 scripts/build.py            # published posts only
    python3 scripts/build.py --drafts   # include drafts, for a local preview
"""
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "content" / "posts"
OUT_DIR = ROOT / "market-updates"
SITE = "https://roysoldquick.com"
TZ = ZoneInfo("America/Los_Angeles")

ROY = {
    "name": "Roy Quick",
    "phone": "980-416-6412",
    "tel": "+19804166412",
    "email": "roy@roysoldquick.com",
    "dre": "02417080",
    "street": "222 Avenida Del Mar",
    "city": "San Clemente",
    "zip": "92672",
    "socials": [
        "https://www.instagram.com/roysoldquick/",
        "https://www.youtube.com/@roysoldquick",
        "https://www.facebook.com/profile.php?id=61581441453609",
        "https://linktr.ee/roysoldquick",
    ],
}
AREAS = ["San Clemente", "Dana Point", "Capistrano Beach", "San Juan Capistrano",
         "Laguna Niguel", "Rancho Mission Viejo", "Orange County"]

esc = html.escape


# ---------- loading ----------

def load_posts(include_drafts):
    posts = []
    for path in sorted(POSTS_DIR.glob("*.html")):
        raw = path.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--(.*?)-->\s*(.*)", raw, re.S)
        if not m:
            sys.exit(f"{path.name}: missing the JSON header comment")
        meta = json.loads(m.group(1))
        meta["body"] = m.group(2).strip()
        for key in ("title", "slug", "date", "description", "image"):
            if key not in meta:
                sys.exit(f"{path.name}: header is missing '{key}'")
        if meta.get("draft") and not include_drafts:
            continue
        hh, mm = (meta.get("time") or "12:00").split(":")
        d = dt.date.fromisoformat(meta["date"])
        meta["published"] = dt.datetime(d.year, d.month, d.day, int(hh), int(mm), tzinfo=TZ)
        upd = meta.get("updated")
        meta["modified"] = (dt.datetime.fromisoformat(upd).replace(tzinfo=TZ) if upd else meta["published"])
        meta["url"] = f"{SITE}/market-updates/{meta['slug']}/"
        meta["path"] = f"/market-updates/{meta['slug']}/"
        words = len(re.sub(r"<[^>]+>", " ", meta["body"]).split())
        meta["minutes"] = max(1, round(words / 230))
        posts.append(meta)
    posts.sort(key=lambda p: p["published"], reverse=True)
    return posts


def nice_date(d):
    return d.strftime("%B %-d, %Y")


def img_url(src, width):
    """Unsplash images are resized on their CDN; local images are used as is."""
    if "images.unsplash.com" in src:
        base = src.split("?")[0]
        return f"{base}?auto=format&fit=crop&w={width}&q=75"
    return src


# ---------- shared chunks ----------

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="preconnect" href="https://images.unsplash.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..700;1,6..96,400..600&family=Figtree:wght@400;500;600;700&display=swap">\n'
         '<link rel="stylesheet" href="/assets/blog.css">\n'
         '<link rel="icon" type="image/png" href="/logo-dark.png">\n'
         '<link rel="alternate" type="application/rss+xml" title="Roy Quick Market Updates" href="/feed.xml">')


def header():
    return f"""<a class="skip" href="#main">Skip to main content</a>
<header class="site">
  <div class="wrap nav">
    <a href="/" aria-label="Roy Quick Real Estate home"><img src="/logo-light.png" alt="Roy Quick Real Estate" width="58" height="54"></a>
    <ul>
      <li><a href="/#listings">Listings</a></li>
      <li><a href="/#expired">Expired Listings</a></li>
      <li><a href="/market-updates/" aria-current="page">Market Updates</a></li>
      <li><a href="/#about">About</a></li>
      <li><a href="/#contact">Contact</a></li>
    </ul>
    <a class="call" href="tel:{ROY['tel']}">{ROY['phone']}</a>
  </div>
</header>"""


def lead_band(heading="Thinking about selling, leasing or investing in South OC?"):
    return f"""<section class="lead" id="talk">
  <div class="wrap grid">
    <div>
      <span class="eyebrow">Talk to Roy</span>
      <h2>{esc(heading)}</h2>
      <p class="lede">Ask me what your home would sell or lease for today, or what these numbers mean for your street. I answer every message myself, usually the same day.</p>
      <dl>
        <div><dt>Call or text</dt><dd><a href="tel:{ROY['tel']}">{ROY['phone']}</a></dd></div>
        <div><dt>Email</dt><dd><a href="mailto:{ROY['email']}">{ROY['email']}</a></dd></div>
        <div><dt>Office</dt><dd>{ROY['street']}, {ROY['city']}</dd></div>
      </dl>
    </div>
    <form data-lead novalidate>
      <div class="f"><label for="l-name">Name</label><input id="l-name" name="name" autocomplete="name" required></div>
      <div class="f"><label for="l-phone">Phone</label><input id="l-phone" name="phone" type="tel" autocomplete="tel"></div>
      <div class="f full"><label for="l-email">Email</label><input id="l-email" name="email" type="email" autocomplete="email"></div>
      <div class="f full"><label for="l-type">I'm looking to</label>
        <select id="l-type" name="looking_to"><option>Sell</option><option>Lease out my home</option><option>Get a home value</option><option>Invest</option><option>Buy</option><option>Other</option></select></div>
      <div class="f full"><label for="l-address">Property address <span style="text-transform:none;letter-spacing:0">(optional)</span></label><input id="l-address" name="address" autocomplete="street-address"></div>
      <div class="f full"><label for="l-msg">How can I help?</label><textarea id="l-msg" name="message"></textarea></div>
      <div class="f full"><label class="check" for="l-sms"><input type="checkbox" id="l-sms" name="sms_consent" value="yes"> <span>Yes, Roy Quick may text me about my real estate needs at the number above. Message frequency varies. Message and data rates may apply. Reply STOP to opt out or HELP for help. Consent is not required to work with me.</span></label></div>
      <div class="hp" aria-hidden="true"><label for="l-website">Leave this empty</label><input id="l-website" name="website" tabindex="-1" autocomplete="off"></div>
      <div class="form-foot">
        <button class="btn btn-dark" type="submit">Send to Roy</button>
        <p class="fine">By sending this, you agree that Roy Quick may contact you by phone or email about your request. See the <a href="/privacy.html">Privacy Policy</a>.</p>
        <p class="err" hidden></p>
      </div>
    </form>
  </div>
</section>"""


def footer():
    return f"""<footer>
  <div class="wrap">
    <img src="/logo-light.png" alt="Roy Quick Real Estate" width="102" height="96" loading="lazy">
    <div>
      <p><strong>Roy Quick, Realtor®</strong> · CA DRE# {ROY['dre']} · <strong>LUXRE Realty, Inc.</strong> · CA DRE# 01897290<br>{ROY['street']}, {ROY['city']}, CA {ROY['zip']} · {ROY['phone']} · {ROY['email']}</p>
      <p>Market statistics come from the third-party sources named in each post and are deemed reliable but not guaranteed. They are general information, not an appraisal, and not legal, tax or lending advice. Roy Quick is a licensed real estate salesperson with LUXRE Realty, Inc., which is responsible for this advertising. Equal Housing Opportunity.</p>
      <p><a href="/market-updates/">Market Updates</a> · <a href="/feed.xml">RSS</a> · <a href="/privacy.html">Privacy Policy &amp; Terms</a> · <a href="/privacy.html#accessibility">Accessibility</a> · © {dt.date.today().year} Roy Quick Real Estate</p>
    </div>
  </div>
</footer>
<nav class="quickbar" aria-label="Contact Roy">
  <a href="tel:{ROY['tel']}">Call Roy</a>
  <a href="sms:{ROY['tel']}">Text</a>
  <a href="mailto:{ROY['email']}">Email</a>
</nav>
<script src="/assets/lead.js" defer></script>"""


def inline_cta():
    return f"""<aside class="cta" aria-label="Contact Roy">
  <h3>Want these numbers for your street?</h3>
  <p>I'll pull the recent sales around your home and tell you honestly what it would sell or lease for right now. No pressure, no obligation.</p>
  <div class="row">
    <a class="btn btn-gold" href="tel:{ROY['tel']}">Call or text {ROY['phone']}</a>
    <a class="btn btn-line" href="#talk">Ask me online</a>
  </div>
</aside>"""


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, indent=1) + "</script>"


def agent_ld():
    return {
        "@type": "RealEstateAgent",
        "@id": f"{SITE}/#roy",
        "name": "Roy Quick",
        "alternateName": "Roy Quick Real Estate",
        "url": f"{SITE}/",
        "image": f"{SITE}/roy.jpg",
        "telephone": "+1-980-416-6412",
        "email": ROY["email"],
        "address": {"@type": "PostalAddress", "streetAddress": ROY["street"], "addressLocality": ROY["city"],
                    "addressRegion": "CA", "postalCode": ROY["zip"], "addressCountry": "US"},
        "areaServed": [{"@type": "City", "name": f"{a}, CA"} if a != "Orange County" else
                       {"@type": "AdministrativeArea", "name": "Orange County, CA"} for a in AREAS],
        "parentOrganization": {"@type": "RealEstateAgent", "name": "LUXRE Realty, Inc.", "url": "https://luxrerealty.com/"},
        "sameAs": ROY["socials"],
    }


def person_ld():
    return {
        "@type": "Person",
        "@id": f"{SITE}/#person",
        "name": "Roy Quick",
        "jobTitle": "Realtor®",
        "url": f"{SITE}/",
        "image": f"{SITE}/roy.jpg",
        "worksFor": {"@type": "RealEstateAgent", "name": "LUXRE Realty, Inc.", "url": "https://luxrerealty.com/"},
        "hasCredential": {"@type": "EducationalOccupationalCredential", "credentialCategory": "license",
                          "name": f"California DRE Salesperson License #{ROY['dre']}"},
        "knowsAbout": ["San Clemente real estate", "Dana Point real estate", "South Orange County housing market",
                       "Selling a home", "Leasing a home", "Real estate investing", "Expired listings"],
        "sameAs": ROY["socials"],
    }


# ---------- pages ----------

def card(p, feature=False, level="h2"):
    cls = "pcard feature" if feature else "pcard"
    w = 1400 if feature else 800
    return f"""<a class="{cls}" href="{p['path']}">
  <div class="ph"><img src="{esc(img_url(p['image']['src'], w))}" alt="{esc(p['image']['alt'])}" loading="lazy" width="{w}" height="{int(w*0.625)}"></div>
  <div class="pb">
    <span class="meta">{nice_date(p['published'])} · {p['minutes']} min read</span>
    <{level}>{esc(p['title'])}</{level}>
    <p>{esc(p['description'])}</p>
  </div>
</a>"""


def faq_html(faq):
    if not faq:
        return ""
    items = "\n".join(f"<details><summary>{esc(f['q'])}</summary><p>{f['a']}</p></details>" for f in faq)
    return f'<section class="faq"><h2>Questions I hear this week</h2>\n{items}\n</section>'


def sources_html(sources):
    if not sources:
        return ""
    items = "\n".join(f'<li><a href="{esc(s["url"])}" rel="nofollow noopener" target="_blank">{esc(s["name"])}</a></li>'
                      for s in sources)
    return f'<section class="sources"><h2>Sources</h2><ol>\n{items}\n</ol></section>'


def author_html():
    return f"""<section class="author">
  <img src="/assets/roy-avatar.jpg" alt="Roy Quick" width="96" height="96" loading="lazy">
  <div>
    <h2>Written by Roy Quick</h2>
    <p>I'm a Realtor® with LUXRE Realty, based in San Clemente. I help South Orange County homeowners sell or lease their homes, and I love running the numbers with investors. Every week I break down what's actually happening in our local market, with sources, so you can make your next move with confidence.</p>
    <div class="row">
      <a href="tel:{ROY['tel']}">Call {ROY['phone']}</a>
      <a href="sms:{ROY['tel']}">Text me</a>
      <a href="mailto:{ROY['email']}">Email</a>
      <a href="https://www.instagram.com/roysoldquick/" target="_blank" rel="noopener">Instagram</a>
      <a href="https://www.youtube.com/@roysoldquick" target="_blank" rel="noopener">YouTube</a>
    </div>
  </div>
</section>"""


def post_page(p, others):
    img = p["image"]
    hero = img_url(img["src"], 1800)
    og = img_url(img["src"], 1200)
    credit = (f'Photo: <a href="{esc(img["photo_url"])}" rel="nofollow noopener" target="_blank">{esc(img["credit"])}</a>'
              f'{" on Unsplash" if "unsplash" in img.get("photo_url", "") else ""}') if img.get("credit") else ""
    body = p["body"].replace("<!-- CTA -->", inline_cta())
    keywords = ", ".join(p.get("keywords", []))
    graph = [
        {
            "@type": "BlogPosting",
            "@id": p["url"] + "#post",
            "mainEntityOfPage": p["url"],
            "headline": p["title"],
            "description": p["description"],
            "image": [og],
            "datePublished": p["published"].isoformat(),
            "dateModified": p["modified"].isoformat(),
            "author": {"@id": f"{SITE}/#person"},
            "publisher": {"@id": f"{SITE}/#roy"},
            "keywords": keywords,
            "articleSection": "Market Updates",
            "inLanguage": "en-US",
            "about": [{"@type": "Place", "name": f"{a}, CA"} for a in p.get("areas", ["San Clemente"])],
            "citation": [s["url"] for s in p.get("sources", [])],
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Market Updates", "item": f"{SITE}/market-updates/"},
                {"@type": "ListItem", "position": 3, "name": p["title"], "item": p["url"]},
            ],
        },
        person_ld(),
        agent_ld(),
    ]
    if p.get("faq"):
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": f["q"],
                            "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", f["a"])}}
                           for f in p["faq"]],
        })
    related = "\n".join(card(o, level="h3") for o in others[:3])
    related_html = (f'<section class="related"><div class="wrap"><span class="eyebrow">Keep reading</span>'
                    f'<h2 style="font-size:clamp(30px,3.6vw,42px);margin-top:12px">More South OC market updates</h2>'
                    f'<div class="posts">{related}</div></div></section>') if related else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(p.get('seo_title') or p['title'])} | Roy Quick, San Clemente Realtor®</title>
<meta name="description" content="{esc(p['description'])}">
<meta name="author" content="Roy Quick">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{p['url']}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Roy Quick Real Estate">
<meta property="og:title" content="{esc(p['title'])}">
<meta property="og:description" content="{esc(p['description'])}">
<meta property="og:url" content="{p['url']}">
<meta property="og:image" content="{esc(og)}">
<meta property="og:image:alt" content="{esc(img['alt'])}">
<meta property="article:published_time" content="{p['published'].isoformat()}">
<meta property="article:modified_time" content="{p['modified'].isoformat()}">
<meta property="article:author" content="Roy Quick">
<meta property="article:section" content="Market Updates">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(p['title'])}">
<meta name="twitter:description" content="{esc(p['description'])}">
<meta name="twitter:image" content="{esc(og)}">
<meta name="geo.region" content="US-CA">
<meta name="geo.placename" content="San Clemente">
{FONTS}
<link rel="preload" as="image" href="{esc(hero)}">
{ld({"@context": "https://schema.org", "@graph": graph})}
</head>
<body>
{header()}
<main id="main">
<article>
  <div class="ahead">
    <div class="narrow">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/market-updates/">Market Updates</a></nav>
      <h1>{esc(p['title'])}</h1>
      <p class="dek">{esc(p.get('dek') or p['description'])}</p>
      <div class="byline">
        <img src="/assets/roy-avatar.jpg" alt="" width="52" height="52">
        <div><strong>By Roy Quick</strong>, Realtor® · LUXRE Realty<br>
        <time datetime="{p['published'].isoformat()}">{nice_date(p['published'])}</time> · {p['minutes']} min read · <a href="tel:{ROY['tel']}">{ROY['phone']}</a></div>
      </div>
    </div>
  </div>
  <figure class="heroimg">
    <img src="{esc(hero)}" alt="{esc(img['alt'])}" width="1800" height="1013" fetchpriority="high">
    {f'<figcaption class="credit">{credit}</figcaption>' if credit else ''}
  </figure>
  <div class="narrow article">
{body}
{faq_html(p.get('faq'))}
{sources_html(p.get('sources'))}
{author_html()}
  </div>
</article>
{lead_band()}
{related_html}
</main>
{footer()}
</body>
</html>
"""


def index_page(posts):
    cards = "\n".join(card(p, feature=(i == 0)) for i, p in enumerate(posts)) or \
        '<p>The first market update is on its way. Check back Monday.</p>'
    graph = [
        {
            "@type": "Blog",
            "@id": f"{SITE}/market-updates/#blog",
            "name": "Roy Quick Market Updates",
            "description": "Weekly San Clemente, Dana Point and South Orange County real estate market updates and local news from Roy Quick, Realtor® with LUXRE Realty.",
            "url": f"{SITE}/market-updates/",
            "inLanguage": "en-US",
            "author": {"@id": f"{SITE}/#person"},
            "publisher": {"@id": f"{SITE}/#roy"},
            "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": p["url"],
                          "datePublished": p["published"].isoformat(), "image": img_url(p["image"]["src"], 1200)}
                         for p in posts[:20]],
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Market Updates", "item": f"{SITE}/market-updates/"},
            ],
        },
        person_ld(),
        agent_ld(),
    ]
    og = img_url(posts[0]["image"]["src"], 1200) if posts else f"{SITE}/roy.jpg"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>San Clemente &amp; South OC Real Estate Market Updates | Roy Quick, Realtor®</title>
<meta name="description" content="Weekly San Clemente, Dana Point, Capistrano Beach and Orange County housing market updates from Roy Quick, Realtor® with LUXRE Realty. Prices, inventory, rates and local news, with sources.">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{SITE}/market-updates/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Roy Quick Real Estate">
<meta property="og:title" content="South OC Market Updates from Roy Quick">
<meta property="og:description" content="Weekly San Clemente, Dana Point and Orange County housing market updates, with sources.">
<meta property="og:url" content="{SITE}/market-updates/">
<meta property="og:image" content="{esc(og)}">
<meta name="twitter:card" content="summary_large_image">
{FONTS}
{ld({"@context": "https://schema.org", "@graph": graph})}
</head>
<body>
{header()}
<main id="main">
<section class="bhero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span>Market Updates</nav>
    <h1>South OC <em>Market Updates</em></h1>
    <p class="lede">Every Monday I break down the San Clemente, Dana Point, Capistrano Beach and Orange County housing market: prices, inventory, rates, and the local news that moves them. Real numbers, real sources, and what it means if you're thinking about selling, leasing or investing.</p>
    <div class="ctas">
      <a class="btn btn-gold" href="tel:{ROY['tel']}">Call or text {ROY['phone']}</a>
      <a class="btn btn-line" href="#talk">What's my home worth?</a>
    </div>
  </div>
</section>
<div class="wrap"><div class="posts">
{cards}
</div></div>
{lead_band("Want a market update for your own home?")}
</main>
{footer()}
</body>
</html>
"""


def homepage_block(posts):
    if not posts:
        return ""
    cards = "\n".join(card(p, level="h3") for p in posts[:3])
    return f"""<section class="band" id="market-updates" style="padding-top:0">
  <div class="wrap">
    <div class="head">
      <span class="eyebrow">Market updates</span>
      <h2>What's happening in the South OC market</h2>
      <p class="lede">A new update every Monday on San Clemente, Dana Point, Capistrano Beach and Orange County, with the numbers and sources behind it.</p>
    </div>
    <div class="posts">
{cards}
    </div>
    <div class="more"><p>Read every weekly update, or ask me what it means for your home.</p><a class="btn btn-dark" href="/market-updates/">All market updates</a></div>
  </div>
</section>"""


def update_homepage(posts):
    index = ROOT / "index.html"
    text = index.read_text(encoding="utf-8")
    start, end = "<!-- LATEST_POSTS_START -->", "<!-- LATEST_POSTS_END -->"
    if start not in text:
        return
    new = f"{start}\n{homepage_block(posts)}\n{end}"
    text = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: new, text, flags=re.S)
    index.write_text(text, encoding="utf-8")


def sitemap(posts):
    today = dt.date.today().isoformat()
    urls = [(f"{SITE}/", today, "weekly", "1.0"),
            (f"{SITE}/market-updates/", posts[0]["modified"].date().isoformat() if posts else today, "weekly", "0.9")]
    urls += [(p["url"], p["modified"].date().isoformat(), "monthly", "0.8") for p in posts]
    urls.append((f"{SITE}/privacy.html", "2026-10-15", "yearly", "0.2"))
    body = "\n".join(f"  <url><loc>{u}</loc><lastmod>{m}</lastmod><changefreq>{c}</changefreq><priority>{pr}</priority></url>"
                     for u, m, c, pr in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'


def feed(posts):
    items = "\n".join(f"""  <item>
    <title>{esc(p['title'])}</title>
    <link>{p['url']}</link>
    <guid isPermaLink="true">{p['url']}</guid>
    <pubDate>{p['published'].strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate>
    <author>{ROY['email']} (Roy Quick)</author>
    <description>{esc(p['description'])}</description>
    <enclosure url="{esc(img_url(p['image']['src'], 1200))}" type="image/jpeg" length="0"/>
  </item>""" for p in posts[:30])
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>Roy Quick Market Updates</title>
  <link>{SITE}/market-updates/</link>
  <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
  <description>Weekly San Clemente, Dana Point and South Orange County real estate market updates from Roy Quick, Realtor® with LUXRE Realty.</description>
  <language>en-us</language>
{items}
</channel>
</rss>
"""


def llms_txt(posts):
    lines = "\n".join(f"- [{p['title']}]({p['url']}): {p['description']}" for p in posts[:30])
    return f"""# Roy Quick Real Estate

> Roy Quick is a Realtor® with LUXRE Realty, Inc. (CA DRE #{ROY['dre']}) based at {ROY['street']}, {ROY['city']}, CA {ROY['zip']}. He helps homeowners in San Clemente, Dana Point, Capistrano Beach, San Juan Capistrano and the rest of South Orange County sell or lease their homes, works with real estate investors, and specializes in relisting homes that did not sell the first time. Phone/text {ROY['phone']}, email {ROY['email']}.

## Main pages
- [Home]({SITE}/): listings, expired-listing help, about Roy, LUXRE Realty, contact
- [Market Updates]({SITE}/market-updates/): weekly South OC housing market reports with cited sources

## Recent market updates
{lines}
"""


def main():
    posts = load_posts("--drafts" in sys.argv)
    OUT_DIR.mkdir(exist_ok=True)
    keep = {p["slug"] for p in posts}
    for old in OUT_DIR.iterdir():
        if old.is_dir() and old.name not in keep:
            for f in old.iterdir():
                f.unlink()
            old.rmdir()
    for p in posts:
        d = OUT_DIR / p["slug"]
        d.mkdir(exist_ok=True)
        others = [o for o in posts if o is not p]
        (d / "index.html").write_text(post_page(p, others), encoding="utf-8")
    (OUT_DIR / "index.html").write_text(index_page(posts), encoding="utf-8")
    update_homepage(posts)
    (ROOT / "sitemap.xml").write_text(sitemap(posts), encoding="utf-8")
    (ROOT / "feed.xml").write_text(feed(posts), encoding="utf-8")
    (ROOT / "llms.txt").write_text(llms_txt(posts), encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print(f"Built {len(posts)} post(s): " + ", ".join(p["slug"] for p in posts))


if __name__ == "__main__":
    main()
