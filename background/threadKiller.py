import threading
from navigation import UIpygame
from background import eventEngine

def damnation(master,masterlock):
    #Destroy all creatures. They can't be regenerated.
    UIpygame.killTheLights(master,masterlock)
    eventEngine.terminate(master,masterlock)




