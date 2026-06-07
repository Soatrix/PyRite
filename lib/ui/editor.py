from tkinter import Text, Canvas
from tkinter import ttk

from lib.project.file import File

from pygments import lex
from pygments.token import Token
from pygments.lexers import get_lexer_for_filename

class CodeEditor(ttk.Frame):

    def __init__(self, parent):

        self.parent = parent

        super().__init__(parent)

        self.file = File()
        self._original_content = ""

        # =====================================================
        # LINE NUMBER GUTTER
        # =====================================================
        self.linenumber_canvas = Canvas(
            self,
            width=40,
            bg="#efefef",
            highlightthickness=0,
            bd=0
        )

        # =====================================================
        # TEXT EDITOR
        # =====================================================
        self.text = Text(
            self,
            undo=True,
            wrap="none"
        )

        # =====================================================
        # SCROLLBARS
        # =====================================================
        self.vertical_scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self._on_scrollbar
        )

        self.horizontal_scrollbar = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.text.xview
        )

        self.text.configure(
            yscrollcommand=self._on_text_scroll,
            xscrollcommand=self.horizontal_scrollbar.set
        )

        # =====================================================
        # LAYOUT
        # =====================================================
        self.linenumber_canvas.grid(
            row=0,
            column=0,
            sticky="ns"
        )

        self.text.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.vertical_scrollbar.grid(
            row=0,
            column=2,
            sticky="ns"
        )

        self.horizontal_scrollbar.grid(
            row=1,
            column=1,
            sticky="ew"
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # =====================================================
        # EVENTS
        # =====================================================
        self.text.bind("<<Modified>>", self._on_modified)

        self.text.bind(
            "<Configure>",
            lambda e: self.after_idle(self.update_line_numbers)
        )

        self.text.bind(
            "<KeyRelease>",
            lambda e: self.after_idle(self.update_line_numbers)
        )

        self.text.bind(
            "<MouseWheel>",
            lambda e: self.after_idle(self.update_line_numbers)
        )

        self.text.bind(
            "<ButtonRelease-1>",
            lambda e: self.after_idle(self.update_line_numbers)
        )

        # Linux scrolling
        self.text.bind(
            "<Button-4>",
            lambda e: self.after_idle(self.update_line_numbers)
        )

        self.text.bind(
            "<Button-5>",
            lambda e: self.after_idle(self.update_line_numbers)
        )

        self.update_line_numbers()
        
    # =====================================================
    # EDIT OPERATIONS
    # =====================================================

    def undo(self):

        try:

            self.text.edit_undo()

        except Exception:

            pass

    def redo(self):

        try:

            self.text.edit_redo()

        except Exception:

            pass

    def copy(self):

        try:

            selected = self.text.get(
                "sel.first",
                "sel.last"
            )

        except Exception:

            return

        self.clipboard_clear()
        self.clipboard_append(selected)

    def cut(self):

        try:

            selected = self.text.get(
                "sel.first",
                "sel.last"
            )

        except Exception:

            return

        self.clipboard_clear()
        self.clipboard_append(selected)

        self.text.delete(
            "sel.first",
            "sel.last"
        )

    def paste(self):

        try:

            text = self.clipboard_get()

        except Exception:

            return

        if self.text.tag_ranges("sel"):

            self.text.delete(
                "sel.first",
                "sel.last"
            )

        self.text.insert(
            "insert",
            text
        )

    def delete(self):

        try:

            self.text.delete(
                "sel.first",
                "sel.last"
            )

        except Exception:

            pass

    def select_all(self):

        self.text.tag_add(
            "sel",
            "1.0",
            "end-1c"
        )

        self.text.mark_set(
            "insert",
            "1.0"
        )

        self.text.see(
            "insert"
        )

    # =====================================================
    # LINE NUMBERS
    # =====================================================
    def update_line_numbers(self):

        self.linenumber_canvas.delete("all")

        index = self.text.index("@0,0")

        while True:

            line_info = self.text.dlineinfo(index)

            if line_info is None:
                break

            y = line_info[1]

            line_number = index.split(".")[0]

            self.linenumber_canvas.create_text(
                self.linenumber_canvas.winfo_width() - 5,
                y,
                anchor="ne",
                text=line_number,
                fill="#888",
                font=("Consolas", 10)
            )

            index = self.text.index(
                "%s+1line" % index
            )

        self.update_line_number_width()

    def update_line_number_width(self):

        line_count = int(
            self.text.index("end-1c").split(".")[0]
        )

        digits = max(
            2,
            len(str(line_count))
        )

        width = (digits * 10) + 1

        self.linenumber_canvas.configure(
            width=width
        )

    # =====================================================
    # SCROLLING
    # =====================================================
    def _on_scrollbar(self, *args):

        self.text.yview(*args)

        self.after_idle(
            self.update_line_numbers
        )

    def _on_text_scroll(self, first, last):

        self.vertical_scrollbar.set(
            first,
            last
        )

        self.after_idle(
            self.update_line_numbers
        )

    # =====================================================
    # MODIFIED STATE
    # =====================================================
    def _on_modified(self, event):

        current_content = self.text.get(
            "1.0",
            "end-1c"
        )

        modified = (
            current_content !=
            self._original_content
        )

        if modified != self.file.modified:

            self.file.modified = modified

            self.parent.set_editor_modified_state(
                self,
                modified
            )

        self.highlight()

        self.after_idle(
            self.update_line_numbers
        )

        self.text.edit_modified(False)

    # =====================================================
    # FILE OPERATIONS
    # =====================================================
    def load_file(self, file):

        self.file = file

        self.text.delete(
            "1.0",
            "end"
        )

        self.text.insert(
            "1.0",
            file.content
        )

        self._original_content = file.content

        self.text.edit_modified(False)

        self.configure_language()

        self.update_line_numbers()

    def save(self):

        if not self.file.absolute_path:
            return

        self.file.content = self.text.get(
            "1.0",
            "end-1c"
        )

        self.file.save()

        self._original_content = self.file.content

        self.parent.set_editor_modified_state(
            self,
            False
        )

        self.text.edit_modified(False)

    # =====================================================
    # SYNTAX HIGHLIGHTING
    # =====================================================
    def highlight(self):

        if not self.file.absolute_path:
            return

        for tag in self.text.tag_names():
            self.text.tag_remove(
                tag,
                "1.0",
                "end"
            )

        content = self.text.get(
            "1.0",
            "end-1c"
        )

        try:

            lexer = get_lexer_for_filename(
                str(self.file.absolute_path)
            )

        except Exception:
            return

        row = 1
        column = 0

        for token_type, value in lex(
            content,
            lexer
        ):

            start = "%d.%d" % (
                row,
                column
            )

            for char in value:

                if char == "\n":

                    row += 1
                    column = 0

                else:

                    column += 1

            end = "%d.%d" % (
                row,
                column
            )

            tag = None

            if token_type in Token.Keyword:
                tag = "keyword"

            elif token_type in Token.String:
                tag = "string"

            elif token_type in Token.Comment:
                tag = "comment"

            elif token_type in Token.Name.Class:
                tag = "class"

            elif token_type in Token.Name.Function:
                tag = "function"

            if tag:

                self.text.tag_add(
                    tag,
                    start,
                    end
                )

    # =====================================================
    # LANGUAGE CONFIG
    # =====================================================
    def configure_language(self):

        self.text.tag_configure(
            "keyword",
            foreground="#569CD6"
        )

        self.text.tag_configure(
            "string",
            foreground="#CE9178"
        )

        self.text.tag_configure(
            "comment",
            foreground="#6A9955"
        )

        self.text.tag_configure(
            "class",
            foreground="#4EC9B0"
        )

        self.text.tag_configure(
            "function",
            foreground="#DCDCAA"
        )

        self.highlight()