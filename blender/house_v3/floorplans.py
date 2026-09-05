"""Render orthographic layout QA from the saved source without modifying it."""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
scene.frame_set(59)
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1200
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.film_transparent=False
scene.render.image_settings.file_format='PNG'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.background_type='WORLD'
scene.world.color=(1,1,1)
camera=bpy.data.objects['V3 Ground plan']
camera.data.ortho_scale=12.8
scene.camera=camera
initial={obj:obj.hide_render for obj in bpy.data.objects}
text_material=bpy.data.materials.new('QA layout labels')
text_material.diffuse_color=(.60,.012,.022,1)
out=ROOT/'docs/version-g-qa/blender-v3/floorplans'
out.mkdir(parents=True,exist_ok=True)
for floor,low,high,labels in [
    ('ground',-.5,3.23,[('WOHNEN',(-3.8,-2.8)),('TECHNIK',(-.4,-1.8)),('ESSEN',(2.5,-2.8)),('KUECHE',(2,2))]),
    ('upper',3.25,6.28,[('SCHLAFEN',(-4.3,-2.5)),('TREPPENKERN',(-2.1,-1.4)),('ARBEITEN',(1.4,-2.8)),('BAD',(1.4,2))]),
]:
    for obj,hidden in initial.items():
        obj.hide_render=hidden
        if obj.type not in ('MESH','CURVE','FONT'):
            continue
        bounds=[obj.matrix_world@Vector(corner) for corner in obj.bound_box]
        if min(v.z for v in bounds)>high or max(v.z for v in bounds)<low:
            obj.hide_render=True
        if any(c.name in ('V3_ROOF','V3_SHELL_FRONT','V3_SHELL_SIDE','V3_LIGHTING') for c in obj.users_collection):
            obj.hide_render=True
    created=[]
    for text,(x,y) in labels:
        data=bpy.data.curves.new('QA '+text,'FONT')
        data.body=text;data.size=.23;data.materials.append(text_material)
        obj=bpy.data.objects.new('QA '+text,data)
        scene.collection.objects.link(obj)
        obj.location=(x,y,high+.1)
        created.append(obj)
    scene.render.filepath=str(out/(floor+'.png'))
    bpy.ops.render.render(write_still=True)
    for obj in created:
        bpy.data.objects.remove(obj,do_unlink=True)
print('V3 floor-plan QA rendered; saved source unchanged')
