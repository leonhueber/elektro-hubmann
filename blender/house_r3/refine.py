"""Refine the saved R3 architecture without rebuilding its layout or animation.

Load the original R3 .blend explicitly. The detailed scene is saved separately.
All new geometry is native, deterministic, and uses packed/procedural materials.
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'blender'))
from house_r3 import core as c

SOURCE = ROOT / 'assets/3d/elektro-hubmann-house-v3-r3.blend'
DETAIL = ROOT / 'assets/3d/elektro-hubmann-house-v3-r3-detail.blend'
OUT = ROOT / 'docs/version-g-qa/blender-v3-r3/detail'
RNG = random.Random(90526)


def remove_object(obj):
    bpy.data.objects.remove(obj, do_unlink=True)


def color_material(name, color, rough=.6, metallic=0, bump=.0005):
    return c.material(name, color, rough, metallic, bump, 145)


def shader_color(material, color, rough, bump):
    material.diffuse_color = (*color, 1)
    nodes = material.node_tree.nodes
    p = nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    for node in nodes:
        if node.type == 'BUMP':
            node.inputs['Distance'].default_value = bump
            node.inputs['Strength'].default_value = .18


def textile(name, color, weave=.0012, rough=.91):
    m = color_material(name, color, rough, bump=0)
    n, l = m.node_tree.nodes, m.node_tree.links
    p = n.get('Principled BSDF')
    p.inputs['Sheen Weight'].default_value = .22
    p.inputs['Sheen Roughness'].default_value = .65
    coord = n.new('ShaderNodeTexCoord')
    tex = n.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = 260
    tex.inputs['Roughness'].default_value = .72
    l.new(coord.outputs['Object'], tex.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*[v*.84 for v in color], 1)
    ramp.color_ramp.elements[1].color = (*[min(1, v*1.08) for v in color], 1)
    l.new(tex.outputs['Fac'], ramp.inputs[0])
    l.new(ramp.outputs[0], p.inputs['Base Color'])
    wave = n.new('ShaderNodeTexWave')
    wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value = 330
    wave.inputs['Distortion'].default_value = 1.1
    l.new(coord.outputs['Object'], wave.inputs['Vector'])
    mix = n.new('ShaderNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = .5
    l.new(wave.outputs['Color'], mix.inputs[1])
    l.new(tex.outputs['Fac'], mix.inputs[2])
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .30
    bump.inputs['Distance'].default_value = weave
    l.new(mix.outputs[0], bump.inputs['Height'])
    l.new(bump.outputs[0], p.inputs['Normal'])
    return m


def oak(name, tint, floor=False):
    m = color_material(name, tint, .48, bump=0)
    n, l = m.node_tree.nodes, m.node_tree.links
    p = n.get('Principled BSDF')
    p.inputs['Coat Weight'].default_value = .10
    p.inputs['Coat Roughness'].default_value = .43
    coord = n.new('ShaderNodeTexCoord')
    mapping = n.new('ShaderNodeVectorMath')
    mapping.operation = 'MULTIPLY'
    mapping.inputs[1].default_value = (.85, .35, .85)
    l.new(coord.outputs['Object'], mapping.inputs[0])
    info = n.new('ShaderNodeObjectInfo')
    shift = n.new('ShaderNodeVectorMath')
    shift.operation = 'ADD'
    l.new(mapping.outputs[0], shift.inputs[0])
    l.new(info.outputs['Random'], shift.inputs[1])
    image = bpy.data.images.get('oak_veneer_01_diff_1k.jpg')
    tex = n.new('ShaderNodeTexImage')
    tex.image = image
    tex.projection = 'BOX'
    tex.projection_blend = .15
    l.new(shift.outputs[0], tex.inputs['Vector'])
    tint_node = n.new('ShaderNodeMixRGB')
    grain = n.new('ShaderNodeValToRGB')
    grain.color_ramp.elements[0].position = .08
    grain.color_ramp.elements[0].color = (.12, .060, .024, 1)
    grain.color_ramp.elements[1].position = .48
    grain.color_ramp.elements[1].color = (.66, .47, .28, 1)
    l.new(tex.outputs['Color'], grain.inputs[0])
    tint_node.inputs[0].default_value = .24 if floor else .33
    tint_node.inputs[2].default_value = (*tint, 1)
    l.new(grain.outputs[0], tint_node.inputs[1])
    l.new(tint_node.outputs[0], p.inputs['Base Color'])
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .22
    bump.inputs['Distance'].default_value = .0007
    l.new(tex.outputs['Color'], bump.inputs['Height'])
    l.new(bump.outputs[0], p.inputs['Normal'])
    rough = n.new('ShaderNodeMapRange')
    rough.inputs['To Min'].default_value = .39
    rough.inputs['To Max'].default_value = .56
    l.new(tex.outputs['Color'], rough.inputs['Value'])
    l.new(rough.outputs[0], p.inputs['Roughness'])
    return m


def stone(name, color):
    m = color_material(name, color, .62, bump=0)
    n, l = m.node_tree.nodes, m.node_tree.links
    p = n.get('Principled BSDF')
    coord = n.new('ShaderNodeTexCoord')
    noise = n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 7
    noise.inputs['Detail'].default_value = 4
    l.new(coord.outputs['Object'], noise.inputs[0])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*[v*.82 for v in color], 1)
    ramp.color_ramp.elements[1].color = (*[v*1.10 for v in color], 1)
    l.new(noise.outputs['Fac'], ramp.inputs[0])
    l.new(ramp.outputs[0], p.inputs['Base Color'])
    fine = n.new('ShaderNodeTexNoise')
    fine.inputs['Scale'].default_value = 180
    l.new(coord.outputs['Object'], fine.inputs[0])
    bump = n.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = .0008
    bump.inputs['Strength'].default_value = .18
    l.new(fine.outputs['Fac'], bump.inputs['Height'])
    l.new(bump.outputs[0], p.inputs['Normal'])
    return m


def materials():
    c.M.update({m.name: m for m in bpy.data.materials})
    for m in bpy.data.materials:
        base = m.name.split(' | ')[0]
        if base in ('wall interior', 'plaster'):
            shader_color(m, (.84, .82, .77), .82, .0007)
        elif base == 'cut edge':
            shader_color(m, (.19, .205, .20), .70, .0003)
        elif base == 'ivory cabinet':
            shader_color(m, (.73, .705, .65), .39, .0001)
        elif base == 'white':
            shader_color(m, (.87, .865, .84), .34, .0001)
        elif base == 'grout':
            shader_color(m, (.47, .44, .38), .88, .0003)
    new = {
        'oak': oak('Detail | natural oak joinery', (.50, .35, .21)),
        'oak light': oak('Detail | pale oak joinery', (.60, .46, .31)),
        'linen': textile('Detail | oatmeal upholstery', (.53, .49, .43)),
        'linen light': textile('Detail | warm white linen', (.81, .78, .71)),
        'linen taupe': textile('Detail | flax upholstery', (.36, .33, .285)),
        'rust': textile('Detail | terracotta linen', (.34, .105, .06)),
        'rug': textile('Detail | woven wool', (.48, .445, .39), .005),
        'tile': stone('Detail | warm grey limestone', (.51, .515, .49)),
        'stone': stone('Detail | honed cream stone', (.69, .65, .57)),
    }
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for slot in obj.material_slots:
                if slot.material and slot.material.name in new:
                    slot.material = new[slot.material.name]
    c.M.update(new)
    for material in new.values():
        c.M[material.name] = material
    # Upper and lower pieces need the same finish when the house is closed.
    for old in list(bpy.data.materials):
        base, separator, group = old.name.partition(' | ')
        if separator and group in ('shell','roof') and base in new:
            name=old.name
            old.name=name+' | replaced'
            replacement=new[base].copy()
            replacement.name=name
            nodes, links=replacement.node_tree.nodes, replacement.node_tree.links
            transparent=nodes.new('ShaderNodeBsdfTransparent')
            visibility=nodes.new('ShaderNodeMixShader'); visibility.name='Visibility'
            visibility.inputs[0].default_value=old.node_tree.nodes['Visibility'].inputs[0].default_value
            links.new(transparent.outputs[0],visibility.inputs[1])
            links.new(nodes.get('Principled BSDF').outputs[0],visibility.inputs[2])
            links.new(visibility.outputs[0],nodes.get('Material Output').inputs['Surface'])
            if old.node_tree.animation_data:
                replacement.node_tree.animation_data_create()
                replacement.node_tree.animation_data.action=old.node_tree.animation_data.action
                replacement.node_tree.animation_data.action_slot=old.node_tree.animation_data.action_slot
            old.user_remap(replacement)
            bpy.data.materials.remove(old)
            c.M[name]=replacement
    for m in bpy.data.materials:
        if m.name.split(' | ')[0]=='glass':
            m.use_raytrace_refraction=True
            m.refraction_depth=.018
    floor = [oak('Detail | oak plank %02d'%i,
                 tuple(v*(.93+i*.022) for v in (.62,.47,.31)), True) for i in range(7)]
    for obj in bpy.data.objects:
        if 'oak plank' in obj.name and obj.type == 'MESH':
            obj.data.materials[0] = RNG.choice(floor)
    textile('Detail | stitch', (.50, .44, .35), .0003)
    textile('Detail | pale stitch', (.78, .73, .64), .0003)
    textile('Detail | soft sage', (.29, .36, .29), .001)
    color_material('Detail | mirror', (.92,.93,.92), .08, 1, 0)
    color_material('Detail | brushed nickel', (.48,.51,.50), .28, .9, .00015)
    color_material('Detail | coffee', (.022,.009,.004), .16, 0, 0)
    color_material('Detail | sink steel', (.20,.235,.23), .33, .88, .00015)
    color_material('Detail | smoked appliance glass', (.035,.045,.047), .15, .48, 0)
    textile('Detail | coir mat', (.24,.16,.075), .004)
    bpy.data.objects['Doormat'].data.materials[0]=c.M['Detail | coir mat']
    textile('Detail | quilted flax', (.40,.355,.29), .004)
    for name in ('Detail | woven wool', 'Detail | quilted flax'):
        for node in c.M[name].node_tree.nodes:
            if node.type=='TEX_NOISE':
                node.inputs['Scale'].default_value=90
            elif node.type=='TEX_WAVE':
                node.inputs['Scale'].default_value=100


def signed_power(value, exponent):
    return math.copysign(abs(value)**exponent, value)


def pillow_mesh(obj):
    """Replace primitive cushions in place so existing furniture transforms survive."""
    # Local mesh bounds include unapplied sphere scale on the original pillows.
    lo = [min(v.co[i] for v in obj.data.vertices) for i in range(3)]
    hi = [max(v.co[i] for v in obj.data.vertices) for i in range(3)]
    radii = [(hi[i]-lo[i])*obj.scale[i]/2 for i in range(3)]
    verts, faces = [], []
    segments, rings = 64, 32
    is_pillow = 'pillow' in obj.name or 'accent' in obj.name
    ex, ez = (.43,.61) if is_pillow else (.26,.36)
    for j in range(rings+1):
        v = -math.pi/2 + math.pi*j/rings
        cv = signed_power(math.cos(v), ez)
        for i in range(segments):
            u = math.tau*i/segments
            x = radii[0]*cv*signed_power(math.cos(u), ex)
            y = radii[1]*cv*signed_power(math.sin(u), ex)
            z = radii[2]*signed_power(math.sin(v), ez)
            # Broad fabric tension and a few millimetres of seam gathering.
            z += .005*math.sin(x*29+y*9)*math.sin(y*17)*math.cos(v)**2
            if is_pillow:
                z -= .009*math.exp(-((x/radii[0])**2+(y/radii[1])**2)*4)*max(0,math.sin(v))
            verts.append((x,y,z))
    for j in range(rings):
        for i in range(segments):
            a=j*segments+i; b=j*segments+(i+1)%segments
            faces.append((a,b,b+segments,a+segments))
    mesh = bpy.data.meshes.new(obj.name+' tailored surface')
    mesh.from_pydata(verts, [], faces)
    for m in obj.data.materials:
        mesh.materials.append(m)
    obj.data = mesh
    obj.scale = (1,1,1)
    obj.modifiers.clear()
    for p in mesh.polygons:
        p.use_smooth = True
    points=[]
    for i in range(129):
        a=math.tau*i/128
        points.append((radii[0]*1.002*signed_power(math.cos(a),ex),
                       radii[1]*1.002*signed_power(math.sin(a),ex),0))
    seam = c.tube('Detail | '+obj.name+' sewn welt', points, .0022,
                  'Detail | pale stitch' if is_pillow else 'Detail | stitch', obj)
    seam['detail'] = 'continuous sewn edge'


def cloth(name, parent, width, y0, y1, height, material, drop=.13, folds=.014):
    verts, faces=[],[]
    nx, ny=64,48
    for j in range(ny+1):
        t=j/ny
        y=y0+(y1-y0)*t
        for i in range(nx+1):
            s=i/nx*2-1
            x=s*width/2
            z=height-drop*abs(s)**14-.07*(1-t)**22
            z+=folds*(math.sin(x*16+y*8)*.55+math.sin(x*29-y*5)*.25+math.sin(y*22+x*3)*.20)
            z+=.019*math.exp(-((x+.25)**2/.07+(t-.45)**2/.2))
            if 'runner' in name:
                z+=.005*(math.cos(x*32+y*32)+math.cos(x*32-y*32))
            verts.append((x,y,z))
    for j in range(ny):
        for i in range(nx):
            a=j*(nx+1)+i
            faces.append((a,a+1,a+nx+2,a+nx+1))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    obj=c.register(bpy.data.objects.new(name,mesh),name,material,parent)
    for p in mesh.polygons:
        p.use_smooth=True
    solid=obj.modifiers.new('Linen hem thickness','SOLIDIFY')
    solid.thickness=.009
    sub=obj.modifiers.new('Soft fabric folds','SUBSURF')
    sub.levels=1
    for edge in (0,nx):
        pts=[verts[j*(nx+1)+edge] for j in range(ny+1)]
        c.tube(name+' bound side hem',pts,.003,'Detail | pale stitch',parent)
    return obj


def rounded_points(width,depth,radius,steps=12):
    pts=[]
    for cx,cy,start in [(width/2-radius,depth/2-radius,0),(-width/2+radius,depth/2-radius,90),
                         (-width/2+radius,-depth/2+radius,180),(width/2-radius,-depth/2+radius,270)]:
        for i in range(steps+1):
            a=math.radians(start+i*90/steps)
            pts.append((cx+radius*math.cos(a),cy+radius*math.sin(a)))
    return pts


def rounded_slab(name,loc,size,mat,radius,parent=None):
    pts=rounded_points(size[0],size[1],radius)
    count=len(pts)
    verts=[(x,y,z) for z in (-size[2]/2,size[2]/2) for x,y in pts]
    faces=[tuple(reversed(range(count))),tuple(range(count,count*2))]
    faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    obj=c.register(bpy.data.objects.new(name,mesh),name,mat,parent)
    obj.location=loc
    bevel=obj.modifiers.new('Rounded finish edge','BEVEL')
    bevel.width=min(.007,size[2]*.20)
    bevel.segments=3
    obj.modifiers.new('Crafted surface normals','WEIGHTED_NORMAL')
    return obj


def furniture():
    c.collection('17 Detail | Tailored furniture')
    for obj in list(bpy.data.objects):
        if obj.type!='MESH':
            continue
        name=obj.name
        upholstered=any(k in name for k in ('soft pillow','accent pillow','pale pillow','rust accent','seat','back cushion','chaise cushion','sectional arm','sleeper sofa arm','padded headboard','upholstered base','mattress'))
        if upholstered and not name.startswith('Toilet'):
            pillow_mesh(obj)
        if 'pillow piping' in name:
            remove_object(obj)
    for name,width in [('Parents double bed',1.82),('Child single bed',.99)]:
        root=bpy.data.objects[name]
        for obj in list(root.children):
            if any(k in obj.name for k in ('draped duvet','folded throw')) or obj.name==name+' duvet':
                remove_object(obj)
        cloth(name+' detailed duvet',root,width+.11,-1.09,.43,.727,'linen light',.12,.026)
        cloth(name+' textured bed runner',root,width+.13,-1.095,-.52,.773,'Detail | quilted flax',.115,.028)
        cloth(name+' turned linen cuff',root,width+.065,.20,.47,.744,'linen light',.075,.005)
    # Broad radii belong to the plan shape, independently of the thin tabletop.
    for name,radius in [('Dining table rounded top',.20),('Coffee table oak top',.22),
                        ('Living wool rug',.12),('Parents wool rug',.08),('Office rug',.10),('Bathroom bathmat',.07)]:
        old=bpy.data.objects[name]
        loc=old.location.copy(); size=old.dimensions.copy(); material=old.data.materials[0]
        remove_object(old)
        obj=rounded_slab(name,loc,size,material,radius)
        if 'rug' in name or 'bathmat' in name:
            pts=rounded_points(size.x-.028,size.y-.028,radius-.012)
            c.tube('Detail | '+name+' bound edge',[(x,y,size.z/2+.001) for x,y in pts+[pts[0]]],.0035,'Detail | stitch',obj)
    # Bent upholstered dining-chair backs with a gentle concave inner surface.
    for obj in list(bpy.data.objects):
        if obj.type!='MESH' or not obj.name.startswith('Dining chair') or ' back' not in obj.name:
            continue
        obj.modifiers.clear()
        verts=[]
        for j in range(9):
            z=-.215+j*.43/8
            for i in range(25):
                x=-.235+i*.47/24
                y=-.045*(x/.235)**2
                verts.append((x,y,z))
        faces=[(j*25+i,j*25+i+1,(j+1)*25+i+1,(j+1)*25+i) for j in range(8) for i in range(24)]
        mesh=bpy.data.meshes.new(obj.name+' curved shell')
        mesh.from_pydata(verts,[],faces); mesh.materials.append(c.M['linen'])
        obj.data=mesh
        for p in mesh.polygons: p.use_smooth=True
        mod=obj.modifiers.new('Padded shell thickness','SOLIDIFY'); mod.thickness=.055
        mod=obj.modifiers.new('Soft rim','BEVEL'); mod.width=.021; mod.segments=4


def basin(name,loc,width,depth,height,material,parent=None):
    """Continuous rim and concave basin, including a real drain at the bottom."""
    verts=[]
    scale=min(1, min(width,depth)/.43)
    layers=[(width,depth,.065*scale,0),(width,depth,.065*scale,height),
            (width-.065*scale,depth-.065*scale,.075*scale,height+.001),
            (width-.10*scale,depth-.10*scale,.075*scale,height-.035*scale),
            (width-.18*scale,depth-.18*scale,.065*scale,.026*scale)]
    for w,d,r,z in layers:
        verts.extend((x,y,z) for x,y in rounded_points(w,d,min(r,d/2-.002)))
    count=len(verts)//len(layers)
    faces=[]
    for level in range(len(layers)-1):
        for i in range(count):
            a=level*count+i; b=level*count+(i+1)%count
            faces.append((a,b,b+count,a+count))
    faces.append(tuple(range((len(layers)-1)*count,len(layers)*count)))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    obj=c.register(bpy.data.objects.new(name,mesh),name,material,parent)
    obj.location=loc
    for p in mesh.polygons: p.use_smooth=len(p.vertices)==4
    mod=obj.modifiers.new('Porcelain radius','BEVEL'); mod.width=.006; mod.segments=3
    obj.modifiers.new('Basin weighted normals','WEIGHTED_NORMAL')
    if width>.2:
        c.cylinder(name+' drain',(0,0,.030),.021,.006,'Detail | brushed nickel',obj)
    return obj


def wet_rooms():
    c.collection('18 Detail | Kitchen and bathroom')
    for obj in list(bpy.data.objects):
        if obj.name.startswith(('Washbasin','Sink recessed basin','Sink interior shadow','Sink drain')):
            remove_object(obj)
    for i,x in enumerate((8.98,9.85)):
        basin('Washbasin' if i==0 else 'Washbasin.001',(x,3.94,.94),.61,.43,.14,'porcelain')
        # Overflow opening at the inner rear rim, no invented branding.
        c.cube('Detail | basin overflow',(x,4.109,1.036),(.046,.006,.011),'charcoal',.004)
    # Carve the stone so the kitchen sink has actual depth below the worktop.
    top=bpy.data.objects['Kitchen north limestone worktop']
    cutter=rounded_slab('Detail | sink cutout',(1.77,6.43,.925),(.545,.395,.40),'black',.065)
    mod=top.modifiers.new('Inset sink opening','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
    bpy.context.view_layer.objects.active=top
    bpy.ops.object.modifier_apply(modifier=mod.name)
    remove_object(cutter)
    basin('Detail | undermount steel sink',(1.77,6.43,.785),.58,.43,.173,'Detail | sink steel')
    bpy.data.objects['Vanity mirror'].data.materials[0]=c.M['Detail | mirror']
    for name in ('Vanity drawer','Vanity drawer.001'):
        obj=bpy.data.objects.get(name)
        if obj:
            c.cube('Detail | vanity recessed pull',(obj.location.x,3.670,.796),(.66,.016,.013),'oak dark',.004)
    # Fine tile joints on the fixed shower support follow its real retained geometry.
    for z in (.61,1.21,1.81):
        c.cube('Detail | shower horizontal joint',(7.74,4.179,z),(1.32,.002,.0025),'grout',0)
    for x in (7.37,7.97):
        c.cube('Detail | shower vertical joint',(x,4.178,1.05),(.0025,.002,2.08),'grout',0)
    for y in (3.25,4.08):
        c.cube('Detail | glass clamp',(8.414,y,.16),(.044,.05,.062),'Detail | brushed nickel',.004)
    for x in (7.65,7.79):
        c.cylinder('Detail | shower valve',(x,4.066,1.05),.025,.033,'Detail | brushed nickel',rotation=(math.pi/2,0,0))
    c.tube('Detail | hand shower hose',[(7.87,4.12,1.01),(8.01,4.06,.65),(8.12,4.07,.58),(8.18,4.10,.72),(8.16,4.10,1.37)],.009,'Detail | brushed nickel')
    c.cylinder('Detail | hand shower',(8.16,4.10,1.46),.023,.20,'Detail | brushed nickel')
    c.cylinder('Detail | soap dispenser',(10.18,3.98,1.02),.043,.14,'porcelain')
    c.tube('Detail | soap pump',[(10.18,3.98,1.09),(10.18,3.98,1.13),(10.12,3.98,1.13)],.008,'Detail | brushed nickel')
    for i in range(3):
        rounded_slab('Detail | folded laundry towel',(8.66,1.42,.981+i*.045),(.42,.31,.042),'linen light' if i!=1 else 'linen taupe',.024)
    # Machine glass gets a visible drum, moulded rim, hinge and detergent drawer.
    for name in ('Washing machine','Dryer'):
        root=bpy.data.objects[name]
        c.cylinder('Detail | '+name+' drum',(0,-.369,.43),.143,.008,'Detail | smoked appliance glass',root,(math.pi/2,0,0))
        c.ring('Detail | '+name+' dark glass edge',(0,-.38,.43),.153,.011,'charcoal',root,(math.pi/2,0,0))
        c.cube('Detail | '+name+' door grip',(.163,-.397,.45),(.03,.017,.11),'white',.012,root)
        c.cube('Detail | '+name+' detergent drawer',(-.185,-.35,.782),(.13,.006,.065),'ivory cabinet',.005,root)


def joinery():
    c.collection('19 Detail | Architectural finishes')
    # Do not bevel the artificial horizontal split used only for the animation.
    # Its meeting faces remain flush while vertical, manufactured edges stay soft.
    bpy.context.view_layer.update()
    for obj in list(bpy.data.objects):
        if obj.type!='MESH' or not any(k in obj.name for k in (' upper',' lower',' retained')):
            continue
        split_edges=[edge.index for edge in obj.data.edges
                     if all(abs((obj.matrix_world @ obj.data.vertices[i].co).z-.97)<.0001 for i in edge.vertices)]
        if not split_edges:
            continue
        weight=obj.data.attributes.get('bevel_weight_edge') or obj.data.attributes.new('bevel_weight_edge','FLOAT','EDGE')
        for i,value in enumerate(weight.data):
            value.value=0 if i in split_edges else 1
        for mod in obj.modifiers:
            if mod.type=='BEVEL':
                mod.limit_method='WEIGHT'
    # Door halves share their hinge/frame coordinate system, including the grain.
    shared={}
    for obj in list(bpy.data.objects):
        if obj.type!='MESH' or not obj.parent or not obj.data.materials:
            continue
        parent=obj.parent
        if not (parent.name.endswith(' hinge') or 'room_access' in parent):
            continue
        old=obj.data.materials[0]
        if not ('oak' in old.name):
            continue
        key=(parent.name,old.name)
        if key not in shared:
            material=old.copy()
            material.name='Detail | '+parent.name+' timber'+(' | shell' if old.name.endswith(' | shell') else '')
            for node in material.node_tree.nodes:
                if node.type=='TEX_COORD':
                    node.object=parent
                if node.type=='VECT_MATH' and node.operation=='ADD':
                    for link in list(node.inputs[1].links):
                        material.node_tree.links.remove(link)
                    node.inputs[1].default_value=(0,0,0)
            shared[key]=material
        obj.data.materials[0]=shared[key]
    for obj in list(bpy.data.objects):
        if 'rear skirting' in obj.name:
            remove_object(obj)
    for obj in list(bpy.data.objects):
        if obj.type!='MESH' or 'retained' not in obj.name or not obj.data.materials:
            continue
        if obj.data.materials[0].name not in ('plaster','wall interior'):
            continue
        loc=obj.location; size=obj.dimensions
        if loc.z-size.z/2>.03 or size.z<.14:
            continue
        if size.y<.35 and size.x>.2:
            for side in (-1,1):
                y=loc.y+side*(size.y/2+.009)
                if .002<y<10.798:
                    c.cube('Detail | continuous skirting',(loc.x,y,.064),(size.x,.018,.092),'white',.003)
        elif size.x<.35 and size.y>.2:
            for side in (-1,1):
                x=loc.x+side*(size.x/2+.009)
                if .002<x<11.398:
                    c.cube('Detail | continuous skirting',(x,loc.y,.064),(.018,size.y,.092),'white',.003)
    for root in [o for o in bpy.data.objects if 'room_access' in o]:
        if root['room_access'] in ('Utility electrical','Bathroom WC','Entrance'):
            c.cube('Detail | flush floor threshold',(0,0,.021),(root['clear_width']+.02,.09,.006),'Detail | brushed nickel',.002,root)
    # Furniture faces get fine reveals and restrained handles rather than extra objects.
    media=bpy.data.objects['Media sideboard']
    for y in (2.30,2.87,3.44):
        c.cube('Detail | sideboard inset front',(4.849,y,.38),(.024,.55,.51),'oak',.005)
        c.cube('Detail | sideboard finger reveal',(4.832,y,.606),(.012,.44,.010),'oak dark',.002)
    for x in (8.49,9.41):
        c.cube('Detail | office storage pull',(x,10.215,.68),(.24,.02,.012),'charcoal',.004)


def props():
    c.collection('20 Detail | Restrained room accessories')
    # Ceramic pieces have an inner surface and lip, avoiding solid primitive tops.
    old=bpy.data.objects['Coffee cup']; remove_object(old)
    basin('Coffee cup',(2.73,1.77,.443),.087,.082,.074,'porcelain')
    c.cylinder('Detail | coffee surface',(2.73,1.77,.501),.027,.001,'Detail | coffee')
    c.ring('Detail | coffee cup handle',(2.783,1.77,.485),.026,.006,'porcelain',rotation=(math.pi/2,0,0))
    for i,(w,d,z) in enumerate([(.26,.20,.455),(.23,.18,.482)]):
        if i:
            rounded_slab('Detail | coffee table second book',(2.47,1.61,z),(w,d,.023),'linen taupe',.004)
    c.plant('Detail | coffee table plant',2.93,1.83,.441,.15)
    # A small olive/sage accent is repeated just once in the guest room.
    pillow=bpy.data.objects['Guest sleeper sofa pale pillow']
    pillow.data.materials[0]=c.M['Detail | soft sage']
    # Visible flat leaves with a slight central fold, replacing the original oval blobs.
    for obj in list(bpy.data.objects):
        if (obj.type!='MESH' or ' leaf' not in obj.name or not obj.data.materials
                or obj.data.materials[0].name not in ('green', 'green light')):
            continue
        sx,sy,sz=obj.scale
        verts=[]
        for j in range(13):
            t=j/12; y=(t*2-1)*sy
            w=math.sin(math.pi*t)**.78*sx
            verts.extend([(-w,y,.016*math.sin(math.pi*t)),(0,y,.035*math.sin(math.pi*t)),(w,y,.012*math.sin(math.pi*t))])
        faces=[]
        for j in range(12):
            for i in range(2):
                a=j*3+i; faces.append((a,a+1,a+4,a+3))
        mesh=bpy.data.meshes.new(obj.name+' folded leaf')
        mesh.from_pydata(verts,[],faces)
        for m in obj.data.materials: mesh.materials.append(m)
        obj.data=mesh; obj.scale=(1,1,1)
        for p in mesh.polygons: p.use_smooth=True
        mod=obj.modifiers.new('Leaf thickness','SOLIDIFY'); mod.thickness=.001


def main():
    if Path(bpy.data.filepath).resolve()!=SOURCE.resolve():
        raise RuntimeError('Load the original architectural R3 source; refinement is a separate reproducible derivative.')
    scene=bpy.context.scene
    scene.frame_set(62)
    materials()
    furniture()
    wet_rooms()
    joinery()
    props()
    scene['R3 detail revision']='r3-detail-01: tailored upholstery, folded linen, oak variation, stone, joinery, hollow basins'
    scene['R3 detail source']=str(SOURCE)
    scene['R3 detail workflow']='Recreate only from baseline using blender/house_r3/refine.py. Edit this native file directly for manual refinements.'
    scene.render.engine='CYCLES'
    scene.cycles.samples=48
    scene.cycles.use_denoising=True
    scene.cycles.adaptive_threshold=.04
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.camera=bpy.data.objects['Camera | Open R3']
    scene.render.resolution_x=1400
    scene.render.resolution_y=1400
    bpy.ops.file.pack_all()
    OUT.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(DETAIL),compress=True)
    report={'source':str(SOURCE),'detail':str(DETAIL),'objects':len(bpy.data.objects),
            'materials':len(bpy.data.materials),'detailObjects':sum(o.name.startswith('Detail |') for o in bpy.data.objects)}
    (OUT/'refinement-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('R3_DETAIL_SAVED',json.dumps(report),flush=True)


if __name__=='__main__':
    main()
