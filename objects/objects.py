import math
import queue
import threading
from copy import deepcopy
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

    def printCacheList(self) -> str:
        returnString = "{"
        for cache in self.cache:
            returnString = returnString + str(cache.id) + " "
        returnString = returnString + "}"
        return returnString

    def point(self):
        return (self.xpos, self.ypos)

    def gotoxy(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos

    def userDistance(self, user):
        return abs(math.dist(self.point(), user.point()))

    def distanceTo(self, point):
        return abs(math.dist(self.point(), point))

    def broadcastUsers(self):
        matchList = []
        radius = math.sqrt(2) * self.master.quadsize
        for user in self.master.user_list:
            if self.userDistance(user) < radius:
                matchList.append(user)
                origin = self.point()
                destiny = user.point()
                origin = (origin[0] + 15,origin[1] + 15)
                destiny = (destiny[0] +15, destiny[1] + 15)
                drawConn = (origin,destiny,self.master.timelapse)
                self.master.conndraw_list.append(drawConn)

        matchList.remove(self)
        return matchList

    def storeInCache(self,poi):

        self.cache.append(poi)

        print("User "+ str(self.id) + "added Poi "+ str(poi.id) + "to it's cache (Buffer size:"+str(len(self.cache))+")")
        if len(self.cache) >= self.master.cachesize:
            self.master.cachedraw_list.append((self.point(),self.master.timelapse))
            self.master.stats('fullCacheTotal')
            quadrant = self.master.pointOnQuadrant(self.point())
            self.master.stats('leaderSearchTotal')
            nearUsers = self.broadcastUsers()
            nearUsers.append(self)
            quadrantDataAvailable = False
            if quadrant.leader in nearUsers:
                quadrantDataAvailable = True
                self.master.stats('leaderInRange')
            else:
                quadrantDataAvailable = self.checkIfUserInFloodRange(quadrant.leader)
                if quadrantDataAvailable:
                    self.master.stats('leaderFromFlood')

            def sortCriteria(e):
                return self.distanceTo(e.point())

            self.cache.sort(key=sortCriteria,
                            reverse=True)  # Sort cache by distance from data to user in descendent order
            existingFrequencies = []

            for frequency in quadrant.frequencyTable:
                existingFrequencies.append(frequency[0])

            if quadrantDataAvailable  or len(existingFrequencies) > self.master.l:
                print("Quadrant leader found: User "+ str(self.id)+" is performing informed caching technique")
                self.master.threadAddEvent(self.master.timelapse, "cache",
                                           ["frequency"], False, self.id)

                for frequency in quadrant.frequencyTable: #This table is sorted in every insertion.

                    for data in self.cache:

                        if data.category not in existingFrequencies:
                            self.master.stats('informedCaching')
                            self.cache.remove(data) #Furthest data (due to cache sort) with no frequency registered.
                            print("User " + str(self.id) + "deletes data relative to POI " + str(
                                data.id) + "from it's cache.")
                            return
                        if data.category == frequency[0]:
                            self.cache.remove(data) #Furthest data (due to cache sort) with the lesser category frequency (due to frequency sort)
                            self.master.stats('informedCaching')
                            print("User " + str(self.id) + "deletes data relative to POI " + str(
                                data.id) + " from it's cache.")
                            return
            else:
                    print("Quadrant leader not found or frequency list smaller than l: User " + str(self.id) + " is priorizing cache by distance.")
                    self.master.threadAddEvent(self.master.timelapse, "cache",
                                               ["distance"], False, self.id)
                    self.master.stats('leaderNotFound')
                    potentialDiscard = self.cache[0]
                    for data in self.cache:
                        if self.distanceTo(data.point()) > self.distanceTo(potentialDiscard.point()):
                            potentialDiscard = data
                    print("User " +str(self.id) + "deletes data relative to POI " + str(potentialDiscard.id) + "from it's cache.")
                    self.cache.remove(potentialDiscard)
                    self.master.stats('distanceCaching')






    def checkIfUserInFloodRange(self,target):
        if target in self.broadcastUsers():  # leader within user broadcast range
            print("target within range")
            return True
        else:
            print("searching for target: " + str(target.id))
            search = ConnectionGraph(self, [target],self.master) # search for user within flood range
            if search.returnMatch() is not None:
                print("target found")
                return True
            else:
                return False


class Poi:
    def __init__(self, id, xpos, ypos, category):
        self.id = id
        self.xpos = xpos
        self.ypos = ypos
        self.category = category

    def point(self):
        point = (self.xpos,self.ypos)
        return point


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
        self.frequencyTable= []
        self.unexplored = True
        self.leader = None

    def addFrequency(self,category):
        if len(self.frequencyTable) == 0:   # If table empty
            self.frequencyTable.append([category,1])
            return

        for frequency in self.frequencyTable:
            if frequency[0] == category: #If category already in table
                frequency[1] = frequency[1] + 1
                self.sortFrequency()
                return

        self.frequencyTable.append([category,1]) #If category wasn't found on table
        self.sortFrequency()
        return

    def sortFrequency(self):
        def sortCriteria(e):
            return e[1]
        self.frequencyTable.sort(key=sortCriteria)
        print(*self.frequencyTable)










class Query:
    def __init__(self, id, user, time, category, point, master):
        self.id = id
        self.user = user
        self.time = time
        self.category = category
        self.point = point
        self.master = master
        self.masked = False
        self.quadrants = self.getQuadrantsOnZone()
        self.user_list = self.usersOnQuery()
        self.quadrant = self.master.pointOnQuadrant(self.point)
        self.response = None
        self.responseType = None # types include : 'masked','risky','flood','direct'.'self'
        self.responder = None
        self.master.askdraw_list.append((point,category,self.master.timelapse))
        self.resolveQuery()
        self.master.stats('totalQueries')

        if self.response is None:
            pass
        else:
            if self.responder != "LBS Server":
                self.master.threadAddEvent(self.master.timelapse, "answer", [self.responder.id,self.response.id,self.responseType], False, user.id)
            else:
                if self.masked is True:
                    self.master.threadAddEvent(self.master.timelapse,"lbsanswer",[self.response.id,"masked"],False,user.id)
                else:
                    self.master.threadAddEvent(self.master.timelapse, "lbsanswer", [self.response.id, "risky"],False,user.id)



    def usersOnQuery(self):
        usersReturn = []
        for user in self.master.user_list:
            if self.master.pointOnQuadrant(user.point()) in self.quadrants:
                usersReturn.append(user)
        usersReturn.remove(self.user)
        return usersReturn

    def resolveQuery(self):
        relevantPois = self.getRelevantPois()
        if len(relevantPois)==0:
            print("Trying to resolve a query with no possible response within coherent area of context. Aborting request.")
            self.master.stats('invalidQueries')
            return False
        possibleResponders = self.getPossibleResponders(relevantPois)
        if self.checkSelfResponse(relevantPois):
            return True
        if self.checkDirectResponse(possibleResponders,relevantPois): #check if query can be solved within user range
            return True
        elif self.checkFloodResponse(possibleResponders,relevantPois): #check if query can be solved by flooding
            return True
        else:
            self.forceLBSresponse(relevantPois)
            #send requests to LBS server, tries to comply with K-anonymity and l-diversity masking requirements.
            return True

    def getRelevantPois(self):
        relevantPoiList = []
        poisOnRange = self.getPoisOnRange(self.getRelevantZonePoint())
        print("Number of POIs relevant to the query : " +str(len(poisOnRange)))
        for poi in self.master.poi_list:
            if poi.category == self.category and poi in poisOnRange:
                relevantPoiList.append(poi)
        return relevantPoiList

    def getPoisOnRange(self, point):
        poisOnRange = []
        relevanceRadius = 1.5 * math.sqrt(2) * self.master.quadsize
        for poi in self.master.poi_list:
            if self.user.distanceTo(poi.point())<relevanceRadius:
                poisOnRange.append(poi)
        print("Possible Responses to query: "+str(len(poisOnRange)))
        return poisOnRange

    def getRelevantZonePoint(self):
        xpos = self.point[0]
        ypos = self.point[1]
        query_x = ((xpos) - (self.master.quadsize // 2))
        query_y = ((ypos) - (self.master.quadsize // 2))
        return (query_x, query_y)

    def getPossibleResponders(self, poiList):
        responderList = []
        for user in self.master.user_list:
            for poi in user.cache:
                if poi in poiList:
                    responderList.append(user)
        print("Possible Responders to query: "+str(len(responderList)))
        return responderList

    def getQuadrantsOnZone(self):
        point = self.getRelevantZonePoint()
        quadrants = [self.master.pointOnQuadrant((point[0] + self.master.quadsize // 2, point[1] + self.master.quadsize // 2))]
        if point[0] > 0 and point[0] < self.master.canvas[0]:
            if point[1] > 0 and point[1] < self.master.canvas[1]:
                quadrants.append(self.master.pointOnQuadrant(point))
        if point[0] + self.master.quadsize > 0 and point[0] + self.master.quadsize < self.master.canvas[0]:
            if point[1] > 0 and point[1] < self.master.canvas[1]:
                quadrants.append(self.master.pointOnQuadrant((point[0] + self.master.quadsize, point[1])))
        if point[0] > 0 and point[0] < self.master.canvas[0]:
            if point[1] + self.master.quadsize > 0 and point[1] + self.master.quadsize < self.master.canvas[1]:
                quadrants.append(self.master.pointOnQuadrant((point[0], point[1] + self.master.quadsize)))
        if point[0] + self.master.quadsize > 0 and point[0] + self.master.quadsize < self.master.canvas[0]:
            if point[1] + self.master.quadsize > 0 and point[1] + self.master.quadsize < self.master.canvas[1]:
                quadrants.append(
                    self.master.pointOnQuadrant((point[0] + self.master.quadsize, point[1] + self.master.quadsize)))
        return quadrants

    #def getUsersOnZone(self):
    #    userList = []
    #    quadrantList = self.getQuadrantsOnZone()
    #    for quadrant in quadrantList:
    #        for user in quadrant.user_list:
    #            userList.append(user)

    def getMatchFromCache(self, user, poiList):
        matchList = []
        for poi in user.cache:
            if poi in poiList:
                matchList.append(poi)
        return matchList

    def checkSelfResponse(self,relevantPois: list):
        for poi in relevantPois:
            if poi in self.user.cache:
                print("Relevant poi found within query user's cache.")
                print("Query responder: " + str(self.user.id))
                self.responder = self.user
                self.setResponse = self.setResponse(poi,"self")
                return True
        return False


    def checkDirectResponse(self, possibleResponders, relevantPois):
        directUsers = self.user.broadcastUsers()
        directUsers.append(self.user)
        for user in directUsers:
            if user in possibleResponders:
                print("Query resolved within direct range.")
                print("Query responder: " + str(user.id))
                self.responder = user
                self.setResponse(self.getMatchFromCache(user, relevantPois)[0],"direct")
                print("Query response: Poi "+ str(self.response.id))
                self.master.stats('peerResponses')
                return True
        return False

    def checkFloodResponse(self, possibleResponders,relevantPois):
        if len(possibleResponders)==0:
            print("There is no possible responder in users universe. Bypassing to forced LBS response to save memory.")
            return False

        search = ConnectionGraph(self.user, possibleResponders, self.master)
        if search.returnMatch() is not None:
            print("Query resolved within flood range.")
            print("Query responder: User" +str(search.returnMatch().id))
            self.responder = search.returnMatch()
            self.setResponse(self.getMatchFromCache(search.returnMatch(),relevantPois)[0],"flood")
            print("Query response: Poi " + str(self.response.id))
            self.master.stats('peerFloodResponses')
            return True
        else:
            return False



    def getMasking(self,l,k):
        semanticMasking = self.lDiversity(l)
        positionMasking = self.kAnonymity(k,self.user)
        if not semanticMasking and not positionMasking:
            print("User "+str(self.user.id)+" couldn't mask query concerning category "+str(self.category)+" from position " +str(self.point)+" at "+str(self.time)+" seconds.")
            #Store historical data in log
            self.masked = False
            return False
        else:
            if semanticMasking:
                print("l-diversity satisfied for query concerning category"+str(self.category)+" from position "+ str(self.point)+ " at "+ str(self.time)+" seconds")
                self.master.stats('lDivApplied')
            if positionMasking:
                self.master.stats('kAnonApplied')
                print("k-anonymity satisfied for query concerning category"+str(self.category)+" from position "+ str(self.point)+ " at "+ str(self.time)+" seconds")

            print("User "+str(self.user.id)+" succesfully masked")
            self.master.stats('maskedQueries')
            #Store historical data in log
            self.masked = True
            return True



    def kAnonymity(self,k,user):
          returnList = []
          usersOnZone = user.broadcastUsers()
          if usersOnZone is not None:
              if len(usersOnZone) >= k:
                for i in range(k):
                    returnList.append(usersOnZone[i].point())
                return returnList
          print("Not enough nearby users to satisfy k-Anonymity on relevant zone.")
          return False


    def lDiversity(self,l):
        frequencyList = []
        categoryList = []
        self.master.stats('leaderSearchTotal')
        nearUsers = self.user.broadcastUsers()
        nearUsers.append(self.user)
        if self.quadrant.leader in nearUsers: #leader within user range or is quadrant leader himself
            self.master.stats('leaderInRange')
            if len(self.quadrant.frequencyTable) >= l:
                for i in range(l):
                    frequencyList.append(self.quadrant.frequencyTable[i])

                for frequency in frequencyList:
                    categoryList.append(frequency[0])

                return categoryList
            else:
                print("Not enough historical data to satisfy l-diversity on quadrant " + str(self.quadrant.id) + "+")
                return False


        if self.quadrant.leader is not None:
            search = ConnectionGraph(self.user, [self.quadrant.leader], self.master) #search for leader within flood range
            if search.returnMatch() is not None:
                self.master.stats('leaderFromFlood')
                if len(self.quadrant.frequencyTable) >= l:
                    for i in range(l):
                        frequencyList.append(self.quadrant.frequencyTable[i])

                    for frequency in frequencyList:
                        categoryList.append(frequency[0])
                    return categoryList
                else:
                    print("Not enough historical data to satisfy l-diversity on quadrant "+str(self.quadrant.id)+"+")
                    return False
            else:
                self.master.stats('leaderNotFound')
                print("Quadrant "+str(self.quadrant.id)+" historical data couldn't be read because it's leader wasn't found within flood range. Can't satisfy l-diversity.")
                return False
        else:
                print("ERROR: Quadrant is missing a quadrant leader. Can't satisfy l-Diversity")
                return False

    def forceLBSresponse(self, relevantPois):
            masking = self.getMasking(self.master.l,self.master.k)  # Values of l and k for l-diversity and k-anonymity.
            tentativeAnswer = relevantPois[0]
            for poi in relevantPois:
                if self.user.distanceTo(poi.point()) < self.user.distanceTo(tentativeAnswer.point()):
                    tentativeAnswer = poi  #If risking a query to LBS server, at least get the best answer possible!


            #add historical data

            if masking:
                responseType = 'masked'
                #add historical data
            else:
                responseType = 'risky'
                self.master.stats('riskyQueries')
                #add historical data
            print("Query responder: LBS Server")
            self.responder = "LBS Server"
            self.response = self.setResponse(tentativeAnswer,responseType)
            print("Query response: Poi " + str(tentativeAnswer.id))
            self.master.stats('serverResponses')

    def setResponse(self, response, responseType):
        self.response = response
        self.responseType = responseType
        self.master.stats('totalResponses')
        self.master.pointOnQuadrant(response.point()).addFrequency(self.category)
        if self.responder == "LBS Server":
            self.master.lbsdraw_list.append((self.point,self.category,self.response.id,self.masked,self.master.timelapse))
        else:
            if(self.responder.id == self.user.id):
                self.master.selfdraw_list.append((self.point,self.category,self.response.id,self.master.timelapse))
            else:
                self.master.respdraw_list.append((self.responder.point(),self.category,self.response.id,self.master.timelapse))
        if response not in self.user.cache:
            self.user.storeInCache(response)






class Master:
    def __init__(self, canvas, quadsize, userlock, poilock, logHandler):


        self.log = []
        self.timelapse = 0
        self.canvas = canvas
        self.quadsize = quadsize
        self.poi_list = []
        self.user_list = []
        self.querydraw_list = []
        self.conndraw_list = []
        self.askdraw_list = []
        self.respdraw_list = []
        self.lbsdraw_list = []
        self.selfdraw_list = []
        self.cachedraw_list = []
        self.query_list = []
        self.config = Config()
        self.quadrant_list = self.getQuadrants()
        self.fileHandler = logHandler
        self.userlock = userlock
        self.poilock = poilock
        self.connectionratio = 1
        self.cachesize = 4
        self.l = 3
        self.k = 3
        self.statLimit = 40
        self.logHandler = logHandler
        self.stats = logHandler.tracker.count
        self.statDict = logHandler.tracker.stats
        fileHandler.StatsTracker.setConstants(self.cachesize,self.l,self.k,self.quadsize)


    def exploreQuadrant(self, user: User) -> User:
        """If quadrant is unexplored then user is retainer and leader.
        If quadrant has leader and is present return Leader.
        If quadrant has a leader but isn't present, tries to claim leadership of said quadrant.
        Returns leader.
        """

        userQuadrant = self.pointOnQuadrant(user.point())
        print("User " + str(user.id) + " is exploring quadrant " + str(userQuadrant.id))
        self.threadAddEvent(self.timelapse, "explore", [userQuadrant.id], False, user.id)
        if userQuadrant.unexplored == True or userQuadrant.leader == None:
            userQuadrant.unexplored = False
            userQuadrant.leader = user
            self.stats('leadershipClaimed')
            user.retainList.append(userQuadrant)
            print("User " + str(user.id) + " explored quadrant " + str(userQuadrant.id) + " for the first time.")
            return userQuadrant.leader
        elif userQuadrant in user.retainList:
            userQuadrant.leader = user
            return userQuadrant.leader
        elif userQuadrant.leader is not None and self.pointOnQuadrant(
                userQuadrant.leader.point()) is self.pointOnQuadrant(user.point()):
            print("Leader found within quadrant range.")
            self.stats('leaderSearchTotal')
            self.stats('leaderInRange')
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
                search = ConnectionGraph(user, [target], self)
                if search.returnMatch() is not None:
                    self.stats('leaderSearchTotal')
                    self.stats('leaderFromFlood')
                    if not self.pointOnQuadrant(target.point()) == self.pointOnQuadrant(user.point()):
                        self.claimQuadrant(userQuadrant, user)
                        return userQuadrant.leader
                else:
                    self.stats('leaderSearchTotal')
                    self.stats('leaderNotFound')

    def getRetainer(self, quadrant: Quadrant):
        for element in self.user_list:
            if quadrant in element.retainList:
                return element
        return None

    def getUniqueCache(self):
        uniqueCacheSet = set()
        for user in self.user_list:
            for cache in user.cache:
                uniqueCacheSet.add(cache.id)
        return len(uniqueCacheSet)

    def getCacheSize(self):
        cacheCount = 0
        for user in self.user_list:
            cacheCount = cacheCount + len(user.cache)
        return cacheCount

    def getUserCount(self):
        return len(self.user_list)

    def getPoiCount(self):
        return len(self.poi_list)


    def claimQuadrant(self, quadrant: Quadrant, user: User):
        retainer = self.getRetainer(quadrant)
        retainer.retainList.remove(quadrant)
        user.retainList.append(quadrant)
        aux = quadrant.leader
        quadrant.leader = user
        aux2 = quadrant.leader
        if aux is not aux2:
            self.stats('leadershipClaimed')

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
        x = point[0]
        y = point[1]
        if x < 1:
            x= 2
        if x > 799:
            x = 799
        if y < 1:
            y = 2
        if y > 599:
            y = 598

        correctedPoint = (x,y)
        checkX = correctedPoint[0] // self.quadsize + 1
        checkY = correctedPoint[1] // self.quadsize + 1
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
            self.query_list.append(Query(len(self.query_list) + 1, user, time, category, point, self))
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
        self.pointOnQuadrant(poi.point()).poi_list.append(poi)

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
    def __init__(self, primalNode: User, targetNodes, master):
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
                    for target in targetNodes:
                        if element.id == target.id:
                            newnode = Node(str(element.id), currentNode, None, **{'User': element, 'Target': True})
                            self.targetFound = newnode
                            self.printGraphInConsole()
                            return
                        else:
                            newnode = Node(str(element.id), currentNode, None, **{'User': element, 'Target': False})
                            possibleList.append(newnode)
        self.printGraphInConsole()


    def printGraphInConsole(self):
        print("Printing connection graph:")
        for pre, fill, node in RenderTree(self.root):
            print("%s%s" % (pre, node.name))
        if self.targetFound is not None:
            print("Found user on graph: (User " + str(self.targetFound.User.id) + ")")
        else:
            print("Target not found on graph.")

            # Node(str(currentNode.id),root,None,**{User: c })

    def returnMatch(self):
        if not self.targetFound:
            return None
        else:
            return self.targetFound.User
