"""Recognisable electrical devices and independent power/data overlays."""
import bpy
from .core import box, cylinder, line, collection, label, area, LAMPS

ROUTES = {'installation': [], 'network': [], 'smart': [], 'security': [], 'energy': []}


def route(name, points, system, radius=.021):
    obj = line(name, points, system, radius)
    obj['system'] = system
    ROUTES[system].append((obj.data, radius))
    return obj


def build():
    collection('ELECTRICAL')
    box('distribution enclosure',(.64,-.69,1.68),(1.0,.23,2.16),'porcelain',.04)
    box('distribution interior',(.64,-.818,1.68),(.86,.025,1.96),'charcoal',.02)
    label('distribution name','ELEKTRO',(.27,-.85,2.54),.1)
    for row in range(5):
        z=.94+row*.29
        box('DIN rail',(.64,-.85,z),(.8,.024,.035),'metal',.004)
        for col in range(6):
            x=.30+col*.135
            box('breaker',(x,-.894,z),(.116,.10,.21),'porcelain',.006)
            box('breaker toggle',(x,-.95,z+.005),(.06,.02,.065),'charcoal',.003)
            box('circuit identifier',(x,-.95,z+.074),(.043,.01,.018),'red',.002)
        # Quiet real wiring within the cabinet; overlay shows the route outside.
        line('panel wiring',[(.25,-.86,z+.11),(.18,-.86,z+.17),(1.04,-.86,z+.17)],'oak',.01)
    box('meter',(.62,-.895,2.27),(.65,.11,.25),'porcelain',.01)
    box('meter LCD',(.64,-.958,2.28),(.34,.013,.10),'glass',.006)
    # Freestanding service door is open and remains part of the fixed alcove.
    door=box('distribution open door',(1.36,-1.16,1.68),(.65,.055,2.16),'porcelain',.018)
    door.rotation_euler.z=-.84
    for x,y,z in [(-4.74,-2.3,.63),(4.78,-1.5,.63),(4.78,-1.5,3.78),(-4.74,-1.9,3.78)]:
        box('double socket',(x,y,z),(.14,.05,.12),'porcelain',.014)
        for dx in (-.029,.029):
            cylinder('socket centre',(x+dx,y-.028,z),.012,.008,'charcoal').rotation_euler.x=1.5708
    route('main riser',[(.70,-.68,2.78),(.70,-.68,6.13)],'installation',.028)
    route('ground socket branch',[(.70,-.68,.69),(.70,-2.91,.69),(-4.65,-2.91,.69),(-4.65,-2.3,.69)],'installation')
    route('ground lighting branch',[(.70,-.68,2.78),(.70,-.68,3.00),(3.15,-.68,3.00),(3.15,-1.5,3.00)],'installation')
    route('upper lighting branch',[(.70,-.68,6.13),(-3.2,-.68,6.13),(-3.2,.1,6.13)],'installation')
    route('workspace supply',[(.70,-.68,3.80),(3.85,-.68,3.80),(3.85,-1.4,3.80)],'installation')
    collection('NETWORK')
    box('network enclosure',(-.32,-.77,1.4),(.60,.42,1.50),'charcoal',.025)
    label('network name','NETZ',(-.55,-1.003,2.01),.083)
    for i in range(6):
        z=.84+i*.18
        box('network rack unit',(-.32,-1.00,z),(.48,.028,.13),'metal',.006)
        for j in range(6):
            box('network port',(-.51+j*.076,-1.023,z),(.045,.014,.045),'charcoal',.002)
            box('network LED',(-.50+j*.076,-1.031,z+.04),(.013,.005,.009),'network',.002)
    route('data backbone',[(-.37,-.68,2.18),(-.37,-.68,2.91),(.40,-.68,2.91),(.40,-.68,5.93),
                           (2.7,-.68,5.93),(2.7,-.68,4.3),(2.7,-1.2,4.3)],'network',.018)
    cylinder('ceiling access point',(1.60,-.88,6.13),.13,.04,'porcelain')
    collection('LIGHTING')
    for x,y,z,kind in [(3.15,-1.50,3.0,'dining'),(-3.0,-1.0,3.0,'lounge'),
                        (2.65,-1.4,6.15,'office'),(-3.2,.1,6.15,'bedroom')]:
        # Permanent beam provides a legible attachment in the cutaway state.
        box(kind+' light support',(x,y,z),(.18,1.5,.13),'oak',.015)
        line(kind+' suspension',[(x,y,z),(x,y,z-.57)],'charcoal',.012)
        cylinder(kind+' shade',(x,y,z-.67),.24,.21,'charcoal')
        cylinder(kind+' diffuser',(x,y,z-.782),.212,.015,'lamp')
        lamp=area(kind+' light',(x,y,z-.82),(x,y,z-3),0,1.15,(1,.72,.4))
        LAMPS.append((lamp.data,95 if z<4 else 80, kind))
    box('kitchen LED diffuser',(2.42,3.39,2.45),(3.7,.07,.035),'lamp',.005)
    light=area('kitchen task light',(2.4,3.2,2.42),(2.4,2.65,1.3),0,2,(1,.78,.52))
    LAMPS.append((light.data,85,'kitchen'))
    collection('SECURITY')
    box('entry timber pier',(1.77,-3.45,1.76),(.24,.24,2.91),'oak',.018)
    box('entry video station',(1.77,-3.585,1.65),(.18,.035,.33),'charcoal',.014)
    lens=cylinder('intercom camera',(1.77,-3.61,1.73),.028,.015,'glass')
    lens.rotation_euler.x=1.5708
    box('intercom button',(1.77,-3.615,1.59),(.055,.009,.035),'lamp',.004)
    box('entry light',(1.77,-3.6,2.70),(.18,.16,.20),'charcoal',.01)
    box('entry light diffuser',(1.77,-3.61,2.59),(.14,.12,.016),'lamp',.003)
    lamp=area('entry light',(1.77,-3.7,2.53),(1.77,-4.6,0),0,.6,(1,.74,.44))
    LAMPS.append((lamp.data,45,'entry'))
    box('alarm contact',(4.76,-3.43,2.55),(.12,.065,.24),'porcelain',.02)
    box('alarm motion sensor',(-.9,-3.60,2.8),(.17,.1,.23),'porcelain',.025)
    cylinder('smoke detector',(1.1,-.9,6.12),.13,.052,'porcelain')
    route('entry protection outline',[(1.55,-3.64,1.43),(1.99,-3.64,1.43),(1.99,-3.64,1.89),
                                      (1.55,-3.64,1.89),(1.55,-3.64,1.43)],'security',.014)
    route('alarm outline',[(4.63,-3.5,2.4),(4.9,-3.5,2.4),(4.9,-3.5,2.72),
                           (4.63,-3.5,2.72),(4.63,-3.5,2.4)],'security',.012)
    collection('SMARTHOME')
    box('smart wall control',(-.9,-3.60,1.7),(.25,.04,.37),'charcoal',.016)
    box('smart screen',(-.9,-3.627,1.75),(.20,.012,.23),'smart',.005)
    route('KNX control link',[(-.9,-3.61,1.43),(-.9,-3.61,.60),(.4,-3.61,.60),(.4,-.68,.60),(.4,-.68,2.37)],'smart',.014)
    # Blind headrail remains attached to the front structural beam in cutaway.
    from .core import empty
    blind=empty('Blind lift')
    blind.location=(-2.8,-3.43,6.13)
    box('blind headrail',(-2.8,-3.43,6.16),(3.1,.09,.10),'charcoal',.009)
    for i in range(12):
        box('blind slat',(0,0,-.09-i*.125),(3.05,.045,.09),'oak',.005,blind)
    collection('ENERGY')
    box('inverter backing',(4.22,.44,1.73),(1.2,.12,2.9),'plaster')
    box('inverter',(4.22,.27,1.85),(.76,.23,1.22),'porcelain',.075)
    box('inverter display',(4.22,.14,2.0),(.42,.017,.21),'charcoal',.012)
    label('inverter name','PV',(4.05,.118,1.62),.13,'charcoal')
    for i in range(7):
        box('inverter vent',(4.0+i*.07,.14,1.47),(.023,.012,.13),'metal',.003)
    route('PV downlead',[(4.22,.4,6.28),(4.22,.4,2.5)],'energy',.026)
    route('PV to distribution',[(4.22,.12,1.22),(4.22,.12,.56),(.9,.12,.56),(.9,-.68,.56),(.9,-.68,.84)],'energy',.026)
    collection('ENERGY_OPTIONAL')
    box('optional storage',(4.22,.04,.77),(.83,.51,1.02),'porcelain',.07)
    box('optional storage status',(4.22,-.225,1.08),(.35,.014,.04),'network',.004)
    box('optional wallbox post',(5.35,-2.55,.9),(.14,.14,1.8),'charcoal')
    box('optional wallbox',(5.35,-2.66,1.35),(.40,.19,.60),'porcelain',.09)
    line('optional charging cable',[(5.42,-2.8,1.1),(5.59,-2.8,.55),(5.15,-2.8,.40),
                                    (5.04,-2.8,1.14)],'charcoal',.026)
    # These are modelled, but not advertised in the public story until confirmed.
    bpy.data.collections['V3_ENERGY_OPTIONAL'].hide_render=True
    bpy.data.collections['V3_ENERGY_OPTIONAL'].hide_viewport=True
    return blind
