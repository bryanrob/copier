import customtkinter as tk

def packChildren(master : tk.CTkBaseClass,padding:dict,*args,**kargs) -> None:
    """
    A shortcut function for packing a series of options under a specific category.
    """
    xPadding=padding.get(0,0)
    yPadding=padding.get(1,0)
    childCount=len(master.winfo_children())
    child : tk.CTkBaseClass
    #print(f"{master=}, {master}")
    for index,child in enumerate(master.winfo_children()):
        if index+1!=childCount:
            #print("\tPacking child...")
            child.pack(side=tk.TOP,padx=xPadding,pady=(yPadding,0),*args,**kargs)
        else:
            #print("\tPacking last child.")
            child.pack(side=tk.TOP,padx=xPadding,pady=yPadding,*args,**kargs)
    #END def packChildren
