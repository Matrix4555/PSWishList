from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QLabel, QPushButton

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(950, 950)
        MainWindow.setMinimumSize(950, 950)
        MainWindow.setMaximumSize(950, 950)
        MainWindow.setStyleSheet(setCSS())
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.line = QtWidgets.QLineEdit(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(10, 10, 600, 40))
        self.line.setPlaceholderText('Drop here URL with game from PlayStation Store...')

        self.list = QtWidgets.QListWidget(self.centralwidget)
        self.list.setGeometry(QtCore.QRect(10, 60, 930, 880))
        self.list.setFocusPolicy(QtCore.Qt.NoFocus)
        self.list.setWordWrap(True)
        self.list.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.list.verticalScrollBar().setSingleStep(20)

        self.addButton          = QPushButton(self.centralwidget)
        self.updateButton       = QPushButton(self.centralwidget)
        self.muteButton         = QPushButton(self.centralwidget)
        self.setSoundButton     = QPushButton(self.centralwidget)
        self.aboutButton        = QPushButton(self.centralwidget)

        shift = 0
        for btn in [self.addButton, self.updateButton, self.muteButton, self.setSoundButton, self.aboutButton]:
            btn.setGeometry(570 + shift, 10, 70, 40)
            btn.setIconSize(QtCore.QSize(70, 40))
            btn.setObjectName('upperbutton')
            shift += 75
        del shift

        self.addButton          .setIcon(QIcon('images/addbutton.png'))
        self.updateButton       .setIcon(QIcon('images/updatebutton.png'))
        self.setSoundButton     .setIcon(QIcon('images/setsoundbutton.png'))
        self.aboutButton        .setIcon(QIcon('images/aboutbutton.png'))

        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

def setCSS():
    file = open('css/style.css', 'r')
    css: str = file.read()
    file.close()
    return css
