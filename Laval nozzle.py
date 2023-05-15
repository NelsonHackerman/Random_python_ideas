import pygame as pg
from numpy import *
import math
#input values
ratio = 0.25 # throat to exit area ratio # 0.6536
pep0 = 0.99
rho0 = 10
t0 = 500

pg.init()
run=True

clock=pg.time.Clock()
screen=pg.display.set_mode((0,0),pg.FULLSCREEN)

xview = 0.8 #0.7
yview = 0
scale = 250
move = 5
red = (255,0,0)
green = (0,255,0)
white = (255,255,255)
simulspeed = 0.005
choked = False
nonsw = False

#nozzle geometry
xr = linspace(0, 3, 100)
xl = linspace(-2, 0, 100)
yrup = ratio + (1 - ratio) / (1 + e ** (-3 * xr + 4.5)) + 0.05
yrdown = -yrup
ylup = ratio + (0.5 - ratio/2) / (1 + e ** (5 * xl + 5)) + 0.007 + 0.05
yldown = -ylup
ae = ratio + (1 - ratio) / (1 + e ** (-3 * 3 + 4.5))
at = ratio + (1 - ratio) / (1 + e ** (-3 * 0 + 4.5))
# particles
partic = 1500
ystart = (random.rand(1,partic)-0.5)*(1+ratio)
#ystart = [linspace(-0.5,0.5,partic)]
#xstart = ones(partic)-3
xstart = linspace(-20,-2,partic)

point = array([xstart,ystart[0]]).T
controlpoint = array([[-2,0.5+ratio/2]])
#print(point)


def essentials():
    pg.display.update()
    clock.tick(100)
    screen.fill((0,0,0))
    global key
    key=pg.key.get_pressed()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            global run
            run=False
def write(string, coordx, coordy, fontSize, color):
    # set the font to write with
    font = pg.font.Font('freesansbold.ttf', fontSize)
    # (0, 0, 0) is black, to make black text
    text = font.render(string, True, color)
    # get the rect of the text
    textRect = text.get_rect()
    # set the position of the text
    textRect.center = (coordx, coordy)
    # add text to window
    screen.blit(text, textRect)
def xshow(x):
    x2=700+(x - xview) * scale
    return x2
def yshow(y):
    y2 =400+(-y - yview) * scale
    return y2

# returns speed at subsonic conditions
def subsonic(A,astar):
    c = 1.2 * (A/astar)**(1/3)
    if 1.587 < c:
        m = c**(-3)
    elif 1.21<c<1.587:
        m = 0.137452*(c-1.053)**(-0.96534)
    else:
        m = 1-sqrt(3*c-3.6)
    t = t0 / (1 + 0.2 * m ** 2)
    v = m *(1.4*287*t)**0.5
    return v
# returns speed at supersonic conditions
def supersonic(A,astar):
    c = 1.2 * (A / astar) ** (1 / 3)
    if 1.32<c<3.5:
        m= 3.131*(c-1.015)**(0.5128)
    elif 1.213<c<1.32:
        m = 3.08076*(c-1.1539)**(1/3)
    else:
        m = 1+sqrt(3*c-3.6)
    t = t0 / (1 + 0.2 * m ** 2)
    v = m * (1.4 * 287 * t)**0.5
    return v

# returns ideal mach number Me6 and pressure change over oblique shockwave Pa/pe6 at exit when flow is isentropically accelerated
def idealexit():
    c = 1.2 * (ae / at) ** (1 / 3)
    if 1.32 < c < 3.5:
        m = 3.131 * (c - 1.015) ** (0.5128)
    elif 1.213 < c < 1.32:
        m = 3.08076 * (c - 1.1539) ** (1 / 3)
    else:
        m = 1 + sqrt(3 * c - 3.6)
    p0pe6 = (1+0.2*m**2)**3.5
    deltaP = p0pe6*pep0

    return m, deltaP

# location of normal shockwave d and critical throat area after shockwave a2
def nsw():
    core = astar/ae/pep0
    me = (2.5*((1+0.2679*core**2)**0.5-1))**0.5
    aea2 = 1/me*(0.8333+0.16667*me**2)**3
    a2 = ae/aea2
    p02p01 = aea2 * astar/ae

    m = linspace(1,5,10000)
    drho = 2.4 * m ** 2 / (2 + 0.4 * m ** 2)
    dp = 1 + 1.1667 * (m ** 2 - 1)
    y = drho ** 3.5 * dp ** (-2.5)
    error = (y-p02p01)**2
    ms1 = m[where(error== min(error))][0]
    answ = ((1 / ms1 ** 2 * (0.8333 + 0.16667 * ms1 ** 2) ** 6)*astar**2)**0.5
    d = min(1.5-0.3333*log((1-ratio)/(answ-ratio)-1),3)
    if math.isnan(d):
        d = 3
    return d,a2

def osw():
    me6,pratio = idealexit()
    mn6 = (0.8572*pratio+0.1428)**0.5
    beta1 = arcsin(min(mn6/me6,1))
    print(beta1)
    return beta1
# returns velocity array for each particle
def velocity(pos):
    vel = zeros((pos.shape[0],2))
    for i in range(pos.shape[0]):
        x= pos[i,0]
        y = pos[i,1]
        if x<0:
            A = (0.5-ratio/2)/(1+e**(5*x+5))+ratio+0.007
            dadx = -(0.5-ratio/2)/(1+e**(5*x+5))**2*5*e**(5*x+5) * y/A
            norm = (1+dadx**2)**0.5
            unitvelx = 1/norm
            unitvely = dadx/norm
            speed = subsonic(A,astar)
        if x>=0:
            A = (1 - ratio) / (1 + e ** (-3* x + 4.5)) + ratio
            dadx = -(1 - ratio) / (1 + e ** (-3 * x + 4.5)) ** 2 * (-3) * e ** (-3 * x + 4.5)*y/A
            norm = (1 + dadx ** 2) ** 0.5
            unitvelx = 1 / norm
            unitvely = dadx / norm
            if choked:
                if x<=d:
                    speed = supersonic(A,astar)
                elif x>d:
                    speed = subsonic(A,a2)
                #else:
                    #speed = supersonic(A, astar)
            else:
                speed =subsonic(A,astar)
        vel[i,0]=unitvelx*speed
        vel[i,1]=unitvely*speed

    return vel


while run:
    dt = 1 / 100 * simulspeed
    essentials()
    # Aerodynamics

    Me = (5 * pep0 ** (-0.4 / 1.4) - 5) ** 0.5
    # rhoerho0 =(1+0.2*Me**2)**(-2.5)
    # tet0 = 1/(1+0.2*Me**2)
    # mflow = rho0 * rhoerho0 * ae * Me *(1.4*8.314*t0*tet0)**0.5
    # astar = mflow * 1.8929 / rho0 * 1.0954 /(1.4*8.314*t0)**0.5
    astar1 = ae * Me * (0.8333 * (1 + 0.2 * Me ** 2)) ** (-3)
    astar = min(astar1, at)

    if astar == at:
        choked = True
        d,a2 = nsw()
       # print(d, nonsw)
        if d == 3:
            nonsw = True
        else:
            nonsw = False
    else:
        choked = False
    if nonsw:
        beta = osw()
        pg.draw.line(screen,green,[xshow(3),yshow(ae)],[xshow(3+ae/tan(beta)),yshow(0)],3)
    for i in range(xstart.shape[0]):
        if i%100 == 0:
            pg.draw.circle(screen,green,[xshow(point[i,0]),yshow(point[i,1])],7)
        else:
            pg.draw.circle(screen,red,[xshow(point[i,0]),yshow(point[i,1])],7)


    rup = array([xshow(xr), yshow(yrup)]).T
    rdown = array([xshow(xr), yshow(yrdown)]).T
    lup = array([xshow(xl), yshow(ylup)]).T
    ldown = array([xshow(xl), yshow(yldown)]).T
    pg.draw.lines(screen,white,False,rup,10)
    pg.draw.lines(screen,white,False,rdown,10)
    pg.draw.lines(screen,white,False,lup,10)
    pg.draw.lines(screen,white,False,ldown,10)
    #integration
    point+= velocity(point)*dt
    adjust = point[where(point[:,0]>3),1][0]
    if len(adjust)>30:
        edge = max(abs(adjust))
        point[:, 1] *= 1 + (1 - edge) / 100

    # resetting position of points.
    resetpos = 6
    for i in range(point.shape[0]):
        if point[i,0]>resetpos:
            point[i,0]-=(resetpos+3)
            point[i,1]*=(1+ratio)/2


    key = pg.key.get_pressed()
    if key[pg.K_d]:
        simulspeed *=1.01
    if key[pg.K_a]:
        simulspeed *= 0.99
    if key[pg.K_w]:
        if pep0<0.9999 and not choked:
            pep0+=0.0001
        elif choked:
            pep0 += 0.0005*(3.5-d)**2
    if key[pg.K_s]:
        if not choked:
            pep0 -= 0.0001
        elif pep0 > 0.01 and choked:
            pep0 -= 0.0005*(3.5-d)**2

    '''''
    if key[pg.K_UP]:
        ratio *=1.01
    if key[pg.K_DOWN]:
        ratio *= 0.99
    
    if key[pg.K_RIGHT]:
        xview += move / scale
    if key[pg.K_LEFT]:
        xview -= move / scale
    if key[pg.K_UP]:
        yview -= move / scale
    if key[pg.K_DOWN]:
        yview += move / scale

    if key[pg.K_w]:
        scale = scale * 1.01
    if key[pg.K_s]:
        scale = scale * 0.99
    '''''
    write("Pe/P0: "+str(round(pep0,3)),1300,20,20,white)
    #write("Me: "+str(round(Me,3)),1300,50,20,white)
    #write("Astar: "+str(round(astar,3)),1300,80,20,white)

    if choked:
        thrspeed = subsonic(astar+0.0001, astar)
        write("Velocity at throat: " + str(round(thrspeed)) + " m/s", 1250, 50, 20, white)
        write("regime: sonic at throat",1250,80,20,white)
    else:
        thrspeed = subsonic(at, astar)
        write("Velocity at throat: " + str(round(thrspeed)) + " m/s", 1250, 50, 20, white)
        if thrspeed < 0.3*(1.4*287*t0*0.8333)**0.5:
            write("regime: incompressible", 1250, 80, 20, white)
        else:
            write("regime: subsonic compressible", 1230, 80, 20, white)



pg.quit()
