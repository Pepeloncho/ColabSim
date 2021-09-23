import csv
import os
from typing import List, Any

from objects import objects
import datetime
import threading



class logHandler:
    def __init__(self):
        self.eventList = []
        self.filename = self.dateString()
        self.tracker = StatsTracker()
        self.taskList = []
        self.statLock = threading.Lock()




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




    #def loadState(self,csvfile,poi_list,user_list):
        #if ".csv" in csvfile:
         #   poi_list = []
          #  user_list = []
           # with open(csvfile, 'r') as load_state:
            #    csv_reader = csv.DictReader(load_state, delimiter=",")
             #   line_count = 0
              #  for row in csv_reader:
               #     if line_count == 0:
                #        print(f'Field names are {", ".join(row)}')
                 #       #Handle headers.
                  #      line_count += 1
                   # else:
                    #    if row[0] == "user":
                     #       newuser = objects.User(int(row[1]), int(row[2]), int(row[3]), [], 1)
                      #      self.master.addUser(newuser)
                       # if row[0] == "poi":
                        #    newpoi = objects.Poi(int(row[1]), int(row[2]), int(row[3]), int(row[4]))
                         #   self.master.addPoi(newpoi)
                        #TODO dump csv into dictionary
                        #line_count += 1
                #print(f'Processed {line_count} lines.')
                #return
                #TODO return dictionary

    #def saveState(self,csvfile):
     #   if not self.master.user_list and not self.master.poi_list:
      #      with open(csvfile, mode='w') as save_state:
       #         writer = csv.writer(save_state,delimiter=",",quotechar='"')
        #        writer.writerow(['data', 'id', 'xpos','ypos','argument'])
         #       for user in self.master.user_list:
          #          writer.writerow(['user', int(user.id), int(user.xpos),int(user.ypos),''])
           #     for poi in self.master.poi_list:
            #        writer.writerow(['poi', int(poi.id), int(poi.xpos), int(poi.ypos), int(poi.category)])


        #else:
         #   pass
          #  #TODO Handle empty state


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



class StatsTracker:
    statThreshold = 10
    historicStats: List[dict] = list()
    statsPrintable = list()
    statsWritable = list()
    studyVariables = dict()
    def __init__(self):

        self.stats = {
                        "time": 0,
                        "totalResponses": 0,
                        "peerResponses": 0,
                        "peerFloodResponses": 0,
                        "serverResponses": 0,
                        "kAnonApplied": 0,
                        "lDivApplied": 0,
                        "totalQueries": 0,
                        "maskedQueries": 0,
                        "riskyQueries": 0,
                        "invalidQueries": 0,
                        "leaderSearchTotal": 0,
                        "leaderNotFound": 0,
                        "leaderFromFlood": 0,
                        "leaderInRange": 0,
                        "fullCacheTotal": 0,
                        "informedCaching": 0,
                        "distanceCaching": 0,
                        "migrations": 0,
                        "leadershipClaimed": 0,
                        "colabPoiRecords": 0,
                        "allPoiRecords": 0,
                        "userCount": 0,
                        "poiCount": 0,
            }

        StatsTracker.historicStats.append(self.stats.copy())
    @staticmethod
    def trackStats(elapsedTime,uniqueCacheSize, cacheSize, userCount, poiCount, statDictionary,statlock):
        statlock.acquire()
        try:
            statDictionary['time'] = elapsedTime
            statDictionary['colabPoiRecords'] = uniqueCacheSize
            statDictionary['allPoiRecords'] = cacheSize
            statDictionary['userCount'] = userCount
            statDictionary['poiCount'] = poiCount
            StatsTracker.historicStats.append(statDictionary.copy())
            print("NUMBER OF STATS:" + str(len(StatsTracker.historicStats)))
            if len(StatsTracker.historicStats) == StatsTracker.statThreshold:
                StatsTracker.getPrintableStats()
        finally:
            statlock.release()



    def count(self,key):
        self.stats[key] += 1

    @staticmethod
    def getPrintableStats():
        StatsTracker.statsPrintable.append(
            "Tiempo,Consultas Formuladas,Respuestas Recibidas,Respuestas en rango de conexion directo,Respuestas por flooding,Respuestas formuladas por un servidor LBS")
        for stat in StatsTracker.historicStats:

            StatsTracker.statsPrintable.append(str(int(stat['time']))+","+str(stat['totalQueries'])+ ","+ str(stat['totalResponses'])+","+str(stat['peerResponses'])+","+str(stat['peerFloodResponses'])+","+ str(stat['serverResponses']))


        StatsTracker.statsPrintable.append("---------------------------------------------------------------")
        StatsTracker.statsPrintable.append("Tiempo,K-anonimatos aplicados,L-diversidad aplicadas, Total de consultas enmascaradas,Consultas arriesgadas")
        for stat in StatsTracker.historicStats:
            StatsTracker.statsPrintable.append(str(int(stat['time']))+","+str(stat['kAnonApplied'])+","+str(stat['lDivApplied'])+","+str(stat['maskedQueries'])+","+str(stat['riskyQueries']))
        StatsTracker.statsPrintable.append("---------------------------------------------------------------")
        StatsTracker.statsPrintable.append("Tiempo, Rastreo de lider realizados, Rastreo de lider fallidos, Rastreos de lider en rango directo, Rastreos de lider por flooding")
        for stat in StatsTracker.historicStats:
            StatsTracker.statsPrintable.append(str(int(stat['time']))+","+str(stat['leaderSearchTotal'])+","+str(stat['leaderNotFound'])+","+str(stat['leaderInRange'])+","+str(stat['leaderFromFlood']))
        StatsTracker.statsPrintable.append("---------------------------------------------------------------")
        StatsTracker.statsPrintable.append("Tiempo,Total de conflictos de almacenamiento por cache repleto, Total de priorizaciones de cache informadas por frecuencia, Total de priorizaciones de cache por distancia")
        for stat in StatsTracker.historicStats:
            StatsTracker.statsPrintable.append(str(int(stat['time']))+","+str(stat['fullCacheTotal'])+","+str(stat['informedCaching'])+","+str(stat['distanceCaching']))
        StatsTracker.statsPrintable.append("---------------------------------------------------------------")
        StatsTracker.statsPrintable.append("Tiempo,Migraciones de cuadrante,Cambios de lider de cuadrante")
        for stat in StatsTracker.historicStats:
            StatsTracker.statsPrintable.append(str(int(stat['time']))+","+str(stat['migrations'])+","+str(stat['leadershipClaimed']))
        StatsTracker.statsPrintable.append("---------------------------------------------------------------")
        StatsTracker.statsPrintable.append("Tiempo,Tasa de dependencia a servidor LBS(Respuestas de servidor/Total de repsuestas),Registros almacenados en ambiente colaborativo")
        for stat in StatsTracker.historicStats:
            if stat['totalResponses'] == 0:
                StatsTracker.statsPrintable.append(str(int(stat['time'])) + "," + "---" + "," + "0")
            else:
                StatsTracker.statsPrintable.append(str(int(stat['time']))+","+str("%.2f" % (stat['serverResponses']/stat['totalResponses']))+","+str(stat['colabPoiRecords']))

    @staticmethod
    def saveStatisticsToFile():
        for table in StatsTracker.getWritable():
            StatsTracker.dumpTableIntoCsv(table,table.pop())

    @staticmethod
    def dumpTableIntoCsv(Table,name):
        file = StatsTracker.tableString(name)
        if ".csv" in file:
            with open(file,'w') as dumpfile:
                writer = csv.writer(dumpfile,delimiter=",",quotechar='"')
                for row in Table:
                        writer.writerow(row)

    @staticmethod
    def tableString(name):
            dateTimeObj = datetime.datetime.now()
            timestampStr = dateTimeObj.strftime("%d_%b_%Y_%H-%M-%S")
            return "table-"+name+" ("+ str(StatsTracker.historicStats[-1]['userCount']) +"["+str(StatsTracker.studyVariables['cacheMaxSize'])+"])  " + timestampStr + ".csv"

    @staticmethod
    def getWritable():
        querySummary = list()
        querySummary.append(["Tiempo","Consultas Formuladas","Respuestas Recibidas","Respuestas en rango de conexion directo","Respuestas por flooding","Respuestas formuladas por un servidor LBS"])
        for stat in StatsTracker.historicStats:
            querySummary.append([stat['time'],stat['totalQueries'],stat['totalResponses'],stat['peerResponses'],stat['peerFloodResponses'],stat['serverResponses']])
        maskingSummary = list()
        maskingSummary.append(["Tiempo","Respuestas formuladas por servidor LBS","Consultas enmascaradas","K-anonimatos aplicados","L-diversidad aplicadas","Consultas arriesgadas"])
        for stat in StatsTracker.historicStats:
            maskingSummary.append([stat['time'],stat['serverResponses'],stat['maskedQueries'],stat['kAnonApplied'],stat['lDivApplied'],stat['riskyQueries']])
        quadrantDataSummary = list()
        quadrantDataSummary.append(["Tiempo","Migraciones","Cambios de lider de cuadrante","Rastreos totales","Rastreos en rango directo","Rastreos por flooding","Rastreos fallidos"])
        for stat in StatsTracker.historicStats:
            quadrantDataSummary.append([stat['time'],stat['migrations'],stat['leadershipClaimed'],stat['leaderSearchTotal'],stat['leaderInRange'],stat['leaderFromFlood'],stat['leaderNotFound']])
        cachingSummary = list()
        cachingSummary.append(["Tiempo","Total de datos en cache","Tamaño del universo de datos en ambiente colaborativo","Conflictos de almacenamiento de cache","Resolución de caché por Frecuencia","Resolución de caché por distancia"])
        for stat in StatsTracker.historicStats:
            cachingSummary.append([stat['time'],stat['allPoiRecords'],stat['colabPoiRecords'],stat['fullCacheTotal'],stat['informedCaching'],stat['distanceCaching']])
        LBSUsageRateSummary = list()
        LBSUsageRateSummary.append(["Tiempo","Tasa de uso del servidor LBS","Tasa de uso del ambiente colaborativo","Porcentaje de capacidad de cache","Universo de datos unicos en ambiente colaborativo vs. Universo"])
        for stat in StatsTracker.historicStats:
            if stat['totalResponses'] == 0:
                serverRate = ""
                colabRate = ""
            else:
                serverRate = (stat['serverResponses'] * 100) /stat['totalResponses']
                colabRate = ((stat['peerResponses']+stat['peerFloodResponses'])*100)/stat['totalResponses']

            if stat['poiCount'] == 0:
                poiKnownPercentage = ""
            else:
                poiKnownPercentage = (stat['colabPoiRecords'] * 100)/stat['poiCount']
            if stat['userCount'] == 0 or StatsTracker.studyVariables['cacheMaxSize'] == 0:
                cacheFillPercentage = ""
            else:
                print(stat['userCount'])
                print(StatsTracker.studyVariables['cacheMaxSize'])
                print(stat['allPoiRecords'])
                cacheFillPercentage = (stat['allPoiRecords']*100)/(stat['userCount']*StatsTracker.studyVariables['cacheMaxSize'])
            LBSUsageRateSummary.append([stat['time'],serverRate,colabRate,poiKnownPercentage,cacheFillPercentage])
        querySummary.append('querySummary')
        maskingSummary.append('maskingSummary')
        quadrantDataSummary.append('quadrantDataSummary')
        cachingSummary.append('cachingSummary')
        LBSUsageRateSummary.append('LBSUsageRateSummary')
        tableLibrary = list([querySummary,maskingSummary,quadrantDataSummary,cachingSummary,LBSUsageRateSummary])
        return tableLibrary





    @staticmethod
    def setConstants(cacheSize,l,k,quadSize):
            StatsTracker.studyVariables = {
                        "cacheMaxSize": cacheSize,
                        "l" : l,
                        "k": k,
                        "QuadrantSideLength": quadSize
            }
            print(StatsTracker.studyVariables)


