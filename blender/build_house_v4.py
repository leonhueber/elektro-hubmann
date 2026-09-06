"""Build and inspect the native V4 scene, independently of the active R3 website.

Blender Python console:
    import sys; sys.path.insert(0, '<repo>/blender'); import build_house_v4; build_house_v4.build()
CLI:
    blender -b --python-exit-code 1 --python blender/build_house_v4.py -- --views plan,installation
    blender -b assets/3d/elektro-hubmann-house-v4.blend --python blender/build_house_v4.py -- --existing --views all
"""
import argparse
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'blender'))
from house_v4 import core as c, architecture

BLEND=ROOT/'assets/3d/elektro-hubmann-house-v4.blend'
OUT=ROOT/'docs/version-g-qa/blender-v4'
POSES={
    'plan':('01-planung',(23,-27,8.3),(4.8,4.5,4.3),78),
    'opening':('02-oeffnung',(24,-32,26),(4.8,5.0,7.8),70),
    'installation':('03-installation',(15.6,-26.6,40.15),(4.8,5.2,.7),120),
    'lighting':('04-beleuchtung',(15.6,-26.6,40.15),(4.8,5.2,.7),120),
    'smart-home':('05-smart-home',(15.6,-26.6,43.15),(4.8,5.2,3.7),120),
    'security':('06-sicherheit',(7.7,-8.7,3.4),(6.0,.1,1.4),74),
    'photovoltaic':('07-photovoltaik',(23,-23,25),(4.8,4.7,4.7),70),
    'closing':('08-abschluss',(23,-27,8.3),(4.8,4.5,4.3),78),
}


def setup():
    scene=bpy.data.scenes.new('V4 | Reference house')
    if bpy.context.window:bpy.context.window.scene=scene
    else:raise RuntimeError('Blender window context is required to select the new scene.')
    scene.unit_settings.system='METRIC'
    scene.unit_settings.length_unit='METERS'
    scene.render.engine='CYCLES'
    scene.cycles.samples=64
    scene.cycles.use_denoising=True
    scene.cycles.adaptive_threshold=.035
    scene.cycles.max_bounces=10
    scene.cycles.diffuse_bounces=4
    scene.cycles.glossy_bounces=4
    scene.cycles.transmission_bounces=8
    scene.cycles.transparent_max_bounces=24
    scene.render.threads_mode='FIXED';scene.render.threads=12
    scene.render.resolution_x=1400;scene.render.resolution_y=1400
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=0
    scene.render.film_transparent=False
    scene.world=bpy.data.worlds.new('V4 | white studio world')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(1,1,1,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
    scene.render.fps=60;scene.frame_end=1441
    c.collection('V4 | 90 Studio')
    c.palette()
    c.box('V4 | white cyclorama',(4.8,5.4,-.25),(200,200,.1),'studio',0)
    c.area('V4 | large daylight key',(-7,-9,19),(4.8,4,1),3000,9,(1,.94,.84))
    c.area('V4 | soft sky fill',(17,-1,15),(4.8,5,3),1000,10,(.91,.96,1))
    c.area('V4 | rear daylight',(1,17,17),(4.8,6,2),1600,9,(1,.96,.87))
    studio_composite(scene)
    return scene


def studio_composite(scene):
    """Native Blender 5 compositor: white surround with a soft contact shadow."""
    scene.render.film_transparent=True
    bpy.data.objects['V4 | white cyclorama'].is_shadow_catcher=True
    tree=bpy.data.node_groups.new('V4 | white studio composite','CompositorNodeTree')
    tree.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
    render=tree.nodes.new('CompositorNodeRLayers');render.scene=scene
    over=tree.nodes.new('CompositorNodeAlphaOver')
    over.inputs['Factor'].default_value=1
    over.inputs['Background'].default_value=(16,16,16,1)
    output=tree.nodes.new('NodeGroupOutput')
    tree.links.new(render.outputs['Image'],over.inputs['Foreground'])
    tree.links.new(over.outputs[0],output.inputs['Image'])
    scene.compositing_node_group=tree


def cameras():
    c.collection('V4 | 91 Reference cameras')
    for i,(name,(label,pos,target,lens)) in enumerate(POSES.items()):
        data=bpy.data.cameras.new('V4 | '+label)
        data.type='PERSP';data.lens=lens;data.clip_end=250
        obj=c.register(bpy.data.objects.new('V4 | '+label,data))
        obj.location=pos;obj.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
        obj['target']=target;obj['reference_image']='docs/mockups/house-v4/states/'+label+'.png'
        marker=bpy.context.scene.timeline_markers.new(label,frame=[1,303,505,678,908,1139,1311,1441][i])
        marker.camera=obj


def reference_images():
    col=c.collection('V4 | 99 Selected reference images')
    for i,(name,(label,*_)) in enumerate(POSES.items()):
        path=ROOT/'docs/mockups/house-v4/states'/f'{label}.png'
        img=bpy.data.images.load(str(path),check_existing=True);img.pack()
        o=c.empty('REFERENCE | '+label,(-20,i*9,4))
        o.empty_display_type='IMAGE';o.data=img;o.empty_display_size=8
        o.rotation_euler.x=math.pi/2
        o.hide_render=True
    col.hide_viewport=True;col.hide_render=True
    text=bpy.data.texts.new('V4_README')
    text.write('V4 | Selected reference: v4-reference-01\nTwo complete storeys, 9.6 x 10.8 m, 35 degree gable roof.\n'
               'Built with native mesh geometry; oak texture and eight references packed.\n'
               'Use build_house_v4.set_view(name) for plan/opening/installation/lighting/smart-home/security/photovoltaic/closing.\n'
               'Cameras are reference poses. The final continuous scroll camera is a subsequent animation task.\n'
               'Reference images are retained in the hidden collection 99.\n')


def set_view(name):
    scene=bpy.context.scene
    scene.frame_set([1,303,505,678,908,1139,1311,1441][list(POSES).index(name)])
    for col in bpy.data.collections:
        if col.name.startswith('V4 | EG '):
            hide=name=='smart-home' and col.name!='V4 | EG 04 U stair'
            col.hide_render=hide;col.hide_viewport=hide
    bpy.data.objects['V4 | white cyclorama'].location.z=-.25
    for key in ['EG','OG','Roof']:
        obj=bpy.data.objects.get('V4 | '+key+' assembly')
        if obj:obj.location.z={'EG':0,'OG':3,'Roof':6}[key]
    cut=name in ['opening','installation','lighting','smart-home']
    for obj in scene.objects:
        if obj.get('og_stairwell_context'):
            obj.hide_render=name!='smart-home';obj.hide_set(name!='smart-home')
        if obj.get('cutaway_upper'):
            obj.hide_render=cut;obj.hide_set(cut)
        if obj.get('interior_light'):
            obj.data.energy=obj.get('nominal_watts',20)*(1.8 if name=='closing' else 1 if name in ['lighting','security'] else .50 if name=='plan' else .20)
        if obj.get('installation_route'):
            obj.hide_render=name!='installation';obj.hide_set(name!='installation')
        if obj.get('smart_blind'):
            obj.hide_render=name!='smart-home';obj.hide_set(name!='smart-home')
    if name=='opening':
        bpy.data.objects['V4 | OG assembly'].location.z=7
        bpy.data.objects['V4 | Roof assembly'].location.z=14
    elif name in ['installation','lighting']:
        bpy.data.objects['V4 | OG assembly'].location.z=30
        bpy.data.objects['V4 | Roof assembly'].location.z=40
    elif name=='smart-home':
        bpy.data.objects['V4 | Roof assembly'].location.z=40
    scene.camera=bpy.data.objects['V4 | '+POSES[name][0]]
    scene['active_reference_view']=name
    bpy.context.view_layer.update()
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA'
                area.spaces.active.overlay.show_overlays=False
                area.spaces.active.shading.color_type='MATERIAL'


def build(stage='full'):
    OUT.mkdir(parents=True,exist_ok=True)
    # Rebuild only generated V4 data. Other scenes and user objects are untouched.
    for obj in list(bpy.data.objects):
        if obj.get('reference_revision')=='v4-reference-01':
            bpy.data.objects.remove(obj,do_unlink=True)
    for col in list(bpy.data.collections):
        if col.name.startswith('V4 | ') and not col.objects:
            bpy.data.collections.remove(col)
    c.M.clear()
    c.RNG.seed(40609)
    c.PARENT=None
    scene=setup()
    for old in list(bpy.data.scenes):
        if old!=scene and old.name.startswith('V4 | Reference house') and not old.objects:
            bpy.data.scenes.remove(old)
    roots=architecture.build()
    architecture.isolated_stairwell_context(roots['EG'])
    if stage=='full':
        from house_v4 import rooms
        rooms.build(roots)
    cameras();reference_images();set_view('plan')
    scene['reference_revision']='v4-reference-01'
    scene['model_revision']='v4-build-02'
    scene['build_stage']=stage
    from house_v4 import ui
    ui.register()
    launcher=bpy.data.texts.get('RUN_V4_SIDEBAR') or bpy.data.texts.new('RUN_V4_SIDEBAR')
    launcher.clear()
    launcher.write("import sys\nsys.path.insert(0, "+repr(str(ROOT/'blender'))+")\nfrom house_v4 import ui\nui.register()\n")
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND),compress=True)
    report={'file':str(BLEND),'stage':stage,'objects':len(scene.objects),'meshes':sum(o.type=='MESH' for o in scene.objects),
            'vertices':sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),'reference':'v4-reference-01',
            'modelRevision':scene['model_revision']}
    (OUT/'build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('V4_BUILD_COMPLETE',json.dumps(report),flush=True)
    return scene


def render(names,size=1400,samples=64):
    OUT.mkdir(parents=True,exist_ok=True)
    scene=bpy.context.scene
    scene.render.resolution_x=size;scene.render.resolution_y=size
    scene.cycles.samples=samples
    for name in names:
        set_view(name)
        scene.render.filepath=str(OUT/(POSES[name][0]+'.png'))
        bpy.ops.render.render(write_still=True)
        print('V4_RENDER_COMPLETE',name,flush=True)
    set_view('plan')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--existing',action='store_true')
    p.add_argument('--stage',default='full',choices=['full','architecture'])
    p.add_argument('--views',default='')
    p.add_argument('--size',type=int,default=1400)
    p.add_argument('--samples',type=int,default=64)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if not args.existing:build(args.stage)
    if args.views:render(list(POSES) if args.views=='all' else args.views.split(','),args.size,args.samples)
