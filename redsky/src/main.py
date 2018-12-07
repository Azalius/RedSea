from PyQt5 import uic, QtGui, QtCore, QtWidgets
import sys
import os


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, urls=None):
        QtWidgets.QMainWindow.__init__(self)
        self.rootpath = os.path.join(__file__, "..", "..", "..")
        uic.loadUi(os.path.join(self.rootpath, "redsky", "ui", "main.ui"), self)

        if urls != None:
            self.addUrls(urls, True)


    def addUrls(self, urls, ignoreErrors = False):
        '''Add all the urls given to the list '''
        if type(urls) == str:
            urls = [urls]
        


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(sys.argv)
    window.show()
    sys.exit(app.exec_())
