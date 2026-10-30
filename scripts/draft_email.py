#!/usr/bin/env python3
"""Turn a post in content/posts/ into the HTML body of Roy's approval email.

    python3 scripts/draft_email.py content/posts/2026-11-02-slug.html > email.html

Gmail drops remote images, so photos become captioned placeholders and the
CTA box becomes a note. Everything else matches the published post.
"""
import datetime as dt
import html
import json
import re
import sys

raw = open(sys.argv[1], encoding="utf-8").read()
m = re.match(r"\s*<!--(.*?)-->\s*(.*)", raw, re.S)
meta, body = json.loads(m.group(1)), m.group(2)
day = dt.date.fromisoformat(meta["date"]).strftime("%A, %B %-d")

body = body.replace("<!-- CTA -->", '<p style="background:#1c1c1e;color:#f3f1ec;padding:16px"><b>[Call-to-action box: "Want these numbers for your street?" with Call/Text and Ask-me-online buttons]</b></p>')


def photo(fig):
    alt = re.search(r'alt="([^"]*)"', fig.group(0))
    cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", fig.group(0), re.S)
    text = re.sub(r"<[^>]+>", "", cap.group(1)) if cap else ""
    return f'<p style="color:#9a7a3c"><i>[Photo: {alt.group(1) if alt else ""}. {text}]</i></p>'


body = re.sub(r"<figure>.*?</figure>", photo, body, flags=re.S)
body = re.sub(r'<div><b>(.*?)</b><span>(.*?)</span><em>(.*?)</em></div>',
              r'<div><b style="font-size:20px">\1</b> &nbsp;\2 <span style="color:#9a7a3c">(\3)</span></div>', body)
body = (body.replace('<div class="stats">', '<div style="border:1px solid #dedad1;padding:10px;background:#fff">')
        .replace('<div class="tldr">', '<div style="border-top:3px solid #c6a15b;background:#fff;padding:12px 16px">')
        .replace('<table class="tbl">', '<table border="1" cellpadding="6" style="border-collapse:collapse;border-color:#dedad1">')
        .replace('<p class="note">', '<p style="font-size:13px;color:#6d6a64">')
        .replace('href="/', 'href="https://roysoldquick.com/'))

faq = "".join(f"<p><b>{html.escape(f['q'])}</b><br>{f['a']}</p>" for f in meta.get("faq", []))
src = "".join(f'<li><a href="{s["url"]}">{html.escape(s["name"])}</a></li>' for s in meta.get("sources", []))
img = meta["image"]

print(f"""<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.6;color:#121212;max-width:680px">
<div style="background:#f6f4ef;border:1px solid #dedad1;padding:14px 18px;margin-bottom:20px">
<b>Roy, here's your Market Update draft for {day} at 12:00 PM Pacific.</b><br>
Reply <b>"post it"</b> to approve, or reply with any changes. Nothing goes live without your OK.<br>
Page title (Google): {html.escape(meta.get('seo_title') or meta['title'])}<br>
Google description: {html.escape(meta['description'])}<br>
Web address: roysoldquick.com/market-updates/{meta['slug']}/<br>
Hero photo: <a href="{img['photo_url']}">{html.escape(img['alt'])}</a> by {html.escape(img.get('credit', ''))} (free Unsplash photo, credited on the page).<br>
On the site, the post also gets your author box, a contact form, and a Call / Text / Email bar on phones.
</div>
<h1 style="font-family:Georgia,serif;font-weight:normal">{html.escape(meta['title'])}</h1>
<p style="color:#6d6a64;font-size:17px">{html.escape(meta.get('dek') or meta['description'])}</p>
<p style="color:#6d6a64">By Roy Quick, Realtor® · LUXRE Realty · {dt.date.fromisoformat(meta['date']).strftime('%B %-d, %Y')}</p>
{body}
<h2 style="font-family:Georgia,serif;font-weight:normal">Questions I hear this week</h2>{faq}
<h3>Sources</h3><ol style="font-size:13px">{src}</ol>
</div>""")
