"""Continuous V4 tour: native camera travel and large, reversible device motion.

Progress is the scroll position, not a sequence of chapter stops. ``rest`` in
CHAPTERS is retained only as the frontend's navigation target. Positions are
world metres, except blind_drop (local metres) and tilt (local X radians).
This module has no Blender dependency and does not mutate an existing scene.
"""
from bisect import bisect_right
from functools import lru_cache
from math import isfinite, radians

from house_v4.motion import FRAME_COUNT, STEP, ramp

REVISION = 'v4-continuous-01'
CHAPTERS = [
    {'id': 'planning', 'start': 0, 'rest': .035},
    {'id': 'installation', 'start': .12, 'rest': .275},
    {'id': 'smarthome', 'start': .37, 'rest': .535},
    {'id': 'security', 'start': .64, 'rest': .755},
    {'id': 'energy', 'start': .81, 'rest': .95},
]

# Existing native objects, verified against architecture.py and rooms.py.
ENTRANCE_LENS = (6.83, -.054, 1.49)
BEDROOM_TARGET = (2.65, 1.05, 4.05)
PV_TARGET = (7.2, 5.4, 7.5)
WALLBOX_TARGET = (9.665, 2.3, 1.35)
CAR_CENTER = (11.5, 3.5, .80)
CHARGING_PORT = (10.55, 2.3, .73)
PLANNING_CAMERA = (25.5, -30.5, 12.)
PLANNING_TARGET = (6.2, 4.2, 4.25)
PLANNING_LENS = 66.
BLIND_TRAVEL_METRES = 1.85

# A shape-preserving cubic spline avoids the braking/hold/acceleration pattern
# of the old independently eased camera legs. Every row is a pass-through pose.
# In particular, the close camera keeps moving sideways during device action.
# Columns: progress, camera XYZ, look target XYZ, focal length in millimetres.
CAMERA_KEYS = (
    (0, PLANNING_CAMERA, PLANNING_TARGET, PLANNING_LENS),
    (.10, (26., -28., 14.), (5.5, 4.5, 5.), 65.),
    (.23, (24., -29., 25.), (4.8, 5., 7.), 54.),
    (.34, (21., -26.5, 25.), (4.8, 4.7, 7.), 51.),
    (.40, (15., -16., 16.), (3.1, 1.8, 5.2), 57.),
    # Look past the right edge of the blind into the room. A frontal low view
    # lets the lowered blind obscure the bed, defeating the scene's explanation.
    (.46, (12.5, -8., 11.8), (2.7, 1.2, 4.2), 58.),
    (.54, (11.3, -5.5, 10.4), BEDROOM_TARGET, 52.),
    (.60, (10.2, -4.8, 9.6), (2.6, 1.1, 4.), 49.),
    (.64, (9.8, -10.7, 5.8), (5.4, .5, 2.7), 65.),
    (.70, (8.2, -5.8, 3.5), ENTRANCE_LENS, 73.),
    (.745, (7.6, -2.8, 1.85), ENTRANCE_LENS, 78.),
    (.78, (6.2, -3.2, 2.1), ENTRANCE_LENS, 76.),
    (.83, (15., -13., 15.3), (7.2, 4.4, 7.5), 70.),
    # Pull across a complete house-and-car view before following the energy
    # connection down to the wallbox. These are moving poses, not chapter holds.
    (.885, (25., -13., 13.), (6., 4.25, 3.9), 51.),
    (.91, (24., -12.5, 11.7), (6.2, 4.2, 3.7), 49.),
    (.95, (19., -7., 7.), (10.8, 2.8, 1.6), 62.),
    (1., (17., -5., 4.6), (10.75, 2.7, 1.25), 60.),
)


def _clamp(progress):
    if not isfinite(progress):
        return 1. if progress > 0 else 0.
    return min(1., max(0., progress))


def _edge_slope(h0, h1, d0, d1):
    slope = ((2*h0+h1)*d0-h0*d1)/(h0+h1)
    if slope*d0 <= 0:
        return 0.
    if d0*d1 < 0 and abs(slope) > abs(3*d0):
        return 3*d0
    return slope


@lru_cache(maxsize=1)
def _curves():
    """PCHIP derivatives: continuous velocity and no coordinate overshoot."""
    times = tuple(row[0] for row in CAMERA_KEYS)
    widths = tuple(b-a for a, b in zip(times, times[1:]))
    values = tuple((*row[1], *row[2], row[3]) for row in CAMERA_KEYS)
    columns = []
    for column in zip(*values):
        slopes = tuple((b-a)/h for a, b, h in zip(column, column[1:], widths))
        derivatives = [_edge_slope(widths[0], widths[1], slopes[0], slopes[1])]
        for index in range(1, len(column)-1):
            left, right = slopes[index-1], slopes[index]
            if left*right <= 0:
                derivatives.append(0.)
            else:
                w1, w2 = 2*widths[index]+widths[index-1], widths[index]+2*widths[index-1]
                derivatives.append((w1+w2)/(w1/left+w2/right))
        derivatives.append(_edge_slope(widths[-1], widths[-2], slopes[-1], slopes[-2]))
        columns.append((tuple(column), tuple(derivatives)))
    return times, widths, tuple(columns)


def camera(progress):
    p = _clamp(progress)
    times, widths, curves = _curves()
    index = max(0, min(len(times)-2, bisect_right(times, p)-1))
    width = widths[index]
    t = (p-times[index])/width
    h00, h10 = 2*t**3-3*t*t+1, t**3-2*t*t+t
    h01, h11 = -2*t**3+3*t*t, t**3-t*t
    value = tuple(h00*ys[index]+h10*width*ds[index]
                  + h01*ys[index+1]+h11*width*ds[index+1]
                  for ys, ds in curves)
    return value[:3], value[3:6], value[6]


def state(progress):
    p = _clamp(progress)
    pos, target, lens = camera(p)
    # All three architectural levels are visible while separating. Roof motion
    # leads the upper floor and closes after it, maintaining real clearance.
    og = 3+4*ramp(p, .12, .265)-4*ramp(p, .30, .415)
    roof = 6+8*ramp(p, .075, .23)-8*ramp(p, .595, .66)
    cut = 1-ramp(p, .135, .25)+ramp(p, .605, .655)
    eg = 1-ramp(p, .36, .415)+ramp(p, .605, .645)
    route = ramp(p, .175, .24)*(1-ramp(p, .335, .405))
    focus = ramp(p, .37, .435)*(1-ramp(p, .595, .64))
    controller = ramp(p, .385, .425)*(1-ramp(p, .605, .64))
    press = ramp(p, .425, .439)*(1-ramp(p, .439, .451))
    blind = ramp(p, .40, .425)
    deployment = ramp(p, .445, .55)
    # Slats separate from a compact stack by almost two metres. The native
    # builder distributes this additional travel by slat index/count.
    # Keeping the lowered state afterwards avoids a distracting automatic reset.
    tilt = radians(55*ramp(p, .45, .485)-90*ramp(p, .515, .59))
    security = ramp(p, .645, .70)*(1-ramp(p, .78, .825))
    energy = ramp(p, .81, .865)
    return {
        'camera': pos, 'target': target, 'lens': lens,
        'og': og, 'roof': roof, 'cut': cut, 'eg': eg,
        'route': route, 'route_trace': ramp(p, .175, .335),
        'blind': blind, 'blind_drop': BLIND_TRAVEL_METRES*deployment,
        'light': 1., 'focus': focus, 'controller': controller,
        'controller_press': press, 'tilt': tilt, 'security_focus': security,
        'energy': energy, 'energy_flow': ramp(p, .85, 1.),
        'charge': ramp(p, .895, 1.),
    }


def schedule():
    """Only exact native-state duplicates may alias; motion is never discarded."""
    seen, unique, aliases = {}, [], {}
    for frame in range(1, FRAME_COUNT+1, STEP):
        signature = tuple(round(x, 7) for value in state((frame-1)/(FRAME_COUNT-1)).values()
                          for x in (value if isinstance(value, tuple) else (value,)))
        if signature in seen:
            aliases[str(frame)] = seen[signature]
        else:
            seen[signature] = frame
            unique.append(frame)
    return unique, aliases
