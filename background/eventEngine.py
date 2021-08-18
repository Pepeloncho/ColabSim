import time
import random
import math
from background import fileHandler

class eventEngine:
    def __init__(self,master,userlock,poilock,timelock,querylock,masterlock):
        self.master = master
        self.userlock = userlock
        self.poilock = poilock
        self.timelock = timelock
        self.querylock = querylock
        self.masterlock = masterlock


        print("Event engine instance created.")


    def terminate(self):
            self.masterlock.acquire()
            try:
                self.master.config.running = False
            finally:
                self.masterlock.release()

    def timeLapse(self):
        while (self.master.config.running):
            flag = False
            if (self.master.config.power == True):
                   time.sleep(0.1)
                   self.timelock.acquire()
                   timeaux = math.modf(self.master.timelapse)[1]
                   self.master.timelapse = self.master.timelapse + 0.1
                   newtime = math.modf(self.master.timelapse)[1]
                   self.timelock.release()
                   if (timeaux != newtime):
                        flag = True
            if (flag):
                self.wakeUserlist()
                self.cleanQueries()

    def getQuery(self):
        return ("query",random.randint(0,5))
        #TODO: Derandomize this.

    def getStep(self):
        return ("move",random.randint(1,4))

    def getQueryStartPoint(self,user):
        self.masterlock.acquire()
        try:
            query_x = ((user.xpos) - (self.master.quadsize // 2))
            query_y = ((user.ypos) - (self.master.quadsize // 2))
        finally:
            self.masterlock.release()
            return (query_x,query_y)

    #def usersOnArea(self, startPoint, ignoreUserList = []):
    #    usersReturnList = []
    #    try:
    #        for element in self.master.user_list:
    #                if (startPoint[0] <= element.xpos < startPoint[0] + self.master.quadsize):
    #                    if (startPoint[1] <= element.ypos < startPoint[1] + self.master.quadsize):
    #                        usersReturnList.append(element)
    #        for element in ignoreUserList:
    #            usersReturnList.remove(element)
    #    finally:
    #        return usersReturnList



    def performQuery(self, user, category,master):
        print("User "+ str(user.id) + " performing a query nearby concerning category  " + str(category))
        # Calculating top-left end of the query square
        queryPoint = self.getQueryStartPoint(user)
        print("Query starting point stablished at: " + str(queryPoint[0]) + "," + str(queryPoint[1]))
        self.timelock.acquire()
        try:
            newQuery = (user, queryPoint, self.master.timelapse)
            EventList = []
            EventList.append(category)
            self.master.threadAddEvent(self.master.timelapse, "query", EventList, False, user.id)
        finally:
            self.timelock.release()


        self.querylock.acquire()
        try:
            self.master.querydraw_list.append(newQuery)
            master.newQuery(user, master.timelapse, category, queryPoint)
        finally:
            self.querylock.release()

        return



    def cleanQueries(self):
        self.querylock.acquire()
        try:
            for query in self.master.querydraw_list:
                if (self.master.timelapse >= query[2] + 5):
                    self.master.querydraw_list.remove(query)
        finally:
            self.querylock.release()



    def performStep(self,user,direction):
        fromQuadrant = self.master.pointOnQuadrant(user.point())
        if (direction == 1):
            #Try to go north
            if (user.ypos >= 10):
                #TODO Check old and new tentative quadrant, if they are different, react.
                newQuadrant = self.master.pointOnQuadrant((user.xpos,user.ypos - 10))
                user.ypos = user.ypos - 10
                toQuadrant = self.master.pointOnQuadrant(user.point())
                if fromQuadrant is not toQuadrant:
                    fromQuadrant.user_list.remove(user)
                    toQuadrant.user_list.append(user)
                    if fromQuadrant.leader is user:
                        fromQuadrant.leader = None
                    self.master.exploreQuadrant(user)
                self.master.setQuadrant(user)
                self.master.threadAddEvent(self.master.timelapse, "move", [direction], True, user.id)
            else:
                self.performStep(user,random.randint(1,4))
        if (direction == 2):
            #Try to go east
            if (user.xpos <= self.master.canvas[0] - 10):
                user.xpos = user.xpos + 10
                toQuadrant = self.master.pointOnQuadrant(user.point())
                if fromQuadrant is not toQuadrant:
                    fromQuadrant.user_list.remove(user)
                    toQuadrant.user_list.append(user)
                    if fromQuadrant.leader is user:
                        fromQuadrant.leader = None
                    self.master.exploreQuadrant(user)



                self.master.setQuadrant(user)
                self.master.threadAddEvent(self.master.timelapse, "move", [direction], True, user.id)
            else:
                self.performStep(user,random.randint(1,4))
        if (direction == 3):
            #Try to go south
            if (user.ypos <= self.master.canvas[1] - 10):
                user.ypos = user.ypos + 10
                toQuadrant = self.master.pointOnQuadrant(user.point())
                if fromQuadrant is not toQuadrant:
                    fromQuadrant.user_list.remove(user)
                    toQuadrant.user_list.append(user)
                    if fromQuadrant.leader is user:
                        fromQuadrant.leader = None
                    self.master.exploreQuadrant(user)


                self.master.setQuadrant(user)
                self.master.threadAddEvent(self.master.timelapse, "move", [direction], True, user.id)
            else:
                self.performStep(user,random.randint(1,4))
        if (direction == 4):
            #Try to go west
            if (user.xpos >= 10):
                user.xpos = user.xpos - 10
                toQuadrant = self.master.pointOnQuadrant(user.point())
                if fromQuadrant is not toQuadrant:
                    fromQuadrant.user_list.remove(user)
                    toQuadrant.user_list.append(user)
                    if fromQuadrant.leader is user:
                        fromQuadrant.leader = None
                    self.master.exploreQuadrant(user)


                self.master.setQuadrant(user)
                self.master.threadAddEvent(self.master.timelapse, "move", [direction], True, user.id)
            else:
                self.performStep(user,random.randint(1,4))



#TODO populateTasks() function only queues random steps for now. Add more functionality here in the format (task,parameter)
    def populateTasks(self,user):
        if (len(user.tasklist) == 0):
            if not (random.randint(0,19)==19):
                user.tasklist.append(self.getStep())
                return
            else:
                user.tasklist.append(self.getQuery())
                return
        else:
            return


    #TODO WARNING: wakeUserList is taking the lock hostage! Tentative concept: Duplicate user_list to iterate through users without the need of a lock.
    def wakeUserlist(self):

        self.userlock.acquire()
        try:

            for element in self.master.user_list:
                self.populateTasks(element)
                #TODO this populateTasks() call doesn't belong here
                perform = element.tasklist.pop(0)
                if (perform[0] == "move"):

                    self.performStep(element,perform[1])

                if (perform[0] == "query"):

                    self.performQuery(element,perform[1],self.master)
        finally:
            self.userlock.release()

