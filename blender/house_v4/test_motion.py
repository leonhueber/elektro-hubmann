"""Geometry and timing invariants for the native scroll bake."""
import unittest
from math import dist
from motion import camera, state, schedule, POSES, LEGS, FRAME_COUNT, STEP


class MotionTests(unittest.TestCase):
    def test_warm_lights_stay_on_through_the_entire_animation(self):
        for frame in range(FRAME_COUNT):
            self.assertEqual(state(frame/(FRAME_COUNT-1))['light'], 1.0)

    def test_reading_poses_and_matching_light_cameras(self):
        for p, name in [(.04, 'planning'), (.215, 'opening'), (.35, 'installation'),
                        (.47, 'lighting'), (.63, 'smarthome'), (.79, 'security'),
                        (.91, 'energy'), (.99, 'closing')]:
            self.assertEqual(camera(p), POSES[name])
        self.assertEqual(camera(.35), camera(.47))
        self.assertEqual(camera(.04), camera(.99))

    def test_roof_clears_upper_storey_and_camera_stays_outside(self):
        for frame in range(FRAME_COUNT):
            s = state(frame/(FRAME_COUNT-1))
            self.assertGreaterEqual(s['roof']-s['og'], 3-1e-9)
            self.assertLess(s['camera'][1], -8)
            self.assertGreater(dist(s['camera'], s['target']), 8)
            for field in ['cut', 'eg', 'route', 'blind']:
                self.assertGreaterEqual(s[field], -1e-9)
                self.assertLessEqual(s[field], 1+1e-9)
        self.assertAlmostEqual(state(.14)['og'], 3)
        self.assertGreater(state(.14)['roof'], 6)

    def test_travel_is_continuous_and_stops_at_holds(self):
        for start, end, *_ in LEGS:
            for boundary in [start, end]:
                self.assertLess(dist(camera(boundary-1e-5)[0], camera(boundary+1e-5)[0]), 1e-5)

    def test_aliases_reuse_only_identical_states(self):
        frames, aliases = schedule()
        self.assertEqual(len(frames)+len(aliases), len(range(1, FRAME_COUNT+1, STEP)))
        for frame, source in aliases.items():
            self.assertIn(source, frames)
            a, b = state((int(frame)-1)/1440), state((source-1)/1440)
            for field in a:
                if isinstance(a[field], tuple):
                    self.assertLess(dist(a[field], b[field]), 1e-6)
                else:
                    self.assertAlmostEqual(a[field], b[field], places=6)


if __name__ == '__main__':
    unittest.main()
