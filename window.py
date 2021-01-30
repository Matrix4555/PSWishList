from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(390, 650)
        MainWindow.setMinimumSize(390, 650)
        MainWindow.setMaximumSize(390, 650)
        MainWindow.setStyleSheet(setCSS())
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.line = QtWidgets.QLineEdit(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(10, 10, 260, 40))
        self.line.setStyleSheet("")
        self.line.setObjectName("line")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(280, 67, 200, 560))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("images/pslogo.png"))
        self.label.setObjectName("label")
        self.addButton = QtWidgets.QPushButton(self.centralwidget)
        self.addButton.setGeometry(QtCore.QRect(280, 10, 100, 40))
        self.addButton.setStyleSheet("")
        self.delButton = QtWidgets.QPushButton(self.centralwidget)
        self.delButton.setGeometry(QtCore.QRect(280, 60, 100, 40))
        self.lookButton = QtWidgets.QPushButton(self.centralwidget)
        self.lookButton.setGeometry(QtCore.QRect(280, 600, 100, 40))
        self.list = QtWidgets.QListWidget(self.centralwidget)
        self.list.setGeometry(QtCore.QRect(10, 60, 260, 580))
        self.list.setObjectName("listWidget")
        self.list.setFocusPolicy(QtCore.Qt.NoFocus)
        self.list.setWordWrap(True)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.addButton.setText(_translate("MainWindow", "Add"))
        self.delButton.setText(_translate("MainWindow", "Delete"))
        self.lookButton.setText(_translate("MainWindow", "Take a Look"))
        __sortingEnabled = self.list.isSortingEnabled()
        self.list.setSortingEnabled(False)
        self.list.setSortingEnabled(__sortingEnabled)

def setCSS():
    file = open('css/style.css', 'r')
    css: str = file.read()
    file.close()
    return css
