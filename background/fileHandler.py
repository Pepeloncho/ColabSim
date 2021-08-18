import csv
import os
from objects import objects
import datetime

class logHandler:
    def __init__(self, master, eventList = [],debugList = []):
        self.eventList = eventList
        self.master = master
        self.filename = self.dateString()

    def dateString(self):
            dateTimeObj = datetime.datetime.now()
            timestampStr = dateTimeObj.strftime("%d_%b_%Y_%H-%M-%S")
            return "log-" + timestampStr + ".csv"

    def addEvent(self,logEvent):
        self.eventList.append(logEvent)

    def dumpLog(self,debug):
        file = self.dateString()
        if ".csv" in file:
            with open(file,'w') as dumpfile:
                writer = csv.writer(dumpfile,delimiter=",",quotechar='"')
                for event in self.eventList:
                    #if ((event.debug is True and debug is True) or event.debug is False):
                        writer.writerow([event.commentary, int(event.timeMark), int(event.userID), event.event, event.argument])




    def loadState(self,csvfile):
        if ".csv" in csvfile:
            self.master.poi_list = []
            self.master.user_list = []
            with open(csvfile, 'r') as load_state:
                csv_reader = csv.DictReader(load_state, delimiter=",")
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        print(f'Field names are {", ".join(row)}')
                        #Handle headers.
                        line_count += 1
                    else:
                        if row[0] == "user":
                            newuser = objects.User(int(row[1]), int(row[2]), int(row[3]), [], 1)
                            self.master.addUser(newuser)
                        if row[0] == "poi":
                            newpoi = objects.Poi(int(row[1]), int(row[2]), int(row[3]), int(row[4]))
                            self.master.addPoi(newpoi)
                        #TODO dump csv into dictionary
                        line_count += 1
                print(f'Processed {line_count} lines.')
                return
                #TODO return dictionary

    def saveState(self,csvfile):
        if not self.master.user_list and not self.master.poi_list:
            with open(csvfile, mode='w') as save_state:
                writer = csv.writer(save_state,delimiter=",",quotechar='"')
                writer.writerow(['data', 'id', 'xpos','ypos','argument'])
                for user in self.master.user_list:
                    writer.writerow(['user', int(user.id), int(user.xpos),int(user.ypos),''])
                for poi in self.master.poi_list:
                    writer.writerow(['poi', int(poi.id), int(poi.xpos), int(poi.ypos), int(poi.category)])


        else:
            pass
            #TODO Handle empty state














class logEvent:
    def __init__(self, time, event, argument, debug, userid = "NotID"):
        self.timeMark = time
        self.userID = userid
        self.event = event
        self.argument = argument
        self.debug = debug
        self.commentary = self.print()


    def print(self):
        if isinstance(self.userID,int):
            if self.event == "move":
                return self._printMovement()
            if self.event == "query":
                return self._printQuery()

            else:
                print("User "+ str(self.userID) + 'around second: ' + str(self.timeMark) + ' performed a "' + str(self.event) + '" request with argument: ' + str(self.argument[0]) + ".")

    def _printMovement(self):
        returnLog = "User " + str(self.userID) + " moved towards " + self._directionPrint() + " at second " + str(self.timeMark)
        return returnLog

    def _printQuery(self):
        returnLog = "User " + str(self.userID) + " performed a query at second: " + str(self.timeMark)  + " concerning category " + self._categoryPrint()
        return returnLog

    def _directionPrint(self):
        if not self.event ==  "move":
            return False
        else:
            if self.argument[0] == 1:
                return "north"
            if self.argument[0] == 2:
                return "east"
            if self.argument[0] == 3:
                return "south"
            if self.argument[0] == 4:
                return "west"
            else: return False

    def _categoryPrint(self):
            if self.argument[0] == 0:
                return "Category0"
            if self.argument[0] == 1:
                return "Category1"
            if self.argument[0] == 2:
                return "Category2"
            if self.argument[0] == 3:
                return "Category3"
            if self.argument[0] == 4:
                return "Category4"
            if self.argument[0] == 5:
                return "Category5"
            if self.argument[0] == 6:
                return "Category6"
            if self.argument[0] == 7:
                return "Category7"

