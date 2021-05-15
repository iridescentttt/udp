from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QVBoxLayout
import sys

'''
@description: 使用PyQt5构造UI界面
@param {*}
@return {*}
@author: 张涛麟
'''


class UI(QDialog):
    recvMsgUI = QtCore.pyqtSignal(str)
    sendMsgUI = QtCore.pyqtSignal(str)
    closeMsgUI = QtCore.pyqtSignal(str)

    def __init__(self):
        super(UI, self).__init__()

        # 默认属性
        self.setObjectName('UDP')
        self.resize(640, 480)
        self.setAcceptDrops(False)
        self.setSizeGripEnabled(False)
        self.setWindowTitle('UDP')
        self._translate = QtCore.QCoreApplication.translate

        # 定义控件
        self.linkUI = QtWidgets.QPushButton()
        self.unlinkUI = QtWidgets.QPushButton()
        self.sendUI = QtWidgets.QPushButton()
        self.pathUI = QtWidgets.QPushButton()
        self.labelPortUI = QtWidgets.QLabel()
        self.labelIPUI = QtWidgets.QLabel()
        self.labelRecvUI = QtWidgets.QLabel()
        self.labelPathUI = QtWidgets.QLabel()
        self.labelSendUI = QtWidgets.QLabel()
        self.labelModeUI = QtWidgets.QLabel()
        self.labelClientIPUI = QtWidgets.QLabel()
        self.portUI = QtWidgets.QLineEdit()
        self.ipUI = QtWidgets.QLineEdit()
        self.clientIPUI = QtWidgets.QLineEdit()
        self.textBrowserSendUI = QtWidgets.QTextBrowser()
        self.textBrowserRecvUI = QtWidgets.QTextBrowser()
        self.modeUI = QtWidgets.QComboBox()
        self.labelModeUI.setFixedSize(QtCore.QSize(50, 40))
        self.modeUI.setFixedSize(QtCore.QSize(248, 40))

        # 选择模式
        self.modeUI.addItem("")
        self.modeUI.addItem("")

        # 定义布局
        self.hBox1 = QHBoxLayout()
        self.hBox2 = QHBoxLayout()
        self.hBox3 = QHBoxLayout()
        self.hBox4 = QHBoxLayout()
        self.hBox5 = QHBoxLayout()
        self.hBoxAll = QHBoxLayout()
        self.vBoxSet = QVBoxLayout()
        self.vBoxSend = QVBoxLayout()
        self.vBox = QVBoxLayout()

        # 设置字体
        font = QtGui.QFont()
        font.setFamily("Yuppy TC")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.labelRecvUI.setFont(font)
        self.labelSendUI.setFont(font)

        # 设置初始属性
        self.unlinkUI.setEnabled(False)
        self.textBrowserRecvUI.hide()

        # 链接函数
        self.modeUI.currentIndexChanged.connect(self.modeChange)
        self.layout_ui()
        self.uiTranslate()
        self.recvMsgUI.connect(self.writeRecvMsg)
        self.sendMsgUI.connect(self.writeSendMsg)
        self.closeMsgUI.connect(self.writeCloseMsg)
    '''
    @description: 控件的布局
    @param {*} self
    @return {*}
    @author: 张涛麟
    '''

    def layout_ui(self):
        self.hBox1.addWidget(self.labelModeUI)
        self.hBox1.addWidget(self.modeUI, alignment=QtCore.Qt.AlignLeft)
        self.hBox1.addWidget(self.labelClientIPUI,
                             alignment=QtCore.Qt.AlignLeft)
        self.hBox1.addWidget(self.clientIPUI)
        self.hBox2.addWidget(self.labelIPUI)
        self.hBox2.addWidget(self.ipUI)
        self.hBox2.addWidget(self.labelPortUI)
        self.hBox2.addWidget(self.portUI)
        self.hBox3.addWidget(self.linkUI)
        self.hBox3.addWidget(self.unlinkUI)
        self.hBox4.addWidget(self.pathUI)
        self.hBox4.addWidget(self.sendUI)
        self.hBox5.addWidget(self.labelPathUI)
        self.vBoxSet.addLayout(self.hBox1)
        self.vBoxSet.addLayout(self.hBox2)
        self.vBoxSet.addLayout(self.hBox3)
        self.vBoxSet.addLayout(self.hBox4)
        self.vBoxSet.addLayout(self.hBox5)
        self.vBoxSend.addWidget(self.labelSendUI)
        self.vBoxSend.addWidget(self.textBrowserSendUI)
        self.vBoxSend.addWidget(self.textBrowserRecvUI)
        self.vBox.addLayout(self.vBoxSet)
        self.vBox.addLayout(self.vBoxSend)

        # 将左右布局添加到窗体布局
        self.hBoxAll.addLayout(self.vBox)
        self.hBoxAll.addLayout(self.vBox)

        # 设置窗体布局到窗体
        self.setLayout(self.hBoxAll)

    '''
    @description: 用于添加文字
    @param {*} self
    @return {*}
    @author: 张涛麟
    '''

    def uiTranslate(self):
        self.labelModeUI.setText(self._translate("UDP", "模式:"))
        self.linkUI.setText(self._translate("UDP", "连接网络"))
        self.unlinkUI.setText(self._translate("UDP", "断开网络"))
        self.sendUI.setText(self._translate("UDP", "发送"))
        self.pathUI.setText(self._translate("UDP", "选择路径"))
        self.labelIPUI.setText(self._translate("UDP", "目标IP:"))
        self.labelPortUI.setText(self._translate("UDP", "目标端口:"))
        self.labelRecvUI.setText(self._translate("UDP", "接收区域"))
        self.labelSendUI.setText(self._translate("UDP", "状态"))
        self.labelPathUI.setText(self._translate("UDP", "已选择文件:\n"))
        self.labelClientIPUI.setText(self._translate("UDP", "本机ip"))
        self.modeUI.setItemText(0, self._translate("UDP", "UDP 客户端"))
        self.modeUI.setItemText(1, self._translate("UDP", "UDP 服务端"))
    '''
    @description: 模式切换时界面切换
    @param {*} self
    @return {*}
    @author: 张涛麟
    '''

    def modeChange(self):
        if self.modeUI.currentIndex() == 0:
            self.textBrowserRecvUI.hide()
            self.textBrowserSendUI.show()
            self.ipUI.show()
            self.labelIPUI.setText(self._translate("UDP", "目标IP:"))
            self.labelPortUI.setText(self._translate("UDP", "目标端口:"))
            self.labelPathUI.setText(self._translate("UDP", "已选择路径:\n"))
            self.sendUI.show()
            self.pathUI.show()
            self.labelPathUI.show()
            self.unlinkUI.setEnabled(False)
            self.linkUI.setEnabled(True)
            self.clientIPUI.show()
            self.labelClientIPUI.show()

        if self.modeUI.currentIndex() == 1:
            self.textBrowserRecvUI.show()
            self.textBrowserSendUI.hide()
            self.labelIPUI.setText(self._translate(
                "UDP", "本机IP:"))
            self.labelPortUI.setText(self._translate("UDP", "本机端口:"))
            self.labelPathUI.setText(self._translate("UDP", "已选择路径:\n"))
            self.sendUI.hide()
            self.pathUI.hide()
            self.labelPathUI.hide()
            self.unlinkUI.setEnabled(False)
            self.linkUI.setEnabled(True)
            self.clientIPUI.hide()
            self.labelClientIPUI.hide()

    def writeRecvMsg(self, msg):
        self.textBrowserRecvUI.insertPlainText(msg)
        # 滚动条移动到结尾
        self.textBrowserRecvUI.moveCursor(QtGui.QTextCursor.End)

    def writeSendMsg(self, msg):
        self.textBrowserSendUI.insertPlainText(msg)
        # 滚动条移动到结尾
        self.textBrowserSendUI.moveCursor(QtGui.QTextCursor.End)

    def writeCloseMsg(self, msg):
        print(msg)
        if msg == "close":
            self.close()

    def closeEvent(self, event):
        close = QtWidgets.QMessageBox()
        # 设置提示框的标题
        close.setWindowTitle('文件传输完成')
        # 设置提示框的内容
        close.setText('文件传输完毕,自动退出程序')
        close.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = UI()
    ui.show()
    sys.exit(app.exec_())
