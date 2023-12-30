import pygame as pg
import numpy as np
import random
from itertools import permutations
pg.init()
run=True

clock=pg.time.Clock()
screen=pg.display.set_mode((1800,1000))

xview = 10
yview = -4.5
scale = 86

red = (255,0,0)
yellow = (255,255,0)
green = (0,255,0)
blue = (0,0,255)
lightblue = (0,100,200)
black = (0,0,0)
white = (255,255,255)

# toggle variables
mousepressed = False
spacepressed = False
inputmode = True
leftpressed,rightpressed,uppressed,downpressed = False, False, False, False
fpressed = False

# essentials for running pygame
def essentials():
    pg.display.update()
    clock.tick(60)
    screen.fill(black)
    global key
    key=pg.key.get_pressed()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            global run
            run=False

# write text on the pygame screen
def write(string, coordx, coordy, fontSize, color):
    # set the font to write with
    font = pg.font.SysFont('freesansbold', fontSize)
    # (0, 0, 0) is black, to make black text
    text = font.render(string, True, color)
    # get the rect of the text
    textRect = text.get_rect()
    # set the position of the text
    textRect.center = (coordx, coordy)
    # add text to window
    screen.blit(text, textRect)
    

# transforms custom x coordinate to pygame x coordinate   
def xshow(x):
    x2=900+(x - xview) * scale
    return x2

# transforms custom x coordinate to pygame x coordinate 
def yshow(y):
    y2 =500+(-y - yview) * scale
    return y2

# gives all possible places a single block can be placed on a grid
def possible(board,block):
    pos = []
    megaboard = np.ones((16,16))
    megaboard[4:12,4:12]=board
    for i in range(12):
        for j in range(12):
            newboard = megaboard.copy()
            newboard[i:i+5,j:j+5]+=block
            if np.sum(newboard==2)==0:
                pos.append(newboard[4:12,4:12])
    return pos

#delete full rows and columns
def execute(board):
    newboard = board.copy()
    for i in range(8):
        if np.sum(board[0:8,i])==8:
            newboard[0:8,i]*=0
        if np.sum(board[i,0:8])==8:
            newboard[i,0:8]*=0
    return newboard

# gives a number to how smooth a certain placement of blocks are in a grid 
#(decreases as the circumference of the filled slots increase)
def smoothness(board):
    smoothness = 112
    for i in range(8):
        for j in range(8):
            entry = board[i,j]
            if i != 7 and j != 7:
                if board[i+1,j] !=entry:
                    smoothness -=1
                if board[i,j+1] !=entry:
                    smoothness -=1
            if i!=7 and j==7:
                if board[i+1,j] !=entry:
                    smoothness -=1
            if i==7 and j!=7:
                if board[i,j+1] !=entry:
                    smoothness -=1
    return smoothness
                
                        


# returns a fitness score for each solution            
def evaluate(solutions):
    fitness = []
    empty_weight = 20
    smooth_weight = 1
    startfitness = empty_weight*(64-np.sum(solutions[0][0]))+smooth_weight*smoothness(solutions[0][0])
    for sol in solutions:
        endfitness = empty_weight*(64-np.sum(sol[6]))+smooth_weight*smoothness(sol[6])
        fitness.append(endfitness - startfitness)
    return fitness          

#outputs list of n_solutions 
# each entry of the list is n_steps 
# each entry of that list is 8 x 8 matrix, representing the board
def solution(board,b1,b2,b3):
    solutions = []
    save0 = execute(board)
    for bl1,bl2,bl3 in permutations([b1,b2,b3]):
        pos1 = possible(save0,bl1)
        if len(pos1)>0:
            for i in pos1:
                save1 = i.copy()
                save2 = execute(save1)
                pos2 = possible(save2,bl2)
                if len(pos2)>0:
                    for j in pos2:
                        save3 = j.copy()
                        save4 = execute(save3)
                        pos3 = possible(save4,bl3)
                        if len(pos3)>0:
                            for k in pos3:
                                save5 = k.copy()
                                save6 = execute(save5)
                                solutions.append([save0,save1,save2,save3,save4,save5,save6])
                                if len(solutions)>49999:
                                    break
                            else:
                                continue
                            break
                    else:
                        continue
                    break
            else:
                continue
            break
    if len(solutions)>0:
        fitness = evaluate(solutions)
        zippedsort = sorted(zip(solutions, fitness), key=lambda x: x[1], reverse=True)
        sorted_solutions = [sol for sol, fit in zippedsort]
        sorted_fitness = [fit for sol, fit in zippedsort]
    else:
        return [],[]
    
    return sorted_solutions, sorted_fitness



gameboard = [[],[],[],[],[],[],[],[]] # constains the pygame Rectangle objects
boardstate = np.zeros((8,8)) # represents the state of the 8x8 board
block1 = [[],[],[],[],[]]
block1state = np.zeros((5,5))
block2 = [[],[],[],[],[]]
block2state = np.zeros((5,5))
block3 = [[],[],[],[],[]]
block3state = np.zeros((5,5))
solnum = 0
stepnum = 0 

while run:
    essentials()
    mouse_x, mouse_y = pg.mouse.get_pos()
    mouse_rect = pg.Rect(mouse_x, mouse_y, 1, 1)
    mouse,middle,right = pg.mouse.get_pressed()
    key = pg.key.get_pressed()
    
    squaresize = 82
    write("Block Blast Solver",380,100,80,white)
    # input mode
    if inputmode:
        
        write("Fill in your blocks and press space",1550,600,40,white)
        write("Press F to toggle fill/empty",1550,650,40,white)
        # making the square objects
        for i in range(8):
            for j in range(1,9):
                gameboard[i].append(pg.Rect(xshow(i),yshow(j),squaresize,squaresize))
        for i in range(9,14):
            for j in range(6,11):
                block1[i-9].append(pg.Rect(xshow(i),yshow(j),squaresize,squaresize))
        for i in range(15,20):
            for j in range(6,11):
                block2[i-15].append(pg.Rect(xshow(i),yshow(j),squaresize,squaresize))
        for i in range(9,14):
            for j in range(0,5):
                block3[i-9].append(pg.Rect(xshow(i),yshow(j),squaresize,squaresize))
                
        # drawing and logic for gameboard
        for i in range(8):
            for j in range(8):
                if mouse and not mousepressed and mouse_rect.colliderect(gameboard[i][j]):
                    boardstate[i,j] = 1- boardstate[i,j]
                if boardstate[i,j]==0:
                    if mouse_rect.colliderect(gameboard[i][j]):
                        pg.draw.rect(screen, yellow,gameboard[i][j])
                    else:
                        pg.draw.rect(screen, lightblue,gameboard[i][j])
                else:
                    pg.draw.rect(screen, red,gameboard[i][j])
        
        # drawing and logic for blockboards
        for i in range(5):
            for j in range(5):
                if mouse and not mousepressed and mouse_rect.colliderect(block1[i][j]):
                    block1state[i,j] = 1- block1state[i,j]
                if block1state[i,j]==0:
                    if mouse_rect.colliderect(block1[i][j]):
                        pg.draw.rect(screen, yellow,block1[i][j])
                    else:
                        pg.draw.rect(screen, green,block1[i][j])
                else:
                    pg.draw.rect(screen, red,block1[i][j])
                
                
                if mouse and not mousepressed and mouse_rect.colliderect(block2[i][j]):
                    block2state[i,j] = 1- block2state[i,j]
                if block2state[i,j]==0:
                    if mouse_rect.colliderect(block2[i][j]):
                        pg.draw.rect(screen, yellow,block2[i][j])
                    else:
                        pg.draw.rect(screen, green,block2[i][j])
                else:
                    pg.draw.rect(screen, red,block2[i][j])
                    
                if mouse and not mousepressed and mouse_rect.colliderect(block3[i][j]):
                    block3state[i,j] = 1- block3state[i,j]
                if block3state[i,j]==0:
                    if mouse_rect.colliderect(block3[i][j]):
                        pg.draw.rect(screen, yellow,block3[i][j])
                    else:
                        pg.draw.rect(screen, green,block3[i][j])
                else:
                    pg.draw.rect(screen, red,block3[i][j])
        
        if key[pg.K_f] and not fpressed:
            if np.sum(boardstate)==0:
                boardstate +=1
            elif np.sum(boardstate)==64:
                boardstate -=1
            else:
                boardstate = boardstate*0+1
        
        if key[pg.K_SPACE] and not spacepressed:
            inputmode = False
            sols,fitness = solution(boardstate,block1state,block2state,block3state)
            nsols = len(sols)
    
    #solution mode
    else:
        if nsols==0:
            write("No solutions found",900,500,150,white)
        else:
            boardstate = sols[solnum][stepnum]
            write("Solution "+str(solnum+1) +"/"+str(nsols),1500,550,80,white)
            write("Fitness: "+str(int(fitness[solnum])),1500,600,40,white)
            write("Step "+str(stepnum) +"/6",1500,700,80,white)
            write( "Scroll through solutions using up/down",1500,800,35,white)
            write("Scroll through steps using left/right",1500,850,35,white)
            write("Press space to retry",1500,900,35,white)
            
            if key[pg.K_LEFT] and not leftpressed and stepnum>0:
                stepnum-=1
            if key[pg.K_RIGHT] and not rightpressed and stepnum<6:
                stepnum +=1
            if key[pg.K_UP] and not uppressed and solnum>0:
                solnum-=1
                stepnum=0
            if key[pg.K_DOWN] and not downpressed and solnum<nsols-1:
                solnum +=1
                stepnum =0
        
            # making the square objects
            for i in range(8):
                for j in range(1,9):
                    gameboard[i].append(pg.Rect(xshow(i),yshow(j),squaresize,squaresize))
            for i in range(9,14):
                for j in range(6,11):
                    block1[i-9].append(pg.Rect(xshow(i),yshow(j),squaresize,squaresize))
            for i in range(15,20):
                for j in range(6,11):
                    block2[i-15].append(pg.Rect(xshow(i),yshow(j),squaresize,squaresize))
            for i in range(9,14):
                for j in range(0,5):
                    block3[i-9].append(pg.Rect(xshow(i),yshow(j),squaresize,squaresize))
                    
            # drawing and logic for gameboard
            for i in range(8):
                for j in range(8):
                    if boardstate[i,j]==0:
                        pg.draw.rect(screen, lightblue,gameboard[i][j])
                    else:
                        pg.draw.rect(screen, red,gameboard[i][j])
            
            # drawing and logic for blockboards
            for i in range(5):
                for j in range(5):
                    if block1state[i,j]==0:
                        pg.draw.rect(screen, green,block1[i][j])
                    else:
                        pg.draw.rect(screen, red,block1[i][j])
                    
                    if block2state[i,j]==0:
                        pg.draw.rect(screen, green,block2[i][j])
                    else:
                        pg.draw.rect(screen, red,block2[i][j])
                    
                    if block3state[i,j]==0:
                        pg.draw.rect(screen, green,block3[i][j])
                    else:
                        pg.draw.rect(screen, red,block3[i][j])
                    
        if key[pg.K_SPACE] and not spacepressed:
            inputmode = True
            block1state*=0
            block2state*=0
            block3state*=0
            solnum = 0
            stepnum = 0
            
    
    
    #toggle keys
    if mouse:
         mousepressed = True
    else:
        mousepressed = False
        
    if key[pg.K_SPACE]:
        spacepressed = True
    else:
        spacepressed = False
    
    if key[pg.K_LEFT]:
        leftpressed = True
    else:
        leftpressed = False
        
    if key[pg.K_RIGHT]:
        rightpressed = True
    else:
        rightpressed = False
        
    if key[pg.K_UP]:
        uppressed = True
    else:
        uppressed = False
        
    if key[pg.K_DOWN]:
        downpressed = True
    else:
        downpressed = False
    if key[pg.K_f]:
        fpressed = True
    else:
        fpressed = False
    
    
pg.quit()
