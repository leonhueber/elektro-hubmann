"""Local, reversible Smart Home A camera/detail overlay on exterior revision 01."""
from math import radians
from house_v4.motion import FRAME_COUNT, STEP, state as base_state, ramp, lerp

REVISION = 'v4-scroll-02-exterior-01-smart-01'
CLOSE_CAMERA = (9.5, -13.0, 21.5)
CLOSE_TARGET = (2.6, 1.65, 3.95)
CLOSE_LENS = 86.0


def details(p):
    focus = ramp(p, .57, .605) * (1-ramp(p, .645, .67))
    visibility = ramp(p, .575, .595) * (1-ramp(p, .645, .665))
    tilt = radians(55*ramp(p, .59, .605)-90*ramp(p, .605, .623)) * (1-ramp(p, .645, .67))
    return {'focus': focus, 'controller': visibility, 'tilt': tilt}


def state(p):
    s = base_state(p)
    d = details(p)
    s['camera'] = lerp(s['camera'], CLOSE_CAMERA, d['focus'])
    s['target'] = lerp(s['target'], CLOSE_TARGET, d['focus'])
    s['lens'] = s['lens']*.9 + (CLOSE_LENS-s['lens']*.9)*d['focus']
    return {**s, **d}


def schedule():
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


def changed(frame):
    return .57 < (frame-1)/(FRAME_COUNT-1) < .67
