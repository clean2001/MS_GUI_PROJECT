from PyQt6.QtWidgets import *

class RunConfigDlg(QDialog):
    def __init__(self, myapp):
        super().__init__()
        self.setWindowTitle("View Config")
        self.resize(400, 400)
        self.myapp = myapp

        self.query_file_list = QListWidget()
        for file in self.myapp.filenames:
            self.query_file_list.addItem(file)
        
        self.initUI()
    
    def initUI(self):
        self.outer_layout = QVBoxLayout()
        
        # file config
        file_layout = QVBoxLayout()
        file_layout.addWidget(QLabel('Query Files:'))
        self.query_file_list.setMaximumHeight(200)
        file_layout.addWidget(self.query_file_list)

        # library config
        library_layout = QVBoxLayout()
        library_layout.addWidget(QLabel('Target lib: ' + str(self.myapp.target_lib_files)))
        library_layout.addWidget(QLabel('Decoy lib: ' + str(self.myapp.decoy_lib_files)))


        # peptide tol config
        peptide_tol_layout = QHBoxLayout()
        peptide_tol_layout.addWidget(QLabel('Peptide Tolerance(ppm): ' + str(self.myapp.peptide_tol)))

        # fragment tol config
        fragment_tol_layout = QHBoxLayout()
        fragment_tol_layout.addWidget(QLabel('Fragment Tolerance(Da): ' + str(round(self.myapp.frag_tol, 2))))

        # C13 isotope tol config
        c13_isotope_tol_layout = QHBoxLayout()
        c13_isotope_tol_layout.addWidget(QLabel('C13 Isotope Tolerance: ' + str(round(self.myapp.c13_isotope_tol_min, 2)) + ', ' + str(round(self.myapp.c13_isotope_tol_max, 2))))

        self.outer_layout.addLayout(file_layout)
        self.outer_layout.addStretch(1)
        self.outer_layout.addLayout(library_layout)
        self.outer_layout.addStretch(1)
        self.outer_layout.addLayout(peptide_tol_layout)
        self.outer_layout.addStretch(1)
        self.outer_layout.addLayout(fragment_tol_layout)
        self.outer_layout.addStretch(1)
        self.outer_layout.addLayout(c13_isotope_tol_layout)
        self.outer_layout.addStretch(1)
        self.setLayout(self.outer_layout)
