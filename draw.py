#!/usr/bin/env python3
"""Draw the news-image-20261120 front page with PIL (build-time only).

Renders a 1024x1024 broadsheet: cream paper, giant serif date masthead,
6-cell numbers strip, region chips, 3 illustrated lead cards + 10 small
cards (13 drawn cards), a dark world map with numbered pins and a full
legend, numbered briefs, a red-framed DATE CHECK strip and a sources
footer. Deterministic: same inputs always produce the same PNG bytes
(no timestamps, no randomness, fixed font paths).

Run locally:  python3 draw.py   -> writes entry.png next to this file.
The grading entrypoint is main.py, which only copies entry.png.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

# --- palette -------------------------------------------------------------
CREAM = (247, 240, 220)
CREAM_DK = (238, 229, 203)
PAPER = (255, 253, 246)      # card faces
INK = (25, 23, 19)
INK_SOFT = (74, 70, 60)
RED = (166, 30, 34)
RED_DK = (140, 22, 26)
NAVY = (22, 38, 63)          # map panel
NAVY_LT = (51, 71, 94)       # map land
NAVY_LN = (96, 126, 158)     # map land outline
GOLD = (176, 141, 58)
TEAL = (36, 110, 118)
GREY = (120, 114, 100)

# --- fonts ---------------------------------------------------------------
FONT_DIR = "/usr/share/fonts/truetype/noto"
SERIF = os.path.join(FONT_DIR, "NotoSerif-Regular.ttf")
SERIF_B = os.path.join(FONT_DIR, "NotoSerif-Bold.ttf")
SERIF_I = os.path.join(FONT_DIR, "NotoSerif-Italic.ttf")
SERIF_BI = os.path.join(FONT_DIR, "NotoSerif-BoldItalic.ttf")
SANS = os.path.join(FONT_DIR, "NotoSans-Regular.ttf")
SANS_B = os.path.join(FONT_DIR, "NotoSans-Bold.ttf")
SANS_I = os.path.join(FONT_DIR, "NotoSans-Italic.ttf")


def F(path, size):
    return ImageFont.truetype(path, size)


# --- text helpers --------------------------------------------------------
def wrap(d, text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, font, fill, max_w, leading, max_lines=None,
               align="left"):
    """Draw wrapped text; returns (lines_used, bottom_y)."""
    lines = wrap(d, text, font, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, line in enumerate(lines):
        lx = x
        if align == "center":
            lx = x + (max_w - d.textlength(line, font=font)) / 2
        d.text((lx, y + i * leading), line, font=font, fill=fill)
    return len(lines), y + len(lines) * leading


def spaced(d, cx, y, text, font, fill, tracking=3):
    """Draw letter-spaced caps centred on cx; returns width used."""
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill)
        x += w + tracking
    return total


def rule(d, x0, y, x1, width=1, fill=INK):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def tag(d, x, y, text, font, fill=RED, bg=None):
    """Small caps label; returns width."""
    w = d.textlength(text, font=font)
    if bg is not None:
        d.rectangle([x - 3, y - 1, x + w + 3, y + font.size + 2], fill=bg)
    d.text((x, y), text, font=font, fill=fill)
    return w


# --- canvas --------------------------------------------------------------
img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)
MX = 14                      # outer margin
RX = W - MX                  # right edge of content (1010)

# double frame
d.rectangle([8, 8, W - 9, H - 9], outline=INK, width=2)
d.rectangle([11, 11, W - 12, H - 12], outline=INK, width=1)

# --- masthead ------------------------------------------------------------
# kicker
spaced(d, W // 2, 26, "THE WORLD IN ONE DAY", F(SANS_B, 13), INK, tracking=4)
rule(d, 120, 33, 330, 1)
rule(d, W - 330, 33, W - 120, 1)
# giant serif date
date_font = F(SERIF_B, 54)
d.text(((W - d.textlength("FRIDAY 20 NOVEMBER 2026", font=date_font)) / 2,
        42), "FRIDAY 20 NOVEMBER 2026", font=date_font, fill=INK)
# red italic sub-headline: the three leads
sub = ("Cyclone Akvan strikes Odisha  —  Kyiv hit by 110+ missiles  —  "
       "COP31 deadlocked on its final day")
sub_font = F(SERIF_I, 17)
d.text(((W - d.textlength(sub, font=sub_font)) / 2, 102), sub,
       font=sub_font, fill=RED)
rule(d, MX, 128, RX, 2)
# story-count line
cnt_font = F(SANS_B, 11)
cnt = "40 STORIES  •  6 CONTINENTS  •  ONE PAGE  •  EVERY FIGURE ATTRIBUTED"
d.text(((W - d.textlength(cnt, font=cnt_font)) / 2, 136), cnt,
       font=cnt_font, fill=INK_SOFT)

# --- numbers strip: 6 verified Friday figures ---------------------------
NUMBERS = [
    ("300,000+", "EVACUATED AHEAD OF AKVAN", "IMD"),
    ("27", "BALLISTIC OF 110+ AT KYIV", "ZELENSKY"),
    ("-4.8%", "NIKKEI — ASIA AI SELL-OFF", "REUTERS"),
    ("35 by 35", "COP31 GOAL — 75 NATIONS", "UN NEWS"),
    ("2.2%", "JAPAN CORE CPI — 2026 HIGH", "REUTERS"),
    ("$48.3bn", "US WAR COST IN IRAN", "PENTAGON"),
]
ny0, ny1 = 158, 214
cw = (RX - MX - 5 * 6) / 6
for i, (num, lab, src) in enumerate(NUMBERS):
    x0 = MX + i * (cw + 6)
    d.rectangle([x0, ny0, x0 + cw, ny1], outline=INK, width=1, fill=PAPER)
    nf = F(SERIF_B, 25)
    d.text((x0 + cw / 2 - d.textlength(num, font=nf) / 2, ny0 + 4), num,
           font=nf, fill=RED_DK if i in (0, 1, 2) else INK)
    lf = F(SANS_B, 8)
    d.text((x0 + cw / 2 - d.textlength(lab, font=lf) / 2, ny0 + 33), lab,
           font=lf, fill=INK)
    sf = F(SANS, 7)
    d.text((x0 + cw / 2 - d.textlength("SRC: " + src, font=sf) / 2, ny1 - 11),
           "SRC: " + src, font=sf, fill=GREY)

# --- region chips ----------------------------------------------------------
CHIPS = [("EUROPE", 8), ("AMERICAS", 7), ("ASIA-PACIFIC", 11),
         ("MIDDLE EAST", 4), ("AFRICA", 4), ("OCEANIA", 3), ("WORLD", 3)]
cf = F(SANS_B, 10)
chip_w = []
for name, n in CHIPS:
    chip_w.append(d.textlength(name + " " + str(n), font=cf) + 16)
total_w = sum(chip_w) + 8 * (len(CHIPS) - 1)
x = (W - total_w) / 2
cy = 222
for (name, n), w in zip(CHIPS, chip_w):
    d.rounded_rectangle([x, cy, x + w, cy + 17], radius=8, outline=INK, width=1)
    d.text((x + 8, cy + 3), name + " ", font=cf, fill=INK)
    d.text((x + 8 + d.textlength(name + " ", font=cf), cy + 3), str(n),
           font=cf, fill=RED)
    x += w + 8

# --- lead illustrations ----------------------------------------------------
def draw_kyiv(box):
    """Night Kyiv skyline, missile trails, red flashes. box=(x0,y0,x1,y1)."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(13, 22, 42))
    # stars
    for sx, sy in [(30, 12), (90, 8), (150, 18), (210, 10), (260, 20),
                   (60, 30), (180, 28), (300, 14)]:
        d.ellipse([x0 + sx - 1, y0 + sy - 1, x0 + sx + 1, y0 + sy + 1],
                  fill=(220, 225, 240))
    # moon
    d.ellipse([x0 + 268, y0 + 10, x0 + 292, y0 + 34], fill=(240, 232, 200))
    # missile trails: curved polylines (stay inside the box), red heads
    for (tx0, ty0, tx1, ty1) in [(40, 78, 150, 22), (120, 84, 220, 30),
                                 (200, 80, 285, 40)]:
        mx, my = (tx0 + tx1) / 2, min(ty0, ty1) - 18
        pts = []
        for t in range(0, 11):
            tt = t / 10
            px = (1 - tt) ** 2 * tx0 + 2 * (1 - tt) * tt * mx + tt ** 2 * tx1
            py = (1 - tt) ** 2 * ty0 + 2 * (1 - tt) * tt * my + tt ** 2 * ty1
            pts.append((x0 + px, y0 + py))
        d.line(pts, fill=(255, 255, 255), width=2)
        d.ellipse([x0 + tx1 - 3, y0 + ty1 - 3, x0 + tx1 + 3, y0 + ty1 + 3],
                  fill=(255, 80, 60))
    # skyline silhouettes
    base = y1
    for bx, bw, bh in [(0, 42, 46), (44, 30, 62), (76, 36, 40),
                       (114, 26, 70), (142, 40, 52), (184, 30, 64),
                       (216, 34, 44), (252, 38, 58), (292, 34, 48)]:
        d.rectangle([x0 + bx, base - bh, x0 + bx + bw, base], fill=(8, 13, 26))
        # lit windows
        for wy in range(base - bh + 8, base - 6, 12):
            for wx in range(bx + 6, bx + bw - 4, 10):
                if (wx * 7 + wy * 3) % 5 == 0:
                    d.rectangle([x0 + wx, wy, x0 + wx + 3, wy + 4],
                                fill=(255, 200, 90))
    # bridge arc over the river line
    d.arc([x0 + 90, base - 26, x0 + 240, base + 14], start=180, end=360,
          fill=(200, 60, 50), width=3)
    d.line([x0, base - 2, x1, base - 2], fill=(60, 90, 140), width=2)


def draw_akvan(box):
    """Bay of Bengal coast with a cyclone spiral over Gopalpur."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(24, 96, 128))
    # land (India east coast) on the left
    land = [(x0, y0 + 90), (x0 + 70, y0 + 78), (x0 + 95, y0 + 55),
            (x0 + 88, y0 + 30), (x0 + 60, y0 + 12), (x0, y0 + 8)]
    d.polygon(land, fill=(214, 196, 150))
    d.line(land + [land[0]], fill=(120, 100, 60), width=1)
    # coastline label
    d.text((x0 + 8, y0 + 62), "ODISHA", font=F(SANS_B, 8), fill=(90, 70, 40))
    # cyclone spiral: concentric arcs, white/teal
    cx, cy = x0 + 205, y0 + 44
    for r, col in [(44, (255, 255, 255)), (35, (200, 235, 240)),
                   (26, (255, 255, 255)), (17, (180, 225, 235)),
                   (9, (255, 255, 255))]:
        d.arc([cx - r, cy - r, cx + r, cy + r], start=20, end=300,
              fill=col, width=4)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 255))
    # landfall marker + dark label band at the bottom
    d.ellipse([cx - 52, cy + 26, cx - 44, cy + 34], fill=RED)
    d.line([cx - 48, cy + 30, cx - 8, cy + 30], fill=RED, width=2)
    d.rectangle([x0 + 6, y0 + 70, x0 + 152, y0 + 85], fill=(10, 40, 55))
    d.text((x0 + 10, y0 + 73), "GOPALPUR  •  LANDFALL 07:30 IST",
           font=F(SANS_B, 8), fill=(255, 255, 255))


def draw_cop31(box):
    """Globe with meridians + red thermometer, Antalya skyline strip."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(18, 52, 74))
    # globe
    cx, cy, r = x0 + 78, y0 + 46, 36
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(46, 130, 110))
    for k in range(-2, 3):
        d.arc([cx - r + abs(k) * 11, cy - r, cx + r - abs(k) * 11, cy + r],
              start=90 if k < 0 else 270, end=270 if k < 0 else 90,
              fill=(200, 235, 225), width=1)
    d.line([cx - r, cy, cx + r, cy], fill=(200, 235, 225), width=1)
    d.ellipse([cx - 16, cy - 24, cx - 2, cy - 10], fill=(120, 200, 140))
    d.ellipse([cx + 4, cy + 6, cx + 20, cy + 22], fill=(120, 200, 140))
    # thermometer
    tx = x0 + 168
    d.rounded_rectangle([tx, y0 + 12, tx + 16, y0 + 70], radius=8,
                        outline=(255, 255, 255), width=2)
    d.rectangle([tx + 3, y0 + 36, tx + 13, y0 + 68], fill=RED)
    d.ellipse([tx - 4, y0 + 64, tx + 20, y0 + 86], fill=RED)
    d.text((tx + 24, y0 + 18), "+1.5°C", font=F(SANS_B, 11),
           fill=(255, 255, 255))
    d.text((tx + 24, y0 + 36), "LIMIT", font=F(SANS_B, 9),
           fill=(200, 220, 235))
    # flags strip: many small flags = deadlocked talks
    for i in range(7):
        fx = x0 + 218 + i * 15
        d.line([fx, y0 + 20, fx, y0 + 52], fill=(220, 220, 210), width=1)
        d.polygon([(fx, y0 + 20), (fx + 12, y0 + 24), (fx, y0 + 28)],
                  fill=[(200, 60, 50), (240, 200, 60), (60, 120, 200),
                        (80, 160, 90), (220, 140, 40), (150, 80, 180),
                        (230, 230, 230)][i])
    d.text((x0 + 218, y0 + 58), "ANTALYA", font=F(SANS_B, 9),
           fill=(255, 255, 255))

# --- lead cards ------------------------------------------------------------
LEADS = [
    ("01", "KYIV", "RUSSIA'S KYIV BARRAGE",
     "110+ missiles, 27 ballistic — 3 Dnipro bridges hit in the war's "
     "biggest bridge attack. 3 killed in Kyiv, 8 across Ukraine.",
     "ZELENSKY • KYIV POST — OFFICIALS SAY", draw_kyiv),
    ("02", "AKVAN", "CYCLONE AKVAN MAKES LANDFALL",
     "Severe storm crosses near Gopalpur, Odisha, 07:30 IST. Winds "
     "70–80 km/h, gusts 90. 300,000+ moved to shelters; no deaths yet.",
     "IMD • THE HINDU — REPORTED", draw_akvan),
    ("03", "COP31", "COP31 DEADLOCK ON FINAL DAY",
     "Antalya talks enter the last day with fossil-fuel language "
     "stripped and the $120bn adaptation target dropped. 21 issues open.",
     "UN NEWS • REUTERS — REPORTED", draw_cop31),
]
ly0, ly1 = 244, 436
lw = (RX - MX - 2 * 9) / 3
for i, (num, kick, head, deck, src, art) in enumerate(LEADS):
    x0 = MX + i * (lw + 9)
    d.rectangle([x0, ly0, x0 + lw, ly1], outline=INK, width=2, fill=PAPER)
    art((x0 + 1, ly0 + 1, x0 + lw - 1, ly0 + 88))
    d.rectangle([x0, ly0 + 88, x0 + lw, ly0 + 88], outline=INK, width=1)
    # number badge
    d.rectangle([x0 + 8, ly0 + 94, x0 + 34, ly0 + 110], fill=RED)
    d.text((x0 + 13, ly0 + 96), num, font=F(SANS_B, 11), fill=(255, 255, 255))
    tag(d, x0 + 40, ly0 + 97, kick, F(SANS_B, 10))
    text_block(d, x0 + 8, ly0 + 114, head, F(SERIF_B, 16), INK, lw - 16, 19,
               max_lines=1)
    text_block(d, x0 + 8, ly0 + 136, deck, F(SANS, 10), INK_SOFT, lw - 16, 12,
               max_lines=3)
    sf = F(SANS_B, 7)
    d.text((x0 + 8, ly1 - 12), src, font=sf, fill=GREY)

# --- small-card mini illustrations -----------------------------------------
def mini_chart(box, down=True):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(250, 244, 228))
    pts = [(x0 + 8 + i * 22, y0 + (10 if down else 30) + (i * 3 if down else -i * 3))
           for i in range(8)]
    d.line(pts, fill=RED, width=2)
    for px, py in pts:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    d.line([x0 + 4, y1 - 6, x1 - 4, y1 - 6], fill=GREY, width=1)


def mini_flags(box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(250, 244, 228))
    # UK flag block + EU circle of stars, side by side
    d.rectangle([x0 + 12, y0 + 8, x0 + 62, y0 + 30], fill=(30, 50, 110))
    d.line([x0 + 12, y0 + 8, x0 + 62, y0 + 30], fill=(255, 255, 255), width=2)
    d.line([x0 + 62, y0 + 8, x0 + 12, y0 + 30], fill=(255, 255, 255), width=2)
    d.rectangle([x0 + 92, y0 + 8, x0 + 142, y0 + 30], fill=(20, 50, 130))
    for k in range(8):
        import math
        a = math.pi * k / 4
        sx, sy = x0 + 117 + 9 * math.cos(a), y0 + 19 + 8 * math.sin(a)
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 220, 60))


def mini_planet(box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(16, 20, 34))
    cx, cy, r = x0 + 34, y0 + 20, 15
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 120, 60))
    for ox, oy, orad in [(28, 14, 3), (40, 24, 2), (30, 26, 2)]:
        d.ellipse([x0 + ox - orad, y0 + oy - orad, x0 + ox + orad,
                   y0 + oy + orad], fill=(160, 90, 40))
    d.ellipse([x0 + 78, y0 + 8, x0 + 84, y0 + 14], fill=(255, 255, 255))
    d.ellipse([x0 + 96, y0 + 26, x0 + 100, y0 + 30], fill=(220, 220, 220))
    d.text((x0 + 58, y0 + 12), "8 YRS", font=F(SANS_B, 9),
           fill=(255, 220, 120))


def mini_bars(box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(250, 244, 228))
    vals = [14, 18, 22, 26]
    for i, v in enumerate(vals):
        bx = x0 + 16 + i * 32
        d.rectangle([bx, y0 + 36 - v, bx + 18, y0 + 36], fill=INK)
    d.rectangle([x0 + 16 + 3 * 32, y0 + 36 - 26, x0 + 16 + 3 * 32 + 18,
                 y0 + 36], fill=RED)


def mini_tanker(box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(30, 90, 110))
    d.polygon([(x0 + 20, y0 + 22), (x0 + 140, y0 + 22), (x0 + 128, y0 + 34),
               (x0 + 32, y0 + 34)], fill=(40, 40, 44))
    d.rectangle([x0 + 60, y0 + 12, x0 + 84, y0 + 22], fill=(200, 200, 190))
    d.polygon([(x0 + 96, y0 + 6), (x0 + 104, y0 + 16), (x0 + 96, y0 + 16)],
              fill=(255, 180, 40))
    d.line([x0 + 100, y0 + 2, x0 + 100, y0 + 10], fill=(255, 120, 40), width=2)


def mini_line(box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(250, 244, 228))
    d.line([x0 + 10, y0 + 30, x0 + 150, y0 + 30], fill=INK, width=2)
    for lx in (40, 80, 120):
        d.line([x0 + lx, y0 + 30, x0 + lx, y0 + 20], fill=INK, width=1)
    d.text((x0 + 12, y0 + 8), "YELLOW LINE", font=F(SANS_B, 9), fill=INK)


def mini_strike(box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(250, 244, 228))
    d.rectangle([x0 + 14, y0 + 12, x0 + 146, y0 + 26], fill=RED)
    d.text((x0 + 22, y0 + 15), "24-HOUR STRIKE", font=F(SANS_B, 10),
           fill=(255, 255, 255))
    for px in (30, 70, 110):
        d.line([x0 + px, y0 + 28, x0 + px + 14, y0 + 36], fill=INK, width=2)


def mini_vote(box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(250, 244, 228))
    d.rectangle([x0 + 20, y0 + 10, x0 + 66, y0 + 30], fill=(30, 80, 160))
    d.text((x0 + 30, y0 + 14), "VOTE", font=F(SANS_B, 11),
           fill=(255, 255, 255))
    d.rectangle([x0 + 94, y0 + 10, x0 + 140, y0 + 30], fill=INK)
    d.text((x0 + 100, y0 + 14), "3RD", font=F(SANS_B, 11),
           fill=(255, 220, 60))


def mini_boat(box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(24, 96, 128))
    d.arc([x0 + 40, y0 + 14, x0 + 120, y0 + 32], start=0, end=180,
          fill=(230, 200, 140), width=3)
    for wx in (30, 70, 110, 140):
        d.arc([x0 + wx, y0 + 22, x0 + wx + 22, y0 + 32], start=0, end=180,
              fill=(255, 255, 255), width=1)


def mini_drought(box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(232, 214, 160))
    d.ellipse([x0 + 66, y0 + 6, x0 + 94, y0 + 34], fill=(255, 200, 60))
    for cx in (20, 60, 100, 130):
        d.line([x0 + cx, y0 + 32, x0 + cx + 8, y0 + 26], fill=(150, 110, 50),
               width=2)
        d.line([x0 + cx + 8, y0 + 26, x0 + cx + 16, y0 + 32], fill=(150, 110, 50),
               width=2)

# --- small cards: 04–13 -----------------------------------------------------
SMALL = [
    ("04", "ASIA AI SELL-OFF", "Nikkei −4.8%, KOSPI −5.2%, Taiex −6.2%. "
     "Worst week since 2020.", "REUTERS", mini_chart),
    ("05", "UK–EU RESET DEAL", "Youth mobility, food trade, carbon "
     "markets — sealed in Brussels.", "BRUSSELS", mini_flags),
    ("06", "BEPICOLOMBO ARRIVES", "ESA/JAXA probe enters Mercury orbit "
     "after 8 years. Only the 2nd ever.", "ESA / JAXA", mini_planet),
    ("07", "JAPAN INFLATION 2.2%", "Core CPI highest this year. BoJ "
     "December hike still on track.", "REUTERS", mini_bars),
    ("08", "HORMUZ TANKER FIRE", "Tanker burns after hitting a mine. "
     "Brent ~$92; IEA confidence hit.", "REUTERS", mini_tanker),
    ("09", "GAZA: YELLOW LINE", "Israeli troops cross the line in "
     "central Gaza — first since truce.", "AP", mini_line),
    ("10", "ITALY GENERAL STRIKE", "CGIL calls 24-hour stoppage across "
     "Italy over pay and jobs.", "ANSA", mini_strike),
    ("11", "BUKELE SEEKS 3RD TERM", "El Salvador president registers "
     "for another term in office.", "AP", mini_vote),
    ("12", "SENEGAL BOAT SINKS", "Migrant boat capsizes off Yenne; "
     "4 dead, dozens missing.", "AP", mini_boat),
    ("13", "FIJI DROUGHT EMERGENCY", "El Niño drought: Fiji declares "
     "disaster; Tonga follows.", "RNZ", mini_drought),
]
sy_rows = [(444, 548), (556, 660)]
sw = (RX - MX - 4 * 9) / 5
for r, (ry0, ry1) in enumerate(sy_rows):
    for c in range(5):
        num, head, deck, src, art = SMALL[r * 5 + c]
        x0 = MX + c * (sw + 9)
        d.rectangle([x0, ry0, x0 + sw, ry1], outline=INK, width=1, fill=PAPER)
        art((x0 + 1, ry0 + 1, x0 + sw - 1, ry0 + 36))
        d.rectangle([x0, ry0 + 36, x0 + sw, ry0 + 36], outline=INK, width=1)
        d.rectangle([x0 + 6, ry0 + 42, x0 + 28, ry0 + 56], fill=RED)
        d.text((x0 + 10, ry0 + 44), num, font=F(SANS_B, 9),
               fill=(255, 255, 255))
        text_block(d, x0 + 6, ry0 + 58, head, F(SERIF_B, 11), INK, sw - 12, 13,
                   max_lines=1)
        text_block(d, x0 + 6, ry0 + 72, deck, F(SANS, 8), INK_SOFT, sw - 12, 9,
                   max_lines=2)
        d.text((x0 + 6, ry1 - 11), src, font=F(SANS_B, 6.5), fill=GREY)

# --- world map: dark panel, numbered pins, full legend ----------------------
MAP_Y0, MAP_Y1 = 668, 792
d.rectangle([MX, MAP_Y0, RX, MAP_Y1], fill=NAVY)
d.rectangle([MX, MAP_Y0, RX, MAP_Y1], outline=INK, width=2)
map_font = F(SANS_B, 11)
d.text((MX + 8, MAP_Y0 + 4), "WHERE IT HAPPENED", font=map_font,
       fill=(255, 255, 255))
d.text((RX - 8 - d.textlength("RED NUMBERS MARK STORIES 01–13  •  POSITIONS APPROXIMATE",
                              font=F(SANS, 8)), MAP_Y0 + 6),
       "RED NUMBERS MARK STORIES 01–13  •  POSITIONS APPROXIMATE",
       font=F(SANS, 8), fill=(180, 200, 220))

# simplified continents (lon, lat), equirectangular
CONTINENTS = {
    "NA": [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 68),
           (-100, 69), (-90, 68), (-82, 66), (-78, 71), (-70, 62),
           (-60, 55), (-55, 47), (-60, 45), (-68, 44), (-70, 41),
           (-74, 38), (-76, 34), (-80, 26), (-81, 25), (-84, 30),
           (-89, 29), (-91, 19), (-95, 16), (-100, 17), (-105, 20),
           (-110, 23), (-114, 29), (-120, 34), (-124, 40), (-124, 48),
           (-130, 55), (-140, 60), (-150, 60), (-158, 58), (-165, 60)],
    "GL": [(-55, 60), (-45, 60), (-40, 66), (-32, 70), (-25, 72),
           (-30, 76), (-45, 76), (-55, 74), (-60, 70), (-58, 64)],
    "SA": [(-79, 9), (-77, 5), (-80, -2), (-81, -6), (-77, -12),
           (-72, -18), (-70, -23), (-70, -32), (-73, -40), (-73, -46),
           (-70, -52), (-66, -55), (-68, -50), (-63, -41), (-58, -34),
           (-52, -33), (-48, -27), (-42, -23), (-38, -15), (-35, -8),
           (-38, -4), (-43, -3), (-48, 0), (-51, 4), (-55, 6),
           (-60, 9), (-66, 10), (-72, 12), (-77, 8)],
    "AF": [(-17, 15), (-16, 21), (-11, 28), (-6, 33), (-1, 35), (9, 37),
           (11, 34), (19, 32), (25, 32), (30, 31), (33, 27), (35, 23),
           (37, 18), (40, 15), (43, 11), (48, 11), (51, 11), (46, 5),
           (41, 0), (40, -8), (37, -14), (35, -20), (32, -27), (27, -33),
           (20, -35), (17, -32), (15, -27), (13, -20), (12, -15),
           (13, -10), (10, -4), (9, 1), (9, 4), (4, 6), (-3, 5),
           (-8, 5), (-13, 8), (-16, 12)],
    "EU": [(-10, 36), (-9, 38), (-9, 43), (-4, 44), (-2, 47), (-4, 48),
           (-1, 49), (1, 51), (3, 53), (5, 53), (7, 55), (8, 57),
           (10, 59), (6, 60), (5, 62), (10, 62), (14, 65), (18, 69),
           (22, 70), (26, 71), (30, 70), (32, 69), (36, 66), (40, 66),
           (42, 65), (40, 61), (35, 59), (30, 60), (28, 58), (24, 58),
           (21, 55), (18, 54), (14, 54), (10, 54), (8, 55), (8, 57),
           (5, 58), (2, 57), (0, 53), (-2, 50), (-5, 48), (-8, 44),
           (-10, 39)],
    "AS": [(30, 60), (40, 67), (50, 69), (60, 69), (70, 71), (80, 73),
           (90, 75), (100, 77), (110, 74), (120, 72), (130, 71),
           (140, 71), (150, 70), (160, 67), (170, 66), (178, 64),
           (170, 60), (162, 58), (158, 52), (150, 59), (142, 50),
           (140, 40), (135, 34), (128, 34), (124, 39), (120, 32),
           (115, 24), (109, 19), (105, 9), (100, 8), (97, 14),
           (92, 21), (87, 22), (82, 18), (80, 10), (76, 9), (73, 17),
           (69, 22), (64, 25), (58, 26), (54, 27), (50, 29), (47, 30),
           (43, 28), (40, 24), (37, 20), (35, 16), (38, 12), (43, 12),
           (48, 14), (52, 18), (56, 22), (58, 25), (54, 26), (50, 25),
           (46, 24), (42, 21), (39, 21), (36, 26), (34, 28), (31, 29),
           (30, 31), (33, 32), (36, 36), (33, 36), (30, 36), (28, 38),
           (26, 41), (28, 44), (30, 46), (33, 48), (36, 50), (40, 53),
           (44, 56), (47, 58), (45, 59), (40, 59), (35, 59), (30, 60)],
    "AU": [(114, -22), (114, -30), (116, -35), (120, -34), (124, -33),
           (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
           (145, -38), (150, -37), (153, -31), (153, -27), (150, -23),
           (146, -19), (142, -11), (140, -17), (136, -14), (132, -11),
           (129, -14), (126, -14), (122, -17), (118, -20)],
    "NZ": [(167, -45), (170, -43), (174, -41), (177, -38), (176, -37),
           (173, -40), (170, -42), (167, -45)],
}
MAP_X0, MAP_X1 = MX + 6, RX - 6
MAP_TOP, MAP_BOT = MAP_Y0 + 22, MAP_Y1 - 26
LON0, LON1, LAT0, LAT1 = -170, 190, 75, -58


def project(lon, lat):
    px = MAP_X0 + (lon - LON0) / (LON1 - LON0) * (MAP_X1 - MAP_X0)
    py = MAP_TOP + (LAT0 - lat) / (LAT0 - LAT1) * (MAP_BOT - MAP_TOP)
    return px, py


for poly in CONTINENTS.values():
    pts = [project(lon, lat) for lon, lat in poly]
    d.polygon(pts, fill=NAVY_LT, outline=NAVY_LN)

# numbered pins 1–13 with hairline leaders to tiny labels
PINS = [
    (1, 30.5, 50.4, "KYIV"), (2, 84.9, 19.3, "GOPALPUR"),
    (3, 30.7, 36.9, "ANTALYA"), (4, 127.0, 37.5, "SEOUL"),
    (5, 4.4, 50.8, "BRUSSELS"), (6, 12.0, 49.9, "DARMSTADT"),
    (7, 139.7, 35.7, "TOKYO"), (8, 56.5, 26.5, "HORMUZ"),
    (9, 34.5, 31.5, "GAZA"), (10, 16.0, 41.9, "ROME"),
    (11, -89.2, 13.7, "SAN SALVADOR"), (12, -17.4, 14.7, "DAKAR"),
    (13, 178.0, -17.7, "FIJI"),
]
pin_font = F(SANS_B, 8)
lab_font = F(SANS_B, 7)
LABELLED = {2, 4, 7, 8, 11, 12, 13}   # Europe/Med pins stay numbers-only
for num, lon, lat, name in PINS:
    px, py = project(lon, lat)
    if num in LABELLED:
        lw = d.textlength(name, font=lab_font)
        if py - 24 >= MAP_TOP + 2:
            # label above the pin
            d.line([px, py - 6, px, py - 14], fill=(255, 255, 255), width=1)
            d.text((px - lw / 2, py - 24), name, font=lab_font,
                   fill=(220, 230, 240))
        else:
            # label below the pin (pin sits near the top edge)
            d.line([px, py + 6, px, py + 10], fill=(255, 255, 255), width=1)
            d.text((px - lw / 2, py + 12), name, font=lab_font,
                   fill=(220, 230, 240))
    d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED,
              outline=(255, 255, 255), width=1)
    nw = d.textlength(str(num), font=pin_font)
    d.text((px - nw / 2, py - 5), str(num), font=pin_font,
           fill=(255, 255, 255))
# legend row inside the panel
leg_y = MAP_Y1 - 20
leg_font = F(SANS, 8)
legend = ("1 Kyiv  •  2 Gopalpur  •  3 Antalya  •  4 Seoul  •  5 Brussels  •  "
          "6 Darmstadt  •  7 Tokyo  •  8 Hormuz  •  9 Gaza  •  10 Rome  •  "
          "11 San Salvador  •  12 Dakar  •  13 Fiji")
d.text(((W - d.textlength(legend, font=leg_font)) / 2, leg_y), legend,
       font=leg_font, fill=(200, 215, 230))

# --- numbered briefs 14–40 (two columns) ----------------------------------
BRIEFS = [
    "Berlin: Ukraine allies meet; Kushner says Trump open to NATO-style guarantee — Reuters",
    "Haiti forces kill 34 gang members in Martissant raid — AP",
    "Sudan drone strike kills 10 at Bajoun gold mine — Reuters",
    "Ethiopia–Eritrea drone and artillery strikes near Badme — AP",
    "Iraq orders Kataib Hezbollah out of Jurf al-Nasr by Friday — Reuters",
    "Denmark ratifies Greenland security deal with the US — AP",
    "IMF warns global debt will near 100% of GDP — Reuters",
    "GTA VI first-day sales pass $2.3bn (launch was Thursday) — Sensor Tower",
    "Cancer pill shrinks tumours 60.7% in early trial — Reuters",
    "Phillips 118: first NZ batter with centuries in all 3 formats — AP",
    "Suneung exam: 111 caught cheating in South Korea — Yonhap",
    "Trump pardons Pete Rose, posthumous — AP",
    "White House fires cyber director Sean Cairncross — Reuters",
    "Mongolia president Khürelsükh resigns — AP",
    "UN secretary-general race stalls after 8th vote — UN News",
    "California probes Nvidia over AI chips in China — Reuters",
    "PBOC holds rates an 18th month; gold −4.2%, Brent ~$92 — Reuters",
    "Voyager 1 reaches one light-day from Earth — NASA *",
    "Tonga declares drought emergency ahead of Cyclone Xavier — RNZ",
    "Cook Islands declare emergency as El Niño drought bites — RNZ",
    "Young people strike in 25+ countries for climate — AP",
    "Berlin youth rally against conscription — dpa",
    "Anthropic shares fall in second session after $81.3bn IPO — Reuters",
    "Bitcoin ~$62k as crypto slides with the tech rout — Reuters",
    "US approved 879,000 AI chips for Chinese firms — Reuters",
    "Yen nears 159 per dollar; BoJ December hike on track — Reuters",
    "Las Vegas GP: Russell takes pole for Saturday's race — AP",
]
bf = F(SANS, 8)
bf_b = F(SANS_B, 8)
by0, by1 = 800, 922
col_w = (RX - MX - 16) / 2
left = BRIEFS[:14]
right = BRIEFS[14:]
for col, items in enumerate((left, right)):
    cx = MX + col * (col_w + 16)
    for j, text in enumerate(items):
        y = by0 + j * 9
        if y > by1:
            break
        num = str(14 + col * 14 + j)
        d.text((cx, y), num + ".", font=bf_b, fill=RED)
        nx = cx + d.textlength("00. ", font=bf_b)
        # truncate to one line
        while d.textlength(text, font=bf) > col_w - (nx - cx) and len(text) > 4:
            text = text[:-2]
        d.text((nx, y), text, font=bf, fill=INK)
d.text((MX, by1 + 2), "* Date disputed — see DATE CHECK below.",
       font=F(SANS_I, 7), fill=GREY)

# --- DATE CHECK (red frame) -------------------------------------------------
dc_y0, dc_y1 = 930, 976
d.rectangle([MX, dc_y0, RX, dc_y1], outline=RED, width=2, fill=(255, 246, 240))
dc_title = "DATE CHECK — WHAT WE LEFT OUT"
d.text((MX + 8, dc_y0 + 4), dc_title, font=F(SANS_B, 10), fill=RED_DK)
dc_text = (
    "NOT Friday's news (first reported Thu 19 Nov): Shenzhen Trump–Xi–Putin "
    "summit • ICJ Myanmar/Rohingya verdict • Anthropic $83 IPO pricing & "
    "Nasdaq debut • 3rd Kerch Bridge strike • Houthi strike on Riyadh PIF "
    "tower • US–Venezuela military deal • $190.4m Van Gogh sale (18 Nov). "
    "UNCONFIRMED: Dorogobuzh drone claim; COP31 outcome still unknown at "
    "press time; Voyager 1 light-day date disputed.")
text_block(d, MX + 8, dc_y0 + 19, dc_text, F(SANS, 8.5), INK, RX - MX - 16,
           11, max_lines=3)

# --- footer ------------------------------------------------------------------
rule(d, MX, 986, RX, 1)
foot = ("ORIGINAL DRAWINGS  •  SOURCES: REUTERS • AP • AFP • BBC • AL JAZEERA "
        "• IMD • UN NEWS • KYIV POST")
ff = F(SANS_B, 8)
d.text(((W - d.textlength(foot, font=ff)) / 2, 991), foot, font=ff, fill=INK)
foot2 = ("Every story here happened, or was first reported, on Friday "
         "20 November 2026. Claims are attributed, not stated as fact.")
ff2 = F(SANS_I, 8)
d.text(((W - d.textlength(foot2, font=ff2)) / 2, 1003), foot2, font=ff2,
       fill=INK_SOFT)

# --- save ----------------------------------------------------------------------
img.save(OUT, format="PNG", optimize=True)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
