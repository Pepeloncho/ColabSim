import threading
from objects import objects
from navigation import UIpygame
from navigation import UItkinter
from background import eventEngine
from background import threadKiller


if __name__ == '__main__':
    # Lock used to protect critical sections using 'User' class variables like X,Y position, ID, cache, etc.
    userlock = threading.Lock()
    # Lock used to protect critical sections using 'Poi' class variables like X,Y position, ID, etc.
    poilock = threading.Lock()
    # Lock used to protect critical sections using track of time and time-based triggers.
    timelock = threading.Lock()
    # Lock used to protect critical sections that R/W 'master' class. Mostly used to protect 'config' child.
    masterlock = threading.Lock()

    # Creating an instance of a 'master' class to use as a central data structure of all threads.
    # To check it's code.
    master = objects.Master([],0,(400,400),100)

    print(master.__dict__)

    # Creating threads and calling procedures:
    # Threads and procedures are named before greek gods accordingly to their functionality.

    #Thanatos, god of demise and death--> Thread spawned to terminate all threads and exit.
    #Check 'threadKiller.py' from 'Background' package to read this thread's code.
    Thanatos = threading.Thread(target=threadKiller.damnation, args=(master, masterlock))

    # Hestia, goddess of hearth and home --> Thread spawned to handle user I/O on a TKinter based user interface.
    # Check 'UItkinter.py' from 'Navigation' package to read this thread's code.
    Hestia = threading.Thread(target= UItkinter.threadGUI, args=(master,userlock,poilock,timelock,masterlock,Thanatos))

    #Cronos, god of time and ether --> Thread spawned to handle timelapse and time-triggered events on background.
    #Check 'eventEngine.py' from 'Background' package to read this thread's code.
    Cronos = threading.Thread(target= eventEngine.timeLapse, args=(master, userlock, poilock, timelock, masterlock))

    #Atlas, titan burdened with the earth --> Thread spawned to handle cartesian canvas visual on a PyGame user interface.
    #Check 'UIpygame.py' from 'Navigation' package to read this thread's code.
    Atlas = threading.Thread(target=UIpygame.threadScreen, args=(master, userlock, poilock, timelock, masterlock))

    #Hermes, olympic messenger, god of haste & guide --> Thread spawned to handle file W/R and event log.
    #Check 'fileHandler.py' from 'Background' package to read this thread's code.
    #Hermes = threading.Thread(target=)




    Hestia.start()
    Atlas.start()
    Cronos.start()
    #Hera ---> Thread spawned to handle user I/O.
    #Atlas ---> Thread spawned to handle canvas visual interface.
    #Cronos ---> Process spawned to handle time lapse.
    #Hermes ---> Thread spawned to handle pipeline with external files.
    #Hades ---> Thread spawned to kill all threads and processes and cleaning out memory heaps.
