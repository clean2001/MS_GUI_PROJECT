import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWebEngineWidgets


class WebViewWindow(QMainWindow):

    def __init__(self, url):
        QMainWindow.__init__(self)
        self.web_view = QtWebEngineWidgets.QWebEngineView()
        self.web_view.setUrl(QtCore.QUrl(url))
        self.setCentralWidget(self.web_view)


if __name__ == "__main__":
    web_url = 'file:///C:/Users/somso/Documents/hyu/4_1/MS_GUI_PROJECT/ui/bar.html'
    if len(sys.argv) == 2:
        web_url = sys.argv[1]
    app = QtWidgets.QApplication(sys.argv)
    window = WebViewWindow(web_url)
    window.show()
    sys.exit(app.exec_())