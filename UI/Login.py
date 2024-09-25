# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Login.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from Scripts.Utils import dict_result, get_config_path, resource_path
import websocket
import requests
import json
import threading
import time

class Login_Ui(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(350, 500)
        Dialog.setStyleSheet("background-color: rgb(255, 255, 255);")
        Dialog.setWindowIcon(QtGui.QIcon(resource_path("UI\\Image\\favicon.ico")))
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setStyleSheet("color: rgb(0, 0, 0);\n"
"font: 16pt \"微软雅黑\";")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setStyleSheet("font: 8pt \"微软雅黑\";\n"
"color: rgb(255, 0, 0);")
        self.label_2.setTextFormat(QtCore.Qt.AutoText)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.verticalLayout_2.setStretch(0, 2)
        self.verticalLayout_2.setStretch(1, 1)
        self.verticalLayout.addWidget(self.widget)
        self.widget_2 = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.QRcode = QtWidgets.QLabel(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.QRcode.sizePolicy().hasHeightForWidth())
        self.QRcode.setSizePolicy(sizePolicy)
        self.QRcode.setMaximumSize(QtCore.QSize(256, 256))
        self.QRcode.setText("")
        self.QRcode.setScaledContents(True)
        self.QRcode.setObjectName("QRcode")
        self.horizontalLayout.addWidget(self.QRcode)
        self.horizontalLayout.setStretch(0, 1)
        self.verticalLayout.addWidget(self.widget_2)
        self.widget_3 = QtWidgets.QWidget(Dialog)
        self.widget_3.setObjectName("widget_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.login_return = QtWidgets.QLabel(self.widget_3)
        self.login_return.setText("")
        self.login_return.setObjectName("login_return")
        self.login_return.setAlignment(QtCore.Qt.AlignCenter)
        self.login_return.setStyleSheet("color: rgb(255, 0, 0);")
        self.verticalLayout_3.addWidget(self.login_return)
        self.verticalLayout.addWidget(self.widget_3)
        self.verticalLayout.setStretch(0, 3)
        self.verticalLayout.setStretch(1, 10)
        self.verticalLayout.setStretch(2, 1)
        # 开启扫码登录所需的websocket连接
        self.start_wssapp(Dialog)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def _flush_login_QRcode(self):
        # 刷新登录二维码，单独线程运行
        count = 0
        # 便于退出的sleep
        while self.flush_on:
            if count == 60:
                count = 0
                data={"op":"requestlogin","role":"web","version":1.4,"type":"qrcode","from":"web"}
                self.wsapp.send(json.dumps(data))
            else:
                time.sleep(1)
                count += 1

    def close_all(self):
        # 关闭websocket连接
        self.flush_on = False
        self.wsapp.close()
        self.flush_t.join()

    def load_config(self, config):
        # 载入配置文件
        self.config = config

    def save(self, sessionid):
        # 保存sessionid
        config = self.config
        config["sessionid"] = sessionid
        config_path = get_config_path()
        with open(config_path,"w+") as f:
            json.dump(config, f)

    def start_wssapp(self, Dialog):
        def on_open(wsapp):
            data={"op":"requestlogin","role":"web","version":1.4,"type":"qrcode","from":"web"}
            wsapp.send(json.dumps(data))

        def on_close(wsapp):
            print("closed")

        def on_message(wsapp, message):
            data = dict_result(message)
            # 二维码刷新
            if data["op"] == "requestlogin":
                img = requests.get(url=data["ticket"],proxies={"http": None,"https":None}).content
                img_pixmap = QtGui.QPixmap()
                img_pixmap.loadFromData(img)
                self.QRcode.setPixmap(img_pixmap)
            # 扫码且登录成功
            elif data["op"] == "loginsuccess":
                web_login_url = "https://pro.yuketang.cn/pc/web_login"
                login_data = {
                    "UserID":data["UserID"],
                    "Auth":data["Auth"]
                }
                headers = {
                    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"
                }
                login_data = json.dumps(login_data)
                # 使用Auth和UserID正式登录获取sessionid
                r = requests.post(url=web_login_url,data=login_data,headers=headers,proxies={"http": None,"https":None})
                sessionid = dict(r.cookies)["sessionid"]
                config = self.config
                config["sessionid"] = sessionid
                self.save(sessionid)
                Dialog.accept()
        login_wss_url = "wss://pro.yuketang.cn/wsapp/"
        # 开启websocket线程和定时刷新二维码线程
        self.wsapp = websocket.WebSocketApp(url=login_wss_url,on_open=on_open,on_message=on_message,on_close=on_close)
        self.wsapp_t = threading.Thread(target=self.wsapp.run_forever,daemon=True)
        self.wsapp_t.start()
        self.flush_on = True
        self.flush_t = threading.Thread(target=self._flush_login_QRcode,daemon=True)
        self.flush_t.start()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "登录"))
        self.label.setText(_translate("Dialog", "微信扫码登录荷塘雨课堂"))
        self.label_2.setText(_translate("Dialog", "注：扫码登录仅用于获取您的登录状态以便软件监听荷塘雨课堂信息。"))
