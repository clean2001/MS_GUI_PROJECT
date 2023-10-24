import os
from PyQt6.QtWidgets import *
from dlgs.loading_dialog import LoadingDialog
from PyQt6.QtCore import *
import time
import help_functions.param_file as param_file

class ExecuteDeephos(QThread):
    def __init__(self):
        super().__init__()
    
    def run(self, query_file_list):
        # deephos를 실행해요
        parameter = './deephos/foo.params'
        # print(parameter)
        os.system('java -jar deephos/deephos_tp2.jar -i ' + parameter)


class InputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("input")
        self.resize(500, 500)
        
        # 나중에 써야하는 정보들
        self.query_file_list = [] # query 파일들
        self.target_lib_file = None # target lib의 파일 이름
        self.decoy_lib_file = None # decoy lib의 파일 이름
        self.pept_tol_value = 10 # default = 10, ppm
        self.isotope_tol_value_min = 0
        self.isotope_tol_value_max = 0
        self.frag_tol_value = 0.02 # default = 0.02, Da

        # queries
        self.query_layout = QVBoxLayout()
        inner_query_layout = QHBoxLayout()
        addBtn = QPushButton("Add")
        addBtn.setMaximumWidth(50)
        removeBtn = QPushButton("Remove")
        removeBtn.setMaximumWidth(60)
        self.query_list = QListWidget()
        inner_query_layout.addWidget(QLabel("Query"))
        inner_query_layout.addWidget(addBtn)
        inner_query_layout.addWidget(removeBtn)
        addBtn.clicked.connect(self.openQuery)
        removeBtn.clicked.connect(self.removeQuery)
        self.query_layout.addLayout(inner_query_layout)
        self.query_layout.addWidget(self.query_list)


        # Target lib
        self.target_lib_layout = QVBoxLayout()
        target_lib_inner_layout = QHBoxLayout()
        self.target_lib_label = QLabel("파일을 열어주세요")
        self.target_lib_browse = QPushButton("Browse")
        self.target_lib_browse.clicked.connect(self.browse_target_lib)
        self.target_lib_browse.setMaximumWidth(70)
        self.target_lib_title = QLineEdit()
        self.target_lib_title.setReadOnly(True)
        self.target_lib_layout.addWidget(QLabel("Target Lib"))
        target_lib_inner_layout.addWidget(self.target_lib_title)
        target_lib_inner_layout.addWidget(self.target_lib_browse)
        self.target_lib_layout.addLayout(target_lib_inner_layout)

        # Decoy lib
        self.decoy_lib_layout = QVBoxLayout()
        decoy_lib_inner_layout = QHBoxLayout()
        self.decoy_lib_title = QLineEdit()
        self.decoy_lib_title.setReadOnly(True)
        self.decoy_lib_browse = QPushButton("Browse")
        self.decoy_lib_browse.clicked.connect(self.browse_decoy_lib)
        self.decoy_lib_browse.setMaximumWidth(70)
        self.decoy_lib_layout.addWidget(QLabel("Decoy Lib"))
        decoy_lib_inner_layout.addWidget(self.decoy_lib_title)
        decoy_lib_inner_layout.addWidget(self.decoy_lib_browse)
        self.decoy_lib_layout.addLayout(decoy_lib_inner_layout)

        # Peptide Tolerance
        self.pept_tol_layout = QHBoxLayout()
        self.pept_tol_layout.addWidget(QLabel("Peptide Tolerance: "))
        self.pept_tol = QLineEdit()
        self.pept_tol.setMaximumWidth(50)
        self.pept_tol_layout.addWidget(self.pept_tol)
        self.pept_tol.setPlaceholderText("10")
        self.pept_tol_layout.addWidget(QLabel("ppm (Default = 10)"))
        self.pept_tol_layout.addStretch(10)

        # C13 Isotope
        self.isotope_tol_layout = QHBoxLayout()
        self.isotope_tol_layout.addWidget(QLabel("C13 Isotope: "))

        self.isotope_tol_min = QSpinBox()
        self.isotope_tol_max = QSpinBox()
        self.isotope_tol_min.setSingleStep(1)
        self.isotope_tol_max.setSingleStep(1)
        self.isotope_tol_min.setRange(-5, 0)
        self.isotope_tol_max.setRange(0, 5)
        self.isotope_tol_min.setMinimumWidth(70)
        self.isotope_tol_max.setMinimumWidth(70)

        self.isotope_tol_layout.addWidget(QLabel("min: (-5~0)"))
        self.isotope_tol_layout.addWidget(self.isotope_tol_min)
        self.isotope_tol_layout.addStretch(1)
        self.isotope_tol_layout.addWidget(QLabel("max: (0~5)"))
        self.isotope_tol_layout.addWidget(self.isotope_tol_max)
        self.isotope_tol_layout.addStretch(8)

    
        # Fragment Tolerance
        self.frag_tol_layout = QHBoxLayout()
        self.frag_tol_layout.addWidget(QLabel("Fragment Tolerance: "))
        self.frag_tol = QLineEdit()
        self.frag_tol.setMaximumWidth(50)
        self.frag_tol_layout.addWidget(self.frag_tol)
        self.frag_tol.setPlaceholderText("0.02")
        self.frag_tol_layout.addWidget(QLabel("Da (Default = 0.02)"))
        self.frag_tol_layout.addStretch(10)

        # RUN Btn
        self.run_layout = QHBoxLayout()
        self.run_btn = QPushButton("RUN", self)
        self.run_btn.clicked.connect(self.return_infomations)
        self.run_btn.setMaximumWidth(50)
        self.run_layout.addStretch(10)
        self.run_layout.addWidget(self.run_btn)

        self.initUI()
        
    def initUI(self):
        self.outer_layout = QVBoxLayout()
        self.outer_layout.addLayout(self.query_layout)
        self.outer_layout.addStretch(10)
        self.outer_layout.addLayout(self.target_lib_layout)
        self.outer_layout.addStretch(10)
        self.outer_layout.addLayout(self.decoy_lib_layout)
        self.outer_layout.addStretch(10)
        self.outer_layout.addLayout(self.pept_tol_layout)
        self.outer_layout.addStretch(10)
        self.outer_layout.addLayout(self.isotope_tol_layout)
        self.outer_layout.addStretch(10)
        self.outer_layout.addLayout(self.frag_tol_layout)
        self.outer_layout.addStretch(10)
        self.outer_layout.addLayout(self.run_layout)

        # 크기 조정
        self.isotope_tol_min.setMaximumWidth(50)
        self.isotope_tol_max.setMaximumWidth(50)
    
        self.setLayout(self.outer_layout)

    def openQuery(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.AnyFile)
        # dlg.setNameFilter("*.mgf")

        filenames = None
        filenames = dlg.getOpenFileNames()

        for f in filenames[0]:
            if f.split('.')[1] != 'mgf':
                continue
            self.query_list.addItem(f)

    

    def removeQuery(self):
        selected = self.query_list.selectedItems()
        files = ''
        for s in selected:
            files += str(s.text()) + '\n'
        
        reply = QMessageBox().question(self, "Remove", "Are you sure to remove the files below?\n"+files, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.query_list.removeItemWidget(self.query_list.takeItem(self.query_list.currentRow()))
    
        
    def browse_target_lib(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.AnyFile)
        dlg.setNameFilter("*.msp") # msp와 어떤 파일이 지원되는지 여쭤봐야겠다.
        filenames = None

        if dlg.exec():
            filenames = dlg.selectedFiles()

            if len(filenames):
                self.target_lib_title.setText(filenames[0])
                self.target_lib_file = filenames[0]

    
    def browse_decoy_lib(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.AnyFile)
        dlg.setNameFilter("*.msp") # msp와 어떤 파일이 지원되는지 여쭤봐야겠다.
        filenames = None

        if dlg.exec():
            filenames = dlg.selectedFiles()

            if len(filenames):
                self.decoy_lib_title.setText(filenames[0])
                self.decoy_lib_file = filenames[0]


    def return_infomations(self):
        # query list에 추가
        for i in range(self.query_list.count()):
            self.query_file_list.append(self.query_list.item(i).text())

        
        print("[debug]", self.query_file_list)
        # query list가 비어져있는지 확인
        if not len(self.query_file_list):
            err = QMessageBox.warning(self, "No file", "There's no Query file.\nPlease import")
            return

        # target_lib이 없다면?
        if not self.target_lib_file:
            err = QMessageBox.warning(self, "No file", "There's no target lib file.\nPlease import")
            return

        # decoy_lib이 없다면?
        if not self.decoy_lib_file:
            err = QMessageBox.warning(self, "No file","There's no decoy lib file.\nPlease import")
            return
        
        # pept tol이 이상한 값이라면?
        pept_tol = 10
        try:
            pept_tol = float(self.pept_tol.text())
            self.pept_tol_value = pept_tol
        except:
            pept_tol = 10
        
        # frag tol이 이상한 값이라면?
        frag_tol = 0.02
        try:
            frag_tol = float(self.frag_tol.text())
            self.frag_tol_value = frag_tol
        except:
            frag_tol = 0.02

        c13_isotope_tol_min, c13_isotope_tol_max = 0, 0
        try:
            c13_isotope_tol_min = int(self.isotope_tol_min.value())
            c13_isotope_tol_max = int(self.isotope_tol_max.value())
            self.isotope_tol_value_min = c13_isotope_tol_min
            self.isotope_tol_value_max = c13_isotope_tol_max
        except:
            c13_isotope_tol_min, c13_isotope_tol_max = 0, 0



        make_decoy = 0 # 임시

        # Deephos
        # 파라미터 파일을 만들어요
        param_file.make_parameter_file("./ddd.devi", self.query_file_list,
                                        self.target_lib_file,
                                        self.decoy_lib_file,
                                        self.pept_tol_value,
                                        self.isotope_tol_value_min,
                                        self.isotope_tol_value_max,
                                        self.frag_tol_value,
                                        make_decoy)
        # deephos를 실행해요
        parameter = './deephos/foo' + str(i) + '.params'
        os.system('java -jar deephos/deephos_tp2.jar -i ' + parameter)

        # ed = ExecuteDeephos()
        # ed.run(self.query_file_list)

        # loadingDlg = LoadingDialog("Executing Deephos...")
        # loadingDlg.exec()
        # loadingDlg.done(0)
        
        self.done(0)

