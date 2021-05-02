
from multiprocessing import Process
import threading
from objects import objects
from navigation import UIpygame
from navigation import UItkinter
from navigation import eventEngine

if __name__ == '__main__':
    userlock = threading.Lock()
    poilock = threading.Lock()
    timelock = threading.Lock()
    masterlock = threading.Lock()
    master = objects.Master(False,[],0,(400,400),100)
    print(master.__dict__)
    Hera = threading.Thread(target= UItkinter.threadGUI, args=(master,userlock,poilock,timelock,masterlock))
    Atlas = threading.Thread(target= UIpygame.threadScreen, args=(master,userlock,poilock,timelock,masterlock))
    Cronos = threading.Thread(target= eventEngine.timeLapse, args=(master,userlock,poilock,timelock,masterlock))
    Hera.start()
    Atlas.start()
    Cronos.start()
    #Hera ---> Thread spawned to handle user I/O.
    #Atlas ---> Thread spawned to handle canvas interface.
    #Cronos ---> Process spawned to handle time lapse.
    #Hermes ---> Thread spawned to handle pipeline with Cronos process.
    #Hades ---> Function spawned to kill all threads and processes and cleaning out memory heaps.
