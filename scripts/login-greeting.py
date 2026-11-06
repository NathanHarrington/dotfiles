#!/usr/bin/env python3
"""One-file login greetings. Python 3.9+, standard library only.

Call this file from .bashrc with a design name, random, or random:GROUP.
The command line is the only configuration; no settings files are read or written.
All renderers, letterforms, research links and 24 CORDINCE logo frames
are embedded below. No sibling files, fonts, converters or network needed.
"""
from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
import ipaddress
import json
import math
import os
from pathlib import Path
import platform
import random
import shutil
import socket
import sys
import textwrap
import time
import zlib


# ========================================================================
# Drawing geometry
# ========================================================================

geo_TAU = math.tau
geo_WHITE = (222, 234, 235)

def geo_clamp(value):
    return max(0.0, min(1.0, value))

def geo_tint(color, strength):
    return tuple((round(channel * geo_clamp(strength)) for channel in color))

def geo_ease(t):
    t = geo_clamp(t)
    return t * t * (3 - 2 * t)

def geo_point(c, x, y):
    return (x * (c.w - 1), y * (c.h - 1))

def geo_path(c, points, color, t=1.0, glow=False):
    c.path([geo_point(c, x, y) for x, y in points], color, geo_clamp(t), glow)

def geo_line(c, x0, y0, x1, y1, color, t=1.0, glow=False):
    geo_path(c, [(x0, y0), (x1, y1)], color, t, glow)

def geo_rect(c, x0, y0, x1, y1, color, t=1.0):
    geo_path(c, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], color, t)

def geo_polygon(c, points, color, density=0, seed=0, t=1.0):
    vertices = [geo_point(c, x, y) for x, y in points]
    if density:
        top = max(0, math.floor(min((y for _, y in vertices))))
        bottom = min(c.h - 1, math.ceil(max((y for _, y in vertices))))
        for y in range(top, bottom + 1):
            crossings = []
            for (x0, y0), (x1, y1) in zip(vertices, vertices[1:] + vertices[:1]):
                if y0 <= y < y1 or y1 <= y < y0:
                    crossings.append(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
            crossings.sort()
            for left, right in zip(crossings[::2], crossings[1::2]):
                for x in range(max(0, math.ceil(left)), min(c.w - 1, math.floor(right)) + 1):
                    if (x * 11 + y * 7 + seed * 3) % 16 < density:
                        c.dot(x, y, geo_tint(color, t))
    c.path(vertices + vertices[:1], color, t)

def geo_ellipse(c, x, y, rx, ry, color, t=1.0, phase=0.0, start=0.0, span=geo_TAU, glow=False):
    points = [geo_point(c, x + rx * math.cos(start + span * step / 160 + phase), y + ry * math.sin(start + span * step / 160 + phase)) for step in range(161)]
    c.path(points, color, geo_clamp(t), glow)

def geo_curve(c, points, color, t=1.0):
    a, b, d, e = points
    geo_path(c, [((1 - p) ** 3 * a[0] + 3 * (1 - p) ** 2 * p * b[0] + 3 * (1 - p) * p ** 2 * d[0] + p ** 3 * e[0], (1 - p) ** 3 * a[1] + 3 * (1 - p) ** 2 * p * b[1] + 3 * (1 - p) * p ** 2 * d[1] + p ** 3 * e[1]) for p in (step / 100 for step in range(101))], color, t)

def geo_grid(c, x0, y0, x1, y1, columns, rows, color):
    for index in range(columns + 1):
        x = x0 + (x1 - x0) * index / columns
        geo_line(c, x, y0, x, y1, color)
    for index in range(rows + 1):
        y = y0 + (y1 - y0) * index / rows
        geo_line(c, x0, y, x1, y, color)

def geo_particles(c, color, count=90, seed=1, bounds=(0, 0, 1, 1), drift=0.0):
    x0, y0, x1, y1 = bounds
    for index in range(count):
        px = (index * 137 + seed * 41) % 997 / 997
        py = ((index * 313 + seed * 73) % 991 / 991 + drift * (index % 3 + 1)) % 1
        c.dot(*geo_point(c, x0 + px * (x1 - x0), y0 + py * (y1 - y0)), geo_tint(color, 0.25 + index % 7 / 10))

def geo_landscape(c, color, y=0.8, amplitude=0.1, seed=1, t=1.0, frequency=8):
    geo_path(c, [(p, y + amplitude * (0.6 * math.sin(p * frequency + seed) + 0.3 * math.sin(p * frequency * 2.7 + seed * 2))) for p in (index / 180 for index in range(181))], color, t)

def geo_greeting(c, t, accent, main=geo_WHITE, x=0.68, y=0.29, tracking=True):
    c.greeting(c.width * x, round(c.height * y), t, accent, main, tracking)

def geo_brackets(c, x0, y0, x1, y1, color, t=1.0, length=0.04):
    for x, sx in ((x0, 1), (x1, -1)):
        for y, sy in ((y0, 1), (y1, -1)):
            geo_path(c, [(x, y + sy * length * 2), (x, y), (x + sx * length, y)], color, t)


# ========================================================================
# Interface designs
# ========================================================================

ui_ARES_SOURCE = 'https://www.darbyfui.com/tronares'
ui_LEGACY_SOURCE = 'https://gmunk.com/TRON-Board-Room'
ui_HUDS = 'https://www.hudsandguis.com/home/'

def ui_ares(c, t):
    red, pale = ((255, 64, 39), (247, 185, 151))
    jump = round(geo_clamp(t * 1.7) * 6) / 6
    offset = (1 - jump) * 0.08
    geo_grid(c, 0.03, 0.08, 0.97, 0.91, 20, 7, geo_tint(red, 0.09))
    geo_brackets(c, 0.08 + offset, 0.22, 0.42 - offset, 0.76, red, jump)
    geo_brackets(c, 0.49, 0.27, 0.93, 0.7, geo_tint(red, 0.6), geo_clamp(t * 2 - 0.2))
    for index in range(24):
        x = 0.07 + index * 0.036
        y = 0.12 if index % 2 else 0.86
        geo_line(c, x, y, x + 0.013, y, geo_tint(red, 0.3 + index % 4 * 0.15))
    geo_path(c, [(0.1, 0.63), (0.27, 0.63), (0.35, 0.43), (0.4, 0.43)], pale, jump)
    geo_polygon(c, [(0.19, 0.38), (0.29, 0.38), (0.24, 0.57)], geo_tint(red, 0.65), 3, t=jump)
    geo_particles(c, red, 55, 17, (0.04, 0.13, 0.45, 0.82), (1 - t) * 0.1)
    geo_greeting(c, t, red, pale, x=0.71)

def ui_identity_disc(c, t):
    ice, amber = ((167, 234, 255), (255, 174, 74))
    cx, cy, radius = (c.w * 0.25, c.h * 0.51, c.h * 0.35)
    for factor in (1, 0.87, 0.43):
        phase = (1 - t) * geo_TAU * (1 if factor == 0.87 else -1)
        for start in (0, math.pi):
            c.arc(cx, cy, radius * factor, start + phase, start + phase + math.pi * 0.77, ice, glow=factor == 1)
    for index in range(4):
        a = index * math.pi / 2 + 0.35
        c.line(cx + radius * 0.88 * math.cos(a), cy + radius * 0.88 * math.sin(a), cx + radius * 1.06 * math.cos(a), cy + radius * 1.06 * math.sin(a), amber)
    geo_path(c, [(0.44, 0.75), (0.52, 0.84), (0.96, 0.84)], geo_tint(ice, 0.4), geo_ease(t))
    geo_greeting(c, t, ice, x=0.72)

def ui_light_table(c, t):
    cyan, yellow = ((109, 213, 207), (235, 220, 132))
    for layer in range(8):
        points = []
        for step in range(90):
            angle = step * geo_TAU / 89
            radius = 0.03 + layer * 0.013 + math.sin(angle * 4 + layer * 0.3 + (1 - t)) * 0.014
            points.append((0.25 + radius * math.cos(angle), 0.48 + radius * 2.6 * math.sin(angle)))
        geo_path(c, points, geo_tint(cyan, 0.2 + layer * 0.07), geo_clamp(t * 2 - layer * 0.04))
    geo_grid(c, 0.05, 0.1, 0.46, 0.89, 8, 6, geo_tint(cyan, 0.12))
    geo_line(c, 0.5, 0.13, 0.94, 0.13, yellow, geo_ease(t))
    for index in range(18):
        x = 0.52 + index * 0.022
        geo_line(c, x, 0.8, x, 0.8 + 0.04 * math.sin(index), geo_tint(cyan, 0.5))
    geo_greeting(c, t, yellow, x=0.72, tracking=False)

def ui_silent_sea(c, t):
    ice, gold = ((186, 223, 239), (201, 176, 111))
    cx, cy, radius = (c.w * 0.26, c.h * 0.47, c.h * 0.31)
    c.arc(cx, cy, radius, 0, geo_TAU * geo_ease(t), ice)
    c.ticks(cx, cy, radius + 2, 32, geo_tint(ice, 0.4))
    c.arc(cx, cy, radius * 0.68, -0.5 + (1 - t) * 2, 3.5 + (1 - t) * 2, geo_tint(gold, 0.8))
    geo_path(c, [(0.08, 0.77), (0.39, 0.77), (0.47, 0.85), (0.94, 0.85)], geo_tint(ice, 0.4), geo_ease(t))
    for index in range(7):
        geo_line(c, 0.51, 0.15 + index * 0.035, 0.63 + index % 3 * 0.1, 0.15 + index * 0.035, geo_tint(ice, 0.17))
    geo_greeting(c, t, gold, ice, x=0.72)
ui_STUDIES = {'ares': ('TRON: ARES / directive HUD', 'Abrupt red brackets and a sparse acquisition field', ui_ares, [ui_ARES_SOURCE]), 'identity-disc': ('TRON: LEGACY / identity disc', 'White-blue circular light with amber key marks', ui_identity_disc, [ui_LEGACY_SOURCE]), 'light-table': ('TRON: LEGACY / light table', 'Topographic contour loops on a planar grid', ui_light_table, [ui_LEGACY_SOURCE]), 'silent-sea': ('SILENT SEA / lunar instrument', 'Cold circular calibration and an asymmetrical frame', ui_silent_sea, [ui_HUDS + '2025/the-silent-sea'])}
ui_COMPACT_STUDIES = {f'{key}-compact': (f'{title} / half height', f'Half-height: {description}', painter, references) for key, (title, description, painter, references) in ui_STUDIES.items()}


# ========================================================================
# Arrival designs
# ========================================================================

arr_FOG = (193, 207, 204)
arr_INK = (125, 148, 147)
arr_LANGUAGE_SOURCE = 'https://www.motionpictures.org/2016/11/how-arrivals-production-designer-created-alien-language/'
arr_SHELL_SOURCE = 'https://meinerthansen.com/2016/11/13/arrival-concept-art-part-1-the-shell/'
arr_CREATURE_SOURCE = 'https://vfxblog.com/2016/11/15/arrival-vfx-supe-louis-morin-breaks-down-the-films-key-shots/'

def arr_ink_ring(c, cx, cy, rx, ry, t, seed=1, color=arr_FOG):
    """A broken brush circumference with irregular branches; no claimed translation."""
    reveal = geo_ease(geo_clamp(t * 1.3))
    for index in range(420):
        p = index / 419
        if p > reveal:
            break
        angle = p * geo_TAU - math.pi / 2
        if math.sin(angle * 5 + seed * 1.3) > 0.94:
            continue
        wobble = 0.028 * math.sin(angle * 17 + seed) + 0.018 * math.sin(angle * 37 - seed)
        thickness = 1 + round(2 * (1 + math.sin(angle * 3 + seed)))
        for layer in range(thickness):
            radius = 1 + wobble + (layer - thickness / 2) * 0.018
            c.dot(*geo_point(c, cx + rx * radius * math.cos(angle), cy + ry * radius * math.sin(angle)), geo_tint(color, 0.45 + layer * 0.12))
    for index in range(17):
        a = (index * 0.618 + seed * 0.13) % 1 * geo_TAU - math.pi / 2
        if (a + math.pi / 2) % geo_TAU / geo_TAU > reveal:
            continue
        length = 0.14 + index * 7 % 9 * 0.025
        sign = 1 if index % 3 else -1
        points = []
        for step in range(21):
            p = step / 20
            bend = a + sign * p * 0.19
            r = 1 + length * p
            points.append((cx + rx * r * math.cos(bend), cy + ry * r * math.sin(bend)))
        geo_path(c, points, geo_tint(color, 0.42 + index % 4 * 0.1))

def arr_heptapod(c, cx, top, width, height, t, strength=1.0):
    body = [(cx - width * 0.16, top), (cx + width * 0.08, top - height * 0.02), (cx + width * 0.21, top + height * 0.16), (cx + width * 0.43, top + height * 0.27), (cx + width * 0.48, top + height * 0.43), (cx + width * 0.3, top + height * 0.59), (cx + width * 0.12, top + height * 0.66), (cx - width * 0.15, top + height * 0.66), (cx - width * 0.3, top + height * 0.54), (cx - width * 0.44, top + height * 0.36), (cx - width * 0.32, top + height * 0.21), (cx - width * 0.2, top + height * 0.16)]
    geo_polygon(c, body, geo_tint(arr_INK, 0.65 * strength), 4, t=geo_ease(t))
    for side in (-1, 1):
        geo_curve(c, [(cx + side * width * 0.04, top + height * 0.15), (cx + side * width * 0.32, top + height * 0.35), (cx + side * width * 0.15, top + height * 0.5), (cx, top + height * 0.65)], geo_tint(arr_FOG, 0.25 * strength), geo_ease(t))
    for index in range(7):
        spread = (index - 3) / 3
        root = cx + width * spread * 0.15
        end = cx + width * spread * 0.78
        wave = math.sin(index * 1.7 + (1 - t) * 3) * width * 0.09
        geo_curve(c, [(root, top + height * 0.6), (root + width * spread * 0.32, top + height * 0.73), (end + wave, top + height * 0.8), (end, top + height * (0.98 - abs(spread) * 0.13))], geo_tint(arr_FOG, (0.4 + index % 3 * 0.12) * strength), geo_ease(t))

def arr_shell(c, cx, cy, rx, ry, t, shade=1.0):
    points = []
    for index in range(121):
        angle = index * geo_TAU / 120
        x = cx + rx * math.sin(angle) * (0.82 + 0.18 * math.cos(angle))
        y = cy + ry * math.cos(angle)
        points.append((x + 0.045 * (y - cy), y))
    geo_polygon(c, points, geo_tint(arr_INK, 0.48 * shade), 5, t=geo_ease(t))
    geo_path(c, points[:61], geo_tint(arr_FOG, 0.78 * shade), geo_ease(t))
    for index in range(6):
        shift = (index - 2) * rx * 0.13
        geo_curve(c, [(cx + shift, cy - ry * 0.88), (cx + shift - rx * 0.2, cy - ry * 0.2), (cx + shift + rx * 0.1, cy + ry * 0.3), (cx + shift, cy + ry * 0.87)], geo_tint(arr_INK, 0.23 * shade), geo_ease(t))

def arr_script(c, t):
    arr_ink_ring(c, 0.25, 0.49, 0.13, 0.34, t, 7)
    geo_particles(c, arr_INK, 65, 22, (0.05, 0.13, 0.44, 0.87), (1 - t) * 0.04)
    geo_greeting(c, t, arr_INK, arr_FOG, x=0.72, tracking=False)

def arr_lexicon(c, t):
    for index, x in enumerate((0.2, 0.5, 0.8)):
        arr_ink_ring(c, x, 0.32, 0.077, 0.2, geo_clamp(t * 1.3 - index * 0.12), index * 5 + 2, geo_tint(arr_FOG, 0.7 + index * 0.12))
    geo_greeting(c, t, arr_INK, arr_FOG, x=0.5, y=0.65)

def arr_inkfall(c, t):
    arr_ink_ring(c, 0.28, 0.45, 0.13, 0.3, t, 15)
    for index in range(36):
        angle = index * geo_TAU / 36
        r = 0.15 + (1 - t) * 0.08 + index % 5 * 0.005
        x, y = (0.28 + r * math.cos(angle), 0.45 + r * 2.3 * math.sin(angle))
        if t > 0.12:
            geo_curve(c, [(x, y), (x - 0.02, y + 0.03), (x + 0.02, y + 0.06), (x + 0.01 * math.sin(index), y + 0.09)], geo_tint(arr_INK, 0.28 + t * 0.25))
    geo_particles(c, arr_FOG, 100, 8, (0.03, 0.08, 0.48, 0.9), (1 - t) * 0.13)
    geo_greeting(c, t, arr_FOG, geo_tint(arr_FOG, 0.8), x=0.74, tracking=False)

def arr_visitor(c, t):
    arr_heptapod(c, 0.23, 0.1, 0.18, 0.78, t)
    for layer in range(4):
        geo_landscape(c, geo_tint(arr_INK, 0.17), 0.64 + layer * 0.08, 0.014, layer + (1 - t), geo_ease(t), 11)
    geo_particles(c, arr_INK, 90, 13, (0.06, 0.15, 0.42, 0.85), (1 - t) * 0.07)
    geo_greeting(c, t, arr_INK, arr_FOG, x=0.72, tracking=False)

def arr_contact(c, t):
    arr_heptapod(c, 0.15, 0.1, 0.14, 0.77, t, 0.58)
    arr_heptapod(c, 0.84, 0.16, 0.14, 0.68, t, 0.42)
    arr_ink_ring(c, 0.5, 0.32, 0.072, 0.19, t, 9, geo_tint(arr_FOG, 0.7))
    geo_line(c, 0.05, 0.89, 0.95, 0.89, geo_tint(arr_INK, 0.35), geo_ease(t))
    geo_greeting(c, t, arr_INK, arr_FOG, x=0.5, y=0.58, tracking=False)

def arr_shard(c, t):
    arr_shell(c, 0.24, 0.44 - (1 - t) * 0.035, 0.075, 0.36, t)
    for layer in range(5):
        geo_landscape(c, geo_tint(arr_INK, 0.18 + layer * 0.1), 0.77 + layer * 0.035, 0.018, layer + (1 - t) * 0.5, geo_ease(t), 8)
    geo_particles(c, arr_INK, 50, 18, (0.08, 0.72, 0.94, 0.92), (1 - t) * 0.08)
    geo_greeting(c, t, arr_INK, arr_FOG, x=0.71, tracking=False)

def arr_ascent(c, t):
    arr_shell(c, 0.51, 0.3, 0.045, 0.24, t)
    for layer in range(6):
        geo_curve(c, [(0.03, 0.72 + layer * 0.035), (0.2, 0.35 + layer * 0.045), (0.37, 0.96), (0.52, 0.72)], geo_tint(arr_INK, 0.2 + layer * 0.07), geo_ease(t))
        geo_curve(c, [(0.97, 0.76 + layer * 0.028), (0.76, 0.48 + layer * 0.025), (0.67, 0.91), (0.53, 0.72)], geo_tint(arr_FOG, 0.14 + layer * 0.045), geo_ease(t))
    geo_greeting(c, t, arr_INK, arr_FOG, x=0.5, y=0.58, tracking=False)

def arr_threshold(c, t):
    for index in range(5):
        inset = index * 0.035
        geo_path(c, [(0.03 + inset, 0.09 + inset), (0.91 - inset, 0.09 + inset), (0.77 - inset, 0.82 - inset), (0.17 + inset, 0.82 - inset), (0.03 + inset, 0.09 + inset)], geo_tint(arr_FOG, 0.15 + index * 0.09), geo_ease(t))
    arr_ink_ring(c, 0.28, 0.43, 0.055, 0.145, t, 4)
    for x in (0.43, 0.55, 0.66):
        geo_line(c, x, 0.72, x + 0.035, 0.88, geo_tint(arr_INK, 0.4), geo_ease(t))
    geo_greeting(c, t, arr_INK, arr_FOG, x=0.62, y=0.28, tracking=False)
arr_STUDIES = {'arrival-script': ('ARRIVAL / broken ink', 'A branching brush circumference writes itself into view', arr_script, [arr_LANGUAGE_SOURCE]), 'arrival-lexicon': ('ARRIVAL / three logograms', 'Three different ink structures and a centered greeting', arr_lexicon, [arr_LANGUAGE_SOURCE]), 'arrival-inkfall': ('ARRIVAL / suspended ink', 'An ink cloud contracts into a frayed circular mark', arr_inkfall, [arr_LANGUAGE_SOURCE]), 'arrival-heptapod': ('ARRIVAL / visitor in fog', 'A seven-limbed silhouette emerges behind drifting mist', arr_visitor, [arr_CREATURE_SOURCE]), 'arrival-contact': ('ARRIVAL / Abbott and Costello', 'Two distant visitors frame a shared ink mark', arr_contact, [arr_CREATURE_SOURCE, arr_LANGUAGE_SOURCE]), 'arrival-shard': ('ARRIVAL / hovering shell', 'A narrow stone lozenge hangs over a low fog bank', arr_shard, [arr_SHELL_SOURCE]), 'arrival-ascent': ('ARRIVAL / valley approach', 'A distant shell above curving valley walls', arr_ascent, [arr_SHELL_SOURCE]), 'arrival-threshold': ('ARRIVAL / gravity threshold', 'An angled stone chamber opens onto a quiet ink mark', arr_threshold, [arr_SHELL_SOURCE])}


# ========================================================================
# Krypton designs
# ========================================================================

kry_BONE = (191, 194, 164)
kry_BRONZE = (183, 142, 91)
kry_ASH = (107, 130, 113)
kry_WORLD_SOURCE = 'https://e-zeppelin.ro/en/vlad-bina-design-for-a-virtual-world-and-then-back/'
kry_GENESIS_SOURCE = 'https://www.artofvfx.com/man-of-steel-dan-lemmon-vfx-supervisor-weta-digital/'
kry_DESIGN_SOURCE = 'https://www.fastcompany.com/1683341/alex-mcdowell-on-creating-krypton-and-the-future-of-production-design'

def kry_grown_spire(c, x, base, height, width, t, color=kry_BRONZE):
    for side in (-1, 1):
        for layer in range(3):
            spread = width * (1 - layer * 0.24)
            geo_curve(c, [(x + side * width, base), (x + side * spread * 0.25, base - height * 0.2), (x + side * spread, base - height * 0.6), (x, base - height)], geo_tint(color, 0.35 + layer * 0.24), geo_ease(t))

def kry_pod(c, x, y, rx, ry, t, color=kry_BONE):
    for side in (-1, 1):
        geo_curve(c, [(x, y - ry), (x + side * rx * 1.5, y - ry * 0.2), (x + side * rx, y + ry), (x, y + ry)], geo_tint(color, 0.7), geo_ease(t))
    geo_curve(c, [(x, y - ry * 0.6), (x - rx * 0.3, y), (x + rx * 0.3, y), (x, y + ry * 0.6)], geo_tint(color, 0.35), geo_ease(t))

def kry_city(c, t):
    for index in range(8):
        y = 0.04 + index * 0.025
        geo_curve(c, [(0.02, y), (0.26, y + 0.1), (0.7, y - 0.05), (0.98, y + 0.05)], geo_tint(kry_ASH, 0.19 + index * 0.05), geo_ease(t))
    for index in range(11):
        x = 0.035 + index * 0.038
        height = 0.22 + index * 7 % 6 * 0.056
        kry_grown_spire(c, x, 0.84, height, 0.018, geo_clamp(t * 1.6 - index * 0.025), kry_BONE if index % 3 else kry_BRONZE)
    for layer in range(4):
        geo_landscape(c, geo_tint(kry_BRONZE, 0.19 + layer * 0.1), 0.85 + layer * 0.025, 0.025, layer + 3, geo_ease(t), 10)
    geo_greeting(c, t, kry_BRONZE, kry_BONE, x=0.72, y=0.32, tracking=False)

def kry_council(c, t):
    for side in (-1, 1):
        for layer in range(7):
            outer = 0.5 + side * (0.14 + layer * 0.045)
            inner = 0.5 + side * (0.04 + layer * 0.018)
            geo_curve(c, [(outer, 0.88), (inner, 0.81), (outer, 0.35), (inner, 0.04)], geo_tint(kry_BRONZE if layer % 2 else kry_BONE, 0.2 + layer * 0.08), geo_ease(t))
    for radius in (0.2, 0.27, 0.34):
        geo_ellipse(c, 0.5, 0.82, radius, radius * 0.2, geo_tint(kry_BRONZE, 0.6), geo_ease(t))
    for index in range(9):
        a = index * geo_TAU / 9
        kry_pod(c, 0.5 + 0.25 * math.cos(a), 0.82 + 0.04 * math.sin(a), 0.009, 0.045, t, geo_tint(kry_BONE, 0.7))
    geo_greeting(c, t, kry_BRONZE, kry_BONE, x=0.5, y=0.29, tracking=False)

def kry_genesis(c, t):
    water = (104, 169, 155)
    for index in range(6):
        x = 0.055 + index * 0.066
        bend = 0.022 * math.sin(index * 2 + (1 - t) * 2)
        geo_curve(c, [(x, 0.94), (x - 0.06, 0.63), (x + bend, 0.33), (x, 0.07)], geo_tint(water, 0.45), geo_ease(t))
        for row in range(4):
            y = 0.17 + row * 0.18 + index % 2 * 0.04
            kry_pod(c, x + 0.016, y, 0.012, 0.049, geo_clamp(t * 1.7 - row * 0.08), geo_tint(kry_BONE, 0.45 + row * 0.12))
    geo_particles(c, water, 120, 41, (0.03, 0.08, 0.96, 0.94), (1 - t) * 0.1)
    geo_curve(c, [(0.48, 0.85), (0.67, 0.74), (0.81, 0.95), (0.95, 0.79)], geo_tint(water, 0.35), geo_ease(t))
    geo_greeting(c, t, water, kry_BONE, x=0.72, tracking=False)

def kry_vault(c, t):
    for layer in range(10):
        rx = 0.055 + layer * 0.012
        ry = 0.15 + layer * 0.026
        geo_ellipse(c, 0.25, 0.49, rx, ry, geo_tint(kry_BRONZE if layer % 2 else kry_BONE, 0.25 + layer * 0.06), geo_ease(t), start=0.2, span=geo_TAU - 0.4)
    for index in range(12):
        angle = index * geo_TAU / 12
        x, y = (0.25 + 0.11 * math.cos(angle), 0.49 + 0.25 * math.sin(angle))
        kry_pod(c, x, y, 0.009, 0.031, geo_clamp(t * 1.6 - index * 0.035), kry_BONE)
    geo_polygon(c, [(0.22, 0.4), (0.27, 0.37), (0.3, 0.46), (0.27, 0.55), (0.22, 0.52)], geo_tint(kry_BONE, 0.65), 4, t=geo_ease(t))
    geo_greeting(c, t, kry_BRONZE, kry_BONE, x=0.72, tracking=False)

def kry_archive(c, t):
    for band, y in enumerate((0.14, 0.78)):
        for index in range(19):
            x = 0.055 + index * 0.048
            bend = (-1 if index % 2 else 1) * 0.015
            geo_curve(c, [(x, y), (x + bend, y + 0.035), (x - bend, y + 0.08), (x + 0.01, y + 0.1)], geo_tint(kry_BRONZE, 0.45 + index % 3 * 0.15), geo_clamp(t * 1.8 - index * 0.02))
            geo_curve(c, [(x - 0.007, y + 0.02), (x + 0.02, y - 0.01), (x + 0.025, y + 0.06), (x + 0.005, y + 0.07)], geo_tint(kry_BONE, 0.25), geo_ease(t))
    for index in range(8):
        x = 0.07 + index * 0.025
        geo_curve(c, [(x, 0.69), (0.4, 0.7), (0.04, 0.28), (0.36 - x, 0.28)], geo_tint(kry_ASH, 0.4 + index * 0.04), geo_ease(t))
    geo_greeting(c, t, kry_BRONZE, kry_BONE, x=0.7, y=0.34, tracking=False)

def kry_house(c, t):
    for index in range(5):
        x = 0.09 + index * 0.065
        geo_curve(c, [(x - 0.055, 0.73), (x - 0.04, 0.27), (x + 0.09, 0.2), (x + 0.065, 0.73)], geo_tint(kry_BONE, 0.3 + index * 0.1), geo_ease(t))
        geo_curve(c, [(x - 0.05, 0.71), (x - 0.1, 0.85), (x + 0.13, 0.9), (x + 0.06, 0.7)], geo_tint(kry_BRONZE, 0.55), geo_ease(t))
    for layer in range(4):
        geo_landscape(c, geo_tint(kry_ASH, 0.3 + layer * 0.1), 0.78 + layer * 0.04, 0.027, 5 + layer, geo_ease(t), 9)
    geo_ellipse(c, 0.82, 0.17, 0.025, 0.065, geo_tint(kry_BRONZE, 0.7), geo_ease(t))
    geo_greeting(c, t, kry_BRONZE, kry_BONE, x=0.72, y=0.31, tracking=False)

def kry_launch(c, t):
    center = 0.25
    for side in (-1, 1):
        for layer in range(5):
            spread = 0.055 + layer * 0.018
            geo_curve(c, [(center, 0.19), (center + side * spread, 0.25), (center + side * spread * 1.4, 0.77), (center, 0.87)], geo_tint(kry_BONE if layer % 2 else kry_BRONZE, 0.35 + layer * 0.1), geo_ease(t))
    kry_pod(c, center, 0.5, 0.035, 0.14, t, kry_BONE)
    for index in range(6):
        geo_curve(c, [(0.48, 0.74 + index * 0.024), (0.6, 0.65), (0.8, 0.9), (0.96, 0.75 + index * 0.01)], geo_tint(kry_BRONZE, 0.2 + index * 0.07), geo_ease(t))
    geo_particles(c, kry_BONE, 75, 17, (0.03, 0.06, 0.96, 0.9), (1 - t) * 0.045)
    geo_greeting(c, t, kry_BRONZE, kry_BONE, x=0.72, tracking=False)
kry_STUDIES = {'krypton-city': ('KRYPTON / city beneath the quarry', 'Grown spires below layered, eroded rock ribbons', kry_city, [kry_WORLD_SOURCE, kry_GENESIS_SOURCE]), 'krypton-council': ('KRYPTON / council of bronze', 'Sweeping Art Nouveau ribs and a ring of organic seats', kry_council, [kry_WORLD_SOURCE, kry_DESIGN_SOURCE]), 'krypton-genesis': ('KRYPTON / Genesis chamber', 'Suspended seed pods on submerged kelp-like structures', kry_genesis, [kry_GENESIS_SOURCE]), 'krypton-vault': ('KRYPTON / genetic vault', 'Nested bone hoops and organic seed forms', kry_vault, [kry_GENESIS_SOURCE, kry_DESIGN_SOURCE]), 'krypton-archive': ('KRYPTON / engraved archive', 'Original curved inscription marks in weathered bronze', kry_archive, [kry_WORLD_SOURCE, kry_DESIGN_SOURCE]), 'krypton-house': ('KRYPTON / House of El', 'Shell-grown dwellings on a dark, eroded homeworld', kry_house, [kry_WORLD_SOURCE]), 'krypton-launch': ('KRYPTON / seed cradle', 'Petal-like bronze structures open around a living vessel', kry_launch, [kry_DESIGN_SOURCE, kry_GENESIS_SOURCE])}


# ========================================================================
# Film environments
# ========================================================================

film_DUNE = 'https://www.pushing-pixels.org/2024/04/10/production-design-of-dune-interview-with-patrice-vermette.html'
film_ROTK = 'https://archives.theonering.net/features/newsroom/files/rotk_prod_notes.html'

def film_gondor(c, t):
    stone, gold = ((207, 217, 212), (201, 181, 112))
    for index in range(5):
        rx, ry = (0.18 - index * 0.023, 0.26 - index * 0.025)
        geo_ellipse(c, 0.24, 0.57 - index * 0.035, rx, ry, geo_tint(stone, 0.35 + index * 0.12), geo_ease(t), start=math.pi, span=math.pi)
        geo_line(c, 0.24 - rx, 0.57 - index * 0.035, 0.24 - rx, 0.84, geo_tint(stone, 0.3))
        geo_line(c, 0.24 + rx, 0.57 - index * 0.035, 0.24 + rx, 0.84, geo_tint(stone, 0.3))
    geo_polygon(c, [(0.2, 0.54), (0.2, 0.29), (0.235, 0.2), (0.27, 0.29), (0.27, 0.54)], stone, 3, t=geo_ease(t))
    geo_line(c, 0.235, 0.19, 0.235, 0.075, gold, geo_ease(t))
    geo_landscape(c, geo_tint(stone, 0.24), 0.84, 0.12, 4, geo_ease(t), 11)
    geo_line(c, 0.5, 0.78, 0.93, 0.78, geo_tint(gold, 0.45), geo_ease(t))
    geo_greeting(c, t, gold, stone, x=0.71)

def film_arrakis(c, t):
    sand, stone = ((221, 168, 90), (159, 157, 142))
    geo_ellipse(c, 0.19, 0.25 + (1 - t) * 0.05, 0.045, 0.12, geo_tint(sand, 0.9), geo_ease(t))
    geo_polygon(c, [(0.28, 0.78), (0.34, 0.12), (0.46, 0.12), (0.5, 0.78)], geo_tint(stone, 0.7), 3, t=geo_ease(t))
    geo_polygon(c, [(0.86, 0.78), (0.89, 0.12), (0.95, 0.12), (0.98, 0.78)], geo_tint(stone, 0.45), 4, t=geo_ease(t))
    geo_line(c, 0.35, 0.13, 0.4, 0.77, geo_tint(sand, 0.4), geo_ease(t))
    for index in range(4):
        geo_landscape(c, geo_tint(sand, 0.22 + index * 0.17), 0.79 + index * 0.035, 0.025, index + 4, geo_ease(t), 6 + index * 2)
    geo_particles(c, geo_tint(sand, 0.7), 70, 19, (0.03, 0.71, 0.97, 0.96), (1 - t) * 0.15)
    geo_greeting(c, t, sand, (228, 216, 184), x=0.68, tracking=False)

def film_giedi_prime(c, t):
    silver = (207, 213, 217)
    geo_ellipse(c, 0.24, 0.38, 0.11, 0.29, silver, geo_ease(t))
    geo_ellipse(c, 0.24, 0.38, 0.115, 0.303, geo_tint(silver, 0.2))
    for index in range(9):
        y = 0.64 + index * 0.029
        geo_curve(c, [(0.02, y), (0.2, y - 0.16), (0.36, y - 0.16), (0.46, y)], geo_tint(silver, 0.17 + index * 0.07), geo_ease(t))
    for index in range(16):
        angle = math.pi * (index + 0.5) / 16
        geo_line(c, 0.24 + 0.15 * math.cos(angle), 0.77 + 0.16 * math.sin(angle), 0.24 + 0.2 * math.cos(angle), 0.77 + 0.18 * math.sin(angle), geo_tint(silver, 0.25))
    geo_line(c, 0.5, 0.77, 0.94, 0.77, geo_tint(silver, 0.4), geo_ease(t))
    geo_greeting(c, t, silver, (237, 238, 235), x=0.72)

def film_arrival(c, t):
    fog, ink = ((194, 205, 199), (123, 145, 143))
    geo_rect(c, 0.065, 0.12, 0.43, 0.86, geo_tint(fog, 0.2), geo_ease(t))
    for layer in range(4):
        points = []
        for index in range(151):
            angle = index * geo_TAU / 150
            radius = 0.11 + 0.006 * math.sin(index * 0.35 + layer) + layer * 0.002
            points.append((0.25 + radius * math.cos(angle), 0.48 + radius * 2.5 * math.sin(angle)))
        geo_path(c, points, geo_tint(fog if layer == 0 else ink, 0.45 + layer * 0.11), geo_ease(t))
    for index in range(13):
        angle = index * 0.45
        x = 0.25 + 0.118 * math.cos(angle)
        y = 0.48 + 0.3 * math.sin(angle)
        geo_line(c, x, y, x + 0.018 * math.cos(angle), y + 0.04 * math.sin(angle), ink)
    geo_particles(c, fog, 90, 3, (0.05, 0.73, 0.96, 0.91), (1 - t) * 0.025)
    geo_greeting(c, t, ink, fog, x=0.72, tracking=False)

def film_krypton(c, t):
    bone, bronze = ((174, 186, 172), (174, 131, 83))
    for index in range(7):
        offset = index * 0.024
        geo_curve(c, [(0.06 + offset, 0.85), (0.02 + offset, 0.51), (0.23, 0.13 + offset), (0.38 - offset, 0.83)], geo_tint(bone, 0.3 + index * 0.075), geo_ease(t))
    for index in range(6):
        y = 0.38 + index * 0.072
        geo_curve(c, [(0.11, y), (0.17, y + 0.05), (0.28, y - 0.04), (0.34, y)], geo_tint(bronze, 0.55), geo_ease(t))
    geo_curve(c, [(0.48, 0.79), (0.66, 0.93), (0.9, 0.67), (0.94, 0.83)], geo_tint(bronze, 0.7), geo_ease(t))
    geo_particles(c, geo_tint(bone, 0.55), 45, 26, (0.1, 0.16, 0.4, 0.82), (1 - t) * 0.025)
    geo_greeting(c, t, bronze, (218, 224, 204), x=0.71, tracking=False)
film_STUDIES = {'gondor': ('LOTR / Gondor', 'Pale concentric terraces and a high citadel', film_gondor, [film_ROTK]), 'arrakis': ('DUNE / Arrakis', 'Angled stone massing, sun and drifting dunes', film_arrakis, [film_DUNE]), 'giedi-prime': ('DUNE: PART TWO / Giedi Prime', 'Monochrome arena geometry and a black-sun silhouette', film_giedi_prime, [film_DUNE]), 'arrival': ('ARRIVAL / aperture and ink', 'Fog, a luminous chamber and an original ink-ring study', film_arrival, ['https://www.bizbooks.net/blog/the-biz-interview-patrice-vermette', 'https://graham-edwards.com/persistence-of-vision-extract-from-arrival-article-in-cinefex-150/']), **arr_STUDIES, 'krypton': ('MAN OF STEEL / Kryptonian bone', 'Bronze filigree and organic structural ribs', film_krypton, ['https://www.fastcompany.com/1683341/alex-mcdowell-on-creating-krypton-and-the-future-of-production-design']), **kry_STUDIES}


# ========================================================================
# Braille canvas and cinematic designs
# ========================================================================

cin_MESSAGE = 'Welcome Mr. Harrington'
cin_RESET = '\x1b[0m'
cin_TAU = math.tau
cin_WHITE = (220, 240, 243)
cin_THEMES = {'phosphor': ('PHOSPHOR / retro vector display', 'Amber traces, phosphor persistence, scanning reveal'), 'grid': ('GRID / Tron study', 'Light trails assemble a cyan circuit around the greeting'), 'tet': ('TET / Oblivion study', 'Chalk, vermilion, precise geometry and sliding registration marks'), 'scope': ('SCOPE / Spectral study', 'A military optical scope with a rotating acquisition sweep'), 'mk42': ('MK42 / Iron Man 3 study', 'Counter-rotating instrument rings and cyan/amber callouts'), 'atlas': ('ATLAS / neural field', 'A breathing holographic mesh and synchronized waveforms')}

def cin_clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))

def cin_tint(color, amount):
    return tuple((round(channel * cin_clamp(amount)) for channel in color))

@dataclass(frozen=True)
class cin_Cell:
    char: str = ' '
    fg: tuple = cin_WHITE
    bg: tuple = (0, 0, 0)
    bold: bool = False

class cin_Canvas:
    """A 2-by-4 subpixel drawing surface for each terminal character cell."""

    def __init__(self, width, height, background=(0, 0, 0)):
        self.width, self.height = (width, height)
        self.w, self.h = (width * 2, height * 4)
        self.background = background
        self.pixels = [[None] * self.w for _ in range(self.h)]
        self.text_cells = {}

    def dot(self, x, y, color, glow=False):
        x, y = (round(x), round(y))
        if not (0 <= x < self.w and 0 <= y < self.h):
            return
        previous = self.pixels[y][x]
        self.pixels[y][x] = color if previous is None else tuple((max(a, b) for a, b in zip(previous, color)))
        if glow:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                self.dot(x + dx, y + dy, cin_tint(color, 0.16))

    def line(self, x0, y0, x1, y1, color, progress=1.0, glow=False):
        x1, y1 = (x0 + (x1 - x0) * cin_clamp(progress), y0 + (y1 - y0) * cin_clamp(progress))
        steps = max(1, math.ceil(max(abs(x1 - x0), abs(y1 - y0))))
        for step in range(steps + 1):
            p = step / steps
            self.dot(x0 + (x1 - x0) * p, y0 + (y1 - y0) * p, color, glow)

    def path(self, points, color, progress=1.0, glow=False):
        lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
        remaining = sum(lengths) * cin_clamp(progress)
        for start, end, length in zip(points, points[1:], lengths):
            if remaining <= 0:
                break
            self.line(*start, *end, color, min(1.0, remaining / max(length, 0.01)), glow)
            remaining -= length

    def arc(self, cx, cy, radius, start, end, color, dashed=False, glow=False):
        steps = max(2, math.ceil(abs(end - start) * radius * 1.5))
        for step in range(steps + 1):
            angle = start + (end - start) * step / steps
            if not dashed or int(angle % cin_TAU * 32 / cin_TAU) % 4 < 2:
                self.dot(cx + math.cos(angle) * radius, cy + math.sin(angle) * radius, color, glow)

    def ticks(self, cx, cy, radius, count, color, phase=0.0):
        for index in range(count):
            angle = phase + index * cin_TAU / count
            length = 3 if index % 3 == 0 else 1.5
            self.line(cx + radius * math.cos(angle), cy + radius * math.sin(angle), cx + (radius + length) * math.cos(angle), cy + (radius + length) * math.sin(angle), color)

    def text(self, x, y, text, color=cin_WHITE, bold=False, center=False):
        x = round(x - len(text) / 2) if center else round(x)
        for offset, char in enumerate(text):
            col = x + offset
            if 0 <= col < self.width and 0 <= y < self.height:
                self.text_cells[col, y] = cin_Cell(char, color, self.background, bold)
                for px in range(max(0, (col - 1) * 2), min(self.w, (col + 2) * 2)):
                    for py in range(y * 4, min(self.h, (y + 1) * 4)):
                        self.pixels[py][px] = None

    def greeting(self, x, y, progress, accent, main=cin_WHITE, tracking=False):
        reveal = cin_clamp((progress - 0.22) / 0.55)
        heading = 'W E L C O M E' if tracking else 'WELCOME'
        name = 'MR. HARRINGTON'
        if reveal > 0:
            self.text(x, y, heading[:math.ceil(len(heading) * reveal)], cin_tint(accent, reveal), center=True)
        if reveal > 0.2:
            visible = math.ceil(len(name) * cin_clamp((reveal - 0.2) / 0.8))
            self.text(round(x - len(name) / 2), y + 2, name[:visible], cin_tint(main, reveal), True)

    def cells(self):
        bits = ((0, 0, 1), (0, 1, 2), (0, 2, 4), (1, 0, 8), (1, 1, 16), (1, 2, 32), (0, 3, 64), (1, 3, 128))
        rows = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if (x, y) in self.text_cells:
                    row.append(self.text_cells[x, y])
                    continue
                mask, colors = (0, [])
                for dx, dy, bit in bits:
                    color = self.pixels[y * 4 + dy][x * 2 + dx]
                    if color is not None and max(color) > 2:
                        mask |= bit
                        colors.append(color)
                color = tuple((max(channels) for channels in zip(*colors))) if colors else cin_WHITE
                row.append(cin_Cell(chr(10240 + mask) if mask else ' ', color, self.background))
            rows.append(row)
        return rows

    def render(self):
        output = []
        for row in self.cells():
            parts, previous = ([], None)
            for cell in row:
                style = (cell.fg, cell.bg, cell.bold)
                if style != previous:
                    parts.append('\x1b[{};38;2;{};{};{};48;2;{};{};{}m'.format(1 if cell.bold else 22, *cell.fg, *cell.bg))
                    previous = style
                parts.append(cell.char)
            output.append(''.join(parts) + cin_RESET)
        return output

def cin_registration(c, color, progress, inset=3, size=9):
    for x, sx in ((inset, 1), (c.w - inset - 1, -1)):
        for y, sy in ((inset, 1), (c.h - inset - 1, -1)):
            c.path([(x, y + sy * size), (x, y), (x + sx * size, y)], color, progress)

def cin_phosphor(c, t):
    amber = (246, 182, 79)
    dim = cin_tint(amber, 0.19)
    left, right = (6, c.w - 7)
    mid = c.h * 0.73
    for x in range(left, right, 6):
        c.dot(x, c.h * 0.22, dim)
        c.dot(x, mid + 7, dim)
    for y in (7, c.h - 8):
        c.line(left, y, right, y, dim)
    for x in range(left, right, 12):
        c.line(x, c.h - 9, x, c.h - 6, cin_tint(amber, 0.45))
    points = []
    for x in range(left, right):
        p = (x - left) / max(1, right - left)
        envelope = math.sin(p * math.pi) ** 2
        wave = math.sin(p * 45 + (1 - t) * 10) * math.cos(p * 11) * 5 * envelope
        points.append((x, mid + wave))
    c.path(points, cin_tint(amber, 0.8), cin_clamp(t * 1.8), True)
    scan = left + (right - left) * cin_clamp(t * 1.25)
    if t < 0.84:
        c.line(scan, 10, scan, c.h - 12, cin_tint(amber, 0.5))
    c.greeting(c.width / 2, 3, t, amber, (255, 222, 165), True)
    c.line(c.w * 0.43, c.h - 4, c.w * 0.57, c.h - 4, cin_tint(amber, cin_clamp(t * 1.2)))

def cin_grid(c, t):
    cyan, orange = ((62, 228, 255), (255, 155, 66))
    dim = cin_tint(cyan, 0.2)
    horizon = c.h * 0.66
    for x in range(-c.w, c.w * 2, max(12, c.w // 9)):
        c.line(c.w / 2, horizon, x, c.h - 2, cin_tint(cyan, 0.16))
    for gap in (2, 5, 10, 17):
        y = min(c.h - 2, horizon + gap)
        c.line(4, y, c.w - 5, y, dim)
    routes = [[(3, 5), (c.w * 0.25, 5), (c.w * 0.33, 14), (c.w * 0.33, 21)], [(c.w - 4, 5), (c.w * 0.76, 5), (c.w * 0.68, 14), (c.w * 0.68, 21)], [(4, c.h - 9), (c.w * 0.2, c.h - 9), (c.w * 0.28, c.h - 17), (c.w * 0.39, c.h - 17)], [(c.w - 5, c.h - 9), (c.w * 0.8, c.h - 9), (c.w * 0.72, c.h - 17), (c.w * 0.61, c.h - 17)]]
    for index, route in enumerate(routes):
        c.path(route, dim)
        c.path(route, cyan, cin_clamp(t * 1.55 - index * 0.08), True)
    c.path([(c.w * 0.36, 16), (c.w * 0.4, 12), (c.w * 0.6, 12), (c.w * 0.64, 16)], cin_tint(cyan, 0.65), cin_clamp((t - 0.15) * 2))
    c.greeting(c.width / 2, 4, t, cyan, cin_WHITE, True)
    c.line(c.w * 0.46, 8, c.w * 0.54, 8, orange, cin_clamp(t * 2))
    for x in (c.w * 0.25, c.w * 0.76):
        c.arc(x, 5, 1.5, 0, cin_TAU, orange)

def cin_tet(c, t):
    chalk, coral = ((224, 235, 224), (255, 87, 56))
    dim = cin_tint(chalk, 0.21)
    cin_registration(c, dim, cin_clamp(t * 2), size=6)
    cx, cy, radius = (c.w * 0.2, c.h * 0.48, c.h * 0.28)
    triangle = [(cx, cy + radius), (cx - radius, cy - radius * 0.7), (cx + radius, cy - radius * 0.7), (cx, cy + radius)]
    c.path(triangle, chalk, cin_clamp(t * 1.7), True)
    c.path([(cx - radius * 0.63, cy - radius * 0.42), (cx + radius * 0.63, cy - radius * 0.42)], coral, cin_clamp((t - 0.18) * 2.2))
    c.line(c.w * 0.39, 10, c.w * 0.39, c.h - 11, dim)
    for y in (10, c.h - 11):
        c.line(c.w * 0.39, y, c.w - 8, y, dim)
        for x in range(round(c.w * 0.4), c.w - 8, 10):
            c.dot(x, y, chalk)
    text_x = c.width * 0.66
    c.greeting(text_x, 4, t, chalk, chalk, True)
    under = c.h * 0.68
    for index in range(15):
        x = c.w * 0.46 + index * c.w * 0.028
        c.line(x, under, x, under + (2 if index % 3 else 5), cin_tint(chalk, 0.3 + index / 30))
    c.line(c.w * 0.48, c.h - 6, c.w * 0.63, c.h - 6, coral, cin_clamp((t - 0.45) * 3))
    slide = (1 - cin_clamp(t * 1.8)) * 10
    c.path([(c.w * 0.46 - slide, 17), (c.w * 0.44 - slide, 17), (c.w * 0.44 - slide, 30)], coral)

def cin_scope(c, t):
    green, white = ((139, 204, 131), (215, 230, 208))
    dim = cin_tint(green, 0.22)
    cx, cy, radius = (c.w * 0.24, c.h * 0.49, c.h * 0.34)
    c.arc(cx, cy, radius, 0, cin_TAU, cin_tint(green, 0.5))
    c.arc(cx, cy, radius * 0.68, 0, cin_TAU, dim, True)
    c.ticks(cx, cy, radius + 1, 24, cin_tint(green, 0.55))
    c.line(cx - radius - 5, cy, cx + radius + 5, cy, dim)
    c.line(cx, cy - radius - 5, cx, cy + radius + 5, dim)
    angle = -math.pi / 3 + (1 - t) * cin_TAU * 1.3
    for trail in range(12):
        a = angle - trail * 0.035
        c.line(cx, cy, cx + math.cos(a) * radius, cy + math.sin(a) * radius, cin_tint(green, (1 - trail / 12) * 0.55))
    c.arc(cx, cy, 3, 0, cin_TAU, white)
    for a, r in ((-0.65, 0.62), (2.4, 0.72), (0.7, 0.4)):
        c.dot(cx + math.cos(a) * radius * r, cy + math.sin(a) * radius * r, white, True)
    tx = c.width * 0.68
    c.greeting(tx, 4, t, green, white)
    x0, x1 = (c.w * 0.46, c.w - 8)
    c.line(x0, 12, x1, 12, dim)
    c.line(x0, c.h - 13, x1, c.h - 13, dim)
    for index in range(17):
        x = x0 + (x1 - x0) * index / 16
        length = 1 + (index * 7 + 3) % 6
        c.line(x, c.h - 9, x, c.h - 9 - length, cin_tint(green, 0.4))
    c.path([(x0, 18), (x0 - 4, 18), (x0 - 4, 30), (x0, 30)], green, cin_clamp(t * 2))

def cin_mk42(c, t):
    cyan, amber = ((108, 218, 246), (247, 184, 79))
    cx, cy, radius = (c.w * 0.25, c.h * 0.5, c.h * 0.35)
    turn = (1 - t) * math.pi * 1.2
    for index, factor in enumerate((1, 0.8, 0.56)):
        phase = turn * (-1 if index % 2 else 1)
        color = cyan if index != 1 else amber
        for quadrant in range(3):
            start = phase + quadrant * cin_TAU / 3
            c.arc(cx, cy, radius * factor, start, start + cin_TAU * 0.22, cin_tint(color, 0.7 if index else 1.0), glow=index == 0)
    c.ticks(cx, cy, radius + 2, 36, cin_tint(cyan, 0.28), turn * 0.2)
    c.arc(cx, cy, radius * 0.27, 0, cin_TAU, cin_tint(cyan, 0.8))
    c.path([(cx, cy - 3), (cx + 3, cy + 2), (cx - 3, cy + 2), (cx, cy - 3)], amber)
    c.path([(cx + radius * 0.7, cy - 6), (c.w * 0.51, 12), (c.w - 8, 12)], cin_tint(cyan, 0.5), cin_clamp(t * 1.7))
    c.path([(cx + radius * 0.7, cy + 6), (c.w * 0.52, c.h - 12), (c.w - 8, c.h - 12)], cin_tint(amber, 0.65), cin_clamp((t - 0.1) * 1.8))
    c.greeting(c.width * 0.69, 4, t, cyan, cin_WHITE, True)
    for index in range(9):
        x = c.w * 0.57 + index * 4
        c.line(x, c.h - 7, x + 2, c.h - 7, cin_tint(amber, 0.3 + 0.07 * index))

def cin_atlas(c, t):
    cyan, blue, gold = ((105, 236, 237), (59, 112, 210), (232, 194, 119))
    cx, cy, radius = (c.w * 0.74, c.h * 0.48, c.h * 0.32)
    phase = (1 - t) * cin_TAU
    for ring in range(8):
        points = []
        for step in range(161):
            angle = step * cin_TAU / 160
            wobble = math.sin(angle * 3 + phase + ring * 0.65) * (2 + ring * 0.12)
            r = radius * (0.52 + ring * 0.055) + wobble
            points.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
        c.path(points, cin_tint(cyan if ring % 3 else blue, 0.25 + ring * 0.065), cin_clamp(t * 2))
    c.arc(cx, cy, radius + 3, -1.5, 0.9, cin_tint(gold, 0.7))
    c.arc(cx, cy, radius + 5, 1.5, 4.2, cin_tint(blue, 0.6), True)
    for index in range(8):
        a = index * cin_TAU / 8 + phase * 0.12
        c.dot(cx + math.cos(a) * (radius + 3), cy + math.sin(a) * (radius + 3), gold, True)
    c.greeting(c.width * 0.28, 4, t, cyan, cin_WHITE)
    for band in range(2):
        points = []
        for x in range(7, round(c.w * 0.51)):
            p = (x - 7) / max(1, c.w * 0.51 - 7)
            y = c.h * 0.73 + band * 3 + math.sin(p * 20 + phase + band) * math.sin(p * math.pi) * 2
            points.append((x, y))
        c.path(points, cin_tint(cyan if band == 0 else gold, 0.5), cin_clamp(t * 1.7))
    c.line(7, 10, c.w * 0.48, 10, cin_tint(cyan, 0.25))
    c.line(7, c.h - 6, c.w * 0.48, c.h - 6, cin_tint(cyan, 0.25))
cin_PAINTERS = {'phosphor': cin_phosphor, 'grid': cin_grid, 'tet': cin_tet, 'scope': cin_scope, 'mk42': cin_mk42, 'atlas': cin_atlas}
cin_ORIGINAL_THEMES = tuple(cin_THEMES)
cin_REFERENCES = {'phosphor': ['https://github.com/0xN1nja/awesome-dotfiles'], 'grid': ['https://gmunk.com/TRON-Board-Room', 'https://github.com/GitSquared/edex-ui'], 'tet': ['https://gmunk.com/OBLIVION-GFX'], 'scope': ['https://www.pushing-pixels.org/2018/02/13/the-art-and-craft-of-screen-graphics-interview-with-todd-a-marks.html'], 'mk42': ['https://www.cantinacreative.com/film/iron-man-3'], 'atlas': ['https://territorystudio.com/project/atlas/']}
for key, (title, description, painter, references) in (ui_STUDIES | ui_COMPACT_STUDIES | film_STUDIES).items():
    cin_THEMES[key] = (title, description)
    cin_PAINTERS[key] = painter
    cin_REFERENCES[key] = references
cin_COLLECTIONS = {'original': cin_ORIGINAL_THEMES, 'interfaces': tuple(ui_STUDIES), 'compact': tuple(ui_COMPACT_STUDIES), 'films': tuple(film_STUDIES), 'arrival': tuple((key for key in film_STUDIES if key.startswith('arrival'))), 'krypton': tuple((key for key in film_STUDIES if key.startswith('krypton'))), 'all': tuple(cin_THEMES)}

def cin_frame_height(theme, height):
    return max(1, height // 2) if theme in ui_COMPACT_STUDIES else height

def cin_scene(theme, width, height, progress=1.0):
    c = cin_Canvas(width, height)
    minimum_height = 6 if theme in ui_COMPACT_STUDIES else 12
    if width < 50 or height < minimum_height:
        lines = textwrap.wrap(cin_MESSAGE, width)
        top = max(0, (height - len(lines)) // 2)
        for index, line in enumerate(lines[:height]):
            c.text(max(0, (width - len(line)) // 2), top + index, line, cin_WHITE, True)
    else:
        cin_PAINTERS[theme](c, cin_clamp(progress))
    return c


# ========================================================================
# Lima and ThinkPad lettering
# ========================================================================

lima_MESSAGE = 'WELCOME MR. HARRINGTON'
lima_BLOCK_MESSAGE = 'WELCOME MR. HARRINGTON'
lima_BLOCK_FADE_SECONDS = 1.0
lima_BLOCK_FADE_FRAMES = 50
lima_BANNER = ('⡄⠀⡄⡤⠤⠄⡄⠀⠀⡠⠤⡀⡠⠤⡀⣄⢀⡄⡤⠤⠄⠀⠀⠀ ⣄⢀⡄⡤⠤⡀⠀⠀⠀⠀⠀⠀ ⡄⠀⡄⡠⠤⡀⡤⠤⡀⡤⠤⡀⠠⡤⠀⡄⠀⡄⡠⠤⡀⠤⡤⠄⡠⠤⡀⡄⠀⡄', '⡇⡄⡇⡗⠒⠀⡇⠀⠀⡇⠀⠀⡇⠀⡇⡇⠃⡇⡗⠒⠀⠀⠀⠀ ⡇⠃⡇⡧⡤⠃⠀⠀⠀⠀⠀⠀ ⡗⠒⡇⡧⠤⡇⡧⡤⠃⡧⡤⠃⠀⡇⠀⡏⠢⡇⡇⠤⡄⠀⡇⠀⡇⠀⡇⡏⠢⡇', '⠋⠈⠃⠓⠒⠂⠓⠒⠂⠑⠒⠁⠑⠒⠁⠃⠀⠃⠓⠒⠂⠀⠀⠀ ⠃⠀⠃⠃⠈⠂⠀⠃⠀⠀⠀⠀ ⠃⠀⠃⠃⠀⠃⠃⠈⠂⠃⠈⠂⠐⠓⠀⠃⠀⠃⠑⠒⠁⠀⠃⠀⠑⠒⠁⠃⠀⠃')
lima_PURPLE = '\x1b[38;2;192;132;252m'
lima_SOFT_PURPLE = '\x1b[38;2;126;87;166m'
lima_WHITE = '\x1b[38;2;245;245;245m'
lima_RESET = '\x1b[0m'
lima_THINKPAD_RED = (226, 35, 26)
lima_THINKPAD_GRAY = (176, 180, 184)
lima_THINKPAD_PALETTES = {'red-gray': ('Red to gray', lima_THINKPAD_RED, lima_THINKPAD_GRAY, lima_THINKPAD_RED), 'silver': ('Silver lettering, red accents', (210, 214, 220), (152, 158, 168), lima_THINKPAD_RED), 'gray-red': ('Gray to red', lima_THINKPAD_GRAY, lima_THINKPAD_RED, (255, 64, 64)), 'carbon': ('Charcoal to silver, bright red accents', (104, 110, 118), (196, 200, 208), (239, 51, 64)), 'crimson': ('Deep crimson to gray', (170, 18, 43), (198, 192, 196), (255, 48, 64)), 'red-white': ('Red to near-white', (230, 33, 42), (236, 238, 242), (255, 35, 35))}
lima_ACCENT_SHAPES = {'round': '●', 'square': '■'}
lima_THINKPAD_VARIANTS = tuple(((palette, shape) for palette in lima_THINKPAD_PALETTES for shape in lima_ACCENT_SHAPES))
lima_ALL_THINKPAD_VARIANTS = tuple(((palette, shape, None, 'fade') for palette, shape in lima_THINKPAD_VARIANTS)) + (('red-gray', 'square', 85, 'fade'), ('silver', 'round', 85, 'wipe'), ('carbon', 'square', 85, 'scan'), ('crimson', 'round', 85, 'center'), ('gray-red', 'square', 93, 'typewriter'), ('red-white', 'round', 93, 'pulse'), ('carbon', 'round', 93, 'wipe'), ('red-gray', 'square', 93, 'scan'), ('carbon', 'square', 100, 'fade'), ('red-white', 'square', 100, 'scan'), ('silver', 'round', 100, 'center'), ('crimson', 'square', 100, 'typewriter'))
lima_STYLES = {'dots': 'Original dotted lettering with a white and purple sweep', 'typewriter': 'Compact purple panel with text typed into place', 'blocks': 'WELCOME MR. HARRINGTON in one row of blocks, with a violet fade', 'thinkpad': 'ThinkPad-inspired red-to-gray lettering with two red dots'}
lima_BLOCK_FONT = {'W': ('█   █', '█   █', '█ █ █', '██ ██', '█   █'), 'E': ('█████', '█    ', '████ ', '█    ', '█████'), 'L': ('█    ', '█    ', '█    ', '█    ', '█████'), 'C': (' ████', '█    ', '█    ', '█    ', ' ████'), 'O': (' ███ ', '█   █', '█   █', '█   █', ' ███ '), 'M': ('█   █', '██ ██', '█ █ █', '█   █', '█   █'), 'R': ('████ ', '█   █', '████ ', '█  █ ', '█   █'), 'H': ('█   █', '█   █', '█████', '█   █', '█   █'), 'A': (' ███ ', '█   █', '█████', '█   █', '█   █'), 'I': ('█████', '  █  ', '  █  ', '  █  ', '█████'), 'N': ('█   █', '██  █', '█ █ █', '█  ██', '█   █'), 'G': (' ████', '█    ', '█ ███', '█   █', ' ███ '), 'T': ('█████', '  █  ', '  █  ', '  █  ', '  █  '), '.': (' ', ' ', ' ', ' ', '█')}
lima_BLOCK_COLORS = ((216, 180, 254), (208, 164, 253), (192, 132, 252), (180, 110, 250), (168, 85, 247))

def lima_pack_block_lines(lines):
    quadrants = ' ▘▝▀▖▌▞▛▗▚▐▜▄▙▟█'
    packed = []
    for y in range(0, len(lines), 2):
        row = []
        for x in range(0, len(lines[0]), 2):
            mask = 0
            accent = False
            for dx, dy, bit in ((0, 0, 1), (1, 0, 2), (0, 1, 4), (1, 1, 8)):
                if y + dy < len(lines) and x + dx < len(lines[0]):
                    if lines[y + dy][x + dx] == '█':
                        mask |= bit
                    elif lines[y + dy][x + dx] == '●':
                        accent = True
            row.append('●' if accent else quadrants[mask])
        packed.append(''.join(row))
    return packed

def lima_fit_block_lines(lines, width, height):
    for candidate in (lines, lima_pack_block_lines(lines)):
        if len(candidate[0]) <= width and len(candidate) <= height:
            return candidate
    return []

def lima_block_lines(width, height):
    lines = ['    '.join(('  '.join((lima_BLOCK_FONT[letter][row] for letter in word)) for word in lima_BLOCK_MESSAGE.split())) for row in range(5)]
    fitted = lima_fit_block_lines(lines, width, height)
    if fitted:
        return fitted
    return [lima_BLOCK_MESSAGE] if len(lima_BLOCK_MESSAGE) <= width else []

def lima_thinkpad_raster():
    font = {letter: (' ' * len(glyph[0]),) * 2 + glyph for letter, glyph in lima_BLOCK_FONT.items()}
    font['I'] = ('  ●  ', '     ') + ('  █  ',) * 5
    font['.'] = (' ',) * 6 + ('●',)
    return ['    '.join(('  '.join((font[letter][row] for letter in word)) for word in lima_BLOCK_MESSAGE.split())) for row in range(7)]

def lima_resize_block_width(lines, target):
    """Stretch the letter strokes while keeping each accent a single pixel."""
    source = len(lines[0])
    resized = []
    for line in lines:
        body = line.replace('●', ' ')
        row = [body[min(source - 1, int((x + 0.5) * source / target))] for x in range(target)]
        for x, char in enumerate(line):
            if char == '●':
                position = min(target - 1, int((x + 0.5) * target / source))
                row[position] = '●'
        resized.append(''.join(row))
    return resized

def lima_thinkpad_lines(width, height, accent_shape='round', width_percent=None):
    accent = lima_ACCENT_SHAPES[accent_shape]
    lines = lima_thinkpad_raster()
    if width_percent is not None:
        full_width = len(lines[0])
        minimum = full_width if height >= 7 and width >= full_width else (full_width + 1) // 2
        target = min(width, max(minimum, round(width * width_percent / 100)))
        if height >= 7 and target >= full_width:
            lines = lima_resize_block_width(lines, target)
        elif height >= 4 and target >= (full_width + 1) // 2:
            lines = lima_pack_block_lines(lima_resize_block_width(lines, target * 2))
    fitted = lima_fit_block_lines(lines, width, height)
    if fitted:
        return [line.replace('●', accent) for line in fitted]
    if len(lima_BLOCK_MESSAGE) > width:
        return []
    if height >= 2:
        return [' ' * lima_BLOCK_MESSAGE.index('I') + accent, lima_BLOCK_MESSAGE.replace('.', accent)]
    return [lima_BLOCK_MESSAGE.replace('.', accent)]

def lima_greeting_lines(style, width, plain_terminal, height=24, accent_shape='round', width_percent=None):
    if style == 'thinkpad':
        if plain_terminal:
            return [lima_BLOCK_MESSAGE] if len(lima_BLOCK_MESSAGE) <= width else []
        return lima_thinkpad_lines(width, height, accent_shape, width_percent)
    if style == 'blocks':
        if plain_terminal:
            return [lima_BLOCK_MESSAGE] if len(lima_BLOCK_MESSAGE) <= width else []
        return lima_block_lines(width, height)
    if not plain_terminal:
        if style == 'dots' and width >= 68:
            return list(lima_BANNER)
        if style == 'typewriter' and width >= 30:
            inner = 28
            return ['┌' + '─ L I M A '.ljust(inner, '─') + '┐', '│' + ' ' * inner + '│', '│ ' + lima_MESSAGE.ljust(inner - 2) + ' │', '│' + ' ' * inner + '│', '└' + '─' * inner + '┘']
    return textwrap.wrap(lima_MESSAGE, width)

def lima_colored_lines(style, lines, brightness=1.0, palette='red-gray', column_levels=None):
    if style == 'thinkpad':
        _, left_rgb, right_rgb, accent_rgb = lima_THINKPAD_PALETTES[palette]
        width = max(map(len, lines), default=1)
        result = []
        for line in lines:
            parts = []
            for column, char in enumerate(line):
                level = brightness * (column_levels[column] if column_levels is not None else 1)
                if char == ' ' or level <= 0:
                    parts.append(' ')
                    continue
                if char in ('●', '■', '.'):
                    rgb = accent_rgb
                else:
                    progress = column / max(1, width - 1)
                    rgb = tuple((round(left + (right - left) * progress) for left, right in zip(left_rgb, right_rgb)))
                color = '\x1b[38;2;{};{};{}m'.format(*(int(c * level) for c in rgb))
                parts.append(color + char)
            result.append(''.join(parts) + lima_RESET)
        return result
    result = []
    for row, line in enumerate(lines):
        if style == 'blocks':
            shade = row * (len(lima_BLOCK_COLORS) - 1) // max(1, len(lines) - 1)
            rgb = lima_BLOCK_COLORS[shade]
            color = '\x1b[38;2;{};{};{}m'.format(*(int(c * brightness) for c in rgb))
        elif style == 'typewriter' and line.startswith(('┌', '│', '└')):
            color = lima_PURPLE if row == 2 else lima_SOFT_PURPLE
        else:
            color = lima_PURPLE
        result.append(color + line + lima_RESET)
    return result


def lima_reveal_line(line, step):
    parts = []
    for column, char in enumerate(line):
        if column >= step:
            parts.append(' ')
        elif column >= step - 2:
            parts.append(lima_WHITE + char)
        elif column >= step - 7:
            parts.append(lima_SOFT_PURPLE + char)
        else:
            parts.append(lima_PURPLE + char)
    return ''.join(parts) + lima_RESET

def lima_thinkpad_letter_stops(width):
    stops = []
    position = 0
    for word_index, word in enumerate(lima_BLOCK_MESSAGE.split()):
        if word_index:
            position += 4
        for letter_index, letter in enumerate(word):
            if letter_index:
                position += 2
            position += len(lima_BLOCK_FONT[letter][0])
            stops.append(position)
    return [min(width, (stop * width + position - 1) // position) for stop in stops]

def lima_thinkpad_animation_frames(lines, palette, animation):
    width = max(map(len, lines), default=1)
    stops = lima_thinkpad_letter_stops(width)
    for step in range(1, lima_BLOCK_FADE_FRAMES + 1):
        progress = step / lima_BLOCK_FADE_FRAMES
        brightness = 1.0
        levels = None
        if animation == 'fade':
            brightness = progress ** 1.5
        elif animation == 'wipe':
            levels = [float(column < progress * width) for column in range(width)]
        elif animation == 'scan':
            edge = progress * (width + 8)
            levels = [min(1.0, max(0.0, (edge - column) / 8)) for column in range(width)]
        elif animation == 'center':
            edge = progress * (width / 2 + 3)
            levels = [min(1.0, max(0.0, (edge - abs(column - (width - 1) / 2)) / 3)) for column in range(width)]
        elif animation == 'typewriter':
            count = int(progress * len(stops))
            edge = stops[count - 1] if count else 0
            levels = [float(column < edge) for column in range(width)]
        elif animation == 'pulse':
            if progress < 0.45:
                brightness = (progress / 0.45) ** 1.5
            elif progress < 0.7:
                brightness = 1 - 0.35 * (progress - 0.45) / 0.25
            else:
                brightness = 0.65 + 0.35 * (progress - 0.7) / 0.3
        yield (lima_colored_lines('thinkpad', lines, brightness, palette, levels), lima_BLOCK_FADE_SECONDS / lima_BLOCK_FADE_FRAMES)

def lima_animation_frames(style, lines, palette='red-gray', animation='fade'):
    if style == 'thinkpad':
        yield from lima_thinkpad_animation_frames(lines, palette, animation)
    elif style == 'dots':
        for step in range(1, max(map(len, lines)) + 8):
            yield ([lima_reveal_line(line, step) for line in lines], 0.01)
    elif style == 'typewriter':
        boxed = lines[0].startswith('┌')
        length = len(lima_MESSAGE) if boxed else sum(map(len, lines))
        for step in range(length + 1):
            cursor = '▌' if step < len(lima_MESSAGE) else ''
            if boxed:
                frame = lines.copy()
                frame[2] = '│ ' + (lima_MESSAGE[:step] + cursor).ljust(26) + ' │'
            else:
                frame = []
                remaining = step
                for line in lines:
                    count = min(len(line), max(0, remaining))
                    frame.append(line[:count].ljust(len(line)))
                    remaining -= len(line)
            yield (lima_colored_lines(style, frame), 0.035)
    else:
        for step in range(1, lima_BLOCK_FADE_FRAMES + 1):
            brightness = (step / lima_BLOCK_FADE_FRAMES) ** 1.5
            yield (lima_colored_lines(style, lines, brightness, palette), lima_BLOCK_FADE_SECONDS / lima_BLOCK_FADE_FRAMES)


# ========================================================================
# Text greetings
# ========================================================================

text_MESSAGE = 'Welcome Mr. Harrington'
text_RESET = '\x1b[0m'
text_DESIGNS = {1: ('Bookplate', 'Ivory lettering with a quiet italic welcome'), 2: ('Nameplate', 'A small rounded frame in soft silver'), 3: ('Teletype', 'One amber line, typed into place'), 4: ('Centered', 'A simple white greeting between fine rules'), 5: ('Slant', 'An ice-blue slanted headline'), 6: ('Handwritten', 'A flowing welcome with a sage-green name')}
text_IVORY = (232, 222, 205)
text_SILVER = (208, 216, 225)
text_MUTED = (104, 117, 133)
text_AMBER = (232, 188, 113)
text_ICE = (170, 209, 225)
text_SAGE = (159, 191, 167)
text_NAME_ART = (' __  __        _  _              _           _', '|  \\/  |_ _   | || |__ _ _ _ _ _(_)_ _  __ _| |_ ___ _ _', "| |\\/| | '_|  | __ / _` | '_| '_| | ' \\/ _` |  _/ _ \\ ' \\", '|_|  |_|_|(_) |_||_\\__,_|_| |_| |_|_||_\\__, |\\__\\___/_||_|', '                                       |___/')
text_SLANT_ART = (' _       __________    __________  __  _________', '| |     / / ____/ /   / ____/ __ \\/  |/  / ____/', '| | /| / / __/ / /   / /   / / / / /|_/ / __/', '| |/ |/ / /___/ /___/ /___/ /_/ / /  / / /___', '|__/|__/_____/_____/\\____/\\____/_/  /_/_____/')
text_SCRIPT_ART = (' _              _', '(_|   |   |_/  | |', '  |   |   | _  | |  __   __   _  _  _    _', '  |   |   ||/  |/  /    /  \\_/ |/ |/ |  |/', '   \\_/ \\_/ |__/|__/\\___/\\__/   |  |  |_/|__/')

@dataclass(frozen=True)
class text_Line:
    text: str
    color: tuple = text_SILVER
    attribute: str = ''

def text_place(text, width, alignment='left', indent=2):
    if alignment == 'center':
        return text.center(width)
    return ' ' * min(indent, max(0, width - len(text))) + text

def text_layout(option, width, height, unicode=True):

    def line(text, color=text_SILVER, attribute='', alignment='left'):
        return text_Line(text_place(text, width, alignment), color, attribute)
    if option == 1:
        rows = [line('Welcome', text_MUTED, '\x1b[3m'), line('')]
        if width >= max(map(len, text_NAME_ART)) + 2:
            rows += [line(text, text_IVORY) for text in text_NAME_ART]
        else:
            rows += [line('Mr. Harrington', text_IVORY, '\x1b[1m')]
    elif option == 2:
        panel = min(width, 44)
        top, bottom, side, rule = ('╭', '╰', '│', '─') if unicode else ('+', '+', '|', '-')
        top_right, bottom_right = ('╮', '╯') if unicode else ('+', '+')
        inside = panel - 2
        rows = [line(top + rule * inside + top_right, text_MUTED, alignment='center'), line(side + ' ' * inside + side, text_MUTED, alignment='center'), line(side + text_MESSAGE.center(inside) + side, text_SILVER, alignment='center'), line(side + ' ' * inside + side, text_MUTED, alignment='center'), line(bottom + rule * inside + bottom_right, text_MUTED, alignment='center')]
    elif option == 3:
        rows = [line(text_MESSAGE, text_AMBER)]
    elif option == 4:
        rule = '─' if unicode else '-'
        rows = [line(rule * 8, text_MUTED, alignment='center'), line(text_MESSAGE, text_SILVER, '\x1b[1m', alignment='center'), line(rule * 8, text_MUTED, alignment='center')]
    elif option == 5:
        if width >= max(map(len, text_SLANT_ART)) + 2:
            rows = [line(text, text_ICE) for text in text_SLANT_ART]
            rows += [line(''), line('Mr. Harrington', text_SILVER, '\x1b[3m')]
        else:
            rows = [line('Welcome', text_ICE, '\x1b[1;3m'), line('Mr. Harrington', text_SILVER)]
    elif width >= max(map(len, text_SCRIPT_ART)) + 2:
        rows = [line(text, text_IVORY) for text in text_SCRIPT_ART]
        rows += [line(''), line('Mr. Harrington', text_SAGE, '\x1b[3m')]
    else:
        rows = [line('Welcome', text_IVORY, '\x1b[3m'), line('Mr. Harrington', text_SAGE)]
    if len(rows) > height or any((len(row.text) > width for row in rows)):
        return [text_Line(text, text_SILVER) for text in textwrap.wrap(text_MESSAGE, width)][:height]
    return rows

def text_colorize(rows, brightness=1.0):
    result = []
    for row in rows:
        rgb = tuple((round(channel * brightness) for channel in row.color))
        color = '\x1b[38;2;{};{};{}m'.format(*rgb)
        result.append(color + row.attribute + row.text + text_RESET)
    return result


def text_frames(option, rows, width, unicode=True):
    if option == 3 and len(rows) == 1 and (text_MESSAGE in rows[0].text):
        indent = rows[0].text.index(text_MESSAGE)
        cursor = '▏' if unicode else '_'
        for step in range(len(text_MESSAGE) + 1):
            text = ' ' * indent + text_MESSAGE[:step]
            if step < len(text_MESSAGE) and len(text) < width:
                text += cursor
            typed = text_Line(text, text_AMBER)
            yield (text_colorize([typed]), 1.0 / (len(text_MESSAGE) + 1))
    else:
        for step in range(1, 25):
            yield (text_colorize(rows, step / 24), 0.65 / 24)


# CORDINCE system panel, adapted from Tempo logindisplay.py.
cord_DEFAULT_GAP = 4
cord_LOGO_HORIZONTAL_OFFSET = 2
cord_RESET = '\x1b[0m'
cord_BOLD = '\x1b[1m'
cord_DEFAULT_BG = '\x1b[49m'
cord_DEFAULT_RED = '\x1b[38;2;244;71;50m'
cord_DEFAULT_SOFT_RED = '\x1b[38;2;196;120;110m'
cord_GREEN = '\x1b[38;2;0;255;0m'
cord_SOFT_GREEN = '\x1b[38;2;0;170;0m'
cord_RED = cord_DEFAULT_RED
cord_SOFT_RED = cord_DEFAULT_SOFT_RED
cord_WHITE = '\x1b[38;2;245;245;245m'
cord_MUTED = '\x1b[38;2;150;150;150m'

def cord_configure_text_colors(use_green: bool) -> None:
    global cord_RED, cord_SOFT_RED
    if use_green:
        cord_RED = cord_GREEN
        cord_SOFT_RED = cord_SOFT_GREEN
    else:
        cord_RED = cord_DEFAULT_RED
        cord_SOFT_RED = cord_DEFAULT_SOFT_RED

def cord_truncate(value: str, width: int) -> str:
    if width <= 0:
        return ''
    if len(value) <= width:
        return value
    if width <= 3:
        return value[:width]
    return value[:width - 3] + '...'

def cord_read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding='utf-8', errors='ignore').strip()
    except OSError:
        return None


def cord_format_size(num_bytes: int) -> str:
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    value = float(num_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == 'B':
                return f'{int(value)} {unit}'
            return f'{value:.2f} {unit}'
        value /= 1024
    return f'{value:.2f} TiB'

def cord_format_percent(used: int, total: int) -> str:
    if total <= 0:
        return '0%'
    return f'{round(used / total * 100)}%'

def cord_format_usage(used: int, total: int) -> str:
    return f'{cord_format_size(used)} / {cord_format_size(total)} ({cord_format_percent(used, total)})'

def cord_parse_meminfo() -> dict[str, int]:
    values: dict[str, int] = {}
    raw = cord_read_text(Path('/proc/meminfo'))
    if not raw:
        return values
    for line in raw.splitlines():
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        amount = value.strip().split()[0]
        if amount.isdigit():
            values[key] = int(amount) * 1024
    return values

def cord_collect_memory_pair() -> tuple[str, str] | None:
    meminfo = cord_parse_meminfo()
    total = meminfo.get('MemTotal')
    available = meminfo.get('MemAvailable')
    if total is None or available is None:
        return None
    used = max(0, total - available)
    return ('Memory', cord_format_usage(used, total))

def cord_collect_swap_pair() -> tuple[str, str] | None:
    meminfo = cord_parse_meminfo()
    total = meminfo.get('SwapTotal')
    free = meminfo.get('SwapFree')
    if total is None or free is None or total <= 0:
        return None
    used = max(0, total - free)
    return ('Swap', cord_format_usage(used, total))

def cord_collect_disk_pair() -> tuple[str, str] | None:
    try:
        usage = shutil.disk_usage('/')
    except OSError:
        return None
    return ('Disk (/)', cord_format_usage(usage.used, usage.total))

def cord_default_route_interface() -> str | None:
    raw = cord_read_text(Path('/proc/net/route'))
    if not raw:
        return None
    for line in raw.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 11:
            continue
        if parts[1] != '00000000':
            continue
        if int(parts[3], 16) & 2:
            return parts[0]
    return None

def cord_route_networks(interface: str) -> list[ipaddress.IPv4Network]:
    raw = cord_read_text(Path('/proc/net/route'))
    if not raw:
        return []
    networks: list[ipaddress.IPv4Network] = []
    for line in raw.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 8 or parts[0] != interface or parts[1] == '00000000':
            continue
        destination = ipaddress.IPv4Address(int.from_bytes(bytes.fromhex(parts[1]), 'little'))
        netmask = ipaddress.IPv4Address(int.from_bytes(bytes.fromhex(parts[7]), 'little'))
        prefixlen = ipaddress.IPv4Network(f'0.0.0.0/{netmask}').prefixlen
        networks.append(ipaddress.IPv4Network(f'{destination}/{prefixlen}', strict=False))
    return networks

def cord_local_ipv4_addresses() -> list[ipaddress.IPv4Address]:
    raw = cord_read_text(Path('/proc/net/fib_trie'))
    if not raw:
        return []
    addresses: list[ipaddress.IPv4Address] = []
    current: ipaddress.IPv4Address | None = None
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith('|-- '):
            candidate = stripped[4:].strip()
            try:
                current = ipaddress.IPv4Address(candidate)
            except ipaddress.AddressValueError:
                current = None
            continue
        if current is not None and stripped == '/32 host LOCAL' and (not current.is_loopback):
            if current not in addresses:
                addresses.append(current)
            current = None
    return addresses

def cord_interface_ipv4_info(interface: str) -> tuple[str, int] | None:
    networks = cord_route_networks(interface)
    addresses = cord_local_ipv4_addresses()
    for network in networks:
        for address in addresses:
            if address in network:
                return (str(address), network.prefixlen)
    if len(addresses) == 1:
        return (str(addresses[0]), 32)
    return None

def cord_collect_local_ip_pair() -> tuple[str, str] | None:
    interface = cord_default_route_interface()
    if not interface:
        return None
    info = cord_interface_ipv4_info(interface)
    if info is None:
        return None
    address, prefix = info
    return (f'Local IP ({interface})', f'{address}/{prefix}')

def cord_default_info_pairs() -> list[tuple[str, str]]:
    pairs = [cord_collect_memory_pair(), cord_collect_swap_pair(), cord_collect_disk_pair(), cord_collect_local_ip_pair()]
    filtered = [pair for pair in pairs if pair is not None]
    if filtered:
        return filtered
    uname = platform.uname()
    return [('system', uname.node or 'unknown'), ('os', f'{uname.system} {uname.release}'), ('python', platform.python_version())]

def cord_render_info_lines(title: str, pairs: list[tuple[str, str]], width: int) -> list[str]:
    max_label_width = max(1, width - 11)
    label_width = min(max((len(label) for label, _ in pairs), default=0), max_label_width)
    lines = [f'{cord_BOLD}{cord_RED}{cord_truncate(title, width)}{cord_RESET}', f"{cord_RED}{'-' * min(width, max(8, len(title)))}{cord_RESET}"]
    value_width = max(8, width - label_width - 3)
    for label, value in pairs:
        rendered_label = cord_truncate(label, label_width)
        wrapped_values = textwrap.wrap(value, width=value_width, break_long_words=True, break_on_hyphens=False) or ['']
        lines.append(f'{cord_RED}{rendered_label:<{label_width}}{cord_RESET} {cord_MUTED}:{cord_RESET} {cord_WHITE}{wrapped_values[0]}{cord_RESET}')
        for continued_value in wrapped_values[1:]:
            lines.append(f"{' ' * label_width}   {cord_WHITE}{continued_value}{cord_RESET}")
    return lines

def cord_compose_frame(frame_lines: list[str], info_lines: list[str], terminal_size: os.terminal_size, logo_width: int) -> tuple[str, int]:
    block_height = max(len(frame_lines), len(info_lines))
    top_pad = 0
    left_pad = 2
    spacer = ' ' * cord_DEFAULT_GAP
    logo_prefix = ' ' * cord_LOGO_HORIZONTAL_OFFSET
    blank_logo = ' ' * (logo_width + cord_LOGO_HORIZONTAL_OFFSET)
    output_lines: list[str] = []
    for _ in range(top_pad):
        output_lines.append(cord_DEFAULT_BG + ' ' * terminal_size.columns + cord_RESET)
    for index in range(block_height):
        if index < len(frame_lines):
            logo_line = logo_prefix + frame_lines[index]
        else:
            logo_line = blank_logo
        info_line = info_lines[index] if index < len(info_lines) else ''
        output_lines.append(cord_DEFAULT_BG + ' ' * left_pad + logo_line + cord_DEFAULT_BG + spacer + info_line + cord_RESET)
    return ('\n'.join(output_lines), len(output_lines))

def cord_colorize_figlet_columns(lines: list[str], step: int, white_columns: int, fade_columns: int) -> list[str]:
    max_width = max((len(line) for line in lines), default=0)
    white_start = step - white_columns
    fade_start = white_start - fade_columns
    colored_lines: list[str] = []
    for line in lines:
        padded = line.ljust(max_width)
        parts: list[str] = []
        for column, char in enumerate(padded):
            if char == ' ':
                parts.append(' ')
                continue
            if column < fade_start:
                parts.append(f'{cord_RED}{char}{cord_RESET}')
            elif column < white_start:
                parts.append(f'{cord_SOFT_RED}{char}{cord_RESET}')
            elif column < step:
                parts.append(f'{cord_WHITE}{char}{cord_RESET}')
            else:
                parts.append(' ')
        colored_lines.append(''.join(parts))
    return colored_lines


# Exact 24-frame quarter-spin logo, pre-rendered in Tempo; no GIF decoder needed.
CORDINCE_LOGO_DATA = (
    'c-qBX$#x{Wjs2B6UiX6YaP%qeUbv)JyXsy4e+OeC00JN*RL}Opr|e8gnG6!daEE{X<Hz-%|NcK??9YGZ-{(Jk`EVb$q>mUreA)hA'
    '7mGPxGw4mu#E)b?f;-;i?>Eukz5Uq#s(;Pb51&3<)c%_F=ELU?mp;P&$G3l{y8V0qnOe{X3+^M^k7&-fhH(7P<E;U|)$YHh((k~2'
    'Q0KRAoIgT7e$yBKLASrP{Y7tuWuc2Q{A~L0WJ!<Lw!geBlso=-N$9l@w;%d&_V~tj{~g=^+~1nfH@4M(MEkLQlm1qJz4iV|$6I6h'
    'X#cpE+<m0&---EfZu?~W%A9ZAekN@n#vdObqPN=o5mWmr;r`0z{#piq0JDEMcfPgwePs<^0kZttFY|WWoZK>PUwnJuuCk8?KN!5z'
    '-AAm~POn+m9NY4gVMmfPv;B8l!)u+;_9I(!I}-4%Hhjc*AIXH5G~p$6a7m-SsqOX|`ewn8bz5*-Kdj@{(zd^_Jrj02vcHmskMa?7'
    '|IqDOhwWM8H9og~IKI%e5j{MH<m?B0_P0=AuCqUG8S)6XztDHMbiPa7AH@0065K@E7TP}4wmZl<qg%+rFUD_hx1II&4ej*}J&10Z'
    '?Dx7K;CQW@g<lUZaj3`gpKonDJ`B6fjB&d^W^~H!_I<a%YtKFC;A?dY<J-nc_$9h4-Es7_(`0kn&vUtsNZr@iZ~+P*k^TBe*Gl7$'
    'x1Z6B&giy<t}DW>ZJ~_USlvQJ-a^uixgDHsfv!M?SAN?N;Hfy_6KtO`wm=!Kz$hNR9QH-dV3G5^$OdmsbA&)}3%L6h$atN$3nRA6'
    'E})&teWAJq3g0e&6ev7?9uMw8DG=fd*5TK-9pLY)Cu%o`l2zHZtGpND^6{o^(YDLEpV`EP1P_8+s5sBD?2}PaqUoN-@iq^ke*3tA'
    'T^Md@gvD{zf|LR80A~!`b5Y4O|M6cxdT#q;SlFIry5Sp^I~<IutoVe_U%hQRbLSjVM2jGzNjdcv7*oq~xLf`V{00R69+#rJGa`K4'
    'Zt}RVA69R{?WngaxiGijxL!j7ny%nSqO=QpR3Kp>k85<-9W@BqMMXg)?Xlk_<`{87!wboC%RqB`H<z>Ex3(l~`!(>wk<PJ6drF?b'
    'k?(mnjzjqf{C9-S@X+9T!EB!_Y~TD!3O%?ost|m(Rcp6)VxOv#-MGRfPVBaAmBL-P<@Ie#e=ELf&?QaEnC%YQpZ&FFaQlq0@BEnv'
    '_RD=($%)>+_4a&irAd->X?qYVt5m)$S91Fn?@`eyE4g3yEy2S#F+DP2uW~H+@RbAIDwBTAleH&br*3KG_B0ZgtX^OB%0TU&fxa(y'
    'rE9)DhIBs$A-rwH$@X+@Ws?lE|2fCz2^Q`foX50n53<$mp!Ks$+Y;tDB&doBl}!Tn{9iaT+y!#KwZ)l!5`{Rrm3iP(riE1Xz7qS{'
    'pnZjWBvYVVwbxaG*LqJAU90-feQb`P%H4TaN`LL20=632KjcZ^91DNeTu`FC{WrM8_2e^)_ee{2(Ct(~<~eRjdjDB2fStd%!2E$+'
    't`1(V>iH%QGwyeXH|z;N69JI(_djCQ1P1PECf9LyRXb^6wBin|h?5&by)F_$`u3Zcu7;M*3eRYZiD5`&=qIZ1N)BUME9JF6<QD6&'
    '8{EAcEREVA4U=+KGtXJCZjX~P_pxi0$EMiW1>@Tu_vSHR^W@=r*taWg6%Uz@ma39<sK-@nr=QUE#>{r2!6(c^&^F-9pf2<;u3dV^'
    's(94R+)=CnXQvfhbmddeH;y-z;ah_!g<>B~$8hF$wu9Lu&z)&Te~`UxO0t;k@&O;<Zp`SNje7LA>9<~f*v@3o?UmN8wJvin)6WZ='
    '&lhlFa}E)T(t0Y_6AbVPnn@Hi`;PK#52f|Z@5@N+=LOI@zjrz9k{GU%8Y3HQ+}C}XuEvL&%Uvx!=B;HbXw3F0uk9GX&aIP{%upG%'
    '-Xwdc|H9Y*8KSvNlcavz#@jQ6rBTv8Tj|RvWTATkb3cD8r?FD}ju9pn(oDh}ch&VBquABm_h+xV$jT*JLBXCqF3|W0+V;s7>#mCC'
    'Q_WC>Kz;TKwX;hbyxWeFDh=lh98&CYt<QLZ7Spez%!Gei_lwL2b_SQ82kKVg_F!adhR5v_ht!I{5bQNDm4!h!F1SWXmK;$B1NWP('
    'P;MG95h?$Al8%;R!U|SexIOn~lkd0ZH~OCB_*Dz987bw2C4iK2;%hn%7hs%?VcIo)pPC_!<T|iFzL8-H8F++shhax@QeV2)0QfaD'
    'L?)Br)}JXue}>*?dB4xt`BW=}d$cAQ3e2(SYXuID;?S6kOwvESk%q>XgEPIrRz}>8&Og=PYC*kU{!)j{2@I%k1lfC_9$bm&4tSAe'
    'lF1_;xBVP;l9STr$)=Ng?r7?I$B${>%i0R+o*IXnJGL?BwA8($Kl}Z)Txox3eQF^@hocYe$(>4*ItSZUX$WFLxa7B#4B%CS>(-s4'
    'Z?-Hk?DLro5%&4Cy}CPO?OP8Hq~_a00O`D$?gv|nczy02|9B4{-7wzkA;pP#U&m%h8QFE!a-AgF=tX#k`!I2DZJ`T{T=Bv6>uZ1I'
    'i_F?{BS|NPevb=!6rHZ$${qALM6RC9kqrIoc{sXeI-qkNhvVZBB!?@_%NK_;V;j2VOAYV{-|<BUN5^2Axi%InB6^Q!*fA22JLvDQ'
    '7drde9xd`6EzClybcQe^Ld5n>EhGsfl;YR6XAIg7`0uqTMQ@Fn*|7h6`P2^?M{?&96ytQZ{Pk`WI!|f1@%)geoYB)m6hssdn-OMK'
    'LL6-Yy60$~##m5uxuJd6QF`{pHn#hg7)~wyd<nO3(1JN_gm@lbc49$J`UQ;SQn|Ae=Ge0BCoQnR#NzI+sOYF!#R#FD7G|!WYSQJv'
    'G8sz`KZ<ez>{D{aS_KNm2CYYXr!u65QF}RCz-nXI>;7xCZBH)rUJi;lcIfW4U&FRUCS{}b@Cp(kU<qVSQm^fVj94!9auyEQgyio+'
    '%yO_?k{uX#bPwksgf><{Sh@<+P$$e0k7=h{Xzd8yO%JEtUvlCE0cZ#}l(=!>bplL;^?YIr(JLj$Fwc|PHEec;ivupwY(ZepK=4+}'
    '$|y@Z{w==t5(MvIid9KCy1<ix-@5f0AgBa=6FuX=r*<FD(B3U=zrdIvb&;+Z!$l{GE`cQ>iCpcv4Smksy0iJlioGam&sbCD;O5o`'
    'JF@nEM*A#N&m!UIgv`KlKqnu8#c1OaMQx!Lq*Y~rP{yxGio~@Vk{bD1)!G5BiAxooI$JFkA_a_$x9)k6XCW9Gx`v&rW{8H#f1n%3'
    '<%Nj`TP?%<vBGANN>R^XOzA#CcX$zI_B~$@0|+6H*H*eCtdL%AE5U#+*LXHtRP68`f@s|?8WiFZ3<bZ2@k&n<$d-v3g#jm<o|Ydl'
    'AY83EE>FqFFz#;KLDW8laYrS_KhGd5Mi;ip&5gE^N)p_!8hfsRKZ-l}x_6nZf<fXS=8+4!t+n50UONKwE=S0)rribLA-8E!9H?=9'
    '1eheS&}<^u3Kl=y5qJq}1*{4&YqZ={jsb00q29js#`TRYD2GWY>J#iKk!@|&n;IP!qqaaChxITTYPn2lIpbKnCv{>l99uI224z6-'
    '$)ykluAwy~i5kU77RV#XvkjIOz&!gg;8F6e<N$ldF2LNy+!Qz2DryX+0V)^nCL1a6#-2_9DZPbYQ|Uf(U~q-Ejh4W+21vfg_dy<t'
    '^_nLRsfR$O+#xJu4e&hsWJfeSyXU4*MUI)|(R#9o_Q0kV*F*EL;7M$uggX(5dA_wE*apf|r82wWc*6~7FYkCet;fKD0`WtG0YpkT'
    '8!WJoNu6BMKr9tZ(^woCpPkLe+m53Hs?;5^IIpm1Niu&1bww%r3RDy%0YDR(CrtCZ;06t3KTI?FK};%{)PuI4`L*8ql44Kg0J;4u'
    'zh#jlwEz9H%*gL%+|3fe1ztH0>3i5NeCuU@)Fb?w<&_(YsWCxB7w-fYkYU>bdp};~l_$t6pYo*<?o604B~-sYV47FJ!4N9a^HVp{'
    'S!dp*<+O|m)!?lcGM#;H$6z&pmRZmFzh=v3M4CAv3lpAsgiMSybXt1}=mmI;hmB2~1<|VDY=d7nj1ftxLn>%hE=3*>{@4Pc9a9Ih'
    '2mdsoJy1bjoS9BLwzTgL^L5HIPpCv{Ur(y#a0Y9ufvJvEt2miw?vG-J?WLM1a?r_kj5KdsRH(RFCOAH^U2}5K_)<x{tBc%?LcA>u'
    'J6fBTg$f6C3Y%OUGZdLkPI>qzN1uiJs)U}4!7nxQLB83Zm_U!exgz+pdL75d=Gr4Cp8@1{77@q%ew2o`b(6jo=9@UNL{@9k1qB>T'
    '?{VVPsn1eq(*1xFz86A)*F3o<$P!aWp2TyQm?*VV=frQo0F_8I1zyw=@jG&T(et?_r1)_%X!*8-hsYs<f}0V)Q3JPr>CcUJ4ZytJ'
    'a$AO%4T7}|qaYIQa!+7=_Xr3yjV?I!BH3Hy*Fpv=0X!E(wZS7$0;9f~vMPxMsd5-l3kzhvy?<AGI~TLN1$aG@DR{u{Mng57-Hlsy'
    'QQeywyW1&)uB@_Z9lQ*M0F^9E>;zo4&oJl<H=o_7@Ds|+IVIJJ-!ZO^Yxhw&Xo=x@n5F!MeHwLblL`ha5)Zs3F`Np~3>S#BD|8<C'
    '`8gbyOjg7tz$cWnL%#*nK$}3S<Ghu{X0ZH`<8Y!JsQ>PUU3pCgg{nH5-E+oq!ln_wIR(5~rFJA;-ZR&L4#k1oS@QfhsN{Z5fRbD9'
    'wx^*j1?WfxZdrzo1c^LRlt|lu&E9EbA_@sUm#%`!&Utm40M1W3<P5_i<=eohX5}^>L-`H^lVQwmB^vVbDA}(Im+|^F>B%TrC0i>w'
    'eD6UEF(2ule1rboR1>s*=r@QrJuXFo8CWdjfsXnyaS)iyny#Bft|>|ZUEtS`3U)$ZglljWUTbDWd8p+-p|>g8J(q+5#u<2Z*n^m>'
    'NGzL{3PQlRhd}x-wWLP7_c<VGPXw$`_VURW%Xu8R+_Dr!8c>2$@-~JQy&-Q~r0(-6^J*bGM?wA)b`n|)TFeB6UojzX?<3IOvyTIi'
    'dK{lIg!E4J4RX%Y-!y?Pg5hi#dKVm0z?R4fw02kxBwa(I$`kf>ZMebh=NHJ^*BKIUmIsKM0aQ<+8ke@0u8@X!Q<mLT>?iZwu!|kC'
    'wDLLe!%_l;C74r<v~zcJwe7Yy|9eLA^95CV+brOk`YF^R6#;s&_#}(cb!>(gmRqs(wjsdK@Ib?hr5B;(e?KuIy~yL+0%bW<V5nHI'
    'Yd2e3XhRpdY2B~cG$7{qd{PMFP{oL{(yffW#5^%Ks3y5VD$o38rxQA18`Xp(VSA>VD<CKSX2Le^2e3Wl%+Z(o>h)ICiZG+77F4*^'
    '%PY^JH~Zo}p)_)*im*HpCddDN%s7n@TN%~k2XO)dn}($~8>s$5!cv?~ZTq(SWRcM9P4|KzNdY?r&JsUW$e(4O&ZFmGw?EuKXe{gc'
    '>V$Rr2biF$RB9W!f-NxBj1cn^8e~Z{>mrKV*hA!rr(mDWi!i0LL7ZxZ@*18?CK9Y6y&TLVAIv9K1_r?~G@hnP5Fg?YJL?=G#3%xT'
    'b(`3xUEyBKzd2o-qEp@jk}br?$t^&_dP?KLuSs)d@11|pH~snp+q=qrGD|p)ztnig3=)k-F~NAi&+o>dTNRfJsuxP-3Rea$_ZMek'
    '!Ny;@0%wQ^vy2|qKRNQczF~0J;K4C#Iy3?t{p!jkiG6Pb__aATf>><0d^6*oCUeI7!8Hn1*|1lL4y&|BlD;Bk@W%+-7zhknI=v$M'
    'wV+^FgjtMA))62>j%_<4UU$-Y-3|h(Bz+9TQ+Ax<q-VL?tK{try9m;4S1@@SMJqo@{d6=m+4+u5@>p#`%eKB)iMvlaq6F-5Jg<92'
    '-VTV3j^u0SViJAN{iUh{L-yqq(RPY?ndkg%bHMxXSR{T^i|<<TDT2Od!as*S<A<3@)=HVQG;1H2UJym#xH$%=XRo0M)&w?b%9LPu'
    'eooJBT|#gVeXh~7lNhds(Vi2LKsP8@6`K^v`VopaeaUi`K~nuexPO5Z)6C1v%{MHn=6qZrY%`*nPN*x~`31QHHtD-A9QAv^K^yrI'
    'sR`g&-&8ch432E5{X}4XMe88yfiyuC48n=b+EK+YlTj8Z3+InMM>1U~oC*fgIbvZEA}7Vcp~B}AmbS56K+j_)PzUs`S7b!#maiPN'
    'mUaUJtYn=s{I+6nYjMV^ESX;2<qi|T4<!C^GB+ZC_@RF8Va#gc;Cx~lAVW>?tivs)@?>s*{>)!9yvo#J0N;8NBiwQ9D%z`ntnP=5'
    'a134{jBvLbmPOD(>(%QotvTi**EVIz<2Z}+EFYdlncE>Z1eR}2%ldAG)XXJGta4f{@?oAQgAl1L)+zzkY*E4e`eg)K)3E7Ks?5qx'
    '0LJ&7uTV%~L~Dp`<qS7Q44lr#obe6wM@Yc?4zHVanPP7n3rTyF*Ii^zvcT(JAaY~xpCl_pjLK&-e?^42A&;JZ3dnxR=}~7(wFwky'
    '+XQdWw!UQ~LS#bq6pa(2n4#7LD6k@H+b$>yQC0WAks3S#HFAh-x{g?SwneOdFoh0pLwWQSEYH=X+TNFZ*3Q>F%SX(xHD;Gtlais>'
    'rDMzvXRIb`irIICy)C)>f~J)jrPR0u9tWl@sIxGJ!P90FbfUn@19m~r<t<ek@x3+iA~(|p!X!4Qs^hS8_Xkw%>?q$2LE1A%dNqTJ'
    'c!$XjoEtV%<$hk(qa$pY_=4uWSC5kWA4W|+r+H&9O25K-FRQ9zjMZY`N6zE$ET}$HhBXOwZ;0R6rF5_l2c_0~`|!hHAuTu{68B++'
    '70NY+MEh_;AoPbjEi1>PncPZuoagH5dtmy8)Q!_wsT9NB(`CuILgjT6_GFgXlS`aTF+Fi2pZYX<X7vp;$~VRzOZMRolVH%zIhglS'
    '8*EWpS5x?z)jdc`LO9>p%XZa19P8yu_Th+}S<?#=sGr%c3-;kV4?0O^?nU(tV`<&kUEay2^vkU79kdDcA(C<t5n*q|BxR{k(iB)S'
    'qrft3^xlbkV-{{ij`hA^mJ!iYRAg`U43=MD@giq&l1$q6J7`1jYoxjiQQ@msw_vUFH=BjGMd*5UFWKJhmjsFT6j$griZUv_e(~rJ'
    'MLk=GNd}yEBi-gKQ$^BH{k`xA$DrdVDk}r@k9lVn9u2(etwJ|?Y!;3!Cf$l!iohAS%KVI&5%LmxN@Ws_5MPnmXXXk^^II_wec%*+'
    '8J6-I)O7`rY8RZsiNG8h9Zw<#a(Io)zOf`vR^4b5CpVJ8=}Quq+#vsPS2$w_-YY!=gqzTTA^yJWTypFutUHA#nRuk_**aq5i{zyo'
    'mK~ax_{3GPJHVFFX~A<^<dP%z>OWv2j*!D{z{3I5-ja!U1JXL)FM0~E?&jlP+~|}498oh<GBRJ}`zGRX;Lr8eJ!cRv14`#sW}1gR'
    ';~iesy~D**l+?3{G)RKn$shCPIguQ(a0xHcVBKM)dqMDaE+g4~3=)mA;gA))!!KoWRt58G$eW=buTcnL4^AwJ)(|&7Cz89vF=#!n'
    'ftEPIa4D@mhrUt<wQ}V*DVxx)*@wG@ltx@5KNsl~=4@FJT=@o_94T^;g2yG8T&F*8B90msl;dllPoPtLEd{DMZ~H`Ha+dSvP$dW?'
    'gV}&kbU5Gz)nv4CWSl1^;_JXE3xHEm{DedFcF><SF|Mz{unmo`VWQoIGRWlajfpt%x<wePFYODd#Pf{Fo-%{`viB`4gIhS=l8x{K'
    '$M^(K&8JKnf~Eknt%Sh3DuRC&a*4DY$Vg0VkYjY_9A$K|M&wy7X0c_#M4XC*7X@sFRV8zg@sOJN_Y)qv=0;9|%fxy?0WM$QRkf=v'
    'Rv>1<Q~b1UGwdb{veBeLsv>^a7!b--p~Jmdw`)u+Rg3kX7E;b_KF`WOJfNjlnEQRov~-A0mPK<ZqQpg|XQRcx!88aafp{0cp`}-('
    'q*YlR4v!{Doa<#xD%adA*1ie%tKh?)3IO4o)jr8i)6ty5R^nxazGFG1JF(Lb>m`yzDJ3|Wk$8EKGRsBxnZ`H(Gzu){KVv1nml{!-'
    '85D^rrm)ByG-aahqO!cN>Po7(nUbBZx=$m&s7I#Z2HDb)?BN&3I=5^+^mD~Pw5arRME>}xXj)#E`ZuVbY4E`ArO{8dU|gV|b4JJE'
    'F)5RxfRX1_RNc?flS!H_59amEcrMs?IxEK2Nin?UHT85Vv_mGR7m989A+*@u@8bs#;bNm+4?!lN?zf*nTpjJo*_jjTgU;yyImLI~'
    'X=+0{A9Bd66vp{w(aeoV$G1Wwa^AR-N}^WS>;ARe0d93l9=H|?EEkweOSE(Bn1B(B-<H1E`+MDE@N-Z<iy%uvCT^e4BQBli1=$r`'
    '4SQd2T)~yjAa3%~*P_C2K|#k4(z|w+_3(Xj&luf4W1F{C{w*lSxJBidzsnUIn@bj@hx*19+;P`b=6p51&Jf3n#9ndsbgU=uci7`t'
    'Lh$F(I0a)P+_I7Cgvp3htHZECJA3^0fMu!3heH=z>b(hKggJi+oU!^n1Bd{?oBv{gbBjnh!R}i&3D$MQRxOHYV@B~krjFo>Joj`o'
    'jQyGgluYXw-c~3RDRI?FO-ILML=8|K!6WuwlEDVI(e@+CIWqMA`GUidcuR3^8VX&ZG!qdx1az?BmDqX`Bm$%ErL-HcbNiP%U$T--'
    '!03mny3iL{MMDx$ryk)%eId($mgbiS#J-U+${OXIMH?YeXqJQ~;CAbBP$RD3ml+|Lh4hT$jVm~51XtOY5szVr(5`BhfV?P(w*GkU'
    '$*$lQOEw`J<Rtnku$9W3xe$(((XlU@9ZYl_CY0}e>++7tD`tUC;V?MGFx<m}#mcgaf8H>B>rFEe{+(gCUoi|1u(~7z%z{<k6PF+{'
    '#yEaT4>t?+aBSoGj2@1CL@~?3p+OKf(EY`6kFu%|&6-5uHkTU!;!xoXNyAtrmn3eldEG;{e8VRTS-w?86hJ^c?DxLo`I-BzSMI~R'
    'ZWRs-+=*4V1G64#6;31=k!Xz>^uD{$1hGtW3zXoQRXBEQ7W2ut5Y~C)Xx@>!%KpJrUJv!F9Xo4bYxFd9Ld;!wq&Y~l`yb$7s~I49'
    '@HZ&AoO~Sk)~uTfC|{D0qA|83th=>O$>ppKygFZUq9MIVF83?3gY?!E+ZRmFxszCF9U}(zg&Dd0<T<B@mf*>*Fldn(T2wq9`L0*R'
    '@W)m&cG8Ufeny%Vr*JIjda09h{PQMZ-&Ha2jWoJvK<)WcU6qad*TfZAVvP8*ZZ-gW00~+>MOi(jG8$cvSUZTsF3K`_xVOK>KPRZ%'
    'qVUg2g@p35{Ky&bTUO!7`}Unxcq2nbVPIY=_u4v#{PeD5Nscb*R^j9txM`K<uNgSCYsW@aEr+Gj9^*A{-Y~|oF{xj0Hhm*lc^Q~='
    '>ZK@CO2j&G&F@u%nJgPC;zr-zt}2o@xJ9Tl>>)BGL;D49aBR2xz#BZs-r(oSuj^*ub-@_payOP9l)<G$8c-Xr%)q0<3`cIyNpXpm'
    '%)rfH1}+M7S4=uha7G-}mXcW@N1)=De3e=`@A_5i@5?#d>%9;Im1izBVlf+sU(bqMLXK)L3<q^zb|J`M!}q8d#XCi9z$t12kx~JG'
    'l<F=5c>^A(E``MctqLrTCihmvhTZb}y|>3aB@q@^IUBYI%<<$z$7u|B6^+3oVvh4JOSf_~RE)aV`rK177GdO7c_R#qNLjWUw+5+T'
    'V7AV8jKR;gab%%4iL?EBm~^(?6NOsojAChK3@+1U*a^Ae@*MkfK_ElAqN9Vp3h}*Zcq+1!+R=XymV4PW9C28mn}%bPNhh~>M!U-O'
    'tnlhf7?2%}(tAor<;q>B8Wx@xHJY1-qn<x)iaW(L+;hD_%`sI(iyN%oSUGO(D}r9`S}0h8;%h+AfkGKe1t(RLq$)Pz70ZRnLyOB~'
    '{iah!Fu;)tWh|AtLj7h8hVN@sWczV_wNM31GZem9V{uNAHmknOiQ~PA_)5cRk9GYEJJV|R2Bfy4f1`m{N&5Csw<2>Ck`7x6e}bvd'
    '1&dM1;0_s_u9LyB1G(xXUZ6WAiEElqI%WHXZ@@dSzx&sMQ#^GN&s-UjS4`{8Z`Nj|i&;p9Q^To2+J(B>LR5I-X@8B^9SM5+@suZy'
    'Jr=%(OEzuW1CYNvLgUvk<p(ZHEhX!3jW1mZZh8Pm=Ank;2LXh|?tbGM!u1s*a?-^*Zh_3H3(Q5Vq9|M~w7Y4%3h>f-=Rcmgi}Q{D'
    'ID7eEwS%c0d0eq0FYvyQ`Qt!8;yr&HV|4$F9r+K|r<J`qEYPl_SwHg9^iSL%N1g!?xQQ&{eZ&w91*5H;CpVAAka_quF3`Y4jBaFF'
    '$%11f!NsFM8WnfyYxK`jcD5!N$RCLx@Yf6P@eC*EH(OMadV#%4nGwDJRwGfsEdx*V^#MF_ml5mmzppn&DfwW&sOv@`1NdRP1=n)k'
    'C<W=65YpAGIqO+jdd|2yEjV9GsVw%;PHT$eMX@3$^W!3NnluOTCk$}a(wth6lSWvU(VZ1pkPwiNUlXCyC5BJ-J&O>+bqr5VXBDo9'
    'KEcG99FU6evgspV7X54nqATdmyrF>S$g!VwFDp%7ml|>@s=XMvnpp>H3>ot8Ip4VE!6!!Ne516EwIZ)8tkk4%nnsnI02BryhjG&h'
    '-~1dpOS)JHuF1*|S_y+z7T8O8>LBEQIg5?mrt#m-s;+eJQDqwbUe1zY$tk2mYNJ`Bb6e;LwZhk2uoah0Pe(ep*o`zCmAyPR8%M?X'
    'lG!**Lc9(b_nKyQOH)UO5s+23SH48n{uo&a_vCOi`Bc{hq3a?yM)J^hnsgY~X$shJxke2hc^Nt{IFe&u=%m8#Sxf5tTQRpziYfNk'
    'MB}88G^xD=<$dmbAE0nD``QID`~BDy9=ep1M}RF>1ZpTUq!eGX4E=M#sGT!-cZxB*liTKY<~)9x)vxftQ9p!~;zI!i<hBUEQz)Re'
    'T(Dh(&yC2{gRJ^X;XA`~g;9lB8~Gw{)F^O)QlM=tsnsb!0GYUb4&ncq5&4~Np@{$W+=#q^jCxD+!BewQp<Fvwd4v2}!Ny#;wN)=('
    'FU}(v4G2aw+6zj_Nbs7zW;liAe~StEHBehnF*2BVjO-t3Sex}GT~8a?btVzA07_7^a_~Imv33>-BUL8JK`qOG3D&8q7EJ`qJ1XQf'
    'I=xn&q;oGIH<%g6<lwD4?m7!HB-qqYaC>}$9JesjBYW;^M$YWkSAVhcm$R`wc)tHymxOUa_ClU$_C>{PJix)+Y*^SPRvl(8aCZ=&'
    'O|&0pdvTntb&?s_z@!-iXg!4#f)N$wm{QziRQj?`)@9|~!=LtA?UKGqA9I19QSHZZ$&-fp7o?3tdfOB*%#SdQcDFg%s9q%CgoQHf'
    'O4``~5mdR&D$8x2Mn3g#vLClgQqdUv6lZ|85&VQ8yEm9Hz)I$g{dmPIuGx<#N(UG1$4x{)p;@=F`@Y=R`#D-b@QE~oM-G^zKe8W3'
    '9-I^VaX)Q=b;z*H`IfvJ_Pnl7!`*Q93)6>GixdO=vq_uNN9?W>V7~R|?Z;*5ChQ0K!hRh4NoLO9vH}H~B;a?onLYI$H`IHaL8%*!'
    'WR+w^AwSrK8qIk08Mz!gpAy!chc+(PXw9?U7bL|roLMKU0i>{OR4>^l4z-z9ETZo%y=<1<bg!=bxdOFtL=sK$v_u&TK%S}E5M=$G'
    'd4^3^Y{(s2&I=$fvB^c*XurS#o~aWd6KOFaMJCis6Dc$E$(Gd4a3e=2lLuM2cj8x$1S+H*WJE7&h0KM$QSx)wbZ$VZ4^*72E=^m}'
    'no)dyB2Ms(Qr`V@wC;{5W`vo0HH$oen*i8Z$D)+rRTTjS`P82Lv~09*?a2v?H4dPEK~!=7bZ_j*CAVMHkf$LW_tg!wOrU<`9s|;Y'
    'eBqNE8<V`_04@w2x5)z~I#Q!K(SrEc-J9ZqT+C}exQC=Pi6!MY^%}-2bWY?^@L>5xW+gQOQ4AGr9}gv*^wyI6a8}m^@v!HvYDxY-'
    '{}1>0sG|'
)

CORDINCE_LOGO_FRAMES = tuple(tuple(frame.splitlines()) for frame in json.loads(zlib.decompress(base64.b85decode(CORDINCE_LOGO_DATA))))

CORDINCE_CONSOLE_BANNER = ('#     # ####### #        #####  ####### #     # #######    #     # ######      ', '#  #  # #       #       #     # #     # ##   ## #          ##   ## #     #     ', '#  #  # #       #       #       #     # # # # # #          # # # # #     #     ', '#  #  # #####   #       #       #     # #  #  # #####      #  #  # ######      ', '#  #  # #       #       #       #     # #     # #          #     # #   #   ### ', '#  #  # #       #       #     # #     # #     # #          #     # #    #  ### ', ' ## ##  ####### #######  #####  ####### #     # #######    #     # #     # ### ', '                                                                               ', '#     #    #    ######  ######  ### #     #  #####  ####### ####### #     # ', '#     #   # #   #     # #     #  #  ##    # #     #    #    #     # ##    # ', '#     #  #   #  #     # #     #  #  # #   # #          #    #     # # #   # ', '####### #     # ######  ######   #  #  #  # #  ####    #    #     # #  #  # ', '#     # ####### #   #   #   #    #  #   # # #     #    #    #     # #   # # ', '#     # #     # #    #  #    #   #  #    ## #     #    #    #     # #    ## ', '#     # #     # #     # #     # ### #     #  #####     #    ####### #     # ', '                                                                            ')

# Exact historical hook retained for migration of existing installations.

# ========================================================================
# Unified catalog and playback
# ========================================================================

VERSION = '1.0'
RESET = '\x1b[0m'
MESSAGE = 'Welcome Mr. Harrington'


@dataclass(frozen=True)
class Design:
    name: str
    title: str
    description: str
    backend: str
    value: object
    duration: float
    sources: tuple = ()


DESIGNS = {}
for name, (title, description) in cin_THEMES.items():
    DESIGNS[name] = Design(name, title, description, 'cinema', name, 1.8,
                           tuple(cin_REFERENCES[name]))
for name, style in (('lima-purple', 'blocks'), ('lima-dots', 'dots'), ('lima-typewriter', 'typewriter')):
    DESIGNS[name] = Design(name, 'LIMA / ' + style, lima_STYLES[style], 'lima',
                           (style, 'red-gray', 'round', None, 'fade'), 1.0)
for number, variant in enumerate(lima_ALL_THINKPAD_VARIANTS, 1):
    palette, shape, fill, animation = variant
    name = f'thinkpad-{number:02d}'
    title = f'THINKPAD {number:02d} / {lima_THINKPAD_PALETTES[palette][0]}'
    description = f'{shape} accents; {fill or "natural"} width; {animation}'
    DESIGNS[name] = Design(name, title, description, 'lima', ('thinkpad', *variant), 1.0)
for number, (title, description) in text_DESIGNS.items():
    name = title.lower()
    DESIGNS[name] = Design(name, 'TEXT / ' + title, description, 'text', number,
                           1.0 if number == 3 else .65)
for name, green in (('cordince-green', True), ('cordince-red', False)):
    DESIGNS[name] = Design(name, 'CORDINCE / ' + ('green' if green else 'red'),
                           'Original quarter-spin logo, live system panel and dotted welcome',
                           'cordince', green, 2.1)
DESIGNS['cordince-console'] = Design('cordince-console', 'CORDINCE / console banner',
                                    'The original green ASCII welcome for Linux consoles',
                                    'console', None, 1.0)

GROUPS = {key: value for key, value in cin_COLLECTIONS.items() if key != 'all'}
GROUPS['cinematic'] = tuple(cin_THEMES)
GROUPS['lima'] = ('lima-purple', 'lima-dots', 'lima-typewriter')
GROUPS['thinkpad'] = tuple(key for key in DESIGNS if key.startswith('thinkpad-'))
GROUPS['text'] = tuple(key for key in DESIGNS if DESIGNS[key].backend == 'text')
GROUPS['cordince'] = ('cordince-green', 'cordince-red', 'cordince-console')
GROUPS['all'] = tuple(DESIGNS)
ALIASES = {'purple': 'lima-purple', 'blocks': 'lima-purple', 'lima': 'lima-purple',
           'dots': 'lima-dots', 'typewriter': 'lima-typewriter',
           'thinkpad': 'thinkpad-01', 'cordince': 'cordince-green'}


def normalize_selection(value):
    value = value.strip().lower()
    if value.startswith('random '):
        value = 'random:' + value[7:].strip()
    value = ALIASES.get(value, value)
    if value in DESIGNS or value in ('random', 'off'):
        return value
    if value.startswith('random:') and value[7:] in GROUPS:
        return 'random' if value[7:] == 'all' else value
    raise ValueError(f'unknown selection {value!r}; use --list or --groups')


def validate_duration(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError('duration must be a positive finite number')
    return float(value)


def choose(selection):
    if selection == 'off':
        return None
    if selection == 'random' or selection.startswith('random:'):
        group = selection.partition(':')[2] or 'all'
        return DESIGNS[random.choice(GROUPS[group])]
    return DESIGNS[selection]


def plain_lines(width, height):
    return textwrap.wrap(MESSAGE, width)[:height]


def prepare(design, width, height, console=False):
    """Return the finished rows, a fresh frame iterator, and native duration."""
    if design.backend == 'cinema':
        w, h = min(width, 120), min(height, 16)
        h = cin_frame_height(design.name, h)
        final = cin_scene(design.name, w, h).render()

        def frames():
            count = math.ceil(design.duration * 24)
            for index in range(count):
                yield cin_scene(design.name, w, h, index / (count - 1)).render(), design.duration / count
        return final, frames, design.duration
    if design.backend == 'lima':
        style, palette, shape, fill, animation = design.value
        lines = lima_greeting_lines(style, width, False, height, shape, fill)
        if not lines or len(lines) > height or any(len(line) > width for line in lines):
            lines = plain_lines(width, height)
        final = lima_colored_lines(style, lines, palette=palette)
        sequence = list(lima_animation_frames(style, lines, palette, animation))
        return final, lambda: iter(sequence), sum(delay for _, delay in sequence)
    if design.backend == 'text':
        rows = text_layout(design.value, width, height)
        final = text_colorize(rows)
        sequence = list(text_frames(design.value, rows, width))
        return final, lambda: iter(sequence), sum(delay for _, delay in sequence)
    if design.backend == 'console':
        rows = list(CORDINCE_CONSOLE_BANNER)
        if len(rows) > height or any(len(row) > width for row in rows):
            rows = plain_lines(width, height)
        final = ['\x1b[32m' + row + RESET for row in rows]
        sequence = [(final, 1.0)]
        return final, lambda: iter(sequence), 1.0

    cord_configure_text_colors(design.value)
    terminal = os.terminal_size((width, height))
    text_width = max(10, width - 20 - 4 - 6)
    info = cord_render_info_lines(socket.gethostname(), cord_default_info_pairs(), text_width)
    message = list(CORDINCE_CONSOLE_BANNER) if console else list(lima_BANNER)
    if any(len(row) > width for row in message):
        message = plain_lines(width, height)
    logo_height = max(len(CORDINCE_LOGO_FRAMES[0]), len(info))
    if width < 50 or logo_height + len(message) + 1 > height:
        if len(message) > height:
            message = plain_lines(width, height)
        final = [cord_RED + row + RESET for row in message]
        sequence = [(final, design.duration)]
        return final, lambda: iter(sequence), design.duration

    def panel(index):
        rendered, _ = cord_compose_frame(CORDINCE_LOGO_FRAMES[index], info, terminal, 20)
        return rendered.split('\n')

    final = panel(0) + [''] + [cord_RED + row + RESET for row in message]
    sequence = []
    # Preserve the original logo speed and then the white-led lettering sweep.
    for index in range(25):
        sequence.append((panel(index % 24) + [''] * (len(message) + 1), .05))
    for step in range(1, max(map(len, message)) + 8):
        sequence.append((panel(0) + [''] + cord_colorize_figlet_columns(message, step, 2, 5), .01))
    return final, lambda: iter(sequence), sum(delay for _, delay in sequence)


def write_rows(rows, color=True):
    for row in rows:
        if color:
            sys.stdout.write('\r' + RESET + '\x1b[2K' + row + RESET + '\r\n')
        else:
            sys.stdout.write(row + '\n')
    sys.stdout.flush()


def play(design, once=False, duration=None):
    terminal = shutil.get_terminal_size((80, 24))
    width = max(1, terminal.columns - 1)
    height = max(1, terminal.lines - 4)
    term = os.environ.get('TERM', 'dumb')
    try:
        '⣿'.encode(sys.stdout.encoding or 'utf-8')
    except UnicodeEncodeError:
        unicode_ok = False
    else:
        unicode_ok = True
    if term == 'dumb' or (term == 'linux' and design.backend not in ('cordince', 'console')) or not unicode_ok:
        write_rows([''] + plain_lines(width, height) + [''], False)
        return
    final, frames, native_duration = prepare(design, width, height, term == 'linux')
    write_rows([''])
    if once or not sys.stdout.isatty():
        write_rows(final)
    else:
        scale = duration / native_duration if duration else 1.0
        started = time.monotonic()
        elapsed = 0.0
        try:
            sys.stdout.write('\x1b[?25l')
            for index, (rows, delay) in enumerate(frames()):
                if index:
                    sys.stdout.write(f'\x1b[{len(final)}F')
                write_rows(rows)
                elapsed += delay * scale
                time.sleep(max(0.0, started + elapsed - time.monotonic()))
            sys.stdout.write(f'\x1b[{len(final)}F')
            write_rows(final)
        finally:
            sys.stdout.write(RESET + '\x1b[?25h')
            sys.stdout.flush()
    write_rows([''])


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Examples:\n  %(prog)s lima-purple\n  %(prog)s random\n'
               '  %(prog)s random:arrival\n  %(prog)s --random krypton\n'
               '  %(prog)s --group compact --gallery\n  %(prog)s --list')
    parser.add_argument('selection', nargs='?', help='Design name, random, random:GROUP or off (default: cordince-green).')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--theme', metavar='NAME', help='Show one design.')
    mode.add_argument('--random', nargs='?', const='all', choices=GROUPS, metavar='GROUP', help='Show a random design, optionally within GROUP.')
    mode.add_argument('--list', action='store_true', help='List design names and descriptions.')
    mode.add_argument('--groups', action='store_true', help='List named groups and their sizes.')
    mode.add_argument('--gallery', action='store_true', help='Print scrollable static previews.')
    mode.add_argument('--demo', action='store_true', help='Animate the selected group.')
    parser.add_argument('--group', '--collection', choices=GROUPS, default='all', help='Group for --list, --gallery, --demo or --random.')
    parser.add_argument('--once', action='store_true', help='Skip animation.')
    parser.add_argument('--duration', type=float, help='Override animation seconds.')
    parser.add_argument('--sources', action='store_true', help='Print research links for the selected design or group.')
    parser.add_argument('--login', action='store_true', help='Shell startup: silent unless attached to an interactive terminal.')
    parser.add_argument('--version', action='version', version='%(prog)s ' + VERSION)
    args = parser.parse_args()
    if args.login and (not sys.stdout.isatty() or os.environ.get('TERM', 'dumb') == 'dumb'):
        return 0
    try:
        if args.duration is not None:
            validate_duration(args.duration)
        browsing = any((args.list, args.groups, args.gallery, args.demo))
        if args.selection is not None and (args.theme is not None or args.random is not None or browsing):
            raise ValueError('use either a positional selection or one selection option')
        explicit = args.theme if args.theme is not None else args.selection
        if args.random:
            group = args.group if args.random == 'all' else args.random
            explicit = 'random' if group == 'all' else 'random:' + group
        if explicit == 'random' and args.group != 'all':
            explicit = 'random:' + args.group
        selected = normalize_selection(explicit) if explicit is not None else None
        if args.groups:
            for group, members in GROUPS.items():
                print(f'{group:12} {len(members):2d} designs')
            return 0
        members = GROUPS[args.group]
        if selected in DESIGNS:
            members = (selected,)
        elif selected == 'off':
            members = ()
        elif selected and selected.startswith('random:'):
            members = GROUPS[selected[7:]]
        if args.sources:
            for name in members:
                design = DESIGNS[name]
                print(f'{name}: {design.title}')
                for source in design.sources:
                    print(f'  {source}')
            return 0
        if args.list:
            for name in members:
                design = DESIGNS[name]
                print(f'{name:24} {design.title}\n  {design.description}')
            return 0
        if args.gallery or args.demo:
            width = max(1, shutil.get_terminal_size((80, 24)).columns - 1)
            for name in members:
                print('\n'.join(textwrap.wrap(name + ': ' + DESIGNS[name].title, width)), flush=True)
                play(DESIGNS[name], args.once or not args.demo, args.duration)
            return 0
        design = choose(selected or 'cordince-green')
        if design:
            play(design, args.once, args.duration)
        return 0
    except (OSError, ValueError) as exc:
        if args.login:
            print(f'login-greeting: {exc}', file=sys.stderr)
            return 0
        parser.error(str(exc))


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        # A pager that has closed early should not print a traceback on login.
        try:
            sys.stdout = open(os.devnull, 'w')
        except OSError:
            pass

