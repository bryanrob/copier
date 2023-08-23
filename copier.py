from threading import Thread,Lock
from queue import Queue
import os,shutil,sqlite3

#@dataclass
class Task:
    """
    An encapsulation of a `Task` that a `CopierThread` will need to process from the queue filled within the `CopierManager` class.
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
    An individual thread for the Copier process.  Pulls a `Task` from the queue to process, applying the provided options flags as necessary.
    """
    __continue : bool
    __queuePointer : Queue[Task]
    __dbConnection : sqlite3.Connection
    __currentTask : Task
    __lockPointer : Lock
    __options : dict

    def __init__(self,queuePointer:Queue[Task],lockPointer:Lock,options:dict) -> None:
        super().__init__()
        self.__queuePointer=queuePointer
        self.__dbConnection=None
        self.__lockPointer=lockPointer
        self.__options=options
    #END def __init__

    def run(self) -> None:
        self.__continue=True
        while self.__continue:
            self.__currentTask=self.__queuePointer.get()
            
            destFile:os.DirEntry
            destFile=os.path.normpath(f"{self.__currentTask.destination}/{self.__currentTask.source.name}")

            #TODO:
            #Check if file confliction exists.  If so, apply the appropriate response.
            logStatement="Unknown Error."
            conflictionStatus=""
            logAction=self.__currentTask.jobType
            actionStatus="Succeeded"
            logSource=os.path.abspath(self.__currentTask.source)
            logDest=os.path.abspath(self.__currentTask.destination)
            execute=True
            if os.path.exists(destFile):
                conflictionStatus="Confliction encountered: "
                collisionMode=self.__options.get("fileConflictMode",0)
                if collisionMode==0: #Do not process the file if set to 'Do nothing.'
                    execute=False
                elif collisionMode==1: #Overwrite the file existing in the destination.
                    pass
                elif collisionMode==2: #Only process the file if the source is newer than the destination.
                    if self.__currentTask.source.stat().st_mtime>=destFile.stat().st_mtime:
                        execute=False
            else:
                conflictionStatus=""
            if execute:
                #Check copy mode flag and apply the appropriate responses according to the task type and the hashing flag(s).
                if self.__currentTask.jobType=="Copy" or self.__currentTask.jobType=="Move":
                    #If mode is copy, copy the item.
                    #If mode is move, copy the item, then add a new task to the queue to delete the source file.
                    try:
                        shutil.copy2(self.__currentTask.source,self.__currentTask.destination)
                        logStatement="Copy success."
                        if self.__currentTask.jobType=="Move":
                            self.__currentTask.destination=destFile
                            self.__currentTask.jobType="Delete"
                            self.__queuePointer.put(self.__currentTask)
                            logStatement+="  Source marked for deletion."
                        #Write to the log that the file was copied.  If it was marked for deletion, then include that statement.
                    except OSError: #Currently, if an IO error occurs, skip this file.
                        actionStatus="Failure"
                        logStatement="Copy failed (check privileges/connection)!  Process skipped."
                        #TODO:
                        #Retry a set number of times.  If the task cannot be completed, log the error and move on.
                elif self.__currentTask.jobType=="Delete":
                    #If mode is delete, delete the source file.
                    try:
                        os.remove(self.__currentTask.source)
                        actionStatus="Success"
                        logStatement="Deletion succeeded."
                    except OSError:
                        actionStatus="Failure"
                        logStatement="Deletion failed (check privileges)!  Process skipped."
                    #Log the result of the operation to the log DB.

            else:
                logStatement="Process skipped."
            self.__queuePointer.task_done()
            #Submit log to the DB.
            with self.__dbConnection:
                query=f"insert into Completed(action,status,description,source,destination) values ('{logAction}','{actionStatus}','{conflictionStatus}{logStatement}','{logSource}','{logDest}')"
                self.__dbConnection.execute(query)
        self.__dbConnection.close()
    #END def run

    def kill(self) -> None:
        self.__continue=False
        #self.__dbConnection.close()
    #END def kill

    def setDB(self,db:os.DirEntry) -> None:
        """
        Sets the logging database connection.  Can be set to `None` if logging is disabled.
        """
        self.__dbConnection=sqlite3.connect(db,check_same_thread=False) if db is not None else None
    #END def setDB
    def closeDB(self) -> None:
        """
        Closes any active DB connection.
        """
        if self.__dbConnection is not None:
            self.__dbConnection.close()
    #END def closeDB
#END class CopierThread

class CopierManager:
    """
    The manager of each thread; scans the given source paths for files to enqueue as `Task` objects.

    Applies the given `options` dictionary to itself and its thread children, ending with a CSV file as the final log file (if logging is enabled).
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
        """
        Begins processing the files from the `sources` paths, inserting them into the `destination` directory.
        """
        #Pass the path of the DB file to the threads.
        #dbLog=None
        logDBPath=os.path.normpath(f"{destination}/job.db")
        db=sqlite3.connect(logDBPath)
        with db:
            db.cursor().execute(
                "create table if not exists Completed (action varchar(8) not null,status varchar(8) not null,description varchar(256) not null,source varchar(4098) not null,destination varchar(4098) not null);"
            )
            #Table name: Completed,
            #action : varchar(8) 
            #status : varchar(8)
            #description : varchar(256)
            #source : varchar(4098)
            #destination : varchar(4098)

        for thread in self.__threads:
            thread.setDB(logDBPath)
            thread.daemon=True
            thread.start()

        for source in sources:
            for task in self.__listDirs(os.path.abspath(source),os.path.abspath(destination)):
                self.__queue.put(task)

        self.__queue.join()

        for thread in self.__threads:
            thread.kill()
        for thread in self.__threads:
            thread.join()

        #Write the transactions from the log DB file to a CSV file (if applicable).
        csvPath=self.__options.get("logDest",None)
        if csvPath is not None:
            logFile=os.path.normpath(f"{csvPath}/__log-file__.csv")

            with open(logFile,"w") as file:
                cursor=db.execute("select * from Completed")

                colNames=[desc[0] for desc in cursor.description]
                file.write(f"{','.join(colNames)}\n") #Write the header first.
                for row in cursor: #For each row in the table, write as a new line into the CSV file.
                    file.write(f"{','.join(row)}\n")
                #cursor.close()
        #When the CSV file is created, delete the DB file(?).
        db.close()

        try:
            os.remove(logDBPath)
            #stillOpen=False
        except OSError as error:
            print(f"\tFailed to remove Sqlite3 Database file at:\n{os.path.abspath(logDBPath)}\n\tReason:\n{str(error)}")
    #END def startJob

    def __listDirs(self,source:os.DirEntry,destination:os.DirEntry) -> Task:
        """
        A generator that finds the next os.DirEntry object within the given 'source'.

        Returns each result in descending order by their path name alphanumerically.
        """
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

    shortenedFlags={f"-{flag[2]}":flag for flag in flags}

    for arg in cmdArgs:
        splitArg=arg.split(":",1)
        if len(splitArg)!=2:
            print(splitArg)
            improperArg(arg)
        
        flag,param=splitArg[0],splitArg[1]

        if flag in shortenedFlags.keys():
            actualFlag=flags[shortenedFlags[flag]]
        elif flag in flags.keys():
            actualFlag=flags[flag]
        #elif flag in noShortenedFlags.keys():
        #    actualFlag=noShortenedFlags[flag]
        else:
            improperArg(arg)

        if actualFlag=="sources": #Convert the string-formatted array into a literal array.
            param=literal_eval(param)
        elif actualFlag=="logType":
            options["log"]=True
        elif actualFlag=="logDest":
            options["log"]=True
            if param=="":
                param=options["destination"]

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
