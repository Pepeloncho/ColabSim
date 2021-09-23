import threading
from objects import objects
from navigation import UIpygame
from navigation import UItkinter
from background import eventEngine
from background import threadKiller
from background import operations
from background import fileHandler


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

    # Instanciating file W/R, statistics tracking and log handler monitor object.
    hermes = fileHandler.logHandler()


    # Creating an instance of a 'master' class to use as a central data structure of all threads.
    # Check 'objects.py' from 'Objects' package to read it's code.
    # Parameters: Canvas Size (x,y), QuadrantSize (int)
    master = objects.Master((800,600),100,userlock,poilock,hermes)
    print(master.config.__dict__)
    # Creating threads and calling procedures:
    # Threads, classes and procedures are named before greek gods accordingly to their functionality.


    # Cronos, god of time and ether --> Thread spawned to handle timelapse and time-triggered events on background.
    # Check 'eventEngine.py' from 'Background' package to read this thread's code.
    # Parameters: Master (objects.Master), UserLock (Lock), POILock (Lock), TimeLock (Lock), MasterLock (Lock)
    Cronos = eventEngine.eventEngine(master,userlock,poilock,timelock,querylock,masterlock)
    CRONOS = threading.Thread(target= Cronos.timeLapse)


    #Athena, goddess of wisdom --> Class populated with backend methods to help with CRUD operations, validations and data processing in general
    # Check 'operations.py' from 'Background' package to read this class' code.
    # Parameters:
    Athena = operations.operations(master,userlock,poilock,timelock,querylock,masterlock)

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
    HESTIA = threading.Thread(target= UItkinter.threadGUI, args=(master,userlock,poilock,timelock,querylock,masterlock, THANATOS, Athena))







    print("Starting Threads...")
    HESTIA.start()
    ATLAS.start()
    CRONOS.start()

