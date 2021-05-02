import time
import random
import math

def timeLapse(master,userlock,poilock,timelock,masterlock):
    while (True):
        timelock.acquire()
        flag = False
        try:
           if (master.power == True):
               time.sleep(0.1)
               timeaux = math.modf(master.timelapse)[1]
               master.timelapse = master.timelapse + 0.1
               newtime = math.modf(master.timelapse)[1]
               print("Time elapsed ="+ str(master.timelapse))
               if (timeaux != newtime):
                   flag = True


        finally:
            timelock.release()
            if (flag):
                wakeUserlist(master,userlock)

def getStep():
    return ("move",random.randint(1,4))

def performStep(user,direction,master):
    print("User "+ str(user.id) + " moving towards " + str(direction))
    if (direction == 1):
        #Try to go north
        if (user.ypos >= 10):
            user.ypos = user.ypos - 10
            master.log.append((master.timelapse,user.id,"move",direction))
        else:
            performStep(user,random.randint(1,4),master)
    if (direction == 2):
        #Try to go east
        if (user.xpos <= master.canvas[0] - 10):
            user.xpos = user.xpos + 10
            master.log.append((master.timelapse,user.id,"move",direction))
        else:
            performStep(user,random.randint(1,4),master)
    if (direction == 3):
        #Try to go south
        if (user.ypos <= master.canvas[1] - 10):
            user.ypos = user.ypos + 10
            master.log.append((master.timelapse,user.id,"move",direction))
        else:
            performStep(user,random.randint(1,4),master)
    if (direction == 4):
        #Try to go west
        if (user.xpos >= 10):
            user.xpos = user.xpos - 10
            master.log.append((master.timelapse,user.id,"move",direction))
        else:
            performStep(user,random.randint(1,4),master)



#TODO populateTasks() function only queues random steps for now. Add more functionality here in the format (task,parameter)
def populateTasks(user):
    if (len(user.tasklist) == 0):
        user.tasklist.append(getStep())
        return
    else:
        return


def wakeUserlist(master,userlock):
    userlock.acquire()
    print("Waking all users.")
    try:

        for element in master.user_list:
            populateTasks(element)
            #TODO this populateTasks() call doesn't belong here
            print(element.__dict__)
            perform = element.tasklist.pop(0)
            print("Performing task: " + str(perform))
            if (perform[0] == "move"):

                performStep(element,perform[1],master)

    finally:
        userlock.release()

