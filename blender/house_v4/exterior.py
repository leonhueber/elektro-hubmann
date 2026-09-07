"""Native exterior refinement of the saved V4 architecture or latest web scene.

blender -b assets/3d/elektro-hubmann-house-v4.blend --python-exit-code 1 --python blender/house_v4/exterior.py -- --apply --views plan,detail,rear,opening
blender -b assets/3d/elektro-hubmann-house-v4-web.blend --python-exit-code 1 --python blender/house_v4/exterior.py -- --apply --frames 1,289,505,909,1139,1311

Writes sibling .blend files, preserving the existing scene and native animation.
"""
import argparse
import hashlib
import json
import math
import random
import re
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'blender'))
from house_v4 import core as c, architecture as a

REVISION = 'v4-exterior-01'
OUT = ROOT / 'docs/version-g-qa/blender-v4-exterior-r1'
MOCKUP = ROOT / 'docs/mockups/house-v4-exterior-r1/02-b-holzfenster.png'
CREATED = []


def box(name, loc, size, mat='charcoal', bevel=.006, parent=None, cut=False):
    return a.mark(c.box('Exterior | ' + name, loc, size, mat, bevel, parent), cut)


def delete_objects(objects):
    for obj in list(objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def load_materials():
    c.M.clear()
    for mat in sorted(bpy.data.materials, key=lambda m: m.users, reverse=True):
        if mat.name.startswith('V4 | ') and ' | web ' not in mat.name:
            c.M.setdefault(re.sub(r'\.\d{3}$', '', mat.name[5:]), mat)
    for key in ['plaster', 'charcoal', 'glass', 'oak', 'stone', 'linen white']:
        if key not in c.M:
            raise RuntimeError('Missing original material: ' + key)
    c.material('exterior larch', (.40, .265, .145), .64, 0, .0008)
    c.material('exterior concrete', (.48, .475, .435), .8, 0, .002)
    c.material('exterior gravel', (.27, .28, .255), .91, 0, .001)
    c.material('exterior grass', (.27, .29, .12), .87, 0, .0003)
    c.material('exterior grass dry', (.43, .34, .18), .89)
    timber = c.M['oak'].copy()
    timber.name = 'V4 | exterior timber window frame'
    c.M['exterior timber window frame'] = timber
    # Slightly tinted real glazing, thin enough to retain clear interior views.
    glass = c.M['glass'].copy()
    glass.name = 'V4 | exterior railing glass'
    c.M['exterior railing glass'] = glass
    glass.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .035


def larch_panel(name, x0, x1, z0, z1, y=-.045, cut=False):
    box(name + ' backing', ((x0+x1)/2, y+.012, (z0+z1)/2),
        (x1-x0, .028, z1-z0), 'oak dark', .002, cut=cut)
    n = max(1, round((x1-x0)/.075))
    for i in range(n):
        x = x0+(i+.5)*(x1-x0)/n
        box(name + ' vertical larch board', (x, y-.022, (z0+z1)/2),
            ((x1-x0)/n-.009, .049, z1-z0), 'exterior larch', .003, cut=cut)
    box(name + ' head flashing', ((x0+x1)/2, y-.027, z1+.011),
        (x1-x0+.035, .13, .022), cut=cut)


def balcony_door(parent):
    # Rebuild only the front wall cells and the left OG opening. The right
    # window, interior furniture, original room boundaries and animations stay.
    delete_objects(o for o in bpy.context.scene.objects if o.name.startswith('OG | front |'))
    old = bpy.data.objects.get('OG | X0.15 window 0')
    if old:
        delete_objects([*old.children_recursive, old])
    c.collection('V4 | OG 02 Facade', parent, 'OG | Parents')
    a.wall('OG | front', 'X', 0, a.W, .15, .30,
           [(1.0, 3.5, .07, 2.43), (6.82, 8.85, .65, 2.43)], True)
    root = a.window('OG | balcony door', (2.25, .15, 0), 2.5, .07, 2.36, cut=True)
    root['balcony_access'] = True
    root['clear_opening_width'] = 2.32
    root['threshold_height'] = .07
    # Handles and hinge barrels are real meshes on the two glazed leaves.
    for x in [-.11, .11]:
        box('balcony door handle plate', (x, -.09, 1.04), (.029, .018, .14), parent=root, cut=True)
        a.mark(c.rod('Exterior | balcony door lever', (x, -.13, 1.08),
                     (x+(-.11 if x < 0 else .11), -.13, 1.08), .009, 'charcoal', root), True)
    for name in ['Parents | curtain left', 'Parents | curtain right']:
        curtain = bpy.data.objects[name]
        curtain.location.z = .09
        for cloth in curtain.children:
            if cloth.type == 'MESH':
                cloth.scale.z = 2.33/1.54


def timber_window_frames():
    changed = []
    profiles = [' | outer jamb', ' | sash jamb', ' | outer rail', ' | central meeting stile']
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and ('window' in obj.name or 'balcony door' in obj.name) and any(part in obj.name for part in profiles):
            for slot in obj.material_slots:
                slot.link = 'OBJECT'
                slot.material = c.M['exterior timber window frame']
            obj['exterior_wood_window'] = True
            changed.append(obj)
    return changed


def balcony(parent, variant):
    c.collection('V4 | OG 20 Exterior balcony', parent, 'OG | Balcony')
    slab = box('balcony structural slab', (2.5, -.95, -.105), (4.50, 1.90, .23), 'exterior concrete', .013)
    slab['balcony_size_m'] = [4.5, 1.9]
    for i in range(6):
        for j in range(3):
            box('balcony porcelain tile', (.30+(i+.5)*.735, -1.85+(j+.5)*.596, .026),
                (.731, .592, .03), 'stone', .002)
    box('balcony drip edge', (2.5, -1.92, -.13), (4.55, .037, .042))
    box('balcony door drainage channel', (2.25, -.07, .044), (2.61, .10, .012))
    for i in range(52):
        box('balcony drain slot', (.99+i*.05, -.073, .052), (.015, .064, .004), 'steel', .001)
    paths = [((.34, -1.80), (4.66, -1.80), 4),
             ((.34, -.08), (.34, -1.80), 2), ((4.66, -1.80), (4.66, -.08), 2)]
    placed_posts = set()
    for start, end, n in paths:
        dx, dy = end[0]-start[0], end[1]-start[1]
        for i in range(n+1):
            x, y = start[0]+dx*i/n, start[1]+dy*i/n
            position = (round(x, 4), round(y, 4))
            if position in placed_posts:
                continue
            placed_posts.add(position)
            box('balcony railing post', (x, y, .61), (.035, .035, 1.15), cut=True)
            box('balcony railing shoe', (x, y, .064), (.095, .085, .025), cut=True)
            for xx in [-.031, .031]:
                a.mark(c.cylinder('Exterior | railing fixing bolt', (x+xx, y, .079),
                                  .009, .009, 'steel', vertices=12), True)
        for i in range(n):
            x, y = start[0]+dx*(i+.5)/n, start[1]+dy*(i+.5)/n
            if variant == 'A':
                size = (abs(dx)/n-.052, .012, .94) if dx else (.012, abs(dy)/n-.052, .94)
                pane = box('balcony laminated glass', (x, y, .635), size,
                           'exterior railing glass', .002, cut=True)
                pane['laminated_glass'] = True
                for z in [.24, 1.0]:
                    for t in [-.5, .5]:
                        box('railing stainless glass clamp', (x+dx/n*t*.9, y+dy/n*t*.9, z),
                            (.055, .035, .038) if dx else (.035, .055, .038), 'steel', cut=True)
            else:
                count = round(math.hypot(dx, dy)/n/.11)
                for k in range(count):
                    u = (i+(k+.5)/count)/n
                    box('balcony vertical picket', (start[0]+dx*u, start[1]+dy*u, .6555),
                        (.014, .014, 1.051), cut=True)
        if variant == 'B':
            box('balcony lower railing', ((start[0]+end[0])/2, (start[1]+end[1])/2, .12),
                (abs(dx)+.035 if dx else .028, abs(dy)+.035 if dy else .028, .035), cut=True)
        box('balcony continuous handrail', ((start[0]+end[0])/2, (start[1]+end[1])/2, 1.20),
            (abs(dx)+.035 if dx else .042, abs(dy)+.035 if dy else .042, .038), cut=True)
    if variant == 'A':
        larch_panel('balcony left surround', .61, .98, .06, 2.46, cut=True)
        larch_panel('balcony right surround', 3.52, 3.91, .06, 2.46, cut=True)
    box('balcony door lintel', (2.25, -.06, 2.47), (2.75, .26, .09), cut=True)
    grass_planter('balcony left planter', .62, -.62, .045, .40, .42, .34, cut=True)
    lounge_chair('balcony chair', 4.0, -.92, .045, .15, scale=.73, cut=True)
    c.cylinder('Exterior | balcony bistro top', (3.43, -1.17, .60), .24, .026, 'exterior larch')
    c.cylinder('Exterior | balcony bistro pedestal', (3.43, -1.17, .32), .023, .54, 'charcoal')
    c.cylinder('Exterior | balcony bistro foot', (3.43, -1.17, .06), .18, .025, 'charcoal')
    # Keep the low balcony furniture and 1.2 m railing readable in exploded
    # views, just like the retained low room walls. Only the tall lintel cuts.
    for obj in c.COL.objects:
        if obj.get('cutaway_upper') and not obj.name.startswith('Exterior | balcony door lintel'):
            obj['cutaway_upper'] = False


def grass_planter(name, x, y, z, width, depth, height, cut=False):
    root = c.empty('Exterior | '+name, (x, y, z))
    for loc, size in [((0, 0, .025), (width, depth, .05)),
                      ((-width/2+.025, 0, height/2), (.05, depth, height)),
                      ((width/2-.025, 0, height/2), (.05, depth, height)),
                      ((0, -depth/2+.025, height/2), (width, .05, height)),
                      ((0, depth/2-.025, height/2), (width, .05, height))]:
        box(name+' hollow concrete planter', loc, size, 'exterior concrete', .008, root, cut)
    box(name+' soil', (0, 0, height-.06), (width-.09, depth-.09, .03), 'soil', parent=root, cut=cut)
    rng = random.Random(name)
    verts, faces = [], []
    for i in range(100):
        angle = rng.random()*math.tau
        base = Vector((rng.uniform(-.32, .32)*width, rng.uniform(-.32, .32)*depth, height-.04))
        length = rng.uniform(.30, .82)*(width/.65)**.22
        side = Vector((-math.sin(angle), math.cos(angle), 0))*rng.uniform(.004, .012)
        n = len(verts)
        for k in range(7):
            t = k/6
            center = base+Vector((math.cos(angle)*length*.6*t*t, math.sin(angle)*length*.6*t*t, length*(t-.25*t*t)))
            verts.extend([center-side*(1-t), center+side*(1-t)])
        faces.extend((n+k*2, n+k*2+1, n+k*2+3, n+k*2+2) for k in range(6))
    obj = a.mark(c.mesh('Exterior | '+name+' individual grass blades', verts, faces, 'exterior grass', root, smooth=True), cut)
    obj.data.materials.append(c.M['exterior grass dry'])
    for poly in obj.data.polygons:
        poly.material_index = int((poly.index//6)%4 == 0)


def lounge_chair(name, x, y, z, angle=0, scale=1, cut=False):
    root = c.empty('Exterior | '+name, (x, y, z), angle)
    root.scale = (scale,)*3
    for xx in [-.32, .32]:
        for yy in [-.29, .29]:
            a.mark(c.rod('Exterior | '+name+' splayed leg', (xx*1.08, yy*1.1, .015),
                         (xx, yy, .38), .016, 'charcoal', root), cut)
        a.mark(c.tube('Exterior | '+name+' arm frame', [(xx, -.32, .38), (xx, -.30, .63),
                     (xx, .31, .63), (xx, .37, .36)], .017, 'charcoal', root), cut)
        box(name+' timber armrest', (xx, -.01, .64), (.055, .57, .038), 'exterior larch', parent=root, cut=cut)
    box(name+' seat frame', (0, 0, .365), (.65, .66, .035), parent=root, cut=cut)
    a.mark(c.soft('Exterior | '+name+' piped seat cushion', (0, -.015, .43),
                  (.62, .60, .13), 'linen white', root, seam=True), cut)
    a.mark(c.soft('Exterior | '+name+' back cushion', (0, .285, .70),
                  (.62, .14, .49), 'linen white', root, rotation=(math.radians(-12), 0, 0), seam=True), cut)
    if cut:
        for obj in root.children_recursive:
            obj['cutaway_upper'] = True
    return root


def terrace(parent):
    c.collection('V4 | EG 20 Exterior terrace', parent, 'EG | Terrace')
    old = bpy.data.objects['Terrace | stone base']
    old.location = (2.37, -1.47, -.115)
    old.scale = (4.78/4.66, 3.10/1.75, .17/.16)
    delete_objects(o for o in bpy.context.scene.objects if o.name.startswith('Terrace | oak decking'))
    for i in range(18):
        obj = c.box('Terrace | oak decking', (2.37, -2.94+i*.17, -.006),
                    (4.77, .164, .044), 'exterior larch', .003)
        for xx in [.13, 4.61]:
            for dy in [-.043, .043]:
                c.cylinder('Exterior | terrace flush deck screw', (xx, obj.location.y+dy, .018),
                           .004, .002, 'steel', vertices=10)
    box('terrace timber front fascia', (2.37, -3.032, -.087), (4.79, .048, .14), 'exterior larch')
    box('terrace timber side fascia', (4.784, -1.48, -.087), (.044, 3.12, .14), 'exterior larch')
    bpy.data.objects['Terrace | left olive tree'].location = (.43, -2.34, .016)
    lounge_chair('terrace lounge left', 1.62, -1.88, .017, -.15)
    lounge_chair('terrace lounge right', 3.55, -1.87, .017, .22)
    c.cylinder('Exterior | terrace coffee table', (2.63, -2.10, .47), .39, .032, 'exterior larch')
    for angle in [0, math.tau/3, 2*math.tau/3]:
        c.rod('Exterior | table tripod', (2.63+.32*math.cos(angle), -2.10+.32*math.sin(angle), .03),
              (2.63+.20*math.cos(angle), -2.10+.20*math.sin(angle), .45), .013, 'charcoal')
    c.lathe('Exterior | terrace ceramic cup', (2.65, -2.09, .486),
            [(0, 0), (.042, 0), (.043, .077), (.038, .079), (.036, .01), (0, .01)], 'ceramic', segments=32)
    # Supports end at the balcony underside. They fade with the EG walls, so
    # the exploded model never has columns stretching between separated floors.
    for x in [.37, 4.63]:
        box('balcony support post', (x, -1.80, 1.41), (.075, .075, 2.78), cut=True)
        box('balcony support foot', (x, -1.80, .039), (.17, .17, .04), cut=True)
        box('balcony support head', (x, -1.80, 2.79), (.19, .15, .035), cut=True)
    grass_planter('terrace outer planter', 4.33, -2.66, .017, .67, .46, .40)
    # Large pavers lead from the entrance. Model tops are flush to their beds.
    for j in range(3):
        box('entry approach paver', (5.77, -1.53-j*.72, -.13), (1.88, .68, .14), 'stone', .011)


def window_trim(name, center, width, bottom, height, rotation, cut=False):
    root = c.empty('Exterior | '+name+' reveal', center, rotation)
    for x in [-width/2-.052, width/2+.052]:
        box(name+' projecting reveal jamb', (x, -.045, bottom+height/2),
            (.10, .18, height+.15), 'plaster', .003, root, cut)
    box(name+' projecting reveal head', (0, -.046, bottom+height+.048),
        (width+.20, .19, .10), 'plaster', .003, root, cut)
    box(name+' deep folded sill', (0, -.105, bottom-.03), (width+.24, .32, .045), parent=root, cut=cut)
    for xx in [-width/2-.108, width/2+.108]:
        box(name+' sill end cap', (xx, -.105, bottom-.004), (.014, .32, .045), parent=root, cut=cut)


def facade_details(roots, variant):
    for level in ['EG', 'OG']:
        c.collection(f'V4 | {level} 21 Exterior facade details', roots[level], level+' | Facade')
        front = [(7.65, 8.53, .85, 2.05)] if level == 'EG' else [(6.82, 8.85, .65, 2.43)]
        for i, (lo, hi, bottom, top) in enumerate(front):
            window_trim(level+' front '+str(i), ((lo+hi)/2, 0, 0), hi-lo, bottom, top-bottom, 0, True)
        for side, xx, rotation in [('east', 9.6, math.pi/2), ('west', 0, -math.pi/2)]:
            openings = [(1.35, 2.25, .83, 2.1), (7.45, 8.45, .83, 2.1)] if side == 'east' else [(1.35, 3.45, .7, 2.3), (7.75, 9.35, 1.13, 2.36)]
            for i, (lo, hi, bottom, top) in enumerate(openings):
                window_trim(level+' '+side+' '+str(i), (xx, (lo+hi)/2, 0), hi-lo, bottom, top-bottom, rotation, side == 'east')
        for i, (lo, hi, bottom, top) in enumerate([(1.05, 3.3, 1.2, 2.38), (7, 8.75, 1.12, 2.35)]):
            window_trim(level+' rear '+str(i), ((lo+hi)/2, 10.8, 0), hi-lo, bottom, top-bottom, math.pi)
        if level == 'OG':
            # Recessed dark line below a shallow plaster lip, one strip per side.
            for loc, size in [((4.8, -.025, .09), (9.6, .045, .025)),
                              ((9.625, 5.4, .09), (.045, 10.8, .025)),
                              ((-.025, 5.4, .09), (.045, 10.8, .025)),
                              ((4.8, 10.825, .09), (9.6, .045, .025))]:
                box('storey recessed shadow joint', loc, size, 'exterior concrete', .002)
            if variant == 'A':
                larch_panel('upper window sliding shutter', 6.08, 6.70, .64, 2.43, y=-.18, cut=True)
                for z in [.57, 2.51]:
                    box('shutter exposed runner', (7.44, -.11, z), (2.88, .06, .035), cut=True)
        for x in [.05, 9.55]:
            for z in [.51, 2.60]:
                box('rainwater wall bracket', (x, -.09, z), (.07, .20, .03), cut=z>1.18)
    c.collection('V4 | EG 22 Exterior entrance canopy', roots['EG'], 'EG | Entrance')
    for x0, x1 in [(4.66, 4.92), (6.57, 6.72)]:
        larch_panel('entrance jamb', x0, x1, .07, 2.43, cut=True)
    canopy = box('entrance floating canopy', (5.72, -.56, 2.56), (2.32, 1.38, .10), cut=True)
    canopy['entrance_canopy'] = True
    box('canopy timber soffit', (5.72, -.57, 2.501), (2.19, 1.26, .018), 'exterior larch', cut=True)
    for x in [4.89, 6.55]:
        box('canopy wall bracket', (x, -.04, 2.40), (.065, .12, .31), cut=True)
        a.mark(c.rod('Exterior | canopy cantilever rib', (x, .0, 2.49), (x, -1.13, 2.49), .023, 'charcoal'), True)
    for x in [5.05, 6.39]:
        a.mark(c.cylinder('Exterior | canopy recessed downlight rim', (x, -.74, 2.482), .055, .016, 'charcoal'), True)
        a.mark(c.cylinder('Exterior | canopy recessed warm diffuser', (x, -.74, 2.471), .044, .008, 'light'), True)
        light = c.area('Exterior | canopy warm pool', (x, -.74, 2.455), (x, -.74, .0), 12, .18)
        light['interior_light'] = True
        light['nominal_watts'] = 12
        light['cutaway_upper'] = True
    box('entry flush mat', (5.75, -.36, .048), (1.08, .56, .012), 'charcoal', .004)
    for x in [7.15, 9.0]:
        box('facade wall sconce body', (x, -.066, 2.14), (.085, .13, .24), cut=True)
        box('facade wall sconce lens', (x, -.069, 2.011), (.059, .087, .007), 'light', cut=True)
    c.collection('V4 | Roof 20 Exterior roof details', roots['Roof'], 'Roof')
    for y, direction in [(-.026, -1), (10.826, 1)]:
        box('gable ventilation dark recess', (4.8, y, 1.68), (.45, .025, .58))
        for z in [1.405, 1.955]:
            box('gable vent surround', (4.8, y+direction*.02, z), (.51, .07, .034), 'stone')
        for x in [4.56, 5.04]:
            box('gable vent surround', (x, y+direction*.02, 1.68), (.035, .07, .58), 'stone')
        for i in range(9):
            louver = box('gable ventilation louver', (4.8, y+direction*.04, 1.44+i*.059), (.43, .065, .022))
            louver.rotation_euler.x = math.radians(23)*direction
    for x in [-.19, 9.79]:
        box('roof timber eaves underside', (x, 5.4, -.035), (.35, 11.13, .048), 'exterior larch')
        for i in range(16):
            box('gutter support clip', (x, -.12+i*.737, -.08), (.15, .032, .025))
    c.collection('V4 | EG 23 Exterior base and gravel', roots['EG'], 'EG | Grounds')
    for loc, size in [((9.615, 5.4, .045), (.065, 10.8, .38)),
                      ((-.015, 5.4, .045), (.065, 10.8, .38)),
                      ((4.8, 10.815, .045), (9.6, .065, .38)),
                      ((8.14, -.025, .045), (2.92, .065, .38))]:
        box('stone splash plinth', loc, size, 'exterior concrete')
    gravel_perimeter()


def gravel_perimeter():
    rng = random.Random(406091)
    verts, faces = [], []
    areas = [(9.67, -.5, 10.13, 11.27), (-.53, -3.17, -.07, 11.27),
             (-.07, 10.87, 9.67, 11.27), (6.80, -.49, 9.67, -.05)]
    for x0, y0, x1, y1 in areas:
        box('gravel bed', ((x0+x1)/2, (y0+y1)/2, -.18), (x1-x0, y1-y0, .04), 'exterior gravel', .005)
        for _ in range(round((x1-x0)*(y1-y0)*160)):
            x, y = rng.uniform(x0+.025, x1-.025), rng.uniform(y0+.025, y1-.025)
            radius = rng.uniform(.018, .038)
            n = len(verts)
            for z, r in [(-.163, radius), (-.132, radius*.63)]:
                verts.extend((x+r*math.cos(i*math.tau/5), y+r*math.sin(i*math.tau/5), z+rng.uniform(-.006, .006)) for i in range(5))
            faces.append(tuple(n+i for i in range(5, 10)))
            faces.extend((n+i, n+(i+1)%5, n+(i+1)%5+5, n+i+5) for i in range(5))
    obj = c.mesh('Exterior | individual drainage pebbles', verts, faces, 'exterior gravel', smooth=True)
    obj.data.materials.append(c.M['stone'])
    for face in obj.data.polygons:
        face.material_index = int((face.index//6)%5 == 0)


def attach_existing_web_animation(objects):
    """Attach new geometry to existing visibility shaders and native keyframes.

    Never bake/recreate the latest camera, lighting, storey or roof animation.
    """
    from house_v4.motion import state, FRAME_COUNT, STEP
    copies = {}
    for obj in objects:
        eg = any(col.name.startswith('V4 | EG ') for col in obj.users_collection)
        group = 'eg_cut' if eg and obj.get('cutaway_upper') else 'eg' if eg else 'cut' if obj.get('cutaway_upper') else None
        if not group or obj.type not in ['MESH', 'CURVE', 'LIGHT']:
            continue
        obj.hide_set(False)
        if obj.type != 'LIGHT':
            for slot in obj.material_slots:
                original = slot.material
                identity = (original.name, group)
                if identity not in copies:
                    mat = original.copy()
                    mat.name = original.name+' | exterior web '+group
                    tree = mat.node_tree
                    output = next(n for n in tree.nodes if n.type == 'OUTPUT_MATERIAL')
                    original_shader = output.inputs['Surface'].links[0].from_socket
                    transparent = tree.nodes.new('ShaderNodeBsdfTransparent')
                    mix = tree.nodes.new('ShaderNodeMixShader')
                    control = tree.nodes.new('ShaderNodeGroup')
                    control.node_tree = bpy.data.node_groups['V4 web visibility | '+group]
                    tree.links.new(control.outputs[0], mix.inputs[0])
                    tree.links.new(transparent.outputs[0], mix.inputs[1])
                    tree.links.new(original_shader, mix.inputs[2])
                    tree.links.new(mix.outputs[0], output.inputs['Surface'])
                    copies[identity] = mat
                slot.link = 'OBJECT'
                slot.material = copies[identity]
        previous = None
        for frame in range(1, FRAME_COUNT+1, STEP):
            s = state((frame-1)/(FRAME_COUNT-1))
            visibility = s['eg']*s['cut'] if group == 'eg_cut' else s['eg'] if group == 'eg' else s['cut']
            hidden = visibility < .002
            if hidden != previous:
                obj.hide_render = obj.hide_viewport = hidden
                obj.keyframe_insert(data_path='hide_render', frame=frame)
                obj.keyframe_insert(data_path='hide_viewport', frame=frame)
                previous = hidden
            if obj.type == 'LIGHT':
                obj.data.energy = obj.get('nominal_watts', 12)*visibility
                obj.data.keyframe_insert(data_path='energy', frame=frame)


def widen_cameras():
    """Give the projecting balcony and terrace consistent breathing room."""
    for camera in bpy.data.cameras:
        camera.lens *= .90
        animation = camera.animation_data
        if not animation or not animation.action:
            continue
        for layer in animation.action.layers:
            for strip in layer.strips:
                bag = strip.channelbag(animation.action_slot)
                if bag:
                    for curve in bag.fcurves:
                        if curve.data_path == 'lens':
                            for point in curve.keyframe_points:
                                point.co.y *= .90
                                point.handle_left.y *= .90
                                point.handle_right.y *= .90
                            curve.update()


def apply(variant='B'):
    scene = bpy.context.scene
    if scene.get('exterior_revision'):
        raise RuntimeError('Refine the original V4 source, not an already refined file.')
    if scene.get('model_revision') != 'v4-build-02':
        raise RuntimeError('Expected the inspected v4-build-02 base model.')
    source = Path(bpy.data.filepath)
    is_web = bool(scene.get('web_revision'))
    if not is_web:
        import build_house_v4
        build_house_v4.set_view('plan')
    else:
        scene.frame_set(1)
    original_objects = set(scene.objects)
    original_camera_action = scene.camera.animation_data.action.name if is_web else None
    roots = {key: bpy.data.objects['V4 | '+key+' assembly'] for key in ['EG', 'OG', 'Roof']}
    load_materials()
    balcony_door(roots['OG'])
    balcony(roots['OG'], variant)
    terrace(roots['EG'])
    facade_details(roots, variant)
    wood_frames = timber_window_frames()
    CREATED[:] = [obj for obj in scene.objects if obj not in original_objects]
    for obj in CREATED:
        obj['exterior_revision'] = REVISION
    if is_web:
        attach_existing_web_animation(list(set(CREATED + wood_frames)))
        assert scene.camera.animation_data.action.name == original_camera_action
        scene['exterior_base_web_revision'] = scene['web_revision']
        scene['web_revision'] = str(scene['web_revision'])+'-exterior-01'
    widen_cameras()
    img = bpy.data.images.load(str(MOCKUP), check_existing=True)
    img.pack()
    note = bpy.data.texts.get('V4_EXTERIOR_README') or bpy.data.texts.new('V4_EXTERIOR_README')
    note.write('Exterior revision 01 / concept '+variant+'\nNative balcony 4.5 x 1.9 m with real glazed access door.\n'
               'Terrace, furniture, larch details, window reveals, canopy, drainage and roof fittings.\n'
               'Existing camera, interior and assembly animation retained; added exterior uses the same visibility groups.\n'
               'Website image sequence has not been re-exported.\nReproduce using blender/house_v4/exterior.py on the original V4 files.\n')
    scene['exterior_revision'] = REVISION
    scene['exterior_variant'] = variant
    scene['exterior_window_finish'] = 'oak timber appearance; anthracite metal sills'
    scene['exterior_source'] = str(source)
    scene['exterior_source_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    scene.frame_set(1)
    bpy.context.view_layer.update()
    destination = ROOT/'assets/3d'/('elektro-hubmann-house-v4-exterior-r1'+('-web' if is_web else '')+'.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
    print('V4_EXTERIOR_SAVED', destination, len(CREATED), 'new objects', flush=True)


def validate():
    scene = bpy.context.scene
    is_web = bool(scene.get('web_revision'))
    scene.frame_set(1)
    bpy.context.view_layer.update()
    checks = []
    def check(name, value):
        checks.append({'check': name, 'passed': bool(value)})
    og = bpy.data.objects['V4 | OG assembly']
    eg = bpy.data.objects['V4 | EG assembly']
    slab = bpy.data.objects.get('Exterior | balcony structural slab')
    door = bpy.data.objects.get('OG | balcony door')
    check('Balcony slab follows upper storey', slab and slab.parent == og)
    check('Usable 4.5 by 1.9 m balcony', slab and list(slab['balcony_size_m']) == [4.5, 1.9])
    check('Full-height balcony access with 7 cm threshold', door and door.get('balcony_access') and door.get('threshold_height') == .07)
    # Verify front plaster vertices do not occupy the new door opening below
    # the old window sill. This checks the actual mesh, not merely metadata.
    obstructing = []
    for obj in scene.objects:
        if obj.name.startswith('OG | front |'):
            for polygon in obj.data.polygons:
                center = polygon.center
                if 1.001 < center.x < 3.499 and .071 < center.z < .649:
                    obstructing.append(obj.name)
    check('Old window parapet removed from mesh', not obstructing)
    check('Two grounded balcony supports', sum(o.name.startswith('Exterior | balcony support post') and o.parent == eg for o in scene.objects) == 2)
    posts = [o for o in scene.objects if o.name.startswith('Exterior | balcony railing post')]
    check('Balcony railing top at least 1.1 m above finished deck', posts and min(o.location.z+o.dimensions.z/2 for o in posts) > 1.14)
    check('Ten PV modules retained', sum(o.name.startswith('PV | module ') and o.type == 'EMPTY' for o in scene.objects) == 10)
    check('Three original beds retained', all(bpy.data.objects.get(name) for name in ['Parents | double oak bed', 'Child front | oak single bed', 'Child rear | oak single bed']))
    check('Eighteen native stair risers retained', sum(o.name.startswith(('U stair | lower riser', 'U stair | upper riser')) for o in scene.objects) == 18)
    check('Entrance camera and bell retained', bpy.data.objects.get('Entrance | optical lens') and bpy.data.objects.get('Entrance | bell button'))
    check('Timber window profiles on all elevations', sum(bool(o.get('exterior_wood_window')) for o in scene.objects) >= 60)
    check('Every new mesh has a material', all(o.data.materials for o in scene.objects if o.type == 'MESH' and o.get('exterior_revision')))
    samples = []
    if is_web:
        cam = bpy.data.objects['V4 | Continuous scroll camera']
        check('Existing continuous camera has native animation', cam.animation_data and cam.animation_data.action)
        for frame in [1, 289, 505, 909, 1139, 1311, 1441]:
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            world_slab = slab.matrix_world.translation.z
            check('Balcony follows OG at frame '+str(frame), abs(world_slab-(og.location.z-.105)) < .001)
            samples.append({'frame': frame, 'ogZ': og.location.z, 'balconyZ': world_slab,
                            'camera': list(cam.location), 'balconyGlassHidden': next((o.hide_render for o in scene.objects if o.name.startswith('Exterior | balcony laminated glass')), None)})
        scene.frame_set(505)
        check('EG support columns hidden in open interior', all(o.hide_render for o in scene.objects if o.name.startswith('Exterior | balcony support post')))
        scene.frame_set(909)
        check('Ground terrace hidden in isolated OG view', bpy.data.objects['Exterior | terrace lounge left piped seat cushion'].hide_render)
    scene.frame_set(1)
    report = {'revision': REVISION, 'file': bpy.data.filepath, 'variant': scene.get('exterior_variant'),
              'allPassed': all(row['passed'] for row in checks), 'checks': checks, 'motionSamples': samples,
              'objects': len(scene.objects), 'addedObjects': sum(bool(o.get('exterior_revision')) for o in scene.objects),
              'vertices': sum(len(o.data.vertices) for o in scene.objects if o.type == 'MESH')}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/('web-validation.json' if is_web else 'model-validation.json')).write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('V4_EXTERIOR_VALIDATION', json.dumps(report), flush=True)
    if not report['allPassed']:
        raise RuntimeError('Exterior validation failed.')


def render(views, frames, size, samples):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.use_persistent_data = True
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 12
    OUT.mkdir(parents=True, exist_ok=True)
    if frames:
        for frame in frames:
            scene.frame_set(frame)
            scene.render.filepath = str(OUT/f'web-{frame:04d}.png')
            bpy.ops.render.render(write_still=True)
            print('EXTERIOR_RENDERED', frame, flush=True)
    else:
        import build_house_v4
        # Render-time camera markers override scene.camera. Unbind them for
        # temporary exterior inspection angles, then restore the saved setup.
        bindings = [(marker, marker.camera) for marker in scene.timeline_markers]
        for marker, _ in bindings:
            marker.camera = None
        for view in views:
            build_house_v4.set_view(view if view in build_house_v4.POSES else 'plan')
            if view in ['detail', 'rear']:
                # Temporary camera copy does not change the eight saved cameras.
                camera = scene.camera.copy()
                camera.data = scene.camera.data.copy()
                scene.collection.objects.link(camera)
                position, target, lens = ((13, -19, 9), (3.5, -.2, 2.8), 67) if view == 'detail' else ((23, 28, 11), (4.8, 5.4, 4.4), 64)
                camera.location = position
                camera.rotation_euler = (Vector(target)-Vector(position)).to_track_quat('-Z', 'Y').to_euler()
                camera.data.lens = lens
                scene.camera = camera
                bpy.context.view_layer.update()
            scene.render.filepath = str(OUT/(view+'.png'))
            bpy.ops.render.render(write_still=True)
            print('EXTERIOR_RENDERED', view, flush=True)
            if view in ['detail', 'rear']:
                bpy.data.objects.remove(camera, do_unlink=True)
        for marker, camera in bindings:
            marker.camera = camera


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--variant', choices=['A', 'B'], default='B')
    parser.add_argument('--views', default='')
    parser.add_argument('--frames', default='')
    parser.add_argument('--size', type=int, default=1000)
    parser.add_argument('--samples', type=int, default=32)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if args.apply:
        apply(args.variant)
    validate()
    if args.views or args.frames:
        render([v for v in args.views.split(',') if v], [int(v) for v in args.frames.split(',') if v], args.size, args.samples)
