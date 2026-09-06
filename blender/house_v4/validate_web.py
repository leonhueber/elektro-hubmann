"""Validate the saved web animation, including actual Blender light keyframes."""
import hashlib
import json
import sys
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'blender'))
from house_v4.motion import MANIFEST, FRAME_COUNT, STEP


def validate():
    path = ROOT/'assets/3d/elektro-hubmann-house-v4-web.blend'
    if Path(bpy.data.filepath).resolve() != path.resolve():
        raise RuntimeError('Load the native web animation explicitly.')
    scene = bpy.context.scene
    assert scene.get('web_revision') == MANIFEST['revision']
    lights = [obj for obj in scene.objects if obj.get('interior_light')]
    assert lights, 'No interior lights in the saved model'
    records = []
    for obj in lights:
        nominal = obj.get('nominal_watts', 20)
        values = []
        action = obj.data.animation_data.action
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    bag = strip.channelbag(slot)
                    if bag:
                        for curve in bag.fcurves:
                            if curve.data_path == 'energy':
                                values.extend(point.co.y for point in curve.keyframe_points)
        assert len(values) >= len(range(1, FRAME_COUNT+1, STEP)), obj.name
        assert max(abs(value-nominal) for value in values) < 1e-4, obj.name
        color = tuple(obj.data.color)
        assert max(abs(a-b) for a,b in zip(color, (1,.46,.18))) < 1e-5, (obj.name, color)
        records.append({'name': obj.name, 'watts': nominal, 'color': color,
                        'keyframes': len(values), 'minimumWatts': min(values), 'maximumWatts': max(values)})
    report = {'revision': MANIFEST['revision'], 'passed': True,
              'nativeAnimationSha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'interiorLights': len(lights), 'constantWarmLighting': records}
    (ROOT/'docs/version-g-qa/blender-v4/web/native-lighting-validation.json').write_text(
        json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('V4_WEB_LIGHTING_VALID', len(lights), 'lights, all keyframes at nominal power')


if __name__ == '__main__':
    validate()
