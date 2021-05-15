import clientUI
import serverUI
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QVBoxLayout
import sys
import socket
import threading
import time

'''
@Author: 张涛麟
@description: 启动程序的主窗口
@param {*}
@return {*}
'''
class MainWindow(clientUI.ClientUI,serverUI.ServerUI):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.linkUI.clicked.connect(self.clickLink)
        self.unlinkUI.clicked.connect(self.clickUnlink)
        self.sendUI.clicked.connect(self.clickSend)
        self.pathUI.clicked.connect(self.clickPath)

    def clickLink(self):
        if self.modeUI.currentIndex() == 0:
            self.clientClickLink()
        elif self.modeUI.currentIndex() == 1:
            self.serverClickLink()

    def clickUnlink(self):
        if self.modeUI.currentIndex() == 0:
            self.clientClickUnlink()
        elif self.modeUI.currentIndex() == 1:
            self.serverClickUnlink()

    def clickSend(self):
        if self.modeUI.currentIndex() == 0:
            self.clientClickSend()
        elif self.modeUI.currentIndex() == 1:
            self.serverClickSend()

    def clickPath(self):
        if self.modeUI.currentIndex() == 0:
            self.clientClickPath()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
