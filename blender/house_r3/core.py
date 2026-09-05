"""Native Blender modelling helpers for the R3 residential pavilion."""
import math
import random
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
M = {}
CURRENT = None
SHELL = []
ROOF = []
ROOM = None
RNG = random.Random(32026)


def collection(name):
    global CURRENT
    name = 'R3 | ' + name
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    CURRENT = c
    return c


def register(o, name, material=None, parent=None):
    o.name = name
    for c in list(o.users_collection):
        c.objects.unlink(o)
    CURRENT.objects.link(o)
    if material:
        o.data.materials.append(M[material] if isinstance(material, str) else material)
    if parent:
        o.parent = parent
    if ROOM:
        o['room'] = ROOM
    return o


def empty(name, loc=(0, 0, 0), rotation=0, parent=None):
    o = bpy.data.objects.new(name, None)
    CURRENT.objects.link(o)
    o.location = loc
    o.rotation_euler.z = rotation
    o.empty_display_type = 'PLAIN_AXES'
    o.empty_display_size = .25
    if parent:
        o.parent = parent
    if ROOM:
        o['room'] = ROOM
    return o


def cube(name, loc, size, mat, bevel=.015, parent=None):
    x,y,z=(v/2 for v in size)
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)],[],
                     [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)])
    o=register(bpy.data.objects.new(name,mesh),name,mat,parent)
    o.location=loc
    if bevel:
        b = o.modifiers.new('Soft manufactured edges', 'BEVEL')
        b.width = min(bevel, min(size) * .45)
        b.segments = 3
        b = o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
        b.keep_sharp = True
    return o


def sphere(name, loc, size, mat, parent=None):
    verts=[]
    seg,rings=24,12
    for j in range(rings+1):
        phi=math.pi*j/rings
        for i in range(seg):
            theta=math.tau*i/seg
            verts.append((math.sin(phi)*math.cos(theta),math.sin(phi)*math.sin(theta),math.cos(phi)))
    faces=[]
    for j in range(rings):
        for i in range(seg):
            a=j*seg+i; b=j*seg+(i+1)%seg
            faces.append((a,a+seg,b+seg,b))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    o=register(bpy.data.objects.new(name,mesh),name,mat,parent)
    o.location=loc
    o.scale = size
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def cylinder(name, loc, radius, depth, mat, parent=None, rotation=None, vertices=32):
    verts=[(radius*math.cos(math.tau*i/vertices),radius*math.sin(math.tau*i/vertices),z) for z in (-depth/2,depth/2) for i in range(vertices)]
    faces=[tuple(reversed(range(vertices))),tuple(range(vertices,vertices*2))]
    faces.extend((i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    o=register(bpy.data.objects.new(name,mesh),name,mat,parent)
    o.location=loc
    if rotation:
        o.rotation_euler = rotation
    b = o.modifiers.new('Edge radius', 'BEVEL')
    b.width = min(.012, depth * .12, radius * .12)
    b.segments = 2
    o.modifiers.new('Normals', 'WEIGHTED_NORMAL')
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return o


def tube(name, points, radius, mat, parent=None):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.bevel_depth = radius
    c.bevel_resolution = 3
    s = c.splines.new('POLY')
    s.points.add(len(points) - 1)
    for p, co in zip(s.points, points):
        p.co = (*co, 1)
    o = bpy.data.objects.new(name, c)
    CURRENT.objects.link(o)
    c.materials.append(M[mat])
    if parent:
        o.parent = parent
    return o


def ring(name, loc, major, minor, mat, parent=None, rotation=None):
    verts=[]
    for i in range(40):
        a=math.tau*i/40
        for j in range(8):
            b=math.tau*j/8
            verts.append(((major+minor*math.cos(b))*math.cos(a),(major+minor*math.cos(b))*math.sin(a),minor*math.sin(b)))
    faces=[(i*8+j,((i+1)%40)*8+j,((i+1)%40)*8+(j+1)%8,i*8+(j+1)%8) for i in range(40) for j in range(8)]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    o=register(bpy.data.objects.new(name,mesh),name,mat,parent)
    o.location=loc
    if rotation:
        o.rotation_euler = rotation
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def material(name, color, rough=.5, metallic=0, noise=0, scale=120):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    ns = m.node_tree.nodes
    links = m.node_tree.links
    p = ns.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metallic
    if noise:
        t = ns.new('ShaderNodeTexNoise')
        t.inputs['Scale'].default_value = scale
        t.inputs['Detail'].default_value = 2
        b = ns.new('ShaderNodeBump')
        b.inputs['Strength'].default_value = .22
        b.inputs['Distance'].default_value = noise
        links.new(t.outputs['Fac'], b.inputs['Height'])
        links.new(b.outputs['Normal'], p.inputs['Normal'])
    M[name] = m
    return m


def fade_material(base, group='shell'):
    name = base + ' | ' + group
    if name in M:
        return M[name]
    m = M[base].copy()
    m.name = name
    n = m.node_tree.nodes
    l = m.node_tree.links
    p = n.get('Principled BSDF')
    out = n.get('Material Output')
    tr = n.new('ShaderNodeBsdfTransparent')
    mix = n.new('ShaderNodeMixShader')
    mix.name = 'Visibility'
    mix.inputs[0].default_value = 1
    l.new(tr.outputs[0], mix.inputs[1])
    l.new(p.outputs[0], mix.inputs[2])
    l.new(mix.outputs[0], out.inputs['Surface'])
    M[name] = m
    if group=='roof':
        ROOF.append(m)
    elif group=='shell':
        SHELL.append(m)
    return m


def palette():
    material('plaster', (.72, .70, .64), .85, noise=.018, scale=150)
    material('wall interior', (.73, .70, .64), .82, noise=.009)
    material('cut edge', (.21, .23, .22), .78)
    material('stone', (.60, .57, .51), .86, noise=.017, scale=65)
    material('grout', (.39, .37, .32), .9)
    material('tile', (.36, .38, .36), .77, noise=.009, scale=80)
    material('white', (.80, .79, .74), .44)
    material('ivory cabinet', (.63, .62, .55), .53)
    material('oak', (.44, .28, .13), .55, noise=.005, scale=170)
    material('oak light', (.58, .41, .24), .6, noise=.004)
    material('oak dark', (.24, .13, .055), .55)
    material('charcoal', (.035, .045, .042), .44, metallic=.35)
    material('black', (.012, .016, .017), .43)
    material('metal', (.4, .44, .43), .3, metallic=.85)
    material('porcelain', (.85, .86, .83), .22)
    material('linen', (.63, .59, .51), .96, noise=.007, scale=200)
    material('linen light', (.81, .77, .68), .98, noise=.006, scale=190)
    material('linen taupe', (.45, .42, .36), .96, noise=.007, scale=180)
    material('rust', (.32, .105, .060), .94, noise=.008)
    material('rug', (.49, .46, .39), 1, noise=.011, scale=240)
    material('green', (.13, .21, .060), .8)
    material('green light', (.23, .31, .11), .85)
    material('soil', (.05, .035, .020), 1)
    material('Hubmann red', (.58, .008, .016), .4)
    material('data blue', (.01, .24, .34), .4)
    material('PV cell', (.012, .030, .044), .24, metallic=.52)
    material('PV grid', (.14, .20, .23), .36, metallic=.7)
    material('roof gravel', (.36, .36, .31), 1, noise=.07, scale=65)
    material('glass', (.88, .94, .97), .035)
    p = M['glass'].node_tree.nodes.get('Principled BSDF')
    p.inputs['Transmission Weight'].default_value = .94
    p.inputs['IOR'].default_value = 1.45
    material('screen', (.014, .035, .040), .24)
    material('light', (1, .65, .32), .35)
    p = M['light'].node_tree.nodes.get('Principled BSDF')
    p.inputs['Emission Color'].default_value = (1, .65, .32, 1)
    p.inputs['Emission Strength'].default_value = 2.5
    # Texture mapping uses object-space metres, consistent across all oak pieces.
    image = bpy.data.images.load(str(ROOT / 'assets/third-party/polyhaven/oak_veneer_01/oak_veneer_01_diff_1k.jpg'))
    for key in ('oak', 'oak light', 'oak dark'):
        m = M[key]
        n, l = m.node_tree.nodes, m.node_tree.links
        coord = n.new('ShaderNodeTexCoord')
        mapping = n.new('ShaderNodeVectorMath')
        mapping.operation = 'MULTIPLY'
        mapping.inputs[1].default_value = (1.6, .28, 1.6)
        tex = n.new('ShaderNodeTexImage')
        tex.image = image
        tex.projection = 'BOX'
        tex.projection_blend = .22
        tint = n.new('ShaderNodeMixRGB')
        tint.blend_type = 'MIX'
        tint.inputs[0].default_value = .78
        tint.inputs[2].default_value = (*{'oak':(.40,.27,.15), 'oak light':(.57,.44,.30), 'oak dark':(.23,.14,.07)}[key], 1)
        l.new(coord.outputs['Object'], mapping.inputs[0])
        l.new(mapping.outputs[0], tex.inputs['Vector'])
        l.new(tex.outputs['Color'], tint.inputs[1])
        l.new(tint.outputs[0], n.get('Principled BSDF').inputs['Base Color'])


def area(name, loc, target, energy, size, color=(1, .91, .77), shape='DISK'):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy, data.shape, data.size, data.color = energy, shape, size, color
    o = bpy.data.objects.new(name, data)
    CURRENT.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()
    return o


def camera(name, loc, target, scale):
    data = bpy.data.cameras.new(name)
    data.type = 'ORTHO'
    data.ortho_scale = scale
    data.lens = 50
    data.clip_end = 250
    o = bpy.data.objects.new(name, data)
    CURRENT.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()
    return o


def key(obj, prop, frame, value):
    setattr(obj, prop, value)
    obj.keyframe_insert(data_path=prop, frame=frame)


def plant(name, x, y, z=0, scale=1):
    root = empty(name, (x, y, z))
    cylinder(name + ' ceramic pot', (0, 0, .19 * scale), .19 * scale, .38 * scale, 'stone', root)
    cylinder(name + ' soil', (0, 0, .375 * scale), .16 * scale, .012, 'soil', root)
    for i in range(13):
        a = i * 2.3999
        h = (.55 + RNG.random() * .5) * scale
        r = (.15 + RNG.random() * .25) * scale
        end = (math.cos(a) * r, math.sin(a) * r, h)
        tube(name + ' stem', [(0, 0, .3 * scale), (end[0] * .4, end[1] * .4, h * .7), end], .009 * scale, 'oak dark', root)
        leaf = sphere(name + ' leaf', end, (.075 * scale, .18 * scale, .025 * scale), 'green' if i % 3 else 'green light', root)
        leaf.rotation_euler = (.4, .4, a)
    return root
