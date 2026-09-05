"""Bake absolute progress into normal Blender keyframes, no runtime handlers."""
import bpy
from .core import FADES, ACCENTS, LAMPS, MATERIALS
from .systems import ROUTES


def ramp(p, start, end):
    t=max(0,min(1,(p-start)/(end-start)))
    return t*t*(3-2*t)


def band(p, a,b,c,d):
    return ramp(p,a,b)*(1-ramp(p,c,d))


def key(data, path, value, frame):
    setattr(data,path,value)
    data.keyframe_insert(data_path=path,frame=frame)


def bake(roof, blind, manifest):
    scene=bpy.context.scene
    count=manifest['frameCount']
    scene.frame_start=1
    scene.frame_end=count
    for chapter in manifest['chapters']:
        marker=scene.timeline_markers.new(chapter['id'],frame=round(chapter['rest']*(count-1))+1)
        marker.camera=bpy.data.objects['V3 Desktop']
    for i in range(count):
        frame=i+1; p=i/(count-1)
        opened=band(p,.10,.23,.93,1)
        roof_up=band(p,.10,.21,.76,.84)
        key(roof,'location',(0,0,.40+roof_up*1.12),frame)
        for socket in FADES:
            key(socket,'default_value',1-opened,frame)
        # Compress slat spacing from the fixed headrail, modelling a raised blind.
        shade=ramp(p,.525,.58)*(1-ramp(p,.90,.95))
        key(blind,'scale',(1,1,.10+.90*shade),frame)
        activity={
            'installation':band(p,.21,.29,.37,.415),
            'network':band(p,.28,.33,.37,.41),
            'smart':band(p,.51,.55,.63,.65),
            'security':band(p,.64,.675,.75,.775),
            'energy':band(p,.78,.84,.93,.97),
        }
        for system, curves in ROUTES.items():
            value=activity[system]
            for curve,radius in curves:
                key(curve,'bevel_depth',radius*value,frame)
                # The installation is drawn along its direction as it is exposed.
                key(curve,'bevel_factor_end',ramp(p,.225,.30) if system=='installation' else 1,frame)
            key(ACCENTS[system],'default_value',.05+value*.85,frame)
        for index,(lamp,power,kind) in enumerate(LAMPS):
            level=ramp(p,.38+index*.007,.42+index*.007)
            if kind in ('lounge','bedroom'):
                level*=1-.45*shade
            key(lamp,'energy',power*level,frame)
        emission=MATERIALS['lamp'].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength']
        key(emission,'default_value',.12+3.3*ramp(p,.38,.46),frame)
    scene.frame_set(1)
