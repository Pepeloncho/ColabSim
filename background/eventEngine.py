import time
import random
import math
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
                   print("Time elapsed ="+ str(self.master.timelapse))
                   if (timeaux != newtime):
                        flag = True
            if (flag):
                self.wakeUserlist()

    def getQuery(self):
        return ("query",random.randint(0,5))

    def getStep(self):
        return ("move",random.randint(1,4))

    def getQueryStartPoint(self,user):
        self.masterlock.acquire()
        self.userlock.acquire()
        try:
            query_x = ((user.xpos) - (self.master.cuadsize//2))
            query_y = ((user.ypos) - (self.master.cuadsize//2))
        finally:
            self.masterlock.release()
            self.userlock.release()
            return (query_x,query_y)

    def usersOnArea(self, startPoint, ignoreUserList = []):
        usersReturnList = []
        self.userlock.acquire()
        try:
            for element in self.master.user_list:
                if startPoint[0] <= element.x_pos < startPoint[0] + self.master.cuadsize and startPoint[1] <= element.y_pos < startPoint[1] + self.master.cuadsize:
                    usersReturnList.append(element)
            for element in ignoreUserList:
                usersReturnList.remove(element)
        finally:
            self.userlock.release()
            return usersReturnList





    def performQuery(self, user, category):
        print("User"+ str(user.id) + " performing a query nearby concerning category  " + str(category))
        # Calculating top-left end of the query square





    def performStep(self,user,direction):
        print("User "+ str(user.id) + " moving towards " + str(direction))
        if (direction == 1):
            #Try to go north
            if (user.ypos >= 10):
                user.ypos = user.ypos - 10
                self.master.log.append((self.master.timelapse,user.id,"move",direction))
            else:
                self.performStep(user,random.randint(1,4))
        if (direction == 2):
            #Try to go east
            if (user.xpos <= self.master.canvas[0] - 10):
                user.xpos = user.xpos + 10
                self.master.log.append((self.master.timelapse,user.id,"move",direction))
            else:
                self.performStep(user,random.randint(1,4))
        if (direction == 3):
            #Try to go south
            if (user.ypos <= self.master.canvas[1] - 10):
                user.ypos = user.ypos + 10
                self.master.log.append((self.master.timelapse,user.id,"move",direction))
            else:
                self.performStep(user,random.randint(1,4))
        if (direction == 4):
            #Try to go west
            if (user.xpos >= 10):
                user.xpos = user.xpos - 10
                self.master.log.append((self.master.timelapse,user.id,"move",direction))
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


    def wakeUserlist(self):
        self.userlock.acquire()
        print("Waking all users.")
        try:

            for element in self.master.user_list:
                self.populateTasks(element)
                #TODO this populateTasks() call doesn't belong here
                print(element.__dict__)
                perform = element.tasklist.pop(0)
                print("Performing task: " + str(perform))
                if (perform[0] == "move"):

                    self.performStep(element,perform[1])

        finally:
            self.userlock.release()

