import pygame as pg
import numpy as np
pg.init()
run=True

clock=pg.time.Clock()
screen=pg.display.set_mode((1400,800))

xview = 0
yview = -1.5
scale = 100
move = 5
red = (255,0,0)
green = (0,255,0)
white = (255,255,255)
purple = (255,0,255)
grav = np.array([0,-5])
xhat = np.array([1,0])
yhat = np.array([0,1])
dt = 1/60
t=0

def essentials():
    pg.display.update()
    clock.tick(60)
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


kf = 2000
cf = 30
dragcoeff = 2
strength=0
kb = 1000
cb = 10
bl = 1
ulna = 0.75
body = 3
# mass,mu
mass = np.array([5.0,8.0,1,1,1,1,1,1,1,1])
mu = np.array([5.0,5.0,5,100,5,100,5,100,5,100])
# node1,node2,length,kb,cb
system = [[0,1,body,kb,cb],[0,2,bl,kb,cb],[2,3,bl*ulna,kb,cb],[0,4,bl,kb,cb],[4,5,bl*ulna,kb,cb],[1,6,bl,kb,cb],[6,7,bl*ulna,kb,cb],[1,8,bl,kb,cb],[8,9,bl*ulna,kb,cb]]
# node1,center,node2,length1,length2
muscle = [[2,0,1,bl,body],[4,0,1,bl,body],[3,2,0,bl*ulna,bl],[5,4,0,bl*ulna,bl],[0,1,6,body,bl],[0,1,8,body,bl],[7,6,1,bl*ulna,bl],[9,8,1,bl*ulna,bl]]
nodes = len(mass)

# instance 1
crook = -0.2
pos = np.array([[0,2.5],[body,2.5],[crook,1.5],[0,0.5],[2*crook,1.5],[crook,0.5],[body+crook,1.5],[body,0.5],[body+2*crook,1.5],[body+crook,0.5]])
vel = np.zeros(pos.shape)



def accel(pos,vel,activation):
    acc = pos*0
    for i in range(nodes):
        floortouch = pos[i,1]<0
        normal = (-kf*pos[i,1]-cf*vel[i,1])*yhat/mass[i]
        friction = -mu[i]*np.sign(vel[i,0])*xhat
        floor = floortouch*(normal+friction)
        speed = (vel[i,0]**2+vel[i,1]**2)**0.5
        drag = -dragcoeff*speed*vel[i,:]
        acc[i,:]=grav+floor+drag
    for i,link in enumerate(system):
        node1 = link[0]
        node2=link[1]
        length = link[2]
        kb = link[3]
        cb = link[4]
        vector = pos[node2,:]-pos[node1,:]
        dist = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
        unit = vector/dist
        speed = vel[node2,:]-vel[node1,:]
        proj = np.dot(speed,unit)
        dist = (vector[0]**2+vector[1]**2)**0.5
        delta = dist-length
        bone = (kb*delta+cb*proj)*unit
        acc[node1,:]+= bone/mass[node1]
        acc[node2,:]-= bone/mass[node2]
    for i,link in enumerate(muscle):
        node1=link[0]
        center=link[1]
        node2=link[2]
        l1 = link[3]
        l2= link[4]
        vector1 = pos[node1, :] - pos[center, :]
        vector2 = pos[node2, :] - pos[center, :]
        m1 = np.array([vector1[1],-vector1[0]])*activation[i]/l1**2
        m2 = np.array([-vector2[1],vector2[0]])*activation[i]/l2**2
        mc = -m1-m2
        acc[node1,:]+=m1/mass[node1]
        acc[node2,:]+=m2/mass[node2]
        acc[center,:]+=mc/mass[center]
    return acc

def angle(p1,pc,p2):
    vec1 = p1-pc
    vec2 = p2-pc
    dist1 = (vec1[0] ** 2 + vec1[1] ** 2) ** 0.5
    dist2 = (vec2[0] ** 2 + vec2[1] ** 2) ** 0.5
    unit1 = vec1/dist1
    unit2 = vec2/dist2
    angle = np.arccos(np.dot(unit1, unit2))
    return angle

def euler(pos,vel,accel):
    vel += accel*dt
    pos += vel*dt
    for i in range(nodes):
        if pos[i,1]<0.1 : # and abs(vel[i,0])<0.5*100
            vel[i,0]*=0
    #pos[0,:]=np.array([0,2.5])
    #pos[1,:]=np.array([2,2.5])

def stand(pos,vel,t):
    n = len(muscle)
    activation=np.zeros(n)
    hip = np.pi*3.2/4
    knee = np.pi*2.4/4
    shoulder = np.pi*1/4
    elbow = np.pi*2/4
    theta = np.array([hip,hip,knee,knee,shoulder,shoulder,elbow,elbow]) # ideal angles of joints
    for i,mus in enumerate(muscle):
        phi = angle(pos[int(mus[0]),:],pos[int(mus[1]),:],pos[int(mus[2]),:])
        activation[i]= (theta[i]-phi)*50
    return activation

start = 3
def walk(pos,vel,t):

    time = 0
    strength = 300
    n = len(muscle)
    if t>start:
        time = (t-start)*2
    level=1.5
    buttheight = (pos[0,1]-level)*(pos[0,1]<level)
    headheight = (pos[1,1]-level)*(pos[1,1]<level)

    stride11=np.pi/1.5+np.pi/7*np.cos(time)
    stride12=np.pi/1.5-np.pi/7*np.cos(time)
    stride21=np.pi/2.5+np.pi/7*np.cos(time)
    stride22=np.pi/2.5-np.pi/7*np.cos(time)
    activation = np.zeros(n)
    for i,mus in enumerate(muscle):
        phi = angle(pos[int(mus[0]), :], pos[int(mus[1]), :], pos[int(mus[2]), :])
        if i == 0:
            activation[i]= (stride11-phi)*strength
        elif i==5:
            activation[i] = (stride21 - phi) * strength
        elif i == 1:
            activation[i]= (stride12-phi)*strength
        elif i == 4:
            activation[i] = (stride22 - phi) * strength
    bonus=0.3
    nerf = 0.3
    if 0<=(time/np.pi)%2<1:
        activation[2]= (pos[3,1]-0.3)*strength*nerf
        activation[6]= (pos[7,1]-0.3)*strength*nerf
        activation[3]= -buttheight*strength*bonus*2.5
        activation[7]= -headheight*strength*bonus*1

    if 1<=(time/np.pi)%2<2:
        activation[3]= (pos[5,1]-0.3)*strength*nerf
        activation[7]= (pos[9,1]-0.3)*strength*nerf
        activation[2]= -buttheight*strength*bonus*2.5
        activation[6]= -headheight*strength*bonus*1

    return activation


def depict(pos,color):
    for i,link in enumerate(system):
        pg.draw.line(screen, red, [xshow(pos[link[0],0]), yshow(pos[link[0],1])], [xshow(pos[link[1],0]), yshow(pos[link[1],1])], 3)
    for i in range(nodes):
        pg.draw.circle(screen,color,[xshow(pos[i,0]),yshow(pos[i,1])],10)


def execute(pos,vel,activation,color=green):
    acc = accel(pos, vel, activation)
    euler(pos, vel, acc)
    depict(pos, color)

while run:
    essentials()
    if t<start:
        strength = stand(pos,vel,t)
    else:
        strength = walk(pos,vel,t)
    key = pg.key.get_pressed()
    if key[pg.K_e]:
        strength[6:8]=100
    execute(pos,vel,strength,green)


    pg.draw.line(screen,white,[0,yshow(-0.1)],[1400,yshow(-0.1)],3)

    # progress lines
    cline = round(xview/5)*5
    pg.draw.line(screen, white, [xshow(cline), yshow(-0.11)], [xshow(cline), yshow(-1)], 3)
    pg.draw.line(screen, white, [xshow(cline+5), yshow(-0.11)], [xshow(cline+5), yshow(-1)], 3)
    pg.draw.line(screen, white, [xshow(cline-5), yshow(-0.11)], [xshow(cline-5), yshow(-1)], 3)

    if key[pg.K_RIGHT]:
        xview += move / scale
    if key[pg.K_LEFT]:
        xview -= move / scale
    if key[pg.K_UP]:
        yview -= move / scale
    if key[pg.K_DOWN]:
        yview += move / scale
    xview = 0.5*pos[1,0]+0.5*pos[0,0]
    strength2=0
    if key[pg.K_w]:
        scale *=1.005
    if key[pg.K_s]:
        scale *=0.995


    t+=dt
pg.quit()
