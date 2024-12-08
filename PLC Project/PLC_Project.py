import sys
import os
import re

from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from io import StringIO

import contextlib
 
class PythonIDE(QMainWindow):
    def __init__(self):
        super(PythonIDE, self).__init__()
 
        self.initUI()
 
    def initUI(self):

        self.current_file = None        
        self.setWindowTitle('Python IDE')
        self.resize(800, 600)

        self.set_up_body()

        self.show()

    def set_up_body(self):
        self.frame = QFrame(self)
        self.frame.setStyleSheet("QWidget { background-color: #ffeaea}")

        self.lyt = QVBoxLayout()

        self.frame.setLayout(self.lyt)
        self.setCentralWidget(self.frame)

        self.myFont = QFont("Helvetica")
        self.myFont.setPointSize(12)

        self.lyt.addWidget(self.set_up_menu())

        # ! Make instance of QSciScintilla class
        self.editor = QsciScintilla()
        self.editor.setLexer(None)            # We install lexer later
        self.editor.setUtf8(True)             # Set encoding to UTF-8
        self.editor.setFont(self.myFont)    # Gets overridden by lexer later on

        # 1. Text wrapping
        self.editor.setWrapMode(QsciScintilla.WrapWord)
        self.editor.setWrapVisualFlags(QsciScintilla.WrapFlagByText)
        self.editor.setWrapIndentMode(QsciScintilla.WrapIndentIndented)

        # 2. End-of-line mode
        self.editor.setEolMode(QsciScintilla.EolWindows)
        self.editor.setEolVisibility(False)

        # 3. Indentation
        self.editor.setIndentationsUseTabs(False)
        self.editor.setTabWidth(4)
        self.editor.setIndentationGuides(True)
        self.editor.setTabIndents(True)
        self.editor.setAutoIndent(True)

        # 4. Caret
        self.editor.setCaretForegroundColor(QColor("#b90000"))
        self.editor.setCaretLineVisible(True)
        self.editor.setCaretLineBackgroundColor(QColor("#f0f0f0"))
        self.editor.setCaretWidth(2)

        # 5. Margins
        self.editor.setMarginType(0, QsciScintilla.NumberMargin)
        self.editor.setMarginWidth(0, "0000")
        self.editor.setMarginsForegroundColor(QColor("#0a6912"))

        self.lyt.addWidget(self.editor)

        # Add/style widget for code output
        self.output_widget = QTextEdit(self)
        self.output_widget.setReadOnly(True)
        self.output_widget.setPlainText("Results shown here")
        self.output_widget.setStyleSheet("QTextEdit { background-color: #ffffff; border-radius: 5px}")

        self.lyt.addWidget(self.output_widget)
 
        # Add/style run button
        self.run_button = QPushButton('Run', self)
        self.run_button.setStyleSheet("QPushButton { background-color: #ffffff; border-radius: 5px; padding: 5px} QPushButton:hover {background-color: #aaaaaa}")
        self.run_button.clicked.connect(self.run_code)

        self.lyt.addWidget(self.run_button)

        self.lexer = MyLexer(self.editor)
        self.editor.setLexer(self.lexer)

    def set_up_menu(self):
        menu_bar = self.menuBar()

        #File Menu
        file_menu = menu_bar.addMenu("File")

        save_file = file_menu.addAction("Save")
        save_file.setShortcut("Ctrl+S")
        save_file.triggered.connect(self.save_file)

        save_as = file_menu.addAction("Save As")
        save_as.setShortcut("Ctrl+Shift+S")
        save_as.triggered.connect(self.save_as)

        #Color Menu
        color_menu = menu_bar.addMenu("Colors")

        change_color = color_menu.addAction("Change Syntax Colors")
        change_color.setShortcut("Ctrl+L")
        change_color.triggered.connect(self.change_color)

    def save_file(self):
        if self.current_file is None:
            self.save_as()

        else:
            editor = self.editor
            self.current_file.write_text(editor.text())
            self.statusBar().showMessage(f"Saved {self.current_file.name}", 2000)

    def save_as(self):
        editor = self.editor

        if editor is None:
            return

        file_path = QFileDialog.getSaveFileName(self, "Save As", os.getcwd())[0]

        if file_path == '':
            self.statusBar().showMessage("Cancelled", 2000)
            return

        path = Path(file_path)
        path.write_text(editor.text())
        self.statusBar().showMessage(f"Saved {path.name}", 2000)
        self.current_file = path

    def change_color(self):
        self.popup = Popup()

        self.popup.setAttribute(Qt.WA_DeleteOnClose)

        self.popup.show()

        loop = QEventLoop()

        self.popup.destroyed.connect(loop.quit)

        loop.exec()

        self.lexer = MyLexer(self.editor)
        self.editor.setLexer(self.lexer)
 
    def run_code(self):
        code = self.editor.text()
        output_stream = StringIO()
         
        with contextlib.redirect_stdout(output_stream):
            try:
                exec(code)
            except Exception as e:
                print(e)
 
        output = output_stream.getvalue()
        self.output_widget.setPlainText(output)

# Popup window for changing syntax colors
class Popup(QWidget):

    def __init__(self):
        super(Popup, self).__init__()

        mainLayout = QVBoxLayout()
        
        self.setWindowTitle("Change Colors")

        self.setGeometry(100, 100, 300, 400)

        self.formGroupBox = QGroupBox("Choose group and color")

        # Syntax group selector
        self.groupComboBox = QComboBox()
        self.groupComboBox.addItems(["Default Text", "Class & Def", "Keywords", "Braces", "Strings", "Comments"])

        # Example text
        self.colorLabel = QLabel()
        self.colorLabel.setText("Example Text")

        # Color selector button
        self.colorButton = QPushButton("Choose color", self)
        self.colorButton.clicked.connect(self.on_click)

        self.createForm()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.buttonBox.accepted.connect(self.changeColor)

        self.buttonBox.rejected.connect(self.reject)

        mainLayout.addWidget(self.formGroupBox)

        mainLayout.addWidget(self.buttonBox)

        self.setLayout(mainLayout)

    # Opens popup to select color
    def openColorDialog(self):
        self.user_color = str(QColorDialog.getColor().name())

        self.colorLabel.setStyleSheet("QLabel {color: " + f"{self.user_color}" + "}")

    def on_click(self):
        self.openColorDialog()

    # Sets the global variable in class MyLexer to the user's chosen color/group combo
    def changeColor(self):

        userGroup = self.groupComboBox.currentText()

        match userGroup:
            case "Default Text":
                MyLexer.default_color = self.user_color

            case "Class & Def":
                MyLexer.class_color = self.user_color

            case "Keywords":
                MyLexer.keyword_color = self.user_color
            
            case "Braces":
                MyLexer.braces_color = self.user_color

            case "Strings":
                MyLexer.string_color = self.user_color

            case "Comments":
                MyLexer.comment_color = self.user_color

            case _:
                print("Error")

        self.close()

    def reject(self):
        self.close()

    def createForm(self):
        layout = QFormLayout()

        layout.addRow(QLabel("Group"), self.groupComboBox)

        layout.addRow(QLabel("Color Preview: "), self.colorLabel)

        layout.addRow(self.colorButton)

        self.formGroupBox.setLayout(layout)
        

class MyLexer(QsciLexerCustom):
    
    default_color = "#000000"
    keyword_color = "#ff0000"
    braces_color = "#bb03cc"
    comment_color = "#0c8d00"
    string_color = "#df6c00"
    class_color = "#0c1ba5"

    def __init__(self, parent):
        super(MyLexer, self).__init__(parent)
        # Default text settings
        self.setDefaultColor(QColor("#ff000000"))
        self.setDefaultPaper(QColor("#ffffffff"))
        self.setDefaultFont(QFont("Helvetica", 12))

        # Initialize colors per style
        self.setColor(QColor(self.default_color), 0)   # Style 0: black
        self.setColor(QColor(self.keyword_color), 1)   # Style 1: red
        self.setColor(QColor(self.braces_color), 2)   # Style 2: purple
        self.setColor(QColor(self.comment_color), 3)   # Style 3: green
        self.setColor(QColor(self.string_color), 4)   # Style 4: orange
        self.setColor(QColor(self.class_color), 5)   # Style 5: blue

        # Initialize paper colors per style
        self.setPaper(QColor("#ffffffff"), 0)   # Style 0: white
        self.setPaper(QColor("#ffffffff"), 1)   # Style 1: white
        self.setPaper(QColor("#ffffffff"), 2)   # Style 2: white
        self.setPaper(QColor("#ffffffff"), 3)   # Style 3: white
        self.setPaper(QColor("#ffffffff"), 4)   # Style 4: white
        self.setPaper(QColor("#ffffffff"), 5)   # Style 5: white

        # Initialize fonts per style
        self.setFont(QFont("Helvetica", 12), 0)   # Style 0: Helvetica 12pt
        self.setFont(QFont("Helvetica", 12), 1)   # Style 1: Helvetica 12pt
        self.setFont(QFont("Helvetica", 12), 2)   # Style 2: Helvetica 12pt
        self.setFont(QFont("Helvetica", 12), 3)   # Style 3: Helvetica 12pt
        self.setFont(QFont("Helvetica", 12), 4)   # Style 4: Helvetica 12pt
        self.setFont(QFont("Helvetica", 12), 5)   # Style 5: Helvetica 12pt

    def language(self):
        return "SimpleLanguage"

    def description(self, style):
        if style == 0:
            return "myStyle_0"
        elif style == 1:
            return "myStyle_1"
        elif style == 2:
            return "myStyle_2"
        elif style == 3:
            return "myStyle_3"
        elif style == 4:
            return "myStyle_4"
        elif style == 5:
            return "myStyle_5"
        ###
        return ""

    def styleText(self, start, end):
        # 1. Initialize the styling procedure
        self.startStyling(start)

        # 2. Slice out a part from the text
        text = self.parent().text()[start:end]

        # 3. Tokenize the text
        p = re.compile(r"\s+|\w+|\W")

        # 'token_list' is a list of tuples: (token_name, token_len)
        token_list = [ (token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]

        # 4. Style the text
        comm_flag = False
        string_flag = False
        
        # 4.2 Style the text in a loop
        for i, token in enumerate(token_list):
            if string_flag:
                self.setStyling(token[1], 4)
                if token[0] == "'" or token[0] == '"':
                    string_flag = False
                continue

            if comm_flag:
                self.setStyling(token[1], 3)
                if token[0].startswith("\n"):
                    comm_flag = False
                continue

            else:
                if token[0] in ["for", "while", "return", "False", "None", "True", "and", "as", "break", "continue", "elif", "else", "from", "global", "if", "import", "in", "not", "or", "try", "with"]:
                    # Red style
                    self.setStyling(token[1], 1)
                elif token[0] in ["class", "def"]:
                    # Blue style
                    self.setStyling(token[1], 5)
                elif token[0] in ["(", ")", "{", "}", "[", "]"]:
                    # Purple style
                    self.setStyling(token[1], 2)
                elif token[0] in ['"', "'"]:
                    # Orange Style
                    self.setStyling(token[1], 4)
                    string_flag = True
                elif token[0] == "#":
                    # Green Style
                    self.setStyling(token[1], 3)
                    comm_flag = True
                else:
                    # Default style
                    self.setStyling(token[1], 0)
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ide = PythonIDE()
    ide.show()
    sys.exit(app.exec_())