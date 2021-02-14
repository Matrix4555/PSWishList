from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QLabel

class GameItem(QtWidgets.QWidget):
    def __init__(self, url, title, price, additionTime, discount, psPlusDiscount, offerTime):
        super().__init__()

        self.resize(930, 220)
        self.title              = QLabel(self)
        self.picture            = QLabel(self)
        self.price              = QLabel(self)
        self.additionTime       = QLabel(self)
        self.discount           = None
        self.psPlusDiscount     = None
        self.offerTime          = None
        self.deleteButton       = None
        self.url                = url

        self.title.setText(title)
        self.title.setAlignment(QtCore.Qt.AlignLeft)
        self.title.setObjectName('titlelabel')
        self.title.setWordWrap(True)

        self.picture.setPixmap(QPixmap('gamepictures/' + title.replace(':', '') + '.png'))
        self.picture.setScaledContents(True)

        self.price.setGeometry(780, 10, 120, 25)
        self.price.setText(price)
        self.price.setObjectName('pricelabel')

        square = False
        size = self.picture.pixmap().rect().size()
        if size.width() == size.height():
            square = True
        del size
        if not square:
            self.title          .setGeometry(370, 10, 350, 130)
            self.picture        .setGeometry(10, 10, 350, 197)
            self.additionTime   .setGeometry(370, 190, 220, 20)
        else:
            self.title          .setGeometry(215, 10, 350, 130)
            self.picture        .setGeometry(10, 10, 197, 197)
            self.additionTime   .setGeometry(215, 190, 220, 20)

        self.additionTime.setText('Added: ' + additionTime)
        self.additionTime.setObjectName('datalabel')

        if discount:
            self.price.setObjectName('strikethrougprice')
            self.discount = QLabel(self)
            self.discount.setObjectName('pricelabel')
            self.discount.setGeometry(780, 40, 120, 25)
            self.discount.setText(discount)

        if psPlusDiscount:
            self.psPlusDiscount = QLabel(self)
            self.psPlusDiscount.setObjectName('pspluspricelabel')
            self.psPlusDiscount.setGeometry(780, 46, 120, 25)
            self.psPlusDiscount.setText(psPlusDiscount)
            if discount:
                self.price.setObjectName('strikethrougprice')
                self.psPlusDiscount.move(780, 74)
            self.psPlusLogo = QLabel(self)
            self.psPlusLogo.resize(40, 43)
            self.psPlusLogo.setPixmap(QPixmap('images/pspluslogo.png'))
            self.psPlusLogo.setScaledContents(True)
            def psPlusMove(shift):
                self.psPlusLogo.move(self.psPlusDiscount.x() + shift, self.psPlusDiscount.y() - 3)
            if not psPlusDiscount == 'Free':
                digit = int(psPlusDiscount.replace('RUB ', '').replace('.', ''))
                psPlusMove(-10) if digit < 1000 else psPlusMove(-25)
            else:
                psPlusMove(32)

        if offerTime:
            self.offerTime = QLabel(self)
            self.offerTime.setObjectName('datalabel')
            if not square:
                self.offerTime.setGeometry(370, 170, 220, 20)
            else:
                self.offerTime.setGeometry(215, 170, 220, 20)
            self.offerTime.setText('Available Until: ' + offerTime)

    def getUrl(self):
        return self.url

    def getTitle(self):
        return self.title.text()

    def getAdditionTime(self):
        return self.additionTime.text().split('Added: ')[1]

    def getButton(self):
        return self.deleteButton

    def setButton(self, btn):
        self.deleteButton = btn

    def setBlockColor(self, blocker):
        if self.psPlusDiscount:
            self.psPlusDiscount.setStyleSheet('color: white;' if blocker else '')

    def getData(self):
        data = []
        data.append(self.title.text())
        data.append(self.price.text())
        data.append(self.discount.text())                                   if self.discount            else data.append(None)
        data.append(self.psPlusDiscount.text())                             if self.psPlusDiscount      else data.append(None)
        data.append(self.offerTime.text().split('Available Until: ')[1])    if self.offerTime           else data.append(None)
        return data

class DelButton(QtWidgets.QPushButton):
    def __init__(self, capture, index):
        super().__init__(capture)
        self.index = index
        self.setGeometry(865, 170, 40, 40)
        self.setIconSize(QtCore.QSize(35, 35))
        self.setIcon(QIcon('images/deletebutton.png'))
        self.setObjectName('delbutton')

    def getIndex(self):
        return self.index

    def setIndex(self, index):
        self.index = index
