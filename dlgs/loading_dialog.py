import os, sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import QSize


class LoadingDialog(QDialog):
    def __init__(self, title = None):
        super().__init__()
        self.setWindowTitle("Loading")
        loading = QMovie('./img/loading.gif')
        loading.setScaledSize(QSize(80, 80))
        lbl_img = QLabel()


        lbl_img.setMovie(loading)
        loading.start()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        box = QVBoxLayout()

        hbox1.addStretch(1)
        hbox1.addWidget(lbl_img)
        hbox1.addStretch(1)

        hbox2.addStretch(1)
        hbox2.addWidget(QLabel(title))
        hbox2.addStretch(1)

        box.addLayout(hbox1)
        box.addLayout(hbox2)
        self.setLayout(box)
        self.setFixedSize(250, 150)


# class MyApp(QMainWindow):
# 
#     def __init__(self):
#         super().__init__()

#         self.main_widget = QWidget() # Make main window
#         self.btn = QPushButton("hi", self)
#         self.btn.clicked.connect(self.click)
#         vbox = QVBoxLayout()
#         vbox.addWidget(self.btn)
#         self.main_widget.setLayout(vbox)
#         self.setCentralWidget(self.main_widget)

#     def click(self):
#         dia = LoadingDialog("Executing Deephos...")
#         dia.exec()



# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     ex = MyApp()
#     ex.show()
#     sys.exit(app.exec())