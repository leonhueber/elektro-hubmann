"""R3 measured shell: six directly accessible rooms and a 1.30 m corridor."""
import math
import bpy
from . import core as c

HEIGHT = 2.75
CUT = .97
ROOMS = {
    'Living dining kitchen': (0, 5.45, 0, 6.80),
    'Parents bedroom': (0, 5.45, 6.95, 10.80),
    'Utility electrical': (7.05, 11.40, 0, 1.80),
    'Bathroom WC': (7.05, 11.40, 1.95, 4.25),
    'Child bedroom': (7.05, 11.40, 4.40, 7.50),
    'Office guest': (7.05, 11.40, 7.65, 10.80),
    'Corridor': (5.60, 6.90, 0, 10.80),
}
DOORS = []
WINDOWS = []


def panel(name, axis, pos, a, b, bottom, top, thickness, mat):
    if b - a < .001 or top - bottom < .001:
        return
    for lo, hi, fading in ((bottom, min(CUT, top), False), (max(bottom, CUT), top, True)):
        if hi - lo < .001:
            continue
        loc = ((a+b)/2, pos, (lo+hi)/2) if axis == 'x' else (pos, (a+b)/2, (lo+hi)/2)
        dim = (b-a, thickness, hi-lo) if axis == 'x' else (thickness, b-a, hi-lo)
        c.cube(name + (' upper' if fading else ' retained'), loc, dim, c.fade_material(mat) if fading else mat, .007)
    if bottom < CUT and top > CUT:
        loc = ((a+b)/2, pos, CUT+.002) if axis == 'x' else (pos, (a+b)/2, CUT+.002)
        dim = (b-a, thickness+.002, .012) if axis == 'x' else (thickness+.002, b-a, .012)
        c.cube(name + ' section cap', loc, dim, c.fade_material('cut edge','cap'), .002)


def wall(name, axis, pos, start, end, thickness, openings=(), mat='wall interior'):
    cuts = sorted(openings, key=lambda i: i[0])
    a = start
    for left, right, bottom, top in cuts:
        panel(name, axis, pos, a, left, 0, HEIGHT, thickness, mat)
        panel(name + ' sill', axis, pos, left, right, 0, bottom, thickness, mat)
        panel(name + ' lintel', axis, pos, left, right, top, HEIGHT, thickness, mat)
        a = right
    panel(name, axis, pos, a, end, 0, HEIGHT, thickness, mat)


def split_piece(name, xy, size_xy, bottom, top, mat, parent):
    for lo, hi, fading in ((bottom, min(CUT, top), False), (max(bottom, CUT), top, True)):
        if hi-lo > .001:
            c.cube(name + (' upper' if fading else ' lower'), (*xy, (lo+hi)/2), (*size_xy, hi-lo),
                   c.fade_material(mat) if fading else mat, .006, parent)


def window(name, axis, pos, a, b, bottom=.8, top=2.3, panes=2):
    parent = c.empty(name, ((a+b)/2, pos, 0) if axis=='x' else (pos, (a+b)/2, 0),
                     0 if axis=='x' else math.pi/2)
    w = b-a
    for x in (-w/2+.035, w/2-.035):
        split_piece(name+' jamb', (x, 0), (.07, .13), bottom, top, 'charcoal', parent)
    for z in (bottom+.035, top-.035):
        c.cube(name+' rail', (0,0,z), (w,.13,.07), c.fade_material('charcoal') if z>CUT else 'charcoal', .008, parent)
    for i in range(panes):
        x=-w/2+w*(i+.5)/panes
        split_piece(name+' glazing', (x,0), (w/panes-.075,.018), bottom+.06, top-.06, 'glass', parent)
        if i:
            split_piece(name+' mullion', (-w/2+w*i/panes,0), (.05,.11), bottom+.06, top-.06, 'charcoal', parent)
    c.cube(name+' stone sill', (0,0,bottom-.025), (w+.1,.39,.05), c.fade_material('stone') if bottom>CUT else 'stone', .012, parent)
    parent['opening_width'] = w
    parent['sill_height'] = bottom
    if name=='Rear window 1':
        # One complete window stays attached to a narrow retained reveal so the
        # blind can demonstrate a real control action in the open-house state.
        for o in parent.children_recursive:
            if o.type=='MESH':
                for slot in o.material_slots:
                    if slot.material and slot.material.name.endswith(' | shell'):
                        slot.material=c.M[slot.material.name.split(' | ')[0]]
        for x in (-w/2-.055,w/2+.055):
            c.cube('Fixed blind window reveal',(x,0,1.13),(.11,.30,2.26),'plaster',.006,parent)
    WINDOWS.append(parent)
    return parent


def door(name, axis, pos, a, b, swing, exterior=False):
    root = c.empty(name+' opening', ((a+b)/2,pos,0) if axis=='x' else (pos,(a+b)/2,0),
                   0 if axis=='x' else math.pi/2)
    width = b-a
    head = 2.25 if exterior else 2.13
    for x in (-width/2+.016, width/2-.016):
        split_piece(name+' frame', (x,0), (.045,.16), 0,head,'oak light',root)
    c.cube(name+' head', (0,0,head-.01), (width,.16,.055), c.fade_material('oak light'), .006, root)
    leaf = c.empty(name+' hinge', (-width/2+.046,0,0), parent=root)
    usable=width-.09
    split_piece(name+' leaf', (usable/2,0), (usable,.045), .035,head-.05,'oak',leaf)
    c.cube(name+' handle rose',(usable-.12,-.037,.92),(.038,.025,.15),'charcoal',.009,leaf)
    c.tube(name+' lever', [(usable-.12,-.045,.96),(usable-.12,-.095,.96),(usable-.23,-.095,.96)], .012,'charcoal',leaf)
    for f, angle in ((1,0),(23,0),(53,swing),(144,swing),(177,0),(181,0)):
        c.key(leaf, 'rotation_euler',f,(0,0,math.radians(angle)))
    root['clear_width'] = usable
    root['room_access'] = name
    DOORS.append(root)
    return root


def floors():
    c.collection('01 Structure and floors')
    c.cube('Insulated foundation slab',(5.7,5.25,-.22),(12.25,11.75,.40),'stone',.035)
    c.cube('Continuous screed',(5.7,5.4,-.045),(11.4,10.8,.08),'grout',.0)
    for room, (x0,x1,y0,y1) in ROOMS.items():
        c.ROOM=room
        root=c.empty('ROOM | '+room)
        root['bounds_xy']=[x0,x1,y0,y1]
        root['clear_area_m2']=round((x1-x0)*(y1-y0),3)
        if room in ('Utility electrical','Bathroom WC'):
            step=.6
            x=x0
            while x<x1-.001:
                y=y0
                while y<y1-.001:
                    w,h=min(step,x1-x),min(step,y1-y)
                    c.cube(room+' porcelain floor tile',(x+w/2,y+h/2,.008),(w-.006,h-.006,.018),'tile',.002,root)
                    y+=step
                x+=step
        else:
            x=x0
            row=0
            while x<x1-.001:
                w=min(.19,x1-x)
                y=y0
                first=.55+(row%3)*.48
                while y<y1-.001:
                    length=min(first if y==y0 else 1.82,y1-y)
                    c.cube(room+' oak plank',(x+w/2,y+length/2,.008),(w-.002,length-.002,.018),'oak light',.0008,root)
                    y+=length
                x+=.19
                row+=1
    c.ROOM=None
    c.cube('Living terrace foundation',(2.55,-1.02,-.30),(6.1,1.75,.30),'stone',.025)
    for i in range(10):
        for j in range(3):
            c.cube('Terrace limestone paving',(-.175+i*.6,-1.60+j*.55,-.132),(.593,.542,.035),'stone',.004)
    c.cube('Front door porch',(6.25,-.86,-.25),(1.92,1.33,.23),'stone',.025)
    c.cube('Entrance lower step',(6.25,-1.62,-.34),(1.92,.30,.10),'stone',.02)
    c.cube('Doormat',(6.25,-.67,-.116),(.82,.45,.015),'rug',.018)


def shell():
    c.collection('02 Exterior walls and windows')
    front=[(.65,4.65,.08,2.40),(5.70,6.80,0,2.25),(8.0,9.55,.80,2.15)]
    west=[(1.25,3.95,.08,2.40),(7.65,9.70,.8,2.25)]
    east=[(2.60,3.55,1.28,2.15),(5.08,6.92,.8,2.25),(8.25,10.12,.8,2.25)]
    rear=[(1.70,3.65,.8,2.25),(8.30,10.20,.8,2.25)]
    wall('Front facade','x',-.15,-.3,11.7,.3,front,'plaster')
    wall('West facade','y',-.15,0,10.8,.3,west,'plaster')
    wall('East facade','y',11.55,0,10.8,.3,east,'plaster')
    wall('Rear facade','x',10.95,-.3,11.7,.3,rear,'plaster')
    for side,axis,pos,openings in [('Front','x',-.15,front),('West','y',-.15,west),('East','y',11.55,east),('Rear','x',10.95,rear)]:
        for i,(a,b,z0,z1) in enumerate(openings):
            if z0:
                window(side+' window '+str(i+1),axis,pos,a,b,z0,z1,3 if b-a>3 else 2)
    door('Entrance','x',-.15,5.70,6.80,70,True)
    c.cube('Entrance oak reveal left',(5.55,-.335,1.365),(.17,.08,2.73),c.fade_material('oak'),.008)
    c.cube('Entrance oak reveal right',(6.95,-.335,1.365),(.17,.08,2.73),c.fade_material('oak'),.008)
    c.cube('Entrance oak reveal soffit',(6.25,-.335,2.4),(1.55,.08,.48),c.fade_material('oak'),.008)
    # Permanent device-bearing patch at the back of the actual utility room.
    c.cube('Utility fixed equipment wall',(11.38,.94,1.70),(.07,1.70,1.46),'wall interior',.008)
    c.collection('03 Room partitions and doors')
    left=[(.75,1.72,0,2.14),(7.15,8.12,0,2.14)]
    right=[(.25,1.22,0,2.14),(2.10,3.07,0,2.14),(4.60,5.57,0,2.14),(7.85,8.82,0,2.14)]
    wall('Living corridor partition','y',5.525,0,10.8,.15,left)
    wall('Service corridor partition','y',6.975,0,10.8,.15,right)
    wall('Parents living partition','x',6.875,0,5.45,.15)
    for name,y in [('Utility bathroom',1.875),('Bathroom child',4.325),('Child office',7.575)]:
        wall(name+' partition','x',y,7.05,11.4,.15)
    for name,a,b in [('Living dining kitchen',.75,1.72),('Parents bedroom',7.15,8.12)]:
        door(name,'y',5.525,a,b,83)
    for name,a,b in [('Utility electrical',.25,1.22),('Bathroom WC',2.10,3.07),('Child bedroom',4.60,5.57),('Office guest',7.85,8.82)]:
        door(name,'y',6.975,a,b,-83)
    # Skirting stays below the section, with clear door gaps.
    for room,(x0,x1,y0,y1) in ROOMS.items():
        if room=='Corridor':
            continue
        c.cube(room+' rear skirting',((x0+x1)/2,y1-.017,.065),(x1-x0,.035,.13),'white',.005)


def roof():
    c.collection('04 Roof and photovoltaic rig')
    rig=c.empty('RIG | Roof lift')
    c.cube('Roof insulated slab',(5.7,5.4,2.89),(12.26,11.66,.28),c.fade_material('plaster','roof'),.025,rig)
    c.cube('Roof gravel surface',(5.7,5.4,3.04),(11.84,11.24,.07),c.fade_material('roof gravel','roof'),.006,rig)
    for name,loc,size in [
        ('Front parapet',(5.7,-.37,3.17),(12.3,.17,.37)),
        ('Rear parapet',(5.7,11.17,3.17),(12.3,.17,.37)),
        ('West parapet',(-.37,5.4,3.17),(.17,11.4,.37)),
        ('East parapet',(11.77,5.4,3.17),(.17,11.4,.37))]:
        c.cube(name,loc,size,c.fade_material('plaster','roof'),.012,rig)
        c.cube(name+' metal coping',(loc[0],loc[1],3.372),(size[0]+.035,size[1]+.035,.038),c.fade_material('charcoal','roof'),.006,rig)
    for row in range(2):
        for col in range(4):
            panel=c.empty('PV module %02d'%(row*4+col+1),(3.25+col*1.16,4.0+row*2.08,3.24),parent=rig)
            panel.rotation_euler.x=math.radians(12)
            c.cube('PV aluminium frame',(0,0,0),(1.10,1.84,.045),c.fade_material('metal','roof'),.008,panel)
            c.cube('PV active glass',(0,0,.027),(1.04,1.78,.014),c.fade_material('PV cell','roof'),.005,panel)
            for n in range(1,6):
                c.cube('PV vertical cell division',(-.52+n*1.04/6,0,.038),(.004,1.77,.002),c.fade_material('PV grid','roof'),0,panel)
            for n in range(1,11):
                c.cube('PV horizontal cell division',(0,-.89+n*1.78/11,.038),(1.04,.003,.002),c.fade_material('PV grid','roof'),0,panel)
            for x in (-.43,.43):
                c.cube('PV back support',(x,.65,-.17),(.045,.05,.30),c.fade_material('metal','roof'),.004,panel)
    for f,z in ((1,0),(12,0),(30,1.5),(47,2.1),(142,2.1),(158,0),(181,0)):
        c.key(rig,'location',f,(0,0,z))
    c.cylinder('Ceiling smoke detector',(6.25,4.8,2.724),.065,.04,c.fade_material('white','roof'),rig)
    return rig


def build():
    floors()
    shell()
    return roof()
