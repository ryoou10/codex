#!/usr/bin/env python3
"""Generate a deliberately clumsy painterly PNG artwork using only stdlib."""
from __future__ import annotations

import math
import random
import struct
import zlib
from pathlib import Path

W = H = 900
random.seed(20260531)

pixels = [[ [248, 232, 194] for _ in range(W) ] for _ in range(H)]


def clamp(v: float) -> int:
    return max(0, min(255, int(round(v))))


def blend(x: int, y: int, color: tuple[int, int, int], alpha: float = 1.0) -> None:
    if not (0 <= x < W and 0 <= y < H):
        return
    dst = pixels[y][x]
    a = max(0.0, min(1.0, alpha))
    for i in range(3):
        dst[i] = clamp(dst[i] * (1 - a) + color[i] * a)


def ellipse(cx: float, cy: float, rx: float, ry: float, color: tuple[int, int, int], alpha: float = 1.0) -> None:
    x0, x1 = int(cx - rx - 2), int(cx + rx + 2)
    y0, y1 = int(cy - ry - 2), int(cy + ry + 2)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = (x + 0.5 - cx) / rx
            dy = (y + 0.5 - cy) / ry
            d = dx * dx + dy * dy
            if d <= 1.0:
                edge = min(1.0, (1.0 - d) * 8.0)
                blend(x, y, color, alpha * edge)


def line(x1: float, y1: float, x2: float, y2: float, width: float, color: tuple[int, int, int], alpha: float = 1.0) -> None:
    minx = int(min(x1, x2) - width - 2)
    maxx = int(max(x1, x2) + width + 2)
    miny = int(min(y1, y2) - width - 2)
    maxy = int(max(y1, y2) + width + 2)
    vx, vy = x2 - x1, y2 - y1
    length2 = vx * vx + vy * vy or 1.0
    radius = width / 2.0
    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            t = ((x - x1) * vx + (y - y1) * vy) / length2
            t = max(0.0, min(1.0, t))
            px, py = x1 + t * vx, y1 + t * vy
            d = math.hypot(x - px, y - py)
            if d <= radius + 1.0:
                blend(x, y, color, alpha * max(0.0, min(1.0, radius + 1.0 - d)))


def polygon(points: list[tuple[float, float]], color: tuple[int, int, int], alpha: float = 1.0) -> None:
    ys = [p[1] for p in points]
    miny, maxy = int(min(ys)), int(max(ys))
    n = len(points)
    for y in range(miny, maxy + 1):
        intersections = []
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            if (y1 <= y < y2) or (y2 <= y < y1):
                x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                intersections.append(x)
        intersections.sort()
        for a, b in zip(intersections[0::2], intersections[1::2]):
            for x in range(int(a), int(b) + 1):
                blend(x, y, color, alpha)


def scribble_ellipse(cx: float, cy: float, rx: float, ry: float, color: tuple[int, int, int], repeats: int, alpha: float) -> None:
    for _ in range(repeats):
        ellipse(
            cx + random.uniform(-rx * 0.06, rx * 0.06),
            cy + random.uniform(-ry * 0.06, ry * 0.06),
            rx * random.uniform(0.92, 1.06),
            ry * random.uniform(0.92, 1.08),
            tuple(clamp(c + random.uniform(-18, 18)) for c in color),
            alpha,
        )


def outline_ellipse(cx: float, cy: float, rx: float, ry: float, color: tuple[int, int, int], loops: int = 3) -> None:
    for _ in range(loops):
        last = None
        for i in range(121):
            t = i / 120 * math.tau
            wobble = 1 + random.uniform(-0.025, 0.025)
            x = cx + math.cos(t) * rx * wobble + random.uniform(-1.8, 1.8)
            y = cy + math.sin(t) * ry * wobble + random.uniform(-1.8, 1.8)
            if last is not None:
                line(last[0], last[1], x, y, random.uniform(2.0, 4.5), color, 0.75)
            last = (x, y)


# canvas texture and crooked background
for _ in range(10000):
    x = random.randrange(W)
    y = random.randrange(H)
    tint = random.choice([(255, 246, 216), (230, 206, 170), (247, 224, 184), (220, 190, 155)])
    blend(x, y, tint, random.uniform(0.12, 0.28))

for _ in range(36):
    line(random.randrange(-100, W), random.randrange(H), random.randrange(W + 100), random.randrange(H), random.uniform(2, 9), random.choice([(239, 198, 148), (252, 232, 174), (224, 174, 139)]), 0.09)

# wonky red cape and body
polygon([(196, 689), (704, 660), (773, 862), (147, 842)], (184, 42, 38), 0.84)
for _ in range(20):
    line(random.randrange(160, 760), random.randrange(670, 855), random.randrange(130, 790), random.randrange(660, 865), random.uniform(4, 12), random.choice([(144, 28, 33), (213, 67, 44), (126, 30, 52)]), 0.18)

scribble_ellipse(454, 610, 132, 102, (216, 83, 43), 6, 0.28)
outline_ellipse(454, 610, 132, 102, (98, 61, 42), 3)
line(380, 530, 350, 705, 26, (240, 183, 77), 0.65)
line(530, 525, 572, 704, 24, (240, 183, 77), 0.65)

# face
scribble_ellipse(450, 351, 248, 236, (230, 173, 99), 7, 0.28)
scribble_ellipse(450, 351, 230, 220, (244, 188, 111), 3, 0.26)
outline_ellipse(450, 351, 248, 236, (91, 62, 43), 4)

# cheeks and nose
scribble_ellipse(283, 382, 65, 72, (211, 50, 47), 8, 0.28)
scribble_ellipse(613, 379, 68, 73, (206, 48, 47), 8, 0.28)
scribble_ellipse(449, 392, 76, 70, (233, 103, 42), 8, 0.28)
outline_ellipse(283, 382, 65, 72, (103, 50, 39), 2)
outline_ellipse(613, 379, 68, 73, (103, 50, 39), 2)
outline_ellipse(449, 392, 76, 70, (103, 50, 39), 2)

# eyes and eyebrows
scribble_ellipse(358, 287, 29, 44, (44, 35, 34), 5, 0.45)
scribble_ellipse(546, 286, 29, 44, (44, 35, 34), 5, 0.45)
line(320, 232, 391, 241, 10, (64, 41, 36), 0.72)
line(512, 243, 587, 229, 10, (64, 41, 36), 0.72)
ellipse(367, 270, 6, 9, (247, 245, 232), 0.82)
ellipse(555, 269, 6, 9, (247, 245, 232), 0.82)

# embarrassed mouth
for shift in [-3, 2, 6]:
    last = None
    for i in range(55):
        t = math.pi * (i / 54)
        x = 386 + 116 * (i / 54) + random.uniform(-2, 2)
        y = 505 + math.sin(t) * 23 + shift + random.uniform(-2, 2)
        if last:
            line(last[0], last[1], x, y, 5.5, (89, 40, 37), 0.58)
        last = (x, y)

# nostril and nose hair trimmer
ellipse(484, 402, 9, 6, (62, 38, 33), 0.76)
ellipse(492, 397, 4, 3, (230, 103, 42), 0.5)
# buzzing hairs
for angle in [-0.9, -0.45, 0.1, 0.6]:
    x2 = 494 + math.cos(angle) * random.uniform(18, 30)
    y2 = 402 + math.sin(angle) * random.uniform(12, 24)
    line(487, 402, x2, y2, 2.2, (39, 31, 29), 0.68)

# arm holding cutter
line(615, 535, 686, 451, 34, (238, 181, 100), 0.75)
ellipse(698, 433, 34, 31, (241, 188, 110), 0.78)
line(657, 431, 525, 405, 22, (185, 194, 190), 0.92)
line(547, 411, 496, 402, 18, (119, 128, 128), 0.92)
ellipse(489, 401, 13, 10, (73, 83, 85), 0.88)
for dy in [-15, 0, 15]:
    line(665, 425 + dy, 715, 438 + dy, 3, (79, 84, 83), 0.52)
for _ in range(16):
    line(493 + random.uniform(-8, 8), 401 + random.uniform(-7, 7), 518 + random.uniform(4, 18), 405 + random.uniform(-8, 9), 2.0, (240, 238, 202), 0.45)

# shaky motion marks
for r in [40, 57, 74]:
    last = None
    for i in range(12, 43):
        t = -0.74 + i / 60
        x = 504 + math.cos(t) * r
        y = 397 + math.sin(t) * r
        if last:
            line(last[0], last[1], x, y, 3, (91, 85, 74), 0.24)
        last = (x, y)

# forehead smile emblem, deliberately crooked
scribble_ellipse(450, 145, 61, 33, (223, 62, 48), 8, 0.18)
line(413, 144, 487, 149, 5, (91, 50, 42), 0.5)
line(425, 132, 420, 160, 5, (91, 50, 42), 0.5)
line(480, 136, 473, 162, 5, (91, 50, 42), 0.5)

# painterly frame
for i in range(16):
    c = (126 + i * 4, 77 + i * 3, 42 + i * 2)
    line(i * 3, i * 3, W - i * 3, i * 2, 5, c, 0.45)
    line(W - i * 2, i * 3, W - i * 3, H - i * 3, 5, c, 0.45)
    line(W - i * 3, H - i * 3, i * 3, H - i * 2, 5, c, 0.45)
    line(i * 2, H - i * 3, i * 3, i * 3, 5, c, 0.45)


def write_png(path: Path) -> None:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack('>I', len(data))
            + kind
            + data
            + struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    raw = bytearray()
    for row in pixels:
        raw.append(0)  # filter type: None
        for r, g, b in row:
            raw.extend((r, g, b))

    png = bytearray(b'\x89PNG\r\n\x1a\n')
    png.extend(chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)))
    png.extend(chunk(b'IDAT', zlib.compress(bytes(raw), 9)))
    png.extend(chunk(b'IEND', b''))
    path.write_bytes(png)


out = Path(__file__).with_name('anpanman-nose-hair-cutter-henachoko.png')
write_png(out)
print(out)
