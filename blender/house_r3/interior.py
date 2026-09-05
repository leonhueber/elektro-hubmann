"""Purpose-built furnished rooms for the approved R3 plan; no legacy assets."""
import math
from . import core as c


def cushion(name, loc, size, mat, parent, rotation=(0,0,0)):
    if 'pillow' in name or 'rust accent' in name:
        o=c.sphere(name,loc,tuple(v*.53 for v in size),mat,parent)
        for v in o.data.vertices:
            for i in range(3):
                p=v.co[i]
                v.co[i]=math.copysign(abs(p)**(.50 if i<2 else .75),p)
        o.rotation_euler=rotation
        return o
    o=c.cube(name,loc,size,mat,min(size)*.42,parent)
    o.modifiers['Soft manufactured edges'].segments=6
    o.rotation_euler=rotation
    return o


def bed(name, x, y, width=1.8, rotation=0):
    root=c.empty(name,(x,y,0),rotation)
    for xx in (-width*.39,width*.39):
        for yy in (-.80,.80):
            c.cylinder(name+' oak foot',(xx,yy,.115),.045,.23,'oak dark',root)
    cushion(name+' upholstered base',(0,0,.27),(width+.10,2.10,.29),'linen taupe',root)
    cushion(name+' mattress',(0,-.03,.48),(width,2.02,.24),'linen light',root)
    cushion(name+' padded headboard',(0,1.04,.69),(width+.20,.15,1.17),'linen',root)
    # Duvet top and overlapping hem remain separate cloth forms.
    cushion(name+' duvet',(0,-.34,.635),(width+.03,1.37,.14),'linen light',root)
    # Subtle cloth undulation breaks the perfectly planar bedding silhouette.
    import bpy
    verts=[]
    for j in range(23):
        yy=-1.02+j*1.39/22
        for i in range(25):
            xx=-(width+.02)/2+i*(width+.02)/24
            zz=.710+.009*math.sin(xx*21+yy*7)*math.sin(yy*9)+.005*math.sin(xx*37+yy*12)
            zz-=.045*(abs(xx)/(width/2+.01))**10
            verts.append((xx,yy,zz))
    faces=[(j*25+i,j*25+i+1,(j+1)*25+i+1,(j+1)*25+i) for j in range(22) for i in range(24)]
    mesh=bpy.data.meshes.new(name+' cloth surface')
    mesh.from_pydata(verts,[],faces)
    cloth=c.register(bpy.data.objects.new(name+' draped duvet',mesh),name+' draped duvet','linen light',root)
    for p in mesh.polygons:
        p.use_smooth=True
    cushion(name+' folded throw',(0,-.69,.719),(width+.06,.51,.055),'linen taupe',root)
    count=2 if width>1.2 else 1
    for i in range(count):
        px=(i-(count-1)/2)*width/count
        cushion(name+' pillow piping',(px,.68,.65),(width/count-.10,.46,.145),'linen',root,(-.10,.01,(-1)**i*.035))
        cushion(name+' soft pillow',(px,.675,.669),(width/count-.13,.43,.145),'linen light',root,(-.10,.01,(-1)**i*.035))
    cushion(name+' rust accent',(0,.35,.752),(.39,.35,.13),'rust',root,(-.17,0,.11))
    return root


def wardrobe(name, x, y, width, depth=.60, rotation=0):
    root=c.empty(name,(x,y,0),rotation)
    c.cube(name+' recessed plinth',(0,0,.065),(width-.07,depth-.06,.13),'oak dark',.012,root)
    c.cube(name+' carcass',(0,0,1.11),(width,depth,2.10),'oak light',.012,root)
    count=round(width/.55)
    for i in range(count):
        xx=-width/2+width*(i+.5)/count
        c.cube(name+' door',(xx,-depth/2-.018,1.15),(width/count-.008,.038,2.02),'oak light',.007,root)
        c.cube(name+' pull',(xx+.15,-depth/2-.047,1.04),(.014,.026,.23),'charcoal',.006,root)
    return root


def sofa(name, x,y,width=2.7,rotation=0,chaise=False):
    root=c.empty(name,(x,y,0),rotation)
    for xx in (-width/2+.14,width/2-.14):
        for yy in (-.29,.29):
            c.cylinder(name+' foot',(xx,yy,.10),.026,.20,'charcoal',root)
    cushion(name+' base',(0,0,.27),(width,.93,.29),'linen taupe',root)
    count=3 if width>2.3 else 2
    for i in range(count):
        xx=-width/2+.17+(width-.34)*(i+.5)/count
        cushion(name+' seat',(xx,-.065,.49),((width-.38)/count-.025,.69,.19),'linen',root)
        cushion(name+' back cushion',(xx,.335,.74),((width-.36)/count-.018,.23,.58),'linen',root,(-.14,0,0))
    for xx in (-width/2+.09,width/2-.09):
        cushion(name+' arm',(xx,-.015,.57),(.20,.97,.53),'linen',root)
    cushion(name+' accent pillow',(-width/2+.46,.12,.77),(.4,.17,.42),'rust',root,(-.2,.10,.11))
    cushion(name+' pale pillow',(width/2-.48,.14,.76),(.42,.16,.39),'linen light',root,(-.2,-.1,-.12))
    if chaise:
        cushion(name+' chaise base',(-width/2+.60,-.71,.29),(1.0,.92,.28),'linen taupe',root)
        cushion(name+' chaise cushion',(-width/2+.60,-.69,.49),(.96,.91,.19),'linen',root)
    return root


def chair(name,x,y,rotation=0,office=False):
    root=c.empty(name,(x,y,0),rotation)
    if office:
        c.cylinder(name+' swivel stem',(0,0,.27),.04,.42,'charcoal',root)
        for i in range(5):
            a=i*math.tau/5
            end=(math.cos(a)*.28,math.sin(a)*.28,.07)
            c.tube(name+' star base',[(0,0,.15),end],.018,'charcoal',root)
            c.sphere(name+' castor',end,(.035,.035,.03),'black',root)
    else:
        for xx in (-.19,.19):
            for yy in (-.19,.19):
                c.tube(name+' leg',[(xx*1.15,yy*1.15,.02),(xx,yy,.47)],.025,'oak',root)
    cushion(name+' seat',(0,0,.48),(.47,.47,.09),'linen taupe' if office else 'linen',root)
    cushion(name+' back',(0,.21,.73),(.47,.075,.43),'linen taupe' if office else 'linen',root,(-.11,0,0))
    return root


def lamp(name,x,y,z=0,scale=1):
    root=c.empty(name,(x,y,z))
    c.cylinder(name+' base',(0,0,.023*scale),.13*scale,.045*scale,'stone',root)
    c.cylinder(name+' stem',(0,0,.22*scale),.021*scale,.39*scale,'metal',root)
    c.cylinder(name+' linen shade',(0,0,.40*scale),.13*scale,.19*scale,'linen light',root)
    c.cylinder(name+' diffuser',(0,0,.306*scale),.11*scale,.012,'light',root)


def desk(name,x,y,width=1.35,rotation=0):
    root=c.empty(name,(x,y,0),rotation)
    c.cube(name+' oak desktop',(0,0,.755),(width,.64,.055),'oak light',.023,root)
    for xx in (-width/2+.10,width/2-.10):
        for yy in (-.22,.22):
            c.cylinder(name+' tapered leg',(xx,yy,.37),.028,.74,'oak',root)
    c.cube(name+' laptop keyboard',(0,-.06,.795),(.34,.24,.017),'metal',.012,root)
    screen=c.cube(name+' laptop screen',(0,.052,.925),(.34,.018,.25),'charcoal',.008,root)
    screen.rotation_euler.x=-.17
    c.cube(name+' display',(0,.039,.927),(.313,.008,.214),'screen',.003,root)
    c.cube(name+' notebook',(.37,-.07,.799),(.15,.20,.02),'linen light',.004,root)
    c.cylinder(name+' pencil cup',(-.43,.12,.85),.04,.15,'stone',root)
    for i in range(4):
        c.cylinder(name+' pencil',(-.45+i*.012,.12,.94),.003,.18,'oak dark',root)
    return root


def cabinet(name,x,y,width=.6,depth=.61,rotation=0,drawers=False):
    root=c.empty(name,(x,y,0),rotation)
    c.cube(name+' plinth',(0,0,.065),(width-.03,depth-.04,.13),'charcoal',.005,root)
    c.cube(name+' carcass',(0,0,.50),(width-.009,depth,.77),'ivory cabinet',.008,root)
    levels=3 if drawers else 1
    for j in range(levels):
        h=.74/levels
        c.cube(name+' front',(0,-depth/2-.013,.13+h*(j+.5)),(width-.016,.028,h-.009),'ivory cabinet',.007,root)
        c.cube(name+' shadow pull',(0,-depth/2-.031,.13+h*(j+1)-.027),(width-.10,.008,.012),'oak dark',.003,root)
    return root


def kitchen():
    c.ROOM='Living dining kitchen'
    c.collection('05 Interior | Living kitchen dining')
    # North run includes sink, drawers, dishwasher and an integrated refrigerator.
    for i in range(6):
        cabinet('Kitchen north unit %d'%i,1.02+i*.62,6.46,.62,drawers=i in (3,4))
    c.cube('Kitchen north limestone worktop',(2.57,6.44,.925),(3.78,.69,.055),'stone',.015)
    for i in range(3):
        cabinet('Kitchen west unit %d'%i,.32,4.98+i*.62,.62,rotation=-math.pi/2,drawers=i==0)
    c.cube('Kitchen return worktop',(.33,5.60,.925),(.68,1.89,.055),'stone',.014)
    # Sink: inset dark basin, bright rims, tap with an actual curved spout.
    c.cube('Sink recessed basin',(1.77,6.43,.956),(.59,.44,.018),'metal',.065)
    c.cube('Sink interior shadow',(1.77,6.43,.966),(.50,.355,.015),'charcoal',.060)
    c.cylinder('Sink drain',(1.77,6.43,.977),.029,.006,'metal')
    c.tube('Kitchen mixer',[(1.77,6.69,.95),(1.77,6.69,1.21),(1.77,6.66,1.28),(1.77,6.57,1.29),(1.77,6.49,1.25),(1.77,6.49,1.20)],.018,'metal')
    c.cube('Induction glass hob',(.33,5.58,.963),(.56,.59,.015),'black',.018)
    for xx in (.19,.47):
        for yy in (5.42,5.75):
            c.ring('Induction cooking zone',(xx,yy,.974),.105,.003,'metal')
    oven=c.empty('Oven',(.32,5.60,0),-math.pi/2)
    c.cube('Oven glass front',(0,-.329,.53),(.52,.025,.47),'black',.016,oven)
    c.cube('Oven handle',(0,-.363,.71),(.40,.032,.025),'metal',.007,oven)
    c.cube('Refrigerator body',(4.81,6.42,1.075),(.65,.70,2.15),'ivory cabinet',.016)
    for z,h in ((.37,.63),(1.42,1.39)):
        c.cube('Refrigerator door',(4.81,6.052,z),(.63,.035,h),'ivory cabinet',.012)
        c.cube('Refrigerator pull',(4.55,6.012,z),(.022,.034,.27),'metal',.006)
    # Backsplash is a permanent supporting wall; wall cabinets do not float.
    c.cube('Kitchen fixed backsplash',(2.65,6.77,1.535),(3.78,.06,1.14),'stone',.006)
    for i in range(5):
        c.cube('Kitchen wall cabinet',(1.33+i*.62,6.59,1.80),(.60,.33,.59),'ivory cabinet',.013)
    c.cube('Kitchen undercabinet LED',(2.57,6.41,1.50),(3.03,.022,.013),'light',.003)
    # Dining table and six upholstered chairs.
    c.cube('Dining table rounded top',(2.78,4.47,.77),(2.02,.95,.08),'oak',.10)
    for x in (1.96,3.60):
        for y in (4.15,4.78):
            c.cylinder('Dining table leg',(x,y,.375),.040,.75,'oak dark')
    for x in (2.18,2.78,3.38):
        chair('Dining chair north',x,5.16,0)
        chair('Dining chair south',x,3.79,math.pi)
    c.cylinder('Dining fruit bowl',(2.78,4.47,.84),.17,.06,'stone')
    for i in range(5):
        c.sphere('Bowl pear',(2.69+(i%3)*.08,4.44+(i//3)*.07,.90),(.055,.05,.06),'green light')
    # Lounge: all furnishings leave the east-side access route clear.
    c.cube('Living wool rug',(2.34,1.80,.043),(3.70,2.83,.035),'rug',.08)
    sofa('Living sectional',.70,1.85,2.74,math.pi/2,True)
    c.cube('Coffee table oak top',(2.65,1.70,.41),(1.09,.70,.055),'oak light',.085)
    for x in (2.23,3.07):
        for y in (1.45,1.95):
            c.cube('Coffee table leg',(x,y,.22),(.035,.035,.38),'oak dark',.004)
    c.cube('Coffee table book',(2.48,1.61,.455),(.26,.20,.026),'linen light',.004)
    c.cylinder('Coffee cup',(2.73,1.77,.48),.042,.07,'porcelain')
    c.cube('Media sideboard',(5.06,2.87,.36),(.40,1.78,.64),'oak',.018)
    c.cube('Television foot',(5.03,2.87,.71),(.30,.60,.03),'charcoal',.01)
    c.cube('Television stand',(5.08,2.87,.79),(.045,.045,.20),'charcoal',.005)
    c.cube('Television bezel',(5.12,2.87,1.16),(.035,1.24,.73),'black',.025)
    c.cube('Television glass',(5.096,2.87,1.16),(.008,1.18,.66),'screen',.004)
    c.cylinder('Reading floor lamp base',(1.06,3.19,.045),.19,.065,'charcoal')
    c.tube('Reading lamp arm',[(1.06,3.19,.07),(1.06,3.19,1.56),(1.25,3.19,1.69),(1.53,3.19,1.69)],.019,'charcoal')
    c.cylinder('Reading lamp shade',(1.55,3.19,1.64),.14,.13,'charcoal')
    c.cylinder('Reading lamp diffuser',(1.55,3.19,1.57),.12,.008,'light')
    c.plant('Living fern',.43,3.68,scale=.75)
    c.plant('Kitchen herb',3.65,6.41,.958,.22)


def bedrooms():
    c.ROOM='Parents bedroom'
    c.collection('06 Interior | Parents bedroom')
    c.cube('Parents wool rug',(2.50,8.91,.040),(3.40,2.91,.025),'rug',.055)
    bed('Parents double bed',2.45,9.29,1.82)
    wardrobe('Parents wardrobe',5.095,9.43,2.44,.60,math.pi/2)
    for x in (1.10,3.81):
        c.cube('Parents bedside table',(x,9.81,.34),(.49,.43,.55),'oak light',.025)
        c.cube('Bedside drawer',(x,9.584,.39),(.46,.021,.27),'oak light',.008)
        lamp('Parents bedside lamp',x,9.83,.625,.73)
    c.plant('Parents plant',.45,7.49,scale=.70)
    c.ROOM='Child bedroom'
    c.collection('07 Interior | Child bedroom')
    bed('Child single bed',10.74,6.22,.99)
    wardrobe('Child wardrobe',8.47,7.16,1.66,.60,0)
    desk('Child desk',8.47,5.34,1.26)
    chair('Child desk chair',8.47,4.79,0)
    c.cylinder('Child round rug',(9.72,5.76,.04),.58,.023,'rug',vertices=64)
    for i in range(5):
        c.cube('Child shelf book',(7.77+i*.06,7.15,2.21),(.045,.16,.15+i*.015),'rust' if i%3==0 else 'linen light',.004)
    c.ROOM='Office guest'
    c.collection('08 Interior | Office guest')
    sofa('Guest sleeper sofa',10.77,9.26,2.13,-math.pi/2)
    desk('Office desk',8.35,9.00,1.37,math.pi/2)
    chair('Office swivel chair',9.02,9.0,-math.pi/2,True)
    c.cube('Office rug',(9.78,9.27,.040),(2.95,2.08,.025),'rug',.06)
    # Low storage under the rear window, plus a small open shelving unit.
    c.cube('Office low storage',(8.95,10.51,.39),(1.84,.52,.74),'ivory cabinet',.02)
    for x in (8.49,9.41):
        c.cube('Office storage door',(x,10.237,.40),(.90,.028,.68),'ivory cabinet',.009)
    c.plant('Office plant',10.84,10.38,scale=.60)
    c.ROOM=None


def bathroom():
    c.ROOM='Bathroom WC'
    c.collection('09 Interior | Bathroom and WC')
    # Shower with raised rim, drain, glass partition and a wall-mounted mixer.
    c.cube('Shower tray',(7.77,3.65,.065),(1.26,1.13,.10),'porcelain',.045)
    c.cube('Shower non-slip inset',(7.77,3.65,.119),(1.12,.99,.013),'tile',.055)
    c.cube('Shower drain',(7.78,4.05,.13),(.58,.055,.008),'metal',.008)
    c.cube('Shower fixed wet wall',(7.74,4.215,1.05),(1.34,.06,2.10),'tile',.008)
    c.cube('Shower glass side',(8.41,3.69,1.08),(.015,1.00,1.90),'glass',.004)
    c.cube('Shower glass frame',(8.41,3.69,2.035),(.032,1.03,.03),'metal',.004)
    c.tube('Shower riser',[(7.72,4.14,.92),(7.72,4.14,2.06),(7.72,3.84,2.06)],.016,'metal')
    c.cylinder('Shower rain head',(7.72,3.82,2.03),.13,.032,'metal')
    c.cube('Shower mixer',(7.72,4.12,1.05),(.23,.075,.07),'metal',.022)
    # Vanity remains floor supported and the mirror has its own retained backing.
    c.cube('Bathroom vanity',(9.42,3.96,.48),(1.64,.52,.78),'oak light',.020)
    c.cube('Vanity stone top',(9.42,3.95,.905),(1.70,.56,.065),'stone',.017)
    for x in (8.98,9.85):
        c.cube('Vanity drawer',(x,3.689,.53),(.79,.025,.63),'oak light',.01)
        c.cube('Washbasin',(x,3.94,.986),(.61,.43,.11),'porcelain',.075)
        c.cube('Washbasin recess',(x,3.915,1.043),(.44,.27,.009),'stone',.05)
        c.tube('Basin tap',[(x,4.125,.94),(x,4.125,1.14),(x,4.00,1.14)],.012,'metal')
    c.cube('Mirror backing',(9.42,4.21,1.51),(1.73,.07,1.06),'wall interior',.012)
    c.cube('Vanity mirror',(9.42,4.161,1.56),(1.58,.023,.80),'metal',.016)
    c.cube('Vanity LED',(9.42,4.12,2.00),(1.50,.022,.018),'light',.004)
    # Wall-hung toilet with a recognisable ceramic bowl and closed oval seat.
    c.cube('Toilet concealed cistern',(11.14,2.63,.64),(.40,.72,1.27),'wall interior',.035)
    c.sphere('Toilet ceramic bowl',(10.77,2.63,.34),(.38,.23,.24),'porcelain')
    c.sphere('Toilet seat',(10.76,2.63,.57),(.355,.235,.040),'porcelain')
    c.cube('Toilet flush plate',(10.932,2.63,1.02),(.015,.23,.14),'metal',.018)
    c.cube('Bathroom bathmat',(9.50,2.96,.044),(1.22,.60,.025),'linen taupe',.085)
    c.tube('Towel rail',[(11.30,3.55,.93),(11.20,3.55,.93),(11.20,4.08,.93),(11.30,4.08,.93)],.014,'metal')
    c.cube('Folded bath towel',(11.19,3.80,.72),(.06,.42,.42),'linen light',.02)
    c.ROOM=None


def utility():
    c.ROOM='Utility electrical'
    c.collection('10 Interior | Utility and electrical equipment')
    for name,x in [('Washing machine',8.32),('Dryer',9.02)]:
        root=c.empty(name,(x,1.43,0))
        c.cube(name+' body',(0,0,.45),(.62,.64,.88),'white',.025,root)
        c.cube(name+' control strip',(0,-.333,.77),(.55,.022,.13),'white',.009,root)
        c.cylinder(name+' selector',(-.12,-.352,.78),.028,.017,'metal',root,(math.pi/2,0,0))
        c.cube(name+' display',(.12,-.349,.79),(.13,.006,.045),'screen',.003,root)
        c.ring(name+' chrome door ring',(0,-.346,.43),.211,.021,'metal',root,(math.pi/2,0,0))
        c.cylinder(name+' dark door',(0,-.350,.43),.188,.020,'screen',root,(math.pi/2,0,0))
        c.ring(name+' inner door seal',(0,-.365,.43),.155,.009,'charcoal',root,(math.pi/2,0,0))
        c.cube(name+' kick panel',(0,-.328,.08),(.56,.017,.10),'white',.009,root)
    # Small worktop at front leaves 1.05 m clear in front of appliances.
    c.cube('Laundry oak worktop',(8.67,1.43,.92),(1.38,.69,.06),'oak light',.02)
    c.cube('Laundry tall cabinet',(7.40,1.49,1.05),(.60,.57,2.10),'ivory cabinet',.012)
    for z in (.55,1.57):
        c.cube('Laundry storage door',(7.40,1.192,z),(.58,.025,.98),'ivory cabinet',.009)
    c.ROOM=None


def outside():
    c.collection('13 Terrace and landscape')
    c.plant('Entrance planter',7.00,-.92,-.12,.65)
    c.cube('Terrace herb planter',(.31,-1.44,.06),(.69,.58,.35),'stone',.022)
    for x,y in [(.08,-1.49),(.42,-1.48),(.29,-1.21)]:
        c.plant('Terrace herbs',x,y,.20,.42)
    c.cylinder('Terrace bistro table',(1.65,-1.10,.59),.40,.055,'oak')
    c.cylinder('Bistro table stem',(1.65,-1.10,.23),.027,.68,'charcoal')
    c.cylinder('Bistro table foot',(1.65,-1.10,-.10),.22,.035,'charcoal')
    chair('Terrace chair',2.50,-1.12,math.pi/2).location.z=-.12


def build():
    kitchen()
    bedrooms()
    bathroom()
    utility()
    outside()
