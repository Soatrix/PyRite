# Import Modules
from tkinter import Tk, Menu

class DynamicMenu:
    
    def __init__(self, root):
        self.menu = Menu(root)
        
    def cascade(self, label):
        submenu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label=label, menu=submenu)
        return DynamicSubMenu(submenu)
        
    def build(self):
        return self.menu
        
class DynamicSubMenu:
    
    def __init__(self, menu):
        self.menu = menu
        
    def command(self, label, callback):
        self.menu.add_command(label=label, command=callback)
        return self
           
    def separator(self):
        self.menu.add_separator()
        return self
            
    def cascade(self, label):
        submenu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label=label, menu=submenu)
        return DynamicSubMenu(submenu)