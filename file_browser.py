# <INSERT LICENSING CLAUSE HERE>

#from typing import Optional, Tuple, Union
import customtkinter as tk
import os
#import json

class FileBrowser(tk.CTkToplevel):

    dimensions = {
        "height":250,
        "width":76
    }

    def __init__(this,*args,**kwargs):
        this.super().__init__(*args,**kwargs)

    #END def __init__
#END class FileBrowser
