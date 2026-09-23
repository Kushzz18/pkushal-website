#!/usr/bin/env python3
"""Build the static site for pkushal.com.np.

Reads src/home.html (the editable page), wraps it into a standalone document
with the full SEO <head> (meta, canonical, OG/Twitter, JSON-LD, verification),
externalises the photo, and writes the deployable bundle to site/.

robots.txt is HAND-MAINTAINED at site/robots.txt (ASCII art) and is NOT
generated here. The IndexNow key file (site/<key>.txt) is also left untouched.
"""
import os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src", "home.html")
PHOTO = os.path.join(HERE, "src", "assets", "kushal.webp")
OUT = os.path.join(HERE, "site")
os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)

s = open(SRC, encoding="utf-8").read()
# Replace the inline preview photo (a base64 data URI used only for local editing)
# with the optimised, responsive band image so the page stays light on mobile.
s = re.sub(
    r'<img\b[^>]*src="data:image/webp;base64,[^"]*"[^>]*>',
    '<img src="/assets/kushal-band.webp" width="860" height="860" '
    'fetchpriority="high" decoding="async" '
    'alt="Kushal Pathak sitting by an alpine lake in the Nepal Himalaya">',
    s, count=1)
i = s.index('<header class="nav">')
head_part = s[:i]
body_part = s[i:]
head_part = head_part.replace('<title>Kushal Pathak</title>',
    '<title>Kushal Pathak, Technical SEO Strategist</title>', 1)

jsonld = ('{"@context":"https://schema.org","@graph":['
'{"@type":"Person","@id":"https://pkushal.com.np/#kushal","name":"Kushal Pathak","url":"https://pkushal.com.np/",'
'"jobTitle":"Technical SEO Strategist","image":"https://pkushal.com.np/assets/kushal.webp",'
'"worksFor":{"@type":"Organization","name":"RankMeTop","url":"https://rankmetop.net/"},'
'"alumniOf":"Bachelor of Information Technology (BIT)",'
'"knowsAbout":["Technical SEO","JavaScript Rendering","Structured Data","Indexation Strategy","Core Web Vitals","Analytics and Measurement"],'
'"address":{"@type":"PostalAddress","addressCountry":"NP"},'
'"sameAs":["https://www.linkedin.com/in/kushal-pathak-485838196/","https://github.com/Kushzz18"]},'
'{"@type":"WebSite","@id":"https://pkushal.com.np/#website","url":"https://pkushal.com.np/","name":"Kushal Pathak","publisher":{"@id":"https://pkushal.com.np/#kushal"},"inLanguage":"en"},'
'{"@type":"ProfilePage","@id":"https://pkushal.com.np/#profilepage","url":"https://pkushal.com.np/","name":"Kushal Pathak, Technical SEO Strategist","isPartOf":{"@id":"https://pkushal.com.np/#website"},"mainEntity":{"@id":"https://pkushal.com.np/#kushal"},"about":{"@id":"https://pkushal.com.np/#kushal"},"inLanguage":"en"}]}')

GTM_HEAD = (
"<!-- Google Tag Manager -->\n"
"<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':\n"
"new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],\n"
"j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=\n"
"'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);\n"
"})(window,document,'script','dataLayer','GTM-TDRG93B8');</script>\n"
"<!-- End Google Tag Manager -->\n")
GTM_NOSCRIPT = (
'<!-- Google Tag Manager (noscript) -->\n'
'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-TDRG93B8"\n'
'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n'
'<!-- End Google Tag Manager (noscript) -->\n')
HEAD_EXTRA = (
GTM_HEAD +
'<meta name="google-site-verification" content="CIKjY7k4ZzqAcKmJATjz5bCmdoRyQMdc8zQQJv7j5cg">\n'
'<meta name="description" content="Kushal Pathak, technical SEO strategist. Rendering, crawlability, structured data and Search Console forensics for sites that are indexed but not winning.">\n'
'<link rel="canonical" href="https://pkushal.com.np/">\n'
'<meta name="robots" content="index,follow,max-image-preview:large">\n'
'<meta name="theme-color" content="#0a0f14">\n'
'<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
'<meta property="og:type" content="website">\n'
'<meta property="og:site_name" content="Kushal Pathak">\n'
'<meta property="og:title" content="Kushal Pathak, Technical SEO Strategist">\n'
'<meta property="og:description" content="Rankings are an engineering problem. I do the engineering, rendering, crawlability, schema and indexation.">\n'
'<meta property="og:url" content="https://pkushal.com.np/">\n'
'<meta property="og:image" content="https://pkushal.com.np/assets/og-home.png">\n'
'<meta property="og:image:width" content="1200">\n'
'<meta property="og:image:height" content="630">\n'
'<meta property="og:image:alt" content="Kushal Pathak, Technical SEO Strategist">\n'
'<meta name="twitter:card" content="summary_large_image">\n'
'<meta name="twitter:title" content="Kushal Pathak, Technical SEO Strategist">\n'
'<meta name="twitter:description" content="Rankings are an engineering problem. I do the engineering.">\n'
'<meta name="twitter:image" content="https://pkushal.com.np/assets/og-home.png">\n'
'<style>[hidden]{display:none!important}img{max-width:100%;height:auto}</style>\n'
'<script type="application/ld+json">' + jsonld + '</script>\n')

doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
'<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
+ HEAD_EXTRA + head_part + '</head>\n<body>\n' + GTM_NOSCRIPT + body_part + '\n</body>\n</html>\n')
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(doc)

shutil.copy(PHOTO, os.path.join(OUT, "assets", "kushal.webp"))
shutil.copy(os.path.join(HERE, "src", "assets", "kushal-band.webp"),
            os.path.join(OUT, "assets", "kushal-band.webp"))

files = {}
# NOTE: robots.txt is intentionally NOT written here (hand-maintained ASCII-art file).
files["llms.txt"] = (
"# Kushal Pathak\n\n"
"> Technical SEO strategist. Rendering, crawlability, structured data and Search Console forensics for sites that are indexed but not winning.\n\n"
"Since 2024, Kushal Pathak has worked on 50+ websites across 10 countries and 20+ industries, focused on JavaScript rendering, crawl architecture, structured data, indexation strategy, analytics and measurement (GA4, Google Tag Manager, Looker Studio, BigQuery) and forensic Google Search Console diagnosis. Platform and host agnostic across WordPress, Shopify, BigCommerce, Squarespace, Wix, Webflow and custom CMS, plus Cloudflare, Cloudways, SiteGround, Kinsta, WP Engine, AWS, Hostinger, Bluehost and HostGator.\n\n"
"## Pages\n\n"
"- [Home](https://pkushal.com.np/): Overview, named frameworks, services, an interactive technical SEO lab and contact.\n"
"- [Experience](https://pkushal.com.np/experience/): First-person write-ups of real technical SEO and analytics builds.\n\n"
"## Experience articles\n\n"
"- [Moving conversion tracking server-side with Stape](https://pkushal.com.np/experience/server-side-tracking-with-stape/): Server-side GTM, first-party GA4 and Meta Conversions API deduplication, verified end to end.\n"
"- [Recovering form leads from a sealed iframe into Meta](https://pkushal.com.np/experience/leads-from-a-sealed-iframe/): Polling a CRM's GraphQL API and posting SHA-256 hashed Lead events to the Meta Conversions API from one Cloudflare Worker.\n\n"
"## Contact\n\n"
"- [Email](mailto:kushalpathak18@gmail.com): kushalpathak18@gmail.com\n"
"- [LinkedIn](https://www.linkedin.com/in/kushal-pathak-485838196/): Professional profile.\n"
"- [GitHub](https://github.com/Kushzz18): Code and tooling, including the SEO Automation Assistant.\n\n"
"## Optional\n\n"
"- [RankMeTop](https://rankmetop.net/): The agency Kushal works with.\n"
"- [Sitemap](https://pkushal.com.np/sitemap.xml): All indexable URLs.\n")

files["sitemap.xml"] = (
'<?xml version="1.0" encoding="UTF-8"?>\n'
'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
'  <url>\n'
'    <loc>https://pkushal.com.np/</loc>\n'
'    <lastmod>2026-09-22</lastmod>\n'
'    <changefreq>weekly</changefreq>\n'
'    <priority>1.0</priority>\n'
'  </url>\n'
'  <url>\n'
'    <loc>https://pkushal.com.np/experience/</loc>\n'
'    <lastmod>2026-09-22</lastmod>\n'
'    <changefreq>weekly</changefreq>\n'
'    <priority>0.8</priority>\n'
'  </url>\n'
'  <url>\n'
'    <loc>https://pkushal.com.np/experience/server-side-tracking-with-stape/</loc>\n'
'    <lastmod>2026-09-22</lastmod>\n'
'    <changefreq>monthly</changefreq>\n'
'    <priority>0.7</priority>\n'
'  </url>\n'
'  <url>\n'
'    <loc>https://pkushal.com.np/experience/leads-from-a-sealed-iframe/</loc>\n'
'    <lastmod>2026-09-22</lastmod>\n'
'    <changefreq>monthly</changefreq>\n'
'    <priority>0.7</priority>\n'
'  </url>\n'
'  <url>\n'
'    <loc>https://pkushal.com.np/experience/restricted-vertical-google-ads/</loc>\n'
'    <lastmod>2026-09-22</lastmod>\n'
'    <changefreq>monthly</changefreq>\n'
'    <priority>0.7</priority>\n'
'  </url>\n'
'  <url>\n'
'    <loc>https://pkushal.com.np/experience/legacy-domain-redirects-cloudflare-workers/</loc>\n'
'    <lastmod>2026-09-23</lastmod>\n'
'    <changefreq>monthly</changefreq>\n'
'    <priority>0.7</priority>\n'
'  </url>\n'
'  <url>\n'
'    <loc>https://pkushal.com.np/case-study/</loc>\n'
'    <lastmod>2026-09-23</lastmod>\n'
'    <changefreq>weekly</changefreq>\n'
'    <priority>0.8</priority>\n'
'  </url>\n'
'  <url>\n'
'    <loc>https://pkushal.com.np/case-study/recipe-schema/</loc>\n'
'    <lastmod>2026-09-23</lastmod>\n'
'    <changefreq>monthly</changefreq>\n'
'    <priority>0.7</priority>\n'
'  </url>\n'
'</urlset>\n')

files["favicon.svg"] = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
'<rect width="64" height="64" rx="14" fill="#0a0f14"/>'
'<text x="10" y="43" font-family="monospace" font-weight="700" font-size="30" fill="#5cc8ff">&gt;</text>'
'<rect x="35" y="23" width="15" height="20" fill="#7ee787"/></svg>')

files["404.html"] = (
'<!doctype html><html lang="en"><head><meta charset="utf-8">'
'<meta name="viewport" content="width=device-width, initial-scale=1">'
'<title>404, Not Found | Kushal Pathak</title><meta name="robots" content="noindex">'
'<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
'<style>:root{--bg:#0a0f14;--txt:#e6edf3;--muted:#8b98a5;--accent:#5cc8ff;--prompt:#7ee787}'
'*{box-sizing:border-box}body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;'
'background:var(--bg);color:var(--txt);font-family:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;padding:24px}'
'.box{max-width:560px}.p{color:var(--muted)}.c{color:var(--prompt)}.big{font-size:clamp(2.4rem,7vw,4rem);margin:0 0 10px}'
'a{color:var(--accent)}</style></head><body><div class="box">'
'<p class="p"><span class="c">$</span> curl -I pkushal.com.np/&lt;path&gt;</p>'
'<p class="big">404 <span class="p">, Not Found</span></p>'
'<p class="p">The crawler followed a link that resolves to nothing, a broken internal link. Exactly the kind of thing I fix.</p>'
'<p><span class="c">$</span> cd <a href="/">~/home</a> <span style="color:var(--prompt)">▉</span></p>'
'</div></body></html>')

files[".htaccess"] = (
"# pkushal.com.np\n"
"RewriteEngine On\n"
"RewriteCond %{HTTPS} off\n"
"RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]\n"
"RewriteCond %{HTTP_HOST} ^www\\.pkushal\\.com\\.np$ [NC]\n"
"RewriteRule ^ https://pkushal.com.np%{REQUEST_URI} [L,R=301]\n\n"
"ErrorDocument 404 /404.html\n\n"
"<IfModule mod_expires.c>\n"
"  ExpiresActive On\n"
"  ExpiresByType text/css \"access plus 1 hour\"\n"
"  ExpiresByType application/javascript \"access plus 1 hour\"\n"
"  ExpiresByType image/webp \"access plus 1 year\"\n"
"  ExpiresByType image/svg+xml \"access plus 1 year\"\n"
"</IfModule>\n"
"<IfModule mod_headers.c>\n"
"  Header set X-Content-Type-Options \"nosniff\"\n"
"  Header set Referrer-Policy \"strict-origin-when-cross-origin\"\n"
"  Header set X-Frame-Options \"SAMEORIGIN\"\n"
"</IfModule>\n")

for name, content in files.items():
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(content)

# Generate the Open Graph feature cards (homepage + every article, auto-discovered).
try:
    import og_gen
    og_gen.run()
except Exception as e:
    print("WARN: og_gen skipped:", e)

print("BUILD OK ->", OUT)
for root, _, fs in os.walk(OUT):
    for f in fs:
        p = os.path.join(root, f)
        print(str(round(os.path.getsize(p)/1024, 1)) + " KB", os.path.relpath(p, OUT))
