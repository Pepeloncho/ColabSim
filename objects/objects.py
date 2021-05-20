import queue

class User:
  def __init__(self, id, xpos, ypos, cache, speed):
    self.id = id
    self.xpos = xpos
    self.ypos = ypos
    self.cache = cache
    self.speed = speed
    self.tasklist = []

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

class Master:
    def __init__(self, canvas, quadsize):

        self.log = []
        self.timelapse = 0
        self.canvas = canvas
        self.quadsize = quadsize
        self.poi_list = []
        self.user_list = []
        self.query_list = []
        self.config = Config()
        self.quadrant_list = self.getQuadrants()

    def getQuadrants(self):
        QuadrantsReturn = []
        xquads = self.canvas[0] // self.quadsize
        yquads = self.canvas[1] // self.quadsize
        id = 1
        print ("Number of quadrants on map: "+str(xquads * yquads))
        for y in range(yquads):
            for x in range(xquads):
                QuadrantsReturn.append(Quadrant(id,(x*self.quadsize,y*self.quadsize)))
                id += 1
        return QuadrantsReturn

    #def pointOnQuadrant(self):
        #Cuidado con salirse!




