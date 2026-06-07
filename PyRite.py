from tkinter import Tk
from lib.ui.menu import DynamicMenu
from lib.ui.ide import Layout
from lib.project.project import Project
from os import getcwd

class PyRite(Tk):
    
    def __init__(self):
        
        # Define Variables
        self.project = None
        
        # Window Setup
        super().__init__()

        # IDE Setup
        self.layout = Layout(self)
        self.layout.project_explorer.update_title()

        self.layout.pack(
            fill="both",
            expand=True
        )

        self.project = Project(getcwd())
        self.layout.project_explorer.load_project(self.project)

        # Menubar Setup
        menubar = DynamicMenu(self)
        
        fileMenu = menubar.cascade("File")
        fileMenu.command("New Project...", None)
        fileMenu.command("New...", None, shortcut="Alt+Insert")
        fileMenu.command("New Empty File", None, shortcut="Ctrl+Alt+Shift+Insert")
        fileMenu.command("Open...", None, "Ctrl+O")
        fileMenu.command("Save As...", None)
        recentFileMenu = fileMenu.cascade("Open Recent")
        fileMenu.command("Close Project", None)
        fileMenu.command("Rename Project...", None)
        fileMenu.separator()
        fileMenu.command("Settings...", None, shortcut="Alt+F7")
        fileMenu.separator()
        fileMenu.command("Save", self.save, shortcut="Ctrl+S")
        fileMenu.command("Save All..", self.save_all, shortcut="Ctrl+Shift+S")
        fileMenu.command("Reload All from Disk", None, shortcut="Ctrl+Alt+Y")
        fileMenu.command("Invalidate Caches / Restart...", None)
        fileMenu.separator()
        fileMenu.command("Print...", None, shortcut="Ctrl+P")
        fileMenu.separator()
        fileMenu.command("Close PyRite")
        
        editMenu = menubar.cascade("Edit")
        editMenu.command("Undo", shortcut="Ctrl+Z", callback=lambda: self.layout.editor_notebook.get_active_editor().undo())
        editMenu.command("Redo", shortcut="Ctrl+Y", callback=lambda: self.layout.editor_notebook.get_active_editor().redo())
        editMenu.separator()
        editMenu.command("Select All", shortcut="Ctrl+A", callback=lambda: self.layout.editor_notebook.get_active_editor().select_all())
        editMenu.command("Copy", shortcut="Ctrl+C", callback=lambda: self.layout.editor_notebook.get_active_editor().copy())
        editMenu.command("Cut", shortcut="Ctrl+X", callback=lambda: self.layout.editor_notebook.get_active_editor().cut())
        editMenu.command("Paste", shortcut="Ctrl+V", callback=lambda: self.layout.editor_notebook.get_active_editor().paste())
        
        viewMenu = menubar.cascade("View")
        toolsMenu = menubar.cascade("Tools")
        helpMenu = menubar.cascade("Help")

        self.config(menu=menubar.build())

    def save(self):
        self.layout.editor_notebook.save_active()
        self.layout.project_explorer.update_title()

    def save_all(self):
        self.layout.editor_notebook.save_all()
        self.layout.project_explorer.update_title()
        
if __name__ == "__main__":
    pyrite = PyRite()
    pyrite.mainloop()
