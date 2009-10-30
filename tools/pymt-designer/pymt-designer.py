
import sys,os
os.environ['PYMT_SHADOW_WINDOW'] = 'False'

from PyQt4 import QtCore, QtGui, QtOpenGL
from OpenGL import GL
from syntaxhighlighter import Highlighter
from pymt import pymt_logger
from cStringIO import StringIO
from qtmtwindow import *
import pymt
import traceback
import os

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupFileMenu()
        self.setupEditor()
        self.setupToolbar()
        self.setupMTWindow()
        self.central_widget = QtGui.QWidget()
        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(self.editor)

        self.vlayout = QtGui.QVBoxLayout()
        self.vlayout.addWidget(self.toolbar)
        self.vlayout.addWidget(self.glWidget)
        self.vlayout.addWidget(self.console)
        self.layout.addLayout(self.vlayout)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle('PyMT Designer')

        self._update_toolbar_status()

    def setupToolbar(self):
        self.toolbar = QtGui.QToolBar()
        pixrun = QtGui.QPixmap('icons/player_play.png')
        pixstop = QtGui.QPixmap('icons/player_stop.png')
        pixpause = QtGui.QPixmap('icons/player_pause.png')
        self.act_run = self.toolbar.addAction(QtGui.QIcon(pixrun), 'Run', self.run)
        self.act_pause = self.toolbar.addAction(QtGui.QIcon(pixpause), 'Pause', self.pause)
        self.act_stop = self.toolbar.addAction(QtGui.QIcon(pixstop), 'Stop', self.stop)

    def setupFileMenu(self):
        fileMenu = QtGui.QMenu("&File", self)
        pymtMenu = QtGui.QMenu("&PyMT",self)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(pymtMenu)

        fileMenu.addAction("&New...", self.newFile, "Ctrl+N")
        fileMenu.addAction("&Open...", self.openFile, "Ctrl+O")
        fileMenu.addAction("&Save", self.saveFile, "Ctrl+S")
        fileMenu.addAction("Save As", self.saveFileAs, "Ctrl+Alt+S")
        fileMenu.addAction("E&xit", QtGui.qApp.quit, "Ctrl+Q")

        pymtMenu.addAction("&Run", self.run, "Ctrl+R")


    def setupMTWindow(self):
        pymt.pymt_config.set('modules', 'touchring', '')
        self.glWidget = QTMTWindow()


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
        self.editor.setMinimumSize(400,600)
        self.highlighter = Highlighter(self.editor.document())
        self.openFile('test.py')


    def newFile(self):
        self.editor.clear()
        self.current_file = None

    def openFile(self, path=None):
        if not path:
            path = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                    '', "PyMT Files (*.py *.xml)")

        if path:
            inFile = QtCore.QFile(path)
            if inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                text = inFile.readAll()
                text = str(text)
                self.editor.setPlainText(text)

        self.current_file = path
        self.setWindowTitle("PyMT Designer | "+path)



    def saveFile(self):
        self.saveFileAs(self.current_file)

    def saveFileAs(self, path=None):
        if not path:
            path = QtGui.QFileDialog.getSaveFileName(self, "Save File",
                    '', "PyMT Files (*.py *.xml)")

        outFile = QtCore.QFile(path)
        if outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            outFile.write(str(self.editor.toPlainText()))
        self.current_file = path



    def pause(self):
        if self.glWidget.is_paused:
            self.glWidget.play()
        else:
            self.glWidget.pause()
        self._update_toolbar_status()

    def stop(self):
        self.glWidget.stop()
        self._update_toolbar_status()

    def run(self):
        pymt.stopTouchApp()
        buff1 = StringIO()
        buff2 = StringIO()
        stdout = sys.stdout
        stderr = sys.stderr
        sys.stdout = buff1
        sys.stderr = buff2
        self.execute_pymt_code()
        self.console.setPlainText(buff1.getvalue() + buff2.getvalue())
        sys.stdout = stdout
        sys.stderr = stderr
        self._update_toolbar_status()

    def execute_pymt_code(self):
        oldRunApp = pymt.runTouchApp
        def designerRunTouchApp(w):
            oldRunApp(w, slave=True)
        pymt.runTouchApp = designerRunTouchApp

        try:
            self.glWidget.create_new_pymt_window()
            d = {}
            exec str(self.editor.toPlainText()) in d
            #pymt.stopTouchApp()
        except Exception as e:
            #pymt.pymt_logger.exception("Error Running PyMT Code:")
            traceback.print_exc()
        pymt.runTouchApp = oldRunApp

    def _update_toolbar_status(self):
        self.act_run.setVisible(not self.glWidget.is_running or
                                self.glWidget.is_paused)
        self.act_stop.setEnabled(self.glWidget.is_running)
        self.act_pause.setVisible(not self.act_run.isVisible())


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 512)
    window.show()
    sys.exit(app.exec_())

