import pygame
import threading
import time

BLACK = (0,0,0)
WHITE = (255,255,255)
WIDTH = 800
HEIGHT = 600

def setText(text, antialias, color):
    font = pygame.font.Font("resources/font/m5x7.ttf", 14)
    return font.render(text, antialias, color, WHITE)

def drawGrid(master, screen):
        for x in range(0, WIDTH, master.cuadsize):
            for y in range(0, HEIGHT, master.cuadsize):
                rect = pygame.Rect(x, y, master.cuadsize, master.cuadsize)
                pygame.draw.rect(screen, BLACK, rect, 1)

def threadScreen(master,userlock,poilock,timelock,masterlock):

    labelList = []
    iconList = []
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption('Sim screen')
    screenSwitch = True
    while screenSwitch:
        userlock.acquire()
        try:
            userList = master.user_list.copy()
        finally:
            userlock.release()

        poilock.acquire()
        try:
            poiList = master.poi_list.copy()
        finally:
            poilock.release()
        pygame.event.get()
        screen.fill((255, 255, 255))
        drawGrid(master, screen)
        for i in userList:
            labelList.append(setText("Usuario "+str(i.id),True,(0,0,0)))
            screen.blit(labelList[-1], (i.xpos - (labelList[-1].get_height()/2),20 + i.ypos + labelList[-1].get_height()))
            iconList.append(pygame.image.load('navigation/ico/user.png'))
            iconList[-1] = pygame.transform.scale(iconList[-1], (33, 33))
            screen.blit(iconList[-1], (i.xpos, i.ypos))


        pygame.display.flip()
        labelList.clear()
        iconList.clear()

