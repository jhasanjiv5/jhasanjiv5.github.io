#!/usr/bin/env python3
"""Draws the career map (assets/image/career-map.svg and -dark.svg). Standard library only.

    python3 build_map.py

A calm, Apple Maps-like map of Europe to India: a plane for the Mumbai → Zurich
leg, and a zoomed panel where a train runs Zurich → Baden → St.Gallen → Konstanz.
Each callout lists the jobs and degrees at that place with their own dates (from
the CV), never how long I lived there. Coastlines are hand-traced and coarse on
purpose. Colours follow the site header: Apple greys, Apple blue, soft tints.
"""
from __future__ import annotations

import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "assets" / "image"

# ---------------------------------------------------------------------------
# Content: each entry is (title, organisation · dates), exactly as on the CV
# ---------------------------------------------------------------------------
MUMBAI = dict(lon=72.83, lat=19.08, city="Mumbai, India", entries=[
    ("B.E. Computer Engineering", "University of Mumbai · Jul 2007 – Jun 2012"),
    ("Co-founder & technical lead", "HelloWelt Technologies · Jan 2013 – Aug 2015"),
    ("Software trainer", "Aptech · Jul 2014 – Aug 2015"),
])
# Stops in the zoomed panel, in the order the train visits them. card = top-left of the callout.
STOPS = [
    dict(lon=8.54, lat=47.38, city="Zurich", card=(458, 258), entries=[
        ("M.Sc. Computer Science", "Univ. of Zurich · Sep 2015 – Apr 2018"),
        ("SAP UI5 developer", "Accenture · Aug – Sep 2016")]),
    dict(lon=8.31, lat=47.47, city="Baden", card=(462, 112), entries=[
        ("Software developer", "Equidato · Apr 2018 – Mar 2019")]),
    dict(lon=9.37, lat=47.42, city="St.Gallen", card=(742, 240), entries=[
        ("Applied AI research assistant", "Univ. St.Gallen · Sep 2019 – May 2025"),
        ("PhD, Computer Science", "Univ. St.Gallen · Feb 2020 – Sep 2025")]),
    dict(lon=9.17, lat=47.66, city="Konstanz", card=(548, 34), entries=[
        ("Freelance AI engineer", "Self-employed · Oct 2025 – present")]),
]
# Rail line the train follows (lon, lat), via Winterthur and Weinfelden/Kreuzlingen.
RAIL = [(8.54, 47.38), (8.31, 47.47), (8.43, 47.42), (8.54, 47.38), (8.73, 47.50), (9.03, 47.48),
        (9.37, 47.42), (9.18, 47.50), (9.10, 47.56), (9.17, 47.66)]

THEMES = {
    "light": dict(card="#ffffff", border="#e5e5ea", text="#1d1d1f", muted="#6e6e73",
                  land="#fbfbfd", coast="#d2d7df", water="#e9f1fa", lake="#d6e6f7",
                  accent="#0071e3", rail="#aeaeb2", shadow=".07", tint=".16"),
    "dark": dict(card="#1c1c1e", border="#38383a", text="#f5f5f7", muted="#a1a1a6",
                 land="#2c2c2e", coast="#3a3a3c", water="#121821", lake="#1b2a3c",
                 accent="#2997ff", rail="#636366", shadow=".5", tint=".12"),
}
FONT = ("-apple-system,BlinkMacSystemFont,'SF Pro Display','SF Pro Text','Helvetica Neue',"
        "Helvetica,Arial,sans-serif")

# ---------------------------------------------------------------------------
# Hand-traced coastlines (lon, lat), coarse on purpose
# ---------------------------------------------------------------------------
AFRICA = [(-17, 14.7), (-16, 19), (-17, 21), (-13, 27.5), (-9.8, 29.5), (-9.5, 32), (-6, 35.8), (-2, 35.1),
          (3, 36.8), (10, 37.3), (11, 33.5), (15, 32.3), (20, 30.8), (20, 32.5), (25, 32), (29, 30.9),
          (32.3, 31.3), (34.2, 31.2), (34.9, 29.5), (32.5, 29.9), (33.5, 27.5), (35.5, 24), (37.2, 21),
          (38.5, 18), (39.7, 15.3), (42.5, 13), (43.3, 11.8), (44.5, 10.4), (51.2, 11.8), (51, 10.5),
          (49, 6), (48, 3), (8, 3), (8, 4.5), (5, 5.8), (1, 6), (-3, 5), (-7.5, 4.4), (-11, 6.8),
          (-13.3, 9.5), (-15, 11)]
EURASIA = [(-5.6, 36), (-6.3, 36.8), (-7.4, 37.2), (-8.9, 37), (-8.8, 38.7), (-9.5, 39), (-8.7, 42),
           (-9.3, 43), (-7.7, 43.8), (-4, 43.4), (-1.8, 43.4), (-1.2, 46), (-2.5, 47.3), (-4.6, 48),
           (-1.6, 48.7), (0.2, 49.7), (1.6, 50.9), (3.2, 51.3), (4.5, 52.5), (5, 53.3), (7, 53.6),
           (8.6, 54), (8.6, 55.5), (8.1, 56.8), (10.5, 57.6), (10.6, 56.4), (9.9, 54.6), (11, 54),
           (13.5, 54.3), (15, 54.1), (18.5, 54.7), (21, 55.3), (21.1, 56.9), (23.7, 57.3), (24.4, 58.4),
           (23.5, 59.2), (28, 59.5), (30, 60), (29, 60.7), (25, 60.3), (22.5, 60), (21.5, 61.7),
           (21.3, 63), (95, 63), (95, 22), (90, 22), (88, 21.6), (86.9, 20.9), (85, 19.5), (82.3, 17),
           (80.3, 15.5), (80.2, 13), (79.8, 10.3), (77.5, 8.1), (76.5, 9.5), (75, 12.8), (74, 15.6),
           (73, 19), (72.8, 21), (72.6, 22.2), (70.3, 21), (69, 22.4), (68.4, 23.6), (67, 24.8),
           (64, 25.3), (61.5, 25.2), (57.3, 25.8), (56.4, 27.1), (54.7, 26.5), (51.6, 27.9), (50.1, 30.1),
           (48.9, 30.4), (47.9, 30), (48.4, 28.5), (49.6, 27), (50.8, 25.5), (51.6, 25.8), (51.6, 24.2),
           (54, 24.1), (55.9, 25.6), (56.4, 26.4), (56.3, 24.9), (58.7, 23.6), (59.8, 22.4), (58.5, 20.4),
           (57.7, 19), (55.3, 17.6), (52.2, 15.6), (48.7, 14), (45, 12.8), (43.5, 12.7), (42.7, 15.7),
           (42.6, 16.8), (40.9, 19.5), (39.1, 21.7), (38.4, 24.3), (36.9, 26), (35.1, 28.1), (34.9, 29.5),
           (34.2, 31.2), (34.9, 32.8), (35.5, 33.9), (35.9, 35.4), (36.2, 36.6), (34.7, 36.8), (32.5, 36.1),
           (30.6, 36.7), (28.7, 36.7), (27.4, 37.4), (26.3, 38.2), (26.2, 39.4), (26.6, 40.2), (28.9, 40.4),
           (29.2, 41.2), (31.2, 41.1), (33.5, 42), (35.2, 42), (38.3, 40.9), (40.5, 41), (41.6, 41.5),
           (41.5, 42.6), (40, 43.4), (38.2, 44.4), (37.4, 44.8), (38.3, 46.2), (36.6, 45.4), (35, 45),
           (33.5, 44.5), (32.7, 45.4), (33.6, 46), (31.7, 46.4), (30.7, 46.6), (29.6, 45.3), (28.7, 44.3),
           (28, 43.1), (27.9, 42), (28.1, 41.6), (28, 41), (26, 40.6), (24, 40.8), (22.6, 40.3),
           (23.3, 39.2), (22.9, 37.5), (21.7, 36.8), (21.1, 38.3), (20.2, 39.6), (19.4, 40.3), (19.5, 41.8),
           (18.5, 42.5), (17, 43.2), (15.2, 44.3), (14, 44.9), (13.6, 45.7), (12.3, 45.3), (12.4, 44.2),
           (13.6, 43.6), (14, 42.6), (15.9, 41.9), (16.9, 41.2), (18.5, 40.1), (17, 39.5), (16.6, 38.4),
           (15.7, 38), (16, 39.4), (15.4, 40), (14.3, 40.8), (12.9, 41.4), (11.2, 42.4), (10.5, 43),
           (10.2, 43.9), (8.8, 44.4), (7.5, 43.8), (6, 43.1), (4.3, 43.5), (3.1, 43.1), (3.2, 41.9),
           (2, 41.2), (0.9, 41), (-0.3, 39.4), (0.2, 38.7), (-0.7, 37.6), (-2.1, 36.7), (-4.4, 36.7)]
SCANDINAVIA = [(5, 63), (5, 62), (5.5, 59), (7, 58), (8.5, 58.1), (10.5, 59.3), (11.2, 58.5), (12, 57.5),
               (12.8, 56), (14.2, 55.4), (16, 56.2), (16.6, 57.8), (18.5, 59.4), (17.3, 60.6), (17.5, 63)]
ISLANDS = [
    [(-5.7, 50), (-3, 50.6), (1.4, 51.1), (1.7, 52.7), (0, 53.5), (-0.4, 54.5), (-1.6, 55.6), (-2.1, 57.7),
     (-3.4, 58.6), (-5, 58.6), (-6.2, 56.6), (-5.6, 55.3), (-4.8, 54.8), (-3.2, 54.1), (-3, 53.3),
     (-4.5, 52.8), (-4.2, 51.6), (-5.3, 51.7), (-3.3, 51.4)],                       # Great Britain
    [(-6, 52.2), (-6, 53.9), (-7.3, 55.3), (-8.5, 54.5), (-10, 54.2), (-9.9, 52), (-8, 51.6)],  # Ireland
    [(79.8, 9.8), (81.9, 7.4), (81.2, 6.1), (80, 6.1)],                             # Sri Lanka
    [(12.4, 38), (15.6, 38.3), (15.1, 36.7)],                                       # Sicily
    [(8.4, 41), (9.8, 41), (9.6, 39.1), (8.4, 39)],                                 # Sardinia
    [(8.6, 42.9), (9.4, 42.9), (9.4, 41.4), (8.7, 41.6)],                           # Corsica
    [(23.5, 35.6), (26.3, 35.3), (24.5, 34.9)],                                     # Crete
    [(32.3, 35), (34.6, 35.6), (33.9, 34.9), (32.4, 34.7)],                         # Cyprus
]
WATER = [  # inland seas drawn over the land
    [(49, 46.5), (47.5, 45.6), (47.3, 43.5), (49.5, 40.5), (49.2, 37.6), (51, 36.7), (54, 36.9),
     (53.9, 40.6), (52.8, 41.5), (53, 42.5), (51.3, 43.2), (51.5, 45.1), (53.2, 46.7), (51, 47)],  # Caspian
]

# Detail-panel geography: lakes and the Swiss border along the Rhine
LAKE_CONSTANCE = [(8.98, 47.70), (9.05, 47.68), (9.17, 47.66), (9.20, 47.65), (9.38, 47.60), (9.53, 47.54),
                  (9.70, 47.53), (9.74, 47.55), (9.62, 47.62), (9.42, 47.68), (9.25, 47.76), (9.10, 47.82),
                  (9.03, 47.80), (9.10, 47.72), (9.00, 47.73)]
LAKE_ZURICH = [(8.54, 47.365), (8.60, 47.31), (8.70, 47.24), (8.84, 47.21), (8.95, 47.20), (8.94, 47.22),
               (8.80, 47.245), (8.68, 47.28), (8.58, 47.34)]
BORDER = [(7.95, 47.56), (8.22, 47.61), (8.45, 47.58), (8.60, 47.65), (8.68, 47.71), (8.88, 47.66),
          (9.00, 47.69), (9.17, 47.66)]
BORDER_AT = [(9.56, 47.53), (9.62, 47.38), (9.53, 47.25), (9.60, 47.12)]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_width(s: str, size: float) -> float:
    return sum(0.33 if c in "il.,:;|' " else 0.62 if c.isupper() else 0.53 for c in s) * size * 1.1


# World projection (equirectangular, squeezed to roughly true shape at 35°N)
W, H = 1000, 660
LON0, LAT0, LAT1 = -12.0, 62.0, 6.0
K = H / (LAT0 - LAT1)
C = math.cos(math.radians(35))


def wxy(lon, lat):
    return (lon - LON0) * K * C, (LAT0 - lat) * K


# Detail panel
PX, PY, PW, PH = 450, 20, 530, 380
D_LON0, D_LON1, D_LAT0, D_LAT1 = 8.10, 9.80, 47.86, 47.04
DK = PW / ((D_LON1 - D_LON0) * math.cos(math.radians(47.5)))


def dxy(lon, lat):
    return (PX + (lon - D_LON0) * DK * math.cos(math.radians(47.5)), PY + (D_LAT0 - lat) * DK)


def pts(seq, f) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in (f(*p) for p in seq))


PLANE = "M0,-9 C1.6,-9 1.6,-6 1.6,-4 L1.6,-1.5 L9,2.5 L9,4.5 L1.6,2.5 L1.2,7 L3.6,8.8 L3.6,10 L0,9 L-3.6,10 L-3.6,8.8 L-1.2,7 L-1.6,2.5 L-9,4.5 L-9,2.5 L-1.6,-1.5 L-1.6,-4 C-1.6,-6 -1.6,-9 0,-9 Z"


def train(t) -> str:
    """A small train pointing along +x, centred on the origin."""
    a, c = t["accent"], t["card"]
    return (f'<g><rect x="-14" y="-5.5" width="28" height="11" rx="5" fill="{a}"/>'
            + "".join(f'<rect x="{x}" y="-3" width="4.5" height="3.5" rx="1" fill="{c}"/>' for x in (-10, -3.5, 3))
            + f'<path d="M14,-5.5 Q18,-5.5 18,0 Q18,5.5 14,5.5 Z" fill="{a}"/></g>')


def marker(x, y, t, r=6) -> str:
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{t["card"]}" stroke="{t["accent"]}" stroke-width="3"/>'


def callout(x, y, city, entries, t, title_size=12) -> tuple[str, float, float]:
    """A white card: city, then each entry as a title line and a muted org · dates line."""
    w = max(max(text_width(a, title_size), text_width(b, 11)) for a, b in entries) + 28
    w = max(w, text_width(city.upper(), 10.5) * 1.15 + 28)
    h = 34 + 36 * len(entries)
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="14" fill="{t["card"]}" stroke="{t["border"]}" filter="url(#sh)"/>',
           f'<text x="{x + 14:.1f}" y="{y + 22:.1f}" font-size="10.5" font-weight="700" letter-spacing="1.1" class="muted">{esc(city.upper())}</text>']
    for i, (a, b) in enumerate(entries):
        ty = y + 42 + i * 36
        out.append(f'<text x="{x + 14:.1f}" y="{ty:.1f}" font-size="{title_size}" font-weight="600">{esc(a)}</text>')
        out.append(f'<text x="{x + 14:.1f}" y="{ty + 15:.1f}" font-size="11" class="muted">{esc(b)}</text>')
    return "\n".join(out), w, h


def build(theme: str) -> str:
    t = THEMES[theme]
    s = [f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Career map">
<title>Career map: Mumbai (B.E. 2007–2012, HelloWelt 2013–2015, Aptech 2014–2015) → Zurich (M.Sc. UZH 2015–2018, Accenture 2016) → Baden (Equidato 2018–2019) → St.Gallen (research assistant 2019–2025, PhD 2020–2025) → Konstanz (freelance AI engineer since Oct 2025)</title>
<defs>
  <filter id="sh" x="-10%" y="-10%" width="120%" height="140%"><feDropShadow dx="0" dy="3" stdDeviation="7" flood-color="#000" flood-opacity="{t['shadow']}"/></filter>
  <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="18"/></clipPath>
  <clipPath id="panel"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="18"/></clipPath>
  <radialGradient id="g1" cx=".12" cy="0" r=".6"><stop offset="0" stop-color="#0071e3" stop-opacity="{t['tint']}"/><stop offset="1" stop-color="#0071e3" stop-opacity="0"/></radialGradient>
  <radialGradient id="g2" cx=".55" cy=".05" r=".5"><stop offset="0" stop-color="#af52de" stop-opacity="{t['tint']}"/><stop offset="1" stop-color="#af52de" stop-opacity="0"/></radialGradient>
  <radialGradient id="g3" cx=".95" cy="1" r=".55"><stop offset="0" stop-color="#ff9f0a" stop-opacity="{t['tint']}"/><stop offset="1" stop-color="#ff9f0a" stop-opacity="0"/></radialGradient>
</defs>
<style>
  text {{ font-family: {FONT}; fill: {t['text']}; }}
  .muted {{ fill: {t['muted']}; }}
  .dash {{ animation: dash 1.6s linear infinite; }}
  @keyframes dash {{ to {{ stroke-dashoffset: -20; }} }}
  @media (prefers-reduced-motion: reduce) {{ .dash {{ animation: none; }} .move {{ display: none; }} }}
</style>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="{t['water']}"/>"""]

    # solid land with a hairline coast
    for poly in [AFRICA, EURASIA, SCANDINAVIA] + ISLANDS:
        s.append(f'<polygon points="{pts(poly, wxy)}" fill="{t["land"]}" stroke="{t["coast"]}" stroke-width="1" stroke-linejoin="round"/>')
    for poly in WATER:
        s.append(f'<polygon points="{pts(poly, wxy)}" fill="{t["water"]}" stroke="{t["coast"]}" stroke-width="1" stroke-linejoin="round"/>')
    # the header's soft colour wash
    for g in ("g1", "g2", "g3"):
        s.append(f'<rect width="{W}" height="{H}" fill="url(#{g})"/>')
    for name, lon, lat in [("INDIA", 78.5, 23.5), ("EUROPE", 14, 50.5), ("ARABIAN SEA", 63.5, 15)]:
        x, y = wxy(lon, lat)
        s.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="10.5" font-weight="600" letter-spacing="1.6" text-anchor="middle" class="muted" opacity=".7">{name}</text>')

    # flight: Mumbai → Zurich
    mx, my = wxy(MUMBAI["lon"], MUMBAI["lat"])
    zx, zy = wxy(8.54, 47.38)
    cx, cy = 430, 520
    arc = f"M {mx:.1f} {my:.1f} Q {cx} {cy} {zx:.1f} {zy:.1f}"
    s.append(f'<path id="flight-{theme}" d="{arc}" fill="none" stroke="{t["accent"]}" stroke-width="2" stroke-dasharray="2 8" stroke-linecap="round" stroke-opacity=".8" class="dash"/>')
    s.append(f'<g class="move"><path d="{PLANE}" fill="{t["accent"]}" stroke="{t["card"]}" stroke-width="1" transform="rotate(90) scale(1.2)"/>'
             f'<animateMotion dur="10s" repeatCount="indefinite" rotate="auto" keyPoints="0;1;1" keyTimes="0;.8;1" calcMode="linear">'
             f'<mpath href="#flight-{theme}"/></animateMotion></g>')
    fx, fy = 0.25 * mx + 0.5 * cx + 0.25 * zx, 0.25 * my + 0.5 * cy + 0.25 * zy
    label = "2015 · Mumbai → Zurich"
    lw = text_width(label, 12) + 26
    s.append(f'<g transform="translate({fx - lw / 2:.0f},{fy + 8:.0f})"><rect width="{lw:.0f}" height="24" rx="12" fill="{t["card"]}" stroke="{t["border"]}"/>'
             f'<text x="{lw / 2:.0f}" y="16.5" font-size="12" font-weight="600" text-anchor="middle" style="fill:{t["accent"]}">{label}</text></g>')

    # Mumbai marker + callout
    s.append(marker(mx, my, t, 7))
    c, cw, ch = callout(0, 0, MUMBAI["city"], MUMBAI["entries"], t)
    bx, by = mx - cw - 24, my + 6
    s.append(f'<line x1="{mx - 8:.1f}" y1="{my + 3:.1f}" x2="{bx + cw:.1f}" y2="{by + 22:.1f}" stroke="{t["accent"]}" stroke-width="1.2" stroke-opacity=".5"/>')
    s.append(f'<g transform="translate({bx:.1f},{by:.1f})">{c}</g>')

    # Switzerland box on the world map + leaders to the panel
    s.append(f'<rect x="{zx - 10:.1f}" y="{zy - 10:.1f}" width="20" height="20" rx="5" fill="none" stroke="{t["accent"]}" stroke-width="1.6"/>')
    for ex, ey, py in ((zx + 10, zy - 10, PY + 10), (zx + 10, zy + 10, PY + PH - 10)):
        s.append(f'<path d="M {ex:.1f} {ey:.1f} L {PX} {py}" stroke="{t["accent"]}" stroke-width="1" stroke-opacity=".3" fill="none"/>')

    # ---- detail panel ----
    s.append(f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="18" fill="{t["land"]}" stroke="{t["border"]}" filter="url(#sh)"/>')
    s.append('<g clip-path="url(#panel)">')
    s.append(f'<polygon points="{pts(LAKE_CONSTANCE, dxy)}" fill="{t["lake"]}"/>')
    s.append(f'<polygon points="{pts(LAKE_ZURICH, dxy)}" fill="{t["lake"]}"/>')
    for b in (BORDER, BORDER_AT):
        s.append(f'<polyline points="{pts(b, dxy)}" fill="none" stroke="{t["muted"]}" stroke-width="1" stroke-dasharray="1 4" stroke-linecap="round" opacity=".6"/>')
    for name, lon, lat in [("GERMANY", 8.25, 47.75), ("SWITZERLAND", 8.95, 47.09), ("AUSTRIA", 9.68, 47.09)]:
        x, y = dxy(lon, lat)
        s.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="10" font-weight="600" letter-spacing="1.4" text-anchor="middle" class="muted" opacity=".75">{name}</text>')
    x, y = dxy(9.47, 47.645)
    s.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="10" font-style="italic" text-anchor="middle" class="muted" transform="rotate(-22 {x:.0f} {y:.0f})">Lake Constance</text>')
    rail = "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in (dxy(*p) for p in RAIL))
    s.append(f'<path id="rail-{theme}" d="{rail}" fill="none" stroke="{t["rail"]}" stroke-width="2" stroke-dasharray="6 4" stroke-linejoin="round"/>')
    s.append(f'<g class="move">{train(t)}<animateMotion dur="16s" repeatCount="indefinite" rotate="auto"><mpath href="#rail-{theme}"/></animateMotion></g>')
    s.append("</g>")
    for st in STOPS:
        x, y = dxy(st["lon"], st["lat"])
        s.append(marker(x, y, t))
        c, w, _ = callout(0, 0, st["city"], st["entries"], t)
        cx_ = min(st["card"][0], PX + PW - w - 10)  # keep the card inside the panel
        s.append(f'<g transform="translate({cx_:.1f},{st["card"][1]})">{c}</g>')

    # legend
    lx, ly = 22, H - 20
    for label, kind in [("Flight", "plane"), ("Train", "train"), ("Work & study", "dot")]:
        if kind == "plane":
            s.append(f'<path d="{PLANE}" fill="{t["accent"]}" transform="translate({lx + 8},{ly - 4}) rotate(90) scale(.75)"/>')
        elif kind == "train":
            s.append(f'<g transform="translate({lx + 10},{ly - 4}) scale(.6)">{train(t)}</g>')
        else:
            s.append(f'<circle cx="{lx + 8}" cy="{ly - 4}" r="4.5" fill="{t["card"]}" stroke="{t["accent"]}" stroke-width="2.5"/>')
        s.append(f'<text x="{lx + 24}" y="{ly}" font-size="12" class="muted">{esc(label)}</text>')
        lx += text_width(label, 12) + 52
    s.append("</g></svg>\n")
    return "\n".join(s)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        suffix = "" if theme == "light" else "-dark"
        (OUT / f"career-map{suffix}.svg").write_text(build(theme), encoding="utf-8")
    print("wrote assets/image/career-map.svg and career-map-dark.svg")


if __name__ == "__main__":
    main()
