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



#Validations!

def checkAddUserDataType(idinput, xinput, yinput):
    returnFlag = True
    if not (idinput.get().isnumeric()):
        returnFlag = False
    if not (xinput.get().isnumeric()):
        returnFlag = False
    if not (yinput.get().isnumeric()):
        returnFlag = False
    return returnFlag


def checkAddUserUnique(idinput, master, userlock):
    userlock.acquire()
    try:
        returnFlag = True
        for element in master.user_list:
            if (int(idinput.get()) == element.id):
                returnFlag = False
    finally:
        userlock.release()
        return returnFlag


def checkAddUserBoundaries(xinput, yinput, master, masterlock):
    returnFlag = True
    masterlock.acquire()
    try:
        canvasx = master.canvas[0]
        canvasy = master.canvas[1]
    finally:
        masterlock.release()
        if not (int(xinput.get()) > 0 and int(xinput.get()) < canvasx):
            returnFlag = False
        if not (int(yinput.get()) > 0 and int(yinput.get()) < canvasy):
            returnFlag = False
        return returnFlag
