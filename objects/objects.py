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
    def __init__(self, id, category):
        self.id = id
        self.category = category

class Master:
    def __init__(self, power, log, timelapse, canvas, cuadsize):
        self.power = power
        self.log = log
        self.timelapse = timelapse
        self.canvas = canvas
        self.cuadsize = cuadsize
        self.poi_list = []
        self.user_list = []

