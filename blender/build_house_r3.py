"""Build a fresh R3 source once; use --existing to render an edited .blend.

blender -b --python-exit-code 1 --python blender/build_house_r3.py -- --views open
blender -b assets/3d/elektro-hubmann-house-v3-r3.blend --python-exit-code 1 --python blender/build_house_r3.py -- --existing --views plan,closed,open,lighting
"""
import argparse
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'blender'))
from house_r3 import core as c, architecture, interior, systems

BLEND=ROOT/'assets/3d/elektro-hubmann-house-v3-r3.blend'
OUT=ROOT/'docs/version-g-qa/blender-v3-r3'
VIEWS={
    'open':('Camera | Open R3',62,1400,1400),
    'plan':('Camera | Plan',62,1400,1450),
    'closed':('Camera | Exterior',1,1600,1300),
    'lighting':('Camera | Open R3',86,1400,1400),
    'smart-home':('Camera | Open R3',113,1400,1400),
    'technical':('Camera | Technical detail',62,1400,1100),
    'security':('Camera | Entrance detail',129,1200,1300),
    'photovoltaic':('Camera | Exterior',161,1600,1300),
    'opening':('Camera | Exterior',28,1200,1200),
    'closing':('Camera | Exterior',181,1600,1300),
    'mobile':('Camera | Open R3',62,390,460),
}


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    scene.unit_settings.length_unit='METERS'
    scene.render.engine='CYCLES'
    scene.cycles.samples=32
    scene.cycles.use_denoising=True
    scene.cycles.adaptive_threshold=.06
    scene.cycles.max_bounces=8
    scene.cycles.diffuse_bounces=2
    scene.cycles.glossy_bounces=3
    scene.cycles.transmission_bounces=6
    scene.cycles.transparent_max_bounces=48
    scene.render.threads_mode='FIXED'
    scene.render.threads=12
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGBA'
    scene.render.film_transparent=True
    scene.render.resolution_percentage=100
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=.05
    scene.render.fps=30
    scene.frame_start=1
    scene.frame_end=181
    scene.world=bpy.data.worlds.new('R3 warm studio world')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.79,.84,.89,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.32
    c.collection('00 Studio')
    c.palette()
    c.material('studio white',(.88,.875,.855),.87)
    c.cube('White studio floor',(5.7,5.4,-.455),(200,200,.06),'studio white',0).is_shadow_catcher=True
    c.area('Studio key',(-3,-4,14),(4,4,0),2000,9,(1,.93,.83))
    c.area('Studio fill',(14,1,11),(6,5,0),1100,8,(.86,.92,1))
    c.area('Studio back',(4,15,13),(5,6,0),2100,8,(1,.93,.82))
    c.area('Studio front soft fill',(4,-9,6),(5,4,1),400,7,(1,.95,.88))


def cameras():
    c.collection('15 Cameras')
    c.camera('Camera | Open R3',(7.25,-14.4,32.0),(5.7,4.65,0),16.3)
    c.camera('Camera | Plan',(5.7,4.6,28),(5.7,4.6,0),14.7)
    c.camera('Camera | Exterior',(20,-24,13),(5.7,4.6,1.2),18.8)
    c.camera('Camera | Technical detail',(5.0,-5.3,8.6),(9.25,.7,.75),6.5)
    c.camera('Camera | Entrance detail',(10,-10,6),(6.4,-.2,1.10),5.7)
    # A separate native animated camera is the future scroll/export source.
    cam=c.camera('Camera | Scroll',(20,-24,13),(5.7,4.6,1.2),18.8)
    for frame,pos,target,scale in [
        (1,(20,-24,13),(5.7,4.6,1.2),18.8),
        (12,(20,-24,13),(5.7,4.6,1.2),18.8),
        (52,(7.25,-14.4,32.0),(5.7,4.65,0),16.3),
        (88,(7.25,-14.4,32.0),(5.7,4.65,0),16.3),
        (117,(7.25,-14.4,32.0),(5.7,4.65,0),16.3),
        (131,(10,-10,6),(6.4,-.2,1.10),5.7),
        (146,(20,-24,13),(5.7,4.6,1.2),18.8),
        (181,(20,-24,13),(5.7,4.6,1.2),18.8)]:
        c.key(cam,'location',frame,pos)
        c.key(cam,'rotation_euler',frame,(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler())
        c.key(cam.data,'ortho_scale',frame,scale)
    for f,label in [(1,'01 PLANUNG'),(28,'02 DACH OEFFNET'),(62,'03 INSTALLATION'),(86,'04 BELEUCHTUNG'),(113,'05 SMART HOME'),(129,'06 SICHERHEIT'),(161,'07 PHOTOVOLTAIK'),(181,'08 ABSCHLUSS')]:
        bpy.context.scene.timeline_markers.new(label,frame=f)


def save():
    scene=bpy.context.scene
    scene['R3 brief']='Approved complete R3 floor plan, 12.0 x 11.4 m. Six rooms, 1.30 m corridor.'
    scene['R3 source']='blender/build_house_r3.py; no old geometry imported.'
    scene['R3 editing']='Native meshes, materials and keyframes. Edit this file; render with --existing. Rebuild only intentionally.'
    scene['R3 scope']='Fictional demonstration model. Schematic electrical routes, not construction documentation.'
    readme=ROOT/'blender/house_r3/README.md'
    if readme.exists():
        text=bpy.data.texts.get('R3 - README') or bpy.data.texts.new('R3 - README')
        text.clear()
        text.write(readme.read_text(encoding='utf-8'))
    scene.frame_set(62)
    scene.camera=bpy.data.objects['Camera | Open R3']
    scene.render.resolution_x=1400
    scene.render.resolution_y=1400
    for screen in bpy.data.screens:
        for a in screen.areas:
            if a.type=='VIEW_3D':
                a.spaces.active.region_3d.view_perspective='CAMERA'
                a.spaces.active.shading.type='MATERIAL'
                a.spaces.active.overlay.show_extras=False
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND),compress=True)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND),compress=True)
    print('R3_SAVED',str(BLEND),len(bpy.data.objects),'objects',flush=True)


def render(name,args):
    scene=bpy.context.scene
    camera,frame,width,height=VIEWS[name]
    scene.frame_set(frame)
    scene.camera=bpy.data.objects[camera]
    if args.width:
        height=round(height*args.width/width)
        width=args.width
    scene.render.resolution_x=width
    scene.render.resolution_y=height
    scene.cycles.samples=args.samples
    if args.eevee:
        scene.render.engine='BLENDER_EEVEE'
        scene.eevee.taa_render_samples=args.samples
        scene.eevee.use_raytracing=True
    else:
        scene.render.engine='CYCLES'
    scene.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('R3_RENDER',name,frame,str(OUT/(name+'.png')),flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--existing',action='store_true')
    p.add_argument('--rebuild',action='store_true',help='Explicitly replace the generated R3 source; discards manual edits to that file.')
    p.add_argument('--views',default='')
    p.add_argument('--samples',type=int,default=32)
    p.add_argument('--width',type=int)
    p.add_argument('--eevee',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if BLEND.exists() and not args.existing and not args.rebuild:
        p.error('R3 source already exists. Use --existing to render it, or --rebuild for an intentional replacement.')
    OUT.mkdir(parents=True,exist_ok=True)
    if not args.existing:
        setup()
        print('R3_BUILD: materials and studio ready',flush=True)
        architecture.build()
        print('R3_BUILD: measured structure ready',len(bpy.data.objects),flush=True)
        interior.build()
        print('R3_BUILD: furnished rooms ready',len(bpy.data.objects),flush=True)
        systems.build()
        print('R3_BUILD: systems and animation ready',len(bpy.data.objects),flush=True)
        cameras()
        save()
    for name in filter(None,args.views.split(',')):
        render(name,args)
    if args.existing:
        print('Existing source preserved: render-only run.',flush=True)


if __name__=='__main__':
    main()
