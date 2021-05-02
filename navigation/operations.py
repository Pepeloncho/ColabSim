from objects import objects
import math

def powerSwitch(master,masterlock,powerflag):
    masterlock.acquire()
    try:
        master.power = powerflag
        print("Turning simulation power to: "+str(master.power))
    finally:
        masterlock.release()

def printLog(master,masterlock):
    masterlock.acquire()
    try:
        print(str(master.log))
    finally:
        masterlock.release()


def getUserList(master,userlock):
    userlock.acquire()
    try:
        returnlist = master.user_list.copy()
    finally:
        userlock.release()
        return returnlist

def getPoiList(master,poilock):
    poilock.acquire()
    try:
        returnlist = master.poi_list.copy()
    finally:
        poilock.release()
        return returnlist

def addUser(id, xpos, ypos, cache, speed, master, userlock):
    newuser = objects.User(int(id.get()), int(xpos.get()), int(ypos.get()), cache, speed)
    print(newuser.__dict__)
    userlock.acquire()
    try:
        master.user_list.append(newuser)
    finally:
        userlock.release()

#TODO in addUser(): Validate x and y within canvas borders, Validate id as a unique value.

def removeUser(id,master,userlock):
    userlock.acquire()
    try:
        for element in master.user_list:
            if element.id == id:
                master.user_list.remove(element)
    finally:
        userlock.release()