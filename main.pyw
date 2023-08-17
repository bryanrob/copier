#Author: Robert Bryant
#Created On: Feb 2, 2023
#Updated On: May 31, 2023

import customtkinter as tk
from interface import Window

def main():
    tk.set_appearance_mode("system") 
    tk.set_default_color_theme("green")
    window=Window()
    window.mainloop()
#END def main

if __name__=="__main__":
    main()
