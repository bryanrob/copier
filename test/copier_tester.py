import csv,os,shutil,time

def clearDir(dir:str) -> None:
    """
    Removes everything within the given directory.
    """
    for path in os.scandir(dir):
        if os.path.isdir(path):
            clearDir(path)
            os.rmdir(path)
        else:
            os.remove(path)
#END def clearDir

def parseLog(destination:str) -> dict:
    """
    Converts the log file at the given `destination` into a Python dictionary with the headers used as keys.
    """
    with open(f"{destination}/__log-file__.csv","r") as file:
        csvData=[row for row in csv.reader(file)]
        csvDict={key:[vals[i] for vals in csvData[1:]] for i,key in enumerate(csvData[0])}
        del csvData
    return csvDict
#END def parseLog

def getResult(logData:dict,expectedStatus:str) -> bool:
    return str(logData["status"][0])==expectedStatus
#END def getResult

def copyFailedLog(iter:int,destination:str) -> None:
    """
    If a test failed without an exception, copy the resulting log file to the `fail_logs` folder.
    """
    failLog=(f"{destination}/../fail_logs/__log-file__{iter}.csv")
    destLog=(f"{destination}/__log-file__.csv")

    with open(destLog,"r") as logSource:
        with open(failLog,"w") as logDest:
            logDest.write(logSource.read())
#END def copyFailedLog

def test1(sources:list[str],destination:str) -> bool:
    """
    Performs a basic test of the Copier CLI.
    
    Using files from the 'source' folder, it will attempt to import them into the 'dest' folder within this script's directory.
    """
    
    #Clear the destination of all files beforehand.
    clearDir(destination)

    command=f"python \"{copierPath}\" -s:{sources} -d:\"{destination}\" -l: -r:100 -w:10"

    print(f"\tCommand text:\n{command}")
    output=os.system(command)
    print(f"\n\tExit code: {output}")
    
    result=getResult(parseLog(destination),"Success")
    print(f"\tTest condition check(s): {result}")

    return result
#END def test1

def test2(sources:list[str],destination:str) -> bool:
    """
    Tests the functionality of the `Move` option.
    """
    clearDir(destination)

    command=f"python \"{copierPath}\" -s:{sources} -d:\"{destination}\" -l: -j:Move -r:100 -w:10"    
    print(f"\tCommand text:\n{command}")
    output=os.system(command)
    print(f"\n\tExit code: {output}")

    subdirs=0
    for source in sources:
        for dir in os.scandir(os.path.abspath(source.strip("\""))):
            subdirs+=1
    
    sourcesAreEmpty=subdirs==0

    #Returns True if the job was successful and all sources are empty.
    logResult=getResult(parseLog(destination),"Success")

    print(f"\tTest condition check(s):\n\t\t{logResult=}\n\t\t{sourcesAreEmpty=}")

    result=logResult and sourcesAreEmpty

    for path in os.scandir(destination):
        if path.is_dir():
            shutil.copytree(path,os.path.join(os.path.dirname(destination),os.path.basename(path)),dirs_exist_ok=True)

    return result
#END def test2

#CLI flags:
    #With shortcuts:
    #"--sources":"sources",
    #"--destination":"destination",
    #"--job-type":"job-type",
    #"--log-destination":"logDest",
    #"--hash-algorithm":"logType",
    #"--thread-count":"threads",
    #"--conflict":"fileConflictMode",
    #"--retry":"retry",
    #"--wait":"wait"
    #Without shortcuts:
    #"--ignore-old-job":"ignoreOldJob"

if __name__=="__main__":
    thisPath=os.path.dirname(__file__)
    copierPath=os.path.abspath(f"{thisPath}/../copier.py")

    sources=[#Sources should be enclosed with ["] characters to avoid space-break issues.
        f"\"{thisPath}/source\""
    ]
    destination=f"{thisPath}/dest"

    tests={
        1:test1,
        2:test2
    }

    results={}
    for i in tests.keys():
        print(f"//START TEST #{i}//")
        try:
            results[i]=tests[i](sources,destination)
            if not results[i]:
                copyFailedLog(i,destination)
        except Exception as e:
            print(str(e))
            results[i]=False
        print(f"//END TEST #{i}//\n")
        time.sleep(0.25)
    print("\n//TEST RESULTS//:")

    for key in results:
        print(f"Test #{key}) {'Passed' if results[key] else 'Failed'}.")
