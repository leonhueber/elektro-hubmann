"""Detailed furniture made for the V4 reference: cloth, joinery and hollow ceramics."""
import math
from mathutils import Vector
from . import core as c


def plant(name,x,y,z=0,height=.65,pot=.16,parent=None):
    root=c.empty(name,(x,y,z),parent=parent)
    c.lathe(name+' | hollow ceramic pot',(0,0,0),[(0,0),(.64*pot,0),(.91*pot,.08*pot),(pot,1.30*pot),(pot*.92,1.35*pot),(.85*pot,1.30*pot),(.72*pot,.25*pot),(0,.25*pot)],'stone',root)
    c.cylinder(name+' | soil',(0,0,pot*1.20),pot*.85,.03,'soil',root)
    verts=[];faces=[]
    for branch in range(44):
        a=c.RNG.random()*math.tau
        top=Vector((math.cos(a)*height*c.RNG.uniform(.18,.34),math.sin(a)*height*c.RNG.uniform(.18,.34),height*c.RNG.uniform(.54,.95)+pot))
        start=Vector((0,0,pot))
        branch_obj=c.tube(name+' | tapered woody branch',[start,start.lerp(top,.4)+Vector((0,0,.04)),top],.002 if height<1 else .0035,'bark',root)
        for point,radius in zip(branch_obj.data.splines[0].points,[1,.56,.08]):point.radius=radius
        for j in range(30):
            center=start.lerp(top,.30+.022*j)
            aa=a+j*2.39996
            length=height*c.RNG.uniform(.08,.14)
            direction=Vector((math.cos(aa),math.sin(aa),.36)).normalized()*length
            side=Vector((-math.sin(aa),math.cos(aa),.0))*length*.22
            n=len(verts)
            for k in range(7):
                t=k/6
                mid=center+direction*t+Vector((0,0,length*.13*math.sin(math.pi*t)))
                spread=side*math.sin(math.pi*t)**.8
                ridge=Vector((0,0,length*.07*math.sin(math.pi*t)))
                verts.extend([tuple(mid-spread),tuple(mid+ridge),tuple(mid+spread)])
            for k in range(6):
                for strip in range(2):faces.append((n+k*3+strip,n+k*3+strip+1,n+(k+1)*3+strip+1,n+(k+1)*3+strip))
    leaf=c.mesh(name+' | individual leaves',verts,faces,'leaf',root,smooth=True)
    leaf.data.materials.append(c.M['leaf light'])
    for p in leaf.data.polygons:p.material_index=(p.index//12)%3==0
    return root


def lamp(name,x,y,z,parent=None,table=True):
    root=c.empty(name,(x,y,z),parent=parent)
    height=.36 if table else 1.53
    radius=.12 if table else .20
    c.cylinder(name+' | foot',(0,0,.015),radius*.66,.028,'brass',root)
    c.cylinder(name+' | stem',(0,0,height*.43),.012,height*.8,'brass',root)
    c.lathe(name+' | linen shade',(0,0,height*.73),[(radius,0),(radius*.63,height*.26),(radius*.59,height*.26),(radius*.95,.008)],'linen white',root)
    c.soft(name+' | opal bulb',(0,0,height*.83),(.065,.065,.10),'light',root)
    light=c.area(name+' | warm pool',(0,0,height*.79),(0,0,0),12 if table else 30,.25,parent=root)
    light['interior_light']=True;light['nominal_watts']=light.data.energy
    return root


def art(name,x,y,z,width=.55,height=.75,parent=None,angle=0):
    root=c.empty(name,(x,y,z),angle,parent)
    c.box(name+' | oak frame',(0,0,0),(width,.035,height),'oak pale',.003,root)
    c.box(name+' | mat board',(0,-.022,0),(width-.035,.008,height-.035),'paper',.001,root)
    # Quiet botanical relief behind glass, native geometry rather than a missing texture.
    for i in range(3):
        c.tube(name+' | fine botanical stem',[(0,-.029,-height*.30),((i-1)*width*.13,-.029,height*.27)],.002,'taupe',root)
        for j in range(4):
            leaf=c.soft(name+' | botanical leaf',((i-1)*width*.13*(j+1)/5+(-1)**j*.045,-.032,-height*.20+j*height*.12),(.11,.004,.045),'olive',root,.8)
            leaf.rotation_euler.y=.5*(-1)**j


def rug(name,x,y,width,length,parent=None):
    c.box(name,(x,y,.061),(width,length,.025),'rug',.022,parent)
    for side in [-1,1]:
        for i in range(int(width/.035)):
            xx=x-width/2+i*.035
            c.rod(name+' | short fringe',(xx,y+side*length/2,.062),(xx+.004,y+side*(length/2+.04),.057),.0015,'taupe',parent)


def table(name,x,y,width=1.9,depth=.92,height=.75,parent=None,angle=0,radius=.08):
    root=c.empty(name,(x,y,0),angle,parent)
    radius=min(radius,depth/2-.001,width/2-.001)
    outline=[]
    for xx,yy,start in [(width/2-radius,depth/2-radius,0),(-width/2+radius,depth/2-radius,90),
                        (-width/2+radius,-depth/2+radius,180),(width/2-radius,-depth/2+radius,270)]:
        for i in range(13):
            a=math.radians(start+i*90/12)
            outline.append((xx+radius*math.cos(a),yy+radius*math.sin(a)))
    n=len(outline)
    verts=[(xx,yy,zz) for zz in [height-.0275,height+.0275] for xx,yy in outline]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    c.mesh(name+' | rounded solid oak top',verts,faces,'oak pale',root,bevel=.006)
    for xx in [-width*.36,width*.36]:
        for yy in [-depth*.33,depth*.33]:
            c.rod(name+' | tapered leg',(xx*1.06,yy*1.1,.07),(xx,yy,height-.025),.028,'oak',root)
    return root


def chair(name,x,y,angle=0,parent=None):
    root=c.empty(name,(x,y,0),angle,parent)
    c.soft(name+' | upholstered seat',(0,0,.46),(.47,.45,.09),'linen',root,exponent=.45,seam=True)
    for xx in [-.185,.185]:
        for yy in [-.17,.17]:c.rod(name+' | oak leg',(xx*1.17,yy*1.2,.065),(xx,yy,.46),.019,'oak',root)
    # Curved open back and low arms avoid a block-chair silhouette.
    points=[(.245*math.cos(a),.19+.11*math.sin(a),.81) for a in [i*math.pi/32 for i in range(33)]]
    c.tube(name+' | bentwood back rail',points,.027,'oak',root)
    back=c.soft(name+' | curved back pad',(0,.245,.745),(.40,.065,.21),'linen',root,.5)
    for xx in [-.22,.22]:c.rod(name+' | back support',(xx,.16,.44),(xx,.22,.81),.018,'oak',root)
    return root


def cabinet(name,x,y,width=1.6,height=2.2,depth=.60,parent=None,angle=0,drawers=False,open_top=False):
    root=c.empty(name,(x,y,0),angle,parent)
    c.box(name+' | recessed plinth',(0,0,.085),(width-.07,depth-.06,.13),'oak dark',.004,root)
    for xx in [-width/2+.009,width/2-.009]:
        c.box(name+' | carcass side',(xx,0,(height+.13)/2),(.018,depth,height-.13),'oak pale',.003,root)
    c.box(name+' | carcass back',(0,depth/2-.009,(height+.13)/2),(width,.018,height-.13),'oak pale',.003,root)
    c.box(name+' | carcass bottom',(0,0,.145),(width,depth,.03),'oak pale',.003,root)
    if not open_top:c.box(name+' | carcass top',(0,0,height-.015),(width,depth,.03),'oak pale',.003,root)
    n=max(1,round(width/.52));d=width/n
    for i in range(n):
        xx=-width/2+d*(i+.5)
        if drawers:
            for j in range(3):
                zz=.16+(height-.18)*(j+.5)/3
                c.box(name+' | drawer front',(xx,-depth/2-.02,zz),(d-.006,.035,(height-.18)/3-.008),'oak',.006,root)
                c.rod(name+' | drawer pull',(xx-.08,-depth/2-.05,zz+.07),(xx+.08,-depth/2-.05,zz+.07),.007,'charcoal',root)
        else:
            c.box(name+' | individual door',(xx,-depth/2-.02,(height+.15)/2),(d-.006,.035,height-.17),'oak',.006,root)
            c.rod(name+' | slim handle',(xx+.12,-depth/2-.05,height*.45),(xx+.12,-depth/2-.05,height*.55),.006,'charcoal',root)
    return root


def bedding(name,width,parent):
    # A continuous cloth sheet drapes over the mattress; folds extend into the silhouette.
    nx,ny=65,51
    verts=[]
    for j in range(ny):
        y=-1.17+j*1.68/(ny-1)
        for i in range(nx):
            x=-(width/2+.13)+i*(width+.26)/(nx-1)
            edge=max(0,(abs(x)-width*.44)/.18)
            foot=max(0,(-y-.93)/.24)
            z=.64-.24*min(1,edge)**1.5-.22*min(1,foot)**1.4
            z+=.015*math.sin(x*15+y*5)+.011*math.sin(x*25-y*13)+.008*math.sin(y*34+x*6)
            z+=.035*math.exp(-((y-.39)/.08)**2)
            verts.append((x,y,z))
    faces=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
    o=c.mesh(name+' | draped linen duvet',verts,faces,'linen white',parent,smooth=True)
    solid=o.modifiers.new('Actual cloth thickness','SOLIDIFY');solid.thickness=.009
    # Separate woven throw across the foot with its own irregular drape.
    v=[];f=[]
    for j in range(19):
        yy=-.99+j*.53/18
        for i in range(45):
            xx=-(width/2+.16)+i*(width+.32)/44
            zz=.68-.28*min(1,max(0,(abs(xx)-width*.43)/.23))**1.4+.009*math.sin(xx*24+yy*12)
            v.append((xx,yy,zz))
    f=[(j*45+i,j*45+i+1,(j+1)*45+i+1,(j+1)*45+i) for j in range(18) for i in range(44)]
    throw=c.mesh(name+' | woven foot throw',v,f,'taupe',parent,smooth=True)
    throw.modifiers.new('Woven thickness','SOLIDIFY').thickness=.007


def bed(name,x,y,width=1.8,angle=0,parent=None):
    root=c.empty(name,(x,y,0),angle,parent)
    for xx in [-width*.40,width*.40]:
        for yy in [-.88,.88]:c.cylinder(name+' | oak foot',(xx,yy,.14),.035,.23,'oak',root)
    c.box(name+' | oak bed frame',(0,0,.265),(width+.12,2.13,.21),'oak pale',.024,root)
    c.soft(name+' | mattress',(0,0,.47),(width,2.04,.24),'linen white',root,.25,seam=True)
    c.box(name+' | solid oak headboard',(0,1.085,.62),(width+.15,.09,1.08),'oak',.026,root)
    c.soft(name+' | headboard linen inset',(0,1.021,.78),(width-.10,.065,.52),'linen',root,.4)
    bedding(name,width,root)
    count=2 if width>1.3 else 1
    for i in range(count):
        xx=(i-(count-1)/2)*width/count
        c.soft(name+' | filled pillow',(xx,.66,.675),(width/count-.11,.51,.16),'linen white',root,.4,(-.10,.03,(-1)**i*.055),True)
        c.soft(name+' | linen accent pillow',(xx,.43,.733),(width/count-.22,.38,.10),'linen',root,.42,(-.12,.01,-.04),True)
    return root


def sofa(name,x,y,parent=None):
    root=c.empty(name,(x,y,0),parent=parent)
    for xx in [-1.3,1.3]:
        for yy in [-.36,.37]:c.cylinder(name+' | recessed oak foot',(xx,yy,.105),.035,.13,'oak dark',root)
    c.soft(name+' | long upholstered base',(0,0,.275),(2.96,.95,.31),'linen',root,.3)
    c.soft(name+' | chaise base',(-1.02,-.70,.275),(.95,1.40,.31),'linen',root,.3)
    for i in range(3):c.soft(name+' | separate seat cushion',(-.95+i*.95,-.02,.47),(.91,.77,.20),'linen',root,.35,seam=True)
    c.soft(name+' | chaise seat',(-1.02,-.82,.47),(.87,.76,.20),'linen',root,.35,seam=True)
    for i in range(3):c.soft(name+' | back cushion',(-.94+i*.94,.365,.75),(.91,.24,.60),'linen',root,.35,(-.11,0,0),True)
    for xx in [-1.48,1.48]:c.soft(name+' | upholstered arm',(xx,-.06,.62),(.19,.92,.48),'linen',root,.33)
    for xx,ang in [(-1.04,-.17),(.97,.14)]:
        c.soft(name+' | olive scatter pillow',(xx,.17,.80),(.42,.15,.41),'olive',root,.6,(-.18,ang,ang),True)
    return root


def basin(name,x,y,z,width=.56,depth=.42,parent=None):
    # Superelliptic shell from outside base, over the lip, down to the hollow floor.
    profile=[(.78,.00),(1,.10),(1,.17),(.88,.18),(.77,.055),(0,.05)]
    verts=[];segments=64
    for r,h in profile:
        for i in range(segments):
            a=i*math.tau/segments
            xx=math.copysign(abs(math.cos(a))**.52,math.cos(a))*width*.5*r
            yy=math.copysign(abs(math.sin(a))**.52,math.sin(a))*depth*.5*r
            verts.append((xx,yy,h))
    faces=[(j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i) for j in range(len(profile)-1) for i in range(segments)]
    o=c.mesh(name+' | hollow basin',verts,faces,'ceramic',parent,smooth=True);o.location=(x,y,z)
    c.cylinder(name+' | basin waste',(x,y,z+.053),.02,.005,'steel',parent)
    faucet(name,x,y+depth*.39,z+.14,parent)
    return o


def faucet(name,x,y,z,parent=None):
    c.cylinder(name+' | tap foot',(x,y,z),.028,.018,'steel',parent)
    c.tube(name+' | bent spout',[(x,y,z),(x,y,z+.21),(x,y-.035,z+.25),(x,y-.15,z+.25),(x,y-.18,z+.22)],.015,'steel',parent)
    c.rod(name+' | mixer lever',(x+.035,y,z+.07),(x+.035,y+.02,z+.13),.01,'steel',parent)


def toilet(name,x,y,angle=0,parent=None):
    root=c.empty(name,(x,y,0),angle,parent)
    c.soft(name+' | ceramic pan',(0,0,.32),(.37,.56,.33),'ceramic',root,.55)
    rim=c.lathe(name+' | open bowl rim',(0,-.02,.455),[(.15,0),(.182,.016),(.18,.033),(.125,.035),(.11,-.09),(0,-.10)],'ceramic',root,scale=(1,1.43,1))
    c.soft(name+' | soft-close lid',(0,-.02,.502),(.366,.51,.025),'ceramic',root,.50)
    c.box(name+' | flush plate',(0,.30,1.02),(.23,.022,.15),'steel',.012,root)
    for xx,r in [(-.04,.027),(.05,.018)]:c.cylinder(name+' | flush button',(xx,.284,1.02),r,.007,'charcoal',root,(math.pi/2,0,0))
    return root


def tub(name,x,y,parent=None):
    root=c.empty(name,(x,y,0),parent=parent)
    profile=[(.84,.05),(1,.47),(1,.56),(.91,.565),(.83,.21),(.64,.16),(0,.16)]
    verts=[]
    for r,z in profile:
        for i in range(96):
            a=i*math.tau/96
            verts.append((math.copysign(abs(math.cos(a))**.44,math.cos(a))*1.0*r,math.copysign(abs(math.sin(a))**.60,math.sin(a))*.43*r,z))
    faces=[(j*96+i,j*96+(i+1)%96,(j+1)*96+(i+1)%96,(j+1)*96+i) for j in range(len(profile)-1) for i in range(96)]
    c.mesh(name+' | hollow freestanding stone tub',verts,faces,'stone',root,smooth=True)
    c.cylinder(name+' | chrome waste',(.45,0,.165),.025,.01,'steel',root)
    c.tube(name+' | bath filler',[(.55,.52,.08),(.55,.52,.82),(.55,.25,.82),(.55,.22,.77)],.025,'steel',root)
    return root


def curtain(name,x,y,z,width,height=2.2,parent=None,angle=0):
    root=c.empty(name,(x,y,z),angle,parent)
    verts=[]
    for j in range(21):
        for i in range(65):
            xx=-width/2+width*i/64
            yy=.025*math.sin(i*math.pi/4)*(1+.12*j/20)
            zz=height*(1-j/20)+.007*math.sin(i*math.pi/4)
            verts.append((xx,yy,zz))
    faces=[(j*65+i,j*65+i+1,(j+1)*65+i+1,(j+1)*65+i) for j in range(20) for i in range(64)]
    cloth=c.mesh(name+' | folded linen',verts,faces,'linen white',root,smooth=True)
    cloth.modifiers.new('Linen thickness','SOLIDIFY').thickness=.003
    return root
