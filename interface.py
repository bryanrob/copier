# <INSERT LICENSING CLAUSE HERE>

#from typing import Optional, Tuple, Union
import customtkinter as tk
import tkfilebrowser
import os
import json
from copy_processor import Manager,IndividualThreadWidget
from interface_elements import packChildren
#from time import sleep

versionData:dict
with open("./versionData/version.json","r") as file:
    versionData=json.load(file)

errStr="ERROR"
version=versionData.get("version",errStr)
author=versionData.get("author",errStr)

def dictValFromKey(value,dict:dict,default=None):
    result = list(dict.keys())[list(dict.values()).index(value)]
    if result is not None:
        return result
    else:
        return default
#END def dictValFromKey

class Window(tk.CTk):
    """
    The container of this graphical interface.
    """

    __activeWorkingBar = False #Indicator for the status of the working bar.
    __selectedItems = [False,False] #Indicates the selected items.

    __foldersDic = {}
    __filesDic = {}
    __othersDic = {}

    __items=[__foldersDic,__filesDic,__othersDic]

    options : dict
    defaultOptions : dict
    #Options' parameters:
    #   "job-type" : str; The base copy mode set for the current job.
    #   "log" : bool; Allows the logging of the job.
    #   "logType" : str; Sets the hashing algorithm used in the logging.
    #   "logDest" : str; The destination of the log file.
    #       - If empty, use the job's destination directory.
    #   "fileConflictMode" : int; The program's reaction to when a file exists in both the source & destination.
    #   "threads" : int; The amount of threads that the program processes for file reading/writing.

    __types = {
        1:"File",
        0:"Folder"
    }
    toplevel = None

    def __init__(this) -> None:
        super().__init__()

        with open("./versionData/defaultOptions.json","r") as file:
            this.defaultOptions=json.load(file)

        #Initialize the files & folders lists.
        this.__filesList=[]
        this.__foldersList=[]

        #with open("options.json","r") as file:
        #    this.options=json.load(file)
        this.options=this.defaultOptions.copy()


    #INTERFACE STYLES
        this.pad=5
        buttonPad=20
        this.baseFontName="Consolas"
        this.titleFont=tk.CTkFont(this.baseFontName,24,weight="bold",underline=True)
        this.bodyFont=tk.CTkFont(this.baseFontName,18)
        this.buttonFont=tk.CTkFont(this.baseFontName,16)
        this.itemFont=tk.CTkFont(this.baseFontName,12)
    #END INTERFACE STYLES

    #WINDOW CONFIGURATION
        #Window Configuration:
        this.programTitle="Copier"
        this.title(f"{this.programTitle}")
        xSize,ySize=1024,768
        this.geometry(f"{xSize}x{ySize}")
        this.minsize(xSize,ySize)
        #this.deiconify()

        #Grid Layout:
        this.grid_rowconfigure(1,weight=1)
        this.grid_columnconfigure(0,weight=1)
    #END WINDOW CONFIGURATION

    #TOP TOOLBAR
        this.toolFrame=tk.CTkFrame(this,height=5)
        this.toolFrame.grid(row=0,columnspan=5,sticky="ew")
    #END TOP TOOLBAR

    #MAIN WINDOW
        this.mainFrame=tk.CTkFrame(this)
        this.mainFrame.grid(row=1,sticky="nesw",padx=(this.pad,this.pad/2),pady=this.pad/2)

        #Destination frame bar.
        this.destinationFrame=tk.CTkFrame(this.mainFrame,height=(buttonPad*1.5),width=this.winfo_screenwidth())
        this.destinationFrame.pack(side=tk.BOTTOM,padx=this.pad,pady=this.pad)

        this.labelDestination=tk.CTkLabel(this.destinationFrame,text="Destination Directory:",font=this.bodyFont)
        this.labelDestination.pack(side=tk.TOP,padx=this.pad,pady=this.pad)

        this.buttonDestination=tk.CTkButton(this.destinationFrame,text="Browse",font=this.buttonFont,command=this.setDestination)
        this.buttonDestination.pack(side=tk.RIGHT,padx=(0,this.pad),pady=this.pad)

        this.stringVarDestination=tk.StringVar(this.mainFrame,value="")
        this.stringVarDestination.trace_add("write",this.__setButtonStates)

        this.textboxDestination=tk.CTkEntry(this.destinationFrame,width=this.winfo_screenwidth(),textvariable=this.stringVarDestination)
        #this.textboxDestination.bind("write",this.__setButtonStates)
        this.textboxDestination.pack(side=tk.LEFT,padx=this.pad,pady=this.pad)

        #Item frame box.
        this.itemFrame=tk.CTkFrame(this.mainFrame,height=this.winfo_screenheight(),width=this.winfo_screenwidth())
        this.itemFrame.pack(side=tk.TOP,padx=this.pad,pady=(this.pad,0))

        this.labelItems=tk.CTkLabel(this.itemFrame,text="Source Directories/Files:",font=this.bodyFont)
        this.labelItems.pack(side=tk.TOP,padx=this.pad,pady=this.pad)

        #this.scrollBarHorizontal=tk.CTkScrollbar(this.itemFrame,orientation="horizontal")
        #this.scrollBarHorizontal.pack(side=tk.BOTTOM)

        this.scrollFrameItems=tk.CTkScrollableFrame(this.itemFrame,height=this.winfo_screenheight(),width=this.winfo_screenwidth())
        this.scrollFrameItems.pack(side=tk.BOTTOM,padx=this.pad/2,pady=(0,this.pad/2))

        #Tools frame:
        this.toolsFrame=tk.CTkFrame(this)
        this.toolsFrame.grid(row=1,column=3,sticky="nesw",padx=(this.pad/2,this.pad),pady=this.pad/2)
        #Tools label:
        #this.labelTools=tk.CTkLabel(this.toolsFrame,text="Client Tools",font=this.titleFont)
        #this.labelTools.grid(row=0)

        #Add folders Button:
        this.buttonAddFolders=tk.CTkButton(this.toolsFrame,text="Add Folder(s)",font=this.buttonFont,command=this.addFolders)
        this.buttonAddFolders.pack(side=tk.TOP,padx=this.pad,pady=(buttonPad,0))
        #Add files Button:
        this.buttonAddFiles=tk.CTkButton(this.toolsFrame,text="Add File(s)",font=this.buttonFont,command=this.addFiles)
        this.buttonAddFiles.pack(side=tk.TOP,padx=this.pad,pady=(this.pad,0))

        #Select all Button:
        this.buttonSelectAll=tk.CTkButton(this.toolsFrame,text="Select All",font=this.buttonFont,command=this.selectAll)
        this.buttonSelectAll.pack(side=tk.TOP,padx=this.pad,pady=(buttonPad,this.pad/2))
        #Select folders Button:
        this.buttonSelectFolders=tk.CTkButton(this.toolsFrame,text="Sel. Folder(s)",font=this.buttonFont,command=this.selectFolders)
        this.buttonSelectFolders.pack(side=tk.TOP,padx=this.pad,pady=this.pad/2)
        #Select files Button:
        this.buttonSelectFiles=tk.CTkButton(this.toolsFrame,text="Select File(s)",font=this.buttonFont,command=this.selectFiles)
        this.buttonSelectFiles.pack(side=tk.TOP,padx=this.pad,pady=this.pad/2)
        #Remove items Button:
        this.buttonRemoveItems=tk.CTkButton(this.toolsFrame,text="Remove Item(s)",font=this.buttonFont,command=this.removeItems)
        this.buttonRemoveItems.pack(side=tk.TOP,padx=this.pad,pady=(this.pad/2,buttonPad))

        #Start Job Button:
        this.buttonStart=tk.CTkButton(this.toolsFrame,height=74,text="Start Job",font=this.titleFont,command=this.startJob)
        this.buttonStart.pack(side=tk.BOTTOM,padx=this.pad,pady=(this.pad/2,buttonPad))
        #Job Type Selection:

        this.jobType=tk.CTkOptionMenu(this.toolsFrame,values=["Copy","Move","Mirror"],font=this.itemFont,command=this.setJobType)
        this.jobType.pack(side=tk.BOTTOM,padx=this.pad,pady=this.pad/2)
        this.labelJobType=tk.CTkLabel(this.toolsFrame,text="Job Type:",font=this.bodyFont)
        this.labelJobType.pack(side=tk.BOTTOM,padx=this.pad,pady=(this.pad/2,0))
        #Settings Button:
        this.buttonSettings=tk.CTkButton(this.toolsFrame,text="Job Settings",font=this.buttonFont,command=this.changeSettings)
        this.buttonSettings.pack(side=tk.BOTTOM,padx=this.pad,pady=(buttonPad,this.pad/2))

        #Load job Button:
        this.buttonLoadJob=tk.CTkButton(this.toolsFrame,text="Load Job",font=this.buttonFont,command=this.loadJob)
        this.buttonLoadJob.pack(side=tk.BOTTOM,padx=this.pad,pady=this.pad/2)

        #Save job Button:
        this.buttonSaveJob=tk.CTkButton(this.toolsFrame,text="Save Job",font=this.buttonFont,command=this.saveJob)
        this.buttonSaveJob.pack(side=tk.BOTTOM,padx=this.pad,pady=(0,this.pad/2))
    #END MAIN WINDOW

    #BOTTOM BAR
        this.bottomFrame=tk.CTkFrame(this,height=50)
        this.bottomFrame.grid(row=2,columnspan=5,sticky="ew")

        #Bottom bar elements:
        this.workingBar=tk.CTkProgressBar(this.bottomFrame,width=200,mode="determinate")
        this.workingBar.set(1)
        this.workingBar.pack(side=tk.LEFT,padx=this.pad,pady=this.pad)
        this.workStatus=tk.CTkLabel(this.bottomFrame,text="Idle",font=this.bodyFont)
        this.workStatus.pack(side=tk.LEFT,padx=this.pad,pady=this.pad)
        #this.copyright=tk.CTkLabel(this.bottomFrame,text=f"License provided by {author} (2023)",font=this.bodyFont)
        #this.copyright.place(relx=0.5,rely=0.5,anchor="center")
        this.versionLabel=tk.CTkLabel(this.bottomFrame,text=f"Version: {version}",font=this.bodyFont)
        this.versionLabel.pack(side=tk.RIGHT,padx=this.pad,pady=this.pad)

    #END BOTTOM BAR

    #EVENT HANDLERS
        this.bind("<FocusIn>",this.__focus)
        this.bind("<FocusOut>",this.__unfocus)
    #END EVENT HANDLERS
        this.__setButtonStates()
        this.__focus()
    #END def __init__

#TOOL BUTTON FUNCTIONS
    def setDestination(this) -> None:
        """
        Sets the copy destination for the copy program.
        """
        #Get the selected directory information.
        directory=tkfilebrowser.askopendirname()
        #If a directory was selected, put it into the destination entry box.
        if directory:
            this.__enableWorkingBar()

            this.__setDestination(directory)
            this.__setButtonStates()

            this.__disableWorkingBar()
    #END def setDestination

    def addFiles(this) -> None:
        """
        Opens a new window for selecting a set of files.
        """
        fileNames=tkfilebrowser.askopenfilenames(parent=this)
        if len(fileNames)>0:
            this.__enableWorkingBar()
            for file in fileNames:
                #print(f"Adding [{file} to files list.]")
                this.__items[1][file]='f' #'f' for File.
                #this.__addItem("File",file)

            this.__setItems()
            this.__disableWorkingBar()
    #END def addFiles
    def addFolders(this) -> None:
        """
        Opens a new window for selecting a set of folders.
        """
        folderNames=tkfilebrowser.askopendirnames(parent=this)
        if len(folderNames)>0:
            this.__enableWorkingBar()
            for folder in folderNames:
                #print(f"Adding [{folder} to folders list.]")
                this.__items[0][folder]="d" #'d' for Directory.
                #this.__addItem("Folder",folder)

            this.__setItems()
            this.__disableWorkingBar()
    #END def addFolders

    def selectAll(this) -> None:
        """
        Selects all items in the sources list.
        """
        this.__enableWorkingBar()
        selected,existing=0,0
        for item in this.scrollFrameItems.winfo_children():
            existing+=1
            selected+=item.winfo_children()[0].get()

        #print(f"{selected}, {existing}")
        if selected==existing:
            for item in this.scrollFrameItems.winfo_children():
                item.winfo_children()[0].deselect()
        else:
            for item in this.scrollFrameItems.winfo_children():
                item.winfo_children()[0].select()

        this.__setButtonStates() 
        this.__disableWorkingBar()
    #END def selectAll
    def selectFiles(this) -> None:
        """
        Selects all files in the sources list.
        """
        this.__enableWorkingBar()

        this.__selectItems("File")
        this.__setButtonStates()

        this.__disableWorkingBar()
    #END def selectFiles
    def selectFolders(this) -> None:
        """
        Selects all folders in the sources list.
        """
        this.__enableWorkingBar()

        this.__selectItems("Folder")
        this.__setButtonStates()

        this.__disableWorkingBar()
    #END def selectFolders
    def removeItems(this) -> None:
        """
        Removes selected items from the sources list.
        """
        this.__enableWorkingBar()

        this.__removeItems()
        this.__setButtonStates()
        
        this.__disableWorkingBar()
    #END def removeItems

    def saveJob(this) -> None:
        fileTypeList=[
            ["Job Files","*.job.json"]
        ]
        filterList=[]
        for option in fileTypeList:
            filterList.append((f"{option[0]} ({option[1]})",f"{option[1]}"))
        fileTarget=tkfilebrowser.asksaveasfilename(this,defaultext=".job.json",filetypes=fileTypeList,okbuttontext="Save")

        if fileTarget:
            this.__enableWorkingBar()
            jsonData={}
            for i,v in enumerate(this.__items):
                jsonData[i]=v
            jsonData["destination"]=this.textboxDestination.get()
            #jsonData["copyType"]=this.jobType.get()
            jsonData["options"]=this.options
            with open(fileTarget,"w") as file:
                json.dump(jsonData,file)
            this.__disableWorkingBar()
    #END def saveJob
    def loadJob(this) -> None:
        fileTypeList=[
            ["Job Files","*.job.json"]
        ]
        filterList=[]

        for option in fileTypeList:
            filterList.append((f"{option[0]} ({option[1]})",f"{option[1]}"))
        jobFile=tkfilebrowser.askopenfilename(this,filetypes=filterList)

        if jobFile:
            this.__enableWorkingBar()
            data:dict
            with open(jobFile,"r") as file:
                data=json.load(file)
            for index in list(data.keys())[0:2]:
                this.__items[int(index)]=data[index]
            this.__setDestination(data.get("destination","<NO DESTINATION>"))
            #this.jobType.set(data.get("copyType","Copy"))
            jobFileOptions=data.get("options",{})
            for key in jobFileOptions.keys():
                this.options[key]=jobFileOptions[key]
            del data
            this.__setItems()
            this.__disableWorkingBar()
    #END def loadJob

    def changeSettings(this) -> None:
        if this.toplevel is None or not this.toplevel.winfo_exists():
            this.__enableWorkingBar()
            this.toplevel=OptionsWindow(this)
            this.__disableWorkingBar()

        #this.toplevel.focus()
    #END def changeSettings
    def setJobType(this) -> None:
        this.options["job-type"]=this.jobType.get()
    def startJob(this) -> None:
        if this.toplevel is None or not this.toplevel.winfo_exists():
            this.__enableWorkingBar()
            this.toplevel=JobActivity(this)
            this.__disableWorkingBar()
    #END def startJob
#END TOOL BUTTON FUNCTIONS

#INTERFACE FUNCTIONS:
    def __setButtonStates(this,*args) -> None:
        """
        Sets the usability states of all buttons in the interface.
        """
        enable,disable="normal","disabled"

        folderCount,fileCount=len(this.__items[0]),len(this.__items[1])
        listSize=folderCount+fileCount+len(this.__items[2])

        destinationExists=os.path.exists(this.textboxDestination.get())

        if listSize>0:
            this.buttonSelectAll.configure(state=enable)
            this.buttonRemoveItems.configure(state=enable)
        else:
            this.buttonSelectAll.configure(state=disable)
            this.buttonRemoveItems.configure(state=disable)

        if folderCount>0:
            this.buttonSelectFolders.configure(state=enable)
        else:
            this.buttonSelectFolders.configure(state=disable)

        if fileCount>0:
            this.buttonSelectFiles.configure(state=enable)
        else:
            this.buttonSelectFiles.configure(state=disable)

        if listSize>0 and destinationExists:
            this.buttonStart.configure(state=enable)
        else:
            this.buttonStart.configure(state=disable)

        item:tk.CTkFrame
        enableCheck=False
        for item in this.scrollFrameItems.winfo_children():
            if item.winfo_children()[0].get()>0:
                enableCheck=True
                break
        if enableCheck:
            this.buttonRemoveItems.configure(state=enable)
        else:
            this.buttonRemoveItems.configure(state=disable)
    #END def __setButtonStates

    def __selectItems(this,term="TYPE-ERROR") -> None:
        """
        Selects the items that match the given checkbox label 'term'.
        """
        selected,existing=0,0
        indexes=[]
        #Count and get indexes of items matching the 'term'.
        for i,item in enumerate(this.scrollFrameItems.winfo_children()):
            if item.winfo_children()[0].cget("text")==f"{term}":
                existing+=1
                selected+=item.winfo_children()[0].get()
                indexes.append(i)

        if selected>=existing and existing > 0:
            for index in indexes:
                this.scrollFrameItems.winfo_children()[index].winfo_children()[0].deselect()
        else:
            for index in indexes:
                this.scrollFrameItems.winfo_children()[index].winfo_children()[0].select()
    #END def __selectItems

    def __setItems(this) -> None:
        """
        Replace the items listed in the GUI with the source targets in memory.
        """
        #Erase GUI list.
        for item in this.scrollFrameItems.winfo_children():
            item.destroy()

        #this.__items={}
        for i,types in enumerate(this.__items):
            #sortedItems=sorted(types.keys())
            for item in sorted(types.keys()):
                #this.__items[element]=key
                this.__addItem(this.__types.get(i,"TYPE-ERROR"),item)
        this.__setButtonStates()
    #END def __setItems

    def __setDestination(this,destination="") -> None:
        this.textboxDestination.delete(0,len(this.textboxDestination.get()))
        this.textboxDestination.insert(0,destination)
    #END def __setDestination

    def __addItem(this,type="TYPE-ERROR",name="terst:NAME") -> None:
        """
        Adds an item to the GUI and the job queue.
        """
        rootFrame=tk.CTkFrame(this.scrollFrameItems,width=this.winfo_screenwidth(),fg_color=this.itemFrame.cget("fg_color"))
        checkboxSelect=tk.CTkCheckBox(rootFrame,text=f"{type}",font=this.buttonFont,command=this.__setButtonStates)
        #checkboxSelect.event_add()
        fileName=name.replace("\\","/").split("/")[-1]
        labelFileName=tk.CTkLabel(rootFrame,text=f"{fileName}\t",font=this.buttonFont)
        labelTargetName=tk.CTkLabel(rootFrame,text=f"{name}",font=this.buttonFont)
        whitespace=tk.CTkFrame(rootFrame,width=this.winfo_screenwidth(),height=1,fg_color=rootFrame.cget("fg_color"))


        rootFrame.pack(side=tk.TOP,anchor="nw",padx=this.pad,pady=(this.pad,0))
        childrenCount=len(rootFrame.winfo_children())
        padxConfig=(this.pad,0)
        child : tk.CTkBaseClass
        for i,child in enumerate(rootFrame.winfo_children()):
            if (i+1)==childrenCount:
                padxConfig=this.pad

            child.grid(row=0,column=i,sticky="e",padx=padxConfig,pady=this.pad)
    #END def addItem

    def __removeItems(this) -> None:
        """
        Removes an item from the GUI and the job queue.
        """
        for item in this.scrollFrameItems.winfo_children():
            if item.winfo_children()[0].get():
                type=dictValFromKey(item.winfo_children()[0].cget("text"),this.__types,2)
                del this.__items[type][item.winfo_children()[2].cget("text")]
                item.destroy()
    #END def __removeItems
#END INTERFACE FUNCTIONS

#WORKING BAR FUNCTIONS:
    def __enableWorkingBar(this) -> None:
        """
        Sets the working bar to its 'working' state.
        """
        this.workStatus.configure(text="Working")
        this.workingBar.configure(mode="indeterminate")
        this.workingBar.start()
        this.__activeWorkingBar=True
    #END def __enableWorkingBar
    def __disableWorkingBar(this) -> None:
        """
        Sets the working bar to its 'idle' state.
        """
        this.workStatus.configure(text="Idle")
        this.workingBar.configure(mode="determinate")
        this.workingBar.stop()
        this.__activeWorkingBar=False
    #END def __disableWorkingBar
    def __toggleWorkingBar(this) -> None:
        """
        Switches the working bar to its opposite state.
        """
        if this.__activeWorkingBar:
            this.__disableWorkingBar()
        else:
            this.__enableWorkingBar()
    #END def __toggleWorkingBar
#END WORKING BAR FUNCTIONS

#FOCUS FUNCTIONS
    def __focus(this,*args) -> None:
        this.toolFrame.configure(fg_color=("white","black"),border_color=("white","black"))
        this.bottomFrame.configure(fg_color=("white","black"),border_color=("white","black"))
    #END def __onFocus
    def __unfocus(this,*args) -> None:
        this.toolFrame.configure(fg_color=this.mainFrame.cget("fg_color"),border_color=this.mainFrame.cget("border_color"))
        this.bottomFrame.configure(fg_color=this.mainFrame.cget("fg_color"),border_color=this.mainFrame.cget("border_color"))
    #END def __unfocus
#END FOCUS FUNCTIONS
#END class Window

class OptionsWindow(tk.CTkToplevel):
    """
    An external window allowing for the modification of advanced parameters for this program.
    """
    __fileConflictions = {
        "Do nothing.":0,
        "Overwrite destination file.":1,
        "Overwrite oldest file.":2
    }

    #__options = {}

    def __init__(this,parent:Window,*args, **kwargs) -> None:
        super().__init__(*args,**kwargs)

        this.__master=parent

        this.title(f"{parent.programTitle} - Options")
        this.dimensions={
            "width":768,
            "height":512#/1.85
        }
        this.geometry(f"{this.dimensions['width']}x{this.dimensions['height']}")
        this.grid_rowconfigure(1,weight=1)
        this.grid_columnconfigure(0,weight=1)

        this.resizable(width=False,height=False)
        this.grab_set()

        this.topFrame=tk.CTkFrame(this,height=5)
        this.topFrame.grid(row=0,column=0,sticky="ew")

        this.mainFrame=tk.CTkFrame(this)
        this.mainFrame.grid_rowconfigure(1,weight=1)
        this.mainFrame.grid_columnconfigure(1,weight=1)
        this.mainFrame.grid(row=1,column=0,sticky="nsew",padx=parent.pad,pady=parent.pad)

        this.loggingOptionsFrame=tk.CTkFrame(this.mainFrame)
        this.loggingOptionsFrame.grid(row=0,column=0,sticky="nsew",padx=parent.pad,pady=parent.pad)
        this.labelLoggingOptions=tk.CTkLabel(this.loggingOptionsFrame,text="Logging Options",font=parent.bodyFont)
        this.checkboxEnableLogging=tk.CTkCheckBox(this.loggingOptionsFrame,text="Enable Job Logging",font=parent.itemFont,command=this.__setButtonStates)
        this.labelLoggingHashTypes=tk.CTkLabel(this.loggingOptionsFrame,text="Logging Hash Type:",font=parent.itemFont)
        this.optionsLoggingHashType=tk.CTkOptionMenu(this.loggingOptionsFrame,values=["None","MD5","Sha256","Sha512","SipHash"])
        this.labelLogDirectory=tk.CTkLabel(this.loggingOptionsFrame,text="Log file location:",font=parent.itemFont)
        this.setLogDirectory=tk.CTkFrame(this.loggingOptionsFrame)
        this.entryLogDirectory=tk.CTkEntry(this.setLogDirectory,placeholder_text="Use <destination> dir.",width=this.dimensions["width"]/2.5)
        this.entryLogDirectory.pack(side=tk.LEFT)
        this.buttonBrowseLogDirectory=tk.CTkButton(this.setLogDirectory,text="Browse",width=70,font=parent.itemFont,command=this.__setLogDestination)
        this.buttonBrowseLogDirectory.pack(side=tk.LEFT)
        this.labelDirectoryNotice=tk.CTkLabel(this.loggingOptionsFrame,text="If path above is empty or invalid, log file will be saved to job <destination>.",font=parent.itemFont,wraplength=(this.dimensions["width"]/2.5))

        packChildren(this.loggingOptionsFrame,padding={0:parent.pad,1:parent.pad})

        this.conflictingFrame=tk.CTkFrame(this.mainFrame)
        this.conflictingFrame.grid(row=0,column=1,sticky="nsew",padx=(0,parent.pad),pady=parent.pad)
        this.labelConflictingTitle=tk.CTkLabel(this.conflictingFrame,text="Confliction Settings",font=parent.bodyFont)
        this.labelConflictingFile=tk.CTkLabel(this.conflictingFrame,text="If file exists in both <source> & <destination>:",font=parent.itemFont)
        this.optionsConflictingFile=tk.CTkOptionMenu(this.conflictingFrame,width=this.conflictingFrame.cget("width"),values=[value for value in this.
        __fileConflictions.keys()])
        this.labelCannotChangeConflict=tk.CTkLabel(this.conflictingFrame,text="",font=parent.itemFont,text_color="red")

        packChildren(this.conflictingFrame,padding={0:parent.pad,1:parent.pad})

        this.threadOptionsFrame=tk.CTkFrame(this.mainFrame)
        this.threadOptionsFrame.grid(row=1,column=0,sticky="nsew",padx=parent.pad,pady=(0,parent.pad))
        this.labelThreadOptions=tk.CTkLabel(this.threadOptionsFrame,text="Multi-Thread Settings",font=parent.bodyFont)
        this.threadSliderFrame=tk.CTkFrame(this.threadOptionsFrame,fg_color=this.threadOptionsFrame.cget("fg_color"))
        this.labelThreadSlider=tk.CTkLabel(this.threadSliderFrame,text="Amount of threads: ",font=parent.itemFont)
        this.labelThreadSlider.pack(side=tk.LEFT,padx=parent.pad,pady=(0,parent.pad))
        #this.threadCountFrame=tk.CTkFrame(this.threadSliderFrame,fg_color=this.mainFrame.cget("fg_color"))
        #this.threadCountFrame.pack(side=tk.LEFT)
        this.optionThreadCount=tk.CTkOptionMenu(this.threadSliderFrame,values=["1","2","4","8","12","16"],width=60,font=parent.itemFont,command=this.__setThreadState)
        this.optionThreadCount.pack(side=tk.LEFT,padx=(0,parent.pad),pady=(0,parent.pad))
        this.sliderThreadSetting=tk.CTkSlider(this.threadOptionsFrame,from_=1,to=16,number_of_steps=15,command=this.__setButtonStates)

        packChildren(this.threadOptionsFrame,padding={0:parent.pad,1:parent.pad})

        this.bottomOptionsFrame=tk.CTkFrame(this.mainFrame)
        this.bottomOptionsFrame.grid(row=2,column=0,columnspan=2,sticky="nsew",padx=parent.pad,pady=(0,parent.pad))
        this.buttonLoadDefault=tk.CTkButton(this.bottomOptionsFrame,text="Load Default",font=parent.buttonFont,command=this.__loadDefaultOptions)
        this.buttonLoadDefault.pack(side=tk.LEFT,padx=parent.pad,pady=parent.pad)
        this.buttonCancelChanges=tk.CTkButton(this.bottomOptionsFrame,text="Cancel",font=parent.buttonFont,command=this.destroy)
        this.buttonCancelChanges.pack(side=tk.RIGHT,padx=parent.pad,pady=parent.pad)
        this.buttonSaveChanges=tk.CTkButton(this.bottomOptionsFrame,text="Save",font=parent.buttonFont,command=this.__saveOptions)
        this.buttonSaveChanges.pack(side=tk.RIGHT,padx=parent.pad,pady=parent.pad)

        this.bottomFrame=tk.CTkFrame(this,height=5)
        this.bottomFrame.grid(row=3,column=0,sticky="ew")

        this.bind("<FocusIn>",this.__focus)
        this.bind("<FocusOut>",this.__unfocus)

        this.__loadButtonStates()
        this.__setButtonStates()
    #END def __init__
    def __loadButtonStates(this,*args) -> None:
        """
        Sets the states of the buttons to match the currently-loaded options.
        """
        if this.__master.options.get("log",False):
            this.checkboxEnableLogging.select()
        else:
            this.checkboxEnableLogging.deselect()
        this.optionsLoggingHashType.set(this.__master.options.get("logType","None"))
        this.entryLogDirectory.insert(0,this.__master.options.get("logDest",""))

        this.optionsConflictingFile.set(dictValFromKey(this.__master.options.get("fileConflictMode",0),this.__fileConflictions))
        if this.__master.jobType.get() not in ["Copy","Mirror"]: #If the job type is neither of the specified settings...
            this.optionsConflictingFile.configure(state="disabled")
            this.labelCannotChangeConflict.configure(text="Setting ignored due to incompatible job type!")

        this.sliderThreadSetting.set(this.__master.options.get("threads",4))
    #END def __loadButtonStates

    def __setButtonStates(this,*args) -> None:
        """
        Sets the usability states of all buttons in the interface.
        """
        enable,disable="normal","disabled"

        if bool(this.checkboxEnableLogging.get()):
            this.optionsLoggingHashType.configure(state=enable)
            this.entryLogDirectory.configure(state=enable)
            this.buttonBrowseLogDirectory.configure(state=enable)
        else:
            this.optionsLoggingHashType.configure(state=disable)
            this.entryLogDirectory.configure(state=disable)
            this.buttonBrowseLogDirectory.configure(state=disable)

        this.optionThreadCount.set(str(int(this.sliderThreadSetting.get())))#configure(text=str(int(this.sliderThreadSetting.get())))
    #END def __setButtonStates

    def __setThreadState(this,*args) -> None:
        this.sliderThreadSetting.set(int(this.optionThreadCount.get()))
    #END def __setThreadState

    def __setLogDestination(this,*args) -> None:
        logFileType=["Comma-Separated Values file",".csv"]
        destination=tkfilebrowser.asksaveasfilename(this,title="Save Log As",filetypes=[(f"{logFileType[0]} ({logFileType[1]})",f"*{logFileType[1]}")],defaultext=logFileType[1])

        if destination:
            this.entryLogDirectory.delete(0,len(this.entryLogDirectory.get()))
            this.entryLogDirectory.insert(0,destination)

        this.grab_set()
    #END def __setLogDestination
    def __saveOptions(this,*args) -> None:
        """
        Saves selected options to the parent's memory, then closes the window.
        """
        if this.checkboxEnableLogging.get():
            this.__master.options["log"]=True
            this.__master.options["logType"]=this.optionsLoggingHashType.get()
            logDir=this.entryLogDirectory.get()
            if logDir:
                this.__master.options["logDest"]=logDir
        else:
            this.__master.options["log"]=False

        this.__master.options["fileConflictMode"]=this.__fileConflictions.get(this.optionsConflictingFile.get(),0)

        this.__master.options["threads"]=int(this.sliderThreadSetting.get())

        this.destroy()
    #END def __saveOptions

    def __loadDefaultOptions(this,*args) -> None:
        """
        Resets this settings menu with the default options.  Does NOT reset the user's previously-saved options.
        """
        temp=this.__master.options.copy()

        this.__master.options=this.__master.defaultOptions.copy()
        this.__loadButtonStates()
        this.__master.options=temp.copy()

        del temp
    #END def __loadDefaultOptions

    def __focus(this,*args) -> None:
        this.topFrame.configure(fg_color=("white","black"))
        this.bottomFrame.configure(fg_color=("white","black"))
    #END def __focus
    def __unfocus(this,*args) -> None:
        this.topFrame.configure(fg_color=this.mainFrame.cget("fg_color"))
        this.bottomFrame.configure(fg_color=this.mainFrame.cget("fg_color"))
    #END def __unfocus
#END class OptionsWindow



class JobActivity(tk.CTkToplevel):
    """
    A class containing the popup window displaying the job activity progress.

    When a job begins, this window displays each thread's progress & the overall job progress.
    """

    __master : Window
    __threads : Manager

    threadBars : list[tk.CTkFrame]

    filesFinished=0
    filesInJob=0

    #avgWriteSpeed=0

    def __init__(this,parent:Window,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        this.__master=parent

        this.title(f"{parent.programTitle} - Job Progress")

        this.dimensions={
            "width":512,
            "height":768
        }

        this.geometry(f"{this.dimensions['width']}x{this.dimensions['height']}")

        this.grid_rowconfigure(1,weight=1)
        this.grid_columnconfigure(0,weight=1)

        this.resizable(width=False,height=True)
        this.grab_set()

        this.topFrame=tk.CTkFrame(this,height=5)
        this.topFrame.grid(row=0,column=0,sticky="ew")

        this.mainFrame=tk.CTkFrame(this)
        this.mainFrame.grid_rowconfigure(1,weight=1)
        this.mainFrame.grid_columnconfigure(0,weight=1)
        this.mainFrame.grid(row=1,column=0,sticky="nsew",padx=parent.pad,pady=parent.pad)

        this.totalProgressFrame=tk.CTkFrame(this.mainFrame)
        this.totalProgressFrame.grid(row=0,column=0,sticky="nsew",padx=parent.pad,pady=(parent.pad,0))
        this.labelTotalProgress=tk.CTkLabel(this.totalProgressFrame,text="Total Progress",font=parent.bodyFont)
        this.labelTotalProgress.pack(side=tk.TOP,padx=parent.pad,pady=parent.pad)
        this.totalProgressBarFrame=tk.CTkFrame(this.totalProgressFrame)
        this.totalProgressBarFrame.pack(side=tk.BOTTOM,padx=parent.pad,pady=(0,parent.pad),fill="x")
        #print(this.totalProgressBarFrame.cget("width"))#
        this.labelProgressDestination=tk.CTkLabel(this.totalProgressBarFrame,text=f"Destination:\n{parent.textboxDestination.get()}",font=parent.itemFont,wraplength=this.dimensions["width"]-50)
        this.labelProgressDestination.pack(side=tk.TOP,padx=parent.pad,pady=parent.pad)
        this.barTotalProgress=tk.CTkProgressBar(this.totalProgressBarFrame,mode="indeterminate",width=this.totalProgressBarFrame.cget("width"))
        this.barTotalProgress.pack(side=tk.TOP,padx=parent.pad,pady=parent.pad,fill="x")
        #print(this.totalProgressBarFrame.cget("width"))#
        this.barTotalProgress.start()
        this.labelFileCount=tk.CTkLabel(this.totalProgressBarFrame,text=f"Completed/Total Files: [{this.filesFinished}/{this.filesInJob}]",font=parent.itemFont)
        this.labelFileCount.pack(side=tk.TOP,padx=parent.pad,pady=0)
        #this.labelAvgSpeed=tk.CTkLabel(this.totalProgressBarFrame,text=f"Write Speed (kB/s): {this.avgWriteSpeed}",font=parent.itemFont)
        #this.labelAvgSpeed.pack(side=tk.TOP,padx=parent.pad,pady=0)

        this.threadProgressFrame=tk.CTkFrame(this.mainFrame)
        this.threadProgressFrame.grid(row=1,column=0,sticky="nsew",padx=parent.pad,pady=parent.pad)
        this.labelThreadProgress=tk.CTkLabel(this.threadProgressFrame,text="Thread Progress",font=parent.bodyFont)
        this.labelThreadProgress.pack(side=tk.TOP,padx=parent.pad,pady=parent.pad)
        this.scrollThreadProgress=tk.CTkScrollableFrame(this.threadProgressFrame,fg_color=this.threadProgressFrame.cget("fg_color"))
        this.scrollThreadProgress.pack(side=tk.TOP,padx=parent.pad,pady=(0,parent.pad),fill="both",expand=1)

        this.threadBars=[]
        for threadNum in range(this.__master.options["threads"]):
            #threadFrame=tk.CTkFrame(this.scrollThreadProgress)

            #Vars
            #threadStatus=tk.StringVar(threadFrame,"Idle")
            #threadTarget=tk.StringVar(threadFrame,value="None")
            #threadWritten=tk.IntVar(threadFrame,0)
            #threadFileSize=tk.IntVar(threadFrame,1)
            #threadProgress=tk.DoubleVar(threadFrame,round((threadWritten.get()/threadFileSize.get())*10000)/100)

            #Elements
            #threadLabel=tk.CTkLabel(threadFrame,text=f"Thread #{threadNum}\nTarget:\n{threadTarget.get()}",font=parent.itemFont,wraplength=this.dimensions["width"]-50)
            #threadProgressBar=tk.CTkProgressBar(threadFrame,#variable=threadProgress,width=this.mainFrame.cget("width"))
            #threadProgressLabel=tk.CTkLabel(threadFrame,text=f"Progress: {threadProgress.get()}%\n{threadWritten.get()} B/{threadFileSize.get()} B")
            #threadProgressBar.set(threadProgress.get())
            #this.packChildren(threadFrame,fill="x")

            this.threadBars.append(IndividualThreadWidget(this.scrollThreadProgress,parent,this.dimensions,threadNum,fill="x"))
        packChildren(this.scrollThreadProgress,padding={0:parent.pad,1:parent.pad},fill="both")

        this.bottomFrame=tk.CTkFrame(this,height=5)
        this.bottomFrame.grid(row=2,column=0,sticky="ew")

        this.bind("<FocusIn>",this.__focus)
        this.bind("<FocusOut>",this.__unfocus)
    #END def __init__

    #END def __init__
    def __focus(this,*args) -> None:
        this.topFrame.configure(fg_color=("white","black"))
        this.bottomFrame.configure(fg_color=("white","black"))
    #END def __focus
    def __unfocus(this,*args) -> None:
        this.topFrame.configure(fg_color=this.mainFrame.cget("fg_color"))
        this.bottomFrame.configure(fg_color=this.mainFrame.cget("fg_color"))
    #END def __unfocus
#END class JobActivity

def main() -> None:
    tk.set_appearance_mode("system") 
    tk.set_default_color_theme("green")
    window=Window()
    window.mainloop()
#END def main

if __name__=="__main__":
    main()
