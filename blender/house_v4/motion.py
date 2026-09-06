"""Deterministic, reversible V4 motion. Coordinates are metres, progress is 0..1.

Quintic time easing advances along sampled arc length of each complete Bezier
travel. Camera orientation is derived from a separate target, with no roll.
This module also runs in regular Python for validation and asset scheduling.
"""
from bisect import bisect_left
from functools import lru_cache
from math import dist

FRAME_COUNT = 1441
STEP = 2
REVISION = 'v4-scroll-02'
POSES = {
    'planning': ((23, -27, 8.3), (4.8, 4.5, 4.3), 78),
    'opening': ((24, -32, 26), (4.8, 5, 7.8), 70),
    'installation': ((15.6, -26.6, 40.15), (4.8, 5.2, .7), 120),
    'lighting': ((15.6, -26.6, 40.15), (4.8, 5.2, .7), 120),
    'smarthome': ((15.6, -26.6, 43.15), (4.8, 5.2, 3.7), 120),
    'wide': ((23, -27, 13), (4.8, 4.5, 4.3), 78),
    'security': ((7.7, -8.7, 3.4), (6, .1, 1.4), 74),
    'energy': ((23, -23, 25), (4.8, 4.7, 4.7), 70),
    'closing': ((23, -27, 8.3), (4.8, 4.5, 4.3), 78),
}
# Each travel is continuous through its internal control points.
LEGS = [
    (.08, .20, 'planning', 'opening', (29, -40, 14), (27, -37, 25)),
    (.23, .30, 'opening', 'installation', (31, -42, 30), (23, -42, 42)),
    (.51, .57, 'lighting', 'smarthome', (35, -80, 65), (35, -80, 68)),
    (.67, .71, 'smarthome', 'wide', (23, -42, 46), (28, -37, 22)),
    (.71, .76, 'wide', 'security', (19, -23, 10), (11, -15, 5)),
    (.82, .88, 'security', 'energy', (15, -25, 7), (28, -30, 21)),
    (.94, .98, 'energy', 'closing', (25, -26, 21), (24, -29, 12)),
]
CHAPTERS = [
    {'id': 'planning', 'start': 0, 'rest': .04},
    {'id': 'installation', 'start': .08, 'rest': .35},
    {'id': 'lighting', 'start': .39, 'rest': .47},
    {'id': 'smarthome', 'start': .51, 'rest': .63},
    {'id': 'security', 'start': .67, 'rest': .79},
    {'id': 'energy', 'start': .82, 'rest': .91},
]
MANIFEST = {
    'version': 4, 'revision': REVISION, 'frameCount': FRAME_COUNT,
    'assetPath': 'images/version-g/house-v4/',
    'profiles': {
        'desktop': {'width': 1000, 'height': 1000, 'step': STEP, 'cacheFrames': 12},
        'mobile': {'width': 720, 'height': 720, 'step': STEP, 'cacheFrames': 18},
    },
    'chapters': CHAPTERS,
}


def ease(t):
    t = min(1, max(0, t))
    return t*t*t*(t*(6*t-15)+10)


def ramp(p, start, end):
    return ease((p-start)/(end-start))


def lerp(a, b, t):
    return tuple(x+(y-x)*t for x, y in zip(a, b))


def bezier(points, t):
    a, b, c, d = points
    return tuple((1-t)**3*a[i]+3*(1-t)**2*t*b[i]+3*(1-t)*t*t*c[i]+t**3*d[i] for i in range(3))


@lru_cache(maxsize=16)
def arc_table(points):
    positions = [bezier(points, i/512) for i in range(513)]
    lengths = [0]
    for a, b in zip(positions, positions[1:]):
        lengths.append(lengths[-1]+dist(a, b))
    return tuple(value/lengths[-1] for value in lengths)


def arc_position(points, progress):
    table = arc_table(points)
    i = max(1, min(512, bisect_left(table, progress)))
    fraction = (progress-table[i-1])/(table[i]-table[i-1])
    return bezier(points, (i-1+fraction)/512)


def camera(p):
    pose = POSES['planning']
    for start, end, first, last, control1, control2 in LEGS:
        if p < start:
            return pose
        a, b = POSES[first], POSES[last]
        if p <= end:
            t = ramp(p, start, end)
            position = arc_position((a[0], control1, control2, b[0]), t)
            target = (bezier((a[1], (4.8, 5.2, 6), (4.8, 5.2, 9), b[1]), t)
                      if first == 'lighting' else lerp(a[1], b[1], t))
            return position, target, a[2]+(b[2]-a[2])*t
        pose = b
    return pose


def state(p):
    p = min(1, max(0, p))
    og = 3+4*ramp(p, .14, .20)+23*ramp(p, .23, .30)-27*ramp(p, .515, .565)
    roof = 6+4*ramp(p, .08, .14)+4*ramp(p, .14, .20)+26*ramp(p, .23, .30)-34*ramp(p, .682, .71)
    cut = 1-ramp(p, .11, .20)+ramp(p, .68, .708)
    eg = 1-ramp(p, .54, .57)+ramp(p, .67, .691)
    route = ramp(p, .265, .30)*(1-ramp(p, .39, .43))
    blind = ramp(p, .57, .60)*(1-ramp(p, .67, .70))
    # Keep the same warm illumination through opening, both storeys and closing.
    light = 1.0
    pos, target, lens = camera(p)
    return {'camera': pos, 'target': target, 'lens': lens, 'og': og, 'roof': roof,
            'cut': cut, 'eg': eg, 'route': route, 'blind': blind, 'light': light}


def schedule():
    """Alias only numerically identical native states, never nearby motion frames."""
    seen, aliases, unique = {}, {}, []
    for frame in range(1, FRAME_COUNT+1, STEP):
        values = state((frame-1)/(FRAME_COUNT-1))
        signature = tuple(round(x, 7) for value in values.values()
                          for x in (value if isinstance(value, tuple) else (value,)))
        if signature in seen:
            aliases[str(frame)] = seen[signature]
        else:
            seen[signature] = frame
            unique.append(frame)
    return unique, aliases
