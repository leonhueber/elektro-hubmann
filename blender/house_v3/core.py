"""Small, explicit primitives for the independent V3 scene (metres)."""
import math
import bpy
from mathutils import Vector

MATERIALS = {}
FADES = []
ACCENTS = {}
LAMPS = []
COLLECTION = None


def collection(name):
    global COLLECTION
    COLLECTION = bpy.data.collections.get('V3_' + name)
    if COLLECTION is None:
        COLLECTION = bpy.data.collections.new('V3_' + name)
        bpy.context.scene.collection.children.link(COLLECTION)
    return COLLECTION


def link(obj):
    for coll in list(obj.users_collection):
        coll.objects.unlink(obj)
    COLLECTION.objects.link(obj)
    return obj


def material(name, color, roughness=.5, metallic=0, emission=0, fade=False):
    mat = bpy.data.materials.new('V3 ' + name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Emission Color'].default_value = (*color, 1)
    bsdf.inputs['Emission Strength'].default_value = emission
    if fade:
        transparent = tree.nodes.new('ShaderNodeBsdfTransparent')
        mix = tree.nodes.new('ShaderNodeMixShader')
        mix.name = 'Shell visibility'
        mix.inputs[0].default_value = 1
        tree.links.new(transparent.outputs[0], mix.inputs[1])
        tree.links.new(bsdf.outputs[0], mix.inputs[2])
        tree.links.new(mix.outputs[0], tree.nodes.get('Material Output').inputs[0])
        mat.surface_render_method = 'BLENDED'
        FADES.append(mix.inputs[0])
    MATERIALS[name] = mat
    return mat


def palette():
    for name, color, rough, metal in [
        ('plaster', (.82,.80,.75), .72, 0),
        ('porcelain', (.93,.91,.85), .38, 0),
        ('concrete', (.48,.49,.47), .72, 0),
        ('oak', (.48,.27,.12), .45, 0),
        ('oak_light', (.66,.43,.22), .5, 0),
        ('charcoal', (.024,.033,.038), .60, .05),
        ('metal', (.16,.19,.2), .33, .65),
        ('glass', (.15,.24,.27), .18, .35),
        ('linen', (.67,.63,.54), .95, 0),
        ('cream', (.88,.83,.71), .85, 0),
        ('sage', (.22,.29,.24), .75, 0),
        ('pv', (.012,.032,.059), .48, .10),
        ('pv_line', (.1,.19,.23), .38, .3),
        ('soil', (.10,.08,.05), 1, 0),
        ('leaf', (.11,.22,.13), .8, 0),
        ('red', (.72,.014,.026), .35, .05),
    ]:
        material(name, color, rough, metal)
    for name in ('plaster','oak','charcoal','glass'):
        base = MATERIALS[name]
        bsdf = base.node_tree.nodes.get('Principled BSDF')
        material(name + '_shell', tuple(base.diffuse_color)[:3],
                 bsdf.inputs['Roughness'].default_value,
                 bsdf.inputs['Metallic'].default_value, fade=True)
    for name, color in [('installation',(.95,.024,.035)), ('network',(.04,.36,.52)),
                        ('smart',(.95,.04,.05)), ('security',(.95,.11,.035)),
                        ('energy',(.98,.23,.035))]:
        mat = material(name, color, .4, emission=.1)
        ACCENTS[name] = mat.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength']
    material('lamp', (1,.72,.36), .35, emission=.1)
    for name in ('pv','charcoal','metal'):
        MATERIALS[name].node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.18
    # Broad, restrained wood grain; no external texture dependency.
    for name in ('oak','oak_light','oak_shell'):
        tree = MATERIALS[name].node_tree
        noise = tree.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 4
        noise.inputs['Detail'].default_value = 2
        coords = tree.nodes.new('ShaderNodeTexCoord')
        mapping = tree.nodes.new('ShaderNodeVectorMath')
        mapping.operation = 'MULTIPLY'
        mapping.inputs[1].default_value = (1,18,3)
        tree.links.new(coords.outputs['Generated'], mapping.inputs[0])
        tree.links.new(mapping.outputs[0], noise.inputs['Vector'])
        bump = tree.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .12
        bump.inputs['Distance'].default_value = .018
        tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
        tree.links.new(bump.outputs[0], tree.nodes.get('Principled BSDF').inputs['Normal'])


def finish(obj, name, mat, parent=None):
    obj.name = 'V3 ' + name
    link(obj)
    if mat:
        obj.data.materials.append(MATERIALS[mat] if isinstance(mat, str) else mat)
    if parent:
        obj.parent = parent
    return obj


def box(name, loc, size, mat, bevel=.025, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(obj, name, mat, parent)
    if bevel:
        mod = obj.modifiers.new('Soft construction edge', 'BEVEL')
        mod.width = min(bevel, min(size) / 3)
        mod.segments = 2
        obj.modifiers.new('Corner normals', 'WEIGHTED_NORMAL')
    return obj


def cylinder(name, loc, radius, depth, mat, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth, location=loc)
    return finish(bpy.context.object, name, mat, parent)


def sphere(name, loc, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, location=loc)
    obj = bpy.context.object
    obj.scale = scale
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return finish(obj, name, mat)


def line(name, points, mat, radius=.018, parent=None):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 1
    data.bevel_depth = radius
    data.bevel_resolution = 2
    spline = data.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1)
    obj = bpy.data.objects.new('V3 ' + name, data)
    COLLECTION.objects.link(obj)
    data.materials.append(MATERIALS[mat])
    if parent:
        obj.parent = parent
    return obj


def empty(name):
    obj = bpy.data.objects.new('V3 ' + name, None)
    COLLECTION.objects.link(obj)
    obj.empty_display_type = 'PLAIN_AXES'
    obj.empty_display_size = .4
    return obj


def wedge(name, x, thickness, mat):
    """Upper side wall closes the real gap under the sloping roof."""
    vertices=[]
    for xx in (x-thickness/2,x+thickness/2):
        vertices.extend([(xx,-3.56,6.28),(xx,3.56,6.28),
                         (xx,3.56,7.154),(xx,-3.56,6.405)])
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),
                                 (1,2,6,5),(2,3,7,6),(3,0,4,7)])
    mesh.update()
    obj=bpy.data.objects.new('V3 '+name,mesh)
    COLLECTION.objects.link(obj)
    mesh.materials.append(MATERIALS[mat])
    return obj


def label(name, text, loc, size=.1, mat='porcelain', parent=None):
    data = bpy.data.curves.new(name, 'FONT')
    data.body = text
    data.size = size
    data.extrude = .001
    obj = bpy.data.objects.new('V3 ' + name, data)
    COLLECTION.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (math.pi/2,0,0)
    data.materials.append(MATERIALS[mat])
    if parent:
        obj.parent = parent
    return obj


def area(name, loc, target, power, size, color=(1,.93,.83)):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = power
    data.shape = 'DISK'
    data.size = size
    data.color = color
    obj = bpy.data.objects.new('V3 ' + name, data)
    COLLECTION.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj


def camera(name, loc, target, scale):
    data = bpy.data.cameras.new(name)
    data.type = 'ORTHO'
    data.ortho_scale = scale
    obj = bpy.data.objects.new('V3 ' + name, data)
    COLLECTION.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj
