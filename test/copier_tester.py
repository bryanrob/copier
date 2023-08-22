import os

def test1():
    """
    Performs a basic test of the Copier CLI.
    
    Using files from the 'source' folder, it will attempt to import them into the 'dest' folder within this script's directory.
    """
    thisPath=os.path.dirname(__file__)
    copierPath=os.path.abspath(f"{thisPath}/../copier.py")

    sources=[#Sources should be enclosed with ["] characters to avoid spacing issues.
        f"\"{thisPath}/source\""
    ]
    destination=f"{thisPath}/dest"

    command=f"python \"{copierPath}\" -s:{sources} -d:\"{destination}\""

    print(f"\tCommand text:\n{command}")
    output=os.system(command)
    print(f"\n\tExit code: {output}")
#END def test1

if __name__=="__main__":
    test1()