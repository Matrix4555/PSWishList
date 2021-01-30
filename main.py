import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from control import Appearance

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    application = Appearance()
    application.show()
    sys.exit(app.exec())
    