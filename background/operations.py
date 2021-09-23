from objects import objects
import math
import random
class operations:

    def __init__(self,master,userlock,poilock,timelock,querylock,masterlock):
        # Defining most used constants.


        self.master = master
        self.userlock = userlock
        self.poilock = poilock
        self.timelock = timelock
        self.querylock = querylock
        self.masterlock = masterlock
        print("Operations instance created.")

    def powerSwitch(self,powerflag):
        """ Turns the 'power' boolean flag to parameter value. 'power' boolean flag is an attribute of the 'config' child of
        'master' data structure. 'Power' boolean flag is specifically used as a stop-and-go signal on time tracking and time-triggered events.
        parameters: (Master structure, Master lock, New value of 'power')"""
        self.masterlock.acquire()
        try:
            self.master.config.power = powerflag
            print("Turning simulation power to: "+str(self.master.config.power))
        finally:
            self.masterlock.release()


    def printLog(self):
        """ Prints on console all tasks stored on the 'log' attribute of 'master' structure.
        parameters: (Master structure, Master lock)"""
        self.masterlock.acquire()
        try:
            #TODO use fileHandler object to print master log
            print(str(self.master.log))
        finally:
            self.masterlock.release()


    def getUserList(self):
        """ Returns an exact copy of the user list stored on 'master' structure on actual time.
        parameters: (Master structure, User lock)"""
        self.userlock.acquire()
        try:
            returnlist = self.master.user_list.copy()
        finally:
            self.userlock.release()
            return returnlist

    def getPoiList(self):
        """ Returns an exact copy of the Point of interest list stored on 'master' structure on actual time.
        parameters: (Master structure, POI lock)"""
        self.poilock.acquire()
        try:
            returnlist = self.master.poi_list.copy()
        finally:
            self.poilock.release()
            return returnlist

    def addUser(self, id, xpos, ypos, cache, speed):
        """ Inserts into 'master' structure's list of users a newly created user using data extracted from parameters.
        parameters: (User unique id, X position on canvas, Y position on canvas, Currently stored cache, Movement speed, 'Master' structure, User lock"""
        newuser = objects.User(int(id.get()), int(xpos.get()), int(ypos.get()), cache, speed, self.master)
        self.userlock.acquire()
        try:

            self.master.addUser(newuser)
        finally:
            self.userlock.release()

    def randomUser(self):
        idlist = list()
        for element in self.master.user_list:
            idlist.append(element.id)
        id = 1
        while id in idlist:
            id = id + 1
        x = random.randint(10,self.master.canvas[0]-10)
        y = random.randint(10,self.master.canvas[1]-10)
        newuser = objects.User(id,x,y,[],1,self.master)
        self.userlock.acquire()
        try:
            self.master.addUser(newuser)
        finally:
            self.userlock.release()


    def addPoi(self, id, xpos, ypos, category):
        """ Inserts into 'master' structure's list of POIs a newly created POI using data extracted from parameters.
        parameters: (POI unique id, X position on canvas, Y position on canvas, POI semantic category, 'Master' structure, POI lock)"""
        newpoi = objects.Poi(int(id.get()), int(xpos.get()), int(ypos.get()), category)
        self.poilock.acquire()
        try:
            self.master.poi_list.append(newpoi)
        finally:
            self.poilock.release()

    def suggestedPois(self):
        if len(self.master.poi_list)>0:
            print("Can't generate suggested POIs as there are already existent POIs on master structure.")
            return False
        for quadrant in self.master.quadrant_list:
            existingCategories = []
            suggestedCategories = []
            while len(suggestedCategories) < 3:
                if quadrant.poi_list:
                    for poi in quadrant.poi_list:
                        if poi.category not in existingCategories:
                            existingCategories.append(poi.category)
                category = random.randint(0, 4)
                while category in existingCategories:
                    category = random.randint(0, 4)
                suggestedCategories.append(category)
            for category in suggestedCategories:
                self.randomPoi(quadrant,category)


    def randomPoi(self,quadrant,category):
        idlist = list()
        for poi in self.master.poi_list:
            idlist.append(poi.id)
        id = 1
        while id in idlist:
            id = id + 1
        x = random.randint(quadrant.startingPoint[0],quadrant.startingPoint[0]+self.master.quadsize-1)
        y = random.randint(quadrant.startingPoint[1],quadrant.startingPoint[1]+self.master.quadsize-1)


        newpoi = objects.Poi(id,x,y,category)
        self.poilock.acquire()
        try:
            self.master.addPoi(newpoi)
        finally:
            self.poilock.release()

    def removeUser(self, id):
        """ Given an id, this function removes an specific User from the 'master' structure's list of users.
        parameters: (User ID, 'master' structure, User lock)"""
        self.userlock.acquire()
        try:
            for element in self.master.user_list:
                if element.id == id:
                    self.master.user_list.remove(element)
        finally:
            self.userlock.release()

    def toggleGrid(self, flag):
        """ This function toggles 'showGrid' boolean flag stored on 'master.config' (see objects.py on objects package)
        structure to True or False depending on 'flag' value extracted from a BooleanVar() generated by tkinter.
        These variables return either 0 or 1 when readed, so it's interpretated by the function before changing the
        'master.config' flag accordingly."""
        if flag == 1:
            toggleflag = True
        elif flag == 0:
            toggleflag = False
        elif flag != 0 and flag != 1:
            print("Wrong grid parameter.")
            return
        self.masterlock.acquire()
        try:
            self.master.config.showGrid = toggleflag
        finally:
            self.masterlock.release()




    #Validations!

    def checkEntryDataType(self, idinput, xinput, yinput):
        """This function checks that every parameter included it's numeric and returns True. If it's not returns False."""
        returnFlag = True
        if not (idinput.get().isnumeric()):
            returnFlag = False
        if not (xinput.get().isnumeric()):
            returnFlag = False
        if not (yinput.get().isnumeric()):
            returnFlag = False
        return returnFlag


    def checkUserUnique(self,idinput):
        """This function checks if given ID doesn't exist within the Users list population. If exists returns false, if it's not, returns true."""
        self.userlock.acquire()
        try:
            returnFlag = True
            for element in self.master.user_list:
                if (int(idinput.get()) == element.id):
                    returnFlag = False
        finally:
            self.userlock.release()
            return returnFlag

    def checkPoiUnique(self, idinput):
        """This function checks if given ID doesn't exist within the POI list population. If exists returns false, if it's not, returns true."""
        self.poilock.acquire()
        try:
            returnFlag = True
            for element in self.master.poi_list:
                if (int(idinput.get()) == element.id):
                    returnFlag = False
        finally:
            self.poilock.release()
            return returnFlag


    def checkBoundariesOnCanvas(self, xinput, yinput):
        """This function gets X and Y input values from parameters and check if they exists within Canvas border stated on 'master' structure."""
        returnFlag = True
        self.masterlock.acquire()
        try:
            canvasx = self.master.canvas[0]
            canvasy = self.master.canvas[1]
        finally:
            self.masterlock.release()
            if not (int(xinput.get()) > 0 and int(xinput.get()) < canvasx):
                returnFlag = False
            if not (int(yinput.get()) > 0 and int(yinput.get()) < canvasy):
                returnFlag = False
            return returnFlag

    def checkCategorySelected(self,category):
        """This function checks if parameter is within possible POI semantic category limit which is now 5"""
        if (category >= 0 and category <= 5):
            return True
        else:
            return False

    