"""V4 room placement, cabinetry and electrical components matching the selected views."""
import math
from . import core as c, furniture as f


def kitchen(parent):
    c.collection('V4 | EG 10 Kitchen',parent,'EG | Kitchen')
    # L-shaped kitchen with separate cabinet fronts, worktop and a real sink opening.
    f.cabinet('Kitchen | drawer base',1.02,10.12,1.36,.86,.60,drawers=True)
    f.cabinet('Kitchen | hollow sink cabinet',2.275,10.12,1.15,.86,.60,open_top=True)
    f.cabinet('Kitchen | narrow base',2.99,10.12,.28,.86,.60,drawers=True)
    for y in [8.0,8.6,9.2]:f.cabinet('Kitchen | return unit',.64,y,.60,.86,.60,angle=math.pi/2,drawers=True)
    # Four counter strips surround the sink instead of covering it with a black rectangle.
    for x,y,w,d in [(1.02,10.09,1.36,.69),(2.99,10.09,.28,.69),(2.25,9.79,1.10,.09),(2.25,10.385,1.10,.08)]:
        c.box('Kitchen | honed limestone worktop',(x,y,.905),(w,d,.065),'stone',.007)
    c.box('Kitchen | return worktop',(.64,8.6425,.905),(.68,2.205,.065),'stone',.007)
    # Sink is a hollow metal vessel; its lip sits into the opening in the stone.
    sink=f.basin('Kitchen | steel sink',2.27,10.10,.745,.97,.49)
    sink.data.materials[0]=c.M['steel']
    c.box('Kitchen | backsplash rear',(1.94,10.47,1.12),(3.16,.035,.38),'stone',.004)
    c.box('Kitchen | backsplash return',(.325,8.97,1.12),(.035,2.96,.38),'stone',.004)
    c.box('Kitchen | induction glass',(.64,8.35,.946),(.54,.73,.015),'black',.008)
    for x in [.50,.78]:
        for y in [8.13,8.57]:
            pts=[(x+.105*math.cos(a*math.tau/64),y+.105*math.sin(a*math.tau/64),.955) for a in range(64)]
            c.tube('Kitchen | fine induction ring',pts,.0015,'steel',cyclic=True)
    f.cabinet('Kitchen | oven tower',3.39,9.96,.63,2.25,.66)
    c.box('Kitchen | inset oven',(3.39,9.595,1.20),(.54,.055,.58),'black',.01)
    c.box('Kitchen | oven glass',(3.39,9.561,1.15),(.47,.012,.39),'charcoal',.012)
    c.rod('Kitchen | oven handle',(3.17,9.53,1.41),(3.61,9.53,1.41),.014,'steel')
    for xx in [3.23,3.55]:c.cylinder('Kitchen | oven dial',(xx,9.546,1.44),.025,.013,'steel',rotation=(math.pi/2,0,0))
    f.plant('Kitchen | herb pot',.74,9.76,.95,.30,.08)
    c.lathe('Kitchen | fruit bowl',(2.9,10.05,.947),[(0,0),(.10,.012),(.16,.07),(.15,.08),(.10,.03),(0,.023)],'stone')
    for i in range(4):c.soft('Kitchen | pear',(2.85+(i%2)*.06,10.0+(i//2)*.07,1.015),(.072,.074,.09),'olive',exponent=.8)
    light=c.area('Kitchen | task lighting',(1.6,9.6,2.42),(1.6,9.9,.9),65,1.2)
    light['interior_light']=True;light['nominal_watts']=65


def living(parent):
    c.collection('V4 | EG 11 Living and dining',parent,'EG | Living / Dining')
    f.rug('Living | woven wool rug',2.36,2.46,3.42,2.84)
    f.sofa('Living | linen corner sofa',2.03,3.13)
    f.table('Living | oak coffee table',2.66,1.81,1.48,.75,.41)
    c.box('Living | coffee table lower shelf',(2.66,1.81,.17),(1.31,.62,.025),'oak pale',.016)
    f.plant('Living | small coffee plant',2.79,1.84,.44,.24,.06)
    c.lathe('Living | ceramic cup',(2.35,1.74,.442),[(0,0),(.043,0),(.047,.07),(.04,.073),(.035,.012),(0,.01)],'ceramic')
    f.lamp('Living | floor lamp',.58,1.12,.07,table=False)
    f.cabinet('Living | low oak media console',4.52,1.92,1.72,.46,.32,angle=-math.pi/2,drawers=True)
    c.box('Living | television',(4.485,1.96,1.05),(.04,1.39,.81),'charcoal',.009)
    c.box('Living | dark display',(4.459,1.96,1.05),(.006,1.34,.755),'black',.003)
    f.art('Living | botanical print',.329,4.55,1.53,.58,.78,angle=math.pi/2)
    f.curtain('Living | left curtain',1.0,.40,.07,.28,2.24)
    f.curtain('Living | right curtain',4.11,.40,.07,.24,2.24)
    f.table('Dining | oval oak table',2.15,5.68,2.25,1.02,.765,radius=.50)
    for xx in [1.43,2.15,2.87]:
        f.chair('Dining | chair front',xx,4.85,math.pi)
        f.chair('Dining | chair rear',xx,6.49,0)
    f.plant('Dining | table foliage',2.13,5.70,.80,.28,.085)
    c.rod('Dining | pendant cable',(2.15,5.68,2.75),(2.15,5.68,2.02),.008,'charcoal')
    c.lathe('Dining | opal pendant',(2.15,5.68,1.93),[(0,0),(.17,0),(.29,.10),(.25,.24),(.05,.28),(0,.28)],'linen white')
    c.cylinder('Dining | luminous diffuser',(2.15,5.68,1.94),.165,.014,'light')
    light=c.area('Dining | warm pendant pool',(2.15,5.68,1.91),(2.15,5.68,.7),70,.5)
    light['interior_light']=True;light['nominal_watts']=70
    f.plant('Dining | corner plant',.58,6.80,.04,.85,.16)


def office(parent):
    c.collection('V4 | EG 12 Office and guest',parent,'EG | Office')
    f.table('Office | solid oak desk',8.01,8.9,1.9,.72,.75)
    f.chair('Office | upholstered work chair',8.0,8.05,math.pi)
    c.box('Office | closed laptop',(8.1,8.9,.795),(.34,.25,.014),'charcoal',.008)
    f.lamp('Office | task lamp',7.30,8.9,.79)
    f.cabinet('Office | bookcase base',7.2,10.25,1.2,.70,.40)
    for x in [6.6,7.8]:c.box('Office | bookcase side',(x,10.25,1.37),(.035,.40,1.99),'oak',.004)
    for z in [.75,1.13,1.51,1.9,2.28]:c.box('Office | shelf',(7.2,10.25,z),(1.23,.40,.025),'oak pale',.004)
    for row in range(4):
        xx=6.68
        for i in range(12):
            w=c.RNG.uniform(.025,.055);height=c.RNG.uniform(.21,.31)
            c.box('Office | individual book',(xx,10.19,.77+row*.38+height/2),(w,.19,height),['paper','olive','taupe','charcoal'][i%4],.001)
            xx+=w+.012
    f.plant('Office | indoor tree',8.99,9.80,.04,1.55,.22)
    f.art('Office | framed print',8.46,10.46,1.64,.55,.70)
    f.cabinet('Office | guest storage',6.75,7.35,.75,1.8,.45,angle=math.pi/2)
    # Guests can use a compact daybed without reducing the circulation around the desk.
    root=c.empty('Office | daybed',(8.83,6.75,0),math.pi/2)
    c.box('Office | daybed oak base',(0,0,.25),(1.6,.74,.32),'oak pale',.022,root)
    c.soft('Office | daybed mattress',(0,0,.48),(1.6,.74,.18),'linen',root,.33,seam=True)


def technical(parent):
    c.collection('V4 | EG 13 Electrical and utility',parent,'EG | HWR / Electrical')
    for name,x,w in [('distribution',7.07,.91),('network rack',8.04,.71)]:
        c.box('HWR | '+name+' housing',(x,3.16,1.22),(w,.33,2.13),'white appliance',.008)
        c.box('HWR | '+name+' recessed interior',(x,2.982,1.23),(w-.09,.023,2.02),'black' if 'rack' in name else 'paper',.002)
        for xx in [x-w/2+.023,x+w/2-.023]:c.box('HWR | enclosure lip',(xx,2.96,1.22),(.033,.027,2.14),'white appliance',.003)
    for row in range(5):
        z=.83+row*.25
        c.box('HWR | DIN rail',(7.07,2.948,z),(.79,.02,.029),'steel',.003)
        for module in range(12):
            x=6.70+module*.063
            c.box('HWR | breaker body',(x,2.912,z),(.054,.066,.14),'white appliance',.004)
            c.box('HWR | black breaker toggle',(x,2.872,z+.008),(.023,.027,.037),'charcoal',.002)
            c.box('HWR | circuit label',(x,2.875,z+.048),(.031,.002,.017),'paper',0)
    for i in range(12):
        x=6.71+i*.063
        c.tube('HWR | neatly dressed cable',[(x,2.92,.79),(x,2.91,.48),((x+7.10)/2,2.91,.36),(7.12+(i-6)*.012,2.91,.24)],.005,['black','blue','black'][i%3])
    for row in range(8):
        z=.58+row*.185
        c.box('HWR | rack equipment face',(8.04,2.948,z),(.58,.032,.13),'charcoal',.003)
        for i in range(8):
            x=7.80+i*.065
            c.box('HWR | ethernet socket',(x,2.927,z+.012),(.041,.016,.026),'black',.001)
            c.box('HWR | status LED',(x+.016,2.914,z+.042),(.007,.006,.005),'led',.001)
        if row%2:
            for i in range(6):
                x=7.83+i*.071
                c.tube('HWR | blue patch lead',[(x,2.91,z),(x,2.85,z-.06),(x+.04,2.85,z-.10),(x+.05,2.915,z-.17)],.004,'blue')
    for name,x in [('washing machine',8.28),('dryer',8.91)]:
        # Appliances face the room from the rear half of the utility area.
        root=c.empty('HWR | '+name,(x,2.35,0))
        c.box(name+' | cabinet',(0,0,.46),(.59,.60,.83),'white appliance',.018,root)
        c.box(name+' | control fascia',(0,-.31,.79),(.55,.035,.13),'ceramic',.006,root)
        c.cylinder(name+' | dial',(-.10,-.335,.79),.032,.018,'steel',root,(math.pi/2,0,0))
        c.box(name+' | display',(.13,-.331,.79),(.12,.009,.041),'charcoal',.003,root)
        c.cylinder(name+' | door gasket',(0,-.321,.44),.207,.025,'charcoal',root,(math.pi/2,0,0))
        c.cylinder(name+' | brushed door surround',(0,-.34,.44),.19,.032,'steel',root,(math.pi/2,0,0))
        c.cylinder(name+' | glass porthole',(0,-.363,.44),.157,.016,'black' if 'washing' in name else 'stone',root,(math.pi/2,0,0))
        c.cylinder(name+' | transparent lens',(0,-.374,.44),.142,.012,'glass',root,(math.pi/2,0,0))
    # Surface outlets and restrained red route make the installation state legible.
    for x,y,z,angle in [(6.475,1.1,.35,math.pi/2),(9.26,.75,.35,math.pi/2),(6.475,2.70,1.1,math.pi/2)]:
        root=c.empty('HWR | socket',(x,y,z),angle)
        c.box('HWR | socket plate',(0,0,0),(.082,.015,.082),'ceramic',.004,root)
        for xx in [-.012,.012]:c.cylinder('HWR | socket contact',(xx,-.011,0),.004,.009,'black',root,(math.pi/2,0,0),vertices=16)
    route=c.tube('HWR | installation highlight',[(7.1,2.94,.23),(7.1,2.85,.12),(9.15,2.85,.12),(9.15,.50,.12),(6.65,.5,.12),(6.50,1.1,.35)],.009,'red')
    route['installation_route']=True


def bathrooms(roots):
    c.collection('V4 | EG 14 Guest WC',roots['EG'],'EG | Guest WC')
    f.toilet('WC | wall-hung toilet',8.64,4.92)
    f.cabinet('WC | oak vanity',7.05,4.93,.62,.65,.43,drawers=True)
    f.basin('WC | basin',7.05,4.90,.68,.54,.39)
    c.box('WC | mirror',(7.05,5.222,1.40),(.50,.024,.69),'steel',.022)
    f.plant('WC | plant',7.28,4.91,.84,.17,.05)
    c.collection('V4 | OG 14 Family bathroom',roots['OG'],'OG | Family bathroom')
    f.tub('Bathroom | freestanding bath',7.75,9.91)
    f.toilet('Bathroom | wall-hung toilet',8.94,8.83,-math.pi/2)
    vanity=f.cabinet('Bathroom | twin oak vanity',8.91,7.67,1.45,.70,.60,angle=-math.pi/2,drawers=True)
    c.box('Bathroom | stone vanity top',(0,0,.735),(1.49,.63,.045),'stone',.006,vanity)
    for xx in [-.37,.37]:f.basin('Bathroom | washbasin',xx,0,.76,.62,.44,vanity)
    c.box('Bathroom | large mirror',(9.263,7.67,1.46),(.024,1.40,.78),'steel',.018)
    # Stone-lined shower, glass screen, metal clamps and actual shower fittings.
    c.box('Bathroom | shower tray',(7.03,8.08,.07),(1.08,1.27,.05),'stone',.013)
    c.box('Bathroom | shower glass',(7.60,8.08,1.09),(.012,1.24,2.03),'glass',.003)
    c.rod('Bathroom | shower glass top brace',(6.48,8.65,2.14),(7.60,8.65,2.14),.011,'steel')
    for z in [.35,1.79]:c.box('Bathroom | shower glass clamp',(7.60,8.66,z),(.031,.05,.034),'steel',.003)
    c.tube('Bathroom | rain shower pipe',[(6.53,8.26,1.08),(6.53,8.26,2.08),(6.85,8.26,2.08)],.015,'steel')
    c.cylinder('Bathroom | rain shower head',(6.85,8.26,2.065),.11,.025,'steel')
    c.rod('Bathroom | mixer',(6.53,8.15,1.03),(6.53,8.42,1.03),.024,'steel')
    c.tube('Bathroom | flexible hose',[(6.54,8.18,1.01),(6.59,8.05,.58),(6.63,8.40,.63),(6.56,8.47,1.31)],.009,'steel')
    for y in [8.0,8.6,9.2,9.8]:
        for z in [.38,.98,1.58,2.18]:c.box('Bathroom | shower stone wall tile',(6.464,y,z),(.018,.597,.597),'stone',.0007)


def bedrooms(parent):
    c.collection('V4 | OG 10 Parents suite',parent,'OG | Parents')
    f.rug('Parents | woven rug',2.24,2.42,2.70,2.66)
    f.bed('Parents | double oak bed',2.04,2.42,1.8,math.pi/2)
    for yy in [1.12,3.70]:
        f.cabinet('Parents | nightstand',.77,yy,.50,.45,.46,drawers=True)
        f.lamp('Parents | bedside lamp',.77,yy,.49)
    f.cabinet('Parents | fitted oak wardrobe',2.08,4.81,3.26,2.28,.59)
    f.art('Parents | botanical artwork',.327,2.40,1.62,.65,.83,angle=math.pi/2)
    f.curtain('Parents | curtain left',1.13,.40,.88,.26,1.54)
    f.curtain('Parents | curtain right',3.37,.40,.88,.26,1.54)
    for i in range(15):
        slat=c.box('Parents | external blind slat',(2.25,.025,2.40-i*.038),(2.46,.075,.016),'charcoal',.004)
        slat['smart_blind']=True
    for y in [3.42,4.58]:
        c.box('Parents | KNX switch',(4.537,y,1.1),(.018,.085,.085),'charcoal',.005)
        for yy in [-.017,.017]:c.box('Parents | KNX rocker',(4.526,y+yy,1.1),(.01,.029,.068),'steel',.002)
    c.collection('V4 | OG 11 Child front',parent,'OG | Child front')
    f.rug('Child front | rug',8.10,2.17,1.30,2.44)
    f.bed('Child front | oak single bed',8.12,2.37,1.05,0)
    f.cabinet('Child front | wardrobe',7.07,4.72,.95,2.16,.59)
    f.cabinet('Child front | nightstand',8.98,3.0,.46,.45,.43,drawers=True)
    f.lamp('Child front | bedside lamp',8.98,3.0,.49)
    f.table('Child front | homework desk',7.03,1.13,1.22,.56,.73,angle=math.pi/2)
    f.chair('Child front | desk chair',7.60,1.13,-math.pi/2)
    c.box('Child front | notebook',(7.02,1.08,.78),(.21,.27,.016),'paper',.003)
    f.plant('Child front | desk plant',7.04,.70,.77,.23,.065)
    c.collection('V4 | OG 12 Child rear',parent,'OG | Child rear')
    f.rug('Child rear | wool rug',2.32,8.28,1.45,1.54)
    f.bed('Child rear | oak single bed',1.20,8.81,1.05,0)
    f.cabinet('Child rear | nightstand',2.06,9.55,.48,.45,.43,drawers=True)
    f.lamp('Child rear | bedside lamp',2.06,9.55,.49)
    f.cabinet('Child rear | wardrobe',3.40,9.23,.93,2.14,.59,angle=-math.pi/2)
    f.table('Child rear | homework desk',1.30,6.98,1.29,.58,.73)
    f.chair('Child rear | desk chair',1.28,7.64,0)
    c.box('Child rear | notebook',(1.35,6.98,.778),(.26,.19,.012),'book olive',.003)
    f.curtain('Child rear | curtain',1.20,10.38,1.20,.20,1.18)
    c.collection('V4 | OG 13 Landing',parent,'OG | Landing')
    for i in range(14):
        y=6.69+i*.265
        c.rod('Landing | stair guard baluster',(3.96,y,.04),(3.96,y,.95),.012,'charcoal')
    c.rod('Landing | oak guardrail',(3.96,6.65,.97),(3.96,10.18,.97),.027,'oak')
    c.box('Landing | KNX panel',(6.275,5.66,1.10),(.025,.15,.12),'charcoal',.006)


def entrance(parent):
    c.collection('V4 | EG 15 Entrance details',parent,'Entrance')
    f.plant('Entrance | right olive shrub',7.55,-.38,-.20,1.07,.36)
    f.plant('Terrace | left olive tree',.38,-.61,.011,1.83,.39)
    c.box('Entrance | video intercom',(6.83,-.016,1.37),(.16,.043,.39),'charcoal',.012)
    c.cylinder('Entrance | camera rim',(6.83,-.045,1.49),.031,.013,'steel',rotation=(math.pi/2,0,0))
    c.cylinder('Entrance | optical lens',(6.83,-.054,1.49),.023,.01,'black',rotation=(math.pi/2,0,0))
    c.cylinder('Entrance | lens highlight',(6.825,-.062,1.494),.005,.002,'glass',rotation=(math.pi/2,0,0))
    for row in range(5):
        for col in range(5):c.cylinder('Entrance | speaker perforation',(6.80+col*.013,-.042,1.38+row*.013),.002,.005,'black',rotation=(math.pi/2,0,0),vertices=12)
    c.cylinder('Entrance | bell button ring',(6.83,-.044,1.26),.027,.009,'steel',rotation=(math.pi/2,0,0))
    c.cylinder('Entrance | bell button',(6.83,-.05,1.26),.022,.009,'charcoal',rotation=(math.pi/2,0,0))
    c.box('Entrance | recessed warm ceiling light',(5.75,.34,2.29),(.36,.13,.02),'light',.015)
    light=c.area('Entrance | warm downlight',(5.75,.34,2.27),(5.75,-.3,0),28,.4)
    light['interior_light']=True;light['nominal_watts']=28


def ceiling_lights(roots):
    # Physical flush ceiling lights provide usable room light through the closed facade.
    for level,rooms in [('EG',[('Living',2.0,2.7,110),('Hall',5.45,3.0,65),('Utility',7.85,1.5,75),
                              ('Guest WC',7.85,4.45,40),('Office',8.0,8.0,90)]),
                        ('OG',[('Parents',2.1,2.5,140),('Child front',8.0,2.5,100),('Child rear',2.1,8.4,100),
                              ('Bathroom',7.9,8.0,100),('Landing',5.45,5.3,65)])]:
        c.collection('V4 | '+level+' 16 Ceiling lighting',roots[level],level)
        for name,x,y,power in rooms:
            trim=c.cylinder(level+' | '+name+' ceiling trim',(x,y,2.7625),.145,.035,'ceramic')
            disc=c.cylinder(level+' | '+name+' ceiling diffuser',(x,y,2.738),.125,.018,'light')
            for obj in [trim,disc]:obj['cutaway_upper']=True
            light=c.area(level+' | '+name+' ceiling light',(x,y,2.71),(x,y,.1),power,.75)
            light['interior_light']=True;light['nominal_watts']=power


def build(roots):
    kitchen(roots['EG']);living(roots['EG']);office(roots['EG']);technical(roots['EG'])
    bedrooms(roots['OG']);bathrooms(roots);entrance(roots['EG'])
    ceiling_lights(roots)
