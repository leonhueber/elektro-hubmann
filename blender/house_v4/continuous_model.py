"""Build a detailed, continuously animated sibling of the existing native B house.

Run with the existing smarthome-r1-web.blend and --prepare. Sources are never
overwritten. New devices and the wallbox are native Blender geometry.
"""
import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'blender'))
from house_v4 import core as c
from house_v4.continuous_motion import REVISION, FRAME_COUNT, STEP, CHAPTERS, state, schedule
from house_v4.web import key, fade_group

SOURCE = ROOT/'assets/3d/elektro-hubmann-house-v4-smarthome-r1-web.blend'
DEST = ROOT/'assets/3d/elektro-hubmann-house-v4-continuous-r1-web.blend'
OUT = ROOT/'docs/version-g-qa/blender-v4-continuous-r1'
NEW = []


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def materials():
    c.M.clear()
    for mat in bpy.data.materials:
        name = mat.name.removeprefix('V4 | ')
        if mat.name.startswith('V4 | ') and ' | ' not in name:
            c.M.setdefault(re.sub(r'\.\d{3}$', '', name), mat)
    c.material('tour rubber', (.012, .015, .017), .72, .05, .0004)
    c.material('tour reader glass', (.015, .027, .035), .13, .42)
    c.material('tour pavement', (.37, .385, .37), .82, 0, .0015)
    c.material('tour route', (.48, .01, .025), .4, .15)
    c.material('tour blue lens', (.011, .037, .07), .09, .45)
    for name, color in [('tour status', (.06, .6, .38)), ('tour led', (.7, .75, .8)), ('tour tail', (.6, .012, .025))]:
        mat = c.material(name, color, .24)
        shader = mat.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Emission Color'].default_value = (*color, 1)
        shader.inputs['Emission Strength'].default_value = 1.7
    c.M['tour tail'].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.12
    for name in ['tour controller feedback','tour camera feedback']:
        mat=c.M['tour status'].copy();mat.name='V4 | '+name;c.M[name]=mat
    for name, strength in [('tour solar path', .25), ('tour solar pulse', 3.)]:
        mat = c.material(name, (.9, .33, .045), .35, .1)
        shader = mat.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Emission Color'].default_value = (.9, .33, .045, 1)
        shader.inputs['Emission Strength'].default_value = strength
    for mat in bpy.data.materials:
        if mat.name.startswith('V4 | plaster'):
            for node in mat.node_tree.nodes:
                if node.type == 'BUMP':
                    node.inputs['Distance'].default_value = min(node.inputs['Distance'].default_value, .0015)
        if mat.name.startswith('V4 | pv') and 'grid' not in mat.name:
            shader = mat.node_tree.nodes.get('Principled BSDF')
            if shader:
                shader.inputs['Roughness'].default_value = .29
                shader.inputs['Metallic'].default_value = .15
                shader.inputs['Specular IOR Level'].default_value = .3


def smooth_curve(name, coords, radius, mat, parent=None):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 20
    curve.bevel_depth, curve.bevel_resolution = radius, 5
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(coords)-1)
    for point, co in zip(spline.bezier_points, coords):
        point.co = co
        point.handle_left_type = point.handle_right_type = 'AUTO'
    return c.register(bpy.data.objects.new(name, curve), mat, parent)


def wallbox_and_solar():
    c.collection('V4 | Continuous 10 Energy', None, 'Exterior | EV bay')
    before = set(bpy.context.scene.objects)
    # Thin individual pavers retain material scale beside the existing house.
    for ix in range(3):
        for iy in range(12):
            c.box('Tour | bay paver', (9.78+(ix+.5)*.56, .10+(iy+.5)*.57, -.13),
                  (.552, .562, .10), 'tour pavement', .004)
    c.box('Tour | bay outer kerb', (11.51, 3.52, -.08), (.10, 6.90, .18), 'stone', .009)
    wall = c.empty('Tour | wallbox', (9.665, 2.3, 1.35))
    wall['mounting_height_m'] = 1.35
    c.box('Tour | wallbox mounting gasket', (.028, 0, 0), (.052, .274, .43), 'tour rubber', .024, wall)
    c.box('Tour | wallbox metal shell', (.10, 0, 0), (.16, .32, .48), 'charcoal', .035, wall)
    c.box('Tour | wallbox face seal', (.182, 0, 0), (.008, .291, .445), 'black', .023, wall)
    c.box('Tour | wallbox satin face', (.189, 0, 0), (.012, .277, .429), 'charcoal', .024, wall)
    c.box('Tour | charge status diffuser', (.199, 0, .078), (.004, .132, .009), 'charcoal', .002, wall)
    for i in range(8):
        lamp=c.box('Tour | charging progress LED', (.202, -.059+i*.017, .078),
                   (.004, .012, .009), 'tour status', .002, wall)
        lamp['charge_segment']=i
    c.box('Tour | reader glass', (.2, 0, -.005), (.004, .096, .082), 'tour reader glass', .005, wall)
    for y in [-.12, .12]:
        for z in [-.19, .19]:
            c.cylinder('Tour | wallbox fixing', (.199, y, z), .004, .005, 'steel', wall, (0, math.pi/2, 0), 16)
    for i in range(7):
        c.box('Tour | lower ventilation slot', (.202, -.063+i*.021, -.146),
              (.002, .009, .018), 'black', .002, wall)
    c.cylinder('Tour | cable gland', (.13, 0, -.262), .023, .06, 'tour rubber', wall)
    # Inverter lives inside the original front-right HWR, not upstairs.
    c.collection('V4 | EG 25 Continuous energy plant', bpy.data.objects['V4 | EG assembly'], 'EG | HWR')
    inverter = c.box('Tour | solar inverter', (9.25, 2.72, 1.40), (.18, .45, .61), 'white appliance', .035)
    inverter['continuous_group'] = 'eg'
    c.box('Tour | inverter face', (9.15, 2.72, 1.40), (.01, .395, .54), 'ceramic', .025)['continuous_group'] = 'eg'
    for i in range(10):
        c.box('Tour | inverter heat sink', (9.34, 2.53+i*.039, 1.4), (.06, .012, .5), 'steel', .003)['continuous_group'] = 'eg'
    c.box('Tour | inverter status', (9.139, 2.72, 1.39), (.004, .072, .012), 'tour status', .002)['continuous_group'] = 'eg'
    c.collection('V4 | Continuous 10 Energy', None, 'Exterior | EV bay')
    c.box('Tour | connector wall holster',(.085,.33,.055),(.11,.095,.14),'charcoal',.018,wall)
    c.cylinder('Tour | docked connector',(.16,.33,.0),.038,.17,'charcoal',wall,vertices=40)
    for j in range(4):
        c.cylinder('Tour | docked connector grip',(.16,.33,-.045-j*.012),.040,.006,'tour rubber',wall,vertices=40)
    smooth_curve('Tour | stowed charging cable',
                 [(.13,0,-.262),(.20,0,-.65),(.22,.14,-.76),(.22,.36,-.66),(.18,.36,-.31),(.16,.33,-.078)],
                 .014,'tour rubber',wall)
    # Explicitly schematic, dimensioned path laid just outside the real surface.
    # The path follows the roof slope and east wall to the actual wallbox face.
    fade_group('energy')
    points=[(6.2,4.2,8.66),(7.7,4.2,7.61),(9.79,4.2,6.16),
            (9.89,4.2,5.70),(9.89,4.2,1.428),(9.87,2.405,1.428)]
    for name,radius,mat in [('solar route',.005,'tour solar path'),('solar pulse',.009,'tour solar pulse')]:
        path=smooth_curve('Tour | '+name,points,radius,mat)
        for point in path.data.splines[0].bezier_points:
            point.handle_left_type=point.handle_right_type='VECTOR'
        path['continuous_group']='energy'
        path['energy_path']=name
    NEW.extend(o for o in bpy.context.scene.objects if o not in before)
    return wall


def retain_balcony_access():
    """Keep the selected timber door and blind hardware visible in the cutaway."""
    copies={}
    for obj in bpy.context.scene.objects:
        if not (obj.name.startswith('OG | balcony door') or
                obj.name.startswith('Exterior | balcony door') or
                obj.name.startswith('Smart A | blind headrail')):
            continue
        obj['continuous_group']='always'
        obj['cutaway_upper']=False
        for slot in obj.material_slots:
            original=slot.material
            if not original:
                continue
            if original.name not in copies:
                mat=original.copy()
                mat.name=original.name+' | retained balcony'
                for mix in list(mat.node_tree.nodes):
                    if mix.type!='MIX_SHADER' or not mix.inputs[0].links:
                        continue
                    control=mix.inputs[0].links[0].from_node
                    if control.type=='GROUP' and control.node_tree.name.startswith('V4 web visibility | '):
                        shader=mix.inputs[2].links[0].from_socket
                        for link in list(mix.outputs[0].links):
                            mat.node_tree.links.new(shader,link.to_socket)
                        mat.node_tree.nodes.remove(mix)
                copies[original.name]=mat
            slot.link='OBJECT';slot.material=copies[original.name]


def details_and_routes():
    scene=bpy.context.scene
    before=set(scene.objects)
    og=bpy.data.objects['V4 | OG assembly']
    c.collection('V4 | OG 26 Continuous shading',og,'OG | Parents')
    old=sorted((o for o in scene.objects if o.get('smart_blind')),key=lambda o:o.name)
    for i in range(15):
        duplicate=old[i].copy()
        duplicate.data=old[i].data.copy()
        duplicate.name=f'Tour | blind lamella {i+15:02d}'
        duplicate.animation_data_clear()
        c.COL.objects.link(duplicate)
    slats=old+[o for o in c.COL.objects if o.get('smart_blind')]
    # Avoid double inclusion if a Blender collection is reused.
    slats=list(dict.fromkeys(slats))
    assert len(slats)==30,len(slats)
    for i,o in enumerate(slats):
        o['continuous_blind_index']=i
        o['smart_blind']=True
        o['continuous_group']='blind'
    for x in [.99,3.51]:
        c.box('Tour | full height blind guide',(x,-.009,1.28),(.027,.032,2.40),'charcoal',.004)['continuous_group']='always'
    lower=c.box('Tour | blind weighted lower rail',(2.25,.005,2.03),(2.49,.08,.046),'charcoal',.008)
    lower['continuous_group']='blind'
    feedback=c.box('Tour | controller scene indicator',(4.17,5.046,1.188),(.104,.002,.006),'tour controller feedback',.001)
    feedback['continuous_group']='controller'
    for obj in scene.objects:
        if obj.name.startswith('Smart A | blind guide'):
            obj.hide_render=True
            obj['continuous_group']='never'
        if obj.type=='FONT' and '21 degree' in obj.name:
            obj.data.body='Szene'
            obj.data.size=.027
    # A real optical lens surface and a physical bell ring, not a magnifier UI.
    c.collection('V4 | EG 26 Continuous entrance details',bpy.data.objects['V4 | EG assembly'],'EG | Entrance')
    c.cylinder('Tour | camera coated lens',(6.83,-.063,1.49),.021,.002,'tour blue lens',rotation=(math.pi/2,0,0),vertices=64)
    for r in [.025,.0275]:
        points=[(6.83+r*math.cos(i*math.tau/64),-.062,1.49+r*math.sin(i*math.tau/64)) for i in range(64)]
        c.tube('Tour | camera focus bezel',points,.001,'steel',cyclic=True)
    for x in [6.783,6.877]:
        for z in [1.22,1.54]:
            c.cylinder('Tour | intercom face screw',(x,-.043,z),.003,.003,'steel',rotation=(math.pi/2,0,0),vertices=16)
    for i in range(5):
        c.box('Tour | intercom microphone slot',(6.808+i*.011,-.040,1.365),(.005,.003,.009),'black',.001)
    ring=c.tube('Tour | camera status ring',[(6.83+.023*math.cos(i*math.tau/64),-.044,1.26+.023*math.sin(i*math.tau/64)) for i in range(64)],.0018,'tour status',cyclic=True)
    c.cylinder('Tour | camera activity LED',(6.86,-.061,1.528),.0028,.002,'tour camera feedback',rotation=(math.pi/2,0,0),vertices=20)
    # Coarse, deliberately schematic routes span the two lifted inhabited levels.
    for level,parent,z in [('EG',bpy.data.objects['V4 | EG assembly'],.18),('OG',og,.18)]:
        c.collection('V4 | '+level+' 27 Continuous wiring',parent,level+' | Routes')
        routes=[[(7.12,2.85,z),(6.0,2.85,z),(6.,5.3,z),(1.0,5.3,z),(1.0,2.2,z)],
                [(6.,5.3,z),(6.,8.9,z),(8.9,8.9,z)],[(6.,5.3,z),(6.,1.0,z),(8.9,1.0,z)]]
        for i,points in enumerate(routes):
            route=c.tube(f'Tour | {level} schematic wiring {i}',points,.016,'tour route')
            route['installation_route']=True
            route['continuous_group']='route'
    NEW.extend(o for o in scene.objects if o not in before)
    return slats,lower,ring


def visibility_for(obj):
    if obj.get('continuous_group'):
        return obj['continuous_group']
    if obj.get('smarthome_revision'):
        return 'controller'
    if obj.get('smart_blind'):
        return 'blind'
    if obj.get('installation_route'):
        return 'route'
    if obj.get('og_stairwell_context'):
        return 'context'
    eg=any(col.name.startswith('V4 | EG ') and col.name!='V4 | EG 04 U stair' for col in obj.users_collection)
    if obj.get('cutaway_upper'):
        return 'eg_cut' if eg else 'cut'
    return 'eg' if eg else None


def attach_fades(objects):
    copied={}
    for obj in objects:
        group=visibility_for(obj)
        if group not in ['eg','route','controller','blind','energy'] or obj.type not in ['MESH','CURVE','FONT']:
            continue
        groupname='smarthome A devices' if group=='controller' else group
        fade=bpy.data.node_groups.get('V4 web visibility | '+groupname)
        if not fade:
            continue
        for slot in obj.material_slots:
            original=slot.material
            if not original:
                continue
            # Copied original slats already have their native blind visibility.
            if any(n.type=='GROUP' and n.node_tree==fade for n in original.node_tree.nodes):
                continue
            ident=(original.name,group)
            if ident not in copied:
                material=original.copy()
                material.name=original.name+' | continuous '+group
                tree=material.node_tree
                output=next(n for n in tree.nodes if n.type=='OUTPUT_MATERIAL')
                prior=output.inputs['Surface'].links[0].from_socket
                transparent=tree.nodes.new('ShaderNodeBsdfTransparent')
                mix=tree.nodes.new('ShaderNodeMixShader')
                control=tree.nodes.new('ShaderNodeGroup');control.node_tree=fade
                tree.links.new(control.outputs[0],mix.inputs[0])
                tree.links.new(transparent.outputs[0],mix.inputs[1])
                tree.links.new(prior,mix.inputs[2])
                tree.links.new(mix.outputs[0],output.inputs['Surface'])
                copied[ident]=material
            slot.link='OBJECT'
            slot.material=copied[ident]


def orient_bounds(scene,points):
    pts=[world_to_camera_view(scene,scene.camera,Vector(p)) for p in points]
    xs=[p.x for p in pts];ys=[1-p.y for p in pts]
    margin=.012
    x=max(0,min(xs)-margin);y=max(0,min(ys)-margin)
    return {'x':round(x,6),'y':round(y,6),'width':round(min(1,max(xs)+margin)-x,6),'height':round(min(1,max(ys)+margin)-y,6)}


def prepare():
    if Path(bpy.data.filepath).resolve()!=SOURCE.resolve():
        raise RuntimeError('Load the unchanged native smarthome-r1-web source.')
    scene=bpy.context.scene
    scene.frame_set(1)
    materials()
    wallbox_and_solar()
    slats,lower,ring=details_and_routes()
    retain_balcony_access()
    attach_fades(NEW)
    # A fixed, physical directional key makes blind shadows visible.
    c.collection('V4 | Continuous 90 Daylight')
    sun_data=bpy.data.lights.new('Tour | directional daylight','SUN')
    sun_data.energy=1.05
    sun_data.angle=math.radians(.8)
    sun=c.register(bpy.data.objects.new(sun_data.name,sun_data))
    sun.rotation_euler=Vector((-.25,1,-.62)).to_track_quat('-Z','Y').to_euler()
    for obj in scene.objects:
        obj.animation_data_clear()
        if obj.type in ['CAMERA','LIGHT']:
            obj.data.animation_data_clear()
        obj.hide_set(False)
    for group in bpy.data.node_groups:
        group.animation_data_clear()
    scene.animation_data_clear()
    cam=bpy.data.objects['V4 | Continuous scroll camera']
    target=bpy.data.objects['V4 | Continuous look target']
    cam.rotation_mode='QUATERNION'
    scene.camera=cam
    cam.data.clip_start=.04
    cam.data.clip_end=250
    scene.render.film_transparent=False
    for marker in scene.timeline_markers:
        marker.camera=None
    groups={}
    for group in bpy.data.node_groups:
        if group.name.startswith('V4 web visibility | '):
            value=next((n.outputs[0] for n in group.nodes if n.type=='VALUE'),None)
            if value:
                groups[group.name.split(' | ',1)[1]]=value
    objects=[(o,visibility_for(o)) for o in scene.objects]
    lights=[(o,o.get('nominal_watts',20)) for o in scene.objects if o.get('interior_light')]
    routes=[o for o in scene.objects if o.get('installation_route') and o.type=='CURVE']
    energy_paths=[o for o in scene.objects if o.get('energy_path')]
    charge_lamps=[o for o in scene.objects if 'charge_segment' in o]
    hidden={}
    records=[]
    for frame in range(1,FRAME_COUNT+1,STEP):
        s=state((frame-1)/(FRAME_COUNT-1))
        key(cam,'location',frame,s['camera'])
        key(cam,'rotation_quaternion',frame,(Vector(s['target'])-Vector(s['camera'])).to_track_quat('-Z','Y'))
        key(cam.data,'lens',frame,s['lens'])
        key(target,'location',frame,s['target'])
        for name,prop in [('OG','og'),('Roof','roof')]:
            key(bpy.data.objects['V4 | '+name+' assembly'],'location',frame,(0,0,s[prop]))
        vis={'cut':s['cut'],'eg':s['eg'],'eg_cut':s['eg']*s['cut'],'route':s['route'],
             'context':1-s['eg'],'blind':s['blind'],'controller':s['controller'],'never':0,'energy':s['energy']}
        for name,socket in groups.items():
            key(socket,'default_value',frame,vis['controller' if name=='smarthome A devices' else name])
        for obj,group in objects:
            invisible=group is not None and vis.get(group,1)<.002
            if hidden.get(obj.name)!=invisible:
                key(obj,'hide_render',frame,invisible)
                key(obj,'hide_viewport',frame,invisible)
                hidden[obj.name]=invisible
        for i,obj in enumerate(slats):
            key(obj,'location',frame,(2.25,.025,2.44-i*.014-(i/29)*s['blind_drop']))
            key(obj,'rotation_euler',frame,(s['tilt'],0,0))
        key(lower,'location',frame,(2.25,.025,2.44-29*.014-s['blind_drop']-.03))
        for route in routes:
            key(route.data,'bevel_factor_end',frame,max(.001,s['route_trace']))
        for path in energy_paths:
            end=max(.001,s['energy_flow'])
            key(path.data,'bevel_factor_end',frame,end)
            key(path.data,'bevel_factor_start',frame,max(0,end-.14) if path['energy_path']=='solar pulse' else 0.)
        for lamp in charge_lamps:
            visible=s['charge']*8>lamp['charge_segment']
            key(lamp,'hide_render',frame,not visible)
            key(lamp,'hide_viewport',frame,not visible)
        for light,nominal in lights:
            key(light.data,'energy',frame,nominal)
        for mat_name,value in [('tour controller feedback',max(0,min(1,((frame-1)/(FRAME_COUNT-1)-.425)/.025))),
                               ('tour camera feedback',s['security_focus'])]:
            # Follow all visibility copies as well as the retained source material.
            for mat in bpy.data.materials:
                if mat.name.startswith('V4 | '+mat_name):
                    shader=mat.node_tree.nodes.get('Principled BSDF')
                    key(shader.inputs['Emission Strength'],'default_value',frame,.06+2.2*value)
        button=bpy.data.objects.get('Smart A | controller glass')
        if button:
            key(button,'location',frame,(4.17,5.054+s['controller_press']*.0015,1.22))
        records.append({'frame':frame,**s})
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    bag=strip.channelbag(slot)
                    if bag:
                        for curve in bag.fcurves:
                            for point in curve.keyframe_points:
                                point.interpolation='CONSTANT' if curve.data_path in ['hide_render','hide_viewport'] else 'LINEAR'
    scene.frame_start,scene.frame_end,scene.render.fps=1,FRAME_COUNT,60
    scene.render.engine='CYCLES'
    scene.cycles.samples=96
    scene.cycles.use_denoising=True
    scene.cycles.use_adaptive_sampling=True
    scene.cycles.adaptive_threshold=.025
    scene.cycles.adaptive_min_samples=8
    scene.cycles.use_animated_seed=False
    scene.cycles.transparent_max_bounces=128
    scene.render.resolution_x=scene.render.resolution_y=1200
    scene.render.resolution_percentage=100
    scene.render.use_persistent_data=True
    scene.render.threads_mode,scene.render.threads='FIXED',12
    scene['web_revision']=REVISION
    scene['continuous_source_sha256']=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    scene['continuous_features']='30 moving lamellae; retained timber balcony access; directional sunlight; detailed door camera; wallbox with stowed cable; animated solar path and status indicator; no vehicle'
    scene.frame_set(1)
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(DEST),compress=True)
    frame=1+round(CHAPTERS[0]['rest']*(FRAME_COUNT-1)/STEP)*STEP
    scene.frame_set(frame);bpy.context.view_layer.update()
    regions={
      'planning':{'regions':[]},
      'installation':{'regions':[orient_bounds(scene,[(0,0,0),(9.6,0,0),(0,0,6),(9.6,0,6)])]},
      'smarthome':{'regions':[orient_bounds(scene,[(.1,-1.8,3),(4.7,-1.8,3),(1,0,5.5),(3.5,0,5.5)])]},
      'security':{'regions':[orient_bounds(scene,[(6.55,0,.95),(7.08,0,1.72)])]},
      'energy':{'regions':[orient_bounds(scene,[(5,1,9),(9.6,1,6),(5,10,9),(9.6,10,6)]),
                              orient_bounds(scene,[(9.65,2,.55),(9.9,2.8,1.65)])]}
    }
    write_json(ROOT/'src/config/house-v4-orientation.json',regions)
    write_json(OUT/'motion-samples.json',records)
    write_json(OUT/'frame-schedule.json',dict(zip(['unique','aliases'],schedule())))
    write_json(OUT/'native-build.json',{'revision':REVISION,'source':str(SOURCE),'sourceSha256':scene['continuous_source_sha256'],
                 'nativeFile':str(DEST),'nativeSha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),
                 'objects':len(scene.objects),'lamellae':len(slats),'addedObjects':len(NEW),
                 'sunlight':sun_data.energy,'allInteriorLightsConstant':True,'frameCount':FRAME_COUNT})
    print('CONTINUOUS_NATIVE_READY',str(DEST),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if args.prepare:
        prepare()
