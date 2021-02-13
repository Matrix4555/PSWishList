from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from ui import Ui_MainWindow
from gameitem import GameItem, DelButton
from threading import Thread
from time import sleep
import urllib.request, urllib.error, urllib.parse
import os
import shutil
import pygame
import datetime

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.__initial()

    def __initial(self):
        self.setWindowTitle('PS WishList')
        self.setWindowIcon(QIcon('images/psico.ico'))

        self.ui.addButton.clicked           .connect(self.add)
        self.ui.updateButton.clicked        .connect(self.update)
        self.ui.muteButton.clicked          .connect(self.muteSounds)
        self.ui.setSoundButton.clicked      .connect(self.setSound)
        self.ui.aboutButton.clicked         .connect(self.about)
        self.ui.list.itemDoubleClicked      .connect(self.goToUrl)

        self.ui.line.installEventFilter(self)
        for btn in [self.ui.addButton, self.ui.updateButton, self.ui.muteButton, self.ui.setSoundButton, self.ui.aboutButton]:
            btn.installEventFilter(self)

        if not os.path.exists('data.dll'):
            with open('data.dll', 'w', encoding='utf-8'):
                pass
        if not os.path.exists('gamepictures'):
            os.mkdir('gamepictures')

        self.mute = False
        if os.path.exists('soundconfig.dll'):
            with open('soundconfig.dll', 'r') as file:
                self.mute = False if file.read() == 'False' else True
        else:
            with open('soundconfig.dll', 'w') as file:
                file.write(str(self.mute))
        sound = 'off' if self.mute else 'on'
        self.ui.muteButton.setIcon(QIcon('images/turned' + sound + 'button.png'))
        del sound

        self.refreshList()

        if not os.path.exists('sound.mp3'):
            here = os.path.dirname(__file__)
            shutil.copy('sounddefault.mp3', here + '\\sound.mp3')

        pygame.mixer.init()
        self.sound = pygame.mixer.Channel(0)
        if not self.mute:
            def play():
                pygame.mixer.music.load('soundstart.mp3')
                pygame.mixer.music.play()
                sleep(2)
                if not self.mute:
                    self.sound.play(pygame.mixer.Sound('sound.mp3'), -1)
            Thread(target = play).start()

    def refreshList(self):

        self.ui.list.clear()
        with open('data.dll', 'r', encoding='utf-8') as file:
            gameList = file.read().splitlines()

        count = len(gameList)
        while not count == 0:
            count -= 1
            game = gameList[count].split('\\')
            game.remove('')                         # remove last element ('\n')

            url                 = game[0]
            title               = game[1]
            price               = game[2]
            addTime             = game[3]
            discountPrice       = None
            psPlusPrice         = None
            offerTime           = None

            if len(game) == 6:
                if 'ps+' in game[4]:
                    psPlusPrice     = game[4].split('+')[1]
                else:
                    discountPrice   = game[4]
                offerTime           = game[5]
            elif len(game) == 7:
                discountPrice       = game[4]
                psPlusPrice         = game[5].split('+')[1]
                offerTime           = game[6]

            gi = GameItem(url, title, price, addTime, discountPrice, psPlusPrice, offerTime)
            btn = DelButton(gi, self.ui.list.count())
            btn.clicked.connect(self.deleteGame)
            gi.setButton(btn)

            newitem = QtWidgets.QListWidgetItem()
            self.ui.list.addItem(newitem)
            newitem.setSizeHint(QtCore.QSize(930, 220))
            self.ui.list.setItemWidget(newitem, gi)

    def add(self):

        url = self.ui.line.text()
        if url == '':
            Info().run('The line is empty')
            return
        elif not 'https://store.playstation.com/ru-ru/product/' in url:
            Info().run('At the beginning of the line there must be https://store.playstation.com/ru-ru/product/' + \
                ' with continuation of the address of any PlayStation product')
            return
        elif not len(url) == 80:
            Info().run('Incorrect input. URL must have 80 symbols.')
            return

        for i in range(self.ui.list.count()):
            if self.ui.list.itemWidget(self.ui.list.item(i)).getUrl() == url:
                Info().run('The game is already there')
                return

        self.block(True)

        def getNewData():
            data = self.getDataFromHtml(url)
            if not data:
                return False
            addTime = self.changeDateFormat(str(datetime.datetime.now()))
            self.waiting.aBitMore()
            self.addToFile(url, addTime, data)
            return True

        def complete(correctness):
            if correctness:
                self.ui.line.clear()
                self.block(False)
            else:
                self.waiting.hide()
                Info().run('Incorrect URL')
                self.block(False, False)

        self.thread = WaititngThread(getNewData)
        self.thread.finish.connect(complete)
        self.thread.start()

    def update(self):

        self.ui.list.clearSelection()
        if not self.ui.list.count():
            Info().run('No games')
            return

        with open('data.dll', 'w', encoding='utf-8'):
            pass
        dataList        = dict()
        additionTimes   = []
        threads         = []
        self.block(True)

        def getNewData():

            itemNumber = self.ui.list.count()
            while not itemNumber == 0:
                itemNumber -= 1
                currentGame = self.ui.list.itemWidget(self.ui.list.item(itemNumber))
                dataList[currentGame.getUrl()] = []
                additionTimes.append(currentGame.getAdditionTime())
            del itemNumber

            i = 0
            for key in dataList:
                def fillData(url):
                    dataList[url] = self.getDataFromHtml(url)
                threads.append(Thread(target = fillData, args = (key,)))
                threads[i].start()
                i += 1
            for t in threads:
                t.join()

            self.waiting.aBitMore()
            sleep(1.5)                  # for widget function above
            return True

        def complete(correctness):
            i = 0
            for keyUrl in dataList:
                if not dataList[keyUrl]:                        # if game has changed its url then save its current data
                    for k in range(self.ui.list.count()):
                        currentGame = self.ui.list.itemWidget(self.ui.list.item(k))
                        if currentGame.getUrl() == keyUrl:
                            dataList[keyUrl] = currentGame.getData()
                            Info(QtWidgets.QMessageBox.Critical, 'Error').run(currentGame.getTitle() + ' possibly changed its URL.' + \
                                ' Please try to check URL of the game and change its URL in your wish list if it\'s need (delete the game then add with new URL).')
                            break
                print(dataList[keyUrl])
                print(additionTimes[i])
                print('---------')
                self.addToFile(keyUrl, additionTimes[i], dataList[keyUrl])
                i += 1
            self.block(False)

        self.thread = WaititngThread(getNewData)
        self.thread.finish.connect(complete)
        self.thread.start()

    def block(self, blocker, refresh = True):
        if blocker:
            self.setEnabled(False)
            self.ui.list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
            self.waiting = WaitingWidget(self)
        else:
            if refresh:
                self.refreshList()
                self.waiting.hide()
            del self.waiting
            del self.thread
            self.ui.list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            self.setEnabled(True)

    def goToUrl(self):
        url = self.ui.list.itemWidget(self.ui.list.currentItem()).getUrl()
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def mousePressEvent(self, event):
        self.ui.list.clearSelection()

    def eventFilter(self, obj, event):

        if obj is self.ui.line and event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Return and self.ui.line.hasFocus():
            self.add()

        if obj is self.ui.line and event.type() == QtCore.QEvent.MouseButtonPress:
            self.ui.list.clearSelection()

        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_F5:
            self.update()

        for btn in [self.ui.addButton, self.ui.updateButton, self.ui.muteButton, self.ui.setSoundButton, self.ui.aboutButton]:
            if obj is btn and event.type() == QtCore.QEvent.HoverEnter:
                btn.setIconSize(QtCore.QSize(65, 35))
            if obj is btn and event.type() == QtCore.QEvent.HoverLeave:
                btn.setIconSize(QtCore.QSize(70, 40))

        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        if not self.mute:
            self.mute = True
            self.sound.stop()
            pygame.mixer.music.load('soundend.mp3')
            pygame.mixer.music.play()
            self.hide()
            sleep(2)

    def addToFile(self, url, addTime, data):
        with open('data.dll', 'a', encoding='utf-8') as file:
            file.write(url + '\\' + data[0] + '\\' + data[1] + '\\' + addTime + '\\')
            if data[2]:
                file.write(data[2] + '\\')
            if data[3]:
                file.write('ps+' + data[3] + '\\')
            if data[4]:
                file.write(data[4] + '\\')
            file.write('\n')

    def changeDateFormat(self, time):
        date = []
        date.append(time[0:-22])
        date.append(time[5:-19])
        date.append(time[8:-16])
        date.append(time[11:-10])
        return date[2] + '/' + date[1] + '/' + date[0] + ' - ' + date[3]

    def getDataFromHtml(self, url):

        html = urllib.request.urlopen(url).read().decode('utf-8')

        try:
            title = html.split('title#name">')[1].split('<')[0]
        except:
            return None
        if '&amp;' in title:
            for cut in (' PS4 &amp; PS5', ' PS4™ &amp; PS5™', ' PS4™ &amp;  PS5™', ' PS4 1 &amp; PS5'):
                title = title.replace(cut, '')

        if not os.path.exists('gamepictures/' + title.replace(':', '') + '.png'):
            image = html.split('fit-cover" src="')[1].split('?w=')[0]
            urllib.request.urlretrieve(image, 'gamepictures/' + title.replace(':', '') + '.png')

        try:
            originalPrice = html.split('"originalPriceFormatted":"')[1].split('"')[0]
            discountPrice = html.split('"discountPriceFormatted":"')[1].split('"')[0]
            zero = False
        except:
            zero = True

        if not zero:
            offerTime = html.split('"offerAvailability":')[2].split(',')[0]
            if not 'null' in offerTime:
                offerTime = self.changeDateFormat(offerTime.replace('"', '').replace('T', ' ') + 'ZZ')
            else:
                offerTime = html.split('"offerAvailability":')[1].split(',')[0]
                if not 'null' in offerTime:
                    offerTime = self.changeDateFormat(offerTime.replace('"', '').replace('T', ' ') + 'ZZ')
                else:
                    offerTime = None
            stringWithPSPlus = 'PS Plus","basePriceValue":' + originalPrice.replace('RUB ', '').replace('.', '') + '00' + ',"discountedValue":'
        psPlusPrice = None

        if zero:
            originalPrice = 'Free'
            discountPrice = None
        elif stringWithPSPlus in html:
            twoDiscounts = False
            if not originalPrice == discountPrice:
                twoDiscounts = True
            psPlusPrice = html.split(stringWithPSPlus)[1].split(',"')[0].replace('00', '')
            if not psPlusPrice == '0':
                if len(psPlusPrice) >= 4:
                    psPlusPrice = psPlusPrice[:1] + '.' + psPlusPrice[1:]
                psPlusPrice = 'RUB ' + psPlusPrice
            else:
                psPlusPrice = 'Free'
            if not twoDiscounts:
                discountPrice = None
        elif originalPrice == discountPrice:
            if originalPrice == 'Бесплатно':
                originalPrice = 'Free'
            discountPrice = None

        return (title, originalPrice, discountPrice, psPlusPrice, offerTime)

    def deleteGame(self):

        btnIndex = self.sender().getIndex()
        currentGame = self.ui.list.itemWidget(self.ui.list.item(btnIndex))

        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle('Delete Game')
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setText('Remove ' + currentGame.getTitle() + '?')
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if msg.exec() == QtWidgets.QMessageBox.No:
            return

        self.ui.list.takeItem(btnIndex)
        rewrite = ''
        with open('data.dll', 'r', encoding='utf-8') as file:
            for line in file:
                if currentGame.getUrl() in line:
                    continue
                rewrite += line
        with open('data.dll', 'w', encoding='utf-8') as file:
            file.write(rewrite)
        if os.path.exists('gamepictures/' + currentGame.getTitle().replace(':', '') + '.png'):
            os.remove('gamepictures/' + currentGame.getTitle().replace(':', '') + '.png')

        for i in range(self.ui.list.count()):
            self.ui.list.itemWidget(self.ui.list.item(i)).getButton().setIndex(i)

    def about(self):
        Info().run('PSWishList (PlayStation WishList)\nVersion: 2.0')

    def setSound(self):     # jax's idea :)

        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Sound', '/', '*.mp3')[0]
        if len(path) == 0:
            return

        self.sound.stop()

        here = os.path.dirname(__file__)
        shutil.copy(path, here)
        path = path.split('/')
        if os.path.exists('sound.mp3'):
            os.remove('sound.mp3')
        os.rename(path[len(path) - 1], 'sound.mp3')

        self.sound.play(pygame.mixer.Sound('sound.mp3'), -1)
        if self.mute:
            self.sound.stop()

    def muteSounds(self):

        self.mute = False if self.mute else True
        with open('soundconfig.dll', 'w', encoding='utf-8') as file:
            file.write(str(self.mute))
        sound = 'off' if self.mute else 'on'
        self.ui.muteButton.setIcon(QIcon('images/turned' + sound + 'button.png'))

        if self.mute:
            self.sound.stop()
            def again():
                sleep(0.2)
                self.sound.stop()
            Thread(target = again).start()
        else:
            Thread(target = lambda: self.sound.play(pygame.mixer.Sound('sound.mp3'), -1)).start()       # there is a thread because button should refresh quickly

class Info(QtWidgets.QMessageBox):
    def __init__(self, icon = QtWidgets.QMessageBox.Information, title = 'Info'):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon('images/psico.ico'))
        self.setIcon(icon)

    def run(self, mes):
        self.setText(mes)
        self.exec()

class WaitingWidget(QtWidgets.QWidget):
    def __init__(self, capture = None):
        super().__init__(capture)
        self.resize(230, 200)
        if capture:
            self.move(360, 375)
        self.setMinimumSize(230, 200)
        self.setMaximumSize(230, 200)
        self.setAutoFillBackground(True)

        self.waitLabel = QtWidgets.QLabel(self)
        self.waitLabel.resize(210, 45)
        self.waitLabel.move(10, 15)
        self.waitLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.waitLabel.setText('Wait Please')
        self.waitLabel.setObjectName('waitingwidget')

        self.gifLabel = QtWidgets.QLabel(self)
        self.gifLabel.setGeometry(10, 55, 210, 160)
        self.gifLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.gifLabel.setObjectName('waitingwidget')
        self.gifLabel.setStyleSheet('font-size: 18pt;')

        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(0, 0, self.width(), self.height())
        self.frame.setStyleSheet('border: 3px solid orange;')

        gif = QtGui.QMovie('images/loading.gif', QtCore.QByteArray(), self)
        gif.setSpeed(200)
        self.gifLabel.setMovie(gif)
        gif.start()
        self.show()

    def aBitMore(self):
        self.gifLabel.setMovie(None)
        self.gifLabel.setText('...and a bit more :)')

class WaititngThread(QtCore.QThread):
    def __init__(self, function):
        super().__init__()
        self.function = function

    finish = QtCore.pyqtSignal(bool)

    def run(self):
        self.finish.emit(self.function())
