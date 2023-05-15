import pygame as pg
import random
import numpy as np
pg.init()
run=True
clock=pg.time.Clock()
screen=pg.display.set_mode((1400,800))
def essentials():
    pg.display.update()
    clock.tick(30)
    screen.fill((255,255,255))
    global key
    key=pg.key.get_pressed()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            global run
            run=False

size = 30
# lines consist of start,end,size

def tree(loc,n,lines):
    if n>0:
        dir1 = random.uniform(0,np.pi)
        dir2 = random.uniform(0,np.pi)
        rot1 = np.array([[np.cos(dir1),np.sin(dir1)],[-np.sin(dir1),np.cos(dir1)]])
        rot2 = np.array([[np.cos(dir2),np.sin(dir2)],[-np.sin(dir2),np.cos(dir2)]])
        default = np.array([size*n,0])
        branch1 = rot1@default
        branch2 = rot2@default
        lines.append([loc,loc+branch1,n])
        lines.append([loc,loc+branch2,n])
        tree(loc+branch1,n-1,lines)
        tree(loc+branch2,n-1,lines)
    return lines

def tree2(loc,n,lines,prev):
    if n>0:
        dir1 = random.uniform(-np.pi/5,-0.1)
        dir2 = random.uniform(0.1,np.pi/5)
        rot1 = np.array([[np.cos(dir1),np.sin(dir1)],[-np.sin(dir1),np.cos(dir1)]])
        rot2 = np.array([[np.cos(dir2),np.sin(dir2)],[-np.sin(dir2),np.cos(dir2)]])
        default = (loc-prev)*n/(n+1)
        branch1 = rot1@default
        branch2 = rot2@default
        lines.append([loc,loc+branch1,n])
        lines.append([loc,loc+branch2,n])
        tree2(loc+branch1,n-1,lines,loc)
        tree2(loc+branch2,n-1,lines,loc)
    return lines

depth = 11
start = np.array([700,720])
start2= np.array([700,620])
t=0
lines = []
while run:
    essentials()
    t+=1
    if t%120==10:
        #lines = []
        #lines = tree(start,7,lines)
        lines = [[start, start2, depth]]
        lines = tree2(start2, depth, lines, start)
    for i in lines:
        pg.draw.line(screen,(0,0,0),i[0],i[1],i[2])

pg.quit()

