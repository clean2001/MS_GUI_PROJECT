import os
from PyQt6.QtWidgets import *
from dlgs.loading_dialog import LoadingDialog
from PyQt6.QtCore import *
from PyQt6 import QtGui
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
        self.resize(500, 650)
        
        # 나중에 써야하는 정보들
        self.project_file_directory = ""
        self.project_file_name = ""
        self.query_file_list = [] # query 파일들
        self.target_lib_files = [] # target lib의 파일 이름
        self.decoy_lib_files = [] # decoy lib의 파일 이름
        self.pept_tol_value = 10 # default = 10, ppm
        self.isotope_tol_value_min = 0
        self.isotope_tol_value_max = 0
        self.frag_tol_value = 0.02 # default = 0.02, Da

        # Project file
        self.project_file_layout = QVBoxLayout()
        self.project_file_dir_layout = QHBoxLayout()
        self.project_file_dir_text = QLineEdit()
        self.project_file_dir_button = QPushButton("Browse")
        self.project_file_dir_button.clicked.connect(self.browse_project_file_dir)
        self.project_file_text = QLineEdit()
        self.project_file_layout.addWidget(QLabel("Project File Directory: "))
        self.project_file_dir_layout.addWidget(self.project_file_dir_text)
        self.project_file_dir_layout.addWidget(self.project_file_dir_button)
        self.project_file_layout.addLayout(self.project_file_dir_layout)
        self.project_file_layout.addWidget(QLabel("Project File name: "))
        self.project_file_layout.addWidget(self.project_file_text)

        # queries
        self.query_layout = QVBoxLayout()
        inner_query_layout = QHBoxLayout()
        query_add_btn = QPushButton("Add")
        query_add_btn.setMaximumWidth(50)
        query_remove_btn = QPushButton("Remove")
        query_remove_btn.setMaximumWidth(60)
        self.query_list = QListWidget()
        inner_query_layout.addWidget(QLabel("Query"))
        inner_query_layout.addWidget(query_add_btn)
        inner_query_layout.addWidget(query_remove_btn)
        query_add_btn.clicked.connect(self.open_query)
        query_remove_btn.clicked.connect(self.remove_query)
        self.query_layout.addLayout(inner_query_layout)
        self.query_layout.addWidget(self.query_list)

        # Target lib
        self.target_lib_layout = QVBoxLayout()
        target_lib_inner_layout = QHBoxLayout()
        target_lib_browse_btn = QPushButton("Add")
        target_lib_browse_btn.setMaximumWidth(50)
        target_lib_remove_btn = QPushButton("Remove")
        target_lib_remove_btn.setMaximumWidth(60)
        self.target_lib_list = QListWidget()
        self.target_lib_list.setMaximumHeight(100)
        target_lib_inner_layout.addWidget(QLabel("Target Libraries"))
        target_lib_inner_layout.addWidget(target_lib_browse_btn)
        target_lib_inner_layout.addWidget(target_lib_remove_btn)
        target_lib_browse_btn.clicked.connect(self.open_target_libs)
        target_lib_remove_btn.clicked.connect(self.remove_target_libs)
        self.target_lib_layout.addLayout(target_lib_inner_layout)
        self.target_lib_layout.addWidget(self.target_lib_list)

        # Make Decoy
        self.make_decoy_layout = QVBoxLayout()
        self.make_decoy_checkbox = QCheckBox('Make Decoy Library', self)
        self.make_decoy_checkbox.toggle()
        self.make_decoy_layout.addWidget(self.make_decoy_checkbox)

        # Decoy lib
        self.decoy_lib_layout = QVBoxLayout()
        decoy_lib_inner_layout = QHBoxLayout()
        decoy_lib_browse_btn = QPushButton("Add")
        decoy_lib_browse_btn.setMaximumWidth(50)
        decoy_lib_remove_btn = QPushButton("Remove")
        decoy_lib_remove_btn.setMaximumWidth(60)
        self.decoy_lib_list = QListWidget()
        self.decoy_lib_list.setMaximumHeight(100)
        decoy_lib_inner_layout.addWidget(QLabel("Decoy Libraries"))
        decoy_lib_inner_layout.addWidget(decoy_lib_browse_btn)
        decoy_lib_inner_layout.addWidget(decoy_lib_remove_btn)
        decoy_lib_browse_btn.clicked.connect(self.open_decoy_libs)
        decoy_lib_remove_btn.clicked.connect(self.remove_decoy_libs)
        self.decoy_lib_layout.addLayout(decoy_lib_inner_layout)
        self.decoy_lib_layout.addWidget(self.decoy_lib_list)

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
        self.outer_layout.addStretch(10)
        self.outer_layout.addLayout(self.project_file_layout)
        self.outer_layout.addStretch(10)
        self.outer_layout.addLayout(self.query_layout)
        self.outer_layout.addStretch(10)
        self.outer_layout.addLayout(self.target_lib_layout)
        self.outer_layout.addStretch(10)
        self.outer_layout.addLayout(self.make_decoy_layout)
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

    def browse_project_file_dir(self):
        dlg = QFileDialog()
        # my_dir = QtGui.QFileDialog.getExistingDirectory(self)
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        self.project_file_directory = dlg.getExistingDirectory()
        self.project_file_dir_text.setText(self.project_file_directory)

    def open_query(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.AnyFile)
        # dlg.setNameFilter("*.mgf")

        filenames = None
        filenames = dlg.getOpenFileNames()

        for f in filenames[0]:
            if f.split('.')[1] != 'mgf':
                continue
            self.query_list.addItem(f)

    def open_target_libs(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.AnyFile)

        filenames = None
        filenames = dlg.getOpenFileNames()

        for f in filenames[0]:
            if f.split('.')[1] != 'msp':
                continue
            self.target_lib_list.addItem(f)

    def open_decoy_libs(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.AnyFile)

        filenames = None
        filenames = dlg.getOpenFileNames()

        for f in filenames[0]:
            if f.split('.')[1] != 'msp':
                continue
            self.decoy_lib_list.addItem(f)

    def remove_target_libs(self):
        selected = self.target_lib_list.selectedItems()
        files = ''
        for s in selected:
            files += str(s.text()) + '\n'
        
        reply = QMessageBox().question(self, "Remove", "Are you sure to remove the files below?\n"+files, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.target_lib_list.removeItemWidget(self.target_lib_list.takeItem(self.target_lib_list.currentRow()))


    def remove_decoy_libs(self):
        selected = self.decoy_lib_list.selectedItems()
        files = ''
        for s in selected:
            files += str(s.text()) + '\n'
        
        reply = QMessageBox().question(self, "Remove", "Are you sure to remove the files below?\n"+files, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.decoy_lib_list.removeItemWidget(self.decoy_lib_list.takeItem(self.decoy_lib_list.currentRow()))
    

    def remove_query(self):
        selected = self.query_list.selectedItems()
        files = ''
        for s in selected:
            files += str(s.text()) + '\n'
        
        reply = QMessageBox().question(self, "Remove", "Are you sure to remove the files below?\n"+files, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.query_list.removeItemWidget(self.query_list.takeItem(self.query_list.currentRow()))


    def return_infomations(self):
        # query list에 추가
        for i in range(self.query_list.count()):
            print("line 268")
            self.query_file_list.append(self.query_list.item(i).text())
        
        # target list에 추가
        for i in range(self.target_lib_list.count()):
            self.target_lib_files.append(self.target_lib_list.item(i).text())

        # decoy list에 추가
        for i in range(self.decoy_lib_list.count()):
            self.decoy_lib_files.append(self.decoy_lib_list.item(i).text())

        
        print("[debug]", self.query_file_list)
        # project file name이 없다면?
        self.project_file_name = self.project_file_text.text()
        if not self.project_file_name or not self.project_file_directory:
            err = QMessageBox.warning(self, "No file", "There's no project file.\nPlease write or browse")
            return
        
        # query list가 비어져있는지 확인
        if not len(self.query_file_list):
            err = QMessageBox.warning(self, "No file", "There's no Query file.\nPlease import")
            return

        # target_lib이 없다면?
        if not self.target_lib_files:
            err = QMessageBox.warning(self, "No file", "There's no target lib file.\nPlease import")
            return

        # decoy_lib이 없다면?
        if not self.decoy_lib_files:
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



        if self.make_decoy_checkbox.checkState() == Qt.CheckState.Unchecked:
            make_decoy = 0
        else:
            make_decoy = 1

        project_file_path = self.project_file_directory + '/' + self.project_file_name + '.devi'
 
        print(project_file_path)
        # Deephos
        # 파라미터 파일을 만들어요
        param_file.make_parameter_file(project_file_path, self.query_file_list,
                                        self.target_lib_files,
                                        self.decoy_lib_files,
                                        self.pept_tol_value,
                                        self.isotope_tol_value_min,
                                        self.isotope_tol_value_max,
                                        self.frag_tol_value,
                                        make_decoy)
        # deephos를 실행해요
        parameter = './deephos/foo.params'
        os.system('java -jar deephos/deephos_tp2.jar -i ' + parameter)

        # ed = ExecuteDeephos()
        # ed.run(self.query_file_list)

        # loadingDlg = LoadingDialog("Executing Deephos...")
        # loadingDlg.exec()
        # loadingDlg.done(0)
        
        self.done(0)

