import numpy as np
import pygame as pg
from numpy import pi,e,sin,cos,sqrt
from math import ceil
#partial differential equation on u(x,y,t) (wave equation)

slitsize=6
slitdist=10
wallx=70





def pulse(arr,arr2,locx,locy,widthx=1.0,widthy=1.0):
    return e**(-(arr-locx)**2/widthx-(arr2-locy)**2/widthy)
dx=0.07
dy=dx

x=np.arange(0,13,dx)
const1=np.ones(len(x))
y=np.arange(0,7,dy)
const2=np.ones(len(y))

xmesh=np.outer(const2,x)
ymesh=np.outer(y,const1)

######initial function
umesh=xmesh*0 #colorrange 4 and floor -0.25

colorrange=3
floor=-0.5
#####

divmesh=np.zeros((len(y),len(x))) #divergence
lapmesh=np.zeros((len(y),len(x))) #laplacian
utmesh=np.zeros((len(y),len(x)))
uttmesh=np.zeros((len(y),len(x)))
hill3=np.array([[0.25,0.5,0.25],[0.5,1,0.5],[0.25,0.5,0.25]])

dt=1/50
#######################################################################
v=0.065/dt/1.5

autoadjust=False

pg.init()
run=True
clock=pg.time.Clock()
screen=pg.display.set_mode((1400,800))

def essentials():
    pg.display.update()
    clock.tick(50)
    screen.fill((0,0,0))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            global run
            run=False
def color(x,range):
    red=max(0,min(510/range*x,255))
    blue=max(0,min(510-510/range*x,255))
    return (red,50,blue)

def yview(arr):
    newarr = arr*100+50
    return newarr
def xview(arr):
    newarr = arr*100+50
    return newarr
t=0
while run:
    essentials()
    t+=dt


    for n in range(len(x)-1):
        for m in range(len(y)-1):
            #divmesh[m,n]=(umesh[m,n+1]-umesh[m,n])/dx+(umesh[m,n]-umesh[m+1,n])/dy
            if n!=0 and m!=0:
                lapmesh[m,n]=(umesh[m,n-1]+umesh[m,n+1]-2*umesh[m,n])/dx**2+(umesh[m-1,n]+umesh[m+1,n]-2*umesh[m,n])/dy**2


    uttmesh=v**2*lapmesh
    utmesh += uttmesh*dt
    umesh+=utmesh*dt
    #boundary conditions
    umesh[:,0]=umesh[:,1]
    umesh[:, -1] = umesh[:, -2]
    umesh[0, :] = umesh[1, :]
    umesh[-1, :] = umesh[-2, :]

    if t<pi/2:
        umesh[:,0]=-cos(t*20)+1

    umesh[0,0] = umesh[1,1]
    umesh[0, -1] = umesh[1, -2]
    umesh[-1, 0] = umesh[-2, 1]
    umesh[-1, -1] = umesh[-2, -2]

    #extra walls for slit

    inter1=50-slitdist-slitsize
    midup=50-slitdist
    middown=50+slitdist
    inter2 = 50+slitdist+slitsize-1
    umesh[0:inter1,wallx]=69.0
    umesh[0:inter1,wallx-1]=umesh[0:inter1,wallx-2]
    umesh[0:inter1, wallx+1] = umesh[0:inter1, wallx+2]
    umesh[inter1,wallx]=umesh[inter1,wallx-1]/3+umesh[inter1,wallx+1]/3+umesh[inter1+1,wallx]/3

    umesh[midup:middown, wallx] = 69.0
    umesh[midup:middown, wallx - 1] = umesh[midup:middown, wallx - 2]
    umesh[midup:middown, wallx + 1] = umesh[midup:middown, wallx + 2]
    umesh[midup-1, wallx] = umesh[midup-1, wallx - 1] / 3 + umesh[midup-1, wallx + 1] / 3 + umesh[midup-2, wallx] / 3
    umesh[middown, wallx] = umesh[middown, wallx - 1] / 3 + umesh[middown, wallx + 1] / 3 + umesh[middown+1, wallx] / 3


    umesh[inter2:-1,wallx]=69
    umesh[-1, wallx] = 69
    umesh[inter2:-1,wallx-1]=umesh[inter2:-1,wallx-2]
    umesh[-1, wallx - 1] = umesh[-1, wallx - 2]
    umesh[inter2:-1, wallx + 1] = umesh[inter2:-1, wallx + 2]
    umesh[-1, wallx + 1] = umesh[-1, wallx + 2]
    umesh[inter2, wallx] = umesh[inter2,wallx-1]/3+umesh[inter2,wallx+1]/3+umesh[inter2-1,wallx]/3


    key = pg.key.get_pressed()
    if autoadjust or key[pg.K_SPACE]:
        colorrange=np.max(umesh)-np.min(umesh)
        floor=np.min(umesh)
        print(colorrange,floor)

    for i in range(len(x)):
        for j in range(len(y)):
            pg.draw.rect(screen,color(umesh[j,i]-floor,colorrange),[xview(xmesh[j,i]),yview(ymesh[j,i]),ceil(100*dx),ceil(100*dy)])
            if umesh[j,i]== 69.0:
                pg.draw.rect(screen,(0,0,0),[xview(xmesh[j,i]),yview(ymesh[j,i]),ceil(100*dx),ceil(100*dy)])
    #if t%0.5==0:
        #print(np.min(umesh),np.max(umesh))


pg.quit()