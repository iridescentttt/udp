import UI
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QVBoxLayout
import re
import threading
import socket
import time
import sys
import math

'''
@Author: 张涛麟
@description: 实现客户端的逻辑
'''


class UdpClient(UI.UI):
    '''
    @Author: 张涛麟
    @description: 初始化相关变量
    @param {*} self
    @return {*}
    '''

    def __init__(self):
        super(UdpClient, self).__init__()
        self.udpSend = None  # 发送数据的socket
        self.udpAck = None  # 接收ack的socket
        self.serverIP = ""  # 目标ip
        self.clientIP = ""  # 本机ip
        self.port = 0  # 目标端口
        self.serverAddress = None  # 目标主机地址
        self.ackAddress = None  # 本地监听ack的地址
        self.fileName = None  # 发送的文件名
        self.fp = None  # 读取文件的指针
        self.filePath = ""  # 发送的文件路径
        self.sendBytes = 0  # 已经发送的字节大小
        self.totalBytes = 0  # 发送文件总字节大小
        self.sendIndex = []  # 用于存储当前缓存中待发送数据包的位置
        self.threadAck = None  # 用于接收ack的线程
        self.threadSend = None  # 用于发送数据的线程
        self.threadInfo = None
        self.data = None  # 从文件中读取的数据
        self.positions = 0  # 当前缓存开始位置对应文件中的位置
        self.buffSize = 1024
        self.link = False
        self.lock = threading.Lock()
        self.closeLock = threading.RLock()
        self.start = False

    def clientStart(self):
        self.closeLock.acquire()
        self.fp = open(self.filePath, 'rb')
        self.data = self.fp.read()
        self.totalBytes = len(self.data)
        self.fileName = re.search('[^/]+$', self.filePath).group()
        self.sendMsgUI.emit(
            "文件总大小为 "+str(round(self.totalBytes/(1024*1024), 2))+" Mb\n"
        )
        self.sendMsgUI.emit("等待接受方连接\n")
        self.fp.close()
        for i in range(1024):
            self.sendIndex.append(i)
        self.threadAck = threading.Thread(target=self.recvAck)
        self.threadAck.setDaemon(True)
        self.threadAck.start()
        self.threadSend = threading.Thread(target=self.sendFile)
        self.threadSend.setDaemon(True)
        self.threadSend.start()
        self.threadInfo = threading.Thread(target=self.getInfo)
        self.threadInfo.setDaemon(True)
        self.threadInfo.start()

    def sendFile(self):
        # 发送文件基本信息,包含文件名以及需要传送的字节数
        while True:
            if self.start == True:
                break
            self.udpSend.sendto(
                f'start:{self.fileName}:{self.totalBytes}'.encode(), self.serverAddress)
            time.sleep(0.1)
        # 开始发送文件
        while self.sendBytes < self.totalBytes:
            while self.sendIndex and self.sendBytes < self.totalBytes:
                for index in self.sendIndex:
                    self.udpSend.sendto(
                        f'{index}:'.encode(
                        ) + self.data[index *
                                      self.buffSize:(index+1)*self.buffSize],
                        self.serverAddress)
                time.sleep(0.01)

            if self.sendBytes >= self.totalBytes:
                break

            # 重新添加待发送数据
            self.lock.acquire()

            self.positions = self.sendBytes//self.buffSize

            for i in range(1024):
                self.sendIndex.append(self.positions+i)
            self.lock.release()

            time.sleep(0.01)

        self.sendBytes = self.totalBytes = 0

    def recvAck(self):
        while True:
            data, _ = self.udpAck.recvfrom(1024)
            if data.startswith(b'over'):
                _, fileName = data.split(b':')
                fileName = fileName.decode()
                fileName = fileName.encode("utf-8").decode("utf-8")
                if fileName == self.fileName:
                    self.sendMsgUI.emit("传输完毕\n")
                    self.closeMsgUI.emit("close")
                    return
                continue
            elif data.startswith(b'start'):
                _, fileName = data.split(b':')
                fileName = fileName.decode()
                fileName = fileName.encode("utf-8").decode("utf-8")
                if self.start == False and fileName == self.fileName:
                    self.sendMsgUI.emit("接受方已连接,开始传输\n")
                    self.start = True
                continue
            index, length, _ = data.split(b':')
            index = int(index)
            length = int(length)
            self.lock.acquire()
            if index in self.sendIndex:
                self.sendIndex.remove(index)
                self.sendBytes += length
            self.lock.release()

    def getInfo(self):
        begin = time.perf_counter()
        while True:
            if self.start == True:
                break
            continue
        while self.sendBytes < self.totalBytes:
            cnt1 = math.ceil(self.sendBytes*50/self.totalBytes)
            cnt2 = 50-cnt1
            a = '-'*cnt1
            b = ' '*cnt2
            c = (self.sendBytes/self.totalBytes)*100
            dur = time.perf_counter()-begin
            self.sendMsgUI.emit(
                "\r{:^3.0f}%[{}->{}]{:.2f}s".format(c, a, b, dur)
            )
            time.sleep(0.1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    udpClient = UdpClient()
    udpClient.show()
    udpClient.filePath = input("请输入文件路径\n")
    sys.exit(app.exec_())
