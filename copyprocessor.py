# <INSERT LICENSING CLAUSE HERE>

import time
import os
import shutil
from threading import Thread,Lock
import hashlib
#from multiprocessing import Process
from queue import Queue
from dataclasses import dataclass

@dataclass
class Task:
    source : os.DirEntry
    destination : os.DirEntry
#END class Task

def listDirs(source,destination):
    #print(f"Source: {str(source)}\nDest: {str(destination)}")
    for directory in os.scandir(source):
        if directory.is_dir():
            newDest=os.path.join(destination,os.path.basename(directory))
            try:
                os.mkdir(newDest)
            finally:
                yield from listDirs(directory,newDest)
        else:
            yield Task(directory,destination)
#END def listDirs

class Manager:
    def __init__(this,workerCount : int,sourceDirectories : list,destDirectory : str,logFile="log.csv"):
        this.queue=Queue()
        this.workerCount=workerCount
        this.sourceDirectories=sourceDirectories
        this.destDirectory=destDirectory

        this.lock=Lock()
        open(logFile,"w").close()

        #this.workers=[Worker(this.queue)]*workerCount
        this.workers={}
        for i in range(0,workerCount):
            this.workers[i]=Worker(this.queue,this.destDirectory,logFile,this.lock)
    #END def __init__

    def startProcess(this):
        #Prepare $ start worker processes...
        for workerID in this.workers:
            this.workers[workerID].daemon=True
            this.workers[workerID].start()
        
        #Build the task queue.
        for sourceDir in this.sourceDirectories:
            for task in listDirs(sourceDir,this.destDirectory):
                this.queue.put(task)
        this.queue.join()
    #END def startProcess

    def startTestProcess(this):
        #Start worker processes...
        for workerID in this.workers:
            this.workers[workerID].daemon=True
            this.workers[workerID].start()
        
        #Fill queue; workers will pull from queue as it fills.
        #for i in range(0,25):
        #    print(f"\tAdding {i} to queue...")
        #    this.queue.put(f"{i}")

        for sourceDir in this.sourceDirectories:
            dirs=listDirs(sourceDir,this.destDirectory)
            for dir in dirs:
            #PRINT ENQUEUE
                #try:
                #    print(f"Enqueing [{dir}].")
                #except:
                #    print(f"Enqueing [<filename contains unusual character>].")
            #END PRINT ENQUEUE
                this.queue.put(dir)
        this.queue.join()
    #END def startTestProcess
#END class Manager

class Worker(Thread):
    def __init__(this,queue:Queue,destination:str,logFile:str,lock:Lock):
        Thread.__init__(this)
        this.queue=queue
        this.destination=destination
        this.logFile=logFile
        this.lock=lock
    #END def __init__

    def run(this):
        while True:
            Task=this.queue.get()
            src=Task.source
            dest=Task.destination
            destFile=f"{dest}\\{Task.source.name}"
            try:
                #print(f"\tID: {id(this)}\tNumber: {num}")

            #PRINT START
                try:
                    print(f"\tID: {id(this)}\n\t\tCopying {src} to {dest}...")
                except:
                    print(f"\tID: {id(this)}\n\t\tCopying <filename contains unusual character> to {dest}...")
            #END PRINT START

                #time.sleep(0.25)
                #print(f"\tID: {id(this)}\n\t\tCopy of {path} to {this.destination} complete!")

            #PRINT END
                #try:
                #    print(f"\tID: {id(this)}\n\t\tCopy of {path} to {this.destination} complete!")
                #except:
                #    print(f"\tID: {id(this)}\n\t\Copy of <filename contains unusual character> to {this.destination} complete!")
            #END PRINT END
                #shutil.copy2(src,dest)
                with open(src,"rb") as source:
                    with open(destFile,"wb") as destination:
                        destination.write(source.read())


                with open(src,"rb") as file:
                    srcHash=hashlib.md5(file.read()).hexdigest()
                with open(destFile,"rb") as file:
                    destHash=hashlib.md5(file.read()).hexdigest()

                
                this.lock.acquire()
                with open(this.logFile,"a") as file:
                    file.write(f"{src},{srcHash},{dest},{destHash}")
                this.lock.release()

            finally:
                this.queue.task_done()
    #END def run

    def printTest(this):
        print(f"Target: {this.target}\tStarted...")
        time.sleep(5)
        print(f"Target: {this.target}\t...Ended.")
    #END def printTest
#END class Worker

class TestWorker(Thread):
    def __init__(this,queue):
        Thread.__init__(this)
        this.queue=queue
    #END def __init__

    def run(this):
        while True:
            num=this.queue.get()
            try:
                print(f"\tID: {id(this)}\tNumber: {num}")
            finally:
                this.queue.task_done()
    #END def run

    #def printStatus(this):
    #    print(f"Target: {this.target}\nRunning Status: {this.isRunning}")
    #END def printStatus
#END class Worker

def main():
    print("Starting test...\n")

    #os.chdir(os.path.dirname(__file__))
    #print(os.path.dirname(__file__))
    sourceDirs=['\\test\\source']
    for i in range(len(sourceDirs)):
        sourceDirs[i]=os.path.dirname(__file__)+sourceDirs[i]
    destDir=os.path.dirname(__file__)+"\\test\\dest"
    
    test=Manager(3,sourceDirs,destDir)
    test.startTestProcess()

    print("\nTest complete!")
#END def main

if __name__=="__main__":
    main()
