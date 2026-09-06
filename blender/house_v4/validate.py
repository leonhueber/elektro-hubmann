"""Read native scene geometry and write a compact model inventory."""
import json
import bpy
from mathutils import Vector
from . import core as c


def run():
    scene=bpy.context.scene
    roots={name:bpy.data.objects.get('V4 | '+name+' assembly') for name in ['EG','OG','Roof']}
    checks=[]
    def check(name,ok):checks.append({'check':name,'passed':bool(ok)})
    check('Independent V4 scene',scene.get('reference_revision')=='v4-reference-01')
    check('Three independently movable assemblies',all(roots.values()))
    modules=[o for o in scene.objects if o.name.startswith('PV | module ') and o.type=='EMPTY']
    roof_inverse=roots['Roof'].matrix_world.inverted() if roots['Roof'] else None
    panel_bounds=[]
    for module in modules:
        frame=next((o for o in module.children if o.name.startswith('PV | anodised perimeter frame')),None)
        if frame and roof_inverse is not None:
            points=[roof_inverse@frame.matrix_world@Vector(v) for v in frame.bound_box]
            panel_bounds.append((min(v.x for v in points),max(v.x for v in points),min(v.y for v in points),max(v.y for v in points)))
    on_roof=all(4.9<x0<x1<9.75 and .1<y0<y1<10.7 for x0,x1,y0,y1 in panel_bounds)
    separated=all(a[1]<=b[0] or b[1]<=a[0] or a[3]<=b[2] or b[3]<=a[2]
                  for i,a in enumerate(panel_bounds) for b in panel_bounds[i+1:])
    check('Ten separate modules inside the roof, parented to it',len(modules)==len(panel_bounds)==10
          and all(o.parent==roots['Roof'] for o in modules) and on_roof and separated)
    for name in ['Parents | double oak bed','Child front | oak single bed','Child rear | oak single bed']:
        bed=bpy.data.objects.get(name)
        check(name+' belongs to OG',bed is not None and bed.parent==roots['OG'])
    check('Two nine-riser stair flights',sum(o.name.startswith('U stair | lower riser') for o in scene.objects)==9
          and sum(o.name.startswith('U stair | upper riser') for o in scene.objects)==9)
    void_clear=True
    for o in scene.objects:
        if o.name.startswith('OG | slab with stair void'):
            points=[o.matrix_local@Vector(v) for v in o.bound_box]
            xmin,xmax=min(v.x for v in points),max(v.x for v in points)
            ymin,ymax=min(v.y for v in points),max(v.y for v in points)
            if xmin<6.299 and xmax>3.951 and ymin<10.349 and ymax>6.601:void_clear=False
    check('Upper slab leaves real U-stair void',void_clear)
    check('Eight perspective target cameras',sum(o.type=='CAMERA' and o.data.type=='PERSP' for o in scene.objects)==8)
    check('Every mesh has a native material',all(o.data.materials for o in scene.objects if o.type=='MESH'))
    images=[i for i in bpy.data.images if i.packed_file]
    check('Reference images and oak texture packed',len(images)>=9)
    check('Videosprechanlage modelled',bpy.data.objects.get('Entrance | optical lens') is not None)
    def world_z(name):
        o=bpy.data.objects[name]
        values=[(o.matrix_world@Vector(v)).z for v in o.bound_box]
        return min(values),max(values)
    ground=world_z('V4 | white cyclorama')[1]
    contacts=[world_z(name)[0] for name in ['Entrance | stone step','Terrace | stone base',
              'Entrance | right olive shrub | hollow ceramic pot']]
    deck=world_z('Terrace | oak decking')[1]
    left_pot=world_z('Terrace | left olive tree | hollow ceramic pot')[0]
    check('Podest, terrace and both pots have real ground contact',all(abs(z-ground)<.002 for z in contacts) and abs(left_pot-deck)<.002)
    ceiling=bpy.data.objects.get('Roof | attic floor and OG ceiling')
    check('OG ceiling belongs to lifting roof and meets the room walls',ceiling is not None and ceiling.parent==roots['Roof']
          and abs(world_z(ceiling.name)[0]-(roots['OG'].location.z+2.78))<.002)
    report={'reference':'v4-reference-01','scene':scene.name,'checks':checks,'allPassed':all(x['passed'] for x in checks),
            'objects':len(scene.objects),'meshes':sum(o.type=='MESH' for o in scene.objects),
            'vertices':sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),
            'rooms':sorted(set(o.get('room') for o in scene.objects if o.get('room'))),
            'packedImages':len(images),'animationStatus':'reference_views_only'}
    out=c.ROOT/'docs/version-g-qa/blender-v4/native-validation.json'
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('V4_NATIVE_VALIDATION',json.dumps(report),flush=True)
    if not report['allPassed']:raise RuntimeError('Native V4 validation failed; inspect native-validation.json.')
    return report
