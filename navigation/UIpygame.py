import pygame
from constants import constants as const



# The following document describes return graphics routines for easy abstraction of simulation data. Every routine stated
# here is SEVERED from the simulation triggered events or the user I/O interface. If you would ever want to change how
# the simulation handle this output graphics. you can just replace this safely by printing graphic data stored on the main
# data structure 'master' stored on 'objects.py' on 'objects' package and be safe that you won't break any simulation
# functionality whatsoever.

class UIpygame:
    def __init__(self,master,userlock,poilock,timelock,querylock,masterlock):
        # Defining most used constants.


        self.master = master
        self.userlock = userlock
        self.poilock = poilock
        self.timelock = timelock
        self.querylock = querylock
        self.masterlock = masterlock
        self.labelList = []
        self.iconList = []

        print("Sim graphics interface instance created.")





    def setText(self, text, antialias, color):
        """ Function to generate a font resource to draw into and return a drawable object to render directly on the screen.
            Parameters: (String to print, Antialias boolean flag, RGB Color of the text)"""
        font = pygame.font.Font("resources/font/m5x7.ttf", 14)
        return font.render(text, antialias, color, const.WHITE)






    def drawGrid(self):
            """Function used to draw quadrants delimiting rects on a PyGame screen described on the parameters
             # Parameters: ('Master' structure, PyGame screen)"""
            for x in range(0, const.WIDTH, self.master.quadsize):
                for y in range(0, const.HEIGHT, self.master.quadsize):
                    rect = pygame.Rect(x, y, self.master.quadsize, self.master.quadsize)
                    pygame.draw.rect(self.screen, const.BLACK, rect, 1)
            for quad in self.master.quadrant_list:
                self.labelList.append(self.setText(str(quad.id), True, (128, 128, 128)))
                self.screen.blit(self.labelList[-1], (quad.startingPoint[0]+ 2, quad.startingPoint[1]+1))




    def terminate(self):
        """ Function used to 'turn off' pygame loop boolean. Ending the loop and, thus, the thread.
            Parameters: ('Master' structure, Master Lock)"""
        self.masterlock.acquire()
        try:
            self.master.config.screenSwitch = False
        finally:
            self.masterlock.release()





    def drawUsers(self,userList):
        """ Called from 'threadScreen' function of ATLAS thread (See main.py) this function cycles through all users on 'master'
        structure and draws them on a pygame screen described on parameters.
        Parameters: ('')"""
        for element in userList:
            self.labelList.append(self.setText("User " + str(element.id), True, (0, 0, 0)))
            self.screen.blit(self.labelList[-1],
                        ((element.xpos + 16) - (self.labelList[-1].get_width() // 2), 20 + element.ypos + self.labelList[-1].get_height()))
            self.iconList.append(pygame.image.load('resources/ico/user.png'))
            self.iconList[-1] = pygame.transform.scale(self.iconList[-1], (9, 9))
            self.screen.blit(self.iconList[-1], (element.xpos, element.ypos))





    def drawPOIs(self,poiList):
        for element in poiList:
            self.labelList.append(self.setText("POI " + str(element.id), True, (0, 0, 0)))
            self.screen.blit(self.labelList[-1], (
                (element.xpos + 16) - (self.labelList[-1].get_width() // 2), 22 + element.ypos + self.labelList[-1].get_height()))
            self.iconList.append(pygame.image.load('resources/ico/cat' + str(element.category) + '.png'))
            self.iconList[-1] = pygame.transform.scale(self.iconList[-1], (33, 33))
            self.screen.blit(self.iconList[-1], (element.xpos, element.ypos))

    def drawQueries(self,queryList):
        for element in queryList:
            rect = pygame.Rect(element[1][0], element[1][1], self.master.quadsize, 0)
            pygame.draw.rect(self.screen, const.BLACK, rect, 1)
            rect = pygame.Rect(element[1][0] + self.master.quadsize, element[1][1], 0, self.master.quadsize)
            pygame.draw.rect(self.screen, const.BLACK, rect, 1)
            rect = pygame.Rect(element[1][0], element[1][1] + self.master.quadsize, self.master.quadsize, 0)
            pygame.draw.rect(self.screen, const.BLACK, rect, 1)
            rect = pygame.Rect(element[1][0], element[1][1], 0, self.master.quadsize)
            pygame.draw.rect(self.screen, const.BLACK, rect, 1)




    ## Function called from ATLAS thread.
    def threadScreen(self):
        """" threadScreen() procedure is called from the 'ATLAS' thread described on 'main.py' document on root directory.
        This function is invoked to constantly draw simulation geographical data stored on the master data structure on a newly generated pygame window.
        Parameters: (Master 'structure', User List Lock, POI List Lock, Master Lock)"""
        pygame.init()
        self.screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
        pygame.display.set_caption('Sim screen')
        print("Starting PyGame...")

        while True:


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()


            self.masterlock.acquire()
            try:
                if not self.master.config.screenSwitch:
                    pygame.quit()
                    return False
            finally:
                self.masterlock.release()



            self.userlock.acquire()
            try:
                userList = self.master.user_list.copy()
            finally:
                self.userlock.release()



            self.poilock.acquire()
            try:
                poiList = self.master.poi_list.copy()
            finally:
                self.poilock.release()

            self.querylock.acquire()
            try:
                queryList = self.master.querydraw_list.copy()
            finally:
                self.querylock.release()

            self.screen.fill(const.WHITE)



            if (self.master.config.showGrid):
                self.drawGrid()

            self.drawPOIs(poiList)
            self.drawUsers(userList)
            self.drawQueries(queryList)


            pygame.display.flip()
            self.labelList.clear()
            self.iconList.clear()

