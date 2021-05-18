from re import T
from time import time
from PyQt5 import QtWidgets
import sys
import threading
import socket
import UI
import math
import time

'''
@description: 实现服务端的逻辑
@param {*}
@return {*}
'''


class UdpServer(UI.UI):
    '''
    @description: 服务端中的变量初始化
    @param {*} self
    @return {*}
    '''

    def __init__(self):
        super(UdpServer, self).__init__()
        self.fileName = ''  # 文件名
        self.fp = None  # 写文件指针
        self.recvBytes = 0  # 已经接收到的文件大小
        self.totalBytes = 0  # 文件总大小
        self.bufferSize = 1024  # 缓冲窗口大小
        self.recvData = set()  # 已经得到的数据
        self.recvIndex = []  # 缓冲窗口
        self.udpRecv = None  # 用于接收数据包的socket
        self.udpAck = None  # 用于发送ack包的socket
        self.threadServer = None  # 用于接收数据包的线程
        self.threadInfo = None  # 用于打印进度的线程
        self.lock = threading.Lock()  # 互斥锁
        self.serverIP = None  # 服务端ip
        self.clientIP = None  # 客户端ip
        self.positions = 0  # 缓存窗口起始位置
        self.start = False  # 是否已经开始文件传输

    '''
    @description: 用于启动服务端
    @param {*} self
    @return {*}
    '''

    def serverStart(self):
        # 初始化接收数据的线程,设置守护线程,开启线程
        self.threadServer = threading.Thread(target=self.recvFile)
        self.threadServer.setDaemon(True)
        self.threadServer.start()

        # 初始化打印进度的线程,设置守护线程,开启线程
        self.threadInfo = threading.Thread(target=self.getServerInfo)
        self.threadInfo.setDaemon(True)
        self.threadInfo.start()
        self.recvMsgUI.emit("正在监听端口 "+str(self.port)+"\n")

    '''
    @description: 接收数据
    @param {*} self
    @return {*}
    '''

    def recvFile(self):
        index = 0  # 接收到数据包的序列号下标

        while True:
            data, clientAddress = self.udpRecv.recvfrom(1050)  # 接收数据包
            ackAddress = (clientAddress[0], 1078)  # 本地接收ack地址

            # 读取第一个数据包,包中的数据格式为start:filename:totalBytes
            if self.start == False and data.startswith(b'start'):
                _, self.fileName, self.totalBytes = str(data).split(':')

                # 获取文件相关信息
                self.totalBytes = int(self.totalBytes[0:-1], 10)

                # 初始化缓存窗口
                for i in range(self.bufferSize):
                    self.recvIndex.append(i)

                # 文本框输出相关信息
                self.textBrowserRecvUI.insertPlainText(
                    "接受文件 "+str(self.fileName)+"\n"
                )
                self.textBrowserRecvUI.insertPlainText(
                    "文件总大小为 "+str(round(self.totalBytes /
                                  (1024*1024), 2))+" MB\n"
                )

                # 开始进行传输
                self.start = True

                # 清空本地同名文件
                self.fp = open(self.fileName, 'wb+')
                self.fp.truncate()
                self.fp.close()

                # 确认文件传输
                for i in range(100):
                    self.udpAck.sendto(
                        ("start:"+self.fileName).encode(), ackAddress)

            # 继续接收数据包
            elif self.start == True and not data.startswith(b'start'):
                # 获取数据包序列号以及对应数据
                index, data = data.split(b':', maxsplit=1)
                index = int(index.decode())

                # 加锁更新缓存窗口并且写入数据
                self.lock.acquire()
                if index in self.recvIndex:
                    self.recvData.add((index, data))
                    self.recvIndex.remove(index)
                    self.recvBytes += len(data)

                # 返回对应序列号的ACK
                self.udpAck.sendto(
                    (str(index)+":"+str(len(data))+":ACK").encode(), ackAddress)
                self.lock.release()

            # 达到缓存上限或者接收完所有的数据包
            if self.start == 1 and len(self.recvData) != 0 \
                    and (len(self.recvIndex) == 0 or self.recvBytes >= self.totalBytes):
                # 加锁将二进制数据写入文件中
                self.lock.acquire()

                # 按照序列号进行排序
                writeData = sorted(
                    self.recvData, key=lambda data: data[0])
                self.fp = open(self.fileName, 'ab+')
                for data in writeData:
                    self.fp.write(data[1])
                self.fp.close()
                self.recvData.clear()

                # 更新缓存窗口及其初始位置
                self.positions = self.recvBytes//self.bufferSize
                for i in range(1024):
                    self.recvIndex.append(self.positions+i)
                self.lock.release()

            # 文件传输完成
            if self.recvBytes >= self.totalBytes and self.start == True:
                self.textBrowserRecvUI.insertPlainText(
                    "\n文件传输完成\n"
                )

                # 发送文件传输结束数据包
                self.lock.acquire()
                for i in range(100):
                    self.udpAck.sendto(
                        ("over:"+self.fileName).encode(), ackAddress)
                self.lock.release()
                self.closeMsgUI.emit("close")

    '''
    @description: 打印进度
    @param {*} self
    @return {*}
    '''

    def getServerInfo(self):
        begin = time.perf_counter()
        while True:
            if self.start == True:
                break
            continue
        while self.recvBytes < self.totalBytes:
            cnt1 = math.ceil(self.recvBytes*50/self.totalBytes)
            cnt2 = 50-cnt1
            a = '-'*cnt1
            b = ' '*cnt2
            c = (self.recvBytes/self.totalBytes)*100
            dur = time.perf_counter()-begin
            self.recvMsgUI.emit(
                "\r{:^3.0f}%[{}->{}]{:.2f}s".format(c, a, b, dur)
            )
            time.sleep(0.1)


if __name__ == '__main__':
    udpServer = UdpServer()
    udpServer.serverself.start()
