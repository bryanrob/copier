import os,csv

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

def test1() -> bool:
    """
    Performs a basic test of the Copier CLI.
    
    Using files from the 'source' folder, it will attempt to import them into the 'dest' folder within this script's directory.
    """
    thisPath=os.path.dirname(__file__)
    copierPath=os.path.abspath(f"{thisPath}/../copier.py")

    sources=[#Sources should be enclosed with ["] characters to avoid space-break issues.
        f"\"{thisPath}/source\""
    ]
    destination=f"{thisPath}/dest"

    #"--sources":"sources",
    #"--destination":"destination",
    #"--job-type":"job-type",
    #"--log-destination":"logDest",
    #"--hash-algorithm":"logType",
    #"--thread-count":"threads",
    #"--conflict":"fileConflictMode",
    #"--retry":"retry",
    #"--wait":"wait"

    command=f"python \"{copierPath}\" -s:{sources} -d:\"{destination}\" -l: -r:1000 -w:10"

    print(f"//TEST #1//\n\tCommand text:\n{command}")
    output=os.system(command)
    print(f"\n\tExit code: {output}")

    logData=parseLog(destination)

    return getResult(logData,"Success")
#END def test1

if __name__=="__main__":
    tests={
        1:test1
    }

    results={}
    for i in tests.keys():
        try:
            results[i]=tests[i]()
        except Exception:
            results[i]=False

    print("\n//TEST RESULTS//:")

    for key in results:
        print(f"Test {key}) {'Passed' if results[key] else 'Failed'}.")
