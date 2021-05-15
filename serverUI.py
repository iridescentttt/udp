import udpServer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QVBoxLayout
import sys
import socket
import threading
import time


class ServerUI(udpServer.UdpServer):
    def __init__(self):
        super(ServerUI, self).__init__()

    def serverClickLink(self):
        try:
            self.port = int(self.portUI.text())
            self.serverIP = str(self.ipUI.text())
            self.clientIP = str(self.clientIPUI.text())
            self.serverAddress = (self.serverIP, self.port)
            self.ackAddress = (self.clientIP, 1078)
            self.udpRecv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udpAck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udpRecv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udpAck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udpRecv.bind(self.serverAddress)
        except Exception as e:
            print(e)
            self.recvMsgUI.emit("本机ip或者端口号错误, 请输入正确的本机ip和端口号\n")
            return
        else:
            self.link = True
            self.unlinkUI.setEnabled(True)
            self.linkUI.setEnabled(False)
            self.recvMsgUI.emit("网络已连接\n")
            self.serverStart()

    def serverClickUnlink(self):
        self.unlinkUI.setEnabled(False)
        self.linkUI.setEnabled(True)
        self.recvMsgUI.emit("网络已断开\n")
        self.udpRecv.close()
        self.udpAck.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    serverUI = ServerUI()
    serverUI.show()
    sys.exit(app.exec_())
