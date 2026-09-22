#!/usr/bin/env python3
"""Generate on-brand Open Graph feature cards (1200x630 PNG) for pkushal.com.np.

Dark terminal theme to match the site: a title, a tag, a brand line, a byline,
and a small constellation motif that echoes the hero. Add an entry to ITEMS for
each new page/article and re-run (build.py also calls this).
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "site")
W, H = 1200, 630

# Colours (match site tokens)
BG = (10, 15, 20)
INK = (233, 240, 245)
MUTED = (150, 165, 178)
ACCENT = (92, 200, 255)
ACCENT_DIM = (47, 111, 150)
CHIP = (34, 48, 61)

# Consolas (bold mono) reads as a clean terminal face, matches the IBM Plex Mono look.
F_MONO = "C:/Windows/Fonts/consolab.ttf"
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

    # soft accent glow, top-right
    glow = Image.new("RGB", (W, H), BG)
    gd = ImageDraw.Draw(glow)
    for i, rad in enumerate(range(520, 0, -26)):
        a = int(10 * (1 - i / 20.0))
        col = (min(BG[0] + a, 255), min(BG[1] + a + 2, 255), min(BG[2] + a + 6, 255))
        gd.ellipse([W - 300 - rad, -260 - rad, W - 300 + rad, -260 + rad], fill=col)
    img = Image.blend(img, glow, 0.6)
    d = ImageDraw.Draw(img)

    constellation(d)

    PAD = 80
    # left accent bar
    d.rectangle([PAD - 16, 96, PAD - 12, 534], fill=ACCENT)

    # brand line
    fb = font(F_MONO, 26)
    d.text((PAD, 74), "~/kushal-pathak", font=fb, fill=MUTED)
    bw = d.textlength("~/kushal-pathak ", font=fb)
    d.text((PAD + bw, 74), "$", font=fb, fill=ACCENT)

    # tag chip
    ft = font(F_MONO, 22)
    label = tag.upper()
    tw = d.textlength(label, font=ft)
    d.rounded_rectangle([PAD, 150, PAD + tw + 36, 194], radius=10, outline=ACCENT_DIM, width=2)
    d.text((PAD + 18, 160), label, font=ft, fill=ACCENT)

    # title (auto-fit)
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

    # byline
    fby = font(F_MONO_R, 25)
    d.text((PAD, 556), "Kushal Pathak  ", font=fby, fill=MUTED)
    off = d.textlength("Kushal Pathak  ", font=fby)
    d.text((PAD + off, 556), "// Technical SEO Strategist", font=fby, fill=ACCENT_DIM)
    host = "pkushal.com.np"
    hw = d.textlength(host, font=fby)
    d.text((W - PAD - hw, 556), host, font=fby, fill=ACCENT)

    # bottom hairline
    d.rectangle([0, 626, W, 630], fill=ACCENT_DIM)

    out = os.path.join(OUT, out_rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out, "PNG", optimize=True)
    print("og ->", out_rel, os.path.getsize(out), "bytes")


ITEMS = [
    dict(out="assets/og-home.png", tag="Technical SEO Strategist",
         title="Rankings are an engineering problem. I do the engineering."),
    dict(out="experience/leads-from-a-sealed-iframe/og.png", tag="Experience \u00b7 Tracking",
         title="Recovering form leads from a sealed iframe into Meta"),
    dict(out="experience/server-side-tracking-with-stape/og.png", tag="Experience \u00b7 Analytics",
         title="Moving conversion tracking server-side with Stape"),
]

if __name__ == "__main__":
    for it in ITEMS:
        make(it["title"], it["tag"], it["out"])
