"""Regression checks for the native Smart Home overlay and frame reuse boundary."""
import sys
import unittest
from math import dist
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from house_v4.motion import state as base_state, FRAME_COUNT, STEP
from house_v4.smarthome_motion import state, details, schedule, changed


class SmartHomeMotionTests(unittest.TestCase):
    def test_only_smart_home_changes_and_all_lights_remain_on(self):
        for frame in range(1, FRAME_COUNT+1, STEP):
            p = (frame-1)/(FRAME_COUNT-1)
            original, smart = base_state(p), state(p)
            for field in ['og', 'roof', 'cut', 'eg', 'route', 'blind', 'light']:
                self.assertEqual(smart[field], original[field])
            self.assertEqual(smart['light'], 1)
            if not changed(frame):
                self.assertEqual(smart['camera'], original['camera'])
                self.assertEqual(smart['target'], original['target'])
                self.assertEqual(smart['lens'], original['lens']*.9)
                self.assertEqual(details(p), {'focus': 0, 'controller': 0, 'tilt': 0})

    def test_camera_enters_and_returns_without_boundary_jump(self):
        for boundary in [.57, .605, .645, .67]:
            before, after = state(boundary-1e-5), state(boundary+1e-5)
            self.assertLess(dist(before['camera'], after['camera']), 1e-5)
            self.assertLess(dist(before['target'], after['target']), 1e-5)
        self.assertGreater(dist(state(.57)['camera'], state(.63)['camera']), 20)

    def test_blinds_tilt_then_open_for_the_reading_pose(self):
        self.assertGreater(details(.605)['tilt'], details(.63)['tilt'])
        self.assertLess(details(.63)['tilt'], 0)
        self.assertEqual(details(.63)['controller'], 1)
        self.assertEqual(details(.67)['controller'], 0)

    def test_aliases_never_replace_movement_with_another_state(self):
        frames, aliases = schedule()
        self.assertEqual(len(frames)+len(aliases), 721)
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
