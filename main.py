import clientUI
import serverUI
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QVBoxLayout
import sys
import socket
import threading
import time

'''
@description: 启动程序的主窗口
@param {*}
@return {*}
'''


class MainWindow(clientUI.ClientUI, serverUI.ServerUI):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.linkUI.clicked.connect(self.clickLink)
        self.unlinkUI.clicked.connect(self.clickUnlink)
        self.sendUI.clicked.connect(self.clickSend)
        self.pathUI.clicked.connect(self.clickPath)

    '''
    @description: 按下link按钮
    @param {*} self
    @return {*}
    '''

    def clickLink(self):
        if self.modeUI.currentIndex() == 0:
            self.clientClickLink()
        elif self.modeUI.currentIndex() == 1:
            self.serverClickLink()

    '''
    @description: 按下unlink按钮
    @param {*} self
    @return {*}
    '''

    def clickUnlink(self):
        if self.modeUI.currentIndex() == 0:
            self.clientClickUnlink()
        elif self.modeUI.currentIndex() == 1:
            self.serverClickUnlink()

    '''
    @description: 按下send按钮
    @param {*} self
    @return {*}
    '''

    def clickSend(self):
        if self.modeUI.currentIndex() == 0:
            self.clientClickSend()
        elif self.modeUI.currentIndex() == 1:
            self.serverClickSend()

    '''
    @description: 按下path按钮
    @param {*} self
    @return {*}
    '''

    def clickPath(self):
        if self.modeUI.currentIndex() == 0:
            self.clientClickPath()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
