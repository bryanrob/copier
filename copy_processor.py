# <INSERT LICENSING CLAUSE HERE>

from threading import Thread,ThreadError,Lock
from queue import Queue
#from interface_elements import IndividualThreadWidget
from interface_elements import packChildren
import logging,os,shutil,itertools,customtkinter as tk
from typing import NewType

from dataclasses import dataclass

#MethodSTR = NewType("MethodSTR",str,default="copy")


class IndividualThreadWidget():
    """
    An encapsulation of a thread's progress being displayed on the GUI.

    Allows for easier interaction between the interface and the worker thread.
    """
    __id:int
    threadStatus:tk.StringVar
    threadTarget:tk.StringVar
    threadWritten:tk.IntVar
    threadFileSize:tk.IntVar
    __threadProgress:tk.DoubleVar

    __threadLabel:tk.CTkLabel
    __threadProgressBar:tk.CTkProgressBar
    __threadProgressLabel:tk.CTkLabel

    def __init__(this,parent:tk.CTkBaseClass,window,dimensions:dict,id:int,*args,**kargs) -> None:
        #super().__init__(*args,**kargs)

        this.threadFrame=tk.CTkFrame(parent)
        this.__id=id

        #Vars
        this.threadStatus=tk.StringVar(this.threadFrame,"Idle")
        this.threadTarget=tk.StringVar(this.threadFrame,value="None")
        this.threadWritten=tk.IntVar(this.threadFrame,0)
        this.threadFileSize=tk.IntVar(this.threadFrame,1)
        this.__threadProgress=tk.DoubleVar(this.threadFrame,0.0)

        #Elements
        this.__threadLabel=tk.CTkLabel(this.threadFrame,font=window.itemFont,wraplength=dimensions["width"]-50)
        this.__threadProgressBar=tk.CTkProgressBar(this.threadFrame,width=parent.cget("width"))
        this.__threadProgressLabel=tk.CTkLabel(this.threadFrame,font=window.itemFont)
        #this.__threadProgressBar.set(this.__threadProgress.get())
        this.showProgress()
        packChildren(this.threadFrame,{0:window.pad,1:window.pad},*args,**kargs)
    #END def __init__

    #def generateThreadLabel(this) -> None:
        
    #END def generateThreadLabel

    def showProgress(this) -> None:
        this.__threadLabel.configure(text=f"Thread # {this.__id}\nTarget:\n{this.threadTarget.get()}")

        this.__threadProgress.set(round((this.threadWritten.get()/this.threadFileSize.get())*10000)/100)

        this.__threadProgressLabel.configure(text=f"Progress: {this.__threadProgress.get()}%\n{this.threadWritten.get()} B/{this.threadFileSize.get()} B")
        this.__threadProgressBar.set(this.__threadProgress.get())
    #END def showProgress
#END class IndividualThreadWidget 

@dataclass
class Task:
    """
    The job task for a given 'source' file going to a specified 'destination'.  The job type is specified as the 'method' string.
    """
    source : str
    destination : str
    method: str
#END class Task

class Hasher:
    """
    Used to generate a specific hash output of a given file.
    """
    def __init__(self,hashType:str):
        pass
    #END def __init__


#END class Hasher

class Worker(Thread):
    __isActive : bool
    __id = itertools.count()
    __lock : Lock
    __queuePointer : Queue
    __currentTask : Task
    __filePath : str
    __fileSize : int
    __logDir : str
    __hasher : Hasher
    __conflictMode : int
    __interfaceObjects : IndividualThreadWidget
    #Object indexes:
    #   [0] = status : StringVar
    #   [1] = target : StringVar
    #   [2] = writtenBytes : IntVar
    #   [3] = targetSize : IntVar
    #   [4] = threadLabel : CTKLabel
    #   [5] = progressBar : CTKProgressBar
    #   [6] = progressLabel : CTKLabel


    def __init__(self,lock:Lock,queuePointer:Queue,interfacePointer:IndividualThreadWidget,hasher:Hasher,logDir="",conflictMode=0):
        self.__isActive=False
        self.__lock=lock
        self.__queuePointer=queuePointer
        self.__interfaceObjects=interfacePointer
        self.__logDir=logDir
        self.__hasher=hasher
        self.__conflictMode=conflictMode

        self.__currentTask=None
    #END def __init__

    def __updateInterface(self):
        #interface=self.__interfaceObjects.winfo_children()
        #interface[0],isActive=self.getStatus()
        self.__interfaceObjects.threadStatus,isActive=self.getStatus()
        if isActive:
            pass
            #writtenBytes = size of target's copy.
            #
    #END def __updateInterface

    def getStatus(self) -> str:
        if self.__currentTask!=None:
            self.__isActive=True
            return "Working"
        else:
            self.__isActive=False
            return "Idle"
        #return "Working",True if self.__currentTask!=None else "Idle",False
    #END def getStatus
#END class Worker

class Manager:
    """
    The thread manager for the file replication system.
    """
    __threads : list[Worker]
    __interfaceObjects : list[IndividualThreadWidget]
    __queue : Queue
    __Lock = Lock()

    def __init__(self,interfacePointers:list[IndividualThreadWidget],options:dict,*args):
        self.__queue=Queue(maxsize=250000)
        
        self.__threads=[Worker(self.__queue)]*options.get("threads",4)

        if options.get("log",False):
            hashType=Hasher(options.get("logType","None"))
            logDestination=options.get("logDest","")
        
        fileConflictMode=options.get("fileConflictMode",0)

        for i in range(options.get("threads",4)):
            self.__threads[i]=Worker(self.__Lock,self.__queue,interfacePointers[i],hashType,logDestination,fileConflictMode)
        

        

    #END def __init__
#END class Manager