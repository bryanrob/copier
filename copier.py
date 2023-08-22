from threading import Thread,Lock
from queue import Queue
#from dataclasses import dataclass
import os,shutil

#@dataclass
class Task:
    """
    An encapsulation of a 'Task' that a 'CopierThread' will need to process from the queue filled within the 'CopierManager' class.
    """
    source : os.DirEntry #The path to the source file.
    destination : os.DirEntry #The path to the destination directory.
    jobType : str #The action to take with this task, i.e. "Copy", "Move" or "Delete".

    def __init__(self,source:os.DirEntry,destination:os.DirEntry,jobType:str):
        self.source=source
        self.destination=destination
        self.jobType=jobType
    #END def __init__
#END class Task

class CopierThread(Thread):
    """
    An individual thread for the Copier process.  Pulls a Task from the queue to process, applying the provided options flags as necessary.
    """
    __queuePointer : Queue[Task]
    __currentTask : Task
    __lockPointer : Lock
    __options : dict

    def __init__(self,queuePointer:Queue[Task],lockPointer:Lock,options:dict) -> None:
        super().__init__()
        self.__queuePointer=queuePointer
        self.__lockPointer=lockPointer
        self.__options=options
    #END def __init__

    def run(self) -> None:
        while self.__queuePointer.not_empty:
            self.__currentTask=self.__queuePointer.get()
            
            destFile:os.DirEntry
            destFile=os.path.normpath(f"{self.__currentTask.destination}/{self.__currentTask.source.name}")

            #TODO:
            #Check if file confliction exists.  If so, apply the appropriate response.
            execute=True
            if os.path.exists(destFile):
                collisionMode=self.__options.get("fileConflictMode",0)
                if collisionMode==0:
                    execute=False
                elif collisionMode==2:
                    if self.__currentTask.source.stat().st_mtime>=destFile.stat().st_mtime:
                        execute=False
            if execute:
                #Check copy mode flag and apply the appropriate responses according to the task type and the hashing flag(s).
                if self.__currentTask.jobType=="Copy" or self.__currentTask.jobType=="Move":
                    #If mode is copy, copy the item.
                    #If mode is move, copy the item, then add a new task to the queue to delete the source file.
                    shutil.copy2(self.__currentTask.source,self.__currentTask.destination)
                    if self.__currentTask.jobType=="Move":
                        self.__currentTask.destination=destFile
                        self.__currentTask.jobType="Delete"
                        self.__queuePointer.put(self.__currentTask)
                elif self.__currentTask.jobType=="Delete":
                    #If mode is delete, delete the source file.
                    os.remove(self.__currentTask.source)
            self.__queuePointer.task_done()
    #END def run
#END class CopierThread

class CopierManager:
    """
    The manager of each thread; inserts newly-found tasks into the task queue as it scans the given directories for files.
    """
    __queue : Queue[Task]
    __threads : list[CopierThread]
    __Lock : Lock
    __options : dict

    def __init__(self,options:dict):
        self.__options=options
        self.__queue=Queue(maxsize=options.get("queue-maximum",250000))
        self.__Lock=Lock()

        self.__threads=[CopierThread(self.__queue,self.__Lock,options) for thread in range(options.get("threads",1))]
    #END def __init__

    def startJob(self,sources:list[str],destination:str):
        for thread in self.__threads:
            thread.daemon=True
            thread.start()

        for source in sources:
            for task in self.__listDirs(os.path.abspath(source),os.path.abspath(destination)):
                self.__queue.put(task)

        self.__queue.join()
    #END def startJob

    def __listDirs(self,source:os.DirEntry,destination:os.DirEntry) -> Task:
        #print(f"Source: {str(source)}\nDest: {str(destination)}")
        for directory in os.scandir(source):
            if directory.is_dir():
                newDest=os.path.join(destination,os.path.basename(directory))
                try:
                    os.makedirs(newDest)
                except OSError:
                    pass
                finally:
                    yield from self.__listDirs(directory,newDest)
            else:
                yield Task(directory,destination,self.__options.get("job-type","Copy"))
    #END def listDirs
#END class CopierManager

def main():
    """
    Starts the CLI version of the Copier program.
    """
    import sys,json
    from ast import literal_eval

    cmdArgs=sys.argv[1:]

    options:dict
    options={"cli":True}
    with open("./versionData/defaultOptions.json","r") as file:
        options=json.load(file)
    #defaultOptions=options.copy()

    #noShortenedFlags={
    #    "--log":"log"
    #}

    flags={
        "--sources":"sources",
        "--destination":"destination",
        "--job-type":"job-type",
        "--log-destination":"logDest",
        "--hash-algorithm":"logType",
        "--thread-count":"threads",
        "--conflict":"fileConflictMode"
    }

    shortendedFlags={f"-{flag[2]}":flag for flag in flags}

    for arg in cmdArgs:
        splitArg=arg.split(":",1)
        if len(splitArg)!=2:
            print(splitArg)
            improperArg(arg)
        
        flag,param=splitArg[0],splitArg[1]

        if flag in shortendedFlags.keys():
            actualFlag=flags[shortendedFlags[flag]]
        elif flag in flags.keys():
            actualFlag=flags[flag]
        #elif flag in noShortenedFlags.keys():
        #    actualFlag=noShortenedFlags[flag]
        else:
            improperArg(arg)

        if actualFlag=="sources": #Convert the string-formatted array into a literal array.
            param=literal_eval(param)
        elif actualFlag=="logDest" or actualFlag=="logType":
            options["log"]=True

        options[actualFlag]=param
    #print(options)

    manager=CopierManager(options)
    manager.startJob(options["sources"],options["destination"])
#END def main

def improperArg(arg:str) -> None:
    import sys
    print(f"FLAG ERROR: Unknown flag near: {arg}")
    sys.exit(1)
#END def improperArg

if __name__=="__main__":
    main()
