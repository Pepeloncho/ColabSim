import tkinter as tk
from tkinter import ttk
from navigation import operations
from functools import partial
import functools as ft


def threadGUI(master,userlock,poilock,timelock,masterlock):

    selected = master.power
    iddrop = 0
    window = tk.Tk()

    window.title("ColabSim Control Pane")
    window.geometry('350x200')
    notebook = ttk.Notebook(window)

    mainframe = ttk.Frame(notebook)
    notebook.add(mainframe, text="Main")
    powerlabel = tk.Label(mainframe, text="Simulation Power Switch", font=("Arial", 12))
    poweronradius = tk.Radiobutton(mainframe, text='Sim On', value=True, command=lambda:operations.powerSwitch(master,masterlock,True))
    poweroffradius = tk.Radiobutton(mainframe, text='Sim Off', value=False, command=lambda:operations.powerSwitch(master,masterlock,False))
    printlogbutton = tk.Button(mainframe, text="Print Log",command=lambda:operations.printLog(master,masterlock))
    powerlabel.grid(column=0, row=1)
    poweronradius.grid(column=0, row=2)
    poweroffradius.grid(column=1, row=2)
    printlogbutton.grid(column=0, row=4)

    newuserframe = ttk.Frame(notebook)
    notebook.add(newuserframe, text="Insert user")
    idinput= tk.StringVar()
    xinput= tk.StringVar()
    yinput= tk.StringVar()
    idlabel = tk.Label(newuserframe, text="New user ID", font=("Arial", 10))
    identry = tk.Entry(newuserframe, textvariable=idinput, font=('Arial', 10, 'normal'))
    xylabel = tk.Label(newuserframe, text="X and Y position of new user", font=("Arial", 10))
    xentry = tk.Entry(newuserframe, textvariable=xinput, font=('Arial', 10, 'normal'))
    yentry = tk.Entry(newuserframe, textvariable=yinput, font=('Arial', 10, 'normal'))
    newuserpartial = partial(operations.addUser, idinput, xinput, yinput, [], 1, master,userlock)
    adduserbutton = tk.Button(newuserframe,text="Add User", command=newuserpartial)
    clearformbutton = tk.Button(newuserframe,text="Clear", command= lambda:operations.removeUser(iddrop,master,userlock))

    idlabel.grid(column=0, row=1)
    identry.grid(column=0, row=2)
    xylabel.grid(column=0, row=3)
    xentry.grid(column=0, row=4)
    yentry.grid(column=1, row=4)
    adduserbutton.grid(column=0, row=5)
    clearformbutton.grid(column=1, row=5)
    notebook.grid(column=0, row=0)

    window.mainloop()
