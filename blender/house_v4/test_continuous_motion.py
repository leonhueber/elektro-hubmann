"""Perceptible motion, collision clearance and reversal for the continuous tour."""
import sys
import unittest
from itertools import product
from math import atan2, dist, isfinite, radians, sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from house_v4.continuous_motion import (
    BLIND_TRAVEL_METRES, CAMERA_KEYS, CHAPTERS, ENTRANCE_LENS,
    WALLBOX_FACE, WALLBOX_TARGET,
    FRAME_COUNT, STEP, camera, schedule, state,
)


def projected(point, pose):
    position, target, lens = pose
    vector = tuple(y-x for x, y in zip(position, target))
    length = sqrt(sum(value*value for value in vector))
    forward = tuple(value/length for value in vector)
    lateral = (forward[1], -forward[0], 0.)
    length = sqrt(sum(value*value for value in lateral))
    right = tuple(value/length for value in lateral)
    up = (right[1]*forward[2], -right[0]*forward[2], right[0]*forward[1]-right[1]*forward[0])
    relative = tuple(x-y for x, y in zip(point, position))
    dot = lambda a, b: sum(x*y for x, y in zip(a, b))
    depth = dot(relative, forward)
    return dot(relative, right)*lens/(36*depth), dot(relative, up)*lens/(36*depth)


class ContinuousMotionTests(unittest.TestCase):
    def test_camera_keeps_moving_at_every_native_sample(self):
        previous = state(0)
        for frame in range(1, FRAME_COUNT):
            current = state(frame/(FRAME_COUNT-1))
            self.assertGreater(dist(previous['camera'], current['camera']), .0001,
                               f'Stationary camera at native frame {frame+1}')
            previous = current
        # A two-percent scroll interval must produce visible travel, including
        # the close-up sections and the beginning/end of each navigation topic.
        for index in range(981):
            p = index/1000
            self.assertGreater(dist(camera(p)[0], camera(p+.02)[0]), .15)

    def test_camera_velocity_is_continuous_through_pass_through_poses(self):
        epsilon = 1e-7
        for p, *_ in CAMERA_KEYS[1:-1]:
            a, b, c = camera(p-epsilon), camera(p), camera(p+epsilon)
            for field in [0, 1]:
                before = tuple((y-x)/epsilon for x, y in zip(a[field], b[field]))
                after = tuple((y-x)/epsilon for x, y in zip(b[field], c[field]))
                self.assertLess(dist(before, after), .02, f'Velocity jump at {p}')
                if field == 0:
                    self.assertGreater(dist(before, (0, 0, 0)), 1., f'Camera brakes to a stop at {p}')
            self.assertLess(abs((b[2]-a[2])-(c[2]-b[2]))/epsilon, .02)

    def test_native_geometry_clearance_and_valid_material_states(self):
        unit_fields = ['cut', 'eg', 'route', 'route_trace', 'blind', 'focus',
                       'controller', 'controller_press', 'security_focus',
                       'energy', 'energy_flow', 'charge']
        for frame in range(FRAME_COUNT):
            s = state(frame/(FRAME_COUNT-1))
            self.assertGreaterEqual(s['roof']-s['og'], 3-1e-9)
            self.assertTrue(s['camera'][1] < -2.7 or s['camera'][0] > 10.2,
                            'Camera must stay outside the front or east facade')
            self.assertGreaterEqual(s['camera'][2], 1.8)
            self.assertGreater(dist(s['camera'], s['target']), 2.5)
            self.assertEqual(s['light'], 1.)
            self.assertTrue(all(0 <= s[field] <= 1 for field in unit_fields))
            self.assertTrue(all(isfinite(value) for value in (*s['camera'], *s['target'], s['lens'])))
        self.assertGreater(state(.275)['og'], 6.9)
        self.assertEqual(state(.275)['eg'], 1)
        self.assertEqual(state(.275)['roof'], 14)
        self.assertEqual(state(.67)['og'], 3)
        self.assertEqual(state(.67)['roof'], 6)
        self.assertEqual(state(.67)['cut'], 1)

    def test_smart_home_has_large_travel_and_tilt_while_camera_moves(self):
        start, lowered, tilted = state(.445), state(.55), state(.59)
        self.assertEqual(start['blind_drop'], 0)
        self.assertAlmostEqual(lowered['blind_drop'], BLIND_TRAVEL_METRES)
        self.assertGreater(lowered['blind_drop']-start['blind_drop'], 1.8)
        self.assertGreater(dist(start['camera'], lowered['camera']), 3)
        self.assertAlmostEqual(state(.49)['tilt'], radians(55))
        self.assertAlmostEqual(tilted['tilt'], radians(-35))
        self.assertGreater(state(.439)['controller_press'], .99)
        self.assertEqual(state(.451)['controller_press'], 0)
        close = state(.535)
        horizontal = dist(close['camera'][:2], close['target'][:2])
        pitch = atan2(close['camera'][2]-close['target'][2], horizontal)
        self.assertLess(pitch, radians(35))
        self.assertEqual(state(.535)['controller'], 1)
        self.assertEqual(state(.535)['og'], 3)

    def test_all_three_installation_levels_fit_with_margin_while_opening(self):
        for index in range(120, 341):
            p = index/1000
            s = state(p)
            roof = [(x, y, s['roof']+z) for x, y, z in [
                (4.8, -.3, 3.5), (4.8, 11.1, 3.5),
                (-.3, -.3, 0), (-.3, 11.1, 0),
                (9.9, -.3, 0), (9.9, 11.1, 0),
            ]]
            levels = [(x, y, z) for x in [0, 9.6] for y in [-1.9, 11.1]
                      for z in [-.25, s['og']-.22, s['og']+2.9]]
            bay = list(product([9.65, 11.56], [.1, 7.2], [-.25, 1.6]))
            for point in roof+levels+bay:
                self.assertLess(max(abs(v) for v in projected(point, camera(p))), .48,
                                f'Clipped installation geometry at progress {p}: {point}')

    def test_smart_home_keeps_balcony_blind_bed_and_controller_visible_together(self):
        balcony = list(product([.3, 4.7], [-1.9], [2.85, 4.2]))
        blind = list(product([.99, 3.51], [.025], [3.16, 5.515]))
        controller = list(product([4.085, 4.255], [5.054], [4.135, 4.305]))
        bed = [(2.04, 2.42, 3.7), (.95, 2.4, 3.75), (2.85, 1.6, 3.55)]
        for index in range(470, 601):
            p = index/1000
            pose = camera(p)
            for point in balcony+blind+controller+bed:
                self.assertLess(max(abs(v) for v in projected(point, pose)), .48,
                                f'Clipped Smart Home feature at progress {p}: {point}')
            # A lowered blind is physically opaque: room visibility must come
            # from the side/above, never from making its material transparent.
            for point in bed:
                fraction = (.025-point[1])/(pose[0][1]-point[1])
                intersection = tuple(a+(b-a)*fraction for a, b in zip(point, pose[0]))
                self.assertTrue(intersection[0] > 3.55 or intersection[2] > 5.55,
                                f'Blind occludes the bed at progress {p}: {intersection}')

    def test_security_uses_real_entrance_lens_in_close_view(self):
        s = state(.755)
        self.assertLess(dist(s['target'], ENTRANCE_LENS), 1e-12)
        self.assertLess(dist(s['camera'], ENTRANCE_LENS), 3.2)
        # 16-cm intercom occupies more than one tenth of a 36-mm-sensor frame.
        visible_width = 36*dist(s['camera'], ENTRANCE_LENS)/s['lens']
        self.assertGreater(.16/visible_width, .10)

    def test_planning_contains_house_and_energy_ends_at_wallbox(self):
        # Conservative whole-house bounds include the roof, balcony and bay.
        house_bounds = list(product([0, 9.6], [-1.9, 10.8], [-.25, 9.5]))
        wallbox_bounds = list(product([9.65, 9.90], [2.1, 2.75], [.55, 1.60]))
        for corner in house_bounds+wallbox_bounds:
            self.assertLess(max(abs(v) for v in projected(corner, camera(0))), .48)
        for anchor in [WALLBOX_TARGET, WALLBOX_FACE]:
            self.assertLess(max(abs(v) for v in projected(anchor, camera(1))), .4)
        self.assertGreater(state(1)['charge'], state(.93)['charge'])
        self.assertGreater(state(1)['energy_flow'], state(.93)['energy_flow'])

    def test_energy_connects_complete_roof_house_and_wallbox_before_close_view(self):
        roof = [(x, y, z) for x, y, z in [
            (4.8, -.3, 9.5), (4.8, 11.1, 9.5),
            (-.3, -.3, 6), (-.3, 11.1, 6),
            (9.9, -.3, 6), (9.9, 11.1, 6),
        ]]
        house = list(product([0, 9.6], [-1.9, 10.8], [-.25, 6]))
        bay = list(product([9.65, 11.56], [.1, 7.2], [-.25, 1.65]))
        for index in range(885, 911):
            p = index/1000
            for point in roof+house+bay+[WALLBOX_TARGET, WALLBOX_FACE]:
                self.assertLess(max(abs(v) for v in projected(point, camera(p))), .48,
                                f'Energy overview clips connected architecture at {p}: {point}')
        # The shared view traverses a real spatial arc, then zooms to the wallbox.
        self.assertGreater(dist(camera(.885)[0], camera(.91)[0]), 1.5)
        wallbox = list(product([9.65, 9.90], [2.1, 2.75], [.55, 1.60]))
        for p in [.95, .975, 1.]:
            for point in wallbox+[WALLBOX_TARGET, WALLBOX_FACE]:
                self.assertLess(max(abs(v) for v in projected(point, camera(p))), .48)

    def test_navigation_targets_have_no_standstill_or_frame_aliases(self):
        self.assertEqual([row['id'] for row in CHAPTERS],
                         ['planning', 'installation', 'smarthome', 'security', 'energy'])
        for chapter in CHAPTERS:
            p = chapter['rest']
            self.assertGreater(dist(camera(p-.005)[0], camera(p+.005)[0]), .08)
        unique, aliases = schedule()
        self.assertEqual(unique, list(range(1, FRAME_COUNT+1, STEP)))
        self.assertEqual(aliases, {})

    def test_state_is_deterministic_on_reversal_and_clamps_endpoints(self):
        forward = [state(frame/(FRAME_COUNT-1)) for frame in range(FRAME_COUNT)]
        for frame in reversed(range(FRAME_COUNT)):
            self.assertEqual(state(frame/(FRAME_COUNT-1)), forward[frame])
        self.assertEqual(state(-.5), state(0))
        self.assertEqual(state(1.5), state(1))
        self.assertEqual(state(float('nan')), state(0))
        self.assertEqual(state(float('inf')), state(1))


if __name__ == '__main__':
    unittest.main()
