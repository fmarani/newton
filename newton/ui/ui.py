import sys
import asyncio
import time
import os

from PyQt5.QtWidgets import QApplication
from PyQt5.uic import loadUi
from quamash import QEventLoop, QThreadExecutor

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QTextEdit, QWidget

from newton.core import get_unified_timeline


stylesheet = """
.entity {
    background-color: white;
}
"""

from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import time

class Worker(QObject):
    refreshing = pyqtSignal()
    newdata = pyqtSignal(list)

    @pyqtSlot()
    def updater(self):
        time.sleep(1)
        self.intReady.emit(i)
        timeline = await get_unified_timeline()
        newton.update_timeline(timeline)

        self.finished.emit()

class Newton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.mainLayout = QGridLayout()
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Newton")
        self.setStyleSheet(stylesheet)

    def displayable_entity(self, entity):
        if entity['type'] == "newt":
            return QLabel("{:%Y-%m-%d %H:%M} {} {}".format(entity['datetime'], entity['handle'], entity['msg']))
        elif entity['type'] == "renewt":
            return QLabel("{:%Y-%m-%d %H:%M} {} Renewt: {}".format(entity['datetime'], entity['handle'], entity['renewtUrl']))
        elif entity['type'] == "like":
            return QLabel("{:%Y-%m-%d %H:%M} {} Like: {}".format(entity['datetime'], entity['handle'], entity['likeUrl']))
        elif entity['type'] == "reply":
            return QLabel("{:%Y-%m-%d %H:%M} {} {} in reply to: {}".format(entity['datetime'], entity['handle'], entity['msg'], entity['replyToUrl']))
        else:
            return QLabel("skipping unrecognized msg type")

    def update_timeline(self, timeline):
        t = [self.displayable_entity(x) for x in timeline]

        for i, x in enumerate(t):
            x.setProperty("class", "entity")
            self.mainLayout.addWidget(x, i, 0)

newton = None

def init():
    global newton
    app = QApplication(sys.argv)
    newton = Newton()
    newton.show()

def master(loop):
    with QThreadExecutor(1) as exec:
        yield from loop.run_in_executor(exec, updater, loop)

def updater(loop):
    #sys.exit(app.exec_())
    while True:
        print("UI cycle")
        asyncio.sleep(5000, loop=loop)
        timeline = await get_unified_timeline()
        newton.update_timeline(timeline)
