"""Compact two-storey pavilion. Front is -Y; camera sees front and right."""
import math
from .core import box, cylinder, sphere, line, collection, empty, wedge


def window(name, x, y, z, width, height, side=False, shell=False):
    suffix = '_shell' if shell else ''
    def b(tag, dx, dy, dz, sx, sy, sz, mat):
        pos = (x+dy, y+dx, z+dz) if side else (x+dx, y+dy, z+dz)
        size = (sy,sx,sz) if side else (sx,sy,sz)
        return box(name+tag, pos, size, mat+suffix, .012)
    b(' glazing',0,0,0,width,.035,height,'glass')
    for sign in (-1,1):
        b(' jamb',sign*width/2,-.025,0,.07,.11,height+.1,'charcoal')
        b(' rail',0,-.025,sign*height/2,width+.1,.11,.07,'charcoal')
    b(' mullion',0,-.03,0,.045,.12,height,'charcoal')


def build():
    collection('STRUCTURE')
    box('floating plinth',(0,0,-.15),(11.8,9,.30),'concrete',.06)
    box('porcelain apron',(0,-.05,.035),(11.55,8.8,.07),'porcelain',.025)
    for y,z,w in [(-4.72,-.11,3.5),(-5.03,-.24,3.9)]:
        box('entry step',(1.9,y,z),(w,.56,.15),'concrete',.02)
    for z in (.17,3.25):
        if z < 1:
            box('floor structural slab',(0,0,z),(10.2,7.4,.23),'porcelain')
        else:
            box('upper slab left',(-3.675,0,z),(2.85,7.4,.23),'porcelain')
            box('upper slab right',(2.075,0,z),(6.05,7.4,.23),'porcelain')
            box('upper slab front',(-1.60,-2.325,z),(1.30,2.75,.23),'porcelain')
            box('upper slab back',(-1.60,3.525,z),(1.30,.35,.23),'porcelain')
        # Fine long planks with real seams, restrained at web scale.
        for i in range(34):
            x=-4.85+i*.294
            if z>1 and -2.40<x<-.80:
                box('oak stair landing',(x,-2.34,z+.128),(.288,2.42,.026),'oak_light',.004)
            else:
                box('oak floor board',(x,0,z+.128),(.288,7.1,.026),'oak_light',.004)
        box('rear wall',(0,3.56,z+1.55),(10,.22,2.96),'plaster')
        box('left wall',(-4.94,0,z+1.55),(.22,7.1,2.96),'plaster')
        for x in (-4.9,-.9,4.9):
            box('front structural post',(x,-3.48,z+1.51),(.15,.18,2.9),'porcelain',.015)
        box('front beam',(0,-3.48,z+2.92),(10,.20,.18),'porcelain')
        # Rear windows sit on the inside face of the retained wall, no overlaps
        # with moving facade components.
        for x in (-3.1,2.85):
            window('rear window',x,3.425,z+1.65,2.2,1.65)
    wedge('left roof closure',-4.94,.22,'plaster')
    box('rear roof closure',(0,3.56,6.717),(10,.22,.874),'plaster')
    # Ground-floor technique room is a shallow alcove on the front sight line.
    box('technical service wall',(.45,-.55,1.74),(2.2,.17,2.87),'sage')
    box('technical return wall',(-.73,.4,1.74),(.15,2.0,2.87),'plaster')
    box('upper partition',(-.6,.8,4.8),(.15,5.3,2.84),'plaster')
    box('bath screen',(2.8,1.65,4.8),(4.1,.14,2.84),'plaster')
    # Rear straight flight with an actual opening in its circulation zone.
    for i in range(16):
        box('stair tread',(-1.6,3.10-i*.245,.33+i*.193),(1.12,.28,.095),'oak',.012)
    line('stair handrail',[(-2.15,-.6,4.04),(-2.15,3.12,1.1)],'charcoal',.025)
    for i in range(0,16,3):
        line('stair spindle',[(-2.15,3.1-i*.245,.38+i*.193),
                               (-2.15,3.1-i*.245,1.1+i*.193)],'charcoal',.012)
    for x in (-2.29,-.91):
        for y in (-.83,1.18,3.24):
            box('stairwell guard post',(x,y,3.89),(.035,.035,1.02),'charcoal',.006)
        line('stairwell guardrail',[(x,-.83,4.39),(x,3.24,4.39)],'charcoal',.021)
    # A visible warm ceiling strip carries pendants when the outer roof rises.
    box('retained upper light beam',(0,-.9,6.27),(9.7,.14,.16),'oak')
    collection('SHELL_FRONT')
    box('front roof closure',(0,-3.56,6.342),(10,.22,.124),'plaster_shell')
    for z in (.29,3.37):
        # Apertures are assembled around openings, never covered by solid walls.
        for x,w in [(-4.64,.52),(-.93,.35),(1.65,.34),(4.65,.5)]:
            box('front facade pier',(x,-3.56,z+1.41),(w,.22,2.83),'plaster_shell')
        box('front lintel',(0,-3.56,z+2.72),(10,.22,.25),'plaster_shell')
        for x,w in [(-2.8,3.17),(.34,2.18),(3.2,2.55)]:
            if z<1 and x==.34:
                window('entry sidelight',-.42,-3.61,z+1.32,.64,2.38,shell=True)
                box('entrance door',(.66,-3.61,z+1.32),(1.30,.10,2.38),'charcoal_shell',.018)
                box('entrance door inset',(.66,-3.674,z+1.60),(.85,.015,1.14),'glass_shell',.014)
                box('entrance pull',(1.12,-3.71,z+1.12),(.045,.06,.46),'oak_shell',.014)
            else:
                window('front window',x,-3.61,z+1.32,w,2.38,shell=True)
    # Warm vertical entrance accent, all part of the fading shell.
    for i in range(12):
        box('front timber batten',(1.97+i*.105,-3.72,1.66),(.055,.07,2.65),'oak_shell',.006)
    collection('SHELL_SIDE')
    wedge('side roof closure',4.94,.22,'plaster_shell')
    for z in (.29,3.37):
        box('side sill',(4.94,0,z+.42),(.22,7.1,.84),'plaster_shell')
        box('side lintel',(4.94,0,z+2.64),(.22,7.1,.44),'plaster_shell')
        for y in (-3.25,0,3.25):
            box('side pier',(4.94,y,z+1.59),(.22,.54,1.5),'plaster_shell')
        for y in (-1.63,1.63):
            window('right window',5.005,y,z+1.62,2.63,1.53,side=True,shell=True)
    collection('ROOF')
    roof = empty('Roof lift')
    slope = .105
    for name,z,size,mat in [('roof soffit',6.46,(10.85,8,.16),'oak'),
                             ('standing seam roof',6.59,(10.96,8.12,.12),'charcoal')]:
        obj=box(name,(0,0,z),size,mat,.02,roof)
        obj.rotation_euler.x=slope
    for x in [i*.47-5.17 for i in range(23)]:
        line('roof standing seam',[(x,-4,6.24),(x,4,7.08)],'metal',.018,roof)
    line('roof gutter',[(-5.5,-4.05,6.20),(5.5,-4.05,6.20)],'charcoal',.055,roof)
    # Integrated photovoltaic field, four columns and two rows.
    for col in range(4):
        for row in range(2):
            x=-2.65+col*1.48; y=-1.50+row*2.1; z=6.75+y*math.tan(slope)
            panel=box('PV frame',(x,y,z),(1.38,1.96,.075),'metal',.015,roof)
            panel.rotation_euler.x=slope
            cells=box('PV laminate',(x,y-.007,z+.045),(1.30,1.89,.016),'pv',.005,roof)
            cells.rotation_euler.x=slope
            for k in range(1,6):
                xx=x-.65+k*1.30/6
                line('PV cell column',[(xx,y-.94,z+.05-.94*math.tan(slope)),
                                       (xx,y+.94,z+.05+.94*math.tan(slope))],'pv_line',.004,roof)
            for k in range(1,10):
                yy=y-.94+k*1.88/10
                line('PV cell row',[(x-.65,yy,z+.05+(yy-y)*math.tan(slope)),
                                    (x+.65,yy,z+.05+(yy-y)*math.tan(slope))],'pv_line',.004,roof)
    return roof


def furniture():
    collection('INTERIOR')
    # Ground floor lounge; upholstered volumes with rounded edges and feet.
    for x in (-4,-2.1):
        for y in (-1.45,-.18):
            cylinder('sofa foot',(x,y,.41),.05,.25,'charcoal')
    box('sofa base',(-3.1,-.82,.64),(2.5,1.35,.42),'linen',.15)
    box('sofa back',(-3.1,-.18,1.06),(2.5,.27,.78),'linen',.13)
    for x in (-4.22,-1.98):
        box('sofa arm',(x,-.85,.95),(.27,1.23,.66),'linen',.12)
    for x in (-3.67,-2.54):
        box('seat cushion',(x,-.87,.90),(1.02,1.02,.18),'cream',.1)
        cushion=box('back cushion',(x,-.38,1.22),(.88,.23,.53),'cream',.1)
        cushion.rotation_euler.x=-.12
    cylinder('coffee table',(-3,-2.45,.68),.63,.10,'oak')
    cylinder('coffee table pedestal',(-3,-2.45,.46),.18,.4,'charcoal')
    box('book',(-3.1,-2.5,.755),(.35,.27,.04),'sage',.008)
    # Kitchen sits against retained rear wall, accessible on the right.
    for i in range(5):
        x=.9+i*.77
        box('kitchen cabinet',(x,2.96,.81),(.75,.9,1.01),'oak',.015)
        line('cabinet pull',[(x-.22,2.493,1.09),(x+.22,2.493,1.09)],'charcoal',.014)
    box('countertop',(2.44,2.91,1.34),(3.91,1.02,.075),'porcelain')
    box('induction hob',(3.20,2.87,1.39),(.83,.61,.025),'charcoal',.01)
    for x in (2.98,3.43):
        for y in (2.7,3.03):
            cylinder('hob ring',(x,y,1.407),.12,.003,'metal')
    box('sink',(.93,2.9,1.39),(.52,.48,.016),'metal',.05)
    line('tap',[(.93,3.19,1.4),(.93,3.19,1.78),(.93,2.98,1.78),(.93,2.98,1.64)],'metal',.026)
    box('dining table',(3.15,-1.5,1.1),(2.0,1.13,.09),'oak',.06)
    for x in (2.4,3.9):
        for y in (-1.85,-1.15):
            box('table leg',(x,y,.7),(.06,.06,.72),'charcoal',.008)
    for x in (2.55,3.75):
        for y in (-2.43,-.56):
            box('chair seat',(x,y,.73),(.56,.52,.13),'cream',.06)
            box('chair back',(x,y+(-.23 if y< -1 else .23),1.03),(.56,.08,.62),'oak',.05)
            for dx in (-.21,.21):
                for dy in (-.19,.19):
                    box('chair leg',(x+dx,y+dy,.49),(.04,.04,.41),'charcoal',.007)
    # Bedroom, with clear floor around bed and front-side view.
    box('bed base',(-3.55,.3,3.76),(1.86,2.30,.42),'oak',.06)
    for x in (-4.27,-2.83):
        for y in (-.6,1.1):
            cylinder('bed foot',(x,y,3.51),.045,.25,'charcoal')
    box('bed mattress',(-3.55,.24,4.03),(1.78,2.22,.20),'cream',.13)
    box('headboard',(-3.55,1.48,4.2),(2.02,.16,1.1),'oak',.04)
    box('duvet',(-3.55,-.17,4.18),(1.83,1.54,.17),'linen',.1)
    for x in (-3.99,-3.12):
        box('pillow',(x,.95,4.21),(.65,.43,.15),'porcelain',.1)
    for x in (-4.68,-2.43):
        box('nightstand',(x,1.09,3.72),(.30,.52,.66),'oak',.025)
        cylinder('bedside lamp stem',(x,1.09,4.24),.025,.38,'charcoal')
        cylinder('bedside lamp shade',(x,1.09,4.40),.13,.20,'cream')
    # Workspace: ground technology route terminates visibly here.
    box('desk',(2.6,-1.4,4.13),(2.3,.82,.07),'oak',.04)
    for x in (1.6,3.6):
        box('desk leg',(x,-1.4,3.77),(.05,.6,.72),'charcoal')
    box('monitor',(2.7,-1.18,4.6),(1.0,.07,.61),'charcoal',.02)
    box('monitor screen',(2.7,-1.224,4.61),(.91,.008,.50),'glass',.01)
    box('monitor stand',(2.7,-1.16,4.27),(.055,.055,.28),'metal')
    box('keyboard',(2.65,-1.56,4.19),(.64,.22,.025),'charcoal',.012)
    cylinder('office chair pedestal',(2.65,-2.34,3.42),.24,.06,'metal')
    cylinder('office chair shaft',(2.65,-2.34,3.71),.045,.55,'metal')
    box('office chair',(2.65,-2.34,4.01),(.62,.59,.14),'sage',.08)
    box('office chair back',(2.65,-2.6,4.33),(.62,.1,.70),'sage',.08)
    # Rear bathroom is an identifiable secondary zone.
    box('vanity',(2.0,2.97,3.96),(1.7,.73,1.0),'oak')
    box('washbasin',(2.0,2.89,4.52),(1.73,.79,.12),'porcelain',.04)
    box('mirror',(2.0,3.41,5.26),(1.68,.03,.95),'metal',.025)
    box('shower tray',(4.02,2.62,3.47),(1.25,1.55,.09),'porcelain')
    line('shower rail',[(4.65,3.29,3.65),(4.65,3.29,5.77),(4.27,3.29,5.77)],'metal',.021)
    cylinder('shower head',(4.27,3.29,5.74),.14,.025,'metal')
    # Two restrained planting accents.
    for x,y,z in [(-4.4,2.65,.30),(4.9,-4,.09)]:
        cylinder('planter',(x,y,z+.24),.24,.48,'porcelain')
        for k in range(7):
            angle=k*2.4
            sphere('leaves',(x+math.cos(angle)*.18,y+math.sin(angle)*.18,z+.75+(k%3)*.12),(.19,.11,.25),'leaf')
