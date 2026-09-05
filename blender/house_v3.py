"""Build V3. Default saves only; rendering is always explicit.

blender --background --python blender/house_v3.py -- --proofs
blender --background --python blender/house_v3.py -- --sequence desktop
"""
import argparse
import json
import shutil
import sys
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'blender'))
from house_v3 import core, architecture, systems, motion

MANIFEST=json.loads((ROOT/'src/config/house-v3-manifest.json').read_text(encoding='utf-8'))
BLEND=ROOT/'assets/3d/elektro-hubmann-house-v3.blend'
QA=ROOT/'docs/version-g-qa/blender-v3'


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    core.collection('STAGE')
    core.palette()
    scene=bpy.context.scene
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGBA'
    scene.render.film_transparent=True
    scene.render.fps=30
    scene.render.use_file_extension=True
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=.15
    scene.world=bpy.data.worlds.new('V3 studio world')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.82,.88,1,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
    if hasattr(scene,'eevee'):
        scene.eevee.taa_render_samples=24
        scene.eevee.use_raytracing=False
    core.area('large softbox',(-7,-10,15),(0,0,2),2100,9)
    core.area('right fill',(9,-4,10),(0,0,2),1450,8,(.84,.91,1))
    core.area('rear rim',(-2,8,13),(0,0,3),1800,7,(1,.91,.77))
    core.area('front bounce',(1,-10,5),(0,0,3),450,7,(1,.95,.85))
    core.collection('CAMERAS')
    core.camera('Desktop',(13,-22,12.5),(0,-.2,3.80),16.8)
    core.camera('Mobile',(11,-25,13.0),(0,-.2,3.80),15.8)
    core.camera('Ground plan',(0,0,23),(0,0,0),12.8)
    scene.camera=bpy.data.objects['V3 Desktop']


def render(frame,path,profile='desktop',width=None,samples=24):
    scene=bpy.context.scene
    config=MANIFEST['profiles'][profile]
    scene.frame_set(frame)
    # Timeline markers use Desktop for editing, so select the output camera last.
    scene.camera=bpy.data.objects['V3 '+profile.capitalize()]
    scene.render.resolution_x=width or config['width']
    scene.render.resolution_y=round(scene.render.resolution_x*config['height']/config['width'])
    scene.eevee.taa_render_samples=samples
    path.parent.mkdir(parents=True,exist_ok=True)
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    print('V3_RENDER',profile,frame,str(path),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--proofs',action='store_true')
    parser.add_argument('--frames',default='')
    parser.add_argument('--sequence',choices=['desktop','mobile'])
    parser.add_argument('--start',type=int,default=1)
    parser.add_argument('--end',type=int,default=MANIFEST['frameCount'])
    parser.add_argument('--width',type=int)
    parser.add_argument('--samples',type=int,default=24)
    parser.add_argument('--existing',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if not args.existing:
        setup()
        roof=architecture.build()
        architecture.furniture()
        blind=systems.build()
        motion.bake(roof,blind,MANIFEST)
        scene=bpy.context.scene
        scene['V3 source']='blender/house_v3.py'
        scene['V3 optional energy']='Storage and wallbox modelled but hidden pending service confirmation.'
        scene.render.resolution_x=1280
        scene.render.resolution_y=1100
        # Open the native file in material preview with the useful camera framing.
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type=='VIEW_3D':
                    area.spaces.active.region_3d.view_perspective='CAMERA'
        BLEND.parent.mkdir(parents=True,exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
        print('V3_SAVED',len(bpy.data.objects),'objects',flush=True)
    if args.proofs:
        frames=[round(c['rest']*180)+1 for c in MANIFEST['chapters']]+[29,37,145,174,181]
        if args.frames:
            frames=[int(f) for f in args.frames.split(',')]
        for frame in frames:
            render(frame,QA/'proofs'/f'frame-{frame:04d}.png',width=args.width,samples=args.samples)
    if args.sequence:
        if not 1<=args.start<=args.end<=MANIFEST['frameCount']:
            raise ValueError('Frame range must stay inside the manifest timeline')
        config=MANIFEST['profiles'][args.sequence]
        seen={}
        for frame in range(1,MANIFEST['frameCount']+1,config['step']):
            if args.start<=frame<=args.end:
                scene=bpy.context.scene
                scene.frame_set(frame)
                # Static holds reuse their exact previous render, including its
                # sampling pattern. All animated values are included below.
                values=[]
                for obj in bpy.data.objects:
                    if obj.animation_data:
                        values.extend(tuple(obj.location)+tuple(obj.scale))
                    if obj.type=='LIGHT':
                        values.append(obj.data.energy)
                    if obj.type=='CURVE':
                        values.extend((obj.data.bevel_depth,obj.data.bevel_factor_end))
                for mat in bpy.data.materials:
                    if mat.node_tree:
                        for node in mat.node_tree.nodes:
                            if node.type=='BSDF_PRINCIPLED':
                                values.append(node.inputs['Emission Strength'].default_value)
                            if node.name=='Shell visibility':
                                values.append(node.inputs[0].default_value)
                signature=tuple(round(value,6) for value in values)
                output=QA/'renders'/args.sequence/f'frame-{frame:04d}.png'
                if signature in seen:
                    shutil.copyfile(seen[signature],output)
                    print('V3_HOLD',args.sequence,frame,flush=True)
                else:
                    render(frame,output,args.sequence,args.width,args.samples)
                    seen[signature]=output
    bpy.context.scene.frame_set(1)


if __name__=='__main__':
    main()
