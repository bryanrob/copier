from threading import Thread
from queue import Queue
#from hashlib import md5,sha256,sha512
import os,shutil,sqlite3,hashlib,time

class Task:
    """
    An encapsulation of a `Task` that a `CopierThread` will need to process from the queue filled within the `CopierManager` class.
    """
    source : os.DirEntry #The path to the source file.
    destination : os.DirEntry #The path to the destination directory.
    jobType : str #The action to take with this task, i.e. "Copy", "Move" or "Delete".

    def __init__(self,target:os.DirEntry,destination:os.DirEntry,jobType:str):
        self.source=target
        self.destination=destination
        self.jobType=jobType
    #END def __init__
#END class Task

class Hasher:
    """
    A basic hash encapsulation that unifies multiple hashing algorithms into one syntax pattern.

    If the hasher is set to 'none', then it simply checks to see if the target exists.
    """
    __algorithmDict = {
        "none":None,
        "siphash":hash,
        "md5":hashlib.md5,
        "sha256":hashlib.sha256,
        "sha512":hashlib.sha512
    }
    __algorithm : str
    def __init__(self,algorithm:str):
        if algorithm.lower() in self.__algorithmDict.keys():
            self.__algorithm=algorithm.lower()
        else:
            raise KeyError(f"Key {algorithm} not found.")
    #END def __init__

    def chceksum(self,file:os.DirEntry) -> str:
        if self.__algorithmDict[self.__algorithm] is None:
            return str(os.path.exists(file))
        else:
            with open(file,"rb") as f:
                checksum=self.__algorithmDict[self.__algorithm](f.read())
            if type(checksum) is int:
                return str(checksum)
            else:
                return checksum.hexdigest()
    #END def checksum

#END class Hasher

class CopierThread(Thread):
    """
    An individual thread for the Copier process.  Pulls a `Task` from the queue to process, applying the provided options flags as necessary.
    """
    __continue : bool
    __queuePointer : Queue[Task]
    __dbConnection : sqlite3.Connection
    __currentTask : Task
    __HasherPointer : Hasher
    __options : dict

    def __init__(self,queuePointer:Queue[Task],HasherPointer:Hasher,options:dict) -> None:
        super().__init__()
        self.__queuePointer=queuePointer
        self.__dbConnection=None
        self.__HasherPointer=HasherPointer
        self.__options=options
    #END def __init__

    def run(self) -> None:
        self.__continue=True
        while self.__continue:
            attemptCounter=0
            self.__currentTask=self.__queuePointer.get()
            
            timerStart=time.time_ns()

            destFile:os.DirEntry
            destFile=os.path.normpath(f"{self.__currentTask.destination}/{self.__currentTask.source.name}")
 
            logSource=os.path.abspath(self.__currentTask.source)
            logDest=os.path.abspath(destFile)

            #Get hash of source file.
            hashSource=self.__HasherPointer.chceksum(self.__currentTask.source)
            hashDest="None"

            actionStatus="Failure"
            logStatement="Unknown Error."
            conflictionStatus=""
            logAction=self.__currentTask.jobType

            #print(f"Task:\n\t{logSource=}\n\t{logDest=}\n\t{logAction=}")

            execute=True
            if os.path.exists(destFile):
                hashDest=self.__HasherPointer.chceksum(destFile)
                conflictionStatus="Confliction encountered: "
                collisionMode=self.__options.get("fileConflictMode",0)
                if collisionMode==0 and hashSource==hashDest: #Do not process the file if set to 'Do nothing.'
                    execute=False
                elif collisionMode==1 and hashSource==hashDest: #Overwrite the file existing in the destination.
                    execute=False
                elif collisionMode==2 and hashSource==hashDest: #Only process the file if the source is newer than the destination.
                    if os.stat(self.__currentTask.source).st_mtime>=os.stat(destFile).st_mtime:
                        execute=False
            else:
                conflictionStatus=""
            if execute:
                #notComplete=True
                while attemptCounter<self.__options.get("retry",1):
                    #Check copy mode flag and apply the appropriate responses according to the task type and the hashing flag(s).
                    if self.__currentTask.jobType in ["Copy","Move","Mirror"]:
                        #If mode is copy, copy the item.
                        #If mode is move, copy the item, then add a new task to the queue to delete the source file.
                        try:
                            shutil.copy2(self.__currentTask.source,self.__currentTask.destination)
                            #Get hash of copied file.  If the hash does not match the source, retry the copy.
                            hashDest=self.__HasherPointer.chceksum(destFile)
                            if hashSource==hashDest:
                                logDest=os.path.abspath(destFile)
                                actionStatus="Success"
                                logStatement="Copy success."
                                if self.__currentTask.jobType=="Move":
                                    self.__currentTask.destination=destFile
                                    self.__currentTask.jobType="Delete"
                                    self.__queuePointer.put(self.__currentTask)
                                    logStatement+="  Source marked for deletion."
                                #notComplete=False
                            else:
                                actionStatus="Failure"
                                logStatement="Copy failed (checksum mismatch)."

                        except OSError: #Currently, if an IO error occurs, skip this file.
                            actionStatus="Failure"
                            logStatement="Copy failed (check privileges/connection)!  Process skipped."
                            #TODO:
                            #Retry a set number of times.  If the task cannot be completed, log the error and move on.
                    elif self.__currentTask.jobType=="Delete":
                        #If mode is delete, delete the source file.
                        #Validate that the destination file exists, then do a checksum.  If checksum passes, delete; otherwise, enter as new 'Move' task.
                        hashDest=self.__HasherPointer.chceksum(self.__currentTask.destination)

                        #Also, check if the targeted file is currently being used by another thread.  If so, then wait for that thread to finish its processing.
                        #If the target & source does not exist in the database, then they have not finished processing within another thread.
                        nrows=0
                        while nrows<=0:
                            nrows=self.__dbConnection.execute("select count(source) from Completed where source=?;",(os.path.abspath(self.__currentTask.source),)).fetchone()[0]
                            #nrows=len([row for row in self.__dbConnection.execute(f"select source from Completed where source=(?);",(os.path.abspath(self.__currentTask.source),))])
                            time.sleep((self.__options.get("wait",0)/1000)+0.5)

                        if hashSource==hashDest:
                            try:
                                os.remove(self.__currentTask.source)
                                actionStatus="Success"
                                logStatement="Deletion succeeded."
                                #notComplete=False
                            except OSError:
                                actionStatus="Failure"
                                logStatement="Deletion failed (check privileges)!  Process skipped."
                            #Log the result of the operation to the log DB.
                        else:
                            actionStatus="Failure"
                            logStatement="Checksum mismatch.  Process skipped."
                            #self.__currentTask.destination=os.path.dirname(self.__currentTask.destination)
                    elif self.__currentTask.jobType=="Delete-super":
                        #print(f"Attempting to delete {os.path.abspath(self.__currentTask.source)}...")
                        try:
                            if os.path.isdir(self.__currentTask.source):
                                os.rmdir(self.__currentTask.source)
                            else:
                                os.remove(self.__currentTask.source)
                            actionStatus="Success"
                            logStatement="Deletion succeeded."
                        except OSError:
                            actionStatus="Failure"
                            logStatement="Deletion failed (check privileges)!  Process skipped."
                    #END of self.__currentTask.jobType conditions.
                    else:
                        actionStatus="Failure"
                        logStatement="Unknown job operation.  Process skipped."
                    if actionStatus=="Failure":#notComplete:
                        attemptCounter+=1
                        time.sleep(self.__options.get("wait",0)/1000) #Convert int milliseconds to floating-point seconds.
                    else:
                        break
            else:
                actionStatus="Success"
                logStatement="Skip condition met.  Process skipped."
                #notComplete=False
            self.__queuePointer.task_done()
            timerEnd=time.time_ns()

            timerStartStr=time.ctime(timerStart/(10**9))
            timerEndStr=time.ctime(timerEnd/(10**9))
            
            #Submit log to the DB.
            with self.__dbConnection:
                self.__dbConnection.execute("insert into Completed(action,status,description,source,src_checksum,destination,dest_checksum,retries,time_started,unix_time_started,time_ended,unix_time_ended) values (?,?,?,?,?,?,?,?,?,?,?,?)",(logAction,actionStatus,f"{conflictionStatus}{logStatement}",logSource,hashSource,logDest,hashDest,attemptCounter,timerStartStr,timerStart,timerEndStr,timerEnd))
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
    __Hasher : Hasher
    __options : dict
    #__mirrorMode = False

    def __init__(self,options:dict):
        self.__options=options
        self.__queue=Queue(maxsize=options.get("queue-maximum",250000))
        self.__Hasher=Hasher(options.get("logType","None"))

        if options.get("job-type","Copy")=="Mirror":
            self.__options["fileConflictMode"]=2 #Mirror mode overwrites if the source is newer.
        #    self.__mirrorMode=True

        self.__threads=[CopierThread(self.__queue,self.__Hasher,options) for thread in range(options.get("threads",1))]
    #END def __init__

    def startJob(self,sources:list[str],destination:str):
        """
        Begins processing the files from the `sources` paths, inserting them into the `destination` directory.
        """
        timerStart=time.time_ns()

        #Pass the path of the DB file to the threads.
        #dbLog=None
        logDBPath=os.path.normpath(f"{destination}/job.db")
        db=sqlite3.connect(logDBPath)
        with db:
            db.cursor().execute(
                "create table if not exists Completed (action varchar(8) not null,status varchar(8) not null,description varchar(256) not null,retries tinyint not null,source varchar(4098) not null,src_checksum varchar(512),destination varchar(4098) not null,dest_checksum varchar(512),time_started varchar(24) not null,unix_time_started int not null,time_ended varchar(24) not null,unix_time_ended int not null);"
            )
            #Table name: Completed,
            #action : varchar(8) 
            #status : varchar(8)
            #description : varchar(256)
            #retries : tinyint
            #source : varchar(4098)
            #src_checksum : varchar(512)
            #destination : varchar(4098)
            #dest_checksum : varchar(512)
            #time_started : varchar(24)
            #unix_time_started : int
            #time_ended : varchar(24)
            #unix_time_ended : int

        for thread in self.__threads:
            thread.setDB(logDBPath)
            thread.daemon=True
            thread.start()

        for source in sources:
            sourcePath=os.path.abspath(source)
            destinationPath=os.path.abspath(f"{destination}/{os.path.basename(sourcePath)}")
            for task in self.__listDirs(sourcePath,destinationPath):
                self.__queue.put(task)
        
        if self.__options.get("job-type","Copy")=="Mirror":
            for task in self.__removeMissingDirs(sources,destination):
                self.__queue.put(task)

        self.__queue.join()

        for thread in self.__threads:
            thread.kill()
        for thread in self.__threads:
            thread.join()
        
        timerEnd=time.time_ns()

        timerStartStr=time.ctime(timerStart/(10**9))
        timerEndStr=time.ctime(timerEnd/(10**9))

        #Create the string for the log summary.
        totalSuccess,totalFail,totalRows,totalRetry=0,0,0,0
        mainStatus="Unknown"
        mainStatement="An unknown error has occurred."
        with db:
            cursor=db.execute("select successes,failures,count(source) as total_operations,sum(retries) as total_retries from Completed,(select count(status) as successes from Completed where status='Success'),(select count(status) as failures from Completed where status='Failure')")
            rowData=[row for row in cursor][0]
            totalSuccess=rowData[0]
            totalFail=rowData[1]
            totalRetry=rowData[3]

            if totalSuccess>0 and totalFail>0:
                mainStatus="Mixed"
                mainStatement=f"Over {rowData[2]} actions, {totalSuccess} succeeded & {totalFail} failed."
            elif totalSuccess>0 and totalFail==0:
                mainStatus="Success"
                mainStatement=f"All {rowData[2]} actions succeeded."
            elif totalSuccess==0 and totalFail>0:
                mainStatus="Failure"
                mainStatement=f"All {rowData[2]} actions failed."

        mainLogEntry=f"Main,{mainStatus},{mainStatement},{totalRetry},{sources},,{destination},,{timerStartStr},{timerStart},{timerEndStr},{timerEnd}"

        #Write the transactions from the log DB file to a CSV file (if applicable).
        csvPath=self.__options.get("logDest",None)
        if csvPath is not None:
            logFile=os.path.normpath(f"{csvPath}/__log-file__.csv")

            with open(logFile,"w") as file:
                cursor=db.execute("select * from Completed order by unix_time_ended asc")

                colNames=[desc[0] for desc in cursor.description]
                file.write(f"{','.join(colNames)}\n{mainLogEntry}\n") #Write the header & log summary first.
                for row in cursor: #For each row in the table, write as a new line into the CSV file.
                    rowElements=[str(element) for element in row]
                    file.write(f"{','.join(rowElements)}\n")
                #cursor.close()
        #When the CSV file is created, delete the DB file(?).
        db.close()

        try:
            os.remove(logDBPath)
            #pass
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
    #END def __listDirs
  
    def __removeMissingDirs(self,sources:list[os.DirEntry],destination:os.DirEntry) -> Task:
        """
        Walks the paths in the destination and returns files & folders that are within the destination and not within the source.
        """
        def searchSubDirs(source:os.DirEntry,destination:os.DirEntry) -> Task:
            """
            Recursive extension of __searchDirs.
            """
            condition="Delete-super"

            for directory in os.scandir(destination):
                sourcePath=os.path.join(source,os.path.basename(directory))
                #If the path exists in both the destination and main, continue the scan from within the path.
                if directory.is_dir() and os.path.exists(sourcePath):
                    newDest=os.path.join(destination,os.path.basename(directory))
                    newSrc=os.path.join(source,os.path.basename(directory))
                    yield from searchSubDirs(newSrc,newDest)
                #If the path is a folder and doesn't exist in the source, return this path and all paths from within it.
                elif directory.is_dir() and not os.path.exists(sourcePath):
                    for dir in os.scandir(directory):
                        if dir.is_dir():
                            #Yield files from `dir`...
                            for file in delPaths(dir): 
                                yield Task(file,os.path.join(sourcePath,os.path.basename(dir),os.path.basename(file)),condition)
                        #Yield path of `dir`.
                        yield Task(dir,os.path.join(sourcePath,os.path.basename(dir)),condition)
                    #Yield path of `directory`.
                    yield Task(directory,sourcePath,condition) 
                else:
                    #Otherwise, check if the source path exists.  If not, the destination path.
                    srcPath=os.path.join(source,os.path.basename(directory))
                    if not os.path.exists(srcPath):
                        yield Task(directory,srcPath,condition)
        #END def __searchDirs

        def delPaths(path:os.DirEntry) -> str:
            """
            Returns all paths from within the given directory, then returns the directory itself.
            """
            for dir in os.scandir(path):
                if dir.is_dir():
                    yield from delPaths(dir)
                yield Task(dir)
        #END def __delPaths

        for source in sources:
            for task in searchSubDirs(source,os.path.join(destination,os.path.basename(source))):
                yield task
    #END def __removeMissingDirs


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
    defaultOptions=options.copy()

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
        "--conflict":"fileConflictMode",
        "--retry":"retry",
        "--wait":"wait"
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
        elif actualFlag=="threads" or actualFlag=="retry" or actualFlag=="fileConflictMode" or actualFlag=="wait":
            try:
                param=int(param)
                if param <= 0 and (actualFlag=="threads" or actualFlag=="retry"):
                    improperValue(arg,param)
                elif param<0 and actualFlag=="wait":
                    improperValue(arg,param)
            except ValueError:
                improperValue(arg,param)
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

def improperValue(arg:str,param) -> None:
    import sys
    print(f"VALUE ERROR: Improper value entered near: {arg}:{param}")
    sys.exit(2)
#END def improperValue

if __name__=="__main__":
    main()
