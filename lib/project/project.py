from pathlib import Path
from tkinter import messagebox
        
class Project:
    
    def __init__(self, path):
        self.path = path
        self.absolute_path = Path(path)
        self.opened_files = {}
        
    @property
    def name(self):
        return self.absolute_path.name
    
    @property
    def files(self):
        for path in self.absolute_path.rglob("*"):
            if path.is_file():
                yield File(path)
                
    @property
    def modified(self):
        modified = False
        for file in self.opened_files:
            if self.opened_files[file].modified:
                modified = True
                break
        
        return modified
                
    def open_file(self, path):
        if path not in self.opened_files and path in self.files:
            file = self.get_file(path)
            file.load()
            self.opened_files[path] = file
            
        return self.opened_files[path]
        
    def get_file(self, path):

        absolute_path = Path(path)

        if not absolute_path.is_absolute():
            absolute_path = self.path / absolute_path

        if not absolute_path.exists():
            raise FileNotFoundError(path)

        return File(path)
            
    def save_file(self, path):
        if path not in self.opened_files:
            return
            
        file = self.opened_files[path]
        file.save()
        
    def close_file(self, path):
        if path in self.opened_files:
            file = self.get_file(path)
            if file.modified:
                if messagebox.askyesno(title="Save File", message="This file is currently not saved. Would you like to save it now?"):
                    file.save()
                del self.opened_files[path]