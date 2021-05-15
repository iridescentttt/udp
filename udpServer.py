from re import T
from time import time
from PyQt5 import QtWidgets
import sys
import threading
import socket
import UI


class UdpServer(UI.UI):
    def __init__(self):
        super(UdpServer, self).__init__()
        self.udpRecv = None
        self.fileName = ''
        self.fp = None
        self.bufferSize = 1024
        self.recvData = set()
        self.recvIndex = []
        self.udpAck = None
        self.totalBytes = 0
        self.threadServer = None
        self.recvBytes = 0
        self.lock = threading.Lock()
        self.serverIP = None
        self.clientIP = None
        self.positions = 0
        self.start = False

    def serverStart(self):
        self.threadServer = threading.Thread(target=self.recvFile)
        self.threadServer.setDaemon(True)
        self.threadServer.start()
        self.recvMsgUI.emit("正在监听端口 "+str(self.port)+"\n")

    def recvFile(self):
        index = 0  # 接收到数据包的序列号下标

        while True:
            data, clientAddress = self.udpRecv.recvfrom(1050)  # 接收数据包
            ackAddress = (clientAddress[0], 1078)  # 本地接收ack地址
            # 读取第一个数据包,包中的数据格式为self.start_filename_totalBytes

            if self.start == False and data.startswith(b'start'):
                _, self.fileName, self.totalBytes = str(data).split('_')
                self.totalBytes = int(self.totalBytes[0:-1], 10)
                for i in range(1024):
                    self.recvIndex.append(i)
                self.textBrowserRecvUI.insertPlainText(
                    "接受文件 "+str(self.fileName)+"\n"
                )
                self.textBrowserRecvUI.insertPlainText(
                    "文件总大小为 "+str(round(self.totalBytes/(1024*1024), 2))+" Mb\n"
                )
                self.start = True
                self.fp = open(self.fileName, 'wb+')
                self.fp.truncate()
                self.fp.close()
                for i in range(100):
                    self.udpAck.sendto(
                        ("start_"+self.fileName).encode(), ackAddress)

            # 继续接收数据包
            elif self.start == True and not data.startswith(b'start'):
                index, data = data.split(b'_', maxsplit=1)
                index = int(index.decode())
                self.lock.acquire()
                if index in self.recvIndex:
                    self.recvData.add((index, data))
                    self.recvIndex.remove(index)
                    self.recvBytes += len(data)
                self.udpAck.sendto(
                    (str(index)+"_"+str(len(data))+"_ACK").encode(), ackAddress)
                self.lock.release()

            # 达到缓存上限或者接收完所有的数据包
            if self.start == 1 and len(self.recvData) != 0 \
                    and (len(self.recvIndex) == 0 or self.recvBytes >= self.totalBytes):
                self.lock.acquire()
                writeData = sorted(
                    self.recvData, key=lambda data: data[0])
                self.fp = open(self.fileName, 'ab+')
                for data in writeData:
                    self.fp.write(data[1])
                self.fp.close()
                self.recvData.clear()
                self.positions = self.recvBytes//self.bufferSize
                for i in range(1024):
                    self.recvIndex.append(self.positions+i)
                self.lock.release()

            if self.recvBytes >= self.totalBytes and self.start == True:
                self.textBrowserRecvUI.insertPlainText(
                    "文件传输完成\n"
                )
                self.lock.acquire()
                for i in range(100):
                    self.udpAck.sendto(
                        ("over_"+self.fileName).encode(), ackAddress)
                self.recvBytes = 0
                self.totalBytes = 0
                self.positions = 0
                self.recvIndex.clear()
                self.recvData.clear()
                self.start = False
                self.lock.release()
                self.closeMsgUI.emit("close")


if __name__ == '__main__':
    udpServer = UdpServer()
    udpServer.serverself.start()
