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
@description: 类UdpClient实现客户端的逻辑
'''


class UdpClient(UI.UI):

    '''
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
        self.sendIndex = []  # 缓存窗口数组
        self.threadAck = None  # 用于接收ack的线程
        self.threadSend = None  # 用于发送数据的线程
        self.threadInfo = None  # 用于打印进度的线程
        self.data = None  # 从文件中读取的数据
        self.positions = 0  # 当前缓存开始位置对应文件中的位置
        self.buffSize = 1024  # 缓冲区的大小,表示缓冲区中数据包的个数
        self.link = False  # 是否点下连接网络按钮
        self.lock = threading.Lock()  # 在多线程中关键变量的修改通过互斥锁实现
        self.start = False  # 是否开始文件传输

    '''
    @description: 开启客户端的服务
    @param {*} self
    @return {*}
    '''

    def clientStart(self):
        # 以二进制字节流方式读取待传输文件并初始化相关变量
        self.fp = open(self.filePath, 'rb')
        self.data = self.fp.read()
        self.totalBytes = len(self.data)

        # 正则表达式获取文件名
        self.fileName = re.search('[^/]+$', self.filePath).group()

        # 在文本框输出文件相关信息
        self.sendMsgUI.emit(
            "文件总大小为 "+str(round(self.totalBytes/(1024*1024), 2))+" Mb\n"
        )
        self.sendMsgUI.emit("等待接受方连接\n")

        # 关闭读取文件指针
        self.fp.close()

        # 初始化缓存窗口
        for i in range(self.buffSize):
            self.sendIndex.append(i)

        # 初始化监听ACK的线程,设置守护线程,开启线程
        self.threadAck = threading.Thread(target=self.recvAck)
        self.threadAck.setDaemon(True)
        self.threadAck.start()

        # 初始化发送数据的线程,设置守护线程,开启线程
        self.threadSend = threading.Thread(target=self.sendFile)
        self.threadSend.setDaemon(True)
        self.threadSend.start()

        # 初始化打印进度的线程,设置守护线程,开启线程
        self.threadInfo = threading.Thread(target=self.getClientInfo)
        self.threadInfo.setDaemon(True)
        self.threadInfo.start()

    '''
    @description: 发送数据
    @param {*} self
    @return {*}
    '''

    def sendFile(self):
        # 发送文件基本信息,包含文件名以及需要传送的字节数
        while True:
            # 没有收到确认信息就持续发送
            if self.start == True:
                break
            self.udpSend.sendto(
                f'start:{self.fileName}:{self.totalBytes}'.encode(), self.serverAddress)
            time.sleep(0.1)

        # 开始发送文件
        while self.sendBytes < self.totalBytes:
            # 缓存窗口有数据包需要发送就发送需要发送的数据包
            while self.sendIndex and self.sendBytes < self.totalBytes:
                for index in self.sendIndex:
                    self.udpSend.sendto(
                        f'{index}:'.encode(
                        ) + self.data[index *
                                      self.buffSize:(index+1)*self.buffSize],
                        self.serverAddress)
                time.sleep(0.01)

            # 文件传输结束退出发送过程
            if self.sendBytes >= self.totalBytes:
                break

            # 缓存窗口数据包成功被接收,使用互斥锁进行更新缓存窗口
            self.lock.acquire()

            # 更新缓存窗口起始位置
            self.positions = self.sendBytes//self.buffSize

            # 更新缓存窗口
            for i in range(self.buffSize):
                self.sendIndex.append(self.positions+i)

            # 释放互斥锁
            self.lock.release()

    '''
    @description: 接收ACK
    @param {*} self
    @return {*}
    '''

    def recvAck(self):
        while True:
            # 接收数据包
            data, _ = self.udpAck.recvfrom(1024)

            # 表示传输结束
            if data.startswith(b'over'):
                # 传输的文件名称
                _, fileName = data.split(b':')
                fileName = fileName.decode()

                if fileName == self.fileName:
                    # 文本框发送消息,结束传输
                    self.sendMsgUI.emit("\n传输完毕\n")
                    self.closeMsgUI.emit("close")
                    return
                continue

            # 表示数据传输开始
            elif data.startswith(b'start'):
                # 传输的文件名
                _, fileName = data.split(b':')
                fileName = fileName.decode()

                if self.start == False and fileName == self.fileName:
                    # 文本框发送消息,开始传输
                    self.sendMsgUI.emit("接受方已连接,开始传输\n")
                    self.start = True
                continue

            # 收到数据包的ack
            index, length, _ = data.split(b':')
            index = int(index)
            length = int(length)

            # 使用互斥锁进行缓存窗口的修改
            self.lock.acquire()
            if index in self.sendIndex:
                self.sendIndex.remove(index)  # 删除该序列号
                self.sendBytes += length  # 更新已经发送成功的长度
            self.lock.release()

    '''
    @description: 打印进度
    @param {*} self
    @return {*}
    '''

    def getClientInfo(self):
        begin = time.perf_counter()
        while True:
            # 尚未开始
            if self.start == True:
                break
            continue
        # 过程中打印进度
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
    sys.exit(app.exec_())
