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

def killTheLights(master,masterlock):
    masterlock.acquire()
    try:
        master.config.screenSwitch = False
    finally:
        masterlock.release()

def threadScreen(master,userlock,poilock,timelock,masterlock):

    labelList = []
    iconList = []
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Sim screen')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                killTheLights(master,masterlock)
        masterlock.acquire()
        try:
            if not master.config.screenSwitch:
                pygame.quit()
                return False
        finally:
            masterlock.release()
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
        screen.fill((255, 255, 255))

        if (master.config.showGrid):
            drawGrid(master, screen)

        for element in userList:
            labelList.append(setText("Usuario "+str(element.id),True,(0,0,0)))
            screen.blit(labelList[-1], (element.xpos - (labelList[-1].get_width() // 2),20 + element.ypos + labelList[-1].get_height()))
            iconList.append(pygame.image.load('resources/ico/user.png'))
            iconList[-1] = pygame.transform.scale(iconList[-1], (33, 33))
            screen.blit(iconList[-1], (element.xpos, element.ypos))

        for element in poiList:
            labelList.append(setText("POI "+str(element.id),True,(0,0,0)))
            screen.blit(labelList[-1], (element.xpos + 15 - (labelList[-1].get_width() // 2), 22 + element.ypos + labelList[-1].get_height()))
            iconList.append(pygame.image.load('resources/ico/cat'+str(element.category)+'.png'))
            iconList[-1] = pygame.transform.scale(iconList[-1], (33,33))
            screen.blit(iconList[-1], (element.xpos, element.ypos))


        pygame.display.flip()
        labelList.clear()
        iconList.clear()

