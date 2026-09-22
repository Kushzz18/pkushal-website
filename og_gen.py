#!/usr/bin/env python3
"""Generate on-brand Open Graph feature cards (1200x630 PNG) for pkushal.com.np.

Auto-discovers every experience article under site/experience/*/index.html, reads
its share title (og:title) and tag (the eyebrow), renders a dark terminal-style
card into that folder as og.png, and makes sure the article's og:image /
twitter:image point at it. The homepage card is rendered explicitly. build.py
calls run(), so current and future articles get a card with no manual steps.
"""
import os, re, glob, math, random, html
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "site")
BASE = "https://pkushal.com.np"
W, H = 1200, 630

BG = (10, 15, 20)
INK = (233, 240, 245)
MUTED = (150, 165, 178)
ACCENT = (92, 200, 255)
ACCENT_DIM = (47, 111, 150)

F_MONO = "C:/Windows/Fonts/consolab.ttf"    # bold mono, reads like IBM Plex Mono
F_MONO_R = "C:/Windows/Fonts/consola.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def constellation(draw):
    random.seed(7)
    pts = [(random.randint(770, 1150), random.randint(60, 330)) for _ in range(18)]
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dx, dy = pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]
            if dx * dx + dy * dy < 150 * 150:
                draw.line([pts[i], pts[j]], fill=ACCENT_DIM, width=1)
    for (x, y) in pts:
        r = random.choice([2, 2, 3])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(130, 195, 235))


def make(title, tag, out_rel):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    glow = Image.new("RGB", (W, H), BG)
    gd = ImageDraw.Draw(glow)
    for i, rad in enumerate(range(520, 0, -26)):
        a = int(10 * (1 - i / 20.0))
        gd.ellipse([W - 300 - rad, -260 - rad, W - 300 + rad, -260 + rad],
                   fill=(min(BG[0] + a, 255), min(BG[1] + a + 2, 255), min(BG[2] + a + 6, 255)))
    img = Image.blend(img, glow, 0.6)
    d = ImageDraw.Draw(img)
    constellation(d)

    PAD = 80
    d.rectangle([PAD - 16, 96, PAD - 12, 534], fill=ACCENT)

    fb = font(F_MONO, 26)
    d.text((PAD, 74), "~/kushal-pathak", font=fb, fill=MUTED)
    d.text((PAD + d.textlength("~/kushal-pathak ", font=fb), 74), "$", font=fb, fill=ACCENT)

    ft = font(F_MONO, 22)
    label = tag.upper()[:44]
    tw = d.textlength(label, font=ft)
    d.rounded_rectangle([PAD, 150, PAD + tw + 36, 194], radius=10, outline=ACCENT_DIM, width=2)
    d.text((PAD + 18, 160), label, font=ft, fill=ACCENT)

    size = 68
    while size >= 40:
        ftitle = font(F_MONO, size)
        lines = wrap(d, title, ftitle, W - PAD * 2 - 30)
        lh = int(size * 1.16)
        if len(lines) * lh <= 250 and len(lines) <= 3:
            break
        size -= 4
    y = 232
    for ln in lines:
        d.text((PAD, y), ln, font=ftitle, fill=INK)
        y += lh

    fby = font(F_MONO_R, 25)
    d.text((PAD, 556), "Kushal Pathak  ", font=fby, fill=MUTED)
    d.text((PAD + d.textlength("Kushal Pathak  ", font=fby), 556), "// Technical SEO Strategist", font=fby, fill=ACCENT_DIM)
    host = "pkushal.com.np"
    d.text((W - PAD - d.textlength(host, font=fby), 556), host, font=fby, fill=ACCENT)

    d.rectangle([0, 626, W, 630], fill=ACCENT_DIM)

    out = os.path.join(OUT, out_rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out, "PNG", optimize=True)
    print("og ->", out_rel, os.path.getsize(out), "bytes")


def _meta(pattern, s):
    m = re.search(pattern, s)
    return html.unescape(m.group(1)).strip() if m else None


def _ensure_meta(path, s, og_url):
    """Point og:image / twitter:image at the card; add dimensions if missing."""
    s2 = re.sub(r'(<meta property="og:image" content=")[^"]*(">)', r'\1' + og_url + r'\2', s)
    s2 = re.sub(r'(<meta name="twitter:image" content=")[^"]*(">)', r'\1' + og_url + r'\2', s2)
    if 'og:image:width' not in s2:
        s2 = s2.replace('<meta property="og:image" content="%s">' % og_url,
                        '<meta property="og:image" content="%s">\n'
                        '<meta property="og:image:width" content="1200">\n'
                        '<meta property="og:image:height" content="630">' % og_url)
    if s2 != s:
        open(path, "w", encoding="utf-8").write(s2)
        print("   patched og meta ->", os.path.relpath(path, OUT))


def discover():
    items = []
    for path in glob.glob(os.path.join(OUT, "experience", "*", "index.html")):
        slug = os.path.basename(os.path.dirname(path))
        s = open(path, encoding="utf-8").read()
        title = _meta(r'<meta property="og:title" content="([^"]+)"', s) \
            or _meta(r'<h1[^>]*>(.*?)</h1>', re.sub(r'<[^>]+>', '', s))
        tag = _meta(r'<p class="eyebrow">(.*?)</p>', s) or "Experience"
        tag = re.sub(r'<[^>]+>', '', tag)
        out_rel = os.path.join("experience", slug, "og.png")
        items.append((title, tag, out_rel, path, "%s/experience/%s/og.png" % (BASE, slug)))
    return items


def run():
    # homepage
    make("Rankings are an engineering problem. I do the engineering.",
         "Technical SEO Strategist", "assets/og-home.png")
    # every experience article, auto-discovered
    for title, tag, out_rel, path, og_url in discover():
        make(title, tag, out_rel)
        _ensure_meta(path, open(path, encoding="utf-8").read(), og_url)


if __name__ == "__main__":
    run()
