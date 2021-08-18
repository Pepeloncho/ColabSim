import math
import queue
import threading
from anytree import Node, RenderTree
from background import fileHandler


class User:
    def __init__(self, id, xpos, ypos, cache, speed, master):
        self.id = id
        self.xpos = xpos
        self.ypos = ypos
        self.cache = cache
        self.speed = speed
        self.tasklist = []
        self.retainList = []
        self.master = master
        self.master.exploreQuadrant(self)

    def printRetainList(self) -> str:
        returnString = "{"
        for retain in self.retainList:
            returnString = returnString + str(retain.id) + " "
        returnString = returnString + "}"
        return returnString

    def point(self):
        return (self.xpos, self.ypos)

    def gotoxy(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos

    def userDistance(self, user):
        return abs(math.dist(self.point(),user.point()))

    def broadcastUsers(self):
        matchList = []
        radius = math.sqrt(2) * self.master.quadsize
        for user in self.master.user_list:
            if self.userDistance(user) < radius:
                matchList.append(user)

        matchList.remove(self)
        return matchList


class Poi:
    def __init__(self, id, xpos, ypos, category):
        self.id = id
        self.xpos = xpos
        self.ypos = ypos
        self.category = category


class Config:
    def __init__(self):
        self.showGrid = True
        self.screenSwitch = True
        self.running = True
        self.power = False


class Quadrant:
    def __init__(self, id, point):
        self.id = id
        self.startingPoint = point
        self.user_list = []
        self.poi_list = []
        self.quadrantData = []  # Make quadrant data an object
        self.unexplored = True
        self.leader = None


class Query:
    def __init__(self, id, user, time, category, point, quadrants, master):
        self.id = id
        self.user = user
        self.time = time
        self.category = category
        self.point = point
        self.quadrants = quadrants
        self.master = master
        self.user_list = self.usersOnQuery()

        print("Users on query: ")
        for user in self.user_list:
            print(user.id)

    def usersOnQuery(self):
        usersReturn = []
        for user in self.master.user_list:
            if self.master.pointOnQuadrant(user.point()) in self.quadrants:
                usersReturn.append(user)
        usersReturn.remove(self.user)
        return usersReturn


class Master:
    def __init__(self, canvas, quadsize, userlock, poilock):

        self.log = []
        self.timelapse = 0
        self.canvas = canvas
        self.quadsize = quadsize
        self.poi_list = []
        self.user_list = []
        self.querydraw_list = []
        self.query_list = []
        self.config = Config()
        self.quadrant_list = self.getQuadrants()
        self.fileHandler = fileHandler.logHandler(self)
        self.userlock = userlock
        self.poilock = poilock
        self.connectionratio = 1

    def exploreQuadrant(self, user: User) -> User:
        """If quadrant is unexplored then user is retainer and leader.
        If quadrant has leader and is present return Leader.
        If quadrant has a leader but isn't present, tries to claim leadership of said quadrant.
        Returns leader.
        """

        userQuadrant = self.pointOnQuadrant(user.point())
        print("User " + str(user.id) + " is exploring quadrant " + str(userQuadrant.id))
        if userQuadrant.unexplored == True:
            userQuadrant.unexplored = False
            userQuadrant.leader = user
            user.retainList.append(userQuadrant)
            print("User " + str(user.id) + " explored quadrant " + str(userQuadrant.id) + " for the first time.")
            return userQuadrant.leader
        elif userQuadrant in user.retainList:
            userQuadrant.leader = user
            return userQuadrant.leader
        elif userQuadrant.leader is not None and self.pointOnQuadrant(userQuadrant.leader.point()) is self.pointOnQuadrant(user.point()):
            print("Leader found within quadrant range.")
            return userQuadrant.leader
        else:
            target = None
            for element in self.user_list:
                if userQuadrant in element.retainList:
                    target = element
            if target is None:
                print("ERROR!!! RETAINER NOT FOUND")
                return userQuadrant.leader
            else:
                search = ConnectionGraph(user, target, self)
                if search.returnMatch() is not None:
                    if not self.pointOnQuadrant(target.point()) == self.pointOnQuadrant(user.point()):
                        self.claimQuadrant(userQuadrant,user)
                        return userQuadrant.leader


    def getRetainer(self,quadrant: Quadrant):
        for element in self.user_list:
            if quadrant in element.retainList:
                return element
        return None

    def populateRandomPoi(self,poi1,poi2,poi3):
        for quadrant in self.quadrant_list:
            quadrant.poi_list.append(poi1)
            quadrant.poi_list.append(poi2)
            quadrant.poi_list.append(poi3)


    def claimQuadrant(self, quadrant: Quadrant, user: User):
            retainer = self.getRetainer(quadrant)
            retainer.retainList.remove(quadrant)
            user.retainList.append(quadrant)
            quadrant.leader = user


    def getQuadrants(self):
        """This function initializes all quadrants """
        QuadrantsReturn = []
        xquads = self.canvas[0] // self.quadsize
        yquads = self.canvas[1] // self.quadsize
        id = 1
        print("Number of quadrants on map: " + str(xquads * yquads))
        for y in range(yquads):
            for x in range(xquads):
                QuadrantsReturn.append(Quadrant(id, (x * self.quadsize, y * self.quadsize)))
                id += 1
        return QuadrantsReturn

    def pointOnQuadrant(self, point):
        """Given a point, returns the quadrant where it exist.
        Parameters: (Point (x,y))"""
        checkX = point[0] // self.quadsize + 1
        checkY = point[1] // self.quadsize + 1
        broad = self.canvas[0] // self.quadsize
        quadId = checkX + (checkY * broad - broad)
        for quadrant in self.quadrant_list:
            if quadId == quadrant.id:
                returnQuad = quadrant
        return returnQuad

    def newQuery(self, user, time, category, point, id=0):
        quadrants = [self.pointOnQuadrant((user.xpos, user.ypos))]
        if point[0] > 0 and point[0] < self.canvas[0]:
            if point[1] > 0 and point[1] < self.canvas[1]:
                quadrants.append(self.pointOnQuadrant(point))
        if point[0] + self.quadsize > 0 and point[0] + self.quadsize < self.canvas[0]:
            if point[1] > 0 and point[1] < self.canvas[1]:
                quadrants.append(self.pointOnQuadrant((point[0] + self.quadsize, point[1])))
        if point[0] > 0 and point[0] < self.canvas[0]:
            if point[1] + self.quadsize > 0 and point[1] + self.quadsize < self.canvas[1]:
                quadrants.append(self.pointOnQuadrant((point[0], point[1] + self.quadsize)))
        if point[0] + self.quadsize > 0 and point[0] + self.quadsize < self.canvas[0]:
            if point[1] + self.quadsize > 0 and point[1] + self.quadsize < self.canvas[1]:
                quadrants.append(self.pointOnQuadrant((point[0] + self.quadsize, point[1] + self.quadsize)))
        if id == 0:
            self.query_list.append(Query(len(self.query_list) + 1, user, time, category, point, quadrants, self))
        else:
            self.query_list.append(Query(id, user, time, category, point, quadrants, self))

    def setQuadrant(self, user):
        Quadrant = self.pointOnQuadrant(user.point())
        Quadrant.user_list.append(user)
        user.quadrant = Quadrant

    def addUser(self, user):
        self.setQuadrant(user)
        self.user_list.append(user)

    def addPoi(self, poi):
        self.poi_list.append(poi)

    def threadLoadState(self, loadfile):
        self.userlock.acquire()
        self.poilock.acquire()
        try:
            threading.Thread(target=self.fileHandler.loadState, args=[loadfile]).start()
        finally:
            self.userlock.release()
            self.poilock.release()

    def threadSaveState(self, savefile):
        self.userlock.acquire()
        self.poilock.acquire()
        try:
            threading.Thread(target=self.fileHandler.loadState, args=[savefile]).start()
        finally:
            self.userlock.release()
            self.poilock.release()

    def threadDumpLog(self, debug):
        thread = threading.Thread(target=self.fileHandler.dumpLog, args=[debug]).start()

    def threadAddEvent(self, time, event, argument, debug, user):
        event = fileHandler.logEvent(time, event, argument, debug, user)
        threading.Thread(target=self.fileHandler.addEvent, args=[event]).start()


class ConnectionGraph:
    def __init__(self, primalNode: User, targetNode: User,master):
        self.root = Node(str(primalNode.id), None, None, **{'User': primalNode, 'Target': False})
        possibleList = list()
        checkedList = list()
        self.targetFound = None
        possibleList.append(self.root)
        while len(possibleList) > 0:
                currentNode = possibleList.pop(0)
                checkedList.append(currentNode.User)
                broadcastList = currentNode.User.broadcastUsers()
                for element in broadcastList:
                    if element not in checkedList:
                        if element is targetNode:
                            newnode = Node(str(element.id), currentNode, None, **{'User': element, 'Target': True})
                            self.targetFound = newnode
                        else:
                            newnode = Node(str(element.id), currentNode, None, **{'User': element, 'Target': False})
                        possibleList.append(newnode)
        self.printGraphInConsole()

    def printGraphInConsole(self):
        print("Printing connection graph:")
        for pre, fill, node in RenderTree(self.root):
            print("%s%s" % (pre, node.name))
        if self.targetFound is not None:
            print("Quadrant leader (User" +self.targetFound.name+") found.")
        else:
            print("Quadrant leader not found within search range.")

            # Node(str(currentNode.id),root,None,**{User: c })

    def returnMatch(self):
        if self.targetFound is not None:
            return self.targetFound.User
        else:
            return None

