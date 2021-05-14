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


class Master:
    def __init__(self, canvas, cuadsize):

        self.log = []
        self.timelapse = 0
        self.canvas = canvas
        self.cuadsize = cuadsize
        self.poi_list = []
        self.user_list = []
        self.query_list = []
        self.config = Config()

