from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPlainTextEdit, QPushButton
from PyQt5.QtGui import QFont
import pyspectrum

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("펩타이드 식별기")
        self.setGeometry(100, 100, 500, 500)

        font = QFont()
        font.setPointSize(12)

        self.textEdit = QPlainTextEdit(self)
        self.textEdit.setFont(font)
        self.textEdit.setGeometry(10, 10, 480, 350)

        self.openButton = QPushButton("데이터 파일 열기", self)
        self.openButton.setGeometry(10, 370, 150, 30)
        self.openButton.clicked.connect(self.openFile)

        self.identifyButton = QPushButton("쿼리 펩타이드 식별", self)
        self.identifyButton.setGeometry(170, 370, 150, 30)
        self.identifyButton.clicked.connect(self.identifyPeptide)

        self.quitButton = QPushButton("종료", self)
        self.quitButton.setGeometry(330, 370, 150, 30)
        self.quitButton.clicked.connect(self.close)

    def openFile(self):
        filename = QFileDialog.getOpenFileName(self, "Open File")
        if filename[0]:
            with open(filename[0], 'r') as f:
                data = f.read()
                self.textEdit.setPlainText(data)

    def identifyPeptide(self):
        spectrum = pyspectrum.read(self.textEdit.toPlainText())
        query_peptide = "QUERY_PEPTIDE_SEQUENCE"
        matches = spectrum.identify(query_peptide)
        result_str = "쿼리 펩타이드 식별 결과:\n"
        if len(matches) > 0:
            for match in matches:
                result_str += f"{match['peptide']} (Score: {match['score']})\n"
        else:
            result_str += "일치하는 펩타이드를 찾을 수 없습니다."
        self.textEdit.setPlainText(result_str)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
