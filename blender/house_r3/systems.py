"""Spatially anchored electrical services and native animated explanation paths."""
import math
from . import core as c

PATHS=[]
LAMPS=[]
BLIND=None


def socket(name,x,y,z=.29,rotation=0,data=False):
    root=c.empty(name,(x,y,z),rotation)
    c.cube(name+' faceplate',(0,0,0),(.083,.018,.083),'white',.01,root)
    if data:
        c.cube(name+' network port',(0,-.011,0),(.023,.004,.018),'charcoal',.001,root)
    else:
        c.cylinder(name+' recessed socket',(0,-.012,0),.025,.008,'stone',root,(math.pi/2,0,0))
        for x in (-.010,.010):
            c.sphere(name+' pin',(x,-.017,0),(.004,.002,.004),'black',root)
    return root


def equipment():
    c.ROOM='Utility electrical'
    c.collection('11 Electrical and network systems')
    root=c.empty('Electrical distribution assembly',(10.14,1.64,0))
    root['service']='Electrical distribution; separate from the network rack'
    c.cube('Distribution enclosure',(0,0,1.22),(.67,.21,1.30),'white',.024,root)
    c.cube('Distribution internal backplate',(0,-.119,1.22),(.59,.025,1.19),'charcoal',.015,root)
    for row in range(5):
        z=.77+row*.22
        c.cube('Distribution DIN rail',(0,-.141,z),(.52,.035,.023),'metal',.005,root)
        for col in range(8):
            x=-.237+col*.067
            c.cube('Distribution circuit breaker',(x,-.182,z),(.057,.068,.145),'white',.004,root)
            c.cube('Breaker switch',(x,-.221,z+.016),(.021,.015,.035),'black',.003,root)
            c.cube('Breaker identifier',(x,-.221,z-.039),(.031,.004,.017),'linen light',.001,root)
    c.cube('Distribution cable duct',(0,-.15,1.76),(.51,.05,.067),'ivory cabinet',.006,root)
    c.cube('Distribution fixed backing wall',(10.14,1.777,1.04),(.84,.045,2.08),'wall interior',.006)
    # Open hinged door stays attached to the cabinet.
    hinge=c.empty('Distribution door hinge',(-.352,-.11,1.22),math.radians(-110),root)
    c.cube('Distribution open door',(.333,0,0),(.67,.035,1.30),'white',.017,hinge)
    rack=c.empty('Network rack assembly',(11.255,.40,0),-math.pi/2)
    rack['service']='Structured data; patchpanel and ethernet switch'
    c.cube('Network rack housing',(0,0,.86),(.60,.29,1.50),'charcoal',.02,rack)
    c.cube('Network rack open face',(0,-.157,.86),(.53,.035,1.40),'black',.009,rack)
    for row in range(9):
        z=.27+row*.143
        c.cube('Network rack device',(0,-.18,z),(.48,.09,.107),'charcoal',.005,rack)
        for col in range(9):
            x=-.20+col*.05
            c.cube('RJ45 patch port',(x,-.23,z),(.033,.007,.023),'metal',.001,rack)
            if row in (5,6,7):
                c.tube('Ethernet patch cable',[(x,-.236,z),(x,-.28,z-.04),(x+.025,-.28,z-.09)],.006,'data blue',rack)
        c.cube('Network status indicator',(.215,-.23,z),(.009,.006,.009),'green light',.001,rack)
    inv=c.empty('PV inverter',(11.24,1.32,0),-math.pi/2)
    inv['service']='PV inverter; connected to the distribution cabinet'
    c.cube('Inverter enclosure',(0,0,1.19),(.50,.22,.65),'white',.035,inv)
    c.cube('Inverter display',(0,-.119,1.23),(.16,.007,.095),'screen',.008,inv)
    c.tube('Inverter AC conduit',[(11.08,1.32,.85),(11.08,1.32,.22),(10.14,1.32,.22),(10.14,1.48,.61)],.015,'charcoal')
    c.ROOM=None
    for name,x,y,z,rot,data in [
        ('Living socket',5.425,3.85,.3,-math.pi/2,False),
        ('Living data outlet',5.425,3.70,.3,-math.pi/2,True),
        ('Parents socket',3.92,10.775,.31,0,False),
        ('Child desk socket',7.075,5.87,.31,math.pi/2,False),
        ('Office data outlet',7.075,9.20,.31,math.pi/2,True),
        ('Office socket',7.075,9.37,.31,math.pi/2,False),
        ('Kitchen socket',3.32,6.727,1.14,0,False)]:
        socket(name,x,y,z,rot,data)
    # Bedside, kitchen and mirror lighting are supported by furniture/walls.
    c.collection('12 Lighting control and security')
    for name,loc,target,power,size in [
        ('Kitchen task lighting',(2.57,6.43,1.46),(2.57,6.22,.92),65,2.7),
        ('Living reading light',(1.55,3.19,1.54),(1.30,2.45,.5),35,.23),
        ('Parents bedside left',(1.1,9.83,.86),(1.1,9.40,.4),13,.22),
        ('Parents bedside right',(3.81,9.83,.86),(3.81,9.40,.4),13,.22),
        ('Bathroom mirror light',(9.42,4.10,1.98),(9.42,3.66,1.0),40,1.4),
        ('Front door downlight',(6.25,-.31,2.25),(6.25,-.8,-.12),45,.25),
        ('Living evening wash',(1.5,2.8,2.5),(2,1.6,.1),80,2.0)]:
        o=c.area(name,loc,target,power,size,(1,.68,.38))
        LAMPS.append((o,power))
    # Control wall is retained above the section so nothing is unsupported.
    c.cube('Retained KNX control wall',(5.525,4.15,.92),(.15,.52,1.84),'wall interior',.006)
    c.cube('KNX room controller',(5.434,4.15,1.14),(.025,.12,.17),'charcoal',.009)
    c.cube('KNX controller display',(5.416,4.15,1.17),(.008,.094,.094),'screen',.003)
    c.cube('Hall indoor station',(5.616,4.15,1.40),(.025,.16,.23),'white',.01)
    c.cube('Hall station screen',(5.635,4.15,1.43),(.006,.12,.13),'screen',.004)
    c.cube('Door station backing',(7.05,-.36,1.15),(.29,.10,2.30),'plaster',.015)
    c.cube('Video door station',(7.05,-.423,1.42),(.12,.035,.32),'charcoal',.012)
    c.cylinder('Door camera lens',(7.05,-.447,1.50),.024,.012,'black',rotation=(math.pi/2,0,0))
    c.cylinder('Door call button',(7.05,-.447,1.33),.024,.01,'metal',rotation=(math.pi/2,0,0))
    # Contact follows the opening door frame; a small interior PIR on the fixed wall.
    c.cube('Door magnetic contact',(6.735,-.19,2.18),(.058,.035,.026),c.fade_material('white'),.006)
    c.cube('Entrance PIR',(5.617,4.15,1.70),(.033,.056,.073),'white',.012)
    global BLIND
    BLIND=c.empty('RIG | Bedroom blind',(2.67,10.89,2.21))
    for i in range(29):
        c.cube('Blind aluminium slat',(0,0,-.02-i*.049),(1.76,.041,.015),'ivory cabinet',.004,BLIND)
    for f,z in ((1,.015),(98,.015),(115,1),(133,1),(149,.015),(181,.015)):
        c.key(BLIND,'scale',f,(1,1,z))
    # Schematic low-level paths stay at fixed physical coordinates.
    c.collection('14 Schematic routes | animated')
    routes=[
        ('Main electrical route',[(10.14,1.48,.28),(9.61,1.48,.28),(9.61,.86,.28),(7.17,.86,.28),(6.60,.86,.28),(6.60,9.7,.28)],'Hubmann red'),
        ('Living electrical branch',[(6.60,2.55,.28),(5.25,2.55,.28),(5.25,3.85,.28),(5.40,3.85,.30)],'Hubmann red'),
        ('Parents electrical branch',[(6.60,9.70,.28),(5.8,9.70,.28),(5.8,10.6,.28),(3.92,10.6,.28),(3.92,10.755,.31)],'Hubmann red'),
        ('Child electrical branch',[(6.60,5.87,.28),(7.08,5.87,.28)],'Hubmann red'),
        ('Office data route',[(11.18,.42,.20),(10.55,.42,.20),(10.55,1.52,.20),(6.47,1.52,.20),(6.47,9.20,.20),(7.06,9.20,.31)],'data blue')]
    for name,points,mat in routes:
        o=c.tube(name,points,.012,mat)
        o['schematic']=True
        PATHS.append(o)


def animate():
    for m in c.SHELL:
        v=m.node_tree.nodes['Visibility'].inputs[0]
        for f,a in ((1,1),(17,1),(31,.70),(50,0),(146,0),(171,1),(181,1)):
            v.default_value=a
            v.keyframe_insert(data_path='default_value',frame=f)
    for m in c.ROOF:
        v=m.node_tree.nodes['Visibility'].inputs[0]
        for f,a in ((1,1),(28,1),(43,0),(142,0),(153,1),(181,1)):
            v.default_value=a
            v.keyframe_insert(data_path='default_value',frame=f)
    for name,m in c.M.items():
        if name.endswith(' | cap'):
            v=m.node_tree.nodes['Visibility'].inputs[0]
            for f,a in ((1,0),(28,0),(50,1),(146,1),(171,0),(181,0)):
                v.default_value=a
                v.keyframe_insert(data_path='default_value',frame=f)
    for o in PATHS:
        for f,v in ((1,0),(43,0),(62,1),(72,1),(83,0),(181,0)):
            c.key(o.data,'bevel_factor_end',f,v)
    for o,power in LAMPS:
        for f,k in ((1,.08),(65,.08),(86,1),(113,.65),(142,.2),(166,.25),(181,1)):
            c.key(o.data,'energy',f,power*k)
    # Fully transparent holds do not need ray intersections. Hiding only after
    # fade-out avoids transparency-depth artefacts without a visible pop.
    import bpy
    for o in bpy.data.objects:
        if o.type=='LIGHT' and o.name.startswith('Studio '):
            power=o.data.energy
            for f,k in ((1,1),(68,1),(85,.24),(117,.24),(139,1),(163,1),(181,.50)):
                c.key(o.data,'energy',f,power*k)
    sky=bpy.context.scene.world.node_tree.nodes['Background'].inputs['Strength']
    for f,value in ((1,.32),(68,.32),(85,.085),(117,.085),(139,.32),(163,.32),(181,.15)):
        sky.default_value=value
        sky.keyframe_insert(data_path='default_value',frame=f)
    for o in bpy.data.objects:
        if o.type!='MESH' or not o.data.materials:
            continue
        names=[m.name for m in o.data.materials if m]
        group='roof' if all(n.endswith(' | roof') for n in names) else 'shell' if all(n.endswith(' | shell') for n in names) else None
        if group:
            points=[(1,False),(43,True),(142,True),(143,False),(181,False)] if group=='roof' else [(1,False),(50,True),(146,True),(147,False),(181,False)]
            for f,hide in points:
                c.key(o,'hide_render',f,hide)
                c.key(o,'hide_viewport',f,hide)


def build():
    equipment()
    animate()
