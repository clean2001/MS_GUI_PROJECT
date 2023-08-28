import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QProgressBar, QLabel
from PyQt6.QtCore import QBasicTimer


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)

        self.percent_label = QLabel(self)  # 퍼센티지를 표시
        self.percent_label.setGeometry(240, 40, 50, 25)

        self.btn = QPushButton('Stop', self)
        self.btn.move(170, 80)
        self.btn.clicked.connect(self.doAction)

        self.timer = QBasicTimer()
        self.step = 0
        self.timer.start(100, self)

        self.setWindowTitle('Loading')
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def timerEvent(self, e):
        if self.step >= 100:
            self.timer.stop()
            self.btn.setText('Finished')
            self.percent_label.setText('100%')  # 100% 표시
            self.close()  # 창 닫기
            return

        self.step = self.step + 1
        self.pbar.setValue(self.step)
        self.percent_label.setText(f'{self.step}%')  # 퍼센티지 표시 업데이트

    def doAction(self):
        if self.timer.isActive():
            self.timer.stop()
            self.btn.setText('Start')
        else:
            self.timer.start(100, self)
            self.btn.setText('Stop')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec())
