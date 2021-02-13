import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from mainwindow import MainWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    application = MainWindow()
    x = app.desktop().geometry().width() / 2 - application.width() / 2
    y = app.desktop().geometry().height() / 2 - application.height() / 2
    application.setGeometry(int(x), int(y), application.width(), application.height())
    application.show()
    sys.exit(app.exec())
