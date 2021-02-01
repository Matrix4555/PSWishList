from PyQt5 import QtCore, QtGui, QtWidgets
from window import Ui_MainWindow
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import *
import ctypes
import os.path

class Appearance(QtWidgets.QMainWindow):
    def __init__(self):
        super(Appearance, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.__initial()

    def __initial(self):
        self.setWindowTitle('PS WishList')
        self.setWindowIcon(QIcon('images/psico.ico'))
        self.ui.addButton.clicked.connect(self.add)
        self.ui.delButton.clicked.connect(self.delete)
        self.ui.lookButton.clicked.connect(self.takeLook)
        self.ui.line.installEventFilter(self)                   # event for pressed enter

        if not os.path.exists('data.dll'):
            with open('data.dll', 'w', encoding='utf-8'):                   # create a file if it doesn't exist
                ctypes.windll.kernel32.SetFileAttributesW('data.dll', 2)    # hide the file

        self.refreshList()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.ui.line \
            and event.key() == QtCore.Qt.Key_Return and self.ui.line.hasFocus():
                self.add()
        return super().eventFilter(obj, event)

    def add(self):
        input = self.ui.line.text()
        if input == '':
            Info().run('The line is empty')
        elif not 'https://store.playstation.com/ru-ru/product/' in input \
            and not 'https://store.playstation.com/ru-ru/concept/' in input:
            Info().run('At the beginning of the line there must be "https://store.playstation.com/ru-ru/product/" with continuation of the address of any PlayStation product')
        elif not ' + ' in input:
            Info().run('The line must have " + " (with gaps) after URL. After the plus - a name of a game.')
        elif len(input.split(' + ')[1]) == 0:
            Info().run('No the name of the game')
        else:
            for i in range(self.ui.list.count()):
                if self.ui.list.item(i).text() == input.split(' + ')[1]:
                    Info().run('The game is already there')
                    return
            with open('data.dll', 'a', encoding='utf-8') as file:
                file.write(input + '\n')
            self.ui.list.addItem(input.split(' + ')[1])
            self.ui.list.item(self.ui.list.count() - 1).setTextAlignment(QtCore.Qt.AlignHCenter)
            self.ui.line.clear()

    def delete(self):
        if not self.ui.list.selectedItems():
            Info().run('No selected game')
            return
        delWord = self.ui.list.currentItem().text() + '\n'
        refreshedText = ''
        deletedAlready = False
        with open('data.dll', 'r') as fileR:
            for game in fileR:
                if not deletedAlready and game.split(' + ')[1] == delWord:
                    deletedAlready = True
                    continue
                refreshedText += game
        with open('data.dll', 'w') as fileW:
            fileW.write(refreshedText)
        self.refreshList()

    def refreshList(self):
        self.ui.list.clear()
        with open('data.dll', 'r', encoding='utf-8') as file:
            count = 0
            for game in file:
                self.ui.list.addItem(game.split('\n')[0].split(' + ')[1])
                self.ui.list.item(count).setTextAlignment(QtCore.Qt.AlignCenter)
                count += 1

    def takeLook(self):
        if(self.ui.list.count() == 0):
            Info().run('No games in the wish list')
            return
        try:
            count = 0
            urls = set()
            with open('data.dll', 'r', encoding='utf-8') as file:
                for site in file:
                    urls.add(site.split(' + ')[0])
                    count += 1
                    if count >= 50:
                        raise
                for site in urls:
                    QDesktopServices.openUrl(QUrl(site))
        except:
            Info(QMessageBox.Critical, 'Error').run('An error has occurred')
                
class Info(QMessageBox):
    def __init__(self, icon = QMessageBox.Information, title = 'Info'):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon('images/psico.ico'))
        self.setIcon(icon)

    def run(self, mes):
        self.setText(mes)
        self.exec()
