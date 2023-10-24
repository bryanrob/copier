import tkinter
from typing import Optional, Tuple, Union
import customtkinter as tk
from customtkinter.windows.widgets.font import CTkFont

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

class NumericEntry(tk.CTkEntry):
    """
    An expansion of the generic text-entry element; allowing only numeric characters.
    """
    __str : tk.StringVar
    __previous_str : str

    def __init__(self, master: any, *args, **kwargs):
        self.__str=tk.StringVar()
        super().__init__(master, textvariable=self.__str,*args, **kwargs)
        self.__previous_str=""
        self.__str.trace("w",self.__check)
    #END def __init__

    def __check(self,*args):
        """
        Validates that the entry is either empty or contains only numeric characters.
        """
        if self.get().isdigit() or self.get()=="":
            self.__previous_str=self.get()
        else:
            self.delete(0,len(self.get()))
            self.insert(0,self.__previous_str)
    #END def __check
#END class NumericEntry
