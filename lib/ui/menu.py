from tkinter import Menu


class DynamicMenu:

    def __init__(self, root):
        self.root = root
        self.menu = Menu(root)

    def cascade(self, label):
        submenu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label=label, menu=submenu)
        return DynamicSubMenu(self.root, submenu)
        
    def spacer(self, count=1):

        label = " " * max(1, count)

        self.menu.add_cascade(
            label=label,
            state="disabled"
        )

        return self

    def build(self):
        return self.menu


class DynamicSubMenu:

    def __init__(self, root, menu):
        self.root = root
        self.menu = menu

    def command(self, label, callback=None, shortcut=None):

        self.menu.add_command(
            label=label,
            command=callback,
            accelerator=shortcut or ""
        )

        if shortcut:
            self._bind_shortcut(shortcut, callback)

        return self

    def separator(self):
        self.menu.add_separator()
        return self

    def cascade(self, label):
        submenu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label=label, menu=submenu)
        return DynamicSubMenu(self.root, submenu)

    def _bind_shortcut(self, shortcut, callback):

        # Convert human-friendly shortcut to Tk format
        event = shortcut.replace("+", "-") \
                        .replace("Ctrl", "Control")

        event = "<" + event + ">"

        self.root.bind_all(
            event,
            lambda e: callback()
        )