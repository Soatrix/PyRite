from tkinter import Text
from tkinter import ttk
from lib.ui.project import EditorNotebook, ProjectExplorer

class Layout(ttk.PanedWindow):

    def __init__(self, parent):
        self.parent = parent
        super().__init__(
            parent,
            orient="horizontal"
        )

        self.project_explorer = ProjectExplorer(self)

        self.editor_notebook = EditorNotebook(self)

        self.add(
            self.project_explorer,
            weight=1
        )

        self.add(
            self.editor_notebook,
            weight=4
        )
        