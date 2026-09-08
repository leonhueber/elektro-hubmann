"""Delivery regressions: failed/partial renders must never activate the site."""
from contextlib import ExitStack
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from house_v4 import continuous_delivery as delivery


class ContinuousDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        root = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.root = root
        animation = root / 'assets/model.blend'
        animation.parent.mkdir(parents=True)
        animation.write_bytes(b'Native animation revision one')
        out = root / 'qa'
        chapters = [{'id': 'planning', 'start': 0, 'rest': 0}, {'id': 'energy', 'start': .5, 'rest': 1}]
        settings = {**delivery.SETTINGS, 'size': 32}
        manifest = deepcopy(delivery.MANIFEST)
        manifest.update(frameCount=3, chapters=chapters)
        manifest['profiles']['desktop'].update(width=32, height=32)
        manifest['profiles']['mobile'].update(width=16, height=16)
        self.stack.enter_context(patch.multiple(delivery, ROOT=root, ANIMATION=animation,
            OUT=out, RENDERS=out / 'renders', FRAME_COUNT=3, CHAPTERS=chapters,
            SETTINGS=settings, MANIFEST=manifest, schedule=lambda: ([1, 3], {})))
        config = root / 'src/config'
        config.mkdir(parents=True)
        for name in ['house-v4-frames.json', 'house-v4-manifest.json']:
            (config / name).write_text('{"previous": true}\n', encoding='utf-8')
        self.original = {path.name: path.read_bytes() for path in config.iterdir()}

    def assert_not_activated(self):
        for name, content in self.original.items():
            self.assertEqual((self.root / 'src/config' / name).read_bytes(), content)

    def seed(self, frames=(1, 3), flat=None):
        delivery.RENDERS.mkdir(parents=True, exist_ok=True)
        progress = {'identity': delivery.identity(), 'blender': 'test', 'completed': {}}
        for frame in frames:
            image = Image.new('RGB', (32, 32), flat or 'white')
            if flat is None:
                ImageDraw.Draw(image).rectangle((4, 5, 24, 26), fill=(40 + frame * 20, 64, 30))
            path = delivery.RENDERS / f'frame-{frame:04d}.png'
            image.save(path)
            progress['completed'][str(frame)] = {'sha256': delivery.sha(path), 'seconds': 1}
        delivery.write_json(delivery.OUT / 'render-progress.json', progress)

    def test_pixels_reject_black_white_flat_and_nonfinite(self):
        for values in [[0, 1 / 255] * 100, [1] * 100, [.5] * 100, [float('nan'), .5]]:
            with self.subTest(values=values[:2]), self.assertRaises(RuntimeError):
                delivery.pixel_metrics(values)
        self.assertGreater(delivery.pixel_metrics([.05, .3, .9, 1])['standardDeviation'], .2)

    def test_missing_frame_does_not_change_active_configuration(self):
        self.seed(frames=(1,))
        with self.assertRaisesRegex(RuntimeError, 'Missing or changed production frame: 3'):
            delivery.export()
        self.assert_not_activated()
        self.assertEqual(json.loads((delivery.OUT / 'pipeline-status.json').read_text())['phase'], 'failed')

    def test_valid_hash_does_not_let_a_black_render_activate(self):
        self.seed(flat='black')
        with self.assertRaisesRegex(RuntimeError, 'Black or empty'):
            delivery.export()
        self.assert_not_activated()

    def test_source_change_rejects_resume_and_export(self):
        self.seed()
        delivery.ANIMATION.write_bytes(b'A different camera bake')
        with self.assertRaisesRegex(RuntimeError, 'identity changed'):
            delivery.verified_production()
        self.assert_not_activated()

    def test_truncated_png_cannot_pass_native_validation(self):
        self.seed()
        path = delivery.RENDERS / 'frame-0003.png'
        path.write_bytes(path.read_bytes()[:35])
        progress_path = delivery.OUT / 'render-progress.json'
        progress = json.loads(progress_path.read_text())
        progress['completed']['3']['sha256'] = delivery.sha(path)
        delivery.write_json(progress_path, progress)
        with self.assertRaises(Exception):
            delivery.export()
        self.assert_not_activated()

    def test_full_export_and_resume_verify_assets_and_preserve_orientation(self):
        self.seed()
        orientation = self.root / 'src/config/house-v4-orientation.json'
        orientation.write_text('{"markers": [{"id": "roof"}]}\n', encoding='utf-8')
        unchanged = orientation.read_bytes()
        result = delivery.export(orientation=orientation)
        self.assertEqual(result['nativeFrames'], 2)
        self.assertEqual(orientation.read_bytes(), unchanged)
        self.assertEqual(result['orientationSource']['sha256'], delivery.sha(orientation))
        for profile, size in [('desktop', 32), ('mobile', 16)]:
            folder = self.root / 'public' / delivery.MANIFEST['assetPath'] / profile
            self.assertEqual({path.name for path in folder.iterdir()},
                             {'frame-0001.webp', 'frame-0003.webp', 'planning.webp', 'energy.webp'})
            self.assertEqual(delivery.sha(folder / 'energy.webp'), delivery.sha(folder / 'frame-0003.webp'))
            with Image.open(folder / 'planning.webp') as image:
                self.assertEqual(image.size, (size, size))
        self.assertEqual(json.loads((self.root / 'src/config/house-v4-manifest.json').read_text()), delivery.MANIFEST)
        resumed = delivery.export(resume=True, orientation=orientation)
        self.assertEqual(result['profiles'], resumed['profiles'])
        self.assertTrue(json.loads((delivery.OUT / 'pipeline-status.json').read_text())['activated'])

    def test_concurrent_configuration_edit_is_preserved_and_blocks_activation(self):
        self.seed()
        inspect = delivery.inspect_image
        changed = self.root / 'src/config/house-v4-manifest.json'
        changed_content = '{"changedByOtherWork": true}\n'
        first = True

        def concurrent_edit(*args, **kwargs):
            nonlocal first
            if first:
                first = False
                changed.write_text(changed_content, encoding='utf-8')
            return inspect(*args, **kwargs)

        with patch.object(delivery, 'inspect_image', side_effect=concurrent_edit):
            with self.assertRaisesRegex(RuntimeError, 'configuration changed'):
                delivery.export()
        self.assertEqual(changed.read_text(encoding='utf-8'), changed_content)
        self.assertEqual((self.root / 'src/config/house-v4-frames.json').read_bytes(), self.original['house-v4-frames.json'])

    def test_second_configuration_replace_failure_restores_frame_map(self):
        config = self.root / 'src/config'
        replace = Path.replace

        def fail_manifest(path, target):
            if path.name == 'house-v4-manifest.json.pending':
                raise OSError('Simulated disk failure')
            return replace(path, target)

        with patch.object(Path, 'replace', fail_manifest), self.assertRaises(OSError):
            delivery.activate(delivery.MANIFEST, {}, self.original)
        self.assert_not_activated()

    def test_preview_requires_explicit_valid_frames_and_never_exports(self):
        with self.assertRaisesRegex(RuntimeError, 'explicit'):
            delivery.requested_frames('', [1, 3], preview=True)
        for frames in ['2', '1,0', 'bad']:
            with self.subTest(frames=frames), self.assertRaises(RuntimeError):
                delivery.requested_frames(frames, [1, 3], preview=True)
        with patch.object(sys, 'argv', ['delivery', '--export', '--preview']):
            with self.assertRaises(SystemExit) as caught:
                delivery.main()
        self.assertEqual(caught.exception.code, 2)
        self.assert_not_activated()
        self.assertNotEqual(delivery.preview_folder(delivery.identity(True)), delivery.OUT)


if __name__ == '__main__':
    unittest.main()
