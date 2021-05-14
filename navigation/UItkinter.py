import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from background import operations
from functools import partial



def handleExit(window,threadKiller):
   if messagebox.askokcancel("Quit", "Do you really want to quit?"):
    #TODO: Session not saved exception and warning.
       window.destroy()
       threadKiller.start()



def checkNewPoi(idinput, xinput, yinput, category, master, poilock, masterlock):
    flag = True
    if not (operations.checkEntryDataType(idinput, xinput, yinput)):
        messagebox.showwarning(message="X,Y and ID parameters require integer numbers only", title="Wrong input data")
        flag = False
    elif not (operations.checkPoiUnique(idinput, master, poilock)):
        messagebox.showwarning(message="New POI can't be assigned with an already existing ID",
                               title="New POI ID duplicity")
        flag = False

    elif not (operations.checkBoundariesOnCanvas(xinput, yinput, master, masterlock)):
        messagebox.showwarning(message="New POI X,Y position out of canvas parameters",
                               title="New user out of boundaries")
        flag = False

    elif not (operations.checkCategorySelected(category)):
        messagebox.showwarning(message="New POI requires a valid category to be selected.", title="Invalid category")
        flag = False

    if (flag):
        operations.addPoi(idinput, xinput, yinput, category, master, poilock)



def checkNewUser(idinput,xinput,yinput,master,userlock,masterlock):
        flag = True
        if not (operations.checkEntryDataType(idinput, xinput, yinput)):
            messagebox.showwarning(message="X,Y and ID parameters require integer numbers only", title="Wrong input data")
            flag = False
        elif not (operations.checkUserUnique(idinput, master, userlock)):
            messagebox.showwarning(message="New user can't be assigned with an already existing ID", title="New user ID duplicity")
            flag = False

        elif not (operations.checkBoundariesOnCanvas(xinput, yinput, master, masterlock)):
            messagebox.showwarning(message="New user X,Y position out of canvas parameters", title="New user out of boundaries")
            flag = False

        if (flag):
            operations.addUser(idinput, xinput, yinput, [], 1, master, userlock)



def threadGUI(master,userlock,poilock,timelock,querylock,masterlock,threadKiller):

    print("Starting Tkinter...")
    selected = master.config.power
    iddrop = 0
    window = tk.Tk()

    window.title("ColabSim Control Pane")
    window.geometry('350x200')
    window.protocol('WM_DELETE_WINDOW', lambda: handleExit(window,threadKiller))
    notebook = ttk.Notebook(window)
    showGridFlag = tk.BooleanVar()
    mainframe = ttk.Frame(notebook)
    notebook.add(mainframe, text="Main")
    powerlabel = tk.Label(mainframe, text="Simulation Power Switch", font=("Arial", 12))
    poweronradius = tk.Radiobutton(mainframe, text='Sim On', value=True, command=lambda: operations.powerSwitch(master, masterlock, True))
    poweroffradius = tk.Radiobutton(mainframe, text='Sim Off', value=False, command=lambda: operations.powerSwitch(master, masterlock, False))
    printlogbutton = tk.Button(mainframe, text="Print Log", command=lambda: operations.printLog(master, masterlock))
    togglegridcheckbox = tk.Checkbutton(mainframe, text="Show grid", variable=showGridFlag, command=lambda: operations.toggleGrid(master, masterlock, showGridFlag.get()))
    togglegridcheckbox.toggle()

    powerlabel.grid(column=0, row=1)
    poweronradius.grid(column=0, row=2)
    poweroffradius.grid(column=1, row=2)
    togglegridcheckbox.grid(column=0, row=3)
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
    newuserpartial = partial(checkNewUser, idinput, xinput, yinput,master,userlock,masterlock)
    adduserbutton = tk.Button(newuserframe,text="Add User", command=newuserpartial)
    clearformbutton = tk.Button(newuserframe, text="Clear", command= lambda: operations.removeUser(iddrop, master, userlock))

    idlabel.grid(column=0, row=1)
    identry.grid(column=0, row=2)
    xylabel.grid(column=0, row=3)
    xentry.grid(column=0, row=4)
    yentry.grid(column=1, row=4)
    adduserbutton.grid(column=0, row=5)
    clearformbutton.grid(column=1, row=5)
    notebook.grid(column=0, row=0)

    newpoiframe = ttk.Frame(notebook)
    notebook.add(newpoiframe, text="Insert POI")
    poiidinput = tk.StringVar()
    poixinput = tk.StringVar()
    poiyinput = tk.StringVar()
    poiidlabel = tk.Label(newpoiframe, text="New Point Of Interest ID", font=("Arial", 10))
    poiidentry = tk.Entry(newpoiframe, textvariable=poiidinput, font=('Arial', 10, 'normal'))
    poixylabel = tk.Label(newpoiframe, text="X and Y position of new POI", font=("Arial", 10))
    poixentry = tk.Entry(newpoiframe, textvariable=poixinput, font=('Arial', 10, 'normal'))
    poiyentry = tk.Entry(newpoiframe, textvariable=poiyinput, font=('Arial', 10, 'normal'))
    categorylabel = tk.Label(newpoiframe, text="Category", font=("Arial", 10))
    categorycombobox =ttk.Combobox(newpoiframe, state="readonly")
    categorycombobox["values"]=["Triangle","5-Star","Diamond","Arrow","4-Star","Heart"]
    addpoibutton = tk.Button(newpoiframe, text="Add Poi", command=lambda:checkNewPoi(poiidinput,poixinput,poiyinput,categorycombobox.current(),master,poilock,masterlock))

    poiidlabel.grid(column=0, row=1)
    poiidentry.grid(column=0, row=2)
    poixylabel.grid(column=0, row=3)
    poixentry.grid(column=0, row=4)
    poiyentry.grid(column=1, row=4)
    categorylabel.grid(column=0, row=6)
    categorycombobox.grid(column=1, row=6)
    addpoibutton.grid(column=0, row=7)


    notebook.grid(column=0, row=0)



    window.mainloop()
