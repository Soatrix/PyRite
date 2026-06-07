from tkinter import ttk
from tkinter import Menu
from pathlib import Path
from lib.ui.editor import CodeEditor
from lib.project.file import File
import shutil
import os
import stat

class EditorNotebook(ttk.Notebook):

    def __init__(self, parent):

        super().__init__(parent)
        self.parent = parent
        self.editors = {}

        self.placeholder_editor = None
        self.create_placeholder_editor()

    def open_file(self, file):

        if file.path in self.editors:

            self.select(
                self.editors[file.path]
            )
            return

        if self.can_replace_placeholder():

            editor = self.placeholder_editor

            editor.load_file(file)

            self.tab(
                editor,
                text=file.name
            )

            self.placeholder_editor = None

        else:

            editor = CodeEditor(self)

            editor.load_file(file)

            self.add(
                editor,
                text=file.name
            )

        self.editors[file.path] = editor

        self.select(editor)
        
    def set_editor_modified_state(self, editor, modified):

        current_text = self.tab(editor, "text")
        clean_text = current_text.strip("*")

        if modified:
            self.tab(editor, text="*{0}*".format(clean_text))
        else:
            self.tab(editor, text=clean_text)
            
        file = editor.file

        if file and file.absolute_path:
            self.parent.project_explorer.set_file_modified_state(
                file.absolute_path,
                modified
            )
            
    def create_placeholder_editor(self):

        editor = CodeEditor(self)

        self.add(
            editor,
            text="New"
        )

        self.placeholder_editor = editor

        self.select(editor)

        return editor
        
    def can_replace_placeholder(self):

        return (
            self.placeholder_editor is not None and
            not self.placeholder_editor.file.modified and
            not self.placeholder_editor.file.absolute_path
        )
        
    def get_active_editor(self):
        widget = self.nametowidget(self.select())
        return widget
        
    def get_active_file(self):
        editor = self.get_active_editor()
        if editor:
            return editor.file
        return None
        
    def save_active(self):
        editor = self.get_active_editor()

        if editor:
            editor.save()
            
    def save_all(self):
        for editor in self.editors.values():
            editor.save()

        if self.placeholder_editor:
            self.placeholder_editor.save()

class ProjectExplorer(ttk.Frame):

    def __init__(self, parent):
        self.parent = parent
        self.project = None
        super().__init__(parent)

        self.tree = ttk.Treeview(self)

        self.tree.pack(
            fill="both",
            expand=True
        )
        
        self.tree.bind(
            "<Double-1>",
            self._on_double_click
        )
        
        self.context_menu = Menu(self, tearoff=0)

        self.context_menu.add_command(label="Open", command=self._open_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Cut")
        self.context_menu.add_command(label="Copy")
        self.context_menu.add_command(label="Paste")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Rename", command=self._rename_selected)
        self.context_menu.add_command(label="Delete", command=self._delete_selected)
        
        self.tree.bind("<Button-3>", self._on_right_click)
        
    def _on_right_click(self, event):

        item = self.tree.identify_row(event.y)

        if not item:
            return

        self.tree.selection_set(item)
        self.tree.focus(item)

        self.context_menu.tk_popup(event.x_root, event.y_root)
        
    def _on_double_click(self, event):

        item = self.tree.focus()

        if not item:
            return

        values = self.tree.item(
            item,
            "values"
        )

        if not values:
            return

        path = Path(values[0])

        if path.is_dir():
            return

        file = File(path)

        file.load()

        self.parent.editor_notebook.open_file(
            file
        )

    def load_project(self, project):
        
        self.project = project

        self.tree.delete(*self.tree.get_children())
        
        self.tree.heading(
            "#0",
            text="{0} - {1}".format(
                project.name,
                project.path
            ),
            anchor="w"
        )

        # Populate the tree directly with the contents of the project
        self._add_directory(
            "",
            project.absolute_path
        )
        
        self.update_title()
        
    def update_title(self):
        if self.project is not None:
            title = "PyRite | " + self.project.name + " - " + self.project.path
        else:
            title = "PyRite | Unsaved Project - /"
        if self.project and self.project.modified:
            title = "*" + title + "*"
        self.parent.parent.title(title)

    def _add_directory(self, parent, path):

        for child in path.iterdir():

            node = self.tree.insert(
                parent,
                "end",
                text=child.name,
                values=(str(child),)
            )

            if child.is_dir():

                self._add_directory(
                    node,
                    child
                )
                
    def set_file_modified_state(self, file_path, modified):

        # find item by path
        for item in self.tree.get_children(""):
            self._update_item_recursive(item, file_path, modified)
    
    def _update_item_recursive(self, item, file_path, modified):

        values = self.tree.item(item, "values")

        if values and values[0] == str(file_path):

            current_text = self.tree.item(item, "text")
            clean_text = current_text.strip("*")

            if modified:
                self.tree.item(
                    item,
                    text="*{0}*".format(clean_text)
                )
            else:
                self.tree.item(
                    item,
                    text=clean_text
                )

            return True

        for child in self.tree.get_children(item):

            if self._update_item_recursive(child, file_path, modified):
                return True

        return False
        
    def _get_selected_path(self):

        item = self.tree.focus()

        if not item:
            return None

        values = self.tree.item(item, "values")

        if not values:
            return None

        return Path(values[0])
        
    def _open_selected(self):
        path = self._get_selected_path()
        if not path or path.is_dir():
            return

        file = File(path)
        file.load()

        self.parent.editor_notebook.open_file(file)
        
    def _handle_remove_readonly(self, func, path, exc):
        # Force delete read-only files (Windows fix)
        os.chmod(path, stat.S_IWRITE)
        func(path)


    def _delete_selected(self):

        path = self._get_selected_path()

        if not path:
            return

        try:

            if path.is_file():
                path.unlink()

            elif path.is_dir():
                shutil.rmtree(
                    path,
                    onerror=self._handle_remove_readonly
                )

        except PermissionError as e:
            print(f"Delete failed: {e}")

        self.load_project(self.project)
        
    def _rename_selected(self):
        print("Rename not implemented yet")