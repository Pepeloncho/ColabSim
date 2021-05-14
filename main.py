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
    # Lock used to protect critical sections using master.Query list.
    querylock = threading.Lock()
    # Lock used to protect critical sections using track of time and time-based triggers.
    timelock = threading.Lock()
    # Lock used to protect critical sections that R/W 'master' class. Mostly used to protect 'config' child.
    masterlock = threading.Lock()

    # Creating an instance of a 'master' class to use as a central data structure of all threads.
    # Check 'objects.py' from 'Objects' package to read it's code.
    # Parameters: Canvas Size (x,y), QuadrantSize (int)
    master = objects.Master((400,400),100)

    print(master.__dict__)
    print(master.config.__dict__)
    # Creating threads and calling procedures:
    # Threads and procedures are named before greek gods accordingly to their functionality.


    # Cronos, god of time and ether --> Thread spawned to handle timelapse and time-triggered events on background.
    # Check 'eventEngine.py' from 'Background' package to read this thread's code.
    # Parameters: Master (objects.Master), UserLock (Lock), POILock (Lock), TimeLock (Lock), MasterLock (Lock)
    Cronos = eventEngine.eventEngine(master,userlock,poilock,timelock,querylock,masterlock)
    CRONOS = threading.Thread(target= Cronos.timeLapse)


    #Atlas, titan burdened with the earth --> Thread spawned to handle cartesian canvas visual on a PyGame user interface.
    #Check 'UIpygame.py' from 'Navigation' package to read this thread's code.
    Atlas = UIpygame.UIpygame(master,userlock,poilock,timelock,querylock,masterlock)
    ATLAS = threading.Thread(target= Atlas.threadScreen)


    # Thanatos, god of demise and death--> Thread spawned to terminate all threads and exit.
    # Check 'threadKiller.py' from 'Background' package to read this thread's code.
    # Parameters: Master (objects.master), Masterlock (Lock)
    THANATOS = threading.Thread(target=threadKiller.damnation, args=(Atlas, Cronos))

    # Hestia, goddess of hearth and home --> Thread spawned to handle user I/O on a TKinter based user interface.
    # Check 'UItkinter.py' from 'Navigation' package to read this thread's code.
    # Parameters: Master (objects.Master), UserLock (Lock), POILock (Lock), TimeLock (Lock), MasterLock (Lock), threadKiller (Thread)
    HESTIA = threading.Thread(target= UItkinter.threadGUI, args=(master, userlock, poilock, querylock, timelock, masterlock, THANATOS))



    #Hermes, olympic messenger, god of haste & guide --> Thread spawned to handle file W/R.
    #Check 'fileHandler.py' from 'Background' package to read this thread's code.
    #Hermes = threading.Thread(target=)



    print("Starting Threads...")
    HESTIA.start()
    ATLAS.start()
    CRONOS.start()

