from pathlib import Path

class File:
    
    def __init__(self, path=None):
        self.path = path
        if self.path:
            self.absolute_path = Path(path)
        else:
            self.absolute_path = None
        self.modified = False
        self.content = ""
    
    @property
    def name(self):
        return self.absolute_path.name
    
    @property
    def exists(self):
        return self.absolute_path.exists()
        
    def load(self):
        self.content = self.absolute_path.read_text()
        return self.content
        
    def save(self):
        self.absolute_path.write_text(self.content)
        self.modified = False
    
    def reload(self):
        return self.load()