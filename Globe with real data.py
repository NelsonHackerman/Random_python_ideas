import pygame as pg
from numpy import *
import os
# types of projections
# mercator, equirectangular, robinson, dymaxion, azimuthal equidistant, orthographic, perspective
compression = 15

# extract file data - this was mostly trial and error and ignored some of the points to make it manageable to my cpu.
filename = "geodata.txt"
if os.path.exists(filename):
        with open(filename, "r") as f:
            full_array = []
            for line in f.readlines():
                full_array.append(line.strip().split(";"))
worldmap = [] # list of nx2 arrays containing coordinates as floats
for i in range(len(full_array)-1):
    allpoints = full_array[i+1][1].replace('"{""coordinates"": ','').replace(']]]], ""type"": ""MultiPolygon""}"','') # raw string containing points
    islands = allpoints.split("]]], [[[") # list of strings where each string is a separate island

    for k in range(len(islands)):
        allpoints2 = islands[k].split("], [")  # list of strings where each string is coordinate doublet
        allpointsx = []  # list of strings of 1st coordinates, ready to be converted into float
        allpointsy = []  # list of strings of 1st coordinates, ready to be converted into float
        for j in range(len(allpoints2)):
            allpointsx.append(allpoints2[j].split(",")[0].replace('[', ''))
            allpointsy.append(allpoints2[j].split(",")[1].replace(']', ''))
        if compression>1:
            if len(allpoints2)>compression*2 and i!=145 and i!=31 and i!=70 and i!=117 and i!=77 and i!=176 and i!=255 and i!=236 and i!=71 and i!=50 and i!=43 and i!=158 and i!=156:
                worldmap.append(array([allpointsx[::compression],allpointsy[::compression]],dtype=float).T*pi/180)
            elif i == 145 or i == 31 or i == 70 or i == 117 or i == 77 or i == 176 or i == 255 or i == 236 or i == 71 or i == 50 and len(allpoints2)>compression*2:
                worldmap.append(array([allpointsx[::2], allpointsy[::2]], dtype=float).T * pi / 180)
            elif (i == 43 or i == 156) and len(allpoints2)>compression*10 and k != 208:
                worldmap.append(array([allpointsx[::compression*3], allpointsy[::compression*3]], dtype=float).T * pi / 180)
            elif k == 208:
                worldmap.append(array([allpointsx[::compression], allpointsy[::compression]], dtype=float).T * pi / 180)
            elif i == 158 and len(allpoints2)>compression*10:
                worldmap.append(array([allpointsx[::compression * 10], allpointsy[::compression * 10]], dtype=float).T * pi / 180)
        elif compression == 1:
            worldmap.append(array([allpointsx, allpointsy], dtype=float).T * pi / 180)



        #if i == 211:
            #worldmap.append(array([allpointsx, allpointsy], dtype=float).T * pi / 180)


print(len(worldmap))
white = (255,255,255)
black = (0,0,0)
pg.init()
run=True
clock=pg.time.Clock()
screen=pg.display.set_mode((1400,800))
t=0.0

# antarctica wasn't included in the dataset so I made it myself using bezier curves
antarcticabezier = [array([[-3.14479638, -1.37104072],
       [-3.03167421, -1.39366516],
       [-2.91855204, -1.37556561],
       [-2.83710407, -1.3800905 ],
       [-2.79638009, -1.39366516],
       [-2.77375566, -1.37104072],
       [-2.75565611, -1.34841629],
       [-2.72096531, -1.34992459],
       [-2.68627451, -1.35143288],
       [-2.65158371, -1.35294118],
       [-2.67873303, -1.30769231],
       [-2.35746606, -1.32126697],
       [-2.24434389, -1.32126697],
       [-2.23529412, -1.26696833],
       [-1.98190045, -1.31221719],
       [-1.81900452, -1.31221719],
       [-1.82352941, -1.20361991],
       [-1.52488688, -1.30316742],
       [-1.41628959, -1.30316742],
       [-1.36199095, -1.25791855],
       [-1.3107089 , -1.29713424],
       [-1.25791855, -1.29411765],
       [-1.35746606, -1.2760181 ],
       [-1.3438914 , -1.19909502],
       [-1.19909502, -1.22624434],
       [-1.14479638, -1.14479638],
       [-1.06334842, -1.11764706],
       [-0.98642534, -1.11764706],
       [-1.01809955, -1.14027149],
       [-1.04524887, -1.14027149],
       [-1.07692308, -1.16742081],
       [-1.0361991 , -1.19909502],
       [-1.04524887, -1.29411765],
       [-1.0678733 , -1.32579186],
       [-0.81447964, -1.3800905 ],
       [-0.66063348, -1.38914027],
       [-0.5520362 , -1.34841629],
       [-0.52639517, -1.34992459],
       [-0.50075415, -1.35143288],
       [-0.47511312, -1.35294118],
       [-0.46606335, -1.30769231],
       [-0.41628959, -1.28054299],
       [-0.37556561, -1.31221719],
       [-0.29411765, -1.26244344],
       [-0.11764706, -1.23076923],
       [-0.02714932, -1.24434389],
       [-0.00904977, -1.2081448 ],
       [ 0.05882353, -1.24434389],
       [ 0.10859729, -1.24434389],
       [ 0.23076923, -1.21719457],
       [ 0.32579186, -1.22624434],
       [ 0.42533937, -1.239819  ],
       [ 0.5520362 , -1.22171946],
       [ 0.64705882, -1.19457014],
       [ 0.69683258, -1.23529412],
       [ 0.69230769, -1.19004525],
       [ 0.85972851, -1.19909502],
       [ 0.93665158, -1.15837104],
       [ 1.        , -1.17647059],
       [ 1.2081448 , -1.19457014],
       [ 1.33484163, -1.22624434],
       [ 1.37556561, -1.2081448 ],
       [ 1.40271493, -1.19457014],
       [ 1.44343891, -1.19909502],
       [ 1.35294118, -1.14479638],
       [ 1.59276018, -1.19004525],
       [ 1.67420814, -1.18099548],
       [ 1.6561086 , -1.12669683],
       [ 1.71493213, -1.12217195],
       [ 1.75565611, -1.16289593],
       [ 1.8280543 , -1.13122172],
       [ 1.85067873, -1.1719457 ],
       [ 1.90497738, -1.17647059],
       [ 1.97737557, -1.15384615],
       [ 2.0361991 , -1.14027149],
       [ 2.05429864, -1.18552036],
       [ 2.08144796, -1.18401207],
       [ 2.10859729, -1.18250377],
       [ 2.13574661, -1.18099548],
       [ 2.14479638, -1.13122172],
       [ 2.27149321, -1.18099548],
       [ 2.36651584, -1.1719457 ],
       [ 2.36199095, -1.12669683],
       [ 2.42081448, -1.15384615],
       [ 2.46153846, -1.18099548],
       [ 2.58371041, -1.19457014],
       [ 2.64253394, -1.15837104],
       [ 2.63800905, -1.21266968],
       [ 2.73303167, -1.20361991],
       [ 2.90045249, -1.239819  ],
       [ 2.99547511, -1.26696833],
       [ 2.95475113, -1.30769231],
       [ 2.86877828, -1.31674208],
       [ 2.86877828, -1.3438914 ],
       [2.9,-1.36],
        [2.92,-1.36],
       [ 2.96832579, -1.37104072],
       [ 3.00904977, -1.36199095],
       [ 3.08597285, -1.37556561],
       [ 3.15384615, -1.37104072]])]


def essentials():
    pg.display.update()
    clock.tick(60)
    screen.fill((0,0,0)) #42,63,121 for dark blue background
    global key
    key=pg.key.get_pressed()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            global run
            run=False

# converts list of control points to list of thousands of straight lines
def bezier(pointlist):
    point = pointlist
    bezierchar = array([[1, 0, 0, 0], [-3, 3, 0, 0], [3, -6, 3, 0], [-1, 3, -3, 1]])
    lines = len(point)
    linelist = []
    for j in range(lines):
        num = point[j].shape[0]
        if (num-1)%3 == 0:
            k=0
            beziernum = int((num-1)/3)
            poslist = zeros((beziernum*10,2))
            for T in linspace(0,beziernum-0.001,beziernum*10):
                t = T%1
                line = int(floor(T))
                cubic = array([1,t,t**2,t**3])
                x = cubic@bezierchar@point[j][3*line:3*line+4,0]
                y = cubic@bezierchar@point[j][3*line:3*line+4,1]
                poslist[k,:]=array([x,y])
                k+=1
            linelist.append(poslist)
        else:
            print("wrong amount of points")

    return linelist

# converts conventional axes to pygame axes
def show(linelist,x = 0, y =0):
       screenlines = []
       inverty = array([[1, 0], [0, -1]])
       for j in range(len(linelist)):
              screenlines.append((linelist[j] + array([700+x, -400+y])) @ inverty)
       return screenlines

# converts list of straight lines into a equirectangular projection
def equirectangular(linelist,R=221):
       equirec=[]
       for j in range(len(linelist)):
              equirec.append(R*linelist[j])
       screenlines = show(equirec)
       return screenlines

# converts list of straight lines into a mercator projection
def mercator(linelist,R=147):
       mercator = []
       for j in range(len(linelist)):
              long = linelist[j][:,0]
              lat = linelist[j][:,1]
              x = R*long
              y = R*log(tan(pi/4+lat/2))

              mercator.append(array([x,y]).T)
       screenlines = show(mercator,0,-40)
       return screenlines

# converts list of straight lines into a robinson projection
def robinson(linelist,R = 250):
       rob = []
       for j in range(len(linelist)):
              long = linelist[j][:, 0]
              lat = linelist[j][:, 1]
              x = 0.8487*R * (long)*(1+0.03189*lat-0.2116*lat**2)
              y = 1.3523*R *(0.7179*lat-0.01334*lat**5)

              rob.append(array([x, y]).T)
       screenlines = show(rob)
       return screenlines

# converts list of straight lines into an azimuthal equidistant projection
def azimequi(linelist,R=130):
       azim = []
       for j in range(len(linelist)):
              long = linelist[j][:, 0]
              lat = linelist[j][:, 1]
              rho = R*(pi/2-lat)
              x = rho*sin(long)
              y = -rho*cos(long)

              azim.append(array([x, y]).T)
       screenlines = show(azim)
       return screenlines

# converts list of straight lines into a 3D orthographic projection
def orthographic(linelist,long0=0.0,lat0=0.0,R=350):
       ortho = []
       depth = []
       linesanddepth = []
       for j in range(len(linelist)):
              long = linelist[j][:, 0]
              lat = linelist[j][:, 1]
              x = R*cos(lat)*sin(long-long0)
              y = R*(cos(lat0)*sin(lat)-sin(lat0)*cos(lat)*cos(long-long0))
              z = sin(lat0)*sin(lat)+cos(lat0)*cos(lat)*cos(long-long0)
              ortho.append(array([x, y]).T)
              depth.append(array(array([z]).T))
       screenlines = show(ortho)
       for j in range(len(linelist)):
              linesanddepth.append(hstack((screenlines[j],depth[j])))
       return linesanddepth

antarctica = bezier(antarcticabezier)

worldmap.append(antarctica[0])

projection = azimequi(worldmap)

for i in range(len(projection)):
    if projection[i].shape[0]<3:
        print(projection[i].shape)

#worldmap = bezier(worldbezier)
size = 350 # default is 350

type ="3d" # choose whether you want 3d or 2d projection
while run:
       essentials()
       t+=1/60

       # choose one of these projections below to depict
       #projection = orthographic(worldmap, -pi*2*t/86400*3600, 0) # 1 sec = 1 hour
       projection = orthographic(worldmap, 0.8*t, 0.41*sin(0.05*t)) # seasons
       #projection = orthographic(worldmap, 4*pi/180, 50*pi/180,size)



       if type == "2d":
            projection = mercator(worldmap)
            for j in range(len(projection)):
                #pg.draw.polygon(screen, (76,105,79), projection[j])
                if j == len(projection)-1:
                    pg.draw.lines(screen, white, False, projection[j], 3)

                else:
                    pg.draw.lines(screen, white, True, projection[j], 2)
       elif type == "3d":
           pg.draw.circle(screen, white, (700, 400), size+2, 2)
           for j in range(len(projection)):
               for i in range(projection[j].shape[0] - 1):
                   if projection[j][i, 2] > 0:
                       pg.draw.line(screen, white, projection[j][i, 0:2], projection[j][i + 1, 0:2], 2)
               if projection[j][0,2] and projection[j][-1,2]>0:
                   pg.draw.line(screen, white, projection[j][-1, 0:2], projection[j][0, 0:2], 2)


pg.quit()