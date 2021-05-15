import UI
import udpClient
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QVBoxLayout
import sys
import socket
import threading
import time


class ClientUI(udpClient.UdpClient):
    def __init__(self):
        super(ClientUI, self).__init__()

    def clientClickLink(self):
        try:
            self.port = int(self.portUI.text())
            self.serverIP = str(self.ipUI.text())
            self.clientIP = str(self.clientIPUI.text())
            self.serverAddress = (self.serverIP, self.port)
            self.ackAddress = (self.clientIP, 1078)
            self.udpSend = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM
            )
            self.udpAck = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM
            )
            self.udpSend.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udpAck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udpAck.bind(self.ackAddress)
        except Exception as e:
            print(e)
            self.sendMsgUI.emit("目标ip或者端口号错误, 请输入正确的目标ip和端口号\n")
            self.sendMsgUI.emit("请确保本机1078号端口未被占用\n")
            return
        else:
            self.link = True
            self.unlinkUI.setEnabled(True)
            self.linkUI.setEnabled(False)
            if self.modeUI.currentIndex() == 0:
                self.sendMsgUI.emit("网络已连接\n")
            elif self.modeUI.currentIndex() == 1:
                self.recvMsgUI.emit("网络已连接\n")

    def clientClickUnlink(self):
        self.unlinkUI.setEnabled(False)
        self.linkUI.setEnabled(True)
        self.sendMsgUI.emit("网络已断开\n")
        self.udpSend.close()
        self.udpAck.close()

    def clientClickSend(self):
        if self.link == False:
            self.sendMsgUI.emit("未连接网络\n")
        elif self.filePath == "":
            self.sendMsgUI.emit("请选择文件\n")
        else:
            self.unlinkUI.setEnabled(False)
            self.linkUI.setEnabled(False)
            self.clientStart()

    def clientClickPath(self):
        self.filePath = QtWidgets.QFileDialog.getOpenFileName(
            self, "获取文件路径", './')[0]
        if self.filePath:
            self.labelPathUI.setText(self._translate(
                "UDP", f"已选择文件: {self.filePath}\n"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    clientUI = ClientUI()
    clientUI.show()
    sys.exit(app.exec_())
