"""Small native-mesh toolkit; dimensions in metres, no imported house geometry."""
import math
import random
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
M = {}
COL = None
PARENT = None
ROOM = ''
RNG = random.Random(40609)


def collection(name, parent=None, room=''):
    global COL, PARENT, ROOM
    COL = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if COL.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(COL)
    PARENT, ROOM = parent, room
    return COL


def register(o, mat=None, parent=None):
    COL.objects.link(o)
    o.parent = parent if parent is not None else PARENT
    if mat:
        o.data.materials.append(M[mat] if isinstance(mat, str) else mat)
    if ROOM:
        o['room'] = ROOM
    o['reference_revision'] = 'v4-reference-01'
    return o


def empty(name, loc=(0, 0, 0), angle=0, parent=None):
    o = register(bpy.data.objects.new(name, None), parent=parent)
    o.location = loc
    o.rotation_euler.z = angle
    o.empty_display_size = .18
    return o


def mesh(name, verts, faces, mat, parent=None, bevel=0, smooth=False):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    o = register(bpy.data.objects.new(name, data), mat, parent)
    for face in data.polygons:
        face.use_smooth = smooth
    if bevel:
        b = o.modifiers.new('Manufactured edge radius', 'BEVEL')
        b.width, b.segments = bevel, 3
        n = o.modifiers.new('Weighted face normals', 'WEIGHTED_NORMAL')
        n.keep_sharp = True
    return o


def box(name, loc, size, mat, bevel=.012, parent=None, angle=0):
    x, y, z = (v / 2 for v in size)
    verts = [(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
    faces = [(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]
    o = mesh(name, verts, faces, mat, parent, min(bevel, min(size)*.45))
    o.location = loc
    o.rotation_euler.z = angle
    return o


def cylinder(name, loc, radius, depth, mat, parent=None, rotation=(0,0,0), vertices=40):
    verts = [(radius*math.cos(i*math.tau/vertices), radius*math.sin(i*math.tau/vertices), z)
             for z in [-depth/2,depth/2] for i in range(vertices)]
    faces = [tuple(reversed(range(vertices))), tuple(range(vertices,2*vertices))]
    faces += [(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
    o = mesh(name,verts,faces,mat,parent,min(.007,radius*.1,depth*.15))
    for face in o.data.polygons:
        face.use_smooth = len(face.vertices)==4
    o.location, o.rotation_euler = loc, rotation
    return o


def tube(name, points, radius, mat, parent=None, cyclic=False):
    data = bpy.data.curves.new(name,'CURVE')
    data.dimensions='3D'
    data.bevel_depth, data.bevel_resolution = radius, 3
    spline=data.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p, co in zip(spline.points,points): p.co=(*co,1)
    spline.use_cyclic_u=cyclic
    return register(bpy.data.objects.new(name,data),mat,parent)


def rod(name, a, b, radius, mat, parent=None):
    return tube(name,[a,b],radius,mat,parent)


def lathe(name, loc, profile, mat, parent=None, segments=64, scale=(1,1,1)):
    verts=[(r*math.cos(a*math.tau/segments),r*math.sin(a*math.tau/segments),z)
           for r,z in profile for a in range(segments)]
    faces=[(j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i)
           for j in range(len(profile)-1) for i in range(segments)]
    o=mesh(name,verts,faces,mat,parent,smooth=True)
    o.location,o.scale=loc,scale
    return o


def soft(name, loc, size, mat, parent=None, exponent=.38, rotation=(0,0,0), seam=False):
    def power(v): return math.copysign(abs(v)**exponent,v)
    seg,rings=48,24
    verts=[]
    for j in range(rings+1):
        phi=-math.pi/2+math.pi*j/rings
        for i in range(seg):
            a=math.tau*i/seg
            verts.append((size[0]/2*power(math.cos(phi))*power(math.cos(a)),
                          size[1]/2*power(math.cos(phi))*power(math.sin(a)),
                          size[2]/2*power(math.sin(phi))))
    faces=[(j*seg+i,j*seg+(i+1)%seg,(j+1)*seg+(i+1)%seg,(j+1)*seg+i)
           for j in range(rings) for i in range(seg)]
    o=mesh(name,verts,faces,mat,parent,smooth=True)
    o.location,o.rotation_euler=loc,rotation
    if seam:
        points=[(size[0]/2*power(math.cos(i*math.tau/128)),size[1]/2*power(math.sin(i*math.tau/128)),size[2]*.22)
                for i in range(128)]
        tube(name+' | sewn piping',points,.0025,'seam',o,True)
    return o


def material(name,color,rough=.6,metal=0,bump=0):
    m=bpy.data.materials.new('V4 | '+name)
    m.use_nodes=True
    m.diffuse_color=(*color,1)
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal
    if bump:
        coord=m.node_tree.nodes.new('ShaderNodeTexCoord')
        n=m.node_tree.nodes.new('ShaderNodeTexNoise')
        n.inputs['Scale'].default_value=500 if name in ['linen','linen white','taupe','olive','seam'] else 90 if name in ['plaster','stone','tile','rug'] else 170
        n.inputs['Detail'].default_value=3
        m.node_tree.links.new(coord.outputs['Object'],n.inputs['Vector'])
        ramp=m.node_tree.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color=(*[v*.89 for v in color],1)
        ramp.color_ramp.elements[1].color=(*[min(1,v*1.05) for v in color],1)
        m.node_tree.links.new(n.outputs['Fac'],ramp.inputs[0])
        m.node_tree.links.new(ramp.outputs[0],p.inputs['Base Color'])
        b=m.node_tree.nodes.new('ShaderNodeBump')
        b.inputs['Strength'].default_value=.65 if name in ['plaster','stone','tile','rug'] else .25
        b.inputs['Distance'].default_value=min(bump,.0007) if name in ['linen','linen white','taupe','olive','seam'] else bump
        m.node_tree.links.new(n.outputs['Fac'],b.inputs['Height'])
        m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
    M[name]=m
    return m


def palette():
    for name,col,rough,metal,bump in [
        ('plaster',(.79,.765,.715),.82,0,.006),('cut',(.14,.155,.15),.75,0,.0002),
        ('oak',(.48,.31,.16),.47,0,0),('oak pale',(.61,.46,.29),.49,0,0),
        ('oak dark',(.21,.125,.063),.5,0,0),('charcoal',(.052,.061,.065),.37,.55,.00015),
        ('roof',(.060,.069,.080),.65,.22,.0002),('pv',(.018,.025,.040),.43,.10,0),
        ('pv grid',(.050,.068,.092),.56,.15,0),('linen',(.50,.46,.385),.93,0,.002),
        ('linen white',(.75,.715,.64),.94,0,.0018),('taupe',(.35,.30,.235),.94,0,.002),
        ('olive',(.20,.24,.13),.93,0,.0015),('rug',(.33,.285,.21),.96,0,.005),
        ('seam',(.47,.43,.36),.9,0,.0003),('stone',(.53,.505,.45),.72,0,.004),
        ('tile',(.45,.445,.395),.58,0,.0012),('grout',(.31,.305,.27),.91,0,.0006),
        ('ceramic',(.84,.83,.79),.2,0,0),('white appliance',(.75,.77,.75),.3,.1,.0001),
        ('steel',(.43,.45,.45),.24,.85,0),('black',(.013,.016,.017),.45,.1,0),
        ('leaf',(.14,.21,.062),.69,0,.0003),('leaf light',(.235,.29,.095),.72,0,.0003),
        ('soil',(.055,.044,.027),1,0,.006),('bark',(.14,.105,.06),.88,0,.004),
        ('red',(.47,.025,.035),.46,0,0),('blue',(.025,.11,.22),.49,0,0),
        ('paper',(.74,.70,.58),.86,0,.0003),('book olive',(.17,.20,.13),.83,0,.0002),
        ('brass',(.46,.29,.115),.32,.7,0),('studio',(.95,.95,.95),.82,0,0)
    ]: material(name,col,rough,metal,bump)
    for name in ['stone','tile']:
        m=M[name];nodes,links=m.node_tree.nodes,m.node_tree.links
        shader=nodes.get('Principled BSDF')
        coord=nodes.get('Texture Coordinate')
        mineral=nodes.new('ShaderNodeTexNoise');mineral.inputs['Scale'].default_value=4.5;mineral.inputs['Detail'].default_value=4
        links.new(coord.outputs['Object'],mineral.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB')
        base=tuple(m.diffuse_color)[:3]
        ramp.color_ramp.elements[0].color=(*[v*.77 for v in base],1)
        ramp.color_ramp.elements[1].color=(*[v*1.08 for v in base],1)
        links.new(mineral.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],shader.inputs['Base Color'])
    image=bpy.data.images.load(str(ROOT/'assets/third-party/polyhaven/oak_veneer_01/oak_veneer_01_diff_1k.jpg'),check_existing=True)
    image.pack()
    for name,tint in [('oak',(.39,.255,.13)),('oak pale',(.43,.30,.17)),('oak dark',(.22,.12,.055))]:
        m=M[name]; n,l=m.node_tree.nodes,m.node_tree.links
        p=n.get('Principled BSDF')
        coord=n.new('ShaderNodeTexCoord')
        scale=n.new('ShaderNodeVectorMath'); scale.operation='MULTIPLY';scale.inputs[1].default_value=(.45,.45,.45)
        l.new(coord.outputs['Object'],scale.inputs[0])
        tex=n.new('ShaderNodeTexImage');tex.image=image;tex.projection='BOX';tex.projection_blend=.12
        info=n.new('ShaderNodeObjectInfo')
        shift=n.new('ShaderNodeVectorMath');shift.operation='ADD'
        l.new(scale.outputs[0],shift.inputs[0]);l.new(info.outputs['Random'],shift.inputs[1])
        l.new(shift.outputs[0],tex.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.08
        ramp.color_ramp.elements[0].color=(*[v*.38 for v in tint],1)
        ramp.color_ramp.elements[1].position=.58
        ramp.color_ramp.elements[1].color=(*tint,1)
        l.new(tex.outputs['Color'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
        bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00065;bump.inputs['Strength'].default_value=.23
        l.new(tex.outputs['Color'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    for name in ['linen','linen white','taupe','olive','rug']:
        M[name].node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.24
    for name in ['roof','pv']:
        shader=M[name].node_tree.nodes.get('Principled BSDF')
        shader.inputs['Specular IOR Level'].default_value=.12 if name=='roof' else 0
        shader.inputs['Metallic'].default_value=.10 if name=='roof' else 0
    glass=material('glass',(.94,.98,1),.06)
    p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.46
    material('light',(.95,.61,.26),.28)
    p=M['light'].node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.46,.18,1);p.inputs['Emission Strength'].default_value=2.2
    material('led',(.04,.3,.55),.3)
    p=M['led'].node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.03,.4,1,1);p.inputs['Emission Strength'].default_value=1


def area(name,loc,target,power,size,color=(1,.46,.18),parent=None):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
    o=register(bpy.data.objects.new(name,data),parent=parent)
    o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    return o
