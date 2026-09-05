"""Read-only geometry/animation checks against R3 requirements in the saved scene."""
import json
import sys
import math
from pathlib import Path
import bpy
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/version-g-qa/blender-v3-r3/validation.json'
if '--detail' in sys.argv:
    OUT=ROOT/'docs/version-g-qa/blender-v3-r3/detail/validation.json'
scene=bpy.context.scene
checks=[]


def check(name,ok,detail):
    checks.append({'check':name,'pass':bool(ok),'detail':detail})


def descendants(root):
    return [o for o in root.children_recursive if o.type=='MESH']


def bounds(objects):
    pts=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]


def signature(frame):
    scene.frame_set(frame)
    values=[]
    for name in ['RIG | Roof lift','RIG | Bedroom blind','Living dining kitchen hinge','Camera | Scroll']:
        o=bpy.data.objects[name]
        values.extend(round(v,7) for row in o.matrix_world for v in row)
    for m in bpy.data.materials:
        if m.node_tree and 'Visibility' in m.node_tree.nodes:
            values.append(round(m.node_tree.nodes['Visibility'].inputs[0].default_value,7))
    return values


rooms=[o for o in bpy.data.objects if o.name.startswith('ROOM | ')]
check('Seven spaces: six rooms and corridor',len(rooms)==7,[o.name for o in rooms])
areas={o.name.replace('ROOM | ',''):o['clear_area_m2'] for o in rooms}
check('R3 clear room area',116.8<sum(areas.values())<117.2,areas)
corr=bpy.data.objects['ROOM | Corridor']['bounds_xy']
check('Corridor width 1.30 m',abs(corr[1]-corr[0]-1.30)<1e-6,list(corr))
doors=[o for o in bpy.data.objects if 'room_access' in o]
check('Six direct internal room entries plus front door',len(doors)==7,{o['room_access']:o['clear_width'] for o in doors})
check('Door clear widths at least 0.85 m',all(o['clear_width']>=.85-1e-6 for o in doors),{o.name:round(o['clear_width'],3) for o in doors})
windows=[o for o in bpy.data.objects if 'opening_width' in o]
check('Exterior window openings',len(windows)==9,[o.name for o in windows])
scene.frame_set(62)
bpy.context.view_layer.update()
furniture={
    'Parents double bed':'Parents bedroom','Parents wardrobe':'Parents bedroom',
    'Child single bed':'Child bedroom','Child wardrobe':'Child bedroom','Child desk':'Child bedroom',
    'Office desk':'Office guest','Guest sleeper sofa':'Office guest',
    'Living sectional':'Living dining kitchen','Washing machine':'Utility electrical','Dryer':'Utility electrical',
}
for name,room in furniture.items():
    o=bpy.data.objects.get(name)
    check(name+' exists',o is not None,room)
    if o:
        b=bounds(descendants(o))
        x0,x1,y0,y1=bpy.data.objects['ROOM | '+room]['bounds_xy']
        ok=b[0][0]>=x0-.03 and b[0][1]<=x1+.03 and b[1][0]>=y0-.03 and b[1][1]<=y1+.03
        check(name+' inside room envelope',ok,{'mesh_bounds':b,'room_bounds':[x0,x1,y0,y1]})
for name in ['Shower tray','Toilet ceramic bowl','Bathroom vanity','Electrical distribution assembly','Network rack assembly','PV inverter','KNX room controller','Video door station']:
    check(name+' present',name in bpy.data.objects,name)

# Independently check door sweeps against actual furnished obstacle bounds.
# Flooring, carpets, walls and door trim are intentionally not obstacles here.
blocker_names=list(furniture)+['Laundry tall cabinet','Bathroom vanity','Shower tray',
    'Toilet concealed cistern','Media sideboard','Electrical distribution assembly','Network rack assembly']
blocker_names += [o.name for o in bpy.data.objects if o.type=='EMPTY' and ('Dining chair' in o.name or 'desk chair' in o.name or 'swivel chair' in o.name)]
obstacles={}
for name in blocker_names:
    obj=bpy.data.objects[name]
    obstacles[name]=bounds([obj] if obj.type=='MESH' else descendants(obj))

def overlaps(poly,box):
    rect=[(box[0][0],box[1][0]),(box[0][1],box[1][0]),(box[0][1],box[1][1]),(box[0][0],box[1][1])]
    axes=[(1,0),(0,1)]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        axes.append((a[1]-b[1],b[0]-a[0]))
    for ax in axes:
        p=[x*ax[0]+y*ax[1] for x,y in poly]
        q=[x*ax[0]+y*ax[1] for x,y in rect]
        if max(p)<=min(q)+.002 or max(q)<=min(p)+.002:
            return False
    return True

for door in doors:
    name=door['room_access']
    if name=='Entrance':
        continue
    max_angle=83 if name in ('Living dining kitchen','Parents bedroom') else -83
    leaf=bpy.data.objects[name+' hinge']
    hit=[]
    for step in range(18):
        angle=math.radians(max_angle*step/17)
        transform=door.matrix_world@Matrix.Translation(leaf.location)@Matrix.Rotation(angle,4,'Z')
        width=door['clear_width']
        poly=[tuple((transform@Vector((x,y,.5)))[:2]) for x,y in [(0,-.0225),(width,-.0225),(width,.0225),(0,.0225)]]
        for obstacle,b in obstacles.items():
            if overlaps(poly,b):
                hit.append({'obstacle':obstacle,'angle':round(math.degrees(angle),1)})
    check(name+' door sweep clear of furniture',not hit,hit)
intrusions=[]
for name,b in obstacles.items():
    if b[0][1]>5.60+.005 and b[0][0]<6.90-.005 and b[1][1]>0 and b[1][0]<10.8:
        intrusions.append(name)
check('Furnished obstacles leave corridor clear',not intrusions,intrusions)
blind=bpy.data.objects['RIG | Bedroom blind']
scene.frame_set(62)
raised=blind.scale.z
scene.frame_set(113)
slats=[o for o in blind.children if o.type=='MESH']
check('Smart Home blind stays visible and moves',blind.scale.z>raised+.8 and len(slats)==29 and not any(o.hide_render for o in slats),{'raised_scale':raised,'lowered_scale':blind.scale.z,'slats':len(slats)})
pv=[o for o in bpy.data.objects if o.name.startswith('PV module ') and o.type=='EMPTY']
check('Eight PV modules grouped with roof',len(pv)==8 and all(o.parent.name=='RIG | Roof lift' for o in pv),[o.name for o in pv])
roof=bpy.data.objects['RIG | Roof lift']
scene.frame_set(1)
start=roof.location.copy()
scene.frame_set(28)
check('Roof lifts as one group',roof.location.z>.8,float(roof.location.z))
scene.frame_set(181)
check('Roof returns to exact seat',(roof.location-start).length<1e-6,list(roof.location))
for group in ['shell','roof']:
    mats=[m for m in bpy.data.materials if m.name.endswith(' | '+group)]
    for frame,expected in [(1,1),(62,0),(181,1)]:
        scene.frame_set(frame)
        vals=[m.node_tree.nodes['Visibility'].inputs[0].default_value for m in mats]
        check(group+' visibility frame '+str(frame),bool(vals) and all(abs(v-expected)<1e-6 for v in vals),{'materials':len(vals),'min':min(vals),'max':max(vals)})
for frame in [1,28,43,62,86,113,129,146,161,181]:
    forward=signature(frame)
    scene.frame_set(181)
    backward=signature(frame)
    check('Reversible evaluation frame '+str(frame),forward==backward,'Roof, doors, blind, camera and material visibility')
check('No external linked libraries',len(bpy.data.libraries)==0,len(bpy.data.libraries))
images=[i for i in bpy.data.images if i.source=='FILE']
check('Texture assets packed',all(i.packed_file is not None for i in images),[i.name for i in images])
if '--detail' in sys.argv:
    leaves=[o for o in bpy.data.objects if o.type=='MESH' and ' leaf lower' in o.name]
    check('Refinement preserves all seven solid door leaves',len(leaves)==7 and all(len(o.data.vertices)==8 for o in leaves),[o.name for o in leaves])
    runners=[o for o in bpy.data.objects if o.type=='MESH' and 'textured bed runner' in o.name]
    check('Both bedrooms have modelled draped linen',len(runners)==2 and all(len(o.data.vertices)>3000 for o in runners),[o.name for o in runners])
    check('Refined source retains its architectural baseline',bool(scene.get('R3 detail source')),scene.get('R3 detail source'))
scene.frame_set(62)
OUT.write_text(json.dumps({'scene':bpy.data.filepath,'passed':all(v['pass'] for v in checks),'checks':checks},indent=2),encoding='utf-8')
for v in checks:
    print(('PASS' if v['pass'] else 'FAIL'),v['check'],v['detail'],flush=True)
if not all(v['pass'] for v in checks):
    raise RuntimeError('R3 geometry validation failed; see '+str(OUT))
