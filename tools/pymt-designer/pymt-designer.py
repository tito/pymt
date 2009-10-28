from PyQt4 import QtCore, QtGui, QtOpenGL
from OpenGL import GL
from syntaxhighlighter import Highlighter
from qtmtwindow import MTWindow
from pymt import pymt_logger
from cStringIO import StringIO
import sys

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupFileMenu()
        self.setupEditor()
        self.setupMTWindow()
        self.central_widget = QtGui.QWidget()
        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(self.editor)
        
        self.vlayout = QtGui.QVBoxLayout()
        self.vlayout.addWidget(self.glWidget)
        self.vlayout.addWidget(self.console)
        self.layout.addLayout(self.vlayout)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Syntax Highlighter")

    def newFile(self):
        self.editor.clear()

    def openFile(self, path=None):
        if not path:
            path = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                    '', "PyMT Files (*.py *.xml)")

        if path:
            inFile = QtCore.QFile(path)
            if inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                text = inFile.readAll()

                try:
                    # Python v3.
                    text = str(text, encoding='ascii')
                except TypeError:
                    # Python v2.
                    text = str(text)

                self.editor.setPlainText(text)

    def setupMTWindow(self):
        self.glWidget = MTWindow()

    def setupEditor(self):
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)

        self.editor = QtGui.QTextEdit()
        self.console = QtGui.QTextEdit()
        self.console.readOnly = True
        self.console.setFont(font)
        self.editor.setFont(font)

        self.highlighter = Highlighter(self.editor.document())

    def run(self):
        buff = StringIO()
        stdout = sys.stdout
        sys.stdout = buff
        try:
            exec str(self.editor.toPlainText())
        except:
            sys.stderr = buff
            pymt_logger.exception("Error executing code:")
        print "printing this"
        sys.stdout = stdout
        self.console.setPlainText(buff.getvalue())
        print "buff", buff.getvalue()


    def setupFileMenu(self):
        fileMenu = QtGui.QMenu("&File", self)
        self.menuBar().addMenu(fileMenu)

        fileMenu.addAction("&New...", self.newFile, "Ctrl+N")
        fileMenu.addAction("&Open...", self.openFile, "Ctrl+O")
        fileMenu.addAction("&Run", self.run, "Ctrl+R")
        fileMenu.addAction("E&xit", QtGui.qApp.quit, "Ctrl+Q")





if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 512)
    window.show()
    sys.exit(app.exec_())

