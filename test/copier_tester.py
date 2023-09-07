import os

def test1():
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

    print(f"\tCommand text:\n{command}")
    output=os.system(command)
    print(f"\n\tExit code: {output}")
#END def test1

if __name__=="__main__":
    test1()